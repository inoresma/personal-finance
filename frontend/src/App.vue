<script setup>
import { computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useUiStore } from '@/stores/ui'
import Toast from '@/components/Toast.vue'

const router = useRouter()
const authStore = useAuthStore()
const uiStore = useUiStore()

const isAuthenticated = computed(() => authStore.isAuthenticated)

onMounted(() => {
  authStore.checkAuth()
  
  if (localStorage.getItem('darkMode') === 'true') {
    uiStore.toggleDarkMode()
  }
})

watch(() => uiStore.darkMode, (isDark) => {
  if (isDark) {
    document.documentElement.classList.add('dark')
  } else {
    document.documentElement.classList.remove('dark')
  }
}, { immediate: true })
</script>

<template>
  <div class="min-h-screen">
    <router-view />
    <Toast />
  </div>
</template>





