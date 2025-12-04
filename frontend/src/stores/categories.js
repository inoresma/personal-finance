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
    error.value = null
    try {
      const response = await api.get('/categories/')
      const data = response.data.results || response.data
      const categoriesArray = Array.isArray(data) ? data : []
      
      categories.value = categoriesArray
    } catch (err) {
      error.value = 'Error al cargar categorías'
      console.error('Error fetching categories:', err)
    } finally {
      loading.value = false
    }
  }
  
  async function createCategory(data) {
    console.log('createCategory llamado con datos:', data)
    loading.value = true
    error.value = null
    try {
      if (!data.category_type || !['ingreso', 'gasto'].includes(data.category_type)) {
        console.error('Tipo de categoría inválido en createCategory:', data.category_type)
        throw new Error('El tipo de categoría es requerido y debe ser "ingreso" o "gasto"')
      }
      
      console.log('Enviando POST a /categories/', data)
      const response = await api.post('/categories/', data)
      console.log('Respuesta del servidor:', response.status, response.data)
      
      if (response.status >= 200 && response.status < 300) {
        const newCategory = response.data
        console.log('Categoría recibida del servidor:', newCategory)
        
        await fetchCategories()
        
        return newCategory
      } else {
        console.error('Status code inesperado:', response.status)
        throw new Error('Error inesperado al crear la categoría')
      }
    } catch (err) {
      console.error('Error en createCategory:', err)
      console.error('Error response:', err.response)
      const errorMessage = err.response?.data 
        ? (typeof err.response.data === 'string' 
            ? err.response.data 
            : err.response.data.detail || JSON.stringify(err.response.data))
        : err.message || 'Error al crear categoría'
      error.value = errorMessage
      throw new Error(errorMessage)
    } finally {
      loading.value = false
    }
  }
  
  async function updateCategory(id, data) {
    loading.value = true
    error.value = null
    try {
      const response = await api.patch(`/categories/${id}/`, data)
      
      if (response.status >= 200 && response.status < 300) {
        await fetchCategories()
        return response.data
      } else {
        throw new Error('Error inesperado al actualizar la categoría')
      }
    } catch (err) {
      const errorMessage = err.response?.data 
        ? (typeof err.response.data === 'string' 
            ? err.response.data 
            : err.response.data.detail || JSON.stringify(err.response.data))
        : err.message || 'Error al actualizar categoría'
      error.value = errorMessage
      throw new Error(errorMessage)
    } finally {
      loading.value = false
    }
  }
  
  async function deleteCategory(id) {
    loading.value = true
    try {
      await api.delete(`/categories/${id}/`)
      await fetchCategories()
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











