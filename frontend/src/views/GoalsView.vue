<script setup>
import { ref, onMounted, computed } from 'vue'
import { useGoalsStore } from '@/stores/goals'
import { useCategoriesStore } from '@/stores/categories'
import { useUiStore } from '@/stores/ui'
import { formatMoney } from '@/composables/useCurrency'
import Modal from '@/components/Modal.vue'
import GoalCard from '@/components/GoalCard.vue'
import { PlusIcon, FunnelIcon } from '@heroicons/vue/24/outline'

const goalsStore = useGoalsStore()
const categoriesStore = useCategoriesStore()
const uiStore = useUiStore()

const showModal = ref(false)
const showDeleteModal = ref(false)
const editingGoal = ref(null)
const goalToDelete = ref(null)
const loading = ref(false)
const filterType = ref('all')

const form = ref({
  name: '',
  goal_type: 'savings',
  target_amount: '',
  target_date: '',
  category: null,
  reduction_percentage: '',
  baseline_amount: '',
  description: '',
})

const goalTypes = [
  { value: 'savings', label: 'Meta de Ahorro' },
  { value: 'category_reduction', label: 'Reducción por Categoría' },
]

const isEditing = computed(() => !!editingGoal.value)

const filteredGoals = computed(() => {
  let goals = [...goalsStore.goals]
  
  if (filterType.value === 'active') {
    goals = goals.filter(g => g.is_active)
  } else if (filterType.value === 'completed') {
    goals = goals.filter(g => g.is_active && g.is_completed)
  } else if (filterType.value === 'savings') {
    goals = goals.filter(g => g.goal_type === 'savings')
  } else if (filterType.value === 'reduction') {
    goals = goals.filter(g => g.goal_type === 'category_reduction')
  }
  
  return goals.sort((a, b) => {
    if (a.is_active !== b.is_active) return a.is_active ? -1 : 1
    if (a.is_completed !== b.is_completed) return a.is_completed ? 1 : -1
    return new Date(b.created_at) - new Date(a.created_at)
  })
})

const expenseCategories = computed(() => {
  return categoriesStore.categories.filter(c => c.category_type === 'gasto')
})

function openNewGoal() {
  editingGoal.value = null
  form.value = {
    name: '',
    goal_type: 'savings',
    target_amount: '',
    target_date: '',
    category: null,
    reduction_percentage: '',
    baseline_amount: '',
    description: '',
  }
  showModal.value = true
}

function openEditGoal(goal) {
  editingGoal.value = goal
  form.value = {
    name: goal.name,
    goal_type: goal.goal_type,
    target_amount: goal.target_amount,
    target_date: goal.target_date,
    category: goal.category,
    reduction_percentage: goal.reduction_percentage || '',
    baseline_amount: goal.baseline_amount || '',
    description: goal.description || '',
  }
  showModal.value = true
}

function confirmDeleteGoal(goal) {
  goalToDelete.value = goal
  showDeleteModal.value = true
}

async function handleSubmit() {
  if (!form.value.name || !form.value.target_amount || !form.value.target_date) {
    uiStore.showError('Completa los campos requeridos')
    return
  }
  
  if (form.value.goal_type === 'category_reduction' && !form.value.category) {
    uiStore.showError('Selecciona una categoría para metas de reducción')
    return
  }
  
  loading.value = true
  
  try {
    const data = {
      name: form.value.name,
      goal_type: form.value.goal_type,
      target_amount: parseFloat(form.value.target_amount),
      target_date: form.value.target_date,
      description: form.value.description,
    }
    
    if (form.value.goal_type === 'category_reduction') {
      data.category = form.value.category
      if (form.value.reduction_percentage) {
        data.reduction_percentage = parseFloat(form.value.reduction_percentage)
      }
      if (form.value.baseline_amount) {
        data.baseline_amount = parseFloat(form.value.baseline_amount)
      }
    }
    
    if (isEditing.value) {
      await goalsStore.updateGoal(editingGoal.value.id, data)
      uiStore.showSuccess('Meta actualizada')
    } else {
      await goalsStore.createGoal(data)
      uiStore.showSuccess('Meta creada')
    }
    showModal.value = false
  } catch (error) {
    const errorMessage = error.response?.data?.detail || error.response?.data?.message || 'Error al guardar'
    uiStore.showError(errorMessage)
  } finally {
    loading.value = false
  }
}

