import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useUiStore = defineStore('ui', () => {
  const sidebarOpen = ref(false)
  const darkMode = ref(false)
  const toasts = ref([])
  
  function toggleSidebar() {
    sidebarOpen.value = !sidebarOpen.value
  }
  
  function closeSidebar() {
    sidebarOpen.value = false
  }
  
  function toggleDarkMode() {
    darkMode.value = !darkMode.value
    localStorage.setItem('darkMode', darkMode.value)
  }
  
  function showToast(message, type = 'info', duration = 3000) {
    const id = Date.now()
    toasts.value.push({ id, message, type })
    
    setTimeout(() => {
      removeToast(id)
    }, duration)
  }
  
  function removeToast(id) {
    toasts.value = toasts.value.filter(t => t.id !== id)
  }
  
  function showSuccess(message) {
    showToast(message, 'success')
  }
  
  function showError(message) {
    showToast(message, 'error', 5000)
  }
  
  function showWarning(message) {
    showToast(message, 'warning', 4000)
  }
  
  return {
    sidebarOpen,
    darkMode,
    toasts,
    toggleSidebar,
    closeSidebar,
    toggleDarkMode,
    showToast,
    removeToast,
    showSuccess,
    showError,
    showWarning,
  }
})














