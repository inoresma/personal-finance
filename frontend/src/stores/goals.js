import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '@/services/api'

export const useGoalsStore = defineStore('goals', () => {
  const goals = ref([])
  const loading = ref(false)
  const error = ref(null)
  
  const activeGoals = computed(() => {
    return goals.value.filter(g => g.is_active)
  })
  
  const completedGoals = computed(() => {
    return goals.value.filter(g => g.is_active && g.is_completed)
  })
  
  const savingsGoals = computed(() => {
    return goals.value.filter(g => g.goal_type === 'savings' && g.is_active)
  })
  
  const categoryReductionGoals = computed(() => {
    return goals.value.filter(g => g.goal_type === 'category_reduction' && g.is_active)
  })
  
  async function fetchGoals() {
    loading.value = true
    error.value = null
    try {
      const response = await api.get('/goals/')
      goals.value = response.data.results || response.data
    } catch (err) {
      error.value = 'Error al cargar metas'
      console.error('Error fetching goals:', err)
    } finally {
      loading.value = false
    }
  }
  
  async function fetchActiveGoals() {
    loading.value = true
    error.value = null
    try {
      const response = await api.get('/goals/active/')
      const active = response.data
      goals.value = goals.value.filter(g => !g.is_active).concat(active)
    } catch (err) {
      error.value = 'Error al cargar metas activas'
      console.error('Error fetching active goals:', err)
    } finally {
      loading.value = false
    }
  }
  
  async function createGoal(data) {
    loading.value = true
    error.value = null
    try {
      const response = await api.post('/goals/', data)
      goals.value.push(response.data)
      return response.data
    } catch (err) {
      error.value = err.response?.data || 'Error al crear meta'
      throw err
    } finally {
      loading.value = false
    }
  }
  
  async function updateGoal(id, data) {
    loading.value = true
    error.value = null
    try {
      const response = await api.patch(`/goals/${id}/`, data)
      const index = goals.value.findIndex(g => g.id === id)
      if (index !== -1) {
        goals.value[index] = response.data
      }
      return response.data
    } catch (err) {
      error.value = err.response?.data || 'Error al actualizar meta'
      throw err
    } finally {
      loading.value = false
    }
  }
  
  async function deleteGoal(id) {
    loading.value = true
    error.value = null
    try {
      await api.delete(`/goals/${id}/`)
      goals.value = goals.value.filter(g => g.id !== id)
    } catch (err) {
      error.value = err.response?.data || 'Error al eliminar meta'
      throw err
    } finally {
      loading.value = false
    }
  }
  
  async function toggleGoalActive(id) {
    loading.value = true
    error.value = null
    try {
      const response = await api.post(`/goals/${id}/toggle_active/`)
      const index = goals.value.findIndex(g => g.id === id)
      if (index !== -1) {
        goals.value[index] = response.data
      }
      return response.data
    } catch (err) {
      error.value = err.response?.data || 'Error al cambiar estado de meta'
      throw err
    } finally {
      loading.value = false
    }
  }
  
  async function getGoalProgress(id) {
    try {
      const response = await api.get(`/goals/${id}/progress/`)
      return response.data
    } catch (err) {
      console.error('Error fetching goal progress:', err)
      return null
    }
  }
  
  return {
    goals,
    loading,
    error,
    activeGoals,
    completedGoals,
    savingsGoals,
    categoryReductionGoals,
    fetchGoals,
    fetchActiveGoals,
    createGoal,
    updateGoal,
    deleteGoal,
    toggleGoalActive,
    getGoalProgress,
  }
})

