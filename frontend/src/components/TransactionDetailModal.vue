<script setup>
import { computed } from 'vue'
import Modal from './Modal.vue'
import CategoryIcon from './CategoryIcon.vue'
import { formatMoney, formatDate } from '@/composables/useCurrency'
import {
  ArrowUpIcon,
  ArrowDownIcon,
  ArrowsRightLeftIcon,
  BugAntIcon,
  ArrowPathIcon,
} from '@heroicons/vue/24/solid'
import { PencilIcon, TrashIcon } from '@heroicons/vue/24/outline'

const props = defineProps({
  transaction: {
    type: Object,
    required: true
  }
})

const emit = defineEmits(['close', 'edit', 'delete'])

const transactionTypeConfig = computed(() => {
  switch (props.transaction.transaction_type) {
    case 'ingreso':
      return {
        icon: ArrowUpIcon,
        color: 'text-emerald-600 bg-emerald-100 dark:bg-emerald-900/30 dark:text-emerald-400',
        label: 'Ingreso'
      }
    case 'gasto':
      return {
        icon: ArrowDownIcon,
        color: 'text-red-600 bg-red-100 dark:bg-red-900/30 dark:text-red-400',
        label: 'Gasto'
      }
    case 'transferencia':
      return {
        icon: ArrowsRightLeftIcon,
        color: 'text-blue-600 bg-blue-100 dark:bg-blue-900/30 dark:text-blue-400',
        label: 'Transferencia'
      }
    default:
      return {
        icon: ArrowDownIcon,
        color: 'text-slate-600 bg-slate-100',
        label: 'Transacción'
      }
  }
})

const formattedAmount = computed(() => {
  return formatMoney(props.transaction.amount)
})

const formattedDate = computed(() => {
  return formatDate(props.transaction.date)
})

const hasItems = computed(() => {
  return props.transaction.items && props.transaction.items.length > 0
})

const totalItemsAmount = computed(() => {
  if (!hasItems.value) return 0
  return props.transaction.items.reduce((sum, item) => {
    return sum + (parseFloat(item.amount) || 0) * (parseInt(item.quantity) || 1)
  }, 0)
})

function handleEdit() {
  emit('edit', props.transaction)
  emit('close')
}

function handleDelete() {
  if (confirm('¿Estás seguro de eliminar esta transacción?')) {
    emit('delete', props.transaction)
    emit('close')
  }
}
</script>

