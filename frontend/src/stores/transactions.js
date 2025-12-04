import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '@/services/api'

export const useTransactionsStore = defineStore('transactions', () => {
  const transactions = ref([])
  const loading = ref(false)
  const error = ref(null)
  const pagination = ref({
    count: 0,
    page: 1,
    next: null,
    previous: null
  })
  
  async function fetchTransactions(params = {}) {
    loading.value = true
    try {
      const response = await api.get('/transactions/', { params })
      if (response.data.results) {
        transactions.value = response.data.results
        pagination.value = {
          count: response.data.count || 0,
          page: Math.floor((response.data.offset || 0) / (response.data.limit || 20)) + 1,
          next: response.data.next,
          previous: response.data.previous
        }
      } else {
        transactions.value = response.data
        pagination.value = {
          count: response.data.length,
          page: 1,
          next: null,
          previous: null
        }
      }
    } catch (err) {
      error.value = 'Error al cargar transacciones'
      throw err
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
      console.error('Error creating transaction:', err)
      console.error('Request data:', data)
      console.error('Response data:', err.response?.data)
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
  
  function getTransactionById(id) {
    return transactions.value.find(t => t.id === id)
  }
  
  async function fetchTransactionDetails(id) {
    try {
      const response = await api.get(`/transactions/${id}/`)
      return response.data
    } catch (err) {
      error.value = err.response?.data || 'Error al cargar detalles de transacción'
      throw err
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
    getTransactionById,
    fetchTransactionDetails,
  }
})
