import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '@/services/api'

export const useAccountsStore = defineStore('accounts', () => {
  const accounts = ref([])
  const loading = ref(false)
  const error = ref(null)
  
  const totalBalance = computed(() => {
    return accounts.value
      .filter(acc => acc.include_in_total && acc.is_active)
      .reduce((sum, acc) => sum + parseFloat(acc.balance), 0)
  })
  
  const activeAccounts = computed(() => {
    return accounts.value.filter(acc => acc.is_active)
  })
  
  async function fetchAccounts() {
    loading.value = true
    try {
      const response = await api.get('/accounts/')
      accounts.value = response.data.results || response.data
    } catch (err) {
      error.value = 'Error al cargar cuentas'
    } finally {
      loading.value = false
    }
  }
  
  async function createAccount(data) {
    loading.value = true
    try {
      const response = await api.post('/accounts/', data)
      accounts.value.push(response.data)
      return response.data
    } catch (err) {
      error.value = err.response?.data || 'Error al crear cuenta'
      throw err
    } finally {
      loading.value = false
    }
  }
  
  async function updateAccount(id, data) {
    loading.value = true
    try {
      const response = await api.patch(`/accounts/${id}/`, data)
      const index = accounts.value.findIndex(a => a.id === id)
      if (index !== -1) {
        accounts.value[index] = response.data
      }
      return response.data
    } catch (err) {
      error.value = err.response?.data || 'Error al actualizar cuenta'
      throw err
    } finally {
      loading.value = false
    }
  }
  
  async function deleteAccount(id) {
    loading.value = true
    try {
      await api.delete(`/accounts/${id}/`)
      accounts.value = accounts.value.filter(a => a.id !== id)
    } catch (err) {
      error.value = err.response?.data || 'Error al eliminar cuenta'
      throw err
    } finally {
      loading.value = false
    }
  }
  
  async function setInitialBalance(id, balance) {
    try {
      const response = await api.post(`/accounts/${id}/set_initial_balance/`, {
        initial_balance: balance
      })
      const index = accounts.value.findIndex(a => a.id === id)
      if (index !== -1) {
        accounts.value[index] = response.data
      }
      return response.data
    } catch (err) {
      error.value = err.response?.data || 'Error al establecer saldo'
      throw err
    }
  }
  
  function getAccountById(id) {
    return accounts.value.find(a => a.id === id)
  }
  
  return {
    accounts,
    loading,
    error,
    totalBalance,
    activeAccounts,
    fetchAccounts,
    createAccount,
    updateAccount,
    deleteAccount,
    setInitialBalance,
    getAccountById,
  }
})






