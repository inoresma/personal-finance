<script setup>
import { computed } from 'vue'
import { formatMoney, formatDate as formatDateUtil } from '@/composables/useCurrency'
import {
  ArrowUpIcon,
  ArrowDownIcon,
  ArrowsRightLeftIcon,
} from '@heroicons/vue/24/solid'
import { BugAntIcon } from '@heroicons/vue/24/outline'

const props = defineProps({
  transactions: {
    type: Array,
    default: () => []
  },
  compact: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['edit', 'delete'])

function formatDate(dateString) {
  return formatDateUtil(dateString)
}

function formatCurrency(amount) {
  return formatMoney(amount)
}

function getTypeIcon(type) {
  switch (type) {
    case 'ingreso': return ArrowUpIcon
    case 'gasto': return ArrowDownIcon
    case 'transferencia': return ArrowsRightLeftIcon
    default: return ArrowDownIcon
  }
}

function getTypeColor(type) {
  switch (type) {
    case 'ingreso': return 'text-emerald-600 bg-emerald-100 dark:bg-emerald-900/30 dark:text-emerald-400'
    case 'gasto': return 'text-red-600 bg-red-100 dark:bg-red-900/30 dark:text-red-400'
    case 'transferencia': return 'text-blue-600 bg-blue-100 dark:bg-blue-900/30 dark:text-blue-400'
    default: return 'text-slate-600 bg-slate-100'
  }
}

function getAmountClass(type) {
  switch (type) {
    case 'ingreso': return 'text-emerald-600 dark:text-emerald-400'
    case 'gasto': return 'text-red-600 dark:text-red-400'
    default: return 'text-slate-600 dark:text-slate-400'
  }
}
</script>

<template>
  <div v-if="transactions.length === 0" class="text-center py-8">
    <p class="text-slate-500 dark:text-slate-400">No hay transacciones</p>
  </div>
  
  <div v-else class="space-y-3">
    <div 
      v-for="transaction in transactions" 
      :key="transaction.id"
      class="flex items-center gap-4 p-3 rounded-xl hover:bg-slate-50 dark:hover:bg-slate-800/50 transition-colors group"
    >
      <!-- Icon -->
      <div 
        :class="getTypeColor(transaction.transaction_type)"
        class="w-10 h-10 rounded-xl flex items-center justify-center flex-shrink-0"
      >
        <component :is="getTypeIcon(transaction.transaction_type)" class="w-5 h-5" />
      </div>
      
      <!-- Info -->
      <div class="flex-1 min-w-0">
        <div class="flex items-center gap-2">
          <p class="font-medium text-slate-900 dark:text-white truncate">
            {{ transaction.description || 'Sin descripción' }}
          </p>
          <BugAntIcon 
            v-if="transaction.is_ant_expense" 
            class="w-4 h-4 text-orange-500 flex-shrink-0" 
            title="Gasto hormiga"
          />
          <span 
            v-if="transaction.category_name"
            class="hidden sm:inline-flex px-2 py-0.5 text-xs font-medium rounded-full"
            :style="{ backgroundColor: transaction.category_color + '20', color: transaction.category_color }"
          >
            {{ transaction.category_name }}
          </span>
        </div>
        <p class="text-sm text-slate-500 dark:text-slate-400">
          <template v-if="transaction.transaction_type === 'transferencia' && transaction.destination_account_name">
            {{ transaction.account_name }} → {{ transaction.destination_account_name }} · {{ formatDate(transaction.date) }}
          </template>
          <template v-else>
            {{ transaction.account_name }} · {{ formatDate(transaction.date) }}
          </template>
        </p>
      </div>
      
      <!-- Amount -->
      <div class="text-right">
        <p 
          :class="getAmountClass(transaction.transaction_type)"
          class="font-semibold"
        >
          {{ transaction.transaction_type === 'ingreso' ? '+' : transaction.transaction_type === 'gasto' ? '-' : '' }}
          {{ formatCurrency(transaction.amount) }}
        </p>
      </div>
      
      <!-- Actions (not in compact mode) -->
      <div v-if="!compact" class="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
        <button
          @click="emit('edit', transaction)"
          class="p-2 rounded-lg hover:bg-slate-200 dark:hover:bg-slate-700 text-slate-600 dark:text-slate-400"
        >
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z" />
          </svg>
        </button>
        <button
          @click="emit('delete', transaction)"
          class="p-2 rounded-lg hover:bg-red-100 dark:hover:bg-red-900/30 text-red-600 dark:text-red-400"
        >
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
          </svg>
        </button>
      </div>
    </div>
  </div>
</template>

