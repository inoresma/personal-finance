<script setup>
import { ref, onMounted, computed } from 'vue'
import { useSecondaryCategoriesStore } from '@/stores/secondaryCategories'
import { useUiStore } from '@/stores/ui'
import Modal from '@/components/Modal.vue'
import CategoryIcon from '@/components/CategoryIcon.vue'
import IconSelector from '@/components/IconSelector.vue'
import { PlusIcon, PencilIcon, TrashIcon, TagIcon } from '@heroicons/vue/24/outline'

const secondaryCategoriesStore = useSecondaryCategoriesStore()
const uiStore = useUiStore()

const showModal = ref(false)
const showDeleteModal = ref(false)
const editingCategory = ref(null)
const categoryToDelete = ref(null)
const loading = ref(false)

const form = ref({
  name: '',
  color: '#6366F1',
  icon: 'otros',
})

const colors = [
  '#EF4444', '#F59E0B', '#22C55E', '#3B82F6', '#8B5CF6',
  '#EC4899', '#14B8A6', '#6366F1', '#64748B', '#0EA5E9'
]

const isEditing = computed(() => !!editingCategory.value)

function openNewCategory() {
  editingCategory.value = null
  form.value = {
    name: '',
    color: '#6366F1',
    icon: 'otros',
  }
  showModal.value = true
}

function openEditCategory(category) {
  editingCategory.value = category
  form.value = {
    name: category.name,
    color: category.color,
    icon: category.icon,
  }
  showModal.value = true
}

function confirmDeleteCategory(category) {
  categoryToDelete.value = category
  showDeleteModal.value = true
}

async function handleSubmit() {
  if (!form.value.name || !form.value.name.trim()) {
    uiStore.showError('El nombre es requerido')
    return
  }
  
  loading.value = true
  
  try {
    const categoryData = {
      name: form.value.name.trim(),
      color: form.value.color || '#6366F1',
      icon: form.value.icon || 'otros',
    }
    
    if (isEditing.value) {
      await secondaryCategoriesStore.updateSecondaryCategory(editingCategory.value.id, categoryData)
      uiStore.showSuccess('Categoría secundaria actualizada')
    } else {
      await secondaryCategoriesStore.createSecondaryCategory(categoryData)
      uiStore.showSuccess('Categoría secundaria creada')
    }
    
    showModal.value = false
  } catch (error) {
    const errorMessage = error.message || error.response?.data?.detail || 'Error al guardar'
    uiStore.showError(errorMessage)
  } finally {
    loading.value = false
  }
}

async function deleteCategory() {
  if (!categoryToDelete.value) return
  
  try {
    await secondaryCategoriesStore.deleteSecondaryCategory(categoryToDelete.value.id)
    await secondaryCategoriesStore.fetchSecondaryCategories()
    uiStore.showSuccess('Categoría secundaria eliminada')
  } catch (error) {
    uiStore.showError(error.message || 'Error al eliminar')
  } finally {
    showDeleteModal.value = false
    categoryToDelete.value = null
  }
}

onMounted(() => {
  secondaryCategoriesStore.fetchSecondaryCategories()
})
</script>

<template>
  <div class="space-y-6 animate-fade-in">
    <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
      <div>
        <h1 class="font-display text-2xl lg:text-3xl font-bold text-slate-900 dark:text-white">
          Categorías Secundarias
        </h1>
        <p class="mt-1 text-slate-600 dark:text-slate-400">
          Etiquetas adicionales para tus transacciones
        </p>
      </div>
      <button @click="openNewCategory" class="btn-primary">
        <PlusIcon class="w-5 h-5" />
        Nueva categoría secundaria
      </button>
    </div>
    
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      <div
        v-for="category in secondaryCategoriesStore.secondaryCategories"
        :key="category.id"
        class="card p-4 hover:shadow-md transition-shadow group"
      >
        <div class="flex items-center justify-between">
          <div class="flex items-center gap-3">
            <div
              class="w-12 h-12 rounded-xl flex items-center justify-center"
              :style="{ backgroundColor: category.color + '20' }"
            >
              <CategoryIcon 
                :icon="category.icon || 'otros'" 
                class="w-7 h-7"
                :style="{ color: category.color }"
              />
            </div>
            <div>
              <h3 class="font-medium text-slate-900 dark:text-white">{{ category.name }}</h3>
            </div>
          </div>
          
          <div class="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
            <button
              @click="openEditCategory(category)"
              class="p-2 rounded-lg hover:bg-slate-100 dark:hover:bg-slate-800 text-slate-600"
            >
              <PencilIcon class="w-4 h-4" />
            </button>
            <button
              @click="confirmDeleteCategory(category)"
              class="p-2 rounded-lg hover:bg-red-100 dark:hover:bg-red-900/30 text-red-600"
            >
              <TrashIcon class="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>
    </div>
    
    <div v-if="secondaryCategoriesStore.secondaryCategories.length === 0" class="text-center py-12">
      <TagIcon class="w-12 h-12 mx-auto text-slate-300 dark:text-slate-600" />
      <p class="mt-4 text-slate-500 dark:text-slate-400">No hay categorías secundarias</p>
      <p class="mt-2 text-sm text-slate-400 dark:text-slate-500">
        Crea categorías secundarias para etiquetar tus transacciones de manera más específica
      </p>
    </div>
    
    <Modal v-if="showModal" :title="isEditing ? 'Editar categoría secundaria' : 'Nueva categoría secundaria'" @close="showModal = false">
      <form @submit.prevent="handleSubmit" class="space-y-5">
        <div>
          <label class="label">Nombre *</label>
          <input
            v-model="form.name"
            type="text"
            placeholder="Ej: Proteína, Leche, etc."
            class="input"
            required
          />
        </div>
        
        <div>
          <label class="label">Color</label>
          <div class="flex gap-2 flex-wrap">
            <button
              v-for="color in colors"
              :key="color"
              type="button"
              @click="form.color = color"
              :class="form.color === color && 'ring-2 ring-offset-2 ring-slate-400'"
              :style="{ backgroundColor: color }"
              class="w-8 h-8 rounded-full transition-all"
            />
          </div>
        </div>
        
        <IconSelector v-model="form.icon" />
      </form>
      
      <template #footer>
        <div class="flex justify-end gap-3">
          <button @click="showModal = false" class="btn-secondary">Cancelar</button>
          <button @click="handleSubmit" :disabled="loading" class="btn-primary">
            {{ loading ? 'Guardando...' : isEditing ? 'Actualizar' : 'Crear' }}
          </button>
        </div>
      </template>
    </Modal>
    
    <Modal v-if="showDeleteModal" title="Eliminar categoría secundaria" @close="showDeleteModal = false">
      <p class="text-slate-600 dark:text-slate-400">
        ¿Estás seguro de eliminar "{{ categoryToDelete?.name }}"?
      </p>
      <template #footer>
        <div class="flex justify-end gap-3">
          <button @click="showDeleteModal = false" class="btn-secondary">Cancelar</button>
          <button @click="deleteCategory" class="btn-danger">Eliminar</button>
        </div>
      </template>
    </Modal>
  </div>
</template>


