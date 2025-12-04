<script setup>
import { ref, computed } from 'vue'
import { formatMoney, formatDate as formatDateUtil } from '@/composables/useCurrency'
import CategoryIcon from './CategoryIcon.vue'
import {
  ArrowUpIcon,
  ArrowDownIcon,
  ArrowsRightLeftIcon,
} from '@heroicons/vue/24/solid'
import { BugAntIcon, ChevronDownIcon, ChevronUpIcon } from '@heroicons/vue/24/outline'

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

const emit = defineEmits(['edit', 'delete', 'select'])

const expandedTransactions = ref(new Set())

function toggleExpand(transactionId) {
  if (expandedTransactions.value.has(transactionId)) {
    expandedTransactions.value.delete(transactionId)
  } else {
    expandedTransactions.value.add(transactionId)
  }
}

function isExpanded(transactionId) {
  return expandedTransactions.value.has(transactionId)
}

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

function handleTransactionClick(event, transaction) {
  const target = event.target
  const isActionButton = target.closest('button') || target.closest('[role="button"]')
  if (!isActionButton) {
    emit('select', transaction)
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
      @click="handleTransactionClick($event, transaction)"
      class="flex items-center gap-4 p-3 rounded-xl hover:bg-slate-50 dark:hover:bg-slate-800/50 transition-colors group cursor-pointer"
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
            v-if="transaction.has_items"
            class="inline-flex items-center gap-1 px-2 py-0.5 text-xs font-medium rounded-full bg-blue-100 dark:bg-blue-900/30 text-blue-600 dark:text-blue-400 cursor-pointer"
            @click.stop="toggleExpand(transaction.id)"
            :title="isExpanded(transaction.id) ? 'Ocultar productos' : 'Ver productos'"
          >
            <ChevronDownIcon 
              v-if="!isExpanded(transaction.id)"
              class="w-3 h-3 transition-transform"
            />
            <ChevronUpIcon 
              v-else
              class="w-3 h-3 transition-transform"
            />
            {{ transaction.items_count || 0 }} productos
          </span>
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
        
        <!-- Items List (when expanded) -->
        <div v-if="transaction.has_items && isExpanded(transaction.id)" class="mt-3 pt-3 border-t border-slate-200 dark:border-slate-700">
          <div class="space-y-2">
            <div 
              v-for="(item, idx) in transaction.items" 
              :key="idx"
              class="flex items-center justify-between p-2.5 bg-slate-50 dark:bg-slate-800/50 rounded-lg hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors"
            >
              <div class="flex-1 min-w-0">
                <div class="flex items-center gap-2 mb-1">
                  <p class="text-sm font-medium text-slate-900 dark:text-white truncate">
                    {{ item.name }}
                  </p>
                </div>
                <div class="flex items-center gap-2 flex-wrap">
                  <p class="text-xs text-slate-500 dark:text-slate-400">
                    {{ item.quantity }}x {{ formatCurrency(item.amount) }}
                  </p>
                  <div v-if="item.category_name" class="flex items-center gap-1">
                    <CategoryIcon 
                      :icon="item.category_icon || 'otros'"
                      class="w-3 h-3"
                      :style="{ color: item.category_color || '#6366F1' }"
                    />
                    <span 
                      class="text-xs font-medium"
                      :style="{ color: item.category_color || '#6366F1' }"
                    >
                      {{ item.category_name }}
                    </span>
                  </div>
                </div>
              </div>
              <p class="text-sm font-semibold text-slate-900 dark:text-white ml-3 flex-shrink-0">
                {{ formatCurrency(item.total || (item.amount * item.quantity)) }}
              </p>
            </div>
          </div>
          <div class="mt-2 pt-2 border-t border-slate-200 dark:border-slate-700">
            <div class="flex items-center justify-between text-xs">
              <span class="text-slate-500 dark:text-slate-400">
                Total de productos: {{ transaction.items.length }}
              </span>
              <span class="font-semibold text-slate-900 dark:text-white">
                {{ formatCurrency(transaction.amount) }}
              </span>
            </div>
          </div>
        </div>
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
      <div v-if="!compact" class="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity" @click.stop>
        <button
          @click.stop="emit('edit', transaction)"
          class="p-2 rounded-lg hover:bg-slate-200 dark:hover:bg-slate-700 text-slate-600 dark:text-slate-400"
        >
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z" />
          </svg>
        </button>
        <button
          @click.stop="emit('delete', transaction)"
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

