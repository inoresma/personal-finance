<script setup>
import { ref, onMounted, computed, watch } from 'vue'
import { useUiStore } from '@/stores/ui'
import { useAccountsStore } from '@/stores/accounts'
import { useCategoriesStore } from '@/stores/categories'
import { useSecondaryCategoriesStore } from '@/stores/secondaryCategories'
import api from '@/services/api'
import { formatMoney } from '@/composables/useCurrency'
import DateInput from '@/components/DateInput.vue'
import LineChart from '@/components/LineChart.vue'
import BarChart from '@/components/BarChart.vue'
import { Doughnut } from 'vue-chartjs'
import {
  Chart as ChartJS,
  ArcElement,
  Tooltip,
  Legend,
} from 'chart.js'
import {
  PresentationChartLineIcon,
  FunnelIcon,
  CalendarIcon,
  ArrowTrendingUpIcon,
  ArrowTrendingDownIcon,
  ChartBarIcon,
  DocumentArrowDownIcon,
  ScaleIcon,
} from '@heroicons/vue/24/outline'

ChartJS.register(ArcElement, Tooltip, Legend)

const uiStore = useUiStore()
const accountsStore = useAccountsStore()
const categoriesStore = useCategoriesStore()
const secondaryCategoriesStore = useSecondaryCategoriesStore()

const loading = ref(false)
const activeReport = ref('summary')
const categoryViewMode = ref('primary')

const dateFrom = ref(null)
const dateTo = ref(null)
const selectedAccount = ref(null)
const selectedCategory = ref(null)
const transactionType = ref(null)
const selectedPeriod = ref('this_month')
const showCustomDates = ref(false)

const summaryData = ref(null)
const categoryData = ref(null)
const accountData = ref(null)
const trendsData = ref(null)

function getPeriodDates(period) {
  const today = new Date()
  const year = today.getFullYear()
  const month = today.getMonth()
  
  switch(period) {
    case 'this_month':
      return {
        from: new Date(year, month, 1).toISOString().split('T')[0],
        to: today.toISOString().split('T')[0]
      }
    case 'last_month':
      const lastMonth = new Date(year, month - 1, 1)
      const lastMonthEnd = new Date(year, month, 0)
      return {
        from: lastMonth.toISOString().split('T')[0],
        to: lastMonthEnd.toISOString().split('T')[0]
      }
    case 'last_3_months':
      const threeMonthsAgo = new Date(year, month - 2, 1)
      return {
        from: threeMonthsAgo.toISOString().split('T')[0],
        to: today.toISOString().split('T')[0]
      }
    case 'this_year':
      return {
        from: new Date(year, 0, 1).toISOString().split('T')[0],
        to: today.toISOString().split('T')[0]
      }
    case 'custom':
      showCustomDates.value = true
      return {
        from: dateFrom.value || new Date(year, month, 1).toISOString().split('T')[0],
        to: dateTo.value || today.toISOString().split('T')[0]
      }
    default:
      return {
        from: new Date(year, month, 1).toISOString().split('T')[0],
        to: today.toISOString().split('T')[0]
      }
  }
}

function setPeriod(period) {
  selectedPeriod.value = period
  if (period !== 'custom') {
    showCustomDates.value = false
    const dates = getPeriodDates(period)
    dateFrom.value = dates.from
    dateTo.value = dates.to
  } else {
    showCustomDates.value = true
  }
  fetchReports()
}

function getParams() {
  const params = {}
  
  if (selectedPeriod.value !== 'custom') {
    const dates = getPeriodDates(selectedPeriod.value)
    params.date_from = dates.from
    params.date_to = dates.to
  } else {
    if (dateFrom.value) params.date_from = dateFrom.value
    if (dateTo.value) params.date_to = dateTo.value
  }
  
  if (selectedAccount.value) params.account = selectedAccount.value
  if (selectedCategory.value) params.category = selectedCategory.value
  if (transactionType.value) params.transaction_type = transactionType.value
  
  return params
}

async function fetchSummary() {
  try {
    const params = getParams()
    const response = await api.get('/transactions/summary/', { params })
    summaryData.value = response.data
  } catch (error) {
    console.error('Error fetching summary:', error)
    uiStore.showError('Error al cargar resumen')
  }
}

