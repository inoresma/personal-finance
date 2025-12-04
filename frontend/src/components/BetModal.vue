<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useAccountsStore } from '@/stores/accounts'
import { useBetsStore } from '@/stores/bets'
import { useUiStore } from '@/stores/ui'
import { formatMoney } from '@/composables/useCurrency'
import Modal from './Modal.vue'
import DateInput from './DateInput.vue'
import BetWarningBanner from './BetWarningBanner.vue'

const props = defineProps({
  bet: {
    type: Object,
    default: null
  }
})

const emit = defineEmits(['close', 'saved'])

const accountsStore = useAccountsStore()
const betsStore = useBetsStore()
const uiStore = useUiStore()

const loading = ref(false)

const form = ref({
  bet_type: 'deportes',
  event_name: '',
  sport_type: null,
  bet_amount: '',
  odds: '',
  result: 'pendiente',
  payout_amount: '',
  account: null,
  date: new Date().toISOString().split('T')[0],
  notes: '',
})

const isEditing = computed(() => !!props.bet)

const title = computed(() => isEditing.value ? 'Editar apuesta' : 'Nueva apuesta')

const betTypes = [
  { value: 'deportes', label: 'Deportes' },
  { value: 'blackjack', label: 'Blackjack' },
  { value: 'poker', label: 'Poker' },
  { value: 'ruleta', label: 'Ruleta' },
  { value: 'tragamonedas', label: 'Tragamonedas' },
  { value: 'otros', label: 'Otros' },
]

const sportTypes = [
  { value: 'futbol', label: 'Fútbol' },
  { value: 'basquet', label: 'Básquetbol' },
  { value: 'tenis', label: 'Tenis' },
  { value: 'beisbol', label: 'Béisbol' },
  { value: 'futbol_americano', label: 'Fútbol Americano' },
  { value: 'hockey', label: 'Hockey' },
  { value: 'boxeo', label: 'Boxeo' },
  { value: 'mma', label: 'MMA' },
  { value: 'otros', label: 'Otros' },
]

const resultOptions = [
  { value: 'pendiente', label: 'Pendiente' },
  { value: 'ganó', label: 'Ganó' },
  { value: 'perdió', label: 'Perdió' },
]

const showSportType = computed(() => form.value.bet_type === 'deportes')

const netResult = computed(() => {
  if (form.value.result === 'ganó' && form.value.payout_amount && form.value.bet_amount) {
    return parseFloat(form.value.payout_amount) - parseFloat(form.value.bet_amount)
  } else if (form.value.result === 'perdió' && form.value.bet_amount) {
    return -parseFloat(form.value.bet_amount)
  }
  return 0
})

watch(() => form.value.result, (newResult) => {
  if (newResult !== 'ganó') {
    form.value.payout_amount = ''
  }
})

watch(() => form.value.bet_type, (newType) => {
  if (newType !== 'deportes') {
    form.value.sport_type = null
  }
})

async function handleSubmit() {
  if (!form.value.account) {
    uiStore.showError('Por favor selecciona una cuenta')
    return
  }
  
  if (!form.value.event_name || !form.value.event_name.trim()) {
    uiStore.showError('El evento/descripción es requerido')
    return
  }
  
  if (!form.value.bet_amount || parseFloat(form.value.bet_amount) <= 0) {
    uiStore.showError('El monto apostado debe ser mayor a 0')
    return
  }
  
  if (form.value.result === 'ganó') {
    if (!form.value.payout_amount || parseFloat(form.value.payout_amount) <= 0) {
      uiStore.showError('El monto ganado es requerido cuando el resultado es "ganó"')
      return
    }
  }
  
  loading.value = true
  
  try {
    const data = {
      bet_type: form.value.bet_type,
      event_name: form.value.event_name.trim(),
      sport_type: form.value.sport_type || null,
      bet_amount: parseFloat(form.value.bet_amount),
      odds: form.value.odds ? parseFloat(form.value.odds) : null,
      result: form.value.result,
      payout_amount: form.value.result === 'ganó' ? parseFloat(form.value.payout_amount) : 0,
      account: form.value.account,
      date: form.value.date,
      notes: form.value.notes || '',
    }
    
    if (isEditing.value) {
      await betsStore.updateBet(props.bet.id, data)
      uiStore.showSuccess('Apuesta actualizada')
    } else {
      await betsStore.createBet(data)
      uiStore.showSuccess('Apuesta creada')
    }
    
    await accountsStore.fetchAccounts()
    // Forzar actualización de estadísticas
    await betsStore.fetchStatistics()
    emit('saved')
    emit('close')
  } catch (error) {
    const errorMessage = error.response?.data?.detail || error.response?.data?.payout_amount?.[0] || 'Error al guardar la apuesta'
    uiStore.showError(errorMessage)
  } finally {
    loading.value = false
  }
}

onMounted(async () => {
  if (accountsStore.accounts.length === 0) {
    await accountsStore.fetchAccounts()
  }
  
  if (props.bet) {
    form.value = {
      bet_type: props.bet.bet_type,
      event_name: props.bet.event_name,
      sport_type: props.bet.sport_type,
      bet_amount: props.bet.bet_amount,
      odds: props.bet.odds || '',
      result: props.bet.result,
      payout_amount: props.bet.payout_amount || '',
      account: props.bet.account,
      date: props.bet.date,
      notes: props.bet.notes || '',
    }
  } else if (accountsStore.accounts.length > 0) {
    form.value.account = accountsStore.accounts[0].id
  }
})
</script>

