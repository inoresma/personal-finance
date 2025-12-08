<script setup>
import { ref, onMounted, computed, watch } from 'vue'
import { useAccountsStore } from '@/stores/accounts'
import { useCategoriesStore } from '@/stores/categories'
import { useGoalsStore } from '@/stores/goals'
import api from '@/services/api'
import { formatMoney } from '@/composables/useCurrency'
import StatCard from '@/components/StatCard.vue'
import TransactionList from '@/components/TransactionList.vue'
import ExpenseChart from '@/components/ExpenseChart.vue'
import BudgetAlerts from '@/components/BudgetAlerts.vue'
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

ChartJS.register(ArcElement, Tooltip, Legend)
import {
  BanknotesIcon,
  ArrowTrendingUpIcon,
  ArrowTrendingDownIcon,
  ScaleIcon,
  ChartPieIcon,
  PresentationChartLineIcon,
  BugAntIcon,
  FunnelIcon,
  BuildingLibraryIcon,
  CalendarIcon,
  FlagIcon,
} from '@heroicons/vue/24/outline'

const accountsStore = useAccountsStore()
const categoriesStore = useCategoriesStore()
const goalsStore = useGoalsStore()

const dashboardData = ref(null)
const antExpensesData = ref(null)
const accountStats = ref([])
const loading = ref(true)

const selectedAccount = ref(null)
const selectedCategory = ref(null)
const dateFrom = ref(null)
const dateTo = ref(null)
const selectedPeriod = ref('this_month')
const transactionType = ref(null)
const showCustomDates = ref(false)

