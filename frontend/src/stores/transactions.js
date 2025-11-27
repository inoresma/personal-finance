import { defineStore } from 'pinia'
import { ref } from 'vue'
import api from '@/services/api'

export const useTransactionsStore = defineStore('transactions', () => {
  const transactions = ref([])
  const loading = ref(false)
  const error = ref(null)
  const pagination = ref({
    count: 0,
    next: null,
    previous: null,
    page: 1,
  })
  
  async function fetchTransactions(params = {}) {
    loading.value = true
    try {
      const response = await api.get('/transactions/', { params })
      transactions.value = response.data.results || response.data
      if (response.data.count !== undefined) {
        pagination.value = {
          count: response.data.count,
          next: response.data.next,
          previous: response.data.previous,
          page: params.page || 1,
        }
      }
    } catch (err) {
      error.value = 'Error al cargar transacciones'
    } finally {
      loading.value = false
    }
  }
  
  async function createTransaction(data) {
    loading.value = true
    try {
      const response = await api.post('/transactions/', data)
      transactions.value.unshift(response.data)
      return response.data
    } catch (err) {
      error.value = err.response?.data || 'Error al crear transacción'
      throw err
    } finally {
      loading.value = false
    }
  }
  
  async function updateTransaction(id, data) {
    loading.value = true
    try {
      const response = await api.patch(`/transactions/${id}/`, data)
      const index = transactions.value.findIndex(t => t.id === id)
      if (index !== -1) {
        transactions.value[index] = response.data
      }
      return response.data
    } catch (err) {
      error.value = err.response?.data || 'Error al actualizar transacción'
      throw err
    } finally {
      loading.value = false
    }
  }
  
  async function deleteTransaction(id) {
    loading.value = true
    try {
      await api.delete(`/transactions/${id}/`)
      transactions.value = transactions.value.filter(t => t.id !== id)
    } catch (err) {
      error.value = err.response?.data || 'Error al eliminar transacción'
      throw err
    } finally {
      loading.value = false
    }
  }
  
  async function getRecentTransactions(limit = 5) {
    try {
      const response = await api.get('/transactions/recent/', { params: { limit } })
      return response.data
    } catch (err) {
      return []
    }
  }
  
  async function getSummary(dateFrom, dateTo) {
    try {
      const params = {}
      if (dateFrom) params.date_from = dateFrom
      if (dateTo) params.date_to = dateTo
      
      const response = await api.get('/transactions/summary/', { params })
      return response.data
    } catch (err) {
      return { income: 0, expenses: 0, balance: 0 }
    }
  }
  
  async function getByCategory(dateFrom, dateTo) {
    try {
      const params = {}
      if (dateFrom) params.date_from = dateFrom
      if (dateTo) params.date_to = dateTo
      
      const response = await api.get('/transactions/by_category/', { params })
      return response.data
    } catch (err) {
      return []
    }
  }
  
  return {
    transactions,
    loading,
    error,
    pagination,
    fetchTransactions,
    createTransaction,
    updateTransaction,
    deleteTransaction,
    getRecentTransactions,
    getSummary,
    getByCategory,
  }
})





