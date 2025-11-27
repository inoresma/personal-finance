<script setup>
import { ref, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useUiStore } from '@/stores/ui'
import { useNotificationsStore } from '@/stores/notifications'
import { UserIcon, KeyIcon, CogIcon, BellIcon, EnvelopeIcon } from '@heroicons/vue/24/outline'

const authStore = useAuthStore()
const uiStore = useUiStore()
const notificationsStore = useNotificationsStore()

const activeTab = ref('profile')
const loading = ref(false)

const notificationForm = ref({
  emailNotifications: true,
  debtReminders: true,
  debtDaysBefore: 7,
  budgetAlerts: true,
  budgetThreshold: 80,
  monthlySummary: true,
})

const profileForm = ref({
  first_name: '',
  last_name: '',
  email: '',
  preferred_currency: 'CLP',
})

const passwordForm = ref({
  old_password: '',
  new_password: '',
  confirm_password: '',
})

const currencies = [
  { value: 'CLP', label: 'Peso Chileno ($)' },
  { value: 'USD', label: 'Dólar (US$)' },
]

async function updateProfile() {
  loading.value = true
  try {
    await authStore.updateProfile({
      first_name: profileForm.value.first_name,
      last_name: profileForm.value.last_name,
      preferred_currency: profileForm.value.preferred_currency,
    })
    uiStore.showSuccess('Perfil actualizado')
  } catch (error) {
    uiStore.showError('Error al actualizar')
  } finally {
    loading.value = false
  }
}

async function changePassword() {
  if (passwordForm.value.new_password !== passwordForm.value.confirm_password) {
    uiStore.showError('Las contraseñas no coinciden')
    return
  }
  
  if (passwordForm.value.new_password.length < 8) {
    uiStore.showError('La contraseña debe tener al menos 8 caracteres')
    return
  }
  
  loading.value = true
  try {
    await authStore.changePassword(
      passwordForm.value.old_password,
      passwordForm.value.new_password
    )
    uiStore.showSuccess('Contraseña actualizada')
    passwordForm.value = { old_password: '', new_password: '', confirm_password: '' }
  } catch (error) {
    uiStore.showError(error.response?.data?.old_password?.[0] || 'Error al cambiar contraseña')
  } finally {
    loading.value = false
  }
}

function saveNotificationPreferences() {
  notificationsStore.updatePreferences(notificationForm.value)
  uiStore.showSuccess('Preferencias de notificación guardadas')
}

onMounted(() => {
  if (authStore.user) {
    profileForm.value = {
      first_name: authStore.user.first_name || '',
      last_name: authStore.user.last_name || '',
      email: authStore.user.email || '',
      preferred_currency: authStore.user.preferred_currency || 'CLP',
    }
  }
  
  notificationForm.value = { ...notificationsStore.preferences }
})
</script>

