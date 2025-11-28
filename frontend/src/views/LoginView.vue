<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useUiStore } from '@/stores/ui'
import { EnvelopeIcon, LockClosedIcon, EyeIcon, EyeSlashIcon } from '@heroicons/vue/24/outline'

const router = useRouter()
const authStore = useAuthStore()
const uiStore = useUiStore()

const email = ref('')
const password = ref('')
const showPassword = ref(false)
const loading = ref(false)
const error = ref('')
const rememberMe = ref(false)

const REMEMBERED_EMAIL_KEY = 'remembered_email'

onMounted(() => {
  const rememberedEmail = localStorage.getItem(REMEMBERED_EMAIL_KEY)
  if (rememberedEmail) {
    email.value = rememberedEmail
    rememberMe.value = true
  }
})

function handleRememberMeChange() {
  if (rememberMe.value) {
    localStorage.setItem(REMEMBERED_EMAIL_KEY, email.value)
  } else {
    localStorage.removeItem(REMEMBERED_EMAIL_KEY)
  }
}

async function handleSubmit() {
  if (!email.value || !password.value) {
    error.value = 'Por favor completa todos los campos'
    return
  }
  
  if (rememberMe.value) {
    localStorage.setItem(REMEMBERED_EMAIL_KEY, email.value)
  } else {
    localStorage.removeItem(REMEMBERED_EMAIL_KEY)
  }
  
  loading.value = true
  error.value = ''
  
  try {
    await authStore.login(email.value, password.value)
    uiStore.showSuccess('¡Bienvenido!')
  } catch (err) {
    error.value = err.response?.data?.detail || 'Credenciales inválidas'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="min-h-screen flex">
    <!-- Left side - Form -->
    <div class="flex-1 flex items-center justify-center p-8">
      <div class="w-full max-w-md">
        <div class="text-center mb-8">
          <div class="w-16 h-16 mx-auto mb-4 rounded-2xl bg-gradient-to-br from-primary-500 to-primary-600 flex items-center justify-center">
            <svg class="w-9 h-9 text-white" fill="currentColor" viewBox="0 0 24 24">
              <path d="M12 7.5a2.25 2.25 0 100 4.5 2.25 2.25 0 000-4.5z" />
              <path fill-rule="evenodd" d="M1.5 4.875C1.5 3.839 2.34 3 3.375 3h17.25c1.035 0 1.875.84 1.875 1.875v9.75c0 1.036-.84 1.875-1.875 1.875H3.375A1.875 1.875 0 011.5 14.625v-9.75zM8.25 9.75a3.75 3.75 0 117.5 0 3.75 3.75 0 01-7.5 0zM18.75 9a.75.75 0 00-.75.75v.008c0 .414.336.75.75.75h.008a.75.75 0 00.75-.75V9.75a.75.75 0 00-.75-.75h-.008zM4.5 9.75A.75.75 0 015.25 9h.008a.75.75 0 01.75.75v.008a.75.75 0 01-.75.75H5.25a.75.75 0 01-.75-.75V9.75z" clip-rule="evenodd" />
            </svg>
          </div>
          <h1 class="font-display text-3xl font-bold text-slate-900 dark:text-white">Bienvenido</h1>
          <p class="mt-2 text-slate-600 dark:text-slate-400">Inicia sesión para gestionar tus finanzas</p>
        </div>
        
        <form @submit.prevent="handleSubmit" class="space-y-5">
          <div v-if="error" class="p-4 rounded-xl bg-red-50 dark:bg-red-900/20 text-red-600 dark:text-red-400 text-sm">
            {{ error }}
          </div>
          
          <div>
            <label class="label">Correo electrónico</label>
            <div class="relative">
              <EnvelopeIcon class="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400" />
              <input
                v-model="email"
                type="email"
                placeholder="tu@email.com"
                class="input pl-12"
                autocomplete="email"
              />
            </div>
          </div>
          
          <div>
            <label class="label">Contraseña</label>
            <div class="relative">
              <LockClosedIcon class="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400" />
              <input
                v-model="password"
                :type="showPassword ? 'text' : 'password'"
                placeholder="••••••••"
                class="input pl-12 pr-12"
                autocomplete="current-password"
              />
              <button
                type="button"
                @click="showPassword = !showPassword"
                class="absolute right-4 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600"
              >
                <EyeSlashIcon v-if="showPassword" class="w-5 h-5" />
                <EyeIcon v-else class="w-5 h-5" />
              </button>
            </div>
          </div>
          
          <div class="flex items-center">
            <input
              id="remember-me"
              v-model="rememberMe"
              type="checkbox"
              @change="handleRememberMeChange"
              class="w-4 h-4 text-primary-600 bg-slate-100 border-slate-300 rounded focus:ring-primary-500 focus:ring-2 dark:bg-slate-700 dark:border-slate-600"
            />
            <label for="remember-me" class="ml-2 text-sm text-slate-600 dark:text-slate-400">
              Mantener sesión iniciada
            </label>
          </div>
          
          <button
            type="submit"
            :disabled="loading"
            class="btn-primary w-full py-3.5"
          >
            <span v-if="loading">Iniciando sesión...</span>
            <span v-else>Iniciar sesión</span>
          </button>
        </form>
        
        <p class="mt-8 text-center text-slate-600 dark:text-slate-400">
          ¿No tienes cuenta?
          <router-link to="/register" class="text-primary-600 dark:text-primary-400 font-medium hover:underline">
            Regístrate
          </router-link>
        </p>
      </div>
    </div>
    
    <!-- Right side - Decorative -->
    <div class="hidden lg:flex flex-1 bg-gradient-to-br from-primary-600 via-primary-700 to-indigo-800 relative overflow-hidden">
      <div class="absolute inset-0 bg-[url('data:image/svg+xml,%3Csvg%20width%3D%2260%22%20height%3D%2260%22%20viewBox%3D%220%200%2060%2060%22%20xmlns%3D%22http%3A%2F%2Fwww.w3.org%2F2000%2Fsvg%22%3E%3Cg%20fill%3D%22none%22%20fill-rule%3D%22evenodd%22%3E%3Cg%20fill%3D%22%23ffffff%22%20fill-opacity%3D%220.05%22%3E%3Cpath%20d%3D%22M36%2034v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6%2034v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6%204V0H4v4H0v2h4v4h2V6h4V4H6z%22%2F%3E%3C%2Fg%3E%3C%2Fg%3E%3C%2Fsvg%3E')] opacity-50" />
      
      <div class="relative z-10 flex items-center justify-center w-full p-12">
        <div class="text-center text-white">
          <h2 class="font-display text-4xl font-bold mb-4">Toma el control de tu dinero</h2>
          <p class="text-xl text-primary-100 max-w-md mx-auto">
            Gestiona tus ingresos, gastos, inversiones y deudas en un solo lugar.
          </p>
          
          <div class="mt-12 grid grid-cols-2 gap-6 max-w-sm mx-auto">
            <div class="bg-white/10 backdrop-blur-sm rounded-2xl p-6">
              <div class="text-3xl font-bold mb-1">📊</div>
              <div class="text-primary-200 text-sm">Reportes</div>
            </div>
            <div class="bg-white/10 backdrop-blur-sm rounded-2xl p-6">
              <div class="text-3xl font-bold mb-1">💰</div>
              <div class="text-primary-200 text-sm">Presupuestos</div>
            </div>
            <div class="bg-white/10 backdrop-blur-sm rounded-2xl p-6">
              <div class="text-3xl font-bold mb-1">📈</div>
              <div class="text-primary-200 text-sm">Inversiones</div>
            </div>
            <div class="bg-white/10 backdrop-blur-sm rounded-2xl p-6">
              <div class="text-3xl font-bold mb-1">∞</div>
              <div class="text-primary-200 text-sm">Transacciones</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>






