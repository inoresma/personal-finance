<script setup>
import { ref, computed } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useUiStore } from '@/stores/ui'
import { 
  EnvelopeIcon, 
  LockClosedIcon, 
  UserIcon,
  EyeIcon, 
  EyeSlashIcon 
} from '@heroicons/vue/24/outline'

const authStore = useAuthStore()
const uiStore = useUiStore()

const form = ref({
  email: '',
  username: '',
  first_name: '',
  last_name: '',
  password: '',
  password_confirm: '',
})

const showPassword = ref(false)
const loading = ref(false)
const errors = ref({})

const isFormValid = computed(() => {
  return form.value.email && 
         form.value.username && 
         form.value.password && 
         form.value.password === form.value.password_confirm
})

async function handleSubmit() {
  errors.value = {}
  
  if (form.value.password !== form.value.password_confirm) {
    errors.value.password_confirm = 'Las contraseñas no coinciden'
    return
  }
  
  if (form.value.password.length < 8) {
    errors.value.password = 'La contraseña debe tener al menos 8 caracteres'
    return
  }
  
  loading.value = true
  
  try {
    await authStore.register(form.value)
    uiStore.showSuccess('¡Cuenta creada exitosamente!')
  } catch (err) {
    if (err.response?.data) {
      errors.value = err.response.data
    }
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="min-h-screen flex">
    <!-- Left side - Decorative -->
    <div class="hidden lg:flex flex-1 bg-gradient-to-br from-emerald-600 via-teal-700 to-cyan-800 relative overflow-hidden">
      <div class="absolute inset-0 bg-[url('data:image/svg+xml,%3Csvg%20width%3D%2260%22%20height%3D%2260%22%20viewBox%3D%220%200%2060%2060%22%20xmlns%3D%22http%3A%2F%2Fwww.w3.org%2F2000%2Fsvg%22%3E%3Cg%20fill%3D%22none%22%20fill-rule%3D%22evenodd%22%3E%3Cg%20fill%3D%22%23ffffff%22%20fill-opacity%3D%220.05%22%3E%3Cpath%20d%3D%22M36%2034v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6%2034v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6%204V0H4v4H0v2h4v4h2V6h4V4H6z%22%2F%3E%3C%2Fg%3E%3C%2Fg%3E%3C%2Fsvg%3E')] opacity-50" />
      
      <div class="relative z-10 flex items-center justify-center w-full p-12">
        <div class="text-center text-white">
          <h2 class="font-display text-4xl font-bold mb-4">Comienza tu viaje financiero</h2>
          <p class="text-xl text-emerald-100 max-w-md mx-auto">
            Crea tu cuenta gratuita y empieza a organizar tus finanzas hoy mismo.
          </p>
          
          <div class="mt-12 space-y-4 max-w-sm mx-auto text-left">
            <div class="flex items-center gap-3 bg-white/10 backdrop-blur-sm rounded-xl p-4">
              <div class="w-10 h-10 rounded-full bg-emerald-500 flex items-center justify-center">✓</div>
              <span>Múltiples cuentas y monedas</span>
            </div>
            <div class="flex items-center gap-3 bg-white/10 backdrop-blur-sm rounded-xl p-4">
              <div class="w-10 h-10 rounded-full bg-emerald-500 flex items-center justify-center">✓</div>
              <span>Presupuestos inteligentes</span>
            </div>
            <div class="flex items-center gap-3 bg-white/10 backdrop-blur-sm rounded-xl p-4">
              <div class="w-10 h-10 rounded-full bg-emerald-500 flex items-center justify-center">✓</div>
              <span>Reportes y gráficos detallados</span>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Right side - Form -->
    <div class="flex-1 flex items-center justify-center p-8">
      <div class="w-full max-w-md">
        <div class="text-center mb-8">
          <h1 class="font-display text-3xl font-bold text-slate-900 dark:text-white">Crear cuenta</h1>
          <p class="mt-2 text-slate-600 dark:text-slate-400">Registra tus datos para comenzar</p>
        </div>
        
        <form @submit.prevent="handleSubmit" class="space-y-4">
          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="label">Nombre</label>
              <input
                v-model="form.first_name"
                type="text"
                placeholder="Juan"
                class="input"
              />
            </div>
            <div>
              <label class="label">Apellido</label>
              <input
                v-model="form.last_name"
                type="text"
                placeholder="Pérez"
                class="input"
              />
            </div>
          </div>
          
          <div>
            <label class="label">Nombre de usuario</label>
            <div class="relative">
              <UserIcon class="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400" />
              <input
                v-model="form.username"
                type="text"
                placeholder="juanperez"
                class="input pl-12"
              />
            </div>
            <p v-if="errors.username" class="mt-1 text-sm text-red-500">{{ errors.username[0] }}</p>
          </div>
          
          <div>
            <label class="label">Correo electrónico</label>
            <div class="relative">
              <EnvelopeIcon class="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400" />
              <input
                v-model="form.email"
                type="email"
                placeholder="tu@email.com"
                class="input pl-12"
              />
            </div>
            <p v-if="errors.email" class="mt-1 text-sm text-red-500">{{ errors.email[0] }}</p>
          </div>
          
          <div>
            <label class="label">Contraseña</label>
            <div class="relative">
              <LockClosedIcon class="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400" />
              <input
                v-model="form.password"
                :type="showPassword ? 'text' : 'password'"
                placeholder="Mínimo 8 caracteres"
                class="input pl-12 pr-12"
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
            <p v-if="errors.password" class="mt-1 text-sm text-red-500">{{ errors.password }}</p>
          </div>
          
          <div>
            <label class="label">Confirmar contraseña</label>
            <div class="relative">
              <LockClosedIcon class="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400" />
              <input
                v-model="form.password_confirm"
                :type="showPassword ? 'text' : 'password'"
                placeholder="Repite tu contraseña"
                class="input pl-12"
              />
            </div>
            <p v-if="errors.password_confirm" class="mt-1 text-sm text-red-500">{{ errors.password_confirm }}</p>
          </div>
          
          <button
            type="submit"
            :disabled="loading || !isFormValid"
            class="btn-primary w-full py-3.5 mt-6"
          >
            <span v-if="loading">Creando cuenta...</span>
            <span v-else>Crear cuenta</span>
          </button>
        </form>
        
        <p class="mt-8 text-center text-slate-600 dark:text-slate-400">
          ¿Ya tienes cuenta?
          <router-link to="/login" class="text-primary-600 dark:text-primary-400 font-medium hover:underline">
            Inicia sesión
          </router-link>
        </p>
      </div>
    </div>
  </div>
</template>

















