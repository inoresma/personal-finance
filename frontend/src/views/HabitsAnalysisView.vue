<script setup>
import { ref, computed, onMounted } from 'vue'
import { Line, Bar } from 'vue-chartjs'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend,
  Filler
} from 'chart.js'
import { formatMoney } from '@/composables/useCurrency'
import { useCategoriesStore } from '@/stores/categories'
import { useUiStore } from '@/stores/ui'
import api from '@/services/api'
import { CalendarIcon, ChartBarIcon } from '@heroicons/vue/24/outline'

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend,
  Filler
)

const categoriesStore = useCategoriesStore()
const uiStore = useUiStore()

const loading = ref(false)
const changeDate = ref('')
const periodDays = ref(30)
const categoryFilter = ref(null)
const analysisData = ref(null)

const expenseCategories = computed(() => {
  return categoriesStore.categories.filter(c => c.category_type === 'gasto')
})

const trendsChartData = computed(() => {
  if (!analysisData.value || !analysisData.value.trends) {
    return {
      labels: [],
      datasets: []
    }
  }

  const trends = analysisData.value.trends
  const changeDateIndex = trends.findIndex(t => t.period === 'after')

  return {
    labels: trends.map(t => {
      const date = new Date(t.date)
      return date.toLocaleDateString('es-ES', { month: 'short', day: 'numeric' })
    }),
    datasets: [
      {
        label: 'Antes del cambio',
        data: trends.map(t => t.period === 'before' ? parseFloat(t.total) : null),
        borderColor: '#ef4444',
        backgroundColor: '#ef444420',
        fill: true,
        tension: 0.4,
        pointRadius: 3,
      },
      {
        label: 'Después del cambio',
        data: trends.map(t => t.period === 'after' ? parseFloat(t.total) : null),
        borderColor: '#10b981',
        backgroundColor: '#10b98120',
        fill: true,
        tension: 0.4,
        pointRadius: 3,
      },
      {
        type: 'line',
        label: 'Fecha de cambio',
        data: trends.map((t, idx) => idx === changeDateIndex ? parseFloat(t.total) : null),
        borderColor: '#6366f1',
        borderWidth: 2,
        borderDash: [5, 5],
        pointRadius: 0,
        fill: false,
      }
    ]
  }
})

const trendsChartOptions = computed(() => ({
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      display: true,
      position: 'top',
    },
    tooltip: {
      backgroundColor: '#1e293b',
      titleFont: { size: 14, weight: '600' },
      bodyFont: { size: 13 },
      padding: 12,
      cornerRadius: 8,
      callbacks: {
        label: function(context) {
          if (context.parsed.y === null) return ''
          return formatMoney(context.parsed.y)
        }
      }
    }
  },
  scales: {
    y: {
      beginAtZero: true,
      ticks: {
        callback: function(value) {
          return formatMoney(value)
        }
      },
      grid: {
        color: 'rgba(148, 163, 184, 0.1)'
      }
    },
    x: {
      grid: {
        display: false
      }
    }
  }
}))

const improvementsChartData = computed(() => {
  if (!analysisData.value || !analysisData.value.improvements) {
    return {
      labels: [],
      datasets: []
    }
  }

  const topImprovements = analysisData.value.improvements.slice(0, 10)

  return {
    labels: topImprovements.map(i => i.category_name),
    datasets: [
      {
        label: 'Ahorro',
        data: topImprovements.map(i => i.savings),
        backgroundColor: topImprovements.map(i => i.category_color + '80'),
        borderColor: topImprovements.map(i => i.category_color),
        borderWidth: 1,
      }
    ]
  }
})

