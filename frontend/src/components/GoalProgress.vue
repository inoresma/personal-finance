<script setup>
import { computed } from 'vue'

const props = defineProps({
  progress: {
    type: Number,
    default: 0
  },
  currentAmount: {
    type: [Number, String],
    default: 0
  },
  targetAmount: {
    type: [Number, String],
    default: 0
  },
  isCompleted: {
    type: Boolean,
    default: false
  },
  goalType: {
    type: String,
    default: 'savings'
  }
})

const progressPercentage = computed(() => {
  return Math.min(100, Math.max(0, props.progress))
})

const progressColor = computed(() => {
  if (props.isCompleted) return 'bg-emerald-500'
  if (progressPercentage.value >= 75) return 'bg-emerald-500'
  if (progressPercentage.value >= 50) return 'bg-amber-500'
  if (progressPercentage.value >= 25) return 'bg-yellow-500'
  return 'bg-red-500'
})
</script>

<template>
  <div class="space-y-2">
    <div class="flex items-center justify-between text-sm">
      <span class="text-slate-600 dark:text-slate-400">Progreso</span>
      <span class="font-semibold text-slate-900 dark:text-white">
        {{ progressPercentage.toFixed(1) }}%
      </span>
    </div>
    <div class="w-full bg-slate-200 dark:bg-slate-700 rounded-full h-3 overflow-hidden">
      <div
        :class="progressColor"
        class="h-full transition-all duration-500 ease-out rounded-full"
        :style="{ width: `${progressPercentage}%` }"
      />
    </div>
    <div class="flex items-center justify-between text-xs text-slate-500 dark:text-slate-400">
      <span>{{ currentAmount.toLocaleString('es-ES', { style: 'currency', currency: 'USD' }) }}</span>
      <span>{{ targetAmount.toLocaleString('es-ES', { style: 'currency', currency: 'USD' }) }}</span>
    </div>
  </div>
</template>

