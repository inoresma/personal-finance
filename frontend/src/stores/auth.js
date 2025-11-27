import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '@/services/api'
import router from '@/router'

export const useAuthStore = defineStore('auth', () => {
  const user = ref(null)
  const loading = ref(false)
  const error = ref(null)
  
  const isAuthenticated = computed(() => !!user.value)
  
  async function login(email, password) {
    loading.value = true
    error.value = null
    
    try {
      const response = await api.post('/auth/login/', { email, password })
      const { access, refresh } = response.data
      
      localStorage.setItem('access_token', access)
      localStorage.setItem('refresh_token', refresh)
      
      await fetchProfile()
      router.push('/dashboard')
    } catch (err) {
      error.value = err.response?.data?.detail || 'Error al iniciar sesión'
      throw err
    } finally {
      loading.value = false
    }
  }
  
  async function register(userData) {
    loading.value = true
    error.value = null
    
    try {
      const response = await api.post('/auth/register/', userData)
      const { tokens } = response.data
      
      localStorage.setItem('access_token', tokens.access)
      localStorage.setItem('refresh_token', tokens.refresh)
      
      user.value = response.data.user
      router.push('/dashboard')
    } catch (err) {
      error.value = err.response?.data || 'Error al registrarse'
      throw err
    } finally {
      loading.value = false
    }
  }
  
  async function fetchProfile() {
    try {
      const response = await api.get('/auth/profile/')
      user.value = response.data
    } catch (err) {
      logout()
    }
  }
  
  async function updateProfile(data) {
    loading.value = true
    try {
      const response = await api.patch('/auth/profile/', data)
      user.value = response.data
      return response.data
    } catch (err) {
      error.value = err.response?.data || 'Error al actualizar perfil'
      throw err
    } finally {
      loading.value = false
    }
  }
  
  async function changePassword(oldPassword, newPassword) {
    loading.value = true
    try {
      await api.put('/auth/change-password/', {
        old_password: oldPassword,
        new_password: newPassword,
      })
    } catch (err) {
      error.value = err.response?.data || 'Error al cambiar contraseña'
      throw err
    } finally {
      loading.value = false
    }
  }
  
  function logout() {
    const refreshToken = localStorage.getItem('refresh_token')
    
    if (refreshToken) {
      api.post('/auth/logout/', { refresh: refreshToken }).catch(() => {})
    }
    
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
    user.value = null
    router.push('/login')
  }
  
  function checkAuth() {
    const token = localStorage.getItem('access_token')
    if (token) {
      fetchProfile()
    }
  }
  
  return {
    user,
    loading,
    error,
    isAuthenticated,
    login,
    register,
    fetchProfile,
    updateProfile,
    changePassword,
    logout,
    checkAuth,
  }
})





