<script setup>
import { ref, onMounted, computed } from 'vue'
import { useAccountsStore } from '@/stores/accounts'
import { useUiStore } from '@/stores/ui'
import { formatMoney } from '@/composables/useCurrency'
import Modal from '@/components/Modal.vue'
import AccountCard from '@/components/AccountCard.vue'
import { PlusIcon } from '@heroicons/vue/24/outline'

const accountsStore = useAccountsStore()
const uiStore = useUiStore()

const showModal = ref(false)
const showDeleteModal = ref(false)
const editingAccount = ref(null)
const accountToDelete = ref(null)
const loading = ref(false)

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
  </div>
</template>

