<script setup>
import { ref, onMounted, watch, computed } from 'vue'
import { useTransactionsStore } from '@/stores/transactions'
import { useAccountsStore } from '@/stores/accounts'
import { useCategoriesStore } from '@/stores/categories'
import { useUiStore } from '@/stores/ui'
import TransactionList from '@/components/TransactionList.vue'
import TransactionModal from '@/components/TransactionModal.vue'
import TransactionDetailModal from '@/components/TransactionDetailModal.vue'
import Modal from '@/components/Modal.vue'
import DateInput from '@/components/DateInput.vue'
import { MagnifyingGlassIcon, FunnelIcon, PlusIcon, BugAntIcon } from '@heroicons/vue/24/outline'

const transactionsStore = useTransactionsStore()
const accountsStore = useAccountsStore()
const categoriesStore = useCategoriesStore()
const uiStore = useUiStore()

const loading = ref(false)
const showFilters = ref(false)
const showModal = ref(false)
const showDeleteModal = ref(false)
const showDetailModal = ref(false)
const selectedTransaction = ref(null)
const selectedTransactionForDetail = ref(null)
const transactionToDelete = ref(null)

const filters = ref({
  search: '',
  transaction_type: '',
  account: '',
  category: '',
  date_from: '',
  date_to: '',
  is_ant_expense: '',
})

const transactions = computed(() => transactionsStore.transactions)

async function fetchData() {
  loading.value = true
  try {
    const params = {}
    if (filters.value.transaction_type) params.transaction_type = filters.value.transaction_type
    if (filters.value.account) params.account = filters.value.account
    if (filters.value.category) params.category = filters.value.category
    if (filters.value.date_from) params.date_from = filters.value.date_from
    if (filters.value.date_to) params.date_to = filters.value.date_to
    if (filters.value.search) params.search = filters.value.search
    if (filters.value.is_ant_expense) params.is_ant_expense = filters.value.is_ant_expense
    
    await transactionsStore.fetchTransactions(params)
  } finally {
    loading.value = false
  }
}

function handleEdit(transaction) {
  selectedTransaction.value = transaction
  showModal.value = true
}

function handleDelete(transaction) {
  transactionToDelete.value = transaction
  showDeleteModal.value = true
}

async function handleSelect(transaction) {
  try {
    loading.value = true
    const response = await transactionsStore.fetchTransactionDetails(transaction.id)
    selectedTransactionForDetail.value = response
    showDetailModal.value = true
  } catch (error) {
    uiStore.showError('Error al cargar los detalles de la transacción')
  } finally {
    loading.value = false
  }
}

function handleDetailEdit(transaction) {
  selectedTransaction.value = transaction
  showDetailModal.value = false
  showModal.value = true
}

function handleDetailDelete(transaction) {
  handleDelete(transaction)
  showDetailModal.value = false
}

async function confirmDelete() {
  if (!transactionToDelete.value) return
  
  try {
    await transactionsStore.deleteTransaction(transactionToDelete.value.id)
    await accountsStore.fetchAccounts()
    uiStore.showSuccess('Transacción eliminada')
  } catch (error) {
    uiStore.showError('Error al eliminar')
  } finally {
    showDeleteModal.value = false
    transactionToDelete.value = null
  }
}

function openNewTransaction() {
  selectedTransaction.value = null
  showModal.value = true
}

function clearFilters() {
  filters.value = {
    search: '',
    transaction_type: '',
    account: '',
    category: '',
    date_from: '',
    date_to: '',
    is_ant_expense: '',
  }
}

