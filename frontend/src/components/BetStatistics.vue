<script setup>
import { computed } from 'vue'
import { formatMoney } from '@/composables/useCurrency'
import StatCard from './StatCard.vue'
import {
  CurrencyDollarIcon,
  ArrowTrendingUpIcon,
  ArrowTrendingDownIcon,
  ChartBarIcon,
  TrophyIcon,
  XCircleIcon,
} from '@heroicons/vue/24/outline'

const props = defineProps({
  statistics: {
    type: Object,
    default: null
  }
})

const totalBet = computed(() => {
  return props.statistics?.total_bet || 0
})

const totalWon = computed(() => {
  return props.statistics?.total_won || 0
})

const totalLost = computed(() => {
  return props.statistics?.total_lost || 0
})

const netResult = computed(() => {
  return props.statistics?.net_result || 0
})

const roi = computed(() => {
  return props.statistics?.roi || 0
})

const winRate = computed(() => {
  return props.statistics?.win_rate || 0
})

const totalBets = computed(() => {
  return props.statistics?.total_bets || 0
})

const wonCount = computed(() => {
  return props.statistics?.won_count || 0
})

const lostCount = computed(() => {
  return props.statistics?.lost_count || 0
})
</script>

<template>
  <div v-if="statistics" class="space-y-6">
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
      <StatCard
        title="Total Apostado"
        :value="formatMoney(totalBet)"
        :icon="CurrencyDollarIcon"
        color="warning"
      />
      
      <StatCard
        title="Total Ganado"
        :value="formatMoney(totalWon)"
        :icon="ArrowTrendingUpIcon"
        color="success"
      />
      
      <StatCard
        title="Total Perdido"
        :value="formatMoney(totalLost)"
        :icon="ArrowTrendingDownIcon"
        color="danger"
      />
      
      <StatCard
        title="Resultado Neto"
        :value="formatMoney(netResult)"
        :icon="ChartBarIcon"
        :color="netResult >= 0 ? 'success' : 'danger'"
      />
    </div>
    
    <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
      <div class="card p-6">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-sm font-medium text-slate-500 dark:text-slate-400">ROI (Return on Investment)</p>
            <p 
              class="mt-2 text-2xl font-bold"
              :class="roi >= 0 ? 'text-emerald-600 dark:text-emerald-400' : 'text-red-600 dark:text-red-400'"
            >
              {{ roi >= 0 ? '+' : '' }}{{ roi.toFixed(2) }}%
            </p>
          </div>
          <div 
            :class="roi >= 0 ? 'bg-emerald-100 dark:bg-emerald-900/30 text-emerald-600' : 'bg-red-100 dark:bg-red-900/30 text-red-600'"
            class="w-12 h-12 rounded-xl flex items-center justify-center"
          >
            <ChartBarIcon class="w-6 h-6" />
          </div>
        </div>
      </div>
      
      <div class="card p-6">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-sm font-medium text-slate-500 dark:text-slate-400">Tasa de Éxito</p>
            <p class="mt-2 text-2xl font-bold text-slate-900 dark:text-white">
              {{ winRate.toFixed(1) }}%
            </p>
            <p class="mt-1 text-xs text-slate-500 dark:text-slate-400">
              {{ wonCount }} ganadas / {{ lostCount }} perdidas
            </p>
          </div>
          <div class="w-12 h-12 rounded-xl flex items-center justify-center bg-blue-100 dark:bg-blue-900/30 text-blue-600">
            <TrophyIcon class="w-6 h-6" />
          </div>
        </div>
      </div>
      
      <div class="card p-6">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-sm font-medium text-slate-500 dark:text-slate-400">Total de Apuestas</p>
            <p class="mt-2 text-2xl font-bold text-slate-900 dark:text-white">
              {{ totalBets }}
            </p>
            <p class="mt-1 text-xs text-slate-500 dark:text-slate-400">
              {{ statistics?.pending_count || 0 }} pendientes
            </p>
          </div>
          <div class="w-12 h-12 rounded-xl flex items-center justify-center bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-400">
            <ChartBarIcon class="w-6 h-6" />
          </div>
        </div>
      </div>
    </div>
    
    <div v-if="netResult < 0" class="p-4 bg-red-50 dark:bg-red-900/20 border-2 border-red-200 dark:border-red-800 rounded-xl">
      <div class="flex items-center gap-3">
        <XCircleIcon class="w-6 h-6 text-red-600 dark:text-red-400 flex-shrink-0" />
        <div>
          <p class="font-semibold text-red-900 dark:text-red-200">
            Has perdido {{ formatMoney(Math.abs(netResult)) }} en apuestas
          </p>
          <p class="text-sm text-red-700 dark:text-red-300 mt-1">
            Considera detenerte antes de que las pérdidas aumenten. Las apuestas no son una forma de recuperar dinero perdido.
          </p>
        </div>
      </div>
    </div>
  </div>
  
  <div v-else class="text-center py-12">
    <p class="text-slate-500 dark:text-slate-400">Cargando estadísticas...</p>
  </div>
</template>