<template>
  <div class="space-y-6 animate-fade-in">
    <!-- Header -->
    <div>
      <h1 class="font-display text-2xl lg:text-3xl font-bold text-slate-900 dark:text-white">
        Mi Perfil
      </h1>
      <p class="mt-1 text-slate-600 dark:text-slate-400">
        Administra tu cuenta y preferencias
      </p>
    </div>
    
    <div class="grid grid-cols-1 lg:grid-cols-4 gap-6">
      <!-- Sidebar -->
      <div class="lg:col-span-1">
        <div class="card p-4 space-y-1">
          <button
            @click="activeTab = 'profile'"
            :class="[
              'w-full flex items-center gap-3 px-4 py-3 rounded-xl transition-colors',
              activeTab === 'profile' 
                ? 'bg-primary-50 dark:bg-primary-900/30 text-primary-600' 
                : 'hover:bg-slate-100 dark:hover:bg-slate-800 text-slate-600'
            ]"
          >
            <UserIcon class="w-5 h-5" />
            Información personal
          </button>
          <button
            @click="activeTab = 'password'"
            :class="[
              'w-full flex items-center gap-3 px-4 py-3 rounded-xl transition-colors',
              activeTab === 'password' 
                ? 'bg-primary-50 dark:bg-primary-900/30 text-primary-600' 
                : 'hover:bg-slate-100 dark:hover:bg-slate-800 text-slate-600'
            ]"
          >
            <KeyIcon class="w-5 h-5" />
            Contraseña
          </button>
          <button
            @click="activeTab = 'preferences'"
            :class="[
              'w-full flex items-center gap-3 px-4 py-3 rounded-xl transition-colors',
              activeTab === 'preferences' 
                ? 'bg-primary-50 dark:bg-primary-900/30 text-primary-600' 
                : 'hover:bg-slate-100 dark:hover:bg-slate-800 text-slate-600'
            ]"
          >
            <CogIcon class="w-5 h-5" />
            Preferencias
          </button>
          <button
            @click="activeTab = 'notifications'"
            :class="[
              'w-full flex items-center gap-3 px-4 py-3 rounded-xl transition-colors',
              activeTab === 'notifications' 
                ? 'bg-primary-50 dark:bg-primary-900/30 text-primary-600' 
                : 'hover:bg-slate-100 dark:hover:bg-slate-800 text-slate-600'
            ]"
          >
            <BellIcon class="w-5 h-5" />
            Notificaciones
          </button>
        </div>
      </div>
      
      <!-- Content -->
      <div class="lg:col-span-3">
        <!-- Profile Tab -->
        <div v-if="activeTab === 'profile'" class="card p-6">
          <h2 class="font-display font-semibold text-lg text-slate-900 dark:text-white mb-6">
            Información personal
          </h2>
          
          <form @submit.prevent="updateProfile" class="space-y-5 max-w-md">
            <div class="grid grid-cols-2 gap-4">
              <div>
                <label class="label">Nombre</label>
                <input
                  v-model="profileForm.first_name"
                  type="text"
                  class="input"
                />
              </div>
              <div>
                <label class="label">Apellido</label>
                <input
                  v-model="profileForm.last_name"
                  type="text"
                  class="input"
                />
              </div>
            </div>
            
            <div>
              <label class="label">Correo electrónico</label>
              <input
                v-model="profileForm.email"
                type="email"
                class="input"
                disabled
              />
              <p class="text-xs text-slate-500 mt-1">El correo no se puede cambiar</p>
            </div>
            
            <button type="submit" :disabled="loading" class="btn-primary">
              {{ loading ? 'Guardando...' : 'Guardar cambios' }}
            </button>
          </form>
        </div>
        
        <!-- Password Tab -->
        <div v-if="activeTab === 'password'" class="card p-6">
          <h2 class="font-display font-semibold text-lg text-slate-900 dark:text-white mb-6">
            Cambiar contraseña
          </h2>
          
          <form @submit.prevent="changePassword" class="space-y-5 max-w-md">
            <div>
              <label class="label">Contraseña actual</label>
              <input
                v-model="passwordForm.old_password"
                type="password"
                class="input"
                required
              />
            </div>
            
            <div>
              <label class="label">Nueva contraseña</label>
              <input
                v-model="passwordForm.new_password"
                type="password"
                class="input"
                required
              />
            </div>
            
            <div>
              <label class="label">Confirmar nueva contraseña</label>
              <input
                v-model="passwordForm.confirm_password"
                type="password"
                class="input"
                required
              />
            </div>
            
            <button type="submit" :disabled="loading" class="btn-primary">
              {{ loading ? 'Guardando...' : 'Cambiar contraseña' }}
            </button>
          </form>
        </div>
        
        <!-- Preferences Tab -->
        <div v-if="activeTab === 'preferences'" class="card p-6">
          <h2 class="font-display font-semibold text-lg text-slate-900 dark:text-white mb-6">
            Preferencias
          </h2>
          
          <form @submit.prevent="updateProfile" class="space-y-5 max-w-md">
            <div>
              <label class="label">Moneda predeterminada</label>
              <select v-model="profileForm.preferred_currency" class="input">
                <option v-for="curr in currencies" :key="curr.value" :value="curr.value">
                  {{ curr.label }}
                </option>
              </select>
            </div>
            
            <div>
              <label class="label">Tema</label>
              <div class="flex gap-3">
                <button
                  type="button"
                  @click="uiStore.darkMode && uiStore.toggleDarkMode()"
                  :class="[
                    'flex-1 px-4 py-3 rounded-xl border-2 transition-all',
                    !uiStore.darkMode 
                      ? 'border-primary-500 bg-primary-50' 
                      : 'border-slate-200 dark:border-slate-700'
                  ]"
                >
                  <div class="text-center">
                    <div class="w-8 h-8 mx-auto mb-2 rounded-lg bg-white border border-slate-200"></div>
                    <span class="text-sm font-medium">Claro</span>
                  </div>
                </button>
                <button
                  type="button"
                  @click="!uiStore.darkMode && uiStore.toggleDarkMode()"
                  :class="[
                    'flex-1 px-4 py-3 rounded-xl border-2 transition-all',
                    uiStore.darkMode 
                      ? 'border-primary-500 bg-primary-900/30' 
                      : 'border-slate-200 dark:border-slate-700'
                  ]"
                >
                  <div class="text-center">
                    <div class="w-8 h-8 mx-auto mb-2 rounded-lg bg-slate-800"></div>
                    <span class="text-sm font-medium">Oscuro</span>
                  </div>
                </button>
              </div>
            </div>
            
            <button type="submit" :disabled="loading" class="btn-primary">
              {{ loading ? 'Guardando...' : 'Guardar preferencias' }}
            </button>
          </form>
        </div>
        
        <!-- Notifications Tab -->
        <div v-if="activeTab === 'notifications'" class="card p-6">
          <h2 class="font-display font-semibold text-lg text-slate-900 dark:text-white mb-6 flex items-center gap-2">
            <EnvelopeIcon class="w-5 h-5" />
            Notificaciones por Email
          </h2>
          
          <div class="space-y-6 max-w-md">
            <!-- Master Toggle -->
            <div class="flex items-center justify-between p-4 bg-slate-50 dark:bg-slate-800 rounded-xl">
              <div>
                <p class="font-medium text-slate-900 dark:text-white">Notificaciones por email</p>
                <p class="text-sm text-slate-500">Recibir alertas en tu correo</p>
              </div>
              <button
                type="button"
                @click="notificationForm.emailNotifications = !notificationForm.emailNotifications"
                :class="[
                  'relative w-11 h-6 rounded-full transition-colors flex-shrink-0',
                  notificationForm.emailNotifications ? 'bg-primary-500' : 'bg-slate-300 dark:bg-slate-600'
                ]"
              >
                <span 
                  :class="[
                    'absolute top-0.5 left-0.5 w-5 h-5 rounded-full bg-white shadow-sm transition-transform duration-200',
                    notificationForm.emailNotifications ? 'translate-x-5' : 'translate-x-0'
                  ]"
                />
              </button>
            </div>
            
            <div v-if="notificationForm.emailNotifications" class="space-y-4">
              <!-- Debt Reminders -->
              <div class="border border-slate-200 dark:border-slate-700 rounded-xl p-4">
                <div class="flex items-center justify-between mb-3">
                  <div>
                    <p class="font-medium text-slate-900 dark:text-white">Recordatorios de deudas</p>
                    <p class="text-sm text-slate-500">Alertas de deudas próximas a vencer</p>
                  </div>
                  <button
                    type="button"
                    @click="notificationForm.debtReminders = !notificationForm.debtReminders"
                    :class="[
                      'relative w-11 h-6 rounded-full transition-colors flex-shrink-0',
                      notificationForm.debtReminders ? 'bg-primary-500' : 'bg-slate-300 dark:bg-slate-600'
                    ]"
                  >
                    <span 
                      :class="[
                        'absolute top-0.5 left-0.5 w-5 h-5 rounded-full bg-white shadow-sm transition-transform duration-200',
                        notificationForm.debtReminders ? 'translate-x-5' : 'translate-x-0'
                      ]"
                    />
                  </button>
                </div>
                <div v-if="notificationForm.debtReminders">
                  <label class="label">Días antes de vencimiento</label>
                  <select v-model="notificationForm.debtDaysBefore" class="input">
                    <option :value="3">3 días</option>
                    <option :value="5">5 días</option>
                    <option :value="7">7 días</option>
                    <option :value="14">14 días</option>
                    <option :value="30">30 días</option>
                  </select>
                </div>
              </div>
              
              <!-- Budget Alerts -->
              <div class="border border-slate-200 dark:border-slate-700 rounded-xl p-4">
                <div class="flex items-center justify-between mb-3">
                  <div>
                    <p class="font-medium text-slate-900 dark:text-white">Alertas de presupuesto</p>
                    <p class="text-sm text-slate-500">Cuando tu presupuesto está bajo o excedido</p>
                  </div>
                  <button
                    type="button"
                    @click="notificationForm.budgetAlerts = !notificationForm.budgetAlerts"
                    :class="[
                      'relative w-11 h-6 rounded-full transition-colors flex-shrink-0',
                      notificationForm.budgetAlerts ? 'bg-primary-500' : 'bg-slate-300 dark:bg-slate-600'
                    ]"
                  >
                    <span 
                      :class="[
                        'absolute top-0.5 left-0.5 w-5 h-5 rounded-full bg-white shadow-sm transition-transform duration-200',
                        notificationForm.budgetAlerts ? 'translate-x-5' : 'translate-x-0'
                      ]"
                    />
                  </button>
                </div>
                <div v-if="notificationForm.budgetAlerts">
                  <label class="label">Umbral de alerta (%)</label>
                  <select v-model="notificationForm.budgetThreshold" class="input">
                    <option :value="50">50% gastado</option>
                    <option :value="70">70% gastado</option>
                    <option :value="80">80% gastado</option>
                    <option :value="90">90% gastado</option>
                  </select>
                </div>
              </div>
              
              <!-- Monthly Summary -->
              <div class="border border-slate-200 dark:border-slate-700 rounded-xl p-4">
                <div class="flex items-center justify-between">
                  <div>
                    <p class="font-medium text-slate-900 dark:text-white">Resumen mensual</p>
                    <p class="text-sm text-slate-500">Recibir un resumen de tus finanzas del mes</p>
                  </div>
                  <button
                    type="button"
                    @click="notificationForm.monthlySummary = !notificationForm.monthlySummary"
                    :class="[
                      'relative w-11 h-6 rounded-full transition-colors flex-shrink-0',
                      notificationForm.monthlySummary ? 'bg-primary-500' : 'bg-slate-300 dark:bg-slate-600'
                    ]"
                  >
                    <span 
                      :class="[
                        'absolute top-0.5 left-0.5 w-5 h-5 rounded-full bg-white shadow-sm transition-transform duration-200',
                        notificationForm.monthlySummary ? 'translate-x-5' : 'translate-x-0'
                      ]"
                    />
                  </button>
                </div>
              </div>
            </div>
            
            <button @click="saveNotificationPreferences" class="btn-primary">
              Guardar preferencias
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

