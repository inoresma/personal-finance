import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '@/services/api'

export const useSecondaryCategoriesStore = defineStore('secondaryCategories', () => {
  const secondaryCategories = ref([])
  const loading = ref(false)
  const error = ref(null)
  
  async function fetchSecondaryCategories() {
    loading.value = true
    error.value = null
    try {
      const response = await api.get('/categories/secondary/')
      const data = response.data.results || response.data
      const categoriesArray = Array.isArray(data) ? data : []
      
      secondaryCategories.value = categoriesArray
    } catch (err) {
      error.value = 'Error al cargar categorías secundarias'
      console.error('Error fetching secondary categories:', err)
    } finally {
      loading.value = false
    }
  }
  
  async function createSecondaryCategory(data) {
    loading.value = true
    error.value = null
    try {
      const response = await api.post('/categories/secondary/', data)
      
      if (response.status >= 200 && response.status < 300) {
        const newCategory = response.data
        
        await fetchSecondaryCategories()
        
        return newCategory
      } else {
        throw new Error('Error inesperado al crear la categoría secundaria')
      }
    } catch (err) {
      const errorMessage = err.response?.data 
        ? (typeof err.response.data === 'string' 
            ? err.response.data 
            : err.response.data.detail || JSON.stringify(err.response.data))
        : err.message || 'Error al crear categoría secundaria'
      error.value = errorMessage
      throw new Error(errorMessage)
    } finally {
      loading.value = false
    }
  }
  
  async function updateSecondaryCategory(id, data) {
    loading.value = true
    error.value = null
    try {
      const response = await api.patch(`/categories/secondary/${id}/`, data)
      
      if (response.status >= 200 && response.status < 300) {
        await fetchSecondaryCategories()
        return response.data
      } else {
        throw new Error('Error inesperado al actualizar la categoría secundaria')
      }
    } catch (err) {
      const errorMessage = err.response?.data 
        ? (typeof err.response.data === 'string' 
            ? err.response.data 
            : err.response.data.detail || JSON.stringify(err.response.data))
        : err.message || 'Error al actualizar categoría secundaria'
      error.value = errorMessage
      throw new Error(errorMessage)
    } finally {
      loading.value = false
    }
  }
  
  async function deleteSecondaryCategory(id) {
    loading.value = true
    try {
      await api.delete(`/categories/secondary/${id}/`)
      await fetchSecondaryCategories()
    } catch (err) {
      error.value = err.response?.data?.detail || 'Error al eliminar categoría secundaria'
      throw err
    } finally {
      loading.value = false
    }
  }
  
  function getSecondaryCategoryById(id) {
    return secondaryCategories.value.find(c => c.id === id)
  }
  
  return {
    secondaryCategories,
    loading,
    error,
    fetchSecondaryCategories,
    createSecondaryCategory,
    updateSecondaryCategory,
    deleteSecondaryCategory,
    getSecondaryCategoryById,
  }
})


