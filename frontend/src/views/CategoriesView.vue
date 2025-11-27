<script setup>
import { ref, onMounted, computed } from 'vue'
import { useCategoriesStore } from '@/stores/categories'
import { useUiStore } from '@/stores/ui'
import Modal from '@/components/Modal.vue'
import { PlusIcon, PencilIcon, TrashIcon, TagIcon, ChevronRightIcon } from '@heroicons/vue/24/outline'

const categoriesStore = useCategoriesStore()
const uiStore = useUiStore()

const showModal = ref(false)
const showDeleteModal = ref(false)
const editingCategory = ref(null)
const categoryToDelete = ref(null)
const activeTab = ref('gasto')
const loading = ref(false)
const isCreatingSubcategory = ref(false)
const parentCategory = ref(null)

const form = ref({
  name: '',
  category_type: 'gasto',
  color: '#6366F1',
  icon: 'tag',
  parent: null,
})

const colors = [
  '#EF4444', '#F59E0B', '#22C55E', '#3B82F6', '#8B5CF6',
  '#EC4899', '#14B8A6', '#6366F1', '#64748B', '#0EA5E9'
]

const isEditing = computed(() => !!editingCategory.value)

const filteredCategories = computed(() => {
  return categoriesStore.categories.filter(
    c => c.category_type === activeTab.value && !c.parent
  )
})

const modalTitle = computed(() => {
  if (isCreatingSubcategory.value) {
    return `Nueva subcategoría de "${parentCategory.value?.name}"`
  }
  return isEditing.value ? 'Editar categoría' : 'Nueva categoría'
})

function openNewCategory() {
  editingCategory.value = null
  isCreatingSubcategory.value = false
  parentCategory.value = null
  form.value = {
    name: '',
    category_type: activeTab.value,
    color: '#6366F1',
    icon: 'tag',
    parent: null,
  }
  showModal.value = true
}

function openNewSubcategory(category) {
  editingCategory.value = null
  isCreatingSubcategory.value = true
  parentCategory.value = category
  form.value = {
    name: '',
    category_type: category.category_type,
    color: category.color,
    icon: 'tag',
    parent: category.id,
  }
  showModal.value = true
}

function openEditCategory(category) {
  if (category.is_default) {
    uiStore.showWarning('No puedes editar categorías predeterminadas')
    return
  }
  editingCategory.value = category
  isCreatingSubcategory.value = false
  parentCategory.value = null
  form.value = {
    name: category.name,
    category_type: category.category_type,
    color: category.color,
    icon: category.icon,
    parent: category.parent,
  }
  showModal.value = true
}

function confirmDeleteCategory(category) {
  if (category.is_default) {
    uiStore.showWarning('No puedes eliminar categorías predeterminadas')
    return
  }
  categoryToDelete.value = category
  showDeleteModal.value = true
}

async function handleSubmit() {
  if (!form.value.name) {
    uiStore.showError('El nombre es requerido')
    return
  }
  
  loading.value = true
  
  try {
    if (isEditing.value) {
      await categoriesStore.updateCategory(editingCategory.value.id, form.value)
      uiStore.showSuccess('Categoría actualizada')
    } else {
      await categoriesStore.createCategory(form.value)
      uiStore.showSuccess('Categoría creada')
    }
    showModal.value = false
  } catch (error) {
    uiStore.showError(error.message || 'Error al guardar')
  } finally {
    loading.value = false
  }
}

async function deleteCategory() {
  if (!categoryToDelete.value) return
  
  try {
    await categoriesStore.deleteCategory(categoryToDelete.value.id)
    uiStore.showSuccess('Categoría eliminada')
  } catch (error) {
    uiStore.showError(error.message || 'Error al eliminar')
  } finally {
    showDeleteModal.value = false
    categoryToDelete.value = null
  }
}

onMounted(() => {
  categoriesStore.fetchCategories()
})
</script>

