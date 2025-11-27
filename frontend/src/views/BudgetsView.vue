<script setup>
import { ref, onMounted, computed } from 'vue'
import { useBudgetsStore } from '@/stores/budgets'
import { useCategoriesStore } from '@/stores/categories'
import { useUiStore } from '@/stores/ui'
import { formatMoney } from '@/composables/useCurrency'
import Modal from '@/components/Modal.vue'
import { PlusIcon, PencilIcon, TrashIcon, ChartBarIcon } from '@heroicons/vue/24/outline'

const budgetsStore = useBudgetsStore()
const categoriesStore = useCategoriesStore()
const uiStore = useUiStore()

const showModal = ref(false)
const showDeleteModal = ref(false)
const editingBudget = ref(null)
const budgetToDelete = ref(null)
const loading = ref(false)

const form = ref({
  category: null,
  amount_limit: '',
  period: 'mensual',
  start_date: new Date().toISOString().split('T')[0],
  alert_threshold: 80,
})

const periods = [
  { value: 'semanal', label: 'Semanal' },
  { value: 'mensual', label: 'Mensual' },
  { value: 'anual', label: 'Anual' },
]

const isEditing = computed(() => !!editingBudget.value)

function formatCurrency(value) {
  return formatMoney(value)
}

function getProgressColor(percentage, isExceeded, isWarning) {
  if (isExceeded) return 'bg-red-500'
  if (isWarning) return 'bg-amber-500'
  return 'bg-emerald-500'
}

function openNewBudget() {
  editingBudget.value = null
  form.value = {
    category: null,
    amount_limit: '',
    period: 'mensual',
    start_date: new Date().toISOString().split('T')[0],
    alert_threshold: 80,
  }
  showModal.value = true
}

function openEditBudget(budget) {
  editingBudget.value = budget
  form.value = {
    category: budget.category,
    amount_limit: budget.amount_limit,
    period: budget.period,
    start_date: budget.start_date,
    alert_threshold: budget.alert_threshold,
  }
  showModal.value = true
}

function confirmDeleteBudget(budget) {
  budgetToDelete.value = budget
  showDeleteModal.value = true
}

async function handleSubmit() {
  if (!form.value.category || !form.value.amount_limit) {
    uiStore.showError('Completa los campos requeridos')
    return
  }
  
  loading.value = true
  
  try {
    const data = {
      ...form.value,
      amount_limit: parseFloat(form.value.amount_limit),
    }
    
    if (isEditing.value) {
      await budgetsStore.updateBudget(editingBudget.value.id, data)
      uiStore.showSuccess('Presupuesto actualizado')
    } else {
      await budgetsStore.createBudget(data)
      uiStore.showSuccess('Presupuesto creado')
    }
    showModal.value = false
  } catch (error) {
    uiStore.showError('Error al guardar')
  } finally {
    loading.value = false
  }
}

async function deleteBudget() {
  if (!budgetToDelete.value) return
  
  try {
    await budgetsStore.deleteBudget(budgetToDelete.value.id)
    uiStore.showSuccess('Presupuesto eliminado')
  } catch (error) {
    uiStore.showError('Error al eliminar')
  } finally {
    showDeleteModal.value = false
    budgetToDelete.value = null
  }
}

onMounted(async () => {
  await Promise.all([
    budgetsStore.fetchBudgets(),
    categoriesStore.fetchCategories(),
  ])
})
</script>

