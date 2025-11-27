<script setup>
import { ref, onMounted } from 'vue'
import { useAccountsStore } from '@/stores/accounts'
import { useCategoriesStore } from '@/stores/categories'
import { useUiStore } from '@/stores/ui'
import api from '@/services/api'
import { formatMoney, formatDate as formatDateUtil } from '@/composables/useCurrency'
import Modal from '@/components/Modal.vue'
import { 
  PlusIcon, 
  PencilIcon, 
  TrashIcon, 
  ArrowPathIcon,
  PlayIcon,
  PauseIcon
} from '@heroicons/vue/24/outline'

const accountsStore = useAccountsStore()
const categoriesStore = useCategoriesStore()
const uiStore = useUiStore()

const recurring = ref([])
const loading = ref(true)
const showModal = ref(false)
const showDeleteModal = ref(false)
const editingRecurring = ref(null)
const recurringToDelete = ref(null)
const submitting = ref(false)

const form = ref({
  transaction_type: 'gasto',
  amount: '',
  description: '',
  account: null,
  destination_account: null,
  category: null,
  frequency: 'mensual',
  start_date: new Date().toISOString().split('T')[0],
  next_execution: new Date().toISOString().split('T')[0],
  end_date: '',
})

const frequencies = [
  { value: 'diaria', label: 'Diaria' },
  { value: 'semanal', label: 'Semanal' },
  { value: 'quincenal', label: 'Quincenal' },
  { value: 'mensual', label: 'Mensual' },
  { value: 'anual', label: 'Anual' },
]

async function fetchData() {
  loading.value = true
  try {
    const response = await api.get('/transactions/recurring/')
    recurring.value = response.data.results || response.data
  } catch (error) {
    uiStore.showError('Error al cargar')
  } finally {
    loading.value = false
  }
}

function formatCurrency(value) {
  return formatMoney(value)
}

function formatDate(dateString) {
  return formatDateUtil(dateString)
}

function openNewRecurring() {
  editingRecurring.value = null
  form.value = {
    transaction_type: 'gasto',
    amount: '',
    description: '',
    account: accountsStore.accounts[0]?.id || null,
    destination_account: null,
    category: null,
    frequency: 'mensual',
    start_date: new Date().toISOString().split('T')[0],
    next_execution: new Date().toISOString().split('T')[0],
    end_date: '',
  }
  showModal.value = true
}

function openEditRecurring(rec) {
  editingRecurring.value = rec
  form.value = {
    transaction_type: rec.transaction_type,
    amount: rec.amount,
    description: rec.description,
    account: rec.account,
    destination_account: rec.destination_account,
    category: rec.category,
    frequency: rec.frequency,
    start_date: rec.start_date,
    next_execution: rec.next_execution,
    end_date: rec.end_date || '',
  }
  showModal.value = true
}

function confirmDelete(rec) {
  recurringToDelete.value = rec
  showDeleteModal.value = true
}

async function handleSubmit() {
  if (!form.value.description || !form.value.amount || !form.value.account) {
    uiStore.showError('Completa los campos requeridos')
    return
  }
  
  submitting.value = true
  
  try {
    const data = {
      ...form.value,
      amount: parseFloat(form.value.amount),
      end_date: form.value.end_date || null,
    }
    
    if (editingRecurring.value) {
      await api.patch(`/transactions/recurring/${editingRecurring.value.id}/`, data)
      uiStore.showSuccess('Actualizado')
    } else {
      await api.post('/transactions/recurring/', data)
      uiStore.showSuccess('Creado')
    }
    
    showModal.value = false
    fetchData()
  } catch (error) {
    uiStore.showError('Error al guardar')
  } finally {
    submitting.value = false
  }
}

async function toggleActive(rec) {
  try {
    await api.post(`/transactions/recurring/${rec.id}/toggle_active/`)
    fetchData()
    uiStore.showSuccess(rec.is_active ? 'Pausado' : 'Activado')
  } catch (error) {
    uiStore.showError('Error')
  }
}