<template>
  <div class="space-y-6 animate-fade-in">
    <!-- Header -->
    <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
      <div>
        <h1 class="font-display text-2xl lg:text-3xl font-bold text-slate-900 dark:text-white">
          Categorías
        </h1>
        <p class="mt-1 text-slate-600 dark:text-slate-400">
          Organiza tus transacciones por categorías
        </p>
      </div>
      <button @click="openNewCategory" class="btn-primary">
        <PlusIcon class="w-5 h-5" />
        Nueva categoría
      </button>
    </div>
    
    <!-- Tabs -->
    <div class="flex gap-2">
      <button
        @click="activeTab = 'gasto'"
        :class="[
          'px-4 py-2 rounded-xl font-medium transition-all',
          activeTab === 'gasto'
            ? 'bg-red-100 dark:bg-red-900/30 text-red-600 dark:text-red-400'
            : 'bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-400 hover:bg-slate-200'
        ]"
      >
        Gastos
      </button>
      <button
        @click="activeTab = 'ingreso'"
        :class="[
          'px-4 py-2 rounded-xl font-medium transition-all',
          activeTab === 'ingreso'
            ? 'bg-emerald-100 dark:bg-emerald-900/30 text-emerald-600 dark:text-emerald-400'
            : 'bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-400 hover:bg-slate-200'
        ]"
      >
        Ingresos
      </button>
    </div>
    
    <!-- Categories Grid -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      <div
        v-for="category in filteredCategories"
        :key="category.id"
        class="card p-4 hover:shadow-md transition-shadow group"
      >
        <div class="flex items-start justify-between">
          <div class="flex items-center gap-3">
            <div
              class="w-10 h-10 rounded-xl flex items-center justify-center"
              :style="{ backgroundColor: category.color + '20' }"
            >
              <TagIcon class="w-5 h-5" :style="{ color: category.color }" />
            </div>
            <div>
              <h3 class="font-medium text-slate-900 dark:text-white">{{ category.name }}</h3>
              <p v-if="category.is_default" class="text-xs text-slate-500">Predeterminada</p>
            </div>
          </div>
          
          <div v-if="!category.is_default" class="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
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
        
        <!-- Subcategories -->
        <div class="mt-3 pt-3 border-t border-slate-100 dark:border-slate-800">
          <div class="flex items-center justify-between mb-2">
            <p class="text-xs text-slate-500">Subcategorías</p>
            <button
              @click="openNewSubcategory(category)"
              class="text-xs text-primary-600 hover:text-primary-700 flex items-center gap-1"
            >
              <PlusIcon class="w-3 h-3" />
              Agregar
            </button>
          </div>
          <div v-if="category.subcategories?.length" class="space-y-1">
            <div
              v-for="sub in category.subcategories"
              :key="sub.id"
              class="flex items-center justify-between py-1.5 px-2 rounded-lg hover:bg-slate-50 dark:hover:bg-slate-800/50 group/sub"
            >
              <div class="flex items-center gap-2">
                <ChevronRightIcon class="w-3 h-3 text-slate-400" />
                <span
                  class="text-sm px-2 py-0.5 rounded-full"
                  :style="{ backgroundColor: sub.color + '20', color: sub.color }"
                >
                  {{ sub.name }}
                </span>
              </div>
              <div class="flex items-center gap-1 opacity-0 group-hover/sub:opacity-100 transition-opacity">
                <button
                  @click="openEditCategory(sub)"
                  class="p-1 rounded hover:bg-slate-200 dark:hover:bg-slate-700 text-slate-500"
                >
                  <PencilIcon class="w-3 h-3" />
                </button>
                <button
                  @click="confirmDeleteCategory(sub)"
                  class="p-1 rounded hover:bg-red-100 dark:hover:bg-red-900/30 text-red-500"
                >
                  <TrashIcon class="w-3 h-3" />
                </button>
              </div>
            </div>
          </div>
          <p v-else class="text-xs text-slate-400 italic">Sin subcategorías</p>
        </div>
      </div>
    </div>
    
    <!-- Empty State -->
    <div v-if="filteredCategories.length === 0" class="text-center py-12">
      <TagIcon class="w-12 h-12 mx-auto text-slate-300 dark:text-slate-600" />
      <p class="mt-4 text-slate-500 dark:text-slate-400">No hay categorías de este tipo</p>
    </div>
    
    <!-- Category Modal -->
    <Modal v-if="showModal" :title="modalTitle" @close="showModal = false">
      <form @submit.prevent="handleSubmit" class="space-y-5">
        <div>
          <label class="label">Nombre *</label>
          <input
            v-model="form.name"
            type="text"
            placeholder="Ej: Alimentación"
            class="input"
            required
          />
        </div>
        
        <div>
          <label class="label">Tipo</label>
          <div class="grid grid-cols-2 gap-2">
            <button
              type="button"
              @click="form.category_type = 'gasto'"
              :class="[
                'px-4 py-2.5 rounded-xl font-medium transition-all',
                form.category_type === 'gasto'
                  ? 'bg-red-100 dark:bg-red-900/30 text-red-600'
                  : 'bg-slate-100 dark:bg-slate-800 text-slate-600'
              ]"
            >
              Gasto
            </button>
            <button
              type="button"
              @click="form.category_type = 'ingreso'"
              :class="[
                'px-4 py-2.5 rounded-xl font-medium transition-all',
                form.category_type === 'ingreso'
                  ? 'bg-emerald-100 dark:bg-emerald-900/30 text-emerald-600'
                  : 'bg-slate-100 dark:bg-slate-800 text-slate-600'
              ]"
            >
              Ingreso
            </button>
          </div>
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
    
    <!-- Delete Modal -->
    <Modal v-if="showDeleteModal" title="Eliminar categoría" @close="showDeleteModal = false">
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