async function fetchByCategory() {
  try {
    const params = getParams()
    if (categoryViewMode.value === 'secondary') {
      const response = await api.get('/reports/by_secondary_category/', { params })
      categoryData.value = response.data
    } else {
      const response = await api.get('/transactions/by_category/', { params })
      categoryData.value = response.data
    }
  } catch (error) {
    console.error('Error fetching category data:', error)
    uiStore.showError('Error al cargar datos por categoría')
  }
}

async function fetchByAccount() {
  try {
    const params = getParams()
    const response = await api.get('/reports/dashboard/', { params })
    accountData.value = response.data.expenses_by_account || []
  } catch (error) {
    console.error('Error fetching account data:', error)
    uiStore.showError('Error al cargar datos por cuenta')
  }
}

async function fetchTrends() {
  try {
    const params = getParams()
    const response = await api.get('/reports/dashboard/', { params })
    trendsData.value = response.data.monthly_trends || []
  } catch (error) {
    console.error('Error fetching trends:', error)
    uiStore.showError('Error al cargar tendencias')
  }
}

async function fetchReports() {
  loading.value = true
  try {
    await Promise.all([
      fetchSummary(),
      fetchByCategory(),
      fetchByAccount(),
      fetchTrends()
    ])
  } finally {
    loading.value = false
  }
}

function clearFilters() {
  selectedAccount.value = null
  selectedCategory.value = null
  transactionType.value = null
  setPeriod('this_month')
}

const categoryChartData = computed(() => {
  if (!categoryData.value || categoryData.value.length === 0) return null
  
  const labelField = categoryViewMode.value === 'secondary' ? 'secondary_category__name' : 'category__name'
  const colorField = categoryViewMode.value === 'secondary' ? 'secondary_category__color' : 'category__color'
  
  return {
    labels: categoryData.value.map(c => c[labelField] || 'Sin categoría'),
    datasets: [{
      data: categoryData.value.map(c => parseFloat(c.total || 0)),
      backgroundColor: categoryData.value.map(c => c[colorField] || '#6366f1'),
      borderWidth: 0,
      hoverOffset: 8,
    }]
  }
})

const categoryChartOptions = computed(() => ({
  responsive: true,
  maintainAspectRatio: false,
  cutout: '70%',
  plugins: {
    legend: {
      position: 'right',
    },
    tooltip: {
      backgroundColor: '#1e293b',
      padding: 12,
      cornerRadius: 8,
      callbacks: {
        label: function(context) {
          return formatMoney(context.parsed)
        }
      }
    }
  }
}))

const accountChartData = computed(() => {
  if (!accountData.value || accountData.value.length === 0) return null
  
  return {
    labels: accountData.value.map(a => a.account__name),
    datasets: [{
      data: accountData.value.map(a => parseFloat(a.total || 0)),
      backgroundColor: accountData.value.map(a => a.account__color || '#6366f1'),
      borderWidth: 0,
      hoverOffset: 8,
    }]
  }
})

const trendsChartData = computed(() => {
  if (!trendsData.value || trendsData.value.length === 0) return null
  
  return {
    labels: trendsData.value.map(t => t.month_label),
    datasets: [
      {
        label: 'Ingresos',
        data: trendsData.value.map(t => t.income),
        borderColor: '#22c55e',
        backgroundColor: 'rgba(34, 197, 94, 0.1)',
        tension: 0.4,
        fill: true
      },
      {
        label: 'Gastos',
        data: trendsData.value.map(t => t.expenses),
        borderColor: '#ef4444',
        backgroundColor: 'rgba(239, 68, 68, 0.1)',
        tension: 0.4,
        fill: true
      }
    ]
  }
})

const topCategories = computed(() => {
  if (!categoryData.value) return []
  const nameField = categoryViewMode.value === 'secondary' ? 'secondary_category__name' : 'category__name'
  const colorField = categoryViewMode.value === 'secondary' ? 'secondary_category__color' : 'category__color'
  
  return categoryData.value.slice(0, 10).map(c => ({
    ...c,
    name: c[nameField] || 'Sin categoría',
    color: c[colorField] || '#6366f1'
  }))
})

watch([activeReport, categoryViewMode], () => {
  if (activeReport.value === 'categories') {
    fetchByCategory()
  } else {
    fetchReports()
  }
})

