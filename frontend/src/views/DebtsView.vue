<script setup>
import { ref, onMounted } from 'vue'
import { useUiStore } from '@/stores/ui'
import api from '@/services/api'
import { formatMoney, formatDate } from '@/composables/useCurrency'
import Modal from '@/components/Modal.vue'
import DateInput from '@/components/DateInput.vue'
import { PlusIcon, PencilIcon, TrashIcon, ScaleIcon, BanknotesIcon, EyeIcon, CalendarIcon, DocumentTextIcon } from '@heroicons/vue/24/outline'

const uiStore = useUiStore()

const debts = ref([])
const summary = ref(null)
const loading = ref(true)
const showModal = ref(false)
const showDeleteModal = ref(false)
const showPaymentModal = ref(false)
const showDetailsModal = ref(false)
const editingDebt = ref(null)
const debtToDelete = ref(null)
const debtForPayment = ref(null)
const selectedDebt = ref(null)
const debtPayments = ref([])
const loadingPayments = ref(false)
const submitting = ref(false)

const form = ref({
  name: '',
  debt_type: 'deuda',
  total_amount: '',
  interest_rate: '',
  start_date: new Date().toISOString().split('T')[0],
  due_date: '',
  creditor_debtor: '',
  notes: '',
})

const paymentForm = ref({
  amount: '',
  payment_date: new Date().toISOString().split('T')[0],
  notes: '',
})

async function fetchData() {
  loading.value = true
  try {
    const [debtsRes, sumRes] = await Promise.all([
      api.get('/debts/'),
      api.get('/debts/summary/')
    ])
    debts.value = debtsRes.data.results || debtsRes.data
    summary.value = sumRes.data
  } catch (error) {
    uiStore.showError('Error al cargar deudas')
  } finally {
    loading.value = false
  }
}

function formatCurrency(value) {
  return formatMoney(value)
}

function openNewDebt() {
  editingDebt.value = null
  form.value = {
    name: '',
    debt_type: 'deuda',
    total_amount: '',
    interest_rate: '',
    start_date: new Date().toISOString().split('T')[0],
    due_date: '',
    creditor_debtor: '',
    notes: '',
  }
  showModal.value = true
}

function openEditDebt(debt) {
  editingDebt.value = debt
  form.value = {
    name: debt.name,
    debt_type: debt.debt_type,
    total_amount: debt.total_amount,
    interest_rate: debt.interest_rate || '',
    start_date: debt.start_date,
    due_date: debt.due_date || '',
    creditor_debtor: debt.creditor_debtor || '',
    notes: debt.notes || '',
  }
  showModal.value = true
}

function openPaymentModal(debt) {
  debtForPayment.value = debt
  paymentForm.value = {
    amount: '',
    payment_date: new Date().toISOString().split('T')[0],
    notes: '',
  }
  showPaymentModal.value = true
}

function confirmDeleteDebt(debt) {
  debtToDelete.value = debt
  showDeleteModal.value = true
}

async function openDetailsModal(debt) {
  selectedDebt.value = debt
  debtPayments.value = []
  showDetailsModal.value = true
  loadingPayments.value = true
  
  try {
    const response = await api.get(`/debts/${debt.id}/payments/`)
    debtPayments.value = response.data
  } catch (error) {
    uiStore.showError('Error al cargar historial de pagos')
  } finally {
    loadingPayments.value = false
  }
}

function calculateAccruedInterest(debt) {
  if (!debt.interest_rate || !debt.due_date) return null
  
  const today = new Date()
  const dueDate = new Date(debt.due_date + 'T00:00:00')
  const startDate = new Date(debt.start_date + 'T00:00:00')
  
  const endDate = dueDate > today ? dueDate : today
  const diffTime = endDate - startDate
  const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24))
  
  if (diffDays <= 0) return 0
  
  const interest = (parseFloat(debt.remaining_amount) * parseFloat(debt.interest_rate) * diffDays) / (365 * 100)
  return Math.round(interest)
}

async function handleSubmit() {
  if (!form.value.name || !form.value.total_amount) {
    uiStore.showError('Completa los campos requeridos')
    return
  }
  
  submitting.value = true
  
  try {
    const data = {
      ...form.value,
      total_amount: parseFloat(form.value.total_amount),
      interest_rate: form.value.interest_rate ? parseFloat(form.value.interest_rate) : null,
      due_date: form.value.due_date || null,
    }
    
    if (editingDebt.value) {
      await api.patch(`/debts/${editingDebt.value.id}/`, data)
      uiStore.showSuccess('Deuda actualizada')
    } else {
      await api.post('/debts/', data)
      uiStore.showSuccess('Deuda creada')
    }
    
    showModal.value = false
    fetchData()
  } catch (error) {
    uiStore.showError('Error al guardar')
  } finally {
    submitting.value = false
  }
}

