<script setup>
import { computed } from 'vue'
import { ExclamationTriangleIcon, CheckCircleIcon } from '@heroicons/vue/24/outline'
import { formatMoney } from '@/composables/useCurrency'

const props = defineProps({
  alerts: {
    type: Array,
    default: () => []
  }
})

function formatCurrency(value) {
  return formatMoney(value)
}
</script>

<template>
  <div v-if="alerts.length === 0" class="text-center py-8">
    <div class="w-12 h-12 mx-auto mb-3 rounded-full bg-emerald-100 dark:bg-emerald-900/30 flex items-center justify-center">
      <CheckCircleIcon class="w-6 h-6 text-emerald-600 dark:text-emerald-400" />
    </div>
    <p class="text-slate-600 dark:text-slate-400">¡Todo en orden!</p>
    <p class="text-sm text-slate-500 dark:text-slate-500">No hay presupuestos excedidos</p>
  </div>
  
  <div v-else class="space-y-3">
    <div 
      v-for="alert in alerts" 
      :key="alert.id"
      class="p-4 rounded-xl"
      :class="alert.is_exceeded ? 'bg-red-50 dark:bg-red-900/20' : 'bg-amber-50 dark:bg-amber-900/20'"
    >
      <div class="flex items-start gap-3">
        <ExclamationTriangleIcon 
          class="w-5 h-5 flex-shrink-0 mt-0.5"
          :class="alert.is_exceeded ? 'text-red-600 dark:text-red-400' : 'text-amber-600 dark:text-amber-400'"
        />
        <div class="flex-1 min-w-0">
          <p 
            class="font-medium"
            :class="alert.is_exceeded ? 'text-red-900 dark:text-red-100' : 'text-amber-900 dark:text-amber-100'"
          >
            {{ alert.category_name }}
          </p>
          <p 
            class="text-sm mt-1"
            :class="alert.is_exceeded ? 'text-red-700 dark:text-red-300' : 'text-amber-700 dark:text-amber-300'"
          >
            {{ formatCurrency(alert.spent) }} de {{ formatCurrency(alert.limit) }}
          </p>
          
          <!-- Progress bar -->
          <div class="mt-2 h-2 rounded-full overflow-hidden"
            :class="alert.is_exceeded ? 'bg-red-200 dark:bg-red-900/50' : 'bg-amber-200 dark:bg-amber-900/50'"
          >
            <div 
              class="h-full rounded-full transition-all"
              :class="alert.is_exceeded ? 'bg-red-600' : 'bg-amber-600'"
              :style="{ width: Math.min(alert.percentage, 100) + '%' }"
            />
          </div>
          
          <p 
            class="text-xs mt-1 font-medium"
            :class="alert.is_exceeded ? 'text-red-600 dark:text-red-400' : 'text-amber-600 dark:text-amber-400'"
          >
            {{ alert.percentage.toFixed(0) }}% {{ alert.is_exceeded ? 'excedido' : 'usado' }}
          </p>
        </div>
      </div>
    </div>
  </div>
</template>