const improvementsChartOptions = computed(() => ({
  responsive: true,
  maintainAspectRatio: false,
  indexAxis: 'y',
  plugins: {
    legend: {
      display: false,
    },
    tooltip: {
      backgroundColor: '#1e293b',
      titleFont: { size: 14, weight: '600' },
      bodyFont: { size: 13 },
      padding: 12,
      cornerRadius: 8,
      callbacks: {
        label: function(context) {
          return formatMoney(context.parsed.x)
        }
      }
    }
  },
  scales: {
    x: {
      beginAtZero: true,
      ticks: {
        callback: function(value) {
          return formatMoney(value)
        }
      },
      grid: {
        color: 'rgba(148, 163, 184, 0.1)'
      }
    },
    y: {
      grid: {
        display: false
      }
    }
  }
}))

async function analyzeHabits() {
  if (!changeDate.value) {
    uiStore.showError('Selecciona una fecha de cambio')
    return
  }

  loading.value = true
  try {
    const params = {
      change_date: changeDate.value,
      period_days: periodDays.value,
    }
    
    if (categoryFilter.value) {
      params.category_id = categoryFilter.value
    }

    const response = await api.get('/reports/habits-analysis/', { params })
    analysisData.value = response.data
  } catch (error) {
    uiStore.showError('Error al analizar hábitos')
    console.error('Error:', error)
  } finally {
    loading.value = false
  }
}

onMounted(async () => {
  await categoriesStore.fetchCategories()
})
</script>

