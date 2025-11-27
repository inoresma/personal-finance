<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useUiStore } from '@/stores/ui'
import {
  HomeIcon,
  CreditCardIcon,
  BanknotesIcon,
  TagIcon,
  ChartBarIcon,
  ArrowPathIcon,
  PresentationChartLineIcon,
  ScaleIcon,
  UserIcon,
  ArrowRightOnRectangleIcon,
  Bars3Icon,
  XMarkIcon,
  MoonIcon,
  SunIcon,
  PlusIcon,
} from '@heroicons/vue/24/outline'
import TransactionModal from '@/components/TransactionModal.vue'
import NotificationCenter from '@/components/NotificationCenter.vue'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()
const uiStore = useUiStore()

const showTransactionModal = ref(false)

const navigation = [
  { name: 'Dashboard', href: '/dashboard', icon: HomeIcon },
  { name: 'Transacciones', href: '/transactions', icon: BanknotesIcon },
  { name: 'Cuentas', href: '/accounts', icon: CreditCardIcon },
  { name: 'Categorías', href: '/categories', icon: TagIcon },
  { name: 'Presupuestos', href: '/budgets', icon: ChartBarIcon },
  { name: 'Inversiones', href: '/investments', icon: PresentationChartLineIcon },
  { name: 'Deudas', href: '/debts', icon: ScaleIcon },
  { name: 'Recurrentes', href: '/recurring', icon: ArrowPathIcon },
  { name: 'Reportes', href: '/reports', icon: ChartBarIcon },
]

const currentRoute = computed(() => route.path)

function isActive(href) {
  return currentRoute.value === href
}

function handleLogout() {
  authStore.logout()
}

function handleResize() {
  if (window.innerWidth >= 1024) {
    uiStore.closeSidebar()
  }
}

onMounted(() => {
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
})
</script>

<template>
  <div class="min-h-screen bg-slate-50 dark:bg-slate-950">
    <!-- Mobile sidebar backdrop -->
    <div 
      v-if="uiStore.sidebarOpen"
      class="fixed inset-0 bg-slate-900/50 z-40 lg:hidden"
      @click="uiStore.closeSidebar"
    />
    
    <!-- Sidebar -->
    <aside 
      :class="[
        'fixed top-0 left-0 z-50 h-full w-72 bg-white dark:bg-slate-900 border-r border-slate-200 dark:border-slate-800 transform transition-transform duration-300 lg:translate-x-0',
        uiStore.sidebarOpen ? 'translate-x-0' : '-translate-x-full'
      ]"
    >
      <div class="flex flex-col h-full">
        <!-- Logo -->
        <div class="flex items-center gap-3 px-6 py-5 border-b border-slate-200 dark:border-slate-800">
          <div class="w-10 h-10 rounded-xl bg-gradient-to-br from-primary-500 to-primary-600 flex items-center justify-center">
            <BanknotesIcon class="w-6 h-6 text-white" />
          </div>
          <div>
            <h1 class="font-display font-bold text-lg text-slate-900 dark:text-white">Finanzas</h1>
            <p class="text-xs text-slate-500 dark:text-slate-400">Control total</p>
          </div>
          <button 
            @click="uiStore.closeSidebar"
            class="ml-auto lg:hidden p-2 rounded-lg hover:bg-slate-100 dark:hover:bg-slate-800"
          >
            <XMarkIcon class="w-5 h-5" />
          </button>
        </div>
        
        <!-- Navigation -->
        <nav class="flex-1 px-4 py-4 space-y-1 overflow-y-auto">
          <router-link
            v-for="item in navigation"
            :key="item.name"
            :to="item.href"
            :class="['sidebar-link', isActive(item.href) && 'active']"
            @click="uiStore.closeSidebar"
          >
            <component :is="item.icon" class="w-5 h-5" />
            <span>{{ item.name }}</span>
          </router-link>
        </nav>
        
        <!-- User section -->
        <div class="p-4 border-t border-slate-200 dark:border-slate-800">
          <router-link 
            to="/profile"
            class="flex items-center gap-3 p-3 rounded-xl hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors"
            @click="uiStore.closeSidebar"
          >
            <div class="w-10 h-10 rounded-full bg-slate-200 dark:bg-slate-700 flex items-center justify-center">
              <UserIcon class="w-5 h-5 text-slate-600 dark:text-slate-300" />
            </div>
            <div class="flex-1 min-w-0">
              <p class="font-medium text-sm text-slate-900 dark:text-white truncate">
                {{ authStore.user?.first_name || authStore.user?.email }}
              </p>
              <p class="text-xs text-slate-500 dark:text-slate-400 truncate">
                {{ authStore.user?.email }}
              </p>
            </div>
          </router-link>
          
          <button
            @click="handleLogout"
            class="w-full mt-2 flex items-center gap-3 px-4 py-3 rounded-xl text-red-600 dark:text-red-400 hover:bg-red-50 dark:hover:bg-red-900/20 transition-colors"
          >
            <ArrowRightOnRectangleIcon class="w-5 h-5" />
            <span>Cerrar sesión</span>
          </button>
        </div>
      </div>
    </aside>
    
    <!-- Main content -->
    <div class="lg:pl-72">
      <!-- Top bar -->
      <header class="sticky top-0 z-30 bg-white/80 dark:bg-slate-900/80 backdrop-blur-xl border-b border-slate-200 dark:border-slate-800">
        <div class="flex items-center justify-between px-4 lg:px-8 py-4">
          <button
            @click="uiStore.toggleSidebar"
            class="lg:hidden p-2 rounded-lg hover:bg-slate-100 dark:hover:bg-slate-800"
          >
            <Bars3Icon class="w-6 h-6" />
          </button>
          
          <div class="flex-1 lg:flex-none" />
          
          <div class="flex items-center gap-3">
            <NotificationCenter />
            
            <button
              @click="uiStore.toggleDarkMode"
              class="p-2 rounded-lg hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors"
            >
              <SunIcon v-if="uiStore.darkMode" class="w-5 h-5" />
              <MoonIcon v-else class="w-5 h-5" />
            </button>
            
            <button
              @click="showTransactionModal = true"
              class="btn-primary"
            >
              <PlusIcon class="w-5 h-5" />
              <span class="hidden sm:inline">Nueva transacción</span>
            </button>
          </div>
        </div>
      </header>
      
      <!-- Page content -->
      <main class="p-4 lg:p-8">
        <router-view />
      </main>
    </div>
    
    <!-- FAB for mobile -->
    <button
      @click="showTransactionModal = true"
      class="fixed bottom-6 right-6 lg:hidden w-14 h-14 bg-primary-600 text-white rounded-full shadow-lg shadow-primary-500/30 hover:bg-primary-700 flex items-center justify-center transition-all hover:scale-105"
    >
      <PlusIcon class="w-7 h-7" />
    </button>
    
    <!-- Transaction Modal -->
    <TransactionModal 
      v-if="showTransactionModal"
      @close="showTransactionModal = false"
    />
  </div>
</template>




