import emailjs from '@emailjs/browser'

const SERVICE_ID = 'service_8lwyibt'
const PUBLIC_KEY = 'QeeyB-gtJqJpGSmXc'

const TEMPLATE_IDS = {
  DEBT_REMINDER: 'template_ulhxrhj',
  BUDGET_ALERT: 'template_f55atqn',
}

emailjs.init(PUBLIC_KEY)

function getLastSentKey(type, id = '') {
  return `email_last_sent_${type}_${id}`
}

function canSendEmail(type, id = '', hoursLimit = 24) {
  const key = getLastSentKey(type, id)
  const lastSent = localStorage.getItem(key)
  
  if (!lastSent) return true
  
  const hoursSinceLastSent = (Date.now() - parseInt(lastSent)) / (1000 * 60 * 60)
  return hoursSinceLastSent >= hoursLimit
}

function markEmailSent(type, id = '') {
  const key = getLastSentKey(type, id)
  localStorage.setItem(key, Date.now().toString())
}

export async function sendDebtReminder(userEmail, userName, debt, daysRemaining) {
  const emailId = `debt_${debt.id}`
  
  if (!canSendEmail('debt', emailId)) {
    console.log('Email de deuda ya enviado recientemente')
    return { success: false, reason: 'already_sent' }
  }
  
  try {
    const templateParams = {
      to_email: userEmail,
      to_name: userName || 'Usuario',
      debt_name: debt.name,
      amount: formatCurrency(debt.remaining_amount),
      due_date: formatDate(debt.due_date),
      days_remaining: daysRemaining,
      debt_type: debt.debt_type === 'deuda' ? 'debes' : 'te deben',
      creditor_debtor: debt.creditor_debtor || 'No especificado',
    }
    
    await emailjs.send(SERVICE_ID, TEMPLATE_IDS.DEBT_REMINDER, templateParams)
    markEmailSent('debt', emailId)
    
    return { success: true }
  } catch (error) {
    console.error('Error enviando recordatorio de deuda:', error)
    return { success: false, error }
  }
}

export async function sendBudgetAlert(userEmail, userName, budget, alertType) {
  const emailId = `budget_${budget.id}_${alertType}`
  
  if (!canSendEmail('budget', emailId)) {
    console.log('Email de presupuesto ya enviado recientemente')
    return { success: false, reason: 'already_sent' }
  }
  
  try {
    const spentAmount = budget.spent || 0
    const amountLimit = budget.amount_limit || 0
    const percentage = budget.percentage || 
      (amountLimit > 0 ? ((spentAmount / amountLimit) * 100).toFixed(0) : 0)
    
    const templateParams = {
      to_email: userEmail,
      to_name: userName || 'Usuario',
      category: budget.category_name || budget.category?.name || 'General',
      budget_amount: formatCurrency(amountLimit),
      spent: formatCurrency(spentAmount),
      remaining: formatCurrency(amountLimit - spentAmount),
      percentage: percentage,
      alert_type: alertType,
      alert_message: alertType === 'exceeded' 
        ? '¡Has excedido tu presupuesto!' 
        : `Tu presupuesto está al ${percentage}%`,
    }
    
    await emailjs.send(SERVICE_ID, TEMPLATE_IDS.BUDGET_ALERT, templateParams)
    markEmailSent('budget', emailId)
    
    return { success: true }
  } catch (error) {
    console.error('Error enviando alerta de presupuesto:', error)
    return { success: false, error }
  }
}


function formatCurrency(value) {
  const num = Math.round(Number(value) || 0)
  return '$' + num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, '.')
}

function formatDate(dateString) {
  if (!dateString) return ''
  const date = new Date(dateString + 'T00:00:00')
  const day = String(date.getDate()).padStart(2, '0')
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const year = date.getFullYear()
  return `${day}/${month}/${year}`
}


export function getNotificationPreferences() {
  const defaults = {
    emailNotifications: true,
    debtReminders: true,
    debtDaysBefore: 7,
    budgetAlerts: true,
  }
  
  try {
    const saved = localStorage.getItem('notification_preferences')
    return saved ? { ...defaults, ...JSON.parse(saved) } : defaults
  } catch {
    return defaults
  }
}

export function saveNotificationPreferences(preferences) {
  localStorage.setItem('notification_preferences', JSON.stringify(preferences))
}

export function getDaysUntilDue(dueDateString) {
  if (!dueDateString) return null
  
  const today = new Date()
  today.setHours(0, 0, 0, 0)
  
  const dueDate = new Date(dueDateString + 'T00:00:00')
  const diffTime = dueDate - today
  const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24))
  
  return diffDays
}

export default {
  sendDebtReminder,
  sendBudgetAlert,
  getNotificationPreferences,
  saveNotificationPreferences,
  getDaysUntilDue,
  TEMPLATE_IDS,
}

