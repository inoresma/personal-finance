<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { useNotificationsStore } from '@/stores/notifications'
import { useAuthStore } from '@/stores/auth'
import { useUiStore } from '@/stores/ui'
import {
  BellIcon,
  XMarkIcon,
  ExclamationTriangleIcon,
  ExclamationCircleIcon,
  CheckCircleIcon,
  ScaleIcon,
  ChartBarIcon,
} from '@heroicons/vue/24/outline'
import { BellAlertIcon } from '@heroicons/vue/24/solid'

const router = useRouter()
const notificationsStore = useNotificationsStore()
const authStore = useAuthStore()
const uiStore = useUiStore()

const isOpen = ref(false)

function togglePanel() {
  isOpen.value = !isOpen.value
}

function closePanel() {
  isOpen.value = false
}

function handleClickOutside(event) {
  const panel = document.getElementById('notification-panel')
  const button = document.getElementById('notification-button')
  
  if (panel && button && !panel.contains(event.target) && !button.contains(event.target)) {
    closePanel()
  }
}

function handleNotificationClick(alert) {
  notificationsStore.markAsRead(alert.id)
  
  if (alert.type === 'debt') {
    router.push('/debts')
  } else if (alert.type === 'budget') {
    router.push('/budgets')
  }
  
  closePanel()
}


function getSeverityIcon(severity) {
  switch (severity) {
    case 'danger': return ExclamationCircleIcon
    case 'warning': return ExclamationTriangleIcon
    default: return CheckCircleIcon
  }
}

function getSeverityColor(severity) {
  switch (severity) {
    case 'danger': return 'text-red-500 bg-red-100 dark:bg-red-900/30'
    case 'warning': return 'text-amber-500 bg-amber-100 dark:bg-amber-900/30'
    default: return 'text-emerald-500 bg-emerald-100 dark:bg-emerald-900/30'
  }
}

function getTypeIcon(type) {
  switch (type) {
    case 'debt': return ScaleIcon
    case 'budget': return ChartBarIcon
    default: return BellIcon
  }
}

onMounted(() => {
  document.addEventListener('click', handleClickOutside)
  notificationsStore.checkAlerts()
})

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
})
</script>