<template>
  <div class="space-y-6 animate-fade-in">
    <div>
      <h1 class="font-display text-2xl lg:text-3xl font-bold text-slate-900 dark:text-white">
        Análisis de Efectividad de Cambios
      </h1>
      <p class="mt-1 text-slate-600 dark:text-slate-400">
        Compara tus gastos antes y después de un cambio en tus hábitos
      </p>
    </div>

    <div class="card p-6">
      <div class="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
        <div>
          <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">
            Fecha del Cambio *
          </label>
          <div class="relative">
            <CalendarIcon class="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-slate-400" />
            <input
              v-model="changeDate"
              type="date"
              required
              class="input pl-10"
            />
          </div>
        </div>

        <div>
          <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">
            Días del Período
          </label>
          <input
            v-model.number="periodDays"
            type="number"
            min="7"
            max="90"
            class="input"
          />
        </div>

        <div>
          <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">
            Filtrar por Categoría (Opcional)
          </label>
          <select v-model="categoryFilter" class="input">
            <option :value="null">Todas las categorías</option>
            <option
              v-for="category in expenseCategories"
              :key="category.id"
              :value="category.id"
            >
              {{ category.name }}
            </option>
          </select>
        </div>
      </div>

      <button
        @click="analyzeHabits"
        :disabled="loading || !changeDate"
        class="btn-primary w-full md:w-auto"
      >
        <ChartBarIcon class="w-5 h-5" />
        Analizar
      </button>
    </div>

    <div v-if="loading" class="text-center py-12">
      <div class="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
    </div>

    <div v-else-if="analysisData" class="space-y-6">
      <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div class="card p-6">
          <p class="text-sm text-slate-500 dark:text-slate-400">Período Anterior</p>
          <p class="text-2xl font-bold text-slate-900 dark:text-white mt-1">
            {{ formatMoney(analysisData.period_before.total) }}
          </p>
          <p class="text-xs text-slate-500 dark:text-slate-400 mt-1">
            {{ new Date(analysisData.period_before.start_date).toLocaleDateString('es-ES') }} - 
            {{ new Date(analysisData.period_before.end_date).toLocaleDateString('es-ES') }}
          </p>
        </div>

        <div class="card p-6">
          <p class="text-sm text-slate-500 dark:text-slate-400">Período Posterior</p>
          <p class="text-2xl font-bold text-slate-900 dark:text-white mt-1">
            {{ formatMoney(analysisData.period_after.total) }}
          </p>
          <p class="text-xs text-slate-500 dark:text-slate-400 mt-1">
            {{ new Date(analysisData.period_after.start_date).toLocaleDateString('es-ES') }} - 
            {{ new Date(analysisData.period_after.end_date).toLocaleDateString('es-ES') }}
          </p>
        </div>

        <div class="card p-6" :class="analysisData.total_savings >= 0 ? 'bg-emerald-50 dark:bg-emerald-900/20' : 'bg-red-50 dark:bg-red-900/20'">
          <p class="text-sm text-slate-500 dark:text-slate-400">Ahorro Total</p>
          <p class="text-2xl font-bold mt-1" :class="analysisData.total_savings >= 0 ? 'text-emerald-600 dark:text-emerald-400' : 'text-red-600 dark:text-red-400'">
            {{ formatMoney(Math.abs(analysisData.total_savings)) }}
            <span class="text-lg">
              ({{ analysisData.reduction_percentage >= 0 ? '+' : '' }}{{ analysisData.reduction_percentage.toFixed(1) }}%)
            </span>
          </p>
        </div>
      </div>

      <div class="card p-6">
        <h3 class="text-lg font-semibold text-slate-900 dark:text-white mb-4">
          Tendencia de Gastos
        </h3>
        <div class="h-80">
          <Line :data="trendsChartData" :options="trendsChartOptions" />
        </div>
      </div>

      <div v-if="analysisData.improvements && analysisData.improvements.length > 0" class="card p-6">
        <h3 class="text-lg font-semibold text-slate-900 dark:text-white mb-4">
          Mejoras por Categoría
        </h3>
        <div class="h-96">
          <Bar :data="improvementsChartData" :options="improvementsChartOptions" />
        </div>
      </div>

      <div v-if="analysisData.improvements && analysisData.improvements.length > 0" class="card p-6">
        <h3 class="text-lg font-semibold text-slate-900 dark:text-white mb-4">
          Detalle de Mejoras
        </h3>
        <div class="overflow-x-auto">
          <table class="w-full">
            <thead>
              <tr class="border-b border-slate-200 dark:border-slate-700">
                <th class="text-left py-3 px-4 text-sm font-semibold text-slate-700 dark:text-slate-300">Categoría</th>
                <th class="text-right py-3 px-4 text-sm font-semibold text-slate-700 dark:text-slate-300">Antes</th>
                <th class="text-right py-3 px-4 text-sm font-semibold text-slate-700 dark:text-slate-300">Después</th>
                <th class="text-right py-3 px-4 text-sm font-semibold text-slate-700 dark:text-slate-300">Ahorro</th>
                <th class="text-right py-3 px-4 text-sm font-semibold text-slate-700 dark:text-slate-300">Mejora</th>
              </tr>
            </thead>
            <tbody>
              <tr
                v-for="improvement in analysisData.improvements"
                :key="improvement.category_id"
                class="border-b border-slate-100 dark:border-slate-800 hover:bg-slate-50 dark:hover:bg-slate-800/50"
              >
                <td class="py-3 px-4">
                  <div class="flex items-center gap-2">
                    <div
                      class="w-3 h-3 rounded-full"
                      :style="{ backgroundColor: improvement.category_color }"
                    />
                    <span class="text-sm text-slate-900 dark:text-white">{{ improvement.category_name }}</span>
                  </div>
                </td>
                <td class="py-3 px-4 text-right text-sm text-slate-600 dark:text-slate-400">
                  {{ formatMoney(improvement.before_total) }}
                </td>
                <td class="py-3 px-4 text-right text-sm text-slate-600 dark:text-slate-400">
                  {{ formatMoney(improvement.after_total) }}
                </td>
                <td class="py-3 px-4 text-right text-sm font-semibold" :class="improvement.savings >= 0 ? 'text-emerald-600 dark:text-emerald-400' : 'text-red-600 dark:text-red-400'">
                  {{ formatMoney(improvement.savings) }}
                </td>
                <td class="py-3 px-4 text-right text-sm font-semibold" :class="improvement.improvement_percentage >= 0 ? 'text-emerald-600 dark:text-emerald-400' : 'text-red-600 dark:text-red-400'">
                  {{ improvement.improvement_percentage >= 0 ? '+' : '' }}{{ improvement.improvement_percentage.toFixed(1) }}%
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>
</template>