onMounted(async () => {
  await accountsStore.fetchAccounts()
  await categoriesStore.fetchCategories()
  await secondaryCategoriesStore.fetchSecondaryCategories()
  const dates = getPeriodDates('this_month')
  dateFrom.value = dates.from
  dateTo.value = dates.to
  fetchReports()
})
</script>

<template>
  <div class="space-y-8 animate-fade-in">
    <!-- Header -->
    <div class="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
      <div>
        <h1 class="font-display text-2xl lg:text-3xl font-bold text-slate-900 dark:text-white flex items-center gap-2">
          <PresentationChartLineIcon class="w-8 h-8" />
          Reportes
        </h1>
        <p class="mt-1 text-slate-600 dark:text-slate-400">
          Análisis detallado de tus finanzas
        </p>
      </div>
    </div>

    <!-- Report Types -->
    <div class="flex flex-wrap gap-2 border-b border-slate-200 dark:border-slate-800">
      <button
        @click="activeReport = 'summary'"
        :class="[
          'px-4 py-2 font-medium transition-all border-b-2',
          activeReport === 'summary'
            ? 'border-primary-600 text-primary-600'
            : 'border-transparent text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-slate-200'
        ]"
      >
        Resumen
      </button>
      <button
        @click="activeReport = 'categories'"
        :class="[
          'px-4 py-2 font-medium transition-all border-b-2',
          activeReport === 'categories'
            ? 'border-primary-600 text-primary-600'
            : 'border-transparent text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-slate-200'
        ]"
      >
        Por Categoría
      </button>
      <button
        @click="activeReport = 'accounts'"
        :class="[
          'px-4 py-2 font-medium transition-all border-b-2',
          activeReport === 'accounts'
            ? 'border-primary-600 text-primary-600'
            : 'border-transparent text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-slate-200'
        ]"
      >
        Por Cuenta
      </button>
      <button
        @click="activeReport = 'trends'"
        :class="[
          'px-4 py-2 font-medium transition-all border-b-2',
          activeReport === 'trends'
            ? 'border-primary-600 text-primary-600'
            : 'border-transparent text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-slate-200'
        ]"
      >
        Tendencias
      </button>
    </div>

    <!-- Filters -->
    <div class="card p-6">
      <div class="flex flex-col gap-4">
        <div class="flex items-center gap-2">
          <FunnelIcon class="w-5 h-5 text-slate-400" />
          <h3 class="font-semibold text-slate-900 dark:text-white">Filtros</h3>
        </div>
        
        <!-- Period Buttons -->
        <div class="flex flex-wrap items-center gap-2">
          <button
            @click="setPeriod('this_month')"
            :class="[
              'px-3 py-1.5 rounded-lg text-sm font-medium transition-all',
              selectedPeriod === 'this_month'
                ? 'bg-primary-600 text-white'
                : 'bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300 hover:bg-slate-200 dark:hover:bg-slate-700'
            ]"
          >
            Este mes
          </button>
          <button
            @click="setPeriod('last_month')"
            :class="[
              'px-3 py-1.5 rounded-lg text-sm font-medium transition-all',
              selectedPeriod === 'last_month'
                ? 'bg-primary-600 text-white'
                : 'bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300 hover:bg-slate-200 dark:hover:bg-slate-700'
            ]"
          >
            Mes anterior
          </button>
          <button
            @click="setPeriod('last_3_months')"
            :class="[
              'px-3 py-1.5 rounded-lg text-sm font-medium transition-all',
              selectedPeriod === 'last_3_months'
                ? 'bg-primary-600 text-white'
                : 'bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300 hover:bg-slate-200 dark:hover:bg-slate-700'
            ]"
          >
            Últimos 3 meses
          </button>
          <button
            @click="setPeriod('this_year')"
            :class="[
              'px-3 py-1.5 rounded-lg text-sm font-medium transition-all',
              selectedPeriod === 'this_year'
                ? 'bg-primary-600 text-white'
                : 'bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300 hover:bg-slate-200 dark:hover:bg-slate-700'
            ]"
          >
            Este año
          </button>
          <button
            @click="setPeriod('custom')"
            :class="[
              'px-3 py-1.5 rounded-lg text-sm font-medium transition-all flex items-center gap-1',
              selectedPeriod === 'custom'
                ? 'bg-primary-600 text-white'
                : 'bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300 hover:bg-slate-200 dark:hover:bg-slate-700'
            ]"
          >
            <CalendarIcon class="w-4 h-4" />
            Personalizado
          </button>
        </div>
        
        <!-- Custom Date Range -->
        <div v-if="showCustomDates" class="flex flex-wrap items-center gap-3 p-3 bg-slate-50 dark:bg-slate-800/50 rounded-lg">
          <div class="flex items-center gap-2">
            <label class="text-sm text-slate-600 dark:text-slate-400">Desde:</label>
            <DateInput v-model="dateFrom" />
          </div>
          <div class="flex items-center gap-2">
            <label class="text-sm text-slate-600 dark:text-slate-400">Hasta:</label>
            <DateInput v-model="dateTo" />
          </div>
        </div>
        
        <!-- Other Filters -->
        <div class="flex flex-wrap items-center gap-3">
          <select v-model="selectedAccount" class="input py-1.5 text-sm w-[160px]">
            <option :value="null">Todas las cuentas</option>
            <option v-for="acc in accountsStore.accounts" :key="acc.id" :value="acc.id">
              {{ acc.name }}
            </option>
          </select>
          <select v-model="selectedCategory" class="input py-1.5 text-sm w-[160px]">
            <option :value="null">Todas las categorías</option>
            <option v-for="cat in categoriesStore.expenseCategories.filter(c => !c.parent)" :key="cat.id" :value="cat.id">
              {{ cat.name }}
            </option>
          </select>
          <select v-model="transactionType" class="input py-1.5 text-sm w-[160px]">
            <option :value="null">Todos los tipos</option>
            <option value="ingreso">Solo ingresos</option>
            <option value="gasto">Solo gastos</option>
          </select>
          <button 
            v-if="selectedAccount || selectedCategory || transactionType || selectedPeriod !== 'this_month'" 
            @click="clearFilters" 
            class="text-sm text-primary-600 hover:underline px-2"
          >
            Limpiar
          </button>
        </div>
      </div>
    </div>

    <!-- Loading -->
    <div v-if="loading" class="flex justify-center items-center py-12">
      <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
    </div>

    <!-- Summary Report -->
    <div v-else-if="activeReport === 'summary'" class="space-y-6">
      <div v-if="summaryData" class="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div class="card p-6">
          <div class="flex items-center justify-between">
            <div>
              <p class="text-sm text-slate-500 dark:text-slate-400">Ingresos</p>
              <p class="text-2xl font-bold text-emerald-600 mt-1">
                {{ formatMoney(summaryData.income) }}
              </p>
            </div>
            <div class="w-12 h-12 rounded-xl bg-emerald-100 dark:bg-emerald-900/30 flex items-center justify-center">
              <ArrowTrendingUpIcon class="w-6 h-6 text-emerald-600 dark:text-emerald-400" />
            </div>
          </div>
        </div>
        
        <div class="card p-6">
          <div class="flex items-center justify-between">
            <div>
              <p class="text-sm text-slate-500 dark:text-slate-400">Gastos</p>
              <p class="text-2xl font-bold text-red-600 mt-1">
                {{ formatMoney(summaryData.expenses) }}
              </p>
            </div>
            <div class="w-12 h-12 rounded-xl bg-red-100 dark:bg-red-900/30 flex items-center justify-center">
              <ArrowTrendingDownIcon class="w-6 h-6 text-red-600 dark:text-red-400" />
            </div>
          </div>
        </div>
        
        <div class="card p-6">
          <div class="flex items-center justify-between">
            <div>
              <p class="text-sm text-slate-500 dark:text-slate-400">Balance</p>
              <p 
                class="text-2xl font-bold mt-1"
                :class="summaryData.balance >= 0 ? 'text-emerald-600' : 'text-red-600'"
              >
                {{ formatMoney(summaryData.balance) }}
              </p>
            </div>
            <div class="w-12 h-12 rounded-xl bg-blue-100 dark:bg-blue-900/30 flex items-center justify-center">
              <ScaleIcon class="w-6 h-6 text-blue-600 dark:text-blue-400" />
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Categories Report -->
    <div v-else-if="activeReport === 'categories'" class="space-y-6">
      <div class="flex items-center justify-between">
        <h3 class="font-semibold text-slate-900 dark:text-white">Vista de Categorías</h3>
        <div class="flex gap-2">
          <button
            @click="categoryViewMode = 'primary'"
            :class="[
              'px-3 py-1.5 rounded-lg text-sm font-medium transition-all',
              categoryViewMode === 'primary'
                ? 'bg-primary-600 text-white'
                : 'bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300 hover:bg-slate-200 dark:hover:bg-slate-700'
            ]"
          >
            Principal
          </button>
          <button
            @click="categoryViewMode = 'secondary'"
            :class="[
              'px-3 py-1.5 rounded-lg text-sm font-medium transition-all',
              categoryViewMode === 'secondary'
                ? 'bg-primary-600 text-white'
                : 'bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300 hover:bg-slate-200 dark:hover:bg-slate-700'
            ]"
          >
            Secundaria
          </button>
        </div>
      </div>
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <!-- Chart -->
        <div v-if="categoryChartData" class="card p-6">
          <h3 class="font-semibold text-slate-900 dark:text-white mb-4">Distribución por Categoría</h3>
          <div class="relative h-64 w-full">
            <Doughnut :data="categoryChartData" :options="categoryChartOptions" />
          </div>
        </div>
        
        <!-- Table -->
        <div class="card p-6">
          <h3 class="font-semibold text-slate-900 dark:text-white mb-4">Top Categorías</h3>
          <div class="space-y-3 max-h-64 overflow-y-auto">
            <div 
              v-for="(cat, index) in topCategories" 
              :key="cat.category__id || index"
              class="flex items-center justify-between p-3 rounded-lg bg-slate-50 dark:bg-slate-800/50"
            >
              <div class="flex items-center gap-3">
                <div 
                  class="w-4 h-4 rounded-full"
                  :style="{ backgroundColor: cat.color || '#6366f1' }"
                ></div>
                <span class="font-medium text-slate-900 dark:text-white">
                  {{ cat.name || 'Sin categoría' }}
                </span>
              </div>
              <span class="font-bold text-slate-900 dark:text-white">
                {{ formatMoney(cat.total) }}
              </span>
            </div>
            <div v-if="!topCategories.length" class="text-center text-slate-500 py-8">
              No hay datos disponibles
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Accounts Report -->
    <div v-else-if="activeReport === 'accounts'" class="space-y-6">
      <div v-if="accountChartData" class="card p-6">
        <h3 class="font-semibold text-slate-900 dark:text-white mb-4">Gastos por Cuenta</h3>
        <div class="relative h-64 w-full">
          <Doughnut :data="accountChartData" :options="categoryChartOptions" />
        </div>
        <div class="mt-4 space-y-2">
          <div 
            v-for="acc in accountData" 
            :key="acc.account__id"
            class="flex items-center justify-between p-3 rounded-lg bg-slate-50 dark:bg-slate-800/50"
          >
            <div class="flex items-center gap-3">
              <div 
                class="w-4 h-4 rounded-full"
                :style="{ backgroundColor: acc.account__color || '#6366f1' }"
              ></div>
              <span class="font-medium text-slate-900 dark:text-white">
                {{ acc.account__name }}
              </span>
            </div>
            <span class="font-bold text-slate-900 dark:text-white">
              {{ formatMoney(acc.total) }}
            </span>
          </div>
          <div v-if="!accountData.length" class="text-center text-slate-500 py-8">
            No hay datos disponibles
          </div>
        </div>
      </div>
    </div>

    <!-- Trends Report -->
    <div v-else-if="activeReport === 'trends'" class="space-y-6">
      <div v-if="trendsChartData" class="card p-6">
        <h3 class="font-semibold text-slate-900 dark:text-white mb-4">Tendencias Mensuales</h3>
        <LineChart 
          :labels="trendsChartData.labels"
          :datasets="trendsChartData.datasets"
          :height="400"
        />
      </div>
      <div v-else class="card p-6">
        <p class="text-center text-slate-500 py-8">
          No hay datos de tendencias disponibles para el período seleccionado
        </p>
      </div>
    </div>
  </div>
</template>
