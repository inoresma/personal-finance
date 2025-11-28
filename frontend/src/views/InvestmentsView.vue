<script setup>
import { ref, onMounted } from 'vue'
import { useUiStore } from '@/stores/ui'
import api from '@/services/api'
import { formatMoney } from '@/composables/useCurrency'
import Modal from '@/components/Modal.vue'
import DateInput from '@/components/DateInput.vue'
import { 
  PlusIcon, 
  PencilIcon, 
  TrashIcon, 
  ArrowTrendingUpIcon,
  ArrowTrendingDownIcon,
  PresentationChartLineIcon 
} from '@heroicons/vue/24/outline'

const uiStore = useUiStore()

const investments = ref([])
const summary = ref(null)
const loading = ref(true)
const showModal = ref(false)
const showDeleteModal = ref(false)
const editingInvestment = ref(null)
const investmentToDelete = ref(null)
const submitting = ref(false)

const form = ref({
  name: '',
  investment_type: 'acciones',
  initial_amount: '',
  current_amount: '',
  start_date: new Date().toISOString().split('T')[0],
  expected_return: '',
  notes: '',
})

const investmentTypes = [
  { value: 'acciones', label: 'Acciones' },
  { value: 'fondos', label: 'Fondos de Inversión' },
  { value: 'bonos', label: 'Bonos' },
  { value: 'cripto', label: 'Criptomonedas' },
  { value: 'inmuebles', label: 'Bienes Raíces' },
  { value: 'deposito', label: 'Depósito a Plazo' },
  { value: 'otro', label: 'Otro' },
]

async function fetchData() {
  loading.value = true
  try {
    const [invRes, sumRes] = await Promise.all([
      api.get('/investments/'),
      api.get('/investments/summary/')
    ])
    investments.value = invRes.data.results || invRes.data
    summary.value = sumRes.data
  } catch (error) {
    uiStore.showError('Error al cargar inversiones')
  } finally {
    loading.value = false
  }
}

function formatCurrency(value) {
  return formatMoney(value)
}

function openNewInvestment() {
  editingInvestment.value = null
  form.value = {
    name: '',
    investment_type: 'acciones',
    initial_amount: '',
    current_amount: '',
    start_date: new Date().toISOString().split('T')[0],
    expected_return: '',
    notes: '',
  }
  showModal.value = true
}

function openEditInvestment(inv) {
  editingInvestment.value = inv
  form.value = {
    name: inv.name,
    investment_type: inv.investment_type,
    initial_amount: inv.initial_amount,
    current_amount: inv.current_amount,
    start_date: inv.start_date,
    expected_return: inv.expected_return || '',
    notes: inv.notes || '',
  }
  showModal.value = true
}

function confirmDeleteInvestment(inv) {
  investmentToDelete.value = inv
  showDeleteModal.value = true
}

async function handleSubmit() {
  if (!form.value.name || !form.value.initial_amount) {
    uiStore.showError('Completa los campos requeridos')
    return
  }
  
  submitting.value = true
  
  try {
    const data = {
      ...form.value,
      initial_amount: parseFloat(form.value.initial_amount),
      current_amount: parseFloat(form.value.current_amount || form.value.initial_amount),
      expected_return: form.value.expected_return ? parseFloat(form.value.expected_return) : null,
    }
    
    if (editingInvestment.value) {
      await api.patch(`/investments/${editingInvestment.value.id}/`, data)
      uiStore.showSuccess('Inversión actualizada')
    } else {
      await api.post('/investments/', data)
      uiStore.showSuccess('Inversión creada')
    }
    
    showModal.value = false
    fetchData()
  } catch (error) {
    uiStore.showError('Error al guardar')
  } finally {
    submitting.value = false
  }
}

async function deleteInvestment() {
  if (!investmentToDelete.value) return
  
  try {
    await api.delete(`/investments/${investmentToDelete.value.id}/`)
    uiStore.showSuccess('Inversión eliminada')
    fetchData()
  } catch (error) {
    uiStore.showError('Error al eliminar')
  } finally {
    showDeleteModal.value = false
    investmentToDelete.value = null
  }
}

