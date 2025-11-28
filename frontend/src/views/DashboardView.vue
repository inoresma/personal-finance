<script setup>
import { ref, onMounted, computed, watch } from 'vue'
import { useAccountsStore } from '@/stores/accounts'
import { useCategoriesStore } from '@/stores/categories'
import api from '@/services/api'
import { formatMoney } from '@/composables/useCurrency'
import StatCard from '@/components/StatCard.vue'
import TransactionList from '@/components/TransactionList.vue'
import ExpenseChart from '@/components/ExpenseChart.vue'
import BudgetAlerts from '@/components/BudgetAlerts.vue'
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
} from '@heroicons/vue/24/outline'

const accountsStore = useAccountsStore()
const categoriesStore = useCategoriesStore()

const dashboardData = ref(null)
const antExpensesData = ref(null)
const accountStats = ref([])
const loading = ref(true)

const selectedAccount = ref(null)
const selectedCategory = ref(null)

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

async function fetchDashboard() {
  loading.value = true
  try {
    const params = {}
    if (selectedAccount.value) params.account = selectedAccount.value
    if (selectedCategory.value) params.category = selectedCategory.value
    
    const [dashRes, antRes] = await Promise.all([
      api.get('/reports/dashboard/', { params }),
      api.get('/transactions/ant_expenses/', { params })
    ])
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
}

watch([selectedAccount, selectedCategory], () => {
  fetchDashboard()
})

onMounted(async () => {
  await accountsStore.fetchAccounts()
  await categoriesStore.fetchCategories()
  fetchDashboard()
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
        <button 
          v-if="selectedAccount || selectedCategory" 
          @click="clearFilters" 
          class="text-sm text-primary-600 hover:underline"
        >
          Limpiar
        </button>
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