<template>
  <Modal :title="title" size="lg" @close="emit('close')">
    <BetWarningBanner />
    
    <form @submit.prevent="handleSubmit" class="space-y-5">
      <div>
        <label class="label">Tipo de apuesta *</label>
        <select v-model="form.bet_type" class="input">
          <option v-for="type in betTypes" :key="type.value" :value="type.value">
            {{ type.label }}
          </option>
        </select>
      </div>
      
      <div>
        <label class="label">Evento/Descripción *</label>
        <input
          v-model="form.event_name"
          type="text"
          placeholder="Ej: Real Madrid vs Barcelona"
          class="input"
          required
        />
      </div>
      
      <div v-if="showSportType">
        <label class="label">Tipo de deporte</label>
        <select v-model="form.sport_type" class="input">
          <option :value="null">Selecciona un deporte</option>
          <option v-for="sport in sportTypes" :key="sport.value" :value="sport.value">
            {{ sport.label }}
          </option>
        </select>
      </div>
      
      <div class="grid grid-cols-2 gap-4">
        <div>
          <label class="label">Monto apostado *</label>
          <div class="relative">
            <span class="absolute left-4 top-1/2 -translate-y-1/2 text-slate-400 font-medium">$</span>
            <input
              v-model="form.bet_amount"
              type="number"
              step="0.01"
              min="0"
              placeholder="0"
              class="input pl-10"
              required
            />
          </div>
        </div>
        
        <div>
          <label class="label">Cuota/Odds (opcional)</label>
          <input
            v-model="form.odds"
            type="number"
            step="0.01"
            min="0"
            placeholder="Ej: 2.5"
            class="input"
          />
        </div>
      </div>
      
      <div>
        <label class="label">Resultado *</label>
        <div class="grid grid-cols-3 gap-2">
          <button
            v-for="option in resultOptions"
            :key="option.value"
            type="button"
            @click="form.result = option.value"
            :class="[
              'px-4 py-2.5 rounded-xl font-medium text-sm transition-all',
              form.result === option.value
                ? option.value === 'ganó'
                  ? 'bg-emerald-100 dark:bg-emerald-900/30 text-emerald-600 dark:text-emerald-400'
                  : option.value === 'perdió'
                  ? 'bg-red-100 dark:bg-red-900/30 text-red-600 dark:text-red-400'
                  : 'bg-amber-100 dark:bg-amber-900/30 text-amber-600 dark:text-amber-400'
                : 'bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-400 hover:bg-slate-200 dark:hover:bg-slate-700'
            ]"
          >
            {{ option.label }}
          </button>
        </div>
      </div>
      
      <div v-if="form.result === 'ganó'">
        <label class="label">Monto ganado *</label>
        <div class="relative">
          <span class="absolute left-4 top-1/2 -translate-y-1/2 text-slate-400 font-medium">$</span>
          <input
            v-model="form.payout_amount"
            type="number"
            step="0.01"
            min="0"
            placeholder="0"
            class="input pl-10"
            required
          />
        </div>
      </div>
      
      <div v-if="form.result !== 'pendiente'" class="p-3 rounded-lg" :class="netResult >= 0 ? 'bg-emerald-50 dark:bg-emerald-900/20' : 'bg-red-50 dark:bg-red-900/20'">
        <div class="flex items-center justify-between">
          <span class="text-sm font-medium" :class="netResult >= 0 ? 'text-emerald-700 dark:text-emerald-300' : 'text-red-700 dark:text-red-300'">
            Resultado neto:
          </span>
          <span class="font-bold text-lg" :class="netResult >= 0 ? 'text-emerald-600 dark:text-emerald-400' : 'text-red-600 dark:text-red-400'">
            {{ netResult >= 0 ? '+' : '' }}{{ formatMoney(netResult) }}
          </span>
        </div>
      </div>
      
      <div>
        <label class="label">Cuenta *</label>
        <select v-model="form.account" class="input" required>
          <option :value="null" disabled>Selecciona una cuenta</option>
          <option 
            v-for="account in accountsStore.activeAccounts" 
            :key="account.id" 
            :value="account.id"
          >
            {{ account.name }} ({{ formatMoney(account.balance) }})
          </option>
        </select>
      </div>
      
      <div>
        <label class="label">Fecha *</label>
        <DateInput v-model="form.date" />
      </div>
      
      <div>
        <label class="label">Notas (opcional)</label>
        <textarea
          v-model="form.notes"
          rows="2"
          placeholder="Notas adicionales..."
          class="input resize-none"
        />
      </div>
    </form>
    
    <template #footer>
      <div class="flex justify-end gap-3">
        <button 
          type="button"
          @click="emit('close')"
          class="btn-secondary"
        >
          Cancelar
        </button>
        <button
          @click="handleSubmit"
          :disabled="loading"
          class="btn-primary"
        >
          {{ loading ? 'Guardando...' : isEditing ? 'Actualizar' : 'Crear apuesta' }}
        </button>
      </div>
    </template>
  </Modal>
</template>