<template>
  <Modal title="Detalles de transacción" size="lg" @close="emit('close')">
    <div class="space-y-6">
      <!-- Header: Tipo y Monto -->
      <div class="flex items-center justify-between">
        <div class="flex items-center gap-3">
          <div 
            :class="transactionTypeConfig.color"
            class="w-12 h-12 rounded-xl flex items-center justify-center"
          >
            <component :is="transactionTypeConfig.icon" class="w-6 h-6" />
          </div>
          <div>
            <h3 class="font-semibold text-slate-900 dark:text-white">
              {{ transactionTypeConfig.label }}
            </h3>
            <p class="text-sm text-slate-500 dark:text-slate-400">
              {{ formattedDate }}
            </p>
          </div>
        </div>
        <div class="text-right">
          <p 
            :class="[
              'text-2xl font-bold',
              props.transaction.transaction_type === 'ingreso' 
                ? 'text-emerald-600 dark:text-emerald-400'
                : props.transaction.transaction_type === 'gasto'
                ? 'text-red-600 dark:text-red-400'
                : 'text-blue-600 dark:text-blue-400'
            ]"
          >
            {{ props.transaction.transaction_type === 'ingreso' ? '+' : props.transaction.transaction_type === 'gasto' ? '-' : '' }}
            {{ formattedAmount }}
          </p>
        </div>
      </div>

      <!-- Descripción -->
      <div v-if="props.transaction.description">
        <h4 class="text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">Descripción</h4>
        <p class="text-slate-900 dark:text-white">{{ props.transaction.description }}</p>
      </div>

      <!-- Cuentas -->
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <h4 class="text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">Cuenta origen</h4>
          <div class="flex items-center gap-2 p-3 bg-slate-50 dark:bg-slate-800 rounded-lg">
            <div 
              v-if="props.transaction.account_color"
              class="w-3 h-3 rounded-full"
              :style="{ backgroundColor: props.transaction.account_color }"
            />
            <span class="text-slate-900 dark:text-white font-medium">
              {{ props.transaction.account_name }}
            </span>
          </div>
        </div>
        
        <div v-if="props.transaction.transaction_type === 'transferencia' && props.transaction.destination_account_name">
          <h4 class="text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">Cuenta destino</h4>
          <div class="flex items-center gap-2 p-3 bg-slate-50 dark:bg-slate-800 rounded-lg">
            <span class="text-slate-900 dark:text-white font-medium">
              {{ props.transaction.destination_account_name }}
            </span>
          </div>
        </div>
      </div>

      <!-- Categoría -->
      <div v-if="props.transaction.category_name">
        <h4 class="text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">Categoría</h4>
        <div class="flex items-center gap-2 p-3 bg-slate-50 dark:bg-slate-800 rounded-lg">
          <CategoryIcon 
            :icon="props.transaction.category_icon || 'otros'"
            class="w-5 h-5"
            :style="{ color: props.transaction.category_color || '#6366F1' }"
          />
          <span 
            class="font-medium"
            :style="{ color: props.transaction.category_color || '#6366F1' }"
          >
            {{ props.transaction.category_name }}
          </span>
        </div>
      </div>

      <!-- Items/Productos -->
      <div v-if="hasItems">
        <h4 class="text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
          Productos ({{ props.transaction.items.length }})
        </h4>
        <div class="space-y-2">
          <div
            v-for="(item, index) in props.transaction.items"
            :key="index"
            class="p-3 bg-slate-50 dark:bg-slate-800 rounded-lg"
          >
            <div class="flex items-start justify-between mb-2">
              <div class="flex-1">
                <p class="font-medium text-slate-900 dark:text-white">{{ item.name }}</p>
                <p class="text-sm text-slate-500 dark:text-slate-400">
                  {{ item.quantity }}x {{ formatMoney(item.amount) }}
                </p>
                <div v-if="item.category_name" class="flex items-center gap-1.5 mt-1">
                  <CategoryIcon 
                    :icon="item.category_icon || 'otros'"
                    class="w-3 h-3"
                    :style="{ color: item.category_color || '#6366F1' }"
                  />
                  <span 
                    class="text-xs"
                    :style="{ color: item.category_color || '#6366F1' }"
                  >
                    {{ item.category_name }}
                  </span>
                </div>
              </div>
              <p class="font-semibold text-slate-900 dark:text-white ml-3">
                {{ formatMoney(item.total || (item.amount * item.quantity)) }}
              </p>
            </div>
          </div>
        </div>
        <div class="mt-3 pt-3 border-t border-slate-200 dark:border-slate-700">
          <div class="flex items-center justify-between">
            <span class="font-semibold text-slate-900 dark:text-white">Total:</span>
            <span class="text-lg font-bold text-slate-900 dark:text-white">
              {{ formatMoney(totalItemsAmount) }}
            </span>
          </div>
        </div>
      </div>

      <!-- Flags -->
      <div v-if="props.transaction.is_ant_expense || props.transaction.is_recurring" class="flex flex-wrap gap-2">
        <div 
          v-if="props.transaction.is_ant_expense"
          class="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-orange-100 dark:bg-orange-900/30 text-orange-600 dark:text-orange-400"
        >
          <BugAntIcon class="w-4 h-4" />
          <span class="text-sm font-medium">Gasto hormiga</span>
        </div>
        <div 
          v-if="props.transaction.is_recurring"
          class="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-blue-100 dark:bg-blue-900/30 text-blue-600 dark:text-blue-400"
        >
          <ArrowPathIcon class="w-4 h-4" />
          <span class="text-sm font-medium">Recurrente</span>
        </div>
      </div>

      <!-- Notas -->
      <div v-if="props.transaction.notes">
        <h4 class="text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">Notas</h4>
        <div class="p-3 bg-slate-50 dark:bg-slate-800 rounded-lg">
          <p class="text-slate-900 dark:text-white whitespace-pre-wrap">{{ props.transaction.notes }}</p>
        </div>
      </div>

      <!-- Información adicional -->
      <div v-if="props.transaction.created_at || props.transaction.updated_at" class="pt-4 border-t border-slate-200 dark:border-slate-700">
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
          <div v-if="props.transaction.created_at">
            <span class="text-slate-500 dark:text-slate-400">Creada:</span>
            <span class="ml-2 text-slate-900 dark:text-white">
              {{ new Date(props.transaction.created_at).toLocaleString('es-ES') }}
            </span>
          </div>
          <div v-if="props.transaction.updated_at">
            <span class="text-slate-500 dark:text-slate-400">Actualizada:</span>
            <span class="ml-2 text-slate-900 dark:text-white">
              {{ new Date(props.transaction.updated_at).toLocaleString('es-ES') }}
            </span>
          </div>
        </div>
      </div>
    </div>

    <template #footer>
      <div class="flex justify-between items-center">
        <button
          @click="handleDelete"
          class="btn-danger flex items-center gap-2"
        >
          <TrashIcon class="w-4 h-4" />
          Eliminar
        </button>
        <div class="flex gap-3">
          <button @click="emit('close')" class="btn-secondary">
            Cerrar
          </button>
          <button @click="handleEdit" class="btn-primary flex items-center gap-2">
            <PencilIcon class="w-4 h-4" />
            Editar
          </button>
        </div>
      </div>
    </template>
  </Modal>
</template>

