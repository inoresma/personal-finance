<script setup>
import { computed } from 'vue'
import CategoryIcon from './CategoryIcon.vue'
import { iconLabels } from '@/utils/iconMapping'

const props = defineProps({
  modelValue: {
    type: String,
    default: 'otros'
  }
})

const emit = defineEmits(['update:modelValue'])

const availableIcons = Object.keys(iconLabels).map(name => ({
  name,
  label: iconLabels[name]
}))

const selectedIcon = computed({
  get: () => props.modelValue || 'otros',
  set: (value) => emit('update:modelValue', value)
})

function selectIcon(iconName) {
  selectedIcon.value = iconName
}

const isNegativeIcon = (iconName) => {
  return iconName === 'dulces_golosinas' || iconName === 'snacks'
}
</script>

<template>
  <div class="space-y-3">
    <label class="label">Ícono</label>
    <div class="grid grid-cols-6 sm:grid-cols-9 gap-2 p-3 bg-slate-50 dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-800 max-h-64 overflow-y-auto">
      <button
        v-for="icon in availableIcons"
        :key="icon.name"
        type="button"
        @click="selectIcon(icon.name)"
        :class="[
          'relative p-2 rounded-lg border-2 transition-all hover:scale-105',
          selectedIcon === icon.name
            ? isNegativeIcon(icon.name)
              ? 'border-red-500 bg-red-50 dark:bg-red-900/30'
              : 'border-primary-500 bg-primary-50 dark:bg-primary-900/30'
            : 'border-slate-200 dark:border-slate-700 hover:border-slate-300 dark:hover:border-slate-600',
          isNegativeIcon(icon.name) && selectedIcon !== icon.name && 'hover:border-red-300 dark:hover:border-red-700'
        ]"
        :title="icon.label"
      >
        <CategoryIcon 
          :icon="icon.name" 
          class="w-5 h-5"
        />
        <div 
          v-if="selectedIcon === icon.name"
          :class="[
            'absolute -top-1 -right-1 w-4 h-4 rounded-full flex items-center justify-center text-xs',
            isNegativeIcon(icon.name)
              ? 'bg-red-500 text-white'
              : 'bg-primary-500 text-white'
          ]"
        >
          ✓
        </div>
      </button>
    </div>
    <p class="text-xs text-slate-500 dark:text-slate-400">
      Selecciona un ícono que represente tu categoría
    </p>
  </div>
</template>




