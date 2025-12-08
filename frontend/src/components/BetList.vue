<script setup>
import { computed } from 'vue'
import { formatMoney, formatDate } from '@/composables/useCurrency'
import {
  TrophyIcon,
  XCircleIcon,
  ClockIcon,
} from '@heroicons/vue/24/solid'

const props = defineProps({
  bets: {
    type: Array,
    default: () => []
  }
})

const emit = defineEmits(['edit', 'delete'])

const getResultConfig = (result) => {
  switch (result) {
    case 'ganó':
      return {
        icon: TrophyIcon,
        color: 'text-emerald-600 bg-emerald-100 dark:bg-emerald-900/30 dark:text-emerald-400',
        label: 'Ganó'
      }
    case 'perdió':
      return {
        icon: XCircleIcon,
        color: 'text-red-600 bg-red-100 dark:bg-red-900/30 dark:text-red-400',
        label: 'Perdió'
      }
    default:
      return {
        icon: ClockIcon,
        color: 'text-slate-600 bg-slate-100 dark:bg-slate-800 dark:text-slate-400',
        label: 'Pendiente'
      }
  }
}

const getBetTypeLabel = (betType) => {
  const types = {
    deportes: 'Deportes',
    blackjack: 'Blackjack',
    poker: 'Poker',
    ruleta: 'Ruleta',
    tragamonedas: 'Tragamonedas',
    otros: 'Otros'
  }
  return types[betType] || betType
}
</script>

<template>
  <div v-if="bets.length === 0" class="text-center py-8">
    <p class="text-slate-500 dark:text-slate-400">No hay apuestas registradas</p>
  </div>
  
  <div v-else class="space-y-3">
    <div 
      v-for="bet in bets" 
      :key="bet.id"
      class="card p-4 hover:shadow-md transition-shadow group"
    >
      <div class="flex items-start justify-between gap-4">
        <div class="flex items-start gap-3 flex-1 min-w-0">
          <div 
            :class="getResultConfig(bet.result).color"
            class="w-10 h-10 rounded-xl flex items-center justify-center flex-shrink-0"
          >
            <component :is="getResultConfig(bet.result).icon" class="w-5 h-5" />
          </div>
          
          <div class="flex-1 min-w-0">
            <div class="flex items-center gap-2 flex-wrap">
              <h3 class="font-medium text-slate-900 dark:text-white truncate">
                {{ bet.event_name }}
              </h3>
              <span class="text-xs px-2 py-0.5 rounded-full bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-400">
                {{ getBetTypeLabel(bet.bet_type) }}
              </span>
              <span 
                :class="getResultConfig(bet.result).color"
                class="text-xs px-2 py-0.5 rounded-full font-medium"
              >
                {{ getResultConfig(bet.result).label }}
              </span>
            </div>
            
            <div class="mt-2 flex items-center gap-4 text-sm text-slate-500 dark:text-slate-400">
              <span>{{ bet.account_name }}</span>
              <span>·</span>
              <span>{{ formatDate(bet.date) }}</span>
              <span v-if="bet.odds">·</span>
              <span v-if="bet.odds">Odds: {{ bet.odds }}</span>
            </div>
            
            <div class="mt-3 flex items-center gap-4">
              <div>
                <span class="text-xs text-slate-500 dark:text-slate-400">Apostado:</span>
                <span class="ml-2 font-semibold text-slate-900 dark:text-white">
                  {{ formatMoney(bet.bet_amount) }}
                </span>
              </div>
              
              <div v-if="bet.result === 'ganó'">
                <span class="text-xs text-slate-500 dark:text-slate-400">Ganado:</span>
                <span class="ml-2 font-semibold text-emerald-600 dark:text-emerald-400">
                  {{ formatMoney(bet.payout_amount) }}
                </span>
              </div>
              
              <div v-if="bet.result !== 'pendiente'">
                <span class="text-xs text-slate-500 dark:text-slate-400">Neto:</span>
                <span 
                  class="ml-2 font-bold text-lg"
                  :class="bet.net_result >= 0 ? 'text-emerald-600 dark:text-emerald-400' : 'text-red-600 dark:text-red-400'"
                >
                  {{ bet.net_result >= 0 ? '+' : '' }}{{ formatMoney(bet.net_result) }}
                </span>
              </div>
            </div>
          </div>
        </div>
        
        <div class="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
          <button
            @click="emit('edit', bet)"
            class="p-2 rounded-lg hover:bg-slate-100 dark:hover:bg-slate-800 text-slate-600 dark:text-slate-400"
            title="Editar"
          >
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z" />
            </svg>
          </button>
          <button
            @click="emit('delete', bet)"
            class="p-2 rounded-lg hover:bg-red-100 dark:hover:bg-red-900/30 text-red-600 dark:text-red-400"
            title="Eliminar"
          >
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
            </svg>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>