onMounted(fetchData)
</script>

<template>
  <div class="space-y-6 animate-fade-in">
    <!-- Header -->
    <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
      <div>
        <h1 class="font-display text-2xl lg:text-3xl font-bold text-slate-900 dark:text-white">
          Inversiones
        </h1>
        <p class="mt-1 text-slate-600 dark:text-slate-400">
          Haz seguimiento de tus inversiones
        </p>
      </div>
      <button @click="openNewInvestment" class="btn-primary">
        <PlusIcon class="w-5 h-5" />
        Nueva inversión
      </button>
    </div>
    
    <!-- Summary Cards -->
    <div v-if="summary" class="grid grid-cols-1 md:grid-cols-3 gap-6">
      <div class="card p-6">
        <p class="text-sm text-slate-500 dark:text-slate-400">Total invertido</p>
        <p class="text-2xl font-bold text-slate-900 dark:text-white mt-1">
          {{ formatCurrency(summary.total_invested) }}
        </p>
      </div>
      <div class="card p-6">
        <p class="text-sm text-slate-500 dark:text-slate-400">Valor actual</p>
        <p class="text-2xl font-bold text-slate-900 dark:text-white mt-1">
          {{ formatCurrency(summary.total_current) }}
        </p>
      </div>
      <div class="card p-6">
        <p class="text-sm text-slate-500 dark:text-slate-400">Ganancia/Pérdida</p>
        <div class="flex items-center gap-2 mt-1">
          <p 
            class="text-2xl font-bold"
            :class="summary.total_profit_loss >= 0 ? 'text-emerald-600' : 'text-red-600'"
          >
            {{ formatCurrency(summary.total_profit_loss) }}
          </p>
          <span 
            :class="[
              'text-sm px-2 py-0.5 rounded-full',
              summary.percentage >= 0 
                ? 'bg-emerald-100 text-emerald-600 dark:bg-emerald-900/30' 
                : 'bg-red-100 text-red-600 dark:bg-red-900/30'
            ]"
          >
            {{ summary.percentage >= 0 ? '+' : '' }}{{ summary.percentage }}%
          </span>
        </div>
      </div>
    </div>
    
    <!-- Investments List -->
    <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
      <div
        v-for="inv in investments"
        :key="inv.id"
        class="card p-5 hover:shadow-md transition-shadow group"
      >
        <div class="flex items-start justify-between">
          <div class="flex items-center gap-3">
            <div 
              class="w-10 h-10 rounded-xl flex items-center justify-center"
              :class="inv.profit_loss >= 0 ? 'bg-emerald-100 dark:bg-emerald-900/30' : 'bg-red-100 dark:bg-red-900/30'"
            >
              <component 
                :is="inv.profit_loss >= 0 ? ArrowTrendingUpIcon : ArrowTrendingDownIcon"
                :class="inv.profit_loss >= 0 ? 'text-emerald-600' : 'text-red-600'"
                class="w-5 h-5"
              />
            </div>
            <div>
              <h3 class="font-medium text-slate-900 dark:text-white">{{ inv.name }}</h3>
              <p class="text-sm text-slate-500">{{ inv.investment_type_display }}</p>
            </div>
          </div>
          
          <div class="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
            <button
              @click="openEditInvestment(inv)"
              class="p-2 rounded-lg hover:bg-slate-100 dark:hover:bg-slate-800 text-slate-600"
            >
              <PencilIcon class="w-4 h-4" />
            </button>
            <button
              @click="confirmDeleteInvestment(inv)"
              class="p-2 rounded-lg hover:bg-red-100 dark:hover:bg-red-900/30 text-red-600"
            >
              <TrashIcon class="w-4 h-4" />
            </button>
          </div>
        </div>
        
        <div class="mt-4 grid grid-cols-2 gap-4">
          <div>
            <p class="text-xs text-slate-500">Invertido</p>
            <p class="font-semibold text-slate-900 dark:text-white">
              {{ formatCurrency(inv.initial_amount) }}
            </p>
          </div>
          <div>
            <p class="text-xs text-slate-500">Valor actual</p>
            <p class="font-semibold text-slate-900 dark:text-white">
              {{ formatCurrency(inv.current_amount) }}
            </p>
          </div>
        </div>
        
        <div class="mt-3 pt-3 border-t border-slate-100 dark:border-slate-800 flex justify-between items-center">
          <span class="text-sm text-slate-500">Rendimiento</span>
          <span 
            :class="inv.profit_loss >= 0 ? 'text-emerald-600' : 'text-red-600'"
            class="font-semibold"
          >
            {{ inv.profit_loss >= 0 ? '+' : '' }}{{ formatCurrency(inv.profit_loss) }}
            ({{ inv.profit_loss_percentage >= 0 ? '+' : '' }}{{ parseFloat(inv.profit_loss_percentage).toFixed(1) }}%)
          </span>
        </div>
      </div>
    </div>
    
    <!-- Empty State -->
    <div v-if="!loading && investments.length === 0" class="text-center py-12">
      <PresentationChartLineIcon class="w-12 h-12 mx-auto text-slate-300 dark:text-slate-600" />
      <h3 class="mt-4 font-medium text-slate-900 dark:text-white">Sin inversiones</h3>
      <p class="text-slate-500 mt-1">Registra tus inversiones para hacer seguimiento</p>
      <button @click="openNewInvestment" class="btn-primary mt-4">
        Agregar inversión
      </button>
    </div>
    
    <!-- Investment Modal -->
    <Modal v-if="showModal" :title="editingInvestment ? 'Editar inversión' : 'Nueva inversión'" @close="showModal = false">
      <form @submit.prevent="handleSubmit" class="space-y-4">
        <div>
          <label class="label">Nombre *</label>
          <input v-model="form.name" type="text" placeholder="Ej: Acciones Apple" class="input" required />
        </div>
        
        <div>
          <label class="label">Tipo</label>
          <select v-model="form.investment_type" class="input">
            <option v-for="t in investmentTypes" :key="t.value" :value="t.value">{{ t.label }}</option>
          </select>
        </div>
        
        <div class="grid grid-cols-2 gap-4">
          <div>
            <label class="label">Monto inicial *</label>
            <input v-model="form.initial_amount" type="number" step="1" class="input" required />
          </div>
          <div>
            <label class="label">Valor actual</label>
            <input v-model="form.current_amount" type="number" step="1" class="input" />
          </div>
        </div>
        
        <div class="grid grid-cols-2 gap-4">
          <div>
            <label class="label">Fecha inicio</label>
            <DateInput v-model="form.start_date" />
          </div>
          <div>
            <label class="label">Rentabilidad esperada (%)</label>
            <input v-model="form.expected_return" type="number" step="0.1" class="input" />
          </div>
        </div>
        
        <div>
          <label class="label">Notas</label>
          <textarea v-model="form.notes" rows="2" class="input resize-none" />
        </div>
      </form>
      
      <template #footer>
        <div class="flex justify-end gap-3">
          <button @click="showModal = false" class="btn-secondary">Cancelar</button>
          <button @click="handleSubmit" :disabled="submitting" class="btn-primary">
            {{ submitting ? 'Guardando...' : editingInvestment ? 'Actualizar' : 'Crear' }}
          </button>
        </div>
      </template>
    </Modal>
    
    <!-- Delete Modal -->
    <Modal v-if="showDeleteModal" title="Eliminar inversión" @close="showDeleteModal = false">
      <p class="text-slate-600 dark:text-slate-400">
        ¿Estás seguro de eliminar "{{ investmentToDelete?.name }}"?
      </p>
      <template #footer>
        <div class="flex justify-end gap-3">
          <button @click="showDeleteModal = false" class="btn-secondary">Cancelar</button>
          <button @click="deleteInvestment" class="btn-danger">Eliminar</button>
        </div>
      </template>
    </Modal>
  </div>
</template>

