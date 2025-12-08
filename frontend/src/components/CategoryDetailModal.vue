<script setup>
import { ref, computed, onMounted } from 'vue'
import { Line } from 'vue-chartjs'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler
} from 'chart.js'
import { formatMoney } from '@/composables/useCurrency'
import api from '@/services/api'
import TransactionList from './TransactionList.vue'
import { XMarkIcon } from '@heroicons/vue/24/outline'

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler
)

const props = defineProps({
  category: {
    type: Object,
    required: true
  },
  show: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['close'])

const loading = ref(false)
const transactions = ref([])
const trendData = ref([])

const chartData = computed(() => {
  if (!trendData.value || trendData.value.length === 0) {
    return {
      labels: [],
      datasets: []
    }
  }

  return {
    labels: trendData.value.map(item => {
      const date = new Date(item.date)
      return date.toLocaleDateString('es-ES', { month: 'short', day: 'numeric' })
    }),
    datasets: [{
      label: 'Gastos',
      data: trendData.value.map(item => parseFloat(item.total)),
      borderColor: props.category.color || '#6366f1',
      backgroundColor: (props.category.color || '#6366f1') + '20',
      fill: true,
      tension: 0.4,
      pointRadius: 4,
      pointHoverRadius: 6,
    }]
  }
})

const chartOptions = computed(() => ({
  responsive: true,
  maintainAspectRatio: false,
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

const totalAmount = computed(() => {
  return transactions.value.reduce((sum, t) => sum + parseFloat(t.amount || 0), 0)
})

async function fetchCategoryDetails() {
  if (!props.category || !props.show) return

  loading.value = true
  try {
    const categoryId = props.category.id || props.category.category__id
    const endDate = new Date()
    const startDate = new Date()
    startDate.setMonth(startDate.getMonth() - 3)

    const [transactionsRes, trendRes] = await Promise.all([
      api.get('/transactions/', {
        params: {
          category: categoryId,
          transaction_type: 'gasto',
          date_from: startDate.toISOString().split('T')[0],
          date_to: endDate.toISOString().split('T')[0],
        }
      }),
      api.get('/reports/category-trend/', {
        params: {
          category_id: categoryId,
          days: 90,
        }
      })
    ])

    transactions.value = transactionsRes.data.results || transactionsRes.data || []
    trendData.value = trendRes.data.trend || []
  } catch (error) {
    console.error('Error fetching category details:', error)
    transactions.value = []
    trendData.value = []
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  if (props.show) {
    fetchCategoryDetails()
  }
})

function handleClose() {
  emit('close')
}
</script>

<template>
  <div
    v-if="show"
    class="fixed inset-0 z-50 overflow-y-auto"
    @click.self="handleClose"
  >
    <div class="flex items-center justify-center min-h-screen px-4 py-8">
      <div
        class="relative bg-white dark:bg-slate-900 rounded-2xl shadow-xl max-w-4xl w-full max-h-[90vh] overflow-hidden"
        @click.stop
      >
        <div class="sticky top-0 bg-white dark:bg-slate-900 border-b border-slate-200 dark:border-slate-800 px-6 py-4 flex items-center justify-between z-10">
          <div class="flex items-center gap-3">
            <div
              class="w-10 h-10 rounded-xl flex items-center justify-center"
              :style="{ backgroundColor: (category.color || '#6366f1') + '20' }"
            >
              <div
                class="w-6 h-6 rounded-full"
                :style="{ backgroundColor: category.color || '#6366f1' }"
              />
            </div>
            <div>
              <h2 class="text-xl font-bold text-slate-900 dark:text-white">
                {{ category.name || category.category__name }}
              </h2>
              <p class="text-sm text-slate-500 dark:text-slate-400">
                Detalles de gastos
              </p>
            </div>
          </div>
          <button
            @click="handleClose"
            class="p-2 rounded-lg hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors"
          >
            <XMarkIcon class="w-5 h-5 text-slate-600 dark:text-slate-400" />
          </button>
        </div>

        <div class="overflow-y-auto max-h-[calc(90vh-80px)] px-6 py-6">
          <div v-if="loading" class="text-center py-12">
            <div class="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
          </div>

          <div v-else class="space-y-6">
            <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div class="card p-4">
                <p class="text-sm text-slate-500 dark:text-slate-400">Total Gastado</p>
                <p class="text-2xl font-bold text-slate-900 dark:text-white mt-1">
                  {{ formatMoney(totalAmount) }}
                </p>
              </div>
              <div class="card p-4">
                <p class="text-sm text-slate-500 dark:text-slate-400">Transacciones</p>
                <p class="text-2xl font-bold text-slate-900 dark:text-white mt-1">
                  {{ transactions.length }}
                </p>
              </div>
              <div class="card p-4">
                <p class="text-sm text-sm text-slate-500 dark:text-slate-400">Promedio</p>
                <p class="text-2xl font-bold text-slate-900 dark:text-white mt-1">
                  {{ formatMoney(transactions.length > 0 ? totalAmount / transactions.length : 0) }}
                </p>
              </div>
            </div>

            <div v-if="trendData.length > 0" class="card p-6">
              <h3 class="text-lg font-semibold text-slate-900 dark:text-white mb-4">
                Tendencia de Gastos (Últimos 3 meses)
              </h3>
              <div class="h-64">
                <Line :data="chartData" :options="chartOptions" />
              </div>
            </div>

            <div class="card p-6">
              <h3 class="text-lg font-semibold text-slate-900 dark:text-white mb-4">
                Transacciones Recientes
              </h3>
              <TransactionList
                :transactions="transactions"
                :show-filters="false"
                :show-pagination="false"
              />
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