async function deleteRecurring() {
  if (!recurringToDelete.value) return
  
  try {
    await api.delete(`/transactions/recurring/${recurringToDelete.value.id}/`)
    uiStore.showSuccess('Eliminado')
    fetchData()
  } catch (error) {
    uiStore.showError('Error')
  } finally {
    showDeleteModal.value = false
    recurringToDelete.value = null
  }
}

onMounted(async () => {
  await Promise.all([
    fetchData(),
    accountsStore.fetchAccounts(),
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
          Transacciones Recurrentes
        </h1>
        <p class="mt-1 text-slate-600 dark:text-slate-400">
          Automatiza tus gastos e ingresos periódicos
        </p>
      </div>
      <button @click="openNewRecurring" class="btn-primary">
        <PlusIcon class="w-5 h-5" />
        Nueva recurrente
      </button>
    </div>
    
    <!-- List -->
    <div class="space-y-4">
      <div
        v-for="rec in recurring"
        :key="rec.id"
        class="card p-5 hover:shadow-md transition-shadow"
        :class="!rec.is_active && 'opacity-60'"
      >
        <div class="flex items-start justify-between">
          <div class="flex items-center gap-3">
            <div 
              class="w-10 h-10 rounded-xl flex items-center justify-center"
              :class="rec.transaction_type === 'ingreso' ? 'bg-emerald-100 dark:bg-emerald-900/30' : 'bg-red-100 dark:bg-red-900/30'"
            >
              <ArrowPathIcon 
                class="w-5 h-5"
                :class="rec.transaction_type === 'ingreso' ? 'text-emerald-600' : 'text-red-600'"
              />
            </div>
            <div>
              <h3 class="font-medium text-slate-900 dark:text-white">{{ rec.description }}</h3>
              <p class="text-sm text-slate-500">
                {{ rec.frequency_display }} · {{ rec.account_name }}
              </p>
            </div>
          </div>
          
          <div class="flex items-center gap-2">
            <span 
              :class="[
                'text-lg font-semibold',
                rec.transaction_type === 'ingreso' ? 'text-emerald-600' : 'text-red-600'
              ]"
            >
              {{ rec.transaction_type === 'ingreso' ? '+' : '-' }}{{ formatCurrency(rec.amount) }}
            </span>
          </div>
        </div>
        
        <div class="mt-4 flex items-center justify-between">
          <div class="text-sm text-slate-500">
            Próxima ejecución: <strong>{{ formatDate(rec.next_execution) }}</strong>
          </div>
          
          <div class="flex items-center gap-1">
            <button
              @click="toggleActive(rec)"
              :class="[
                'p-2 rounded-lg transition-colors',
                rec.is_active 
                  ? 'hover:bg-amber-100 text-amber-600' 
                  : 'hover:bg-emerald-100 text-emerald-600'
              ]"
              :title="rec.is_active ? 'Pausar' : 'Activar'"
            >
              <PauseIcon v-if="rec.is_active" class="w-4 h-4" />
              <PlayIcon v-else class="w-4 h-4" />
            </button>
            <button
              @click="openEditRecurring(rec)"
              class="p-2 rounded-lg hover:bg-slate-100 dark:hover:bg-slate-800 text-slate-600"
            >
              <PencilIcon class="w-4 h-4" />
            </button>
            <button
              @click="confirmDelete(rec)"
              class="p-2 rounded-lg hover:bg-red-100 dark:hover:bg-red-900/30 text-red-600"
            >
              <TrashIcon class="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Empty State -->
    <div v-if="!loading && recurring.length === 0" class="text-center py-12">
      <ArrowPathIcon class="w-12 h-12 mx-auto text-slate-300 dark:text-slate-600" />
      <h3 class="mt-4 font-medium text-slate-900 dark:text-white">Sin recurrentes</h3>
      <p class="text-slate-500 mt-1">Crea transacciones que se repitan automáticamente</p>
      <button @click="openNewRecurring" class="btn-primary mt-4">
        Crear recurrente
      </button>
    </div>
    
    <!-- Modal -->
    <Modal v-if="showModal" :title="editingRecurring ? 'Editar recurrente' : 'Nueva recurrente'" @close="showModal = false">
      <form @submit.prevent="handleSubmit" class="space-y-4">
        <div>
          <label class="label">Tipo</label>
          <div class="grid grid-cols-2 gap-2">
            <button
              type="button"
              @click="form.transaction_type = 'gasto'"
              :class="[
                'px-4 py-2.5 rounded-xl font-medium transition-all',
                form.transaction_type === 'gasto' ? 'bg-red-100 text-red-600' : 'bg-slate-100 text-slate-600'
              ]"
            >
              Gasto
            </button>
            <button
              type="button"
              @click="form.transaction_type = 'ingreso'"
              :class="[
                'px-4 py-2.5 rounded-xl font-medium transition-all',
                form.transaction_type === 'ingreso' ? 'bg-emerald-100 text-emerald-600' : 'bg-slate-100 text-slate-600'
              ]"
            >
              Ingreso
            </button>
          </div>
        </div>
        
        <div>
          <label class="label">Descripción *</label>
          <input v-model="form.description" type="text" placeholder="Ej: Suscripción Netflix" class="input" required />
        </div>
        
        <div class="grid grid-cols-2 gap-4">
          <div>
            <label class="label">Monto *</label>
            <input v-model="form.amount" type="number" step="1" class="input" required />
          </div>
          <div>
            <label class="label">Frecuencia</label>
            <select v-model="form.frequency" class="input">
              <option v-for="f in frequencies" :key="f.value" :value="f.value">{{ f.label }}</option>
            </select>
          </div>
        </div>
        
        <div>
          <label class="label">Cuenta *</label>
          <select v-model="form.account" class="input" required>
            <option v-for="acc in accountsStore.accounts" :key="acc.id" :value="acc.id">
              {{ acc.name }}
            </option>
          </select>
        </div>
        
        <div v-if="form.transaction_type !== 'transferencia'">
          <label class="label">Categoría</label>
          <select v-model="form.category" class="input">
            <option :value="null">Sin categoría</option>
            <option 
              v-for="cat in form.transaction_type === 'ingreso' ? categoriesStore.incomeCategories : categoriesStore.expenseCategories" 
              :key="cat.id" 
              :value="cat.id"
            >
              {{ cat.name }}
            </option>
          </select>
        </div>
        
        <div class="grid grid-cols-2 gap-4">
          <div>
            <label class="label">Primera ejecución</label>
            <input v-model="form.next_execution" type="date" class="input" />
          </div>
          <div>
            <label class="label">Fecha fin (opcional)</label>
            <input v-model="form.end_date" type="date" class="input" />
          </div>
        </div>
      </form>
      
      <template #footer>
        <div class="flex justify-end gap-3">
          <button @click="showModal = false" class="btn-secondary">Cancelar</button>
          <button @click="handleSubmit" :disabled="submitting" class="btn-primary">
            {{ submitting ? 'Guardando...' : editingRecurring ? 'Actualizar' : 'Crear' }}
          </button>
        </div>
      </template>
    </Modal>
    
    <!-- Delete Modal -->
    <Modal v-if="showDeleteModal" title="Eliminar recurrente" @close="showDeleteModal = false">
      <p class="text-slate-600 dark:text-slate-400">
        ¿Estás seguro de eliminar "{{ recurringToDelete?.description }}"?
      </p>
      <template #footer>
        <div class="flex justify-end gap-3">
          <button @click="showDeleteModal = false" class="btn-secondary">Cancelar</button>
          <button @click="deleteRecurring" class="btn-danger">Eliminar</button>
        </div>
      </template>
    </Modal>
  </div>
</template>

