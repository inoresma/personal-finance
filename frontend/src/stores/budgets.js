import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '@/services/api'

export const useBudgetsStore = defineStore('budgets', () => {
  const budgets = ref([])
  const loading = ref(false)
  const error = ref(null)
  
  const activeBudgets = computed(() => {
    return budgets.value.filter(b => b.is_active)
  })
  
  const alertBudgets = computed(() => {
    return budgets.value.filter(b => b.is_active && (b.is_warning || b.is_exceeded))
  })
  
  async function fetchBudgets() {
    loading.value = true
    try {
      const response = await api.get('/budgets/')
      budgets.value = response.data.results || response.data
    } catch (err) {
      error.value = 'Error al cargar presupuestos'
    } finally {
      loading.value = false
    }
  }
  
  async function createBudget(data) {
    loading.value = true
    try {
      const response = await api.post('/budgets/', data)
      budgets.value.push(response.data)
      return response.data
    } catch (err) {
      error.value = err.response?.data || 'Error al crear presupuesto'
      throw err
    } finally {
      loading.value = false
    }
  }
  
  async function updateBudget(id, data) {
    loading.value = true
    try {
      const response = await api.patch(`/budgets/${id}/`, data)
      const index = budgets.value.findIndex(b => b.id === id)
      if (index !== -1) {
        budgets.value[index] = response.data
      }
      return response.data
    } catch (err) {
      error.value = err.response?.data || 'Error al actualizar presupuesto'
      throw err
    } finally {
      loading.value = false
    }
  }
  
  async function deleteBudget(id) {
    loading.value = true
    try {
      await api.delete(`/budgets/${id}/`)
      budgets.value = budgets.value.filter(b => b.id !== id)
    } catch (err) {
      error.value = err.response?.data || 'Error al eliminar presupuesto'
      throw err
    } finally {
      loading.value = false
    }
  }
  
  async function getAlerts() {
    try {
      const response = await api.get('/budgets/alerts/')
      return response.data
    } catch (err) {
      return []
    }
  }
  
  return {
    budgets,
    loading,
    error,
    activeBudgets,
    alertBudgets,
    fetchBudgets,
    createBudget,
    updateBudget,
    deleteBudget,
    getAlerts,
  }
})














