<script setup>
import { useUiStore } from '@/stores/ui'
import { 
  CheckCircleIcon, 
  ExclamationCircleIcon, 
  ExclamationTriangleIcon,
  InformationCircleIcon,
  XMarkIcon 
} from '@heroicons/vue/24/outline'

const uiStore = useUiStore()

function getIcon(type) {
  switch (type) {
    case 'success': return CheckCircleIcon
    case 'error': return ExclamationCircleIcon
    case 'warning': return ExclamationTriangleIcon
    default: return InformationCircleIcon
  }
}

function getClasses(type) {
  switch (type) {
    case 'success': 
      return 'bg-emerald-50 dark:bg-emerald-900/90 text-emerald-800 dark:text-emerald-100 border-emerald-200 dark:border-emerald-800'
    case 'error': 
      return 'bg-red-50 dark:bg-red-900/90 text-red-800 dark:text-red-100 border-red-200 dark:border-red-800'
    case 'warning': 
      return 'bg-amber-50 dark:bg-amber-900/90 text-amber-800 dark:text-amber-100 border-amber-200 dark:border-amber-800'
    default: 
      return 'bg-blue-50 dark:bg-blue-900/90 text-blue-800 dark:text-blue-100 border-blue-200 dark:border-blue-800'
  }
}

function getIconClass(type) {
  switch (type) {
    case 'success': return 'text-emerald-500'
    case 'error': return 'text-red-500'
    case 'warning': return 'text-amber-500'
    default: return 'text-blue-500'
  }
}
</script>

<template>
  <Teleport to="body">
    <div class="fixed bottom-4 right-4 z-50 space-y-2">
      <TransitionGroup name="toast">
        <div
          v-for="toast in uiStore.toasts"
          :key="toast.id"
          :class="getClasses(toast.type)"
          class="flex items-center gap-3 px-4 py-3 rounded-xl border shadow-lg max-w-sm animate-slide-up"
        >
          <component 
            :is="getIcon(toast.type)" 
            :class="getIconClass(toast.type)"
            class="w-5 h-5 flex-shrink-0" 
          />
          <p class="flex-1 text-sm font-medium">{{ toast.message }}</p>
          <button 
            @click="uiStore.removeToast(toast.id)"
            class="p-1 rounded-lg hover:bg-black/5 dark:hover:bg-white/10 transition-colors"
          >
            <XMarkIcon class="w-4 h-4" />
          </button>
        </div>
      </TransitionGroup>
    </div>
  </Teleport>
</template>

<style scoped>
.toast-enter-active,
.toast-leave-active {
  transition: all 0.3s ease;
}

.toast-enter-from {
  opacity: 0;
  transform: translateX(100%);
}

.toast-leave-to {
  opacity: 0;
  transform: translateX(100%);
}
</style>

















