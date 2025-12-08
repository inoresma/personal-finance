<script setup>
import { computed } from 'vue'
import GoalProgress from './GoalProgress.vue'
import { formatMoney } from '@/composables/useCurrency'
import { 
  BanknotesIcon, 
  ChartBarIcon,
  CalendarIcon,
  CheckCircleIcon,
  XCircleIcon
} from '@heroicons/vue/24/outline'
import { CheckCircleIcon as CheckCircleIconSolid } from '@heroicons/vue/24/solid'

const props = defineProps({
  goal: {
    type: Object,
    required: true
  }
})

const emit = defineEmits(['edit', 'delete', 'toggle'])

const goalTypeIcon = computed(() => {
  return props.goal.goal_type === 'savings' ? BanknotesIcon : ChartBarIcon
})

const goalTypeColor = computed(() => {
  return props.goal.goal_type === 'savings' 
    ? 'bg-emerald-100 dark:bg-emerald-900/30 text-emerald-600 dark:text-emerald-400'
    : 'bg-blue-100 dark:bg-blue-900/30 text-blue-600 dark:text-blue-400'
})

const daysRemaining = computed(() => {
  const today = new Date()
  const targetDate = new Date(props.goal.target_date)
  const diffTime = targetDate - today
  const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24))
  return Math.max(0, diffDays)
})

const isOverdue = computed(() => {
  return daysRemaining.value === 0 && !props.goal.is_completed
})
</script>

<template>
  <div class="card p-6 hover:shadow-lg transition-all">
    <div class="flex items-start justify-between mb-4">
      <div class="flex items-start gap-3 flex-1">
        <div :class="goalTypeColor" class="w-12 h-12 rounded-xl flex items-center justify-center flex-shrink-0">
          <component :is="goalTypeIcon" class="w-6 h-6" />
        </div>
        <div class="flex-1 min-w-0">
          <div class="flex items-center gap-2">
            <h3 class="text-lg font-semibold text-slate-900 dark:text-white truncate">
              {{ goal.name }}
            </h3>
            <component 
              :is="goal.is_completed ? CheckCircleIconSolid : CheckCircleIcon"
              :class="goal.is_completed ? 'text-emerald-500' : 'text-slate-400'"
              class="w-5 h-5 flex-shrink-0"
            />
          </div>
          <p class="text-sm text-slate-500 dark:text-slate-400 mt-1">
            {{ goal.goal_type_display }}
            <span v-if="goal.category_data" class="ml-2">
              · {{ goal.category_data.name }}
            </span>
          </p>
        </div>
      </div>
      <div class="flex items-center gap-2">
        <button
          @click="$emit('toggle', goal.id)"
          :class="goal.is_active ? 'text-emerald-600' : 'text-slate-400'"
          class="p-1 hover:bg-slate-100 dark:hover:bg-slate-800 rounded transition-colors"
          :title="goal.is_active ? 'Desactivar' : 'Activar'"
        >
          <component 
            :is="goal.is_active ? CheckCircleIconSolid : XCircleIcon"
            class="w-5 h-5"
          />
        </button>
      </div>
    </div>

    <div v-if="goal.description" class="mb-4 text-sm text-slate-600 dark:text-slate-400">
      {{ goal.description }}
    </div>

    <GoalProgress
      :progress="goal.progress_percentage"
      :current-amount="goal.current_amount"
      :target-amount="goal.target_amount"
      :is-completed="goal.is_completed"
      :goal-type="goal.goal_type"
      class="mb-4"
    />

    <div class="flex items-center justify-between text-sm pt-4 border-t border-slate-200 dark:border-slate-700">
      <div class="flex items-center gap-2 text-slate-600 dark:text-slate-400">
        <CalendarIcon class="w-4 h-4" />
        <span>
          <span v-if="isOverdue" class="text-red-600 font-medium">Vencida</span>
          <span v-else-if="goal.is_completed" class="text-emerald-600 font-medium">Completada</span>
          <span v-else>{{ daysRemaining }} días restantes</span>
        </span>
      </div>
      <div class="flex items-center gap-2">
        <button
          @click="$emit('edit', goal)"
          class="p-2 text-slate-600 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800 rounded transition-colors"
          title="Editar"
        >
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
          </svg>
        </button>
        <button
          @click="$emit('delete', goal)"
          class="p-2 text-red-600 hover:bg-red-50 dark:hover:bg-red-900/20 rounded transition-colors"
          title="Eliminar"
        >
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
          </svg>
        </button>
      </div>
    </div>
  </div>
</template>

