<script setup>
import { computed } from 'vue'
import { PencilIcon, TrashIcon, EllipsisVerticalIcon } from '@heroicons/vue/24/outline'
import { 
  BanknotesIcon, 
  BuildingLibraryIcon, 
  CreditCardIcon,
  GlobeAltIcon,
  WalletIcon,
} from '@heroicons/vue/24/solid'
import { formatMoney } from '@/composables/useCurrency'

const props = defineProps({
  account: {
    type: Object,
    required: true
  }
})

const emit = defineEmits(['edit', 'delete', 'detail'])

const accountIcons = {
  efectivo: BanknotesIcon,
  banco: BuildingLibraryIcon,
  credito: CreditCardIcon,
  debito: CreditCardIcon,
  billetera: GlobeAltIcon,
  inversion: WalletIcon,
  otro: WalletIcon,
}

const icon = computed(() => accountIcons[props.account.account_type] || WalletIcon)

function formatCurrency(value) {
  return formatMoney(value, props.account.currency || 'CLP')
}
</script>

<template>
  <div 
    @click="emit('detail', account)"
    class="card p-5 hover:shadow-md transition-shadow group cursor-pointer"
  >
    <div class="flex items-start justify-between">
      <div class="flex items-center gap-3">
        <div 
          class="w-12 h-12 rounded-xl flex items-center justify-center"
          :style="{ backgroundColor: account.color + '20' }"
        >
          <component 
            :is="icon" 
            class="w-6 h-6"
            :style="{ color: account.color }"
          />
        </div>
        <div>
          <h3 class="font-semibold text-slate-900 dark:text-white">{{ account.name }}</h3>
          <p class="text-sm text-slate-500 dark:text-slate-400">{{ account.account_type_display }}</p>
        </div>
      </div>
      
      <div class="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
        <button
          @click.stop="emit('edit', account)"
          class="p-2 rounded-lg hover:bg-slate-100 dark:hover:bg-slate-800 text-slate-600 dark:text-slate-400"
        >
          <PencilIcon class="w-4 h-4" />
        </button>
        <button
          @click.stop="emit('delete', account)"
          class="p-2 rounded-lg hover:bg-red-100 dark:hover:bg-red-900/30 text-red-600 dark:text-red-400"
        >
          <TrashIcon class="w-4 h-4" />
        </button>
      </div>
    </div>
    
    <div class="mt-4 pt-4 border-t border-slate-100 dark:border-slate-800">
      <p class="text-sm text-slate-500 dark:text-slate-400">Saldo actual</p>
      <p 
        class="text-2xl font-bold"
        :class="account.balance >= 0 ? 'text-slate-900 dark:text-white' : 'text-red-600 dark:text-red-400'"
      >
        {{ formatCurrency(account.balance) }}
      </p>
    </div>
    
    <div v-if="!account.include_in_total" class="mt-3">
      <span class="text-xs px-2 py-1 rounded-full bg-slate-100 dark:bg-slate-800 text-slate-500">
        No incluida en total
      </span>
    </div>
  </div>
</template>