async function submitPayment() {
  if (!paymentForm.value.amount) {
    uiStore.showError('Ingresa el monto del pago')
    return
  }
  
  submitting.value = true
  
  try {
    await api.post(`/debts/${debtForPayment.value.id}/add_payment/`, {
      amount: parseFloat(paymentForm.value.amount),
      payment_date: paymentForm.value.payment_date,
      notes: paymentForm.value.notes,
    })
    uiStore.showSuccess('Pago registrado')
    showPaymentModal.value = false
    fetchData()
  } catch (error) {
    uiStore.showError('Error al registrar pago')
  } finally {
    submitting.value = false
  }
}

async function deleteDebt() {
  if (!debtToDelete.value) return
  
  try {
    await api.delete(`/debts/${debtToDelete.value.id}/`)
    uiStore.showSuccess('Deuda eliminada')
    fetchData()
  } catch (error) {
    uiStore.showError('Error al eliminar')
  } finally {
    showDeleteModal.value = false
    debtToDelete.value = null
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
          Deudas y Préstamos
        </h1>
        <p class="mt-1 text-slate-600 dark:text-slate-400">
          Gestiona lo que debes y lo que te deben
        </p>
      </div>
      <button @click="openNewDebt" class="btn-primary">
        <PlusIcon class="w-5 h-5" />
        Nueva deuda
      </button>
    </div>
    
    <!-- Summary -->
    <div v-if="summary" class="grid grid-cols-1 md:grid-cols-2 gap-6">
      <div class="card p-6 border-l-4 border-red-500">
        <div class="flex items-center gap-3">
          <div class="w-10 h-10 rounded-xl bg-red-100 dark:bg-red-900/30 flex items-center justify-center">
            <ScaleIcon class="w-5 h-5 text-red-600" />
          </div>
          <div>
            <p class="text-sm text-slate-500">Debo (Deudas)</p>
            <p class="text-xl font-bold text-red-600">{{ formatCurrency(summary.debts.remaining) }}</p>
            <p class="text-xs text-slate-400">
              Pagado: {{ formatCurrency(summary.debts.paid) }} de {{ formatCurrency(summary.debts.total) }}
            </p>
          </div>
        </div>
      </div>
      
      <div class="card p-6 border-l-4 border-emerald-500">
        <div class="flex items-center gap-3">
          <div class="w-10 h-10 rounded-xl bg-emerald-100 dark:bg-emerald-900/30 flex items-center justify-center">
            <BanknotesIcon class="w-5 h-5 text-emerald-600" />
          </div>
          <div>
            <p class="text-sm text-slate-500">Me deben (Préstamos)</p>
            <p class="text-xl font-bold text-emerald-600">{{ formatCurrency(summary.loans.remaining) }}</p>
            <p class="text-xs text-slate-400">
              Cobrado: {{ formatCurrency(summary.loans.paid) }} de {{ formatCurrency(summary.loans.total) }}
            </p>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Debts List -->
    <div class="space-y-4">
      <div
        v-for="debt in debts"
        :key="debt.id"
        class="card p-5 hover:shadow-md transition-shadow"
      >
        <div class="flex items-start justify-between">
          <div class="flex items-center gap-3">
            <div 
              class="w-10 h-10 rounded-xl flex items-center justify-center"
              :class="debt.debt_type === 'deuda' ? 'bg-red-100 dark:bg-red-900/30' : 'bg-emerald-100 dark:bg-emerald-900/30'"
            >
              <ScaleIcon 
                class="w-5 h-5"
                :class="debt.debt_type === 'deuda' ? 'text-red-600' : 'text-emerald-600'"
              />
            </div>
            <div>
              <h3 class="font-medium text-slate-900 dark:text-white">{{ debt.name }}</h3>
              <p class="text-sm text-slate-500">
                {{ debt.debt_type_display }}
                <span v-if="debt.creditor_debtor"> · {{ debt.creditor_debtor }}</span>
              </p>
            </div>
          </div>
          
          <div class="flex items-center gap-2">
            <span 
              v-if="debt.is_paid"
              class="px-2 py-1 text-xs rounded-full bg-emerald-100 text-emerald-600"
            >
              Pagada
            </span>
            <button
              v-if="!debt.is_paid"
              @click="openPaymentModal(debt)"
              class="btn-secondary btn-sm"
            >
              <BanknotesIcon class="w-4 h-4" />
              Pagar
            </button>
            <button
              @click="openDetailsModal(debt)"
              class="p-2 rounded-lg hover:bg-primary-100 dark:hover:bg-primary-900/30 text-primary-600"
              title="Ver detalles"
            >
              <EyeIcon class="w-4 h-4" />
            </button>
            <button
              @click="openEditDebt(debt)"
              class="p-2 rounded-lg hover:bg-slate-100 dark:hover:bg-slate-800 text-slate-600"
            >
              <PencilIcon class="w-4 h-4" />
            </button>
            <button
              @click="confirmDeleteDebt(debt)"
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
              {{ formatCurrency(debt.paid_amount) }} de {{ formatCurrency(debt.total_amount) }}
            </span>
            <span class="font-medium text-slate-900 dark:text-white">
              {{ parseFloat(debt.progress_percentage).toFixed(0) }}%
            </span>
          </div>
          <div class="h-2 bg-slate-100 dark:bg-slate-800 rounded-full overflow-hidden">
            <div
              :class="debt.debt_type === 'deuda' ? 'bg-red-500' : 'bg-emerald-500'"
              class="h-full rounded-full transition-all"
              :style="{ width: debt.progress_percentage + '%' }"
            />
          </div>
          <p class="mt-2 text-sm text-slate-500">
            Restante: {{ formatCurrency(debt.remaining_amount) }}
            <span v-if="debt.due_date"> · Vence: {{ formatDate(debt.due_date) }}</span>
          </p>
          <p v-if="debt.interest_rate && calculateAccruedInterest(debt)" class="mt-1 text-sm text-amber-600 dark:text-amber-400">
            Interés proyectado: {{ formatCurrency(calculateAccruedInterest(debt)) }} ({{ debt.interest_rate }}% anual)
          </p>
        </div>
      </div>
    </div>
    
    <!-- Empty State -->
    <div v-if="!loading && debts.length === 0" class="text-center py-12">
      <ScaleIcon class="w-12 h-12 mx-auto text-slate-300 dark:text-slate-600" />
      <h3 class="mt-4 font-medium text-slate-900 dark:text-white">Sin deudas ni préstamos</h3>
      <p class="text-slate-500 mt-1">¡Excelente! No tienes deudas pendientes</p>
    </div>
    
    <!-- Debt Modal -->
    <Modal v-if="showModal" :title="editingDebt ? 'Editar deuda' : 'Nueva deuda'" @close="showModal = false">
      <form @submit.prevent="handleSubmit" class="space-y-4">
        <div>
          <label class="label">Descripción *</label>
          <input v-model="form.name" type="text" placeholder="Ej: Préstamo banco" class="input" required />
        </div>
        
        <div>
          <label class="label">Tipo</label>
          <div class="grid grid-cols-2 gap-2">
            <button
              type="button"
              @click="form.debt_type = 'deuda'"
              :class="[
                'px-4 py-2.5 rounded-xl font-medium transition-all',
                form.debt_type === 'deuda' ? 'bg-red-100 text-red-600' : 'bg-slate-100 text-slate-600'
              ]"
            >
              Debo
            </button>
            <button
              type="button"
              @click="form.debt_type = 'prestamo'"
              :class="[
                'px-4 py-2.5 rounded-xl font-medium transition-all',
                form.debt_type === 'prestamo' ? 'bg-emerald-100 text-emerald-600' : 'bg-slate-100 text-slate-600'
              ]"
            >
              Me deben
            </button>
          </div>
        </div>
        
        <div class="grid grid-cols-2 gap-4">
          <div>
            <label class="label">Monto total *</label>
            <input v-model="form.total_amount" type="number" step="1" class="input" required />
          </div>
          <div>
            <label class="label">Interés (%)</label>
            <input v-model="form.interest_rate" type="number" step="0.1" class="input" />
          </div>
        </div>
        
        <div class="grid grid-cols-2 gap-4">
          <div>
            <label class="label">Fecha inicio</label>
            <DateInput v-model="form.start_date" />
          </div>
          <div>
            <label class="label">Fecha vencimiento</label>
            <DateInput v-model="form.due_date" />
          </div>
        </div>
        
        <div>
          <label class="label">{{ form.debt_type === 'deuda' ? 'Acreedor' : 'Deudor' }}</label>
          <input v-model="form.creditor_debtor" type="text" class="input" />
        </div>
      </form>
      
      <template #footer>
        <div class="flex justify-end gap-3">
          <button @click="showModal = false" class="btn-secondary">Cancelar</button>
          <button @click="handleSubmit" :disabled="submitting" class="btn-primary">
            {{ submitting ? 'Guardando...' : editingDebt ? 'Actualizar' : 'Crear' }}
          </button>
        </div>
      </template>
    </Modal>
    
    <!-- Payment Modal -->
    <Modal v-if="showPaymentModal" title="Registrar pago" @close="showPaymentModal = false">
      <form @submit.prevent="submitPayment" class="space-y-4">
        <p class="text-slate-600 dark:text-slate-400">
          Registrar pago para: <strong>{{ debtForPayment?.name }}</strong>
        </p>
        <p class="text-sm text-slate-500">
          Pendiente: {{ formatCurrency(debtForPayment?.remaining_amount) }}
        </p>
        
        <div>
          <label class="label">Monto del pago *</label>
          <input v-model="paymentForm.amount" type="number" step="1" class="input" required />
        </div>
        
        <div>
          <label class="label">Fecha del pago</label>
          <DateInput v-model="paymentForm.payment_date" />
        </div>
        
        <div>
          <label class="label">Notas</label>
          <input v-model="paymentForm.notes" type="text" class="input" />
        </div>
      </form>
      
      <template #footer>
        <div class="flex justify-end gap-3">
          <button @click="showPaymentModal = false" class="btn-secondary">Cancelar</button>
          <button @click="submitPayment" :disabled="submitting" class="btn-primary">
            {{ submitting ? 'Guardando...' : 'Registrar pago' }}
          </button>
        </div>
      </template>
    </Modal>
    
    <!-- Delete Modal -->
    <Modal v-if="showDeleteModal" title="Eliminar deuda" @close="showDeleteModal = false">
      <p class="text-slate-600 dark:text-slate-400">
        ¿Estás seguro de eliminar "{{ debtToDelete?.name }}"?
      </p>
      <template #footer>
        <div class="flex justify-end gap-3">
          <button @click="showDeleteModal = false" class="btn-secondary">Cancelar</button>
          <button @click="deleteDebt" class="btn-danger">Eliminar</button>
        </div>
      </template>
    </Modal>
    
    <!-- Details Modal -->
    <Modal v-if="showDetailsModal" :title="selectedDebt?.name" size="lg" @close="showDetailsModal = false">
      <div v-if="selectedDebt" class="space-y-6">
        <!-- Info General -->
        <div class="grid grid-cols-2 gap-4">
          <div class="bg-slate-50 dark:bg-slate-800 rounded-xl p-4">
            <p class="text-sm text-slate-500 dark:text-slate-400">Tipo</p>
            <p class="font-medium text-slate-900 dark:text-white">{{ selectedDebt.debt_type_display }}</p>
          </div>
          <div class="bg-slate-50 dark:bg-slate-800 rounded-xl p-4">
            <p class="text-sm text-slate-500 dark:text-slate-400">{{ selectedDebt.debt_type === 'deuda' ? 'Acreedor' : 'Deudor' }}</p>
            <p class="font-medium text-slate-900 dark:text-white">{{ selectedDebt.creditor_debtor || 'No especificado' }}</p>
          </div>
          <div class="bg-slate-50 dark:bg-slate-800 rounded-xl p-4">
            <p class="text-sm text-slate-500 dark:text-slate-400">Monto Total</p>
            <p class="font-medium text-slate-900 dark:text-white">{{ formatCurrency(selectedDebt.total_amount) }}</p>
          </div>
          <div class="bg-slate-50 dark:bg-slate-800 rounded-xl p-4">
            <p class="text-sm text-slate-500 dark:text-slate-400">Restante</p>
            <p class="font-medium" :class="selectedDebt.debt_type === 'deuda' ? 'text-red-600' : 'text-emerald-600'">
              {{ formatCurrency(selectedDebt.remaining_amount) }}
            </p>
          </div>
          <div v-if="selectedDebt.start_date" class="bg-slate-50 dark:bg-slate-800 rounded-xl p-4">
            <p class="text-sm text-slate-500 dark:text-slate-400">Fecha inicio</p>
            <p class="font-medium text-slate-900 dark:text-white">{{ formatDate(selectedDebt.start_date) }}</p>
          </div>
          <div v-if="selectedDebt.due_date" class="bg-slate-50 dark:bg-slate-800 rounded-xl p-4">
            <p class="text-sm text-slate-500 dark:text-slate-400">Fecha vencimiento</p>
            <p class="font-medium text-slate-900 dark:text-white">{{ formatDate(selectedDebt.due_date) }}</p>
          </div>
        </div>
        
        <!-- Interés acumulado -->
        <div v-if="selectedDebt.interest_rate && calculateAccruedInterest(selectedDebt)" class="bg-amber-50 dark:bg-amber-900/20 rounded-xl p-4 border border-amber-200 dark:border-amber-800">
          <div class="flex items-center gap-3">
            <div class="w-10 h-10 rounded-xl bg-amber-100 dark:bg-amber-900/30 flex items-center justify-center">
              <CalendarIcon class="w-5 h-5 text-amber-600" />
            </div>
            <div>
              <p class="text-sm text-amber-700 dark:text-amber-400">Interés proyectado ({{ selectedDebt.interest_rate }}% anual)</p>
              <p class="text-xl font-bold text-amber-700 dark:text-amber-300">
                {{ formatCurrency(calculateAccruedInterest(selectedDebt)) }}
              </p>
              <p class="text-xs text-amber-600 dark:text-amber-500">
                Calculado hasta {{ selectedDebt.due_date ? formatDate(selectedDebt.due_date) : 'hoy' }}
              </p>
            </div>
          </div>
        </div>
        
        <!-- Notas -->
        <div v-if="selectedDebt.notes" class="bg-slate-50 dark:bg-slate-800 rounded-xl p-4">
          <div class="flex items-center gap-2 mb-2">
            <DocumentTextIcon class="w-4 h-4 text-slate-400" />
            <p class="text-sm font-medium text-slate-500 dark:text-slate-400">Notas</p>
          </div>
          <p class="text-slate-700 dark:text-slate-300">{{ selectedDebt.notes }}</p>
        </div>
        
        <!-- Progress -->
        <div>
          <div class="flex justify-between text-sm mb-2">
            <span class="text-slate-600 dark:text-slate-400">Progreso de pago</span>
            <span class="font-medium text-slate-900 dark:text-white">
              {{ parseFloat(selectedDebt.progress_percentage).toFixed(0) }}%
            </span>
          </div>
          <div class="h-3 bg-slate-100 dark:bg-slate-800 rounded-full overflow-hidden">
            <div
              :class="selectedDebt.debt_type === 'deuda' ? 'bg-red-500' : 'bg-emerald-500'"
              class="h-full rounded-full transition-all"
              :style="{ width: selectedDebt.progress_percentage + '%' }"
            />
          </div>
          <p class="mt-2 text-sm text-slate-500">
            {{ formatCurrency(selectedDebt.paid_amount) }} de {{ formatCurrency(selectedDebt.total_amount) }} pagado
          </p>
        </div>
        
        <!-- Historial de pagos -->
        <div>
          <h4 class="font-medium text-slate-900 dark:text-white mb-3 flex items-center gap-2">
            <BanknotesIcon class="w-5 h-5 text-slate-400" />
            Historial de pagos
          </h4>
          
          <div v-if="loadingPayments" class="text-center py-6">
            <div class="animate-spin w-6 h-6 border-2 border-primary-500 border-t-transparent rounded-full mx-auto"></div>
            <p class="text-sm text-slate-500 mt-2">Cargando pagos...</p>
          </div>
          
          <div v-else-if="debtPayments.length === 0" class="text-center py-6 bg-slate-50 dark:bg-slate-800 rounded-xl">
            <BanknotesIcon class="w-8 h-8 text-slate-300 dark:text-slate-600 mx-auto" />
            <p class="text-sm text-slate-500 mt-2">No hay pagos registrados</p>
          </div>
          
          <div v-else class="space-y-3">
            <div 
              v-for="payment in debtPayments" 
              :key="payment.id"
              class="flex items-center justify-between p-3 bg-slate-50 dark:bg-slate-800 rounded-xl"
            >
              <div class="flex items-center gap-3">
                <div class="w-8 h-8 rounded-lg bg-emerald-100 dark:bg-emerald-900/30 flex items-center justify-center">
                  <BanknotesIcon class="w-4 h-4 text-emerald-600" />
                </div>
                <div>
                  <p class="font-medium text-slate-900 dark:text-white">
                    {{ formatCurrency(payment.amount) }}
                  </p>
                  <p class="text-xs text-slate-500">{{ formatDate(payment.payment_date) }}</p>
                </div>
              </div>
              <div v-if="payment.notes" class="text-right max-w-[200px]">
                <p class="text-sm text-slate-500 dark:text-slate-400 truncate" :title="payment.notes">
                  {{ payment.notes }}
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <template #footer>
        <div class="flex justify-end">
          <button @click="showDetailsModal = false" class="btn-secondary">Cerrar</button>
        </div>
      </template>
    </Modal>
  </div>
</template>