<template>
  <div class="relative">
    <!-- Notification Button -->
    <button
      id="notification-button"
      @click="togglePanel"
      class="relative p-2 rounded-lg hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors"
    >
      <BellAlertIcon 
        v-if="notificationsStore.alertCount > 0" 
        class="w-5 h-5 text-amber-500"
      />
      <BellIcon 
        v-else 
        class="w-5 h-5 text-slate-600 dark:text-slate-400"
      />
      
      <!-- Badge -->
      <span
        v-if="notificationsStore.alertCount > 0"
        class="absolute -top-1 -right-1 w-5 h-5 bg-red-500 text-white text-xs font-bold rounded-full flex items-center justify-center animate-pulse"
      >
        {{ notificationsStore.alertCount > 9 ? '9+' : notificationsStore.alertCount }}
      </span>
    </button>
    
    <!-- Notification Panel -->
    <Transition
      enter-active-class="transition duration-200 ease-out"
      enter-from-class="opacity-0 scale-95"
      enter-to-class="opacity-100 scale-100"
      leave-active-class="transition duration-150 ease-in"
      leave-from-class="opacity-100 scale-100"
      leave-to-class="opacity-0 scale-95"
    >
      <div
        v-if="isOpen"
        id="notification-panel"
        class="absolute left-1/2 -translate-x-1/2 sm:left-auto sm:translate-x-0 sm:right-0 mt-2 w-[calc(100vw-2rem)] sm:w-96 bg-white dark:bg-slate-900 rounded-2xl shadow-xl border border-slate-200 dark:border-slate-800 z-50 overflow-hidden max-h-[calc(100vh-6rem)] sm:max-h-[calc(100vh-5rem)]"
      >
        <!-- Header -->
        <div class="px-3 sm:px-4 py-2.5 sm:py-3 border-b border-slate-200 dark:border-slate-800">
          <div class="flex items-center justify-between mb-3">
            <h3 class="font-semibold text-sm sm:text-base text-slate-900 dark:text-white flex items-center gap-2">
              <BellIcon class="w-4 h-4 sm:w-5 sm:h-5" />
              Notificaciones
            </h3>
            <button
              @click="closePanel"
              class="p-1 rounded-lg hover:bg-slate-100 dark:hover:bg-slate-800"
            >
              <XMarkIcon class="w-4 h-4 sm:w-5 sm:h-5 text-slate-400" />
            </button>
          </div>
          
          <!-- Filter Buttons -->
          <div class="flex gap-2">
            <button
              @click="notificationsStore.setFilter('unread')"
              :class="[
                'flex-1 px-3 py-1.5 text-xs sm:text-sm rounded-lg font-medium transition-colors',
                notificationsStore.filterType === 'unread'
                  ? 'bg-primary-600 text-white'
                  : 'bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-400 hover:bg-slate-200 dark:hover:bg-slate-700'
              ]"
            >
              No leídas
              <span v-if="notificationsStore.unreadAlerts.length > 0" class="ml-1.5 px-1.5 py-0.5 rounded-full bg-white/20 text-xs">
                {{ notificationsStore.unreadAlerts.length }}
              </span>
            </button>
            <button
              @click="notificationsStore.setFilter('read')"
              :class="[
                'flex-1 px-3 py-1.5 text-xs sm:text-sm rounded-lg font-medium transition-colors',
                notificationsStore.filterType === 'read'
                  ? 'bg-primary-600 text-white'
                  : 'bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-400 hover:bg-slate-200 dark:hover:bg-slate-700'
              ]"
            >
              Leídas
              <span v-if="notificationsStore.readAlerts.length > 0" class="ml-1.5 px-1.5 py-0.5 rounded-full bg-white/20 text-xs">
                {{ notificationsStore.readAlerts.length }}
              </span>
            </button>
          </div>
        </div>
        
        <!-- Content -->
        <div class="max-h-96 overflow-y-auto">
          <!-- Loading -->
          <div v-if="notificationsStore.loading" class="p-6 text-center">
            <div class="animate-spin w-6 h-6 border-2 border-primary-500 border-t-transparent rounded-full mx-auto"></div>
            <p class="text-sm text-slate-500 mt-2">Verificando alertas...</p>
          </div>
          
          <!-- Empty State -->
          <div v-else-if="notificationsStore.pendingAlerts.length === 0" class="p-8 text-center">
            <div class="w-16 h-16 rounded-full bg-emerald-100 dark:bg-emerald-900/30 flex items-center justify-center mx-auto mb-4">
              <CheckCircleIcon class="w-8 h-8 text-emerald-500" />
            </div>
            <p class="font-medium text-slate-900 dark:text-white">
              {{ notificationsStore.filterType === 'read' ? 'No hay notificaciones leídas' : '¡Todo en orden!' }}
            </p>
            <p class="text-sm text-slate-500 mt-1">
              {{ notificationsStore.filterType === 'read' ? 'Aún no has leído ninguna notificación' : 'No tienes alertas pendientes' }}
            </p>
          </div>
          
          <!-- Alerts List -->
          <div v-else class="divide-y divide-slate-100 dark:divide-slate-800">
            <div
              v-for="alert in notificationsStore.pendingAlerts"
              :key="alert.id"
              @click="handleNotificationClick(alert)"
              class="p-3 sm:p-4 hover:bg-slate-50 dark:hover:bg-slate-800/50 transition-colors cursor-pointer"
            >
              <div class="flex gap-3">
                <!-- Icon -->
                <div :class="[getSeverityColor(alert.severity), 'w-10 h-10 sm:w-12 sm:h-12 rounded-xl flex items-center justify-center flex-shrink-0']">
                  <component :is="getSeverityIcon(alert.severity)" class="w-5 h-5 sm:w-6 sm:h-6" />
                </div>
                
                <!-- Content -->
                <div class="flex-1 min-w-0">
                  <div class="flex flex-col sm:flex-row sm:items-start sm:justify-between gap-2">
                    <div class="flex-1 min-w-0">
                      <p class="font-medium text-sm sm:text-base text-slate-900 dark:text-white break-words">
                        {{ alert.title }}
                      </p>
                      <p class="text-xs sm:text-sm text-slate-500 dark:text-slate-400 mt-0.5 break-words">
                        {{ alert.message }}
                      </p>
                    </div>
                    <span 
                      class="flex-shrink-0 px-2 py-0.5 text-xs rounded-full self-start sm:self-auto"
                      :class="alert.type === 'debt' ? 'bg-blue-100 text-blue-600 dark:bg-blue-900/30 dark:text-blue-400' : 'bg-violet-100 text-violet-600 dark:bg-violet-900/30 dark:text-violet-400'"
                    >
                      {{ alert.type === 'debt' ? 'Deuda' : 'Presupuesto' }}
                    </span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
        
        <!-- Footer -->
        <div class="px-3 sm:px-4 py-2.5 sm:py-3 border-t border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-slate-800/50">
          <router-link
            to="/profile"
            @click="closePanel"
            class="text-xs sm:text-sm text-primary-600 dark:text-primary-400 hover:underline flex items-center justify-center gap-1"
          >
            Configurar notificaciones
          </router-link>
        </div>
      </div>
    </Transition>
  </div>
</template>

