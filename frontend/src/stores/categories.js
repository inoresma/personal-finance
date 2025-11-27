import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '@/services/api'

export const useCategoriesStore = defineStore('categories', () => {
  const categories = ref([])
  const loading = ref(false)
  const error = ref(null)
  
  const expenseCategories = computed(() => {
    return categories.value.filter(c => c.category_type === 'gasto' && !c.parent)
  })
  
  const incomeCategories = computed(() => {
    return categories.value.filter(c => c.category_type === 'ingreso' && !c.parent)
  })
  
  async function fetchCategories() {
    loading.value = true
    try {
      const response = await api.get('/categories/')
      categories.value = response.data.results || response.data
    } catch (err) {
      error.value = 'Error al cargar categorías'
    } finally {
      loading.value = false
    }
  }
  
  async function createCategory(data) {
    loading.value = true
    try {
      const response = await api.post('/categories/', data)
      categories.value.push(response.data)
      return response.data
    } catch (err) {
      error.value = err.response?.data || 'Error al crear categoría'
      throw err
    } finally {
      loading.value = false
    }
  }
  
  async function updateCategory(id, data) {
    loading.value = true
    try {
      const response = await api.patch(`/categories/${id}/`, data)
      const index = categories.value.findIndex(c => c.id === id)
      if (index !== -1) {
        categories.value[index] = response.data
      }
      return response.data
    } catch (err) {
      error.value = err.response?.data || 'Error al actualizar categoría'
      throw err
    } finally {
      loading.value = false
    }
  }
  
  async function deleteCategory(id) {
    loading.value = true
    try {
      await api.delete(`/categories/${id}/`)
      categories.value = categories.value.filter(c => c.id !== id)
    } catch (err) {
      error.value = err.response?.data?.detail || 'Error al eliminar categoría'
      throw err
    } finally {
      loading.value = false
    }
  }
  
  function getCategoryById(id) {
    return categories.value.find(c => c.id === id)
  }
  
  function getCategoriesByType(type) {
    return categories.value.filter(c => c.category_type === type && !c.parent)
  }
  
  return {
    categories,
    loading,
    error,
    expenseCategories,
    incomeCategories,
    fetchCategories,
    createCategory,
    updateCategory,
    deleteCategory,
    getCategoryById,
    getCategoriesByType,
  }
})