watch(filters, () => {
  fetchData()
}, { deep: true })

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
          Transacciones
        </h1>
        <p class="mt-1 text-slate-600 dark:text-slate-400">
          Gestiona tus ingresos, gastos y transferencias
        </p>
      </div>
      <button @click="openNewTransaction" class="btn-primary">
        <PlusIcon class="w-5 h-5" />
        Nueva transacción
      </button>
    </div>
    
    <!-- Search and Filters -->
    <div class="card p-4">
      <div class="flex flex-col lg:flex-row gap-4">
        <!-- Search -->
        <div class="relative flex-1">
          <MagnifyingGlassIcon class="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400" />
          <input
            v-model="filters.search"
            type="text"
            placeholder="Buscar transacciones..."
            class="input pl-12"
          />
        </div>
        
        <!-- Filter Toggle -->
        <button
          @click="showFilters = !showFilters"
          :class="[
            'btn-secondary',
            showFilters && 'bg-primary-100 dark:bg-primary-900/30 text-primary-600'
          ]"
        >
          <FunnelIcon class="w-5 h-5" />
          Filtros
        </button>
      </div>
      
      <!-- Filter Options -->
      <div v-if="showFilters" class="mt-4 pt-4 border-t border-slate-200 dark:border-slate-700">
        <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4">
          <div>
            <label class="label">Tipo</label>
            <select v-model="filters.transaction_type" class="input">
              <option value="">Todos</option>
              <option value="ingreso">Ingresos</option>
              <option value="gasto">Gastos</option>
              <option value="transferencia">Transferencias</option>
            </select>
          </div>
          
          <div>
            <label class="label">Cuenta</label>
            <select v-model="filters.account" class="input">
              <option value="">Todas</option>
              <option v-for="account in accountsStore.accounts" :key="account.id" :value="account.id">
                {{ account.name }}
              </option>
            </select>
          </div>
          
          <div>
            <label class="label">Desde</label>
            <DateInput v-model="filters.date_from" />
          </div>
          
          <div>
            <label class="label">Hasta</label>
            <DateInput v-model="filters.date_to" />
          </div>
          
          <div>
            <label class="label">Gasto hormiga</label>
            <select v-model="filters.is_ant_expense" class="input">
              <option value="">Todos</option>
              <option value="true">Solo hormiga</option>
              <option value="false">Sin hormiga</option>
            </select>
          </div>
        </div>
        
        <div class="mt-4 flex items-center gap-4">
          <button @click="clearFilters" class="text-sm text-primary-600 dark:text-primary-400 hover:underline">
            Limpiar filtros
          </button>
          <button 
            @click="filters.is_ant_expense = 'true'" 
            class="flex items-center gap-1.5 text-sm text-orange-600 hover:text-orange-700"
          >
            <BugAntIcon class="w-4 h-4" />
            Ver gastos hormiga
          </button>
        </div>
      </div>
    </div>
    
    <!-- Transactions List -->
    <div class="card p-6">
      <div v-if="loading" class="space-y-4">
        <div v-for="i in 5" :key="i" class="flex items-center gap-4 animate-pulse">
          <div class="w-10 h-10 bg-slate-200 dark:bg-slate-700 rounded-xl"></div>
          <div class="flex-1">
            <div class="h-4 bg-slate-200 dark:bg-slate-700 rounded w-1/3 mb-2"></div>
            <div class="h-3 bg-slate-200 dark:bg-slate-700 rounded w-1/4"></div>
          </div>
          <div class="h-5 bg-slate-200 dark:bg-slate-700 rounded w-20"></div>
        </div>
      </div>
      
      <TransactionList 
        v-else
        :transactions="transactions"
        @edit="handleEdit"
        @delete="handleDelete"
        @select="handleSelect"
      />
      
      <!-- Pagination -->
      <div v-if="transactionsStore.pagination.count > 20" class="mt-6 flex justify-center gap-2">
        <button
          :disabled="!transactionsStore.pagination.previous"
          @click="fetchData({ page: transactionsStore.pagination.page - 1 })"
          class="btn-secondary btn-sm"
        >
          Anterior
        </button>
        <span class="px-4 py-2 text-sm text-slate-600 dark:text-slate-400">
          Página {{ transactionsStore.pagination.page }}
        </span>
        <button
          :disabled="!transactionsStore.pagination.next"
          @click="fetchData({ page: transactionsStore.pagination.page + 1 })"
          class="btn-secondary btn-sm"
        >
          Siguiente
        </button>
      </div>
    </div>
    
    <!-- Transaction Modal -->
    <TransactionModal
      v-if="showModal"
      :transaction="selectedTransaction"
      @close="showModal = false; selectedTransaction = null"
      @saved="fetchData"
    />
    
    <!-- Transaction Detail Modal -->
    <TransactionDetailModal
      v-if="showDetailModal && selectedTransactionForDetail"
      :transaction="selectedTransactionForDetail"
      @close="showDetailModal = false; selectedTransactionForDetail = null"
      @edit="handleDetailEdit"
      @delete="handleDetailDelete"
    />
    
    <!-- Delete Confirmation -->
    <Modal v-if="showDeleteModal" title="Eliminar transacción" @close="showDeleteModal = false">
      <p class="text-slate-600 dark:text-slate-400">
        ¿Estás seguro de que deseas eliminar esta transacción? Esta acción actualizará el saldo de la cuenta.
      </p>
      <template #footer>
        <div class="flex justify-end gap-3">
          <button @click="showDeleteModal = false" class="btn-secondary">Cancelar</button>
          <button @click="confirmDelete" class="btn-danger">Eliminar</button>
        </div>
      </template>
    </Modal>
  </div>
</template>

