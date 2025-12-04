<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { ExclamationTriangleIcon } from '@heroicons/vue/24/solid'

const warnings = [
  'Las apuestas pueden generar adicción y pérdidas financieras significativas',
  'La casa siempre tiene ventaja: las probabilidades están en tu contra',
  'Las apuestas no son una forma de generar ingresos, son entretenimiento de alto riesgo',
  'Si sientes que no puedes controlar tus apuestas, busca ayuda profesional',
  'El 95% de los apostadores pierden dinero a largo plazo',
  'Las apuestas pueden arruinar relaciones y causar problemas financieros graves',
  'Nunca apuestes más de lo que puedes permitirte perder',
  'Las ganancias pasadas no garantizan resultados futuros',
  'El juego responsable es fundamental: establece límites y cúmplelos',
  'Las apuestas online pueden ser especialmente adictivas por su accesibilidad',
  'Si apuestas para recuperar pérdidas, estás en un camino peligroso',
  'Las apuestas deben ser una decisión consciente, no un impulso emocional',
  'El tiempo que pasas apostando podría invertirse en actividades más productivas',
  'Las apuestas pueden afectar tu salud mental y bienestar emocional',
]

const currentWarning = ref(warnings[0])
let warningIndex = 0
let intervalId = null

function rotateWarning() {
  warningIndex = (warningIndex + 1) % warnings.length
  currentWarning.value = warnings[warningIndex]
}

onMounted(() => {
  intervalId = setInterval(rotateWarning, 5000)
})

onUnmounted(() => {
  if (intervalId) {
    clearInterval(intervalId)
  }
})
</script>

<template>
  <div class="bg-gradient-to-r from-red-600 to-orange-600 text-white p-4 rounded-xl shadow-lg mb-6 animate-pulse-subtle">
    <div class="flex items-start gap-3">
      <ExclamationTriangleIcon class="w-6 h-6 flex-shrink-0 mt-0.5" />
      <div class="flex-1 min-h-[80px] flex flex-col justify-center">
        <h3 class="font-bold text-lg mb-1">⚠️ Advertencia sobre Apuestas</h3>
        <p class="text-sm leading-relaxed">{{ currentWarning }}</p>
      </div>
    </div>
  </div>
</template>

<style scoped>
@keyframes pulse-subtle {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.95;
  }
}
.animate-pulse-subtle {
  animation: pulse-subtle 3s ease-in-out infinite;
}
</style>

