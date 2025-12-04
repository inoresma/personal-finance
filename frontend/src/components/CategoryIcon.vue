<script setup>
import { computed } from 'vue'
import { getIconComponent } from '@/utils/iconMapping'

const props = defineProps({
  icon: {
    type: String,
    default: 'otros'
  },
  class: {
    type: String,
    default: ''
  }
})

const iconName = computed(() => props.icon || 'otros')
const isNegativeIcon = computed(() => {
  return iconName.value === 'dulces_golosinas' || iconName.value === 'snacks'
})

const IconComponent = computed(() => getIconComponent(iconName.value))
</script>

<template>
  <component
    :is="IconComponent"
    :class="[
      'inline-flex items-center justify-center',
      isNegativeIcon && 'text-red-500 dark:text-red-400',
      props.class || 'w-6 h-6'
    ]"
  />
</template>

