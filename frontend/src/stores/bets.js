import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '@/services/api'

export const useBetsStore = defineStore('bets', () => {
  const bets = ref([])
  const loading = ref(false)
  const error = ref(null)
  const statistics = ref(null)
  
  async function fetchBets(params = {}) {
    loading.value = true
    try {
      const response = await api.get('/bets/', { params })
      if (response.data.results) {
        bets.value = response.data.results
      } else {
        bets.value = response.data
      }
    } catch (err) {
      error.value = 'Error al cargar apuestas'
      throw err
    } finally {
      loading.value = false
    }
  }
  
  async function createBet(data) {
    loading.value = true
    try {
      const response = await api.post('/bets/', data)
      bets.value.unshift(response.data)
      // Actualizar estadísticas después de crear
      await fetchStatistics()
      return response.data
    } catch (err) {
      error.value = err.response?.data || 'Error al crear apuesta'
      throw err
    } finally {
      loading.value = false
    }
  }
  
  async function updateBet(id, data) {
    loading.value = true
    try {
      const response = await api.patch(`/bets/${id}/`, data)
      const index = bets.value.findIndex(b => b.id === id)
      if (index !== -1) {
        bets.value[index] = response.data
      }
      // Actualizar estadísticas después de actualizar
      await fetchStatistics()
      return response.data
    } catch (err) {
      error.value = err.response?.data || 'Error al actualizar apuesta'
      throw err
    } finally {
      loading.value = false
    }
  }
  
  async function deleteBet(id) {
    loading.value = true
    try {
      await api.delete(`/bets/${id}/`)
      bets.value = bets.value.filter(b => b.id !== id)
      // Actualizar estadísticas después de eliminar
      await fetchStatistics()
    } catch (err) {
      error.value = err.response?.data || 'Error al eliminar apuesta'
      throw err
    } finally {
      loading.value = false
    }
  }
  
  async function fetchStatistics() {
    try {
      const response = await api.get('/bets/statistics/')
      if (response.data) {
        statistics.value = response.data
      } else {
        statistics.value = {
          total_bet: 0,
          total_won: 0,
          total_lost: 0,
          net_result: 0,
          roi: 0,
          total_bets: 0,
          won_count: 0,
          lost_count: 0,
          pending_count: 0,
          win_rate: 0,
        }
      }
      return statistics.value
    } catch (err) {
      console.error('Error fetching statistics:', err)
      error.value = err.response?.data || 'Error al cargar estadísticas'
      // En caso de error, establecer valores por defecto
      statistics.value = {
        total_bet: 0,
        total_won: 0,
        total_lost: 0,
        net_result: 0,
        roi: 0,
        total_bets: 0,
        won_count: 0,
        lost_count: 0,
        pending_count: 0,
        win_rate: 0,
      }
      // No lanzar el error para que no interrumpa el flujo
      return statistics.value
    }
  }
  
  function getBetById(id) {
    return bets.value.find(b => b.id === id)
  }
  
  return {
    bets,
    loading,
    error,
    statistics,
    fetchBets,
    createBet,
    updateBet,
    deleteBet,
    fetchStatistics,
    getBetById,
  }
})

