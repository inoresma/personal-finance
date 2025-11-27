import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '@/services/api'
import emailService from '@/services/emailService'
import { useAuthStore } from '@/stores/auth'

export const useNotificationsStore = defineStore('notifications', () => {
  const alerts = ref([])
  const loading = ref(false)
  const preferences = ref(emailService.getNotificationPreferences())
  
  function getUserInfo() {
    const authStore = useAuthStore()
    return {
      email: authStore.user?.email,
      name: authStore.user?.first_name || authStore.user?.email
    }
  }
  
  const filterType = ref('unread')
  
  const allAlerts = computed(() => alerts.value.filter(a => !a.dismissed))
  const unreadAlerts = computed(() => allAlerts.value.filter(a => !isRead(a.id)))
  const readAlerts = computed(() => allAlerts.value.filter(a => isRead(a.id)))
  
  const pendingAlerts = computed(() => {
    if (filterType.value === 'read') {
      return readAlerts.value
    }
    return unreadAlerts.value
  })
  
  const alertCount = computed(() => unreadAlerts.value.length)
  
  const debtAlerts = computed(() => pendingAlerts.value.filter(a => a.type === 'debt'))
  const budgetAlerts = computed(() => pendingAlerts.value.filter(a => a.type === 'budget'))
  
  function setFilter(type) {
    filterType.value = type
  }
  
  async function checkAlerts() {
    loading.value = true
    alerts.value = []
    
    try {
      await Promise.all([
        checkDebtAlerts(),
        checkBudgetAlerts()
      ])
    } catch (error) {
      console.error('Error checking alerts:', error)
    } finally {
      loading.value = false
    }
  }
  
  async function checkDebtAlerts() {
    if (!preferences.value.debtReminders) return
    
    try {
      const response = await api.get('/debts/')
      const debts = response.data.results || response.data
      
      debts.forEach(debt => {
        if (debt.is_paid || !debt.due_date) return
        
        const daysRemaining = emailService.getDaysUntilDue(debt.due_date)
        
        if (daysRemaining !== null && daysRemaining <= preferences.value.debtDaysBefore && daysRemaining >= 0) {
          const alertId = `debt_${debt.id}`
          const dismissed = isDismissed(alertId)
          const read = isRead(alertId)
          
          const alert = {
            id: alertId,
            type: 'debt',
            severity: daysRemaining <= 3 ? 'danger' : 'warning',
            title: debt.debt_type === 'deuda' ? 'Deuda próxima a vencer' : 'Préstamo próximo a vencer',
            message: `"${debt.name}" vence en ${daysRemaining} día${daysRemaining !== 1 ? 's' : ''}`,
            data: { ...debt, daysRemaining },
            dismissed,
            read,
          }
          
          alerts.value.push(alert)
          
          if (preferences.value.emailNotifications && preferences.value.debtReminders && !read) {
            const userInfo = getUserInfo()
            if (userInfo.email) {
              sendEmailForAlert(alert, userInfo.email, userInfo.name).catch(err => {
                console.error('Error enviando email de deuda:', err)
              })
            }
          }
        }
        
        if (daysRemaining !== null && daysRemaining < 0) {
          const alertId = `debt_overdue_${debt.id}`
          const dismissed = isDismissed(alertId)
          const read = isRead(alertId)
          
          const alert = {
            id: alertId,
            type: 'debt',
            severity: 'danger',
            title: debt.debt_type === 'deuda' ? 'Deuda vencida' : 'Préstamo vencido',
            message: `"${debt.name}" venció hace ${Math.abs(daysRemaining)} día${Math.abs(daysRemaining) !== 1 ? 's' : ''}`,
            data: { ...debt, daysRemaining },
            dismissed,
            read,
          }
          
          alerts.value.push(alert)
          
          if (preferences.value.emailNotifications && preferences.value.debtReminders && !read) {
            const userInfo = getUserInfo()
            if (userInfo.email) {
              sendEmailForAlert(alert, userInfo.email, userInfo.name).catch(err => {
                console.error('Error enviando email de deuda vencida:', err)
              })
            }
          }
        }
      })
    } catch (error) {
      console.error('Error checking debt alerts:', error)
    }
  }
  
  async function checkBudgetAlerts() {
    if (!preferences.value.budgetAlerts) return
    
    try {
      const response = await api.get('/budgets/')
      const budgets = response.data.results || response.data
      
      budgets.forEach(budget => {
        if (!budget.is_active) return
        
        const spentAmount = budget.spent || 0
        const amountLimit = budget.amount_limit || 0
        
        if (amountLimit === 0) return
        
        const spentPercentage = budget.percentage || 
          ((spentAmount / amountLimit) * 100)
        
        const alertThreshold = budget.alert_threshold || 80
        
        if (spentPercentage >= 100) {
          const alertId = `budget_exceeded_${budget.id}`
          const dismissed = isDismissed(alertId)
          const read = isRead(alertId)
          
          const alert = {
            id: alertId,
            type: 'budget',
            severity: 'danger',
            title: 'Presupuesto excedido',
            message: `${budget.category_name || 'General'}: Gastaste ${spentPercentage.toFixed(1)}% del presupuesto`,
            data: { ...budget, alertType: 'exceeded' },
            dismissed,
            read,
          }
          
          alerts.value.push(alert)
          
          if (preferences.value.emailNotifications && preferences.value.budgetAlerts && !read) {
            const userInfo = getUserInfo()
            if (userInfo.email) {
              sendEmailForAlert(alert, userInfo.email, userInfo.name).catch(err => {
                console.error('Error enviando email de presupuesto excedido:', err)
              })
            }
          }
        } else if (spentPercentage >= alertThreshold) {
          const alertId = `budget_low_${budget.id}`
          const dismissed = isDismissed(alertId)
          const read = isRead(alertId)
          
          const alert = {
            id: alertId,
            type: 'budget',
            severity: 'warning',
            title: 'Presupuesto bajo',
            message: `${budget.category_name || 'General'}: Has usado ${spentPercentage.toFixed(1)}% del presupuesto`,
            data: { ...budget, alertType: 'low' },
            dismissed,
            read,
          }
          
          alerts.value.push(alert)
          
          if (preferences.value.emailNotifications && preferences.value.budgetAlerts && !read) {
            const userInfo = getUserInfo()
            if (userInfo.email) {
              sendEmailForAlert(alert, userInfo.email, userInfo.name).catch(err => {
                console.error('Error enviando email de presupuesto bajo:', err)
              })
            }
          }
        }
      })
    } catch (error) {
      console.error('Error checking budget alerts:', error)
    }
  }
  
  function isDismissed(alertId) {
    const dismissedAlerts = JSON.parse(localStorage.getItem('dismissed_alerts') || '{}')
    const dismissedUntil = dismissedAlerts[alertId]
    
    if (!dismissedUntil) return false
    
    return Date.now() < dismissedUntil
  }
  
  function isRead(alertId) {
    const readAlerts = JSON.parse(localStorage.getItem('read_alerts') || '{}')
    return readAlerts[alertId] === true
  }
  
  function markAsRead(alertId) {
    const readAlerts = JSON.parse(localStorage.getItem('read_alerts') || '{}')
    readAlerts[alertId] = true
    localStorage.setItem('read_alerts', JSON.stringify(readAlerts))
    
    const alert = alerts.value.find(a => a.id === alertId)
    if (alert) {
      alert.read = true
    }
    
    alerts.value = [...alerts.value]
  }
  
  function dismissAlert(alertId, hours = 24) {
    const dismissedAlerts = JSON.parse(localStorage.getItem('dismissed_alerts') || '{}')
    dismissedAlerts[alertId] = Date.now() + (hours * 60 * 60 * 1000)
    localStorage.setItem('dismissed_alerts', JSON.stringify(dismissedAlerts))
    
    const alert = alerts.value.find(a => a.id === alertId)
    if (alert) {
      alert.dismissed = true
    }
  }
  
  function dismissAllAlerts(hours = 24) {
    pendingAlerts.value.forEach(alert => {
      dismissAlert(alert.id, hours)
    })
  }
  
  async function sendEmailForAlert(alert, userEmail, userName) {
    if (alert.type === 'debt') {
      return await emailService.sendDebtReminder(
        userEmail,
        userName,
        alert.data,
        alert.data.daysRemaining
      )
    } else if (alert.type === 'budget') {
      return await emailService.sendBudgetAlert(
        userEmail,
        userName,
        alert.data,
        alert.data.alertType
      )
    }
    
    return { success: false, reason: 'unknown_type' }
  }
  
  async function sendAllPendingEmails(userEmail, userName) {
    const results = []
    
    for (const alert of pendingAlerts.value) {
      const result = await sendEmailForAlert(alert, userEmail, userName)
      results.push({ alert, result })
    }
    
    return results
  }
  
  function updatePreferences(newPreferences) {
    preferences.value = { ...preferences.value, ...newPreferences }
    emailService.saveNotificationPreferences(preferences.value)
  }
  
  function clearAlerts() {
    alerts.value = []
  }
  
  return {
    alerts,
    loading,
    preferences,
    filterType,
    allAlerts,
    unreadAlerts,
    readAlerts,
    pendingAlerts,
    alertCount,
    debtAlerts,
    budgetAlerts,
    setFilter,
    checkAlerts,
    dismissAlert,
    dismissAllAlerts,
    markAsRead,
    sendEmailForAlert,
    sendAllPendingEmails,
    updatePreferences,
    clearAlerts,
  }
})