<template>
  <div class="space-y-6 animate-fade-in">
    <!-- Header -->
    <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
      <div>
        <h1 class="font-display text-2xl lg:text-3xl font-bold text-slate-900 dark:text-white">
          Presupuestos
        </h1>
        <p class="mt-1 text-slate-600 dark:text-slate-400">
          Controla tus gastos con límites por categoría
        </p>
      </div>
      <button @click="openNewBudget" class="btn-primary">
        <PlusIcon class="w-5 h-5" />
        Nuevo presupuesto
      </button>
    </div>
    
    <!-- Budgets Grid -->
    <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
      <div
        v-for="budget in budgetsStore.budgets"
        :key="budget.id"
        class="card p-5 hover:shadow-md transition-shadow"
      >
        <div class="flex items-start justify-between">
          <div class="flex items-center gap-3">
            <div
              class="w-10 h-10 rounded-xl flex items-center justify-center"
              :style="{ backgroundColor: budget.category_color + '20' }"
            >
              <ChartBarIcon class="w-5 h-5" :style="{ color: budget.category_color }" />
            </div>
            <div>
              <h3 class="font-medium text-slate-900 dark:text-white">{{ budget.category_name }}</h3>
              <p class="text-sm text-slate-500">{{ budget.period_display }}</p>
            </div>
          </div>
          
          <div class="flex items-center gap-1">
            <button
              @click="openEditBudget(budget)"
              class="p-2 rounded-lg hover:bg-slate-100 dark:hover:bg-slate-800 text-slate-600"
            >
              <PencilIcon class="w-4 h-4" />
            </button>
            <button
              @click="confirmDeleteBudget(budget)"
              class="p-2 rounded-lg hover:bg-red-100 dark:hover:bg-red-900/30 text-red-600"
            >
              <TrashIcon class="w-4 h-4" />
            </button>
          </div>
        </div>
        
        <!-- Progress -->
        <div class="mt-4">
          <div class="flex justify-between text-sm mb-2">
            <span class="text-slate-600 dark:text-slate-400">
              {{ formatCurrency(budget.spent) }} de {{ formatCurrency(budget.amount_limit) }}
            </span>
            <span 
              :class="[
                'font-medium',
                budget.is_exceeded ? 'text-red-600' : budget.is_warning ? 'text-amber-600' : 'text-emerald-600'
              ]"
            >
              {{ budget.percentage.toFixed(0) }}%
            </span>
          </div>
          
          <div class="h-3 bg-slate-100 dark:bg-slate-800 rounded-full overflow-hidden">
            <div
              :class="getProgressColor(budget.percentage, budget.is_exceeded, budget.is_warning)"
              class="h-full rounded-full transition-all duration-500"
              :style="{ width: Math.min(budget.percentage, 100) + '%' }"
            />
          </div>
          
          <p class="mt-2 text-sm" :class="budget.remaining >= 0 ? 'text-slate-500' : 'text-red-500'">
            {{ budget.remaining >= 0 ? 'Restante:' : 'Excedido:' }}
            {{ formatCurrency(Math.abs(budget.remaining)) }}
          </p>
        </div>
        
        <!-- Alert Badge -->
        <div v-if="budget.is_exceeded" class="mt-3">
          <span class="text-xs px-2 py-1 rounded-full bg-red-100 dark:bg-red-900/30 text-red-600">
            ⚠️ Presupuesto excedido
          </span>
        </div>
        <div v-else-if="budget.is_warning" class="mt-3">
          <span class="text-xs px-2 py-1 rounded-full bg-amber-100 dark:bg-amber-900/30 text-amber-600">
            ⚠️ Cerca del límite
          </span>
        </div>
      </div>
    </div>
    
    <!-- Empty State -->
    <div v-if="budgetsStore.budgets.length === 0" class="text-center py-12">
      <ChartBarIcon class="w-12 h-12 mx-auto text-slate-300 dark:text-slate-600" />
      <h3 class="mt-4 font-medium text-slate-900 dark:text-white">Sin presupuestos</h3>
      <p class="text-slate-500 mt-1">Crea un presupuesto para controlar tus gastos</p>
      <button @click="openNewBudget" class="btn-primary mt-4">
        Crear presupuesto
      </button>
    </div>
    
    <!-- Budget Modal -->
    <Modal v-if="showModal" :title="isEditing ? 'Editar presupuesto' : 'Nuevo presupuesto'" @close="showModal = false">
      <form @submit.prevent="handleSubmit" class="space-y-5">
        <div>
          <label class="label">Categoría *</label>
          <select v-model="form.category" class="input" required>
            <option :value="null" disabled>Selecciona categoría</option>
            <option v-for="cat in categoriesStore.expenseCategories" :key="cat.id" :value="cat.id">
              {{ cat.name }}
            </option>
          </select>
        </div>
        
        <div>
          <label class="label">Límite *</label>
          <div class="relative">
            <span class="absolute left-4 top-1/2 -translate-y-1/2 text-slate-400">$</span>
            <input
              v-model="form.amount_limit"
              type="number"
              step="1"
              min="0"
              placeholder="0"
              class="input pl-10"
              required
            />
          </div>
        </div>
        
        <div>
          <label class="label">Período</label>
          <select v-model="form.period" class="input">
            <option v-for="p in periods" :key="p.value" :value="p.value">
              {{ p.label }}
            </option>
          </select>
        </div>
        
        <div>
          <label class="label">Umbral de alerta (%)</label>
          <input
            v-model="form.alert_threshold"
            type="number"
            min="50"
            max="100"
            class="input"
          />
          <p class="text-xs text-slate-500 mt-1">
            Recibirás alertas cuando superes este porcentaje
          </p>
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
    <Modal v-if="showDeleteModal" title="Eliminar presupuesto" @close="showDeleteModal = false">
      <p class="text-slate-600 dark:text-slate-400">
        ¿Estás seguro de eliminar este presupuesto?
      </p>
      <template #footer>
        <div class="flex justify-end gap-3">
          <button @click="showDeleteModal = false" class="btn-secondary">Cancelar</button>
          <button @click="deleteBudget" class="btn-danger">Eliminar</button>
        </div>
      </template>
    </Modal>
  </div>
</template>