function getPeriodDates(period) {
  const today = new Date()
  const year = today.getFullYear()
  const month = today.getMonth()
  
  function formatDate(date) {
    const y = date.getFullYear()
    const m = String(date.getMonth() + 1).padStart(2, '0')
    const d = String(date.getDate()).padStart(2, '0')
    return `${y}-${m}-${d}`
  }
  
  switch(period) {
    case 'this_month':
      return {
        from: formatDate(new Date(year, month, 1)),
        to: formatDate(today)
      }
    case 'last_month':
      const lastMonth = new Date(year, month - 1, 1)
      const lastMonthEnd = new Date(year, month, 0)
      return {
        from: formatDate(lastMonth),
        to: formatDate(lastMonthEnd)
      }
    case 'last_3_months':
      const threeMonthsAgo = new Date(year, month - 2, 1)
      return {
        from: formatDate(threeMonthsAgo),
        to: formatDate(today)
      }
    case 'this_year':
      return {
        from: formatDate(new Date(year, 0, 1)),
        to: formatDate(today)
      }
    case 'custom':
      showCustomDates.value = true
      return {
        from: dateFrom.value || formatDate(new Date(year, month, 1)),
        to: dateTo.value || formatDate(today)
      }
    default:
      return {
        from: formatDate(new Date(year, month, 1)),
        to: formatDate(today)
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
  fetchDashboard()
}

const totalBalance = computed(() => {
  if (selectedAccount.value) {
    const account = accountsStore.accounts.find(a => a.id === selectedAccount.value)
    return account?.balance || 0
  }
  return dashboardData.value?.total_balance || 0
})

const monthIncome = computed(() => {
  return dashboardData.value?.month_summary?.income || 0
})

const monthExpenses = computed(() => {
  return dashboardData.value?.month_summary?.expenses || 0
})

const monthBalance = computed(() => {
  return monthIncome.value - monthExpenses.value
})

const antExpensesChartData = computed(() => {
  if (!dashboardData.value?.ant_expenses) return null
  
  const ant = dashboardData.value.ant_expenses.ant || 0
  const normal = dashboardData.value.ant_expenses.normal || 0
  
  if (ant === 0 && normal === 0) return null
  
  return {
    labels: ['Gastos hormiga', 'Gastos normales'],
    datasets: [{
      data: [ant, normal],
      backgroundColor: ['#f97316', '#6366f1'],
      borderWidth: 0,
      hoverOffset: 8,
    }]
  }
})

const antExpensesChartOptions = computed(() => ({
  responsive: true,
  maintainAspectRatio: false,
  cutout: '70%',
  plugins: {
    legend: {
      display: false,
    },
    tooltip: {
      backgroundColor: '#1e293b',
      padding: 12,
      cornerRadius: 8,
      callbacks: {
        label: function(context) {
          return formatCurrency(context.parsed)
        }
      }
    }
  }
}))

const expensesByAccountChartData = computed(() => {
  if (!dashboardData.value?.expenses_by_account?.length) return null
  
  const data = dashboardData.value.expenses_by_account
  
  return {
    labels: data.map(item => item.account__name),
    datasets: [{
      data: data.map(item => parseFloat(item.total || 0)),
      backgroundColor: data.map(item => item.account__color || '#6366f1'),
      borderWidth: 0,
      hoverOffset: 8,
    }]
  }
})

const expensesByAccountChartOptions = computed(() => ({
  responsive: true,
  maintainAspectRatio: false,
  cutout: '70%',
  plugins: {
    legend: {
      display: false,
    },
    tooltip: {
      backgroundColor: '#1e293b',
      padding: 12,
      cornerRadius: 8,
      callbacks: {
        label: function(context) {
          return formatCurrency(context.parsed)
        }
      }
    }
  }
}))

const totalAntExpenses = computed(() => {
  if (!dashboardData.value?.ant_expenses) return 0
  return dashboardData.value.ant_expenses.total || 0
})

const totalExpensesByAccount = computed(() => {
  if (!dashboardData.value?.expenses_by_account?.length) return 0
  return dashboardData.value.expenses_by_account.reduce((sum, item) => sum + parseFloat(item.total || 0), 0)
})

const filteredExpensesByCategory = computed(() => {
  if (!dashboardData.value?.expenses_by_category) return []
  if (!selectedCategory.value) return dashboardData.value.expenses_by_category
  return dashboardData.value.expenses_by_category.filter(
    e => e.category__id === selectedCategory.value
  )
})

const monthlyTrendsData = computed(() => {
  if (!dashboardData.value?.monthly_trends?.length) return null
  
  const trends = dashboardData.value.monthly_trends
  return {
    labels: trends.map(t => t.month_label),
    datasets: [
      {
        label: 'Ingresos',
        data: trends.map(t => t.income),
        borderColor: '#22c55e',
        backgroundColor: 'rgba(34, 197, 94, 0.1)',
        tension: 0.4,
        fill: true
      },
      {
        label: 'Gastos',
        data: trends.map(t => t.expenses),
        borderColor: '#ef4444',
        backgroundColor: 'rgba(239, 68, 68, 0.1)',
        tension: 0.4,
        fill: true
      }
    ]
  }
})

const dailyExpensesData = computed(() => {
  if (!dashboardData.value?.daily_expenses?.length) return null
  
  const expenses = dashboardData.value.daily_expenses
  return {
    labels: expenses.map(e => `${e.day} ${e.day_name}`),
    data: expenses.map(e => e.total)
  }
})

const topCategories = computed(() => {
  if (!dashboardData.value?.expenses_by_category?.length) return []
  return dashboardData.value.expenses_by_category
    .slice(0, 5)
    .map(cat => ({
      name: cat.category__name || 'Sin categoría',
      total: parseFloat(cat.total || 0),
      color: cat.category__color || '#6366f1',
      percentage: dashboardData.value.month_summary?.expenses 
        ? ((parseFloat(cat.total || 0) / dashboardData.value.month_summary.expenses) * 100).toFixed(1)
        : 0
    }))
})

const previousMonthComparison = computed(() => {
  if (!dashboardData.value?.monthly_trends?.length || dashboardData.value.monthly_trends.length < 2) {
    return null
  }
  
  const current = dashboardData.value.monthly_trends[dashboardData.value.monthly_trends.length - 1]
  const previous = dashboardData.value.monthly_trends[dashboardData.value.monthly_trends.length - 2]
  
  const incomeChange = previous.income > 0 
    ? ((current.income - previous.income) / previous.income) * 100 
    : 0
  const expensesChange = previous.expenses > 0 
    ? ((current.expenses - previous.expenses) / previous.expenses) * 100 
    : 0
  
  return {
    income: {
      current: current.income,
      previous: previous.income,
      change: incomeChange,
      isPositive: incomeChange >= 0
    },
    expenses: {
      current: current.expenses,
      previous: previous.expenses,
      change: expensesChange,
      isPositive: expensesChange <= 0
    }
  }
})

const savingsRate = computed(() => {
  if (!monthIncome.value || monthIncome.value === 0) return 0
  return ((monthBalance.value / monthIncome.value) * 100).toFixed(1)
})

const antExpensesPercentage = computed(() => {
  if (!monthExpenses.value || monthExpenses.value === 0) return 0
  const ant = dashboardData.value?.ant_expenses?.ant || 0
  return ((ant / monthExpenses.value) * 100).toFixed(1)
})

async function fetchDashboard() {
  loading.value = true
  try {
    const params = {}
    if (selectedAccount.value) params.account = selectedAccount.value
    if (selectedCategory.value) params.category = selectedCategory.value
    if (transactionType.value) params.transaction_type = transactionType.value
    
    if (selectedPeriod.value !== 'custom') {
      const dates = getPeriodDates(selectedPeriod.value)
      params.date_from = dates.from
      params.date_to = dates.to
    } else {
      if (dateFrom.value) params.date_from = dateFrom.value
      if (dateTo.value) params.date_to = dateTo.value
    }
    
    if (!params.date_from || !params.date_to) {
      const dates = getPeriodDates('this_month')
      params.date_from = dates.from
      params.date_to = dates.to
    }
    
    console.log('Fetching dashboard with params:', params)
    
    const [dashRes, antRes] = await Promise.all([
      api.get('/reports/dashboard/', { params }),
      api.get('/transactions/ant_expenses/', { params })
    ])
    
    console.log('Dashboard response:', dashRes.data)
    console.log('Month summary:', dashRes.data?.month_summary)
    console.log('Total balance:', dashRes.data?.total_balance)
    
    dashboardData.value = dashRes.data
    antExpensesData.value = antRes.data
    
    if (!selectedAccount.value) {
      accountStats.value = accountsStore.accounts.map(acc => ({
        ...acc,
        monthExpenses: dashboardData.value?.account_stats?.[acc.id]?.expenses || 0,
        monthIncome: dashboardData.value?.account_stats?.[acc.id]?.income || 0,
      }))
    }
  } catch (error) {
    console.error('Error fetching dashboard:', error)
    console.error('Error details:', error.response?.data || error.message)
    if (error.response?.data) {
      dashboardData.value = {
        total_balance: 0,
        month_summary: { income: 0, expenses: 0, balance: 0 },
        ant_expenses: { ant: 0, normal: 0, total: 0 },
        expenses_by_category: [],
        expenses_by_account: [],
        account_stats: {},
        recent_transactions: [],
        budget_alerts: [],
        investments_total: 0,
        debts_remaining: 0,
        monthly_trends: [],
        daily_expenses: []
      }
    }
  } finally {
    loading.value = false
  }
}

function formatCurrency(value, currency = 'CLP') {
  return formatMoney(value, currency)
}

function clearFilters() {
  selectedAccount.value = null
  selectedCategory.value = null
  transactionType.value = null
  setPeriod('this_month')
}

watch([selectedAccount, selectedCategory, transactionType, dateFrom, dateTo], () => {
  fetchDashboard()
})

watch(() => accountsStore.accounts, () => {
  if (accountsStore.accounts.length > 0) {
    fetchDashboard()
  }
}, { deep: true })

onMounted(async () => {
  setPeriod('this_month')
  const dates = getPeriodDates('this_month')
  dateFrom.value = dates.from
  dateTo.value = dates.to
  
  await Promise.all([
    accountsStore.fetchAccounts(),
    categoriesStore.fetchCategories(),
    goalsStore.fetchActiveGoals(),
    fetchDashboard()
  ])
})
</script>

<template>
  <div class="space-y-8 animate-fade-in">
    <!-- Header -->
    <div class="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
      <div>
        <h1 class="font-display text-2xl lg:text-3xl font-bold text-slate-900 dark:text-white">
          Dashboard
        </h1>
        <p class="mt-1 text-slate-600 dark:text-slate-400">
          Resumen de tus finanzas personales
        </p>
      </div>
      
      <!-- Filters -->
      <div class="flex flex-col gap-4">
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
          <FunnelIcon class="w-4 h-4 text-slate-400 hidden sm:block" />
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
    
    <!-- Loading state -->
    <div v-if="loading" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
      <div v-for="i in 4" :key="i" class="card p-6 animate-pulse">
        <div class="h-4 bg-slate-200 dark:bg-slate-700 rounded w-24 mb-3"></div>
        <div class="h-8 bg-slate-200 dark:bg-slate-700 rounded w-32"></div>
      </div>
    </div>
    
    <!-- Stats Grid -->
    <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
      <StatCard
        title="Saldo total"
        :value="formatCurrency(totalBalance)"
        :icon="BanknotesIcon"
        color="primary"
      />
      <StatCard
        title="Ingresos del mes"
        :value="formatCurrency(monthIncome)"
        :icon="ArrowTrendingUpIcon"
        color="success"
      />
      <StatCard
        title="Gastos del mes"
        :value="formatCurrency(monthExpenses)"
        :icon="ArrowTrendingDownIcon"
        color="danger"
      />
      <StatCard
        title="Balance mensual"
        :value="formatCurrency(monthBalance)"
        :icon="ScaleIcon"
        :color="monthBalance >= 0 ? 'success' : 'danger'"
      />
    </div>
    
    <!-- Account Stats (only when no account filter) -->
    <div v-if="!selectedAccount && accountsStore.accounts.length > 0" class="card p-6">
      <div class="flex items-center gap-3 mb-4">
        <div class="w-10 h-10 rounded-xl bg-blue-100 dark:bg-blue-900/30 flex items-center justify-center">
          <BuildingLibraryIcon class="w-5 h-5 text-blue-600 dark:text-blue-400" />
        </div>
        <div>
          <h2 class="font-display font-semibold text-slate-900 dark:text-white">Resumen por cuenta</h2>
          <p class="text-sm text-slate-500 dark:text-slate-400">Balance de cada cuenta</p>
        </div>
      </div>
      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div 
          v-for="acc in accountsStore.accounts" 
          :key="acc.id"
          @click="selectedAccount = acc.id"
          class="p-4 rounded-xl border-2 cursor-pointer transition-all hover:shadow-md"
          :style="{ borderColor: acc.color + '40' }"
        >
          <div class="flex items-center gap-2 mb-2">
            <div 
              class="w-3 h-3 rounded-full"
              :style="{ backgroundColor: acc.color }"
            />
            <span class="text-sm font-medium text-slate-700 dark:text-slate-300 truncate">{{ acc.name }}</span>
          </div>
          <p 
            class="text-xl font-bold"
            :class="acc.balance >= 0 ? 'text-slate-900 dark:text-white' : 'text-red-600'"
          >
            {{ formatCurrency(acc.balance, acc.currency) }}
          </p>
          <p class="text-xs text-slate-500 mt-1">{{ acc.currency }}</p>
        </div>
      </div>
    </div>
    
    <!-- Monthly Trends Chart -->
    <div v-if="monthlyTrendsData && !selectedAccount && !selectedCategory" class="card p-6">
      <div class="flex items-center gap-3 mb-6">
        <div class="w-10 h-10 rounded-xl bg-indigo-100 dark:bg-indigo-900/30 flex items-center justify-center">
          <PresentationChartLineIcon class="w-5 h-5 text-indigo-600 dark:text-indigo-400" />
        </div>
        <div>
          <h2 class="font-display font-semibold text-slate-900 dark:text-white">Tendencias Mensuales</h2>
          <p class="text-sm text-slate-500 dark:text-slate-400">Ingresos vs Gastos</p>
        </div>
      </div>
      <LineChart 
        :labels="monthlyTrendsData.labels"
        :datasets="monthlyTrendsData.datasets"
        :height="300"
      />
    </div>
    
    <!-- Comparison Cards -->
    <div v-if="previousMonthComparison && !selectedAccount && !selectedCategory" class="grid grid-cols-1 md:grid-cols-2 gap-6">
      <div class="card p-6">
        <div class="flex items-center justify-between mb-4">
          <div>
            <p class="text-sm text-slate-500 dark:text-slate-400">Ingresos</p>
            <p class="text-2xl font-bold text-slate-900 dark:text-white mt-1">
              {{ formatCurrency(previousMonthComparison.income.current) }}
            </p>
          </div>
          <div 
            class="flex items-center gap-1 px-3 py-1.5 rounded-lg"
            :class="previousMonthComparison.income.isPositive ? 'bg-emerald-100 dark:bg-emerald-900/30 text-emerald-600' : 'bg-red-100 dark:bg-red-900/30 text-red-600'"
          >
            <ArrowTrendingUpIcon v-if="previousMonthComparison.income.isPositive" class="w-4 h-4" />
            <ArrowTrendingDownIcon v-else class="w-4 h-4" />
            <span class="text-sm font-semibold">
              {{ previousMonthComparison.income.isPositive ? '+' : '' }}{{ previousMonthComparison.income.change.toFixed(1) }}%
            </span>
          </div>
        </div>
        <p class="text-xs text-slate-500">Mes anterior: {{ formatCurrency(previousMonthComparison.income.previous) }}</p>
      </div>
      
      <div class="card p-6">
        <div class="flex items-center justify-between mb-4">
          <div>
            <p class="text-sm text-slate-500 dark:text-slate-400">Gastos</p>
            <p class="text-2xl font-bold text-slate-900 dark:text-white mt-1">
              {{ formatCurrency(previousMonthComparison.expenses.current) }}
            </p>
          </div>
          <div 
            class="flex items-center gap-1 px-3 py-1.5 rounded-lg"
            :class="previousMonthComparison.expenses.isPositive ? 'bg-emerald-100 dark:bg-emerald-900/30 text-emerald-600' : 'bg-red-100 dark:bg-red-900/30 text-red-600'"
          >
            <ArrowTrendingUpIcon v-if="previousMonthComparison.expenses.isPositive" class="w-4 h-4" />
            <ArrowTrendingDownIcon v-else class="w-4 h-4" />
            <span class="text-sm font-semibold">
              {{ previousMonthComparison.expenses.isPositive ? '+' : '' }}{{ previousMonthComparison.expenses.change.toFixed(1) }}%
            </span>
          </div>
        </div>
        <p class="text-xs text-slate-500">Mes anterior: {{ formatCurrency(previousMonthComparison.expenses.previous) }}</p>
      </div>
    </div>
    
    <!-- Health Metrics -->
    <div v-if="!selectedAccount && !selectedCategory" class="grid grid-cols-1 md:grid-cols-3 gap-6">
      <div class="card p-6">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-sm text-slate-500 dark:text-slate-400">Tasa de Ahorro</p>
            <p 
              class="text-2xl font-bold mt-1"
              :class="parseFloat(savingsRate) >= 0 ? 'text-emerald-600' : 'text-red-600'"
            >
              {{ savingsRate }}%
            </p>
          </div>
          <div class="w-12 h-12 rounded-xl bg-blue-100 dark:bg-blue-900/30 flex items-center justify-center">
            <ScaleIcon class="w-6 h-6 text-blue-600 dark:text-blue-400" />
          </div>
        </div>
        <p class="text-xs text-slate-500 mt-2">
          {{ monthBalance >= 0 ? 'Ahorrando' : 'Gastando más de lo que ingresas' }}
        </p>
      </div>
      
      <div class="card p-6">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-sm text-slate-500 dark:text-slate-400">Gastos Hormiga</p>
            <p class="text-2xl font-bold text-orange-600 mt-1">
              {{ antExpensesPercentage }}%
            </p>
          </div>
          <div class="w-12 h-12 rounded-xl bg-orange-100 dark:bg-orange-900/30 flex items-center justify-center">
            <BugAntIcon class="w-6 h-6 text-orange-600 dark:text-orange-400" />
          </div>
        </div>
        <p class="text-xs text-slate-500 mt-2">del total de gastos</p>
      </div>
      
      <div class="card p-6">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-sm text-slate-500 dark:text-slate-400">Proyección Anual</p>
            <p 
              class="text-2xl font-bold mt-1"
              :class="monthBalance >= 0 ? 'text-emerald-600' : 'text-red-600'"
            >
              {{ formatCurrency(monthBalance * 12) }}
            </p>
          </div>
          <div class="w-12 h-12 rounded-xl bg-purple-100 dark:bg-purple-900/30 flex items-center justify-center">
            <ArrowTrendingUpIcon class="w-6 h-6 text-purple-600 dark:text-purple-400" />
          </div>
        </div>
        <p class="text-xs text-slate-500 mt-2">Basado en el mes actual</p>
      </div>
    </div>
    
    <!-- Top 5 Categories -->
    <div v-if="topCategories.length > 0" class="card p-6">
      <div class="flex items-center gap-3 mb-6">
        <div class="w-10 h-10 rounded-xl bg-rose-100 dark:bg-rose-900/30 flex items-center justify-center">
          <ChartPieIcon class="w-5 h-5 text-rose-600 dark:text-rose-400" />
        </div>
        <div>
          <h2 class="font-display font-semibold text-slate-900 dark:text-white">Top 5 Categorías</h2>
          <p class="text-sm text-slate-500 dark:text-slate-400">Categorías con más gastos</p>
        </div>
      </div>
      <div class="space-y-3">
        <div 
          v-for="(cat, index) in topCategories" 
          :key="index"
          class="flex items-center gap-4"
        >
          <div class="flex items-center gap-3 flex-1">
            <div class="w-8 h-8 rounded-lg flex items-center justify-center text-white font-bold text-sm" :style="{ backgroundColor: cat.color }">
              {{ index + 1 }}
            </div>
            <div class="flex-1">
              <p class="font-medium text-slate-900 dark:text-white">{{ cat.name }}</p>
              <div class="flex items-center gap-2 mt-1">
                <div class="flex-1 h-2 bg-slate-200 dark:bg-slate-700 rounded-full overflow-hidden">
                  <div 
                    class="h-full rounded-full transition-all"
                    :style="{ 
                      width: `${cat.percentage}%`,
                      backgroundColor: cat.color
                    }"
                  ></div>
                </div>
                <span class="text-xs text-slate-500 w-12 text-right">{{ cat.percentage }}%</span>
              </div>
            </div>
          </div>
          <div class="text-right">
            <p class="font-bold text-slate-900 dark:text-white">{{ formatCurrency(cat.total) }}</p>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Daily Expenses Chart -->
    <div v-if="dailyExpensesData && !selectedAccount && !selectedCategory" class="card p-6">
      <div class="flex items-center gap-3 mb-6">
        <div class="w-10 h-10 rounded-xl bg-cyan-100 dark:bg-cyan-900/30 flex items-center justify-center">
          <PresentationChartLineIcon class="w-5 h-5 text-cyan-600 dark:text-cyan-400" />
        </div>
        <div>
          <h2 class="font-display font-semibold text-slate-900 dark:text-white">Gastos Diarios</h2>
          <p class="text-sm text-slate-500 dark:text-slate-400">Distribución de gastos por día</p>
        </div>
      </div>
      <BarChart 
        :labels="dailyExpensesData.labels"
        :data="dailyExpensesData.data"
        :height="250"
      />
    </div>
    
    <!-- Main Grid -->
    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <!-- Expense Chart -->
      <div class="lg:col-span-2 card p-6">
        <div class="flex items-center gap-3 mb-6">
          <div class="w-10 h-10 rounded-xl bg-violet-100 dark:bg-violet-900/30 flex items-center justify-center">
            <ChartPieIcon class="w-5 h-5 text-violet-600 dark:text-violet-400" />
          </div>
          <div>
            <h2 class="font-display font-semibold text-slate-900 dark:text-white">Gastos por categoría</h2>
            <p class="text-sm text-slate-500 dark:text-slate-400">Este mes</p>
          </div>
        </div>
        <ExpenseChart :data="filteredExpensesByCategory" />
      </div>
      
      <!-- Budget Alerts -->
      <div class="card p-6">
        <div class="flex items-center gap-3 mb-6">
          <div class="w-10 h-10 rounded-xl bg-amber-100 dark:bg-amber-900/30 flex items-center justify-center">
            <PresentationChartLineIcon class="w-5 h-5 text-amber-600 dark:text-amber-400" />
          </div>
          <div>
            <h2 class="font-display font-semibold text-slate-900 dark:text-white">Presupuestos</h2>
            <p class="text-sm text-slate-500 dark:text-slate-400">Alertas activas</p>
          </div>
        </div>
        <BudgetAlerts :alerts="dashboardData?.budget_alerts || []" />
      </div>
      
      <!-- Goals Widget -->
      <div class="card p-6">
        <div class="flex items-center justify-between mb-6">
          <div class="flex items-center gap-3">
            <div class="w-10 h-10 rounded-xl bg-emerald-100 dark:bg-emerald-900/30 flex items-center justify-center">
              <FlagIcon class="w-5 h-5 text-emerald-600 dark:text-emerald-400" />
            </div>
            <div>
              <h2 class="font-display font-semibold text-slate-900 dark:text-white">Metas Activas</h2>
              <p class="text-sm text-slate-500 dark:text-slate-400">Progreso de objetivos</p>
            </div>
          </div>
          <router-link to="/goals" class="text-sm text-primary-600 dark:text-primary-400 font-medium hover:underline">
            Ver todas
          </router-link>
        </div>
        <div v-if="goalsStore.loading" class="text-center py-8">
          <div class="inline-block animate-spin rounded-full h-6 w-6 border-b-2 border-primary-600"></div>
        </div>
        <div v-else-if="goalsStore.activeGoals.length === 0" class="text-center py-8 text-slate-500 dark:text-slate-400">
          <p class="text-sm">No hay metas activas</p>
          <router-link to="/goals" class="text-sm text-primary-600 dark:text-primary-400 hover:underline mt-2 inline-block">
            Crear una meta
          </router-link>
        </div>
        <div v-else class="space-y-4">
          <div
            v-for="goal in goalsStore.activeGoals.slice(0, 3)"
            :key="goal.id"
            class="p-4 rounded-lg bg-slate-50 dark:bg-slate-800/50 hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors cursor-pointer"
            @click="$router.push('/goals')"
          >
            <div class="flex items-center justify-between mb-2">
              <h3 class="font-medium text-slate-900 dark:text-white text-sm truncate">
                {{ goal.name }}
              </h3>
              <span class="text-xs font-semibold" :class="goal.is_completed ? 'text-emerald-600 dark:text-emerald-400' : 'text-slate-500 dark:text-slate-400'">
                {{ goal.progress_percentage.toFixed(0) }}%
              </span>
            </div>
            <div class="w-full bg-slate-200 dark:bg-slate-700 rounded-full h-2 overflow-hidden">
              <div
                class="h-full transition-all duration-500 ease-out rounded-full"
                :class="goal.is_completed ? 'bg-emerald-500' : goal.progress_percentage >= 75 ? 'bg-emerald-500' : goal.progress_percentage >= 50 ? 'bg-amber-500' : 'bg-red-500'"
                :style="{ width: `${Math.min(100, goal.progress_percentage)}%` }"
              />
            </div>
            <div class="flex items-center justify-between mt-2 text-xs text-slate-500 dark:text-slate-400">
              <span>{{ formatCurrency(goal.current_amount) }} / {{ formatCurrency(goal.target_amount) }}</span>
              <span v-if="goal.days_remaining > 0">{{ goal.days_remaining }} días restantes</span>
              <span v-else-if="!goal.is_completed" class="text-red-600 dark:text-red-400">Vencida</span>
              <span v-else class="text-emerald-600 dark:text-emerald-400">Completada</span>
            </div>
          </div>
          <router-link
            v-if="goalsStore.activeGoals.length > 3"
            to="/goals"
            class="block text-center text-sm text-primary-600 dark:text-primary-400 hover:underline pt-2"
          >
            Ver {{ goalsStore.activeGoals.length - 3 }} más
          </router-link>
        </div>
      </div>
    </div>
    
    <!-- Recent Transactions -->
    <div class="card p-6">
      <div class="flex items-center justify-between mb-6">
        <div class="flex items-center gap-3">
          <div class="w-10 h-10 rounded-xl bg-primary-100 dark:bg-primary-900/30 flex items-center justify-center">
            <BanknotesIcon class="w-5 h-5 text-primary-600 dark:text-primary-400" />
          </div>
          <div>
            <h2 class="font-display font-semibold text-slate-900 dark:text-white">Últimas transacciones</h2>
            <p class="text-sm text-slate-500 dark:text-slate-400">Movimientos recientes</p>
          </div>
        </div>
        <router-link to="/transactions" class="text-sm text-primary-600 dark:text-primary-400 font-medium hover:underline">
          Ver todas
        </router-link>
      </div>
      <TransactionList :transactions="dashboardData?.recent_transactions || []" compact />
    </div>
    
    <!-- Charts Grid -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <!-- Ant Expenses Chart -->
      <div class="card p-6">
        <div class="flex items-center gap-3 mb-6">
          <div class="w-10 h-10 rounded-xl bg-orange-100 dark:bg-orange-900/30 flex items-center justify-center">
            <BugAntIcon class="w-5 h-5 text-orange-600 dark:text-orange-400" />
          </div>
          <div>
            <h2 class="font-display font-semibold text-slate-900 dark:text-white">Gastos hormiga vs normales</h2>
            <p class="text-sm text-slate-500 dark:text-slate-400">Este mes</p>
          </div>
        </div>
        <div class="relative h-64 w-full">
          <Doughnut v-if="antExpensesChartData" :data="antExpensesChartData" :options="antExpensesChartOptions" />
          <div v-else class="h-full flex items-center justify-center text-slate-400">
            Sin datos
          </div>
          <div v-if="antExpensesChartData" class="absolute inset-0 flex flex-col items-center justify-center pointer-events-none">
            <p class="text-sm text-slate-500 dark:text-slate-400">Total</p>
            <p class="text-xl font-bold text-slate-900 dark:text-white">{{ formatCurrency(totalAntExpenses) }}</p>
          </div>
        </div>
        <div v-if="antExpensesChartData" class="mt-4 flex justify-center gap-6">
          <div class="flex items-center gap-2">
            <div class="w-3 h-3 rounded-full bg-orange-500"></div>
            <span class="text-sm text-slate-600 dark:text-slate-400">Hormiga</span>
          </div>
          <div class="flex items-center gap-2">
            <div class="w-3 h-3 rounded-full bg-indigo-500"></div>
            <span class="text-sm text-slate-600 dark:text-slate-400">Normal</span>
          </div>
        </div>
      </div>
      
      <!-- Expenses by Account Chart -->
      <div class="card p-6">
        <div class="flex items-center gap-3 mb-6">
          <div class="w-10 h-10 rounded-xl bg-blue-100 dark:bg-blue-900/30 flex items-center justify-center">
            <BuildingLibraryIcon class="w-5 h-5 text-blue-600 dark:text-blue-400" />
          </div>
          <div>
            <h2 class="font-display font-semibold text-slate-900 dark:text-white">Gastos por cuenta</h2>
            <p class="text-sm text-slate-500 dark:text-slate-400">Este mes</p>
          </div>
        </div>
        <div class="relative h-64 w-full">
          <Doughnut v-if="expensesByAccountChartData" :data="expensesByAccountChartData" :options="expensesByAccountChartOptions" />
          <div v-else class="h-full flex items-center justify-center text-slate-400">
            Sin datos
          </div>
          <div v-if="expensesByAccountChartData" class="absolute inset-0 flex flex-col items-center justify-center pointer-events-none">
            <p class="text-sm text-slate-500 dark:text-slate-400">Total</p>
            <p class="text-xl font-bold text-slate-900 dark:text-white">{{ formatCurrency(totalExpensesByAccount) }}</p>
          </div>
        </div>
        <div v-if="expensesByAccountChartData && dashboardData?.expenses_by_account" class="mt-4 space-y-2 max-h-32 overflow-y-auto">
          <div 
            v-for="item in dashboardData.expenses_by_account" 
            :key="item.account__id"
            class="flex items-center justify-between text-sm"
          >
            <div class="flex items-center gap-2">
              <div class="w-3 h-3 rounded-full" :style="{ backgroundColor: item.account__color || '#6366f1' }"></div>
              <span class="text-slate-600 dark:text-slate-400">{{ item.account__name }}</span>
            </div>
            <span class="font-semibold text-slate-900 dark:text-white">{{ formatCurrency(item.total) }}</span>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Ant Expenses Section -->
    <div v-if="antExpensesData" class="card p-6 border-l-4 border-orange-500">
      <div class="flex items-center gap-3 mb-4">
        <div class="w-10 h-10 rounded-xl bg-orange-100 dark:bg-orange-900/30 flex items-center justify-center">
          <BugAntIcon class="w-5 h-5 text-orange-600 dark:text-orange-400" />
        </div>
        <div>
          <h2 class="font-display font-semibold text-slate-900 dark:text-white">Gastos Hormiga</h2>
          <p class="text-sm text-slate-500 dark:text-slate-400">Pequeños gastos que suman</p>
        </div>
      </div>
      
      <div class="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-4">
        <div class="bg-orange-50 dark:bg-orange-900/20 rounded-xl p-4">
          <p class="text-sm text-orange-600 dark:text-orange-400">Este mes</p>
          <p class="text-2xl font-bold text-orange-700 dark:text-orange-300">
            {{ formatCurrency(antExpensesData.current_month_total) }}
          </p>
          <p class="text-xs text-orange-500">{{ antExpensesData.current_month_count }} gastos</p>
        </div>
        <div class="bg-slate-50 dark:bg-slate-800 rounded-xl p-4">
          <p class="text-sm text-slate-500">Mes anterior</p>
          <p class="text-2xl font-bold text-slate-700 dark:text-slate-300">
            {{ formatCurrency(antExpensesData.previous_month_total) }}
          </p>
        </div>
        <div class="bg-slate-50 dark:bg-slate-800 rounded-xl p-4">
          <p class="text-sm text-slate-500">Diferencia</p>
          <p 
            class="text-2xl font-bold"
            :class="antExpensesData.current_month_total <= antExpensesData.previous_month_total ? 'text-emerald-600' : 'text-red-600'"
          >
            {{ formatCurrency(antExpensesData.current_month_total - antExpensesData.previous_month_total) }}
          </p>
        </div>
      </div>
      
      <div v-if="antExpensesData.recent_ant_expenses?.length" class="mt-4">
        <p class="text-sm font-medium text-slate-600 dark:text-slate-400 mb-2">Recientes:</p>
        <div class="space-y-2">
          <div 
            v-for="expense in antExpensesData.recent_ant_expenses.slice(0, 3)" 
            :key="expense.id"
            class="flex items-center justify-between py-2 border-b border-slate-100 dark:border-slate-800 last:border-0"
          >
            <div class="flex items-center gap-2">
              <BugAntIcon class="w-4 h-4 text-orange-500" />
              <span class="text-sm text-slate-700 dark:text-slate-300">{{ expense.description || 'Sin descripción' }}</span>
            </div>
            <span class="text-sm font-medium text-red-600">-{{ formatCurrency(expense.amount) }}</span>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Quick Stats -->
    <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
      <div class="card p-6">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-sm text-slate-500 dark:text-slate-400">Inversiones</p>
            <p class="text-2xl font-bold text-slate-900 dark:text-white mt-1">
              {{ formatCurrency(dashboardData?.investments_total || 0) }}
            </p>
          </div>
          <div class="w-12 h-12 rounded-xl bg-emerald-100 dark:bg-emerald-900/30 flex items-center justify-center">
            <ArrowTrendingUpIcon class="w-6 h-6 text-emerald-600 dark:text-emerald-400" />
          </div>
        </div>
        <router-link to="/investments" class="mt-4 text-sm text-primary-600 dark:text-primary-400 font-medium hover:underline inline-block">
          Ver inversiones →
        </router-link>
      </div>
      
      <div class="card p-6">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-sm text-slate-500 dark:text-slate-400">Deudas pendientes</p>
            <p class="text-2xl font-bold text-slate-900 dark:text-white mt-1">
              {{ formatCurrency(dashboardData?.debts_remaining || 0) }}
            </p>
          </div>
          <div class="w-12 h-12 rounded-xl bg-red-100 dark:bg-red-900/30 flex items-center justify-center">
            <ScaleIcon class="w-6 h-6 text-red-600 dark:text-red-400" />
          </div>
        </div>
        <router-link to="/debts" class="mt-4 text-sm text-primary-600 dark:text-primary-400 font-medium hover:underline inline-block">
          Ver deudas →
        </router-link>
      </div>
    </div>
  </div>
</template>

