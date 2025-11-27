<script setup>
import { XMarkIcon } from '@heroicons/vue/24/outline'

const props = defineProps({
  title: String,
  size: {
    type: String,
    default: 'md'
  }
})

const emit = defineEmits(['close'])

const sizeClasses = {
  sm: 'max-w-md',
  md: 'max-w-lg',
  lg: 'max-w-2xl',
  xl: 'max-w-4xl',
}
</script>

<template>
  <Teleport to="body">
    <div class="fixed inset-0 z-50 overflow-y-auto">
      <!-- Backdrop -->
      <div 
        class="fixed inset-0 bg-slate-900/60 backdrop-blur-sm"
        @click="emit('close')"
      />
      
      <!-- Modal -->
      <div class="flex min-h-full items-center justify-center p-4">
        <div 
          :class="sizeClasses[size]"
          class="relative w-full bg-white dark:bg-slate-900 rounded-2xl shadow-xl animate-scale-in"
        >
          <!-- Header -->
          <div class="flex items-center justify-between px-6 py-4 border-b border-slate-200 dark:border-slate-800">
            <h3 class="font-display text-lg font-semibold text-slate-900 dark:text-white">
              {{ title }}
            </h3>
            <button
              @click="emit('close')"
              class="p-2 rounded-lg hover:bg-slate-100 dark:hover:bg-slate-800 text-slate-500 transition-colors"
            >
              <XMarkIcon class="w-5 h-5" />
            </button>
          </div>
          
          <!-- Content -->
          <div class="px-6 py-4">
            <slot />
          </div>
          
          <!-- Footer -->
          <div v-if="$slots.footer" class="px-6 py-4 border-t border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-slate-800/50 rounded-b-2xl">
            <slot name="footer" />
          </div>
        </div>
      </div>
    </div>
  </Teleport>
</template>





