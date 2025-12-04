<script setup>
import { ref, onMounted, computed } from 'vue'
import { useAccountsStore } from '@/stores/accounts'
import { useUiStore } from '@/stores/ui'
import { formatMoney } from '@/composables/useCurrency'
import Modal from '@/components/Modal.vue'
import AccountCard from '@/components/AccountCard.vue'
import TransactionList from '@/components/TransactionList.vue'
import { PlusIcon } from '@heroicons/vue/24/outline'
import api from '@/services/api'

const accountsStore = useAccountsStore()
const uiStore = useUiStore()

const showModal = ref(false)
const showDeleteModal = ref(false)
const showDetailModal = ref(false)
const showAdjustModal = ref(false)
const selectedAccount = ref(null)
const editingAccount = ref(null)
const accountToDelete = ref(null)
const accountToAdjust = ref(null)
const loading = ref(false)
const accountDetails = ref(null)
const loadingDetails = ref(false)
const adjustingBalance = ref(false)
const adjustmentForm = ref({
  newBalance: '',
  description: ''
})

const form = ref({
  name: '',
  account_type: 'banco',
  currency: 'CLP',
  color: '#3B82F6',
  icon: 'credit-card',
  include_in_total: true,
})

const initialBalance = ref('')

const accountTypes = [
  { value: 'efectivo', label: 'Efectivo' },
  { value: 'banco', label: 'Cuenta Bancaria' },
  { value: 'credito', label: 'Tarjeta de Crédito' },
  { value: 'debito', label: 'Tarjeta de Débito' },
  { value: 'billetera', label: 'Billetera Digital' },
  { value: 'inversion', label: 'Cuenta de Inversión' },
  { value: 'otro', label: 'Otro' },
]

const currencies = [
  { value: 'CLP', label: 'Peso Chileno ($)' },
  { value: 'USD', label: 'Dólar (US$)' },
]

const colors = [
  '#3B82F6', '#22C55E', '#EF4444', '#F59E0B', '#8B5CF6', 
  '#EC4899', '#14B8A6', '#6366F1', '#64748B', '#0EA5E9'
]

const isEditing = computed(() => !!editingAccount.value)

function openNewAccount() {
  editingAccount.value = null
  form.value = {
    name: '',
    account_type: 'banco',
    currency: 'CLP',
    color: '#3B82F6',
    icon: 'credit-card',
    include_in_total: true,
  }
  initialBalance.value = ''
  showModal.value = true
}

function openEditAccount(account) {
  editingAccount.value = account
  form.value = {
    name: account.name,
    account_type: account.account_type,
    currency: account.currency,
    color: account.color,
    icon: account.icon,
    include_in_total: account.include_in_total,
  }
  showModal.value = true
}

function confirmDeleteAccount(account) {
  accountToDelete.value = account
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
      await accountsStore.updateAccount(editingAccount.value.id, form.value)
      uiStore.showSuccess('Cuenta actualizada')
    } else {
      const newAccount = await accountsStore.createAccount(form.value)
      
      if (initialBalance.value) {
        await accountsStore.setInitialBalance(newAccount.id, parseFloat(initialBalance.value))
      }
      
      uiStore.showSuccess('Cuenta creada')
    }
    showModal.value = false
  } catch (error) {
    uiStore.showError('Error al guardar la cuenta')
  } finally {
    loading.value = false
  }
}

async function deleteAccount() {
  if (!accountToDelete.value) return
  
  try {
    await accountsStore.deleteAccount(accountToDelete.value.id)
    uiStore.showSuccess('Cuenta eliminada')
  } catch (error) {
    uiStore.showError('Error al eliminar la cuenta')
  } finally {
    showDeleteModal.value = false
    accountToDelete.value = null
  }
}

function formatCurrency(value) {
  return formatMoney(value)
}

function openAdjustBalance(account) {
  accountToAdjust.value = account
  adjustmentForm.value = {
    newBalance: account.balance.toString(),
    description: ''
  }
  showAdjustModal.value = true
}

async function handleAdjustBalance() {
  if (!accountToAdjust.value) return
  
  const newBalance = parseFloat(adjustmentForm.value.newBalance)
  if (isNaN(newBalance)) {
    uiStore.showError('El balance debe ser un número válido')
    return
  }
  
  adjustingBalance.value = true
  
  try {
    await accountsStore.adjustBalance(
      accountToAdjust.value.id,
      newBalance,
      adjustmentForm.value.description
    )
    uiStore.showSuccess('Balance ajustado correctamente')
    showAdjustModal.value = false
    accountToAdjust.value = null
    adjustmentForm.value = { newBalance: '', description: '' }
  } catch (error) {
    uiStore.showError('Error al ajustar el balance')
  } finally {
    adjustingBalance.value = false
  }
}

