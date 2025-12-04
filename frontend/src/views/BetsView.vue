<script setup>
import { ref, onMounted, computed } from 'vue'
import { useBetsStore } from '@/stores/bets'
import { useAccountsStore } from '@/stores/accounts'
import { useUiStore } from '@/stores/ui'
import BetModal from '@/components/BetModal.vue'
import BetStatistics from '@/components/BetStatistics.vue'
import BetList from '@/components/BetList.vue'
import BetWarningBanner from '@/components/BetWarningBanner.vue'
import Modal from '@/components/Modal.vue'
import { PlusIcon, FunnelIcon } from '@heroicons/vue/24/outline'

const betsStore = useBetsStore()
const accountsStore = useAccountsStore()
const uiStore = useUiStore()

const loading = ref(false)
const showModal = ref(false)
const showDeleteModal = ref(false)
const showFilters = ref(false)
const selectedBet = ref(null)
const betToDelete = ref(null)

const filters = ref({
  bet_type: '',
  result: '',
  account: '',
})

const bets = computed(() => betsStore.bets)
const statistics = computed(() => betsStore.statistics)

async function fetchData() {
  loading.value = true
  try {
    const params = {}
    if (filters.value.bet_type) params.bet_type = filters.value.bet_type
    if (filters.value.result) params.result = filters.value.result
    if (filters.value.account) params.account = filters.value.account
    
    await Promise.all([
      betsStore.fetchBets(params),
      betsStore.fetchStatistics()
    ])
  } catch (error) {
    uiStore.showError('Error al cargar apuestas')
  } finally {
    loading.value = false
  }
}

function openNewBet() {
  selectedBet.value = null
  showModal.value = true
}

function handleEdit(bet) {
  selectedBet.value = bet
  showModal.value = true
}

function handleDelete(bet) {
  betToDelete.value = bet
  showDeleteModal.value = true
}

async function confirmDelete() {
  if (!betToDelete.value) return
  
  try {
    await betsStore.deleteBet(betToDelete.value.id)
    await accountsStore.fetchAccounts()
    uiStore.showSuccess('Apuesta eliminada')
  } catch (error) {
    uiStore.showError('Error al eliminar')
  } finally {
    showDeleteModal.value = false
    betToDelete.value = null
  }
}

function clearFilters() {
  filters.value = {
    bet_type: '',
    result: '',
    account: '',
  }
}

onMounted(async () => {
  await Promise.all([
    fetchData(),
    accountsStore.fetchAccounts()
  ])
})
</script>

<template>
  <div class="space-y-6 animate-fade-in">
    <BetWarningBanner />
    
    <!-- Header -->
    <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
      <div>
        <h1 class="font-display text-2xl lg:text-3xl font-bold text-slate-900 dark:text-white">
          Apuestas
        </h1>
        <p class="mt-1 text-slate-600 dark:text-slate-400">
          Registra y gestiona tus apuestas
        </p>
      </div>
      <button @click="openNewBet" class="btn-primary">
        <PlusIcon class="w-5 h-5" />
        Nueva apuesta
      </button>
    </div>
    
    <!-- Filters -->
    <div class="card p-4">
      <div class="flex items-center justify-between mb-4">
        <h3 class="font-medium text-slate-900 dark:text-white">Filtros</h3>
        <button
          @click="showFilters = !showFilters"
          :class="[
            'btn-secondary btn-sm',
            showFilters && 'bg-primary-100 dark:bg-primary-900/30 text-primary-600'
          ]"
        >
          <FunnelIcon class="w-4 h-4" />
        </button>
      </div>
      
      <div v-if="showFilters" class="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <div>
          <label class="label">Tipo de apuesta</label>
          <select v-model="filters.bet_type" class="input" @change="fetchData">
            <option value="">Todos</option>
            <option value="deportes">Deportes</option>
            <option value="blackjack">Blackjack</option>
            <option value="poker">Poker</option>
            <option value="ruleta">Ruleta</option>
            <option value="tragamonedas">Tragamonedas</option>
            <option value="otros">Otros</option>
          </select>
        </div>
        
        <div>
          <label class="label">Resultado</label>
          <select v-model="filters.result" class="input" @change="fetchData">
            <option value="">Todos</option>
            <option value="ganó">Ganó</option>
            <option value="perdió">Perdió</option>
            <option value="pendiente">Pendiente</option>
          </select>
        </div>
        
        <div>
          <label class="label">Cuenta</label>
          <select v-model="filters.account" class="input" @change="fetchData">
            <option value="">Todas</option>
            <option v-for="account in accountsStore.accounts" :key="account.id" :value="account.id">
              {{ account.name }}
            </option>
          </select>
        </div>
      </div>
      
      <div v-if="showFilters" class="mt-4">
        <button @click="clearFilters; fetchData()" class="text-sm text-primary-600 dark:text-primary-400 hover:underline">
          Limpiar filtros
        </button>
      </div>
    </div>
    
    <!-- Statistics -->
    <BetStatistics :statistics="statistics" />
    
    <!-- Bets List -->
    <div class="card p-6">
      <div v-if="loading" class="space-y-4">
        <div v-for="i in 5" :key="i" class="flex items-center gap-4 animate-pulse">
          <div class="w-10 h-10 bg-slate-200 dark:bg-slate-700 rounded-xl"></div>
          <div class="flex-1">
            <div class="h-4 bg-slate-200 dark:bg-slate-700 rounded w-1/3 mb-2"></div>
            <div class="h-3 bg-slate-200 dark:bg-slate-700 rounded w-1/4"></div>
          </div>
        </div>
      </div>
      
      <BetList 
        v-else
        :bets="bets"
        @edit="handleEdit"
        @delete="handleDelete"
      />
    </div>
    
    <!-- Bet Modal -->
    <BetModal
      v-if="showModal"
      :bet="selectedBet"
      @close="showModal = false; selectedBet = null"
      @saved="fetchData"
    />
    
    <!-- Delete Confirmation -->
    <Modal v-if="showDeleteModal" title="Eliminar apuesta" @close="showDeleteModal = false">
      <p class="text-slate-600 dark:text-slate-400">
        ¿Estás seguro de eliminar esta apuesta? Esta acción revertirá los cambios en el saldo de la cuenta.
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



