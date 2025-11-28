<script setup>
import { computed } from 'vue'

const props = defineProps({
  title: String,
  value: [String, Number],
  icon: [Object, Function],
  color: {
    type: String,
    default: 'primary'
  },
  trend: {
    type: Number,
    default: null
  }
})

const colorClasses = computed(() => {
  const colors = {
    primary: 'bg-primary-100 dark:bg-primary-900/30 text-primary-600 dark:text-primary-400',
    success: 'bg-emerald-100 dark:bg-emerald-900/30 text-emerald-600 dark:text-emerald-400',
    danger: 'bg-red-100 dark:bg-red-900/30 text-red-600 dark:text-red-400',
    warning: 'bg-amber-100 dark:bg-amber-900/30 text-amber-600 dark:text-amber-400',
  }
  return colors[props.color] || colors.primary
})
</script>

<template>
  <div class="card p-6 hover:shadow-md transition-shadow">
    <div class="flex items-start justify-between">
      <div>
        <p class="text-sm font-medium text-slate-500 dark:text-slate-400">{{ title }}</p>
        <p class="mt-2 text-2xl font-bold text-slate-900 dark:text-white">{{ value }}</p>
        <div v-if="trend !== null" class="mt-2 flex items-center gap-1">
          <span 
            :class="trend >= 0 ? 'text-emerald-600' : 'text-red-600'"
            class="text-sm font-medium"
          >
            {{ trend >= 0 ? '+' : '' }}{{ trend }}%
          </span>
          <span class="text-xs text-slate-400">vs mes anterior</span>
        </div>
      </div>
      <div 
        :class="colorClasses"
        class="w-12 h-12 rounded-xl flex items-center justify-center"
      >
        <component :is="icon" class="w-6 h-6" />
      </div>
    </div>
  </div>
</template>