function closeDeleteModal() {
  showDeleteModal.value = false
  goalToDelete.value = null
}

async function deleteGoal() {
  if (!goalToDelete.value) return
  
  try {
    await goalsStore.deleteGoal(goalToDelete.value.id)
    uiStore.showSuccess('Meta eliminada')
    closeDeleteModal()
  } catch (error) {
    uiStore.showError('Error al eliminar')
  }
}

async function toggleGoalActive(goalId) {
  try {
    await goalsStore.toggleGoalActive(goalId)
    uiStore.showSuccess('Estado de meta actualizado')
  } catch (error) {
    uiStore.showError('Error al cambiar estado')
  }
}

onMounted(async () => {
  await Promise.all([
    goalsStore.fetchGoals(),
    categoriesStore.fetchCategories(),
  ])
})
</script>

<template>
  <div class="space-y-6 animate-fade-in">
    <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
      <div>
        <h1 class="font-display text-2xl lg:text-3xl font-bold text-slate-900 dark:text-white">
          Metas Financieras
        </h1>
        <p class="mt-1 text-slate-600 dark:text-slate-400">
          Establece y alcanza tus objetivos financieros
        </p>
      </div>
      <button @click="openNewGoal" class="btn-primary">
        <PlusIcon class="w-5 h-5" />
        Nueva meta
      </button>
    </div>
    
    <div class="flex items-center gap-3">
      <FunnelIcon class="w-4 h-4 text-slate-400" />
      <div class="flex gap-2 bg-slate-100 dark:bg-slate-800 rounded-xl p-1">
        <button
          @click="filterType = 'all'"
          :class="[
            'px-4 py-2 rounded-lg text-sm font-medium transition-all',
            filterType === 'all'
              ? 'bg-white dark:bg-slate-700 shadow text-slate-900 dark:text-white'
              : 'text-slate-600 dark:text-slate-400 hover:text-slate-900'
          ]"
        >
          Todas
        </button>
        <button
          @click="filterType = 'active'"
          :class="[
            'px-4 py-2 rounded-lg text-sm font-medium transition-all',
            filterType === 'active'
              ? 'bg-white dark:bg-slate-700 shadow text-slate-900 dark:text-white'
              : 'text-slate-600 dark:text-slate-400 hover:text-slate-900'
          ]"
        >
          Activas
        </button>
        <button
          @click="filterType = 'completed'"
          :class="[
            'px-4 py-2 rounded-lg text-sm font-medium transition-all',
            filterType === 'completed'
              ? 'bg-white dark:bg-slate-700 shadow text-slate-900 dark:text-white'
              : 'text-slate-600 dark:text-slate-400 hover:text-slate-900'
          ]"
        >
          Completadas
        </button>
        <button
          @click="filterType = 'savings'"
          :class="[
            'px-4 py-2 rounded-lg text-sm font-medium transition-all',
            filterType === 'savings'
              ? 'bg-white dark:bg-slate-700 shadow text-slate-900 dark:text-white'
              : 'text-slate-600 dark:text-slate-400 hover:text-slate-900'
          ]"
        >
          Ahorro
        </button>
        <button
          @click="filterType = 'reduction'"
          :class="[
            'px-4 py-2 rounded-lg text-sm font-medium transition-all',
            filterType === 'reduction'
              ? 'bg-white dark:bg-slate-700 shadow text-slate-900 dark:text-white'
              : 'text-slate-600 dark:text-slate-400 hover:text-slate-900'
          ]"
        >
          Reducción
        </button>
      </div>
    </div>
    
    <div v-if="goalsStore.loading" class="text-center py-12">
      <div class="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
    </div>
    
    <div v-else-if="filteredGoals.length === 0" class="text-center py-12">
      <p class="text-slate-500 dark:text-slate-400">No hay metas para mostrar</p>
    </div>
    
    <div v-else class="grid grid-cols-1 md:grid-cols-2 gap-6">
      <GoalCard
        v-for="goal in filteredGoals"
        :key="goal.id"
        :goal="goal"
        @edit="openEditGoal"
        @delete="confirmDeleteGoal"
        @toggle="toggleGoalActive"
      />
    </div>
    
    <Modal v-model="showModal" :title="isEditing ? 'Editar Meta' : 'Nueva Meta'">
      <form @submit.prevent="handleSubmit" class="space-y-4">
        <div>
          <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">
            Nombre *
          </label>
          <input
            v-model="form.name"
            type="text"
            required
            class="input"
            placeholder="Ej: Ahorro para vacaciones"
          />
        </div>
        
        <div>
          <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">
            Tipo de Meta *
          </label>
          <select v-model="form.goal_type" class="input" required>
            <option v-for="type in goalTypes" :key="type.value" :value="type.value">
              {{ type.label }}
            </option>
          </select>
        </div>
        
        <div>
          <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">
            Monto Objetivo *
          </label>
          <input
            v-model="form.target_amount"
            type="number"
            step="0.01"
            min="0"
            required
            class="input"
            placeholder="0.00"
          />
        </div>
        
        <div>
          <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">
            Fecha Límite *
          </label>
          <input
            v-model="form.target_date"
            type="date"
            required
            class="input"
          />
        </div>
        
        <div v-if="form.goal_type === 'category_reduction'">
          <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">
            Categoría *
          </label>
          <select v-model="form.category" class="input" required>
            <option :value="null">Selecciona una categoría</option>
            <option
              v-for="category in expenseCategories"
              :key="category.id"
              :value="category.id"
            >
              {{ category.name }}
            </option>
          </select>
        </div>
        
        <div v-if="form.goal_type === 'category_reduction'" class="grid grid-cols-2 gap-4">
          <div>
            <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">
              Porcentaje de Reducción (%)
            </label>
            <input
              v-model="form.reduction_percentage"
              type="number"
              step="0.01"
              min="0"
              max="100"
              class="input"
              placeholder="0.00"
            />
          </div>
          <div>
            <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">
              Monto Base
            </label>
            <input
              v-model="form.baseline_amount"
              type="number"
              step="0.01"
              min="0"
              class="input"
              placeholder="0.00"
            />
          </div>
        </div>
        
        <div>
          <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">
            Descripción
          </label>
          <textarea
            v-model="form.description"
            rows="3"
            class="input"
            placeholder="Descripción opcional de la meta"
          />
        </div>
        
        <div class="flex justify-end gap-3 pt-4">
          <button
            type="button"
            @click="showModal = false"
            class="btn-secondary"
          >
            Cancelar
          </button>
          <button
            type="submit"
            :disabled="loading"
            class="btn-primary"
          >
            {{ loading ? 'Guardando...' : isEditing ? 'Actualizar' : 'Crear' }}
          </button>
        </div>
      </form>
    </Modal>
    
    <Modal v-model="showDeleteModal" title="Eliminar Meta" @close="closeDeleteModal">
      <p v-if="goalToDelete" class="text-slate-600 dark:text-slate-400 mb-6">
        ¿Estás seguro de que deseas eliminar la meta "{{ goalToDelete.name }}"? Esta acción no se puede deshacer.
      </p>
      <div v-else class="text-slate-600 dark:text-slate-400 mb-6">
        Cargando...
      </div>
      <div class="flex justify-end gap-3">
        <button
          @click="closeDeleteModal"
          class="btn-secondary"
        >
          Cancelar
        </button>
        <button
          v-if="goalToDelete"
          @click="deleteGoal"
          class="btn-danger"
        >
          Eliminar
        </button>
      </div>
    </Modal>
  </div>
</template>