async function openAccountDetail(account) {
  selectedAccount.value = account
  loadingDetails.value = true
  showDetailModal.value = true
  
  try {
    const response = await api.get(`/accounts/${account.id}/details/`)
    accountDetails.value = response.data
  } catch (error) {
    uiStore.showError('Error al cargar detalles de la cuenta')
    accountDetails.value = null
  } finally {
    loadingDetails.value = false
  }
}

onMounted(() => {
  accountsStore.fetchAccounts()
})
</script>

<template>
  <div class="space-y-6 animate-fade-in">
    <!-- Header -->
    <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
      <div>
        <h1 class="font-display text-2xl lg:text-3xl font-bold text-slate-900 dark:text-white">
          Cuentas
        </h1>
        <p class="mt-1 text-slate-600 dark:text-slate-400">
          Administra tus cuentas financieras
        </p>
      </div>
      <button @click="openNewAccount" class="btn-primary">
        <PlusIcon class="w-5 h-5" />
        Nueva cuenta
      </button>
    </div>
    
    <!-- Total Balance -->
    <div class="card p-6 bg-gradient-to-br from-primary-600 to-primary-700 text-white">
      <p class="text-primary-100">Saldo total</p>
      <p class="text-3xl font-bold mt-1">{{ formatCurrency(accountsStore.totalBalance) }}</p>
      <p class="text-sm text-primary-200 mt-2">
        {{ accountsStore.activeAccounts.length }} cuentas activas
      </p>
    </div>
    
    <!-- Accounts Grid -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      <AccountCard
        v-for="account in accountsStore.accounts"
        :key="account.id"
        :account="account"
        @edit="openEditAccount"
        @delete="confirmDeleteAccount"
        @detail="openAccountDetail"
        @adjust="openAdjustBalance"
      />
    </div>
    
    <!-- Empty State -->
    <div v-if="accountsStore.accounts.length === 0 && !accountsStore.loading" class="text-center py-12">
      <div class="w-16 h-16 mx-auto mb-4 rounded-full bg-slate-100 dark:bg-slate-800 flex items-center justify-center">
        <PlusIcon class="w-8 h-8 text-slate-400" />
      </div>
      <h3 class="font-medium text-slate-900 dark:text-white">No tienes cuentas</h3>
      <p class="text-slate-500 dark:text-slate-400 mt-1">Crea tu primera cuenta para empezar</p>
      <button @click="openNewAccount" class="btn-primary mt-4">
        Crear cuenta
      </button>
    </div>
    
    <!-- Account Modal -->
    <Modal 
      v-if="showModal" 
      :title="isEditing ? 'Editar cuenta' : 'Nueva cuenta'" 
      @close="showModal = false"
    >
      <form @submit.prevent="handleSubmit" class="space-y-5">
        <div>
          <label class="label">Nombre de la cuenta *</label>
          <input
            v-model="form.name"
            type="text"
            placeholder="Ej: Mi banco principal"
            class="input"
            required
          />
        </div>
        
        <div class="grid grid-cols-2 gap-4">
          <div>
            <label class="label">Tipo</label>
            <select v-model="form.account_type" class="input">
              <option v-for="type in accountTypes" :key="type.value" :value="type.value">
                {{ type.label }}
              </option>
            </select>
          </div>
          
          <div>
            <label class="label">Moneda</label>
            <select v-model="form.currency" class="input">
              <option v-for="curr in currencies" :key="curr.value" :value="curr.value">
                {{ curr.label }}
              </option>
            </select>
          </div>
        </div>
        
        <div v-if="!isEditing">
          <label class="label">Saldo inicial</label>
          <div class="relative">
            <span class="absolute left-4 top-1/2 -translate-y-1/2 text-slate-400">$</span>
            <input
              v-model="initialBalance"
              type="number"
              step="1"
              placeholder="0"
              class="input pl-10"
            />
          </div>
        </div>
        
        <div>
          <label class="label">Color</label>
          <div class="flex gap-2">
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
        
        <div class="flex items-center gap-3">
          <input
            v-model="form.include_in_total"
            type="checkbox"
            id="include_in_total"
            class="w-4 h-4 rounded border-slate-300 text-primary-600 focus:ring-primary-500"
          />
          <label for="include_in_total" class="text-sm text-slate-700 dark:text-slate-300">
            Incluir en el saldo total
          </label>
        </div>
      </form>
      
      <template #footer>
        <div class="flex justify-end gap-3">
          <button @click="showModal = false" class="btn-secondary">Cancelar</button>
          <button @click="handleSubmit" :disabled="loading" class="btn-primary">
            {{ loading ? 'Guardando...' : isEditing ? 'Actualizar' : 'Crear cuenta' }}
          </button>
        </div>
      </template>
    </Modal>
    
    <!-- Delete Modal -->
    <Modal v-if="showDeleteModal" title="Eliminar cuenta" @close="showDeleteModal = false">
      <p class="text-slate-600 dark:text-slate-400">
        ¿Estás seguro de eliminar la cuenta "{{ accountToDelete?.name }}"? 
        Esto también eliminará todas las transacciones asociadas.
      </p>
      <template #footer>
        <div class="flex justify-end gap-3">
          <button @click="showDeleteModal = false" class="btn-secondary">Cancelar</button>
          <button @click="deleteAccount" class="btn-danger">Eliminar</button>
        </div>
      </template>
    </Modal>
    
    <!-- Adjust Balance Modal -->
    <Modal v-if="showAdjustModal && accountToAdjust" title="Ajustar Balance" @close="showAdjustModal = false">
      <div class="space-y-5">
        <div class="p-4 bg-slate-50 dark:bg-slate-800 rounded-xl">
          <p class="text-sm text-slate-500 dark:text-slate-400">Balance actual</p>
          <p class="text-2xl font-bold text-slate-900 dark:text-white mt-1">
            {{ formatCurrency(accountToAdjust.balance) }}
          </p>
        </div>
        
        <div>
          <label class="label">Nuevo balance *</label>
          <div class="relative">
            <span class="absolute left-4 top-1/2 -translate-y-1/2 text-slate-400">$</span>
            <input
              v-model="adjustmentForm.newBalance"
              type="number"
              step="0.01"
              placeholder="0"
              class="input pl-10"
              required
            />
          </div>
          <p class="text-xs text-slate-500 dark:text-slate-400 mt-1">
            Este ajuste no afectará las estadísticas de ingresos y gastos
          </p>
        </div>
        
        <div>
          <label class="label">Descripción (opcional)</label>
          <input
            v-model="adjustmentForm.description"
            type="text"
            placeholder="Ej: Corrección por error en transacción eliminada"
            class="input"
          />
        </div>
      </div>
      
      <template #footer>
        <div class="flex justify-end gap-3">
          <button @click="showAdjustModal = false" class="btn-secondary">Cancelar</button>
          <button @click="handleAdjustBalance" :disabled="adjustingBalance" class="btn-primary">
            {{ adjustingBalance ? 'Ajustando...' : 'Ajustar balance' }}
          </button>
        </div>
      </template>
    </Modal>
    
    <!-- Account Detail Modal -->
    <Modal v-if="showDetailModal && selectedAccount" :title="`Detalles: ${selectedAccount.name}`" @close="showDetailModal = false" size="lg">
      <div v-if="loadingDetails" class="text-center py-8">
        <div class="animate-spin w-6 h-6 border-2 border-primary-500 border-t-transparent rounded-full mx-auto"></div>
        <p class="text-sm text-slate-500 mt-2">Cargando detalles...</p>
      </div>
      <div v-else-if="accountDetails">
        <div class="mb-6 p-4 bg-slate-50 dark:bg-slate-800 rounded-xl">
          <div class="grid grid-cols-2 gap-4">
            <div>
              <p class="text-sm text-slate-500 dark:text-slate-400">Ingresos del mes</p>
              <p class="text-lg font-semibold text-emerald-600">{{ formatCurrency(accountDetails.summary.income) }}</p>
            </div>
            <div>
              <p class="text-sm text-slate-500 dark:text-slate-400">Gastos del mes</p>
              <p class="text-lg font-semibold text-red-600">{{ formatCurrency(accountDetails.summary.expenses) }}</p>
            </div>
            <div>
              <p class="text-sm text-slate-500 dark:text-slate-400">Transferencias salientes</p>
              <p class="text-lg font-semibold text-blue-600">{{ formatCurrency(accountDetails.summary.transfers_out) }}</p>
            </div>
            <div>
              <p class="text-sm text-slate-500 dark:text-slate-400">Transferencias entrantes</p>
              <p class="text-lg font-semibold text-emerald-600">{{ formatCurrency(accountDetails.summary.transfers_in) }}</p>
            </div>
          </div>
        </div>
        
        <div>
          <h3 class="font-semibold text-slate-900 dark:text-white mb-3">Últimas transacciones</h3>
          <TransactionList 
            v-if="accountDetails.transactions.length > 0"
            :transactions="accountDetails.transactions" 
            compact 
          />
          <div v-else class="text-center py-8 text-slate-500 dark:text-slate-400">
            No hay transacciones
          </div>
        </div>
      </div>
    </Modal>
  </div>
</template>

