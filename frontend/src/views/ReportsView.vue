<script setup>
import { ref, onMounted, computed, watch } from 'vue'
import { useUiStore } from '@/stores/ui'
import api from '@/services/api'
import { formatMoney } from '@/composables/useCurrency'
import { Line, Doughnut, Bar } from 'vue-chartjs'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  ArcElement,
  Title,
  Tooltip,
  Legend,
  Filler
} from 'chart.js'
import { 
  ChartBarIcon, 
  ArrowDownTrayIcon,
  CalendarIcon,
  ChevronDownIcon,
  ChevronRightIcon
} from '@heroicons/vue/24/outline'

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  ArcElement,
  Title,
  Tooltip,
  Legend,
  Filler
)

const uiStore = useUiStore()

const reportData = ref(null)
const loading = ref(true)
const period = ref('month')
const exporting = ref(false)
const expandedCategories = ref(new Set())

const periods = [
  { value: 'week', label: 'Semana' },
  { value: 'month', label: 'Mes' },
  { value: 'year', label: 'Año' },
]

async function fetchReport() {
  loading.value = true
  try {
    const response = await api.get('/reports/', { params: { period: period.value } })
    reportData.value = response.data
  } catch (error) {
    uiStore.showError('Error al cargar reportes')
  } finally {
    loading.value = false
  }
}

function formatCurrency(value) {
  return formatMoney(value)
}

const groupedCategories = computed(() => {
  if (!reportData.value?.by_category?.length) return []
  
  const groups = new Map()
  
  reportData.value.by_category.forEach(item => {
    const hasParent = item.category__parent_id !== null && item.category__parent_id !== undefined
    
    if (hasParent) {
      const parentId = item.category__parent_id
      const parentName = item.category__parent__name || 'Sin categoría'
      const parentColor = item.category__parent__color || '#6366f1'
      
      if (!groups.has(parentId)) {
        groups.set(parentId, {
          id: parentId,
          name: parentName,
          color: parentColor,
          total: 0,
          count: 0,
          subcategories: []
        })
      }
      
      const group = groups.get(parentId)
      group.total += parseFloat(item.total || 0)
      group.count += item.count || 0
      group.subcategories.push({
        id: item.category__id,
        name: item.category__name,
        color: item.category__color || '#6366f1',
        total: parseFloat(item.total || 0),
        count: item.count || 0
      })
    } else {
      const catId = item.category__id
      
      if (groups.has(catId)) {
        const group = groups.get(catId)
        group.total += parseFloat(item.total || 0)
        group.count += item.count || 0
        group.hasDirectExpenses = true
      } else {
        groups.set(catId, {
          id: catId,
          name: item.category__name || 'Sin categoría',
          color: item.category__color || '#6366f1',
          total: parseFloat(item.total || 0),
          count: item.count || 0,
          subcategories: [],
          hasDirectExpenses: true
        })
      }
    }
  })
  
  return Array.from(groups.values()).sort((a, b) => b.total - a.total)
})

const totalExpenses = computed(() => {
  return groupedCategories.value.reduce((sum, cat) => sum + cat.total, 0)
})

function getPercentage(value) {
  if (totalExpenses.value === 0) return 0
  return ((value / totalExpenses.value) * 100).toFixed(1)
}

const lineChartData = computed(() => {
  if (!reportData.value) return null
  
  const income = reportData.value.income_over_time || []
  const expenses = reportData.value.expenses_over_time || []
  
  const allDates = [...new Set([
    ...income.map(i => i.period),
    ...expenses.map(e => e.period)
  ])].sort()
  
  return {
    labels: allDates.map(d => new Date(d).toLocaleDateString('es-ES', { month: 'short', day: 'numeric' })),
    datasets: [
      {
        label: 'Ingresos',
        data: allDates.map(d => {
          const item = income.find(i => i.period === d)
          return item ? parseFloat(item.total) : 0
        }),
        borderColor: '#22c55e',
        backgroundColor: 'rgba(34, 197, 94, 0.1)',
        fill: true,
        tension: 0.4,
      },
      {
        label: 'Gastos',
        data: allDates.map(d => {
          const item = expenses.find(e => e.period === d)
          return item ? parseFloat(item.total) : 0
        }),
        borderColor: '#ef4444',
        backgroundColor: 'rgba(239, 68, 68, 0.1)',
        fill: true,
        tension: 0.4,
      }
    ]
  }
})

const doughnutChartData = computed(() => {
  if (groupedCategories.value.length === 0) return null
  
  return {
    labels: groupedCategories.value.map(c => c.name),
    datasets: [{
      data: groupedCategories.value.map(c => c.total),
      backgroundColor: groupedCategories.value.map(c => c.color),
      borderWidth: 0,
      hoverOffset: 8,
    }]
  }
})

const chartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      position: 'bottom',
    },
    tooltip: {
      backgroundColor: '#1e293b',
      padding: 12,
      cornerRadius: 8,
      callbacks: {
        label: function(context) {
          return formatCurrency(context.parsed.y || context.parsed)
        }
      }
    }
  },
  scales: {
    y: {
      beginAtZero: true,
      ticks: {
        callback: function(value) {
          return formatCurrency(value)
        }
      }
    }
  }
}

const doughnutOptions = computed(() => ({
  responsive: true,
  maintainAspectRatio: false,
  cutout: '60%',
  plugins: {
    legend: {
      display: false,
    },
    tooltip: {
      backgroundColor: '#1e293b',
      padding: 12,
      cornerRadius: 8,
      callbacks: {
        title: function(context) {
          const index = context[0].dataIndex
          const category = groupedCategories.value[index]
          return category?.name || 'Sin categoría'
        },
        label: function(context) {
          return formatCurrency(context.parsed)
        },
        afterLabel: function(context) {
          const index = context.dataIndex
          const category = groupedCategories.value[index]
          if (category?.subcategories?.length > 0) {
            return `(${category.subcategories.length} subcategorías)`
          }
          return ''
        }
      }
    }
  }
}))

async function exportData(format) {
  exporting.value = true
  try {
    const token = localStorage.getItem('access_token')
    const baseURL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api'
    
    const response = await fetch(`${baseURL}/reports/exportar/?format=${format}`, {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${token}`
      }
    })
    
    if (!response.ok) throw new Error('Error en la exportación')
    
    const blob = await response.blob()
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.setAttribute('download', `transacciones.${format === 'excel' ? 'xlsx' : 'csv'}`)
    document.body.appendChild(link)
    link.click()
    link.remove()
    window.URL.revokeObjectURL(url)
    
    uiStore.showSuccess('Exportación completada')
  } catch (error) {
    console.error('Export error:', error)
    uiStore.showError('Error al exportar')
  } finally {
    exporting.value = false
  }
}

function toggleCategory(categoryId) {
  if (expandedCategories.value.has(categoryId)) {
    expandedCategories.value.delete(categoryId)
  } else {
    expandedCategories.value.add(categoryId)
  }
}

function isExpanded(categoryId) {
  return expandedCategories.value.has(categoryId)
}

function hasSubcategories(category) {
  return category.subcategories && category.subcategories.length > 0
}

watch(period, fetchReport)
onMounted(fetchReport)
</script>

<template>
  <div class="space-y-6 animate-fade-in">
    <!-- Header -->
    <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
      <div>
        <h1 class="font-display text-2xl lg:text-3xl font-bold text-slate-900 dark:text-white">
          Reportes
        </h1>
        <p class="mt-1 text-slate-600 dark:text-slate-400">
          Analiza tus finanzas con gráficos detallados
        </p>
      </div>
      
      <div class="flex items-center gap-3">
        <!-- Period Selector -->
        <div class="flex items-center gap-2 bg-slate-100 dark:bg-slate-800 rounded-xl p-1">
          <button
            v-for="p in periods"
            :key="p.value"
            @click="period = p.value"
            :class="[
              'px-4 py-2 rounded-lg text-sm font-medium transition-all',
              period === p.value
                ? 'bg-white dark:bg-slate-700 shadow text-slate-900 dark:text-white'
                : 'text-slate-600 dark:text-slate-400 hover:text-slate-900'
            ]"
          >
            {{ p.label }}
          </button>
        </div>
        
        <!-- Export -->
        <div class="relative group">
          <button class="btn-secondary" :disabled="exporting">
            <ArrowDownTrayIcon class="w-5 h-5" />
            Exportar
          </button>
          <div class="absolute right-0 top-full mt-2 py-2 bg-white dark:bg-slate-800 rounded-xl shadow-lg border border-slate-200 dark:border-slate-700 opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all z-10">
            <button
              @click="exportData('csv')"
              class="w-full px-4 py-2 text-left text-sm hover:bg-slate-100 dark:hover:bg-slate-700"
            >
              Exportar CSV
            </button>
            <button
              @click="exportData('excel')"
              class="w-full px-4 py-2 text-left text-sm hover:bg-slate-100 dark:hover:bg-slate-700"
            >
              Exportar Excel
            </button>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Summary Cards -->
    <div v-if="reportData" class="grid grid-cols-1 md:grid-cols-4 gap-6">
      <div class="card p-6">
        <p class="text-sm text-slate-500 dark:text-slate-400">Ingresos</p>
        <p class="text-2xl font-bold text-emerald-600 mt-1">
          {{ formatCurrency(reportData.totals?.income || 0) }}
        </p>
      </div>
      <div class="card p-6">
        <p class="text-sm text-slate-500 dark:text-slate-400">Gastos</p>
        <p class="text-2xl font-bold text-red-600 mt-1">
          {{ formatCurrency(reportData.totals?.expenses || 0) }}
        </p>
      </div>
      <div class="card p-6">
        <p class="text-sm text-slate-500 dark:text-slate-400">Transferencias</p>
        <p class="text-2xl font-bold text-blue-600 mt-1">
          {{ formatCurrency(reportData.totals?.transfers || 0) }}
        </p>
      </div>
      <div class="card p-6">
        <p class="text-sm text-slate-500 dark:text-slate-400">Balance</p>
        <p 
          class="text-2xl font-bold mt-1"
          :class="reportData.totals?.balance >= 0 ? 'text-emerald-600' : 'text-red-600'"
        >
          {{ formatCurrency(reportData.totals?.balance || 0) }}
        </p>
      </div>
    </div>
    
    <!-- Charts -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <!-- Line Chart -->
      <div class="card p-6">
        <h3 class="font-display font-semibold text-slate-900 dark:text-white mb-4">
          Evolución de ingresos y gastos
        </h3>
        <div class="h-80">
          <Line v-if="lineChartData" :data="lineChartData" :options="chartOptions" />
          <div v-else class="h-full flex items-center justify-center text-slate-400">
            Sin datos suficientes
          </div>
        </div>
      </div>
      
      <!-- Doughnut Chart with Custom Legend -->
      <div class="card p-6">
        <h3 class="font-display font-semibold text-slate-900 dark:text-white mb-4">
          Gastos por categoría
        </h3>
        <div class="flex flex-col lg:flex-row gap-6">
          <!-- Chart -->
          <div class="h-64 w-full lg:w-56 flex-shrink-0">
            <Doughnut v-if="doughnutChartData" :data="doughnutChartData" :options="doughnutOptions" />
            <div v-else class="h-full flex items-center justify-center text-slate-400">
              Sin gastos
            </div>
          </div>
          
          <!-- Custom Legend -->
          <div class="flex-1 space-y-1 max-h-64 overflow-y-auto">
            <template v-for="category in groupedCategories" :key="category.id">
              <div 
                class="flex items-center gap-2 p-2 rounded-lg transition-colors"
                :class="[
                  hasSubcategories(category) 
                    ? 'cursor-pointer hover:bg-slate-100 dark:hover:bg-slate-800' 
                    : 'hover:bg-slate-50 dark:hover:bg-slate-800/50'
                ]"
                @click="hasSubcategories(category) && toggleCategory(category.id)"
              >
                <div class="w-4 h-4 flex items-center justify-center flex-shrink-0">
                  <template v-if="hasSubcategories(category)">
                    <ChevronDownIcon v-if="isExpanded(category.id)" class="w-3.5 h-3.5 text-slate-400" />
                    <ChevronRightIcon v-else class="w-3.5 h-3.5 text-slate-400" />
                  </template>
                </div>
                <div 
                  class="w-3 h-3 rounded-full flex-shrink-0"
                  :style="{ backgroundColor: category.color }"
                />
                <span class="flex-1 text-sm text-slate-700 dark:text-slate-300 truncate font-medium">
                  {{ category.name }}
                </span>
                <span 
                  v-if="hasSubcategories(category)"
                  class="text-xs px-1.5 py-0.5 rounded-full bg-slate-100 dark:bg-slate-700 text-slate-500"
                >
                  {{ category.subcategories.length }}
                </span>
                <span class="text-xs text-slate-400 w-10 text-right">{{ getPercentage(category.total) }}%</span>
                <span class="text-sm font-semibold text-slate-900 dark:text-white min-w-[70px] text-right">
                  {{ formatCurrency(category.total) }}
                </span>
              </div>
              
              <!-- Subcategories -->
              <div 
                v-if="hasSubcategories(category) && isExpanded(category.id)"
                class="ml-4 pl-2 border-l-2 border-slate-200 dark:border-slate-700 space-y-0.5"
              >
                <div 
                  v-for="sub in category.subcategories" 
                  :key="sub.id"
                  class="flex items-center gap-2 py-1.5 px-2 rounded-lg hover:bg-slate-50 dark:hover:bg-slate-800/50"
                >
                  <div 
                    class="w-2 h-2 rounded-full flex-shrink-0"
                    :style="{ backgroundColor: sub.color }"
                  />
                  <span 
                    class="flex-1 text-sm text-slate-600 dark:text-slate-400 truncate"
                    :title="`${category.name} > ${sub.name}`"
                  >
                    {{ sub.name }}
                  </span>
                  <span class="text-xs text-slate-400 w-10 text-right">{{ getPercentage(sub.total) }}%</span>
                  <span class="text-sm text-slate-600 dark:text-slate-400 min-w-[70px] text-right">
                    {{ formatCurrency(sub.total) }}
                  </span>
                </div>
              </div>
            </template>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Category Breakdown -->
    <div v-if="groupedCategories.length" class="card p-6">
      <h3 class="font-display font-semibold text-slate-900 dark:text-white mb-4">
        Desglose por categoría
      </h3>
      <div class="space-y-2">
        <template v-for="cat in groupedCategories" :key="cat.id">
          <!-- Parent Category Row -->
          <div
            class="flex items-center gap-4 p-3 rounded-lg transition-colors"
            :class="[
              hasSubcategories(cat) 
                ? 'cursor-pointer hover:bg-slate-100 dark:hover:bg-slate-800' 
                : 'hover:bg-slate-50 dark:hover:bg-slate-800/50'
            ]"
            @click="hasSubcategories(cat) && toggleCategory(cat.id)"
          >
            <div class="w-5 h-5 flex items-center justify-center flex-shrink-0">
              <template v-if="hasSubcategories(cat)">
                <ChevronDownIcon v-if="isExpanded(cat.id)" class="w-4 h-4 text-slate-400" />
                <ChevronRightIcon v-else class="w-4 h-4 text-slate-400" />
              </template>
            </div>
            <div 
              class="w-3 h-3 rounded-full flex-shrink-0"
              :style="{ backgroundColor: cat.color }"
            />
            <span class="flex-1 text-slate-700 dark:text-slate-300 font-medium">
              {{ cat.name }}
            </span>
            <span 
              v-if="hasSubcategories(cat)"
              class="text-xs px-2 py-0.5 rounded-full bg-slate-100 dark:bg-slate-700 text-slate-500"
            >
              {{ cat.subcategories.length }} subcategorías
            </span>
            <span class="text-sm text-slate-500 w-28 text-right">
              {{ cat.count }} transacciones
            </span>
            <span class="text-xs text-slate-400 w-12 text-right">
              {{ getPercentage(cat.total) }}%
            </span>
            <span class="font-semibold text-slate-900 dark:text-white w-28 text-right">
              {{ formatCurrency(cat.total) }}
            </span>
          </div>
          
          <!-- Subcategories Breakdown -->
          <div 
            v-if="hasSubcategories(cat) && isExpanded(cat.id)"
            class="ml-6 pl-4 border-l-2 border-slate-200 dark:border-slate-700 space-y-1"
          >
            <div 
              v-for="sub in cat.subcategories" 
              :key="sub.id"
              class="flex items-center gap-4 py-2 px-3 rounded-lg hover:bg-slate-50 dark:hover:bg-slate-800/50"
            >
              <div 
                class="w-2.5 h-2.5 rounded-full flex-shrink-0"
                :style="{ backgroundColor: sub.color }"
              />
              <span 
                class="flex-1 text-slate-600 dark:text-slate-400"
                :title="`${cat.name} > ${sub.name}`"
              >
                {{ sub.name }}
              </span>
              <span class="text-sm text-slate-500 w-28 text-right">
                {{ sub.count }} transacciones
              </span>
              <span class="text-xs text-slate-400 w-12 text-right">
                {{ getPercentage(sub.total) }}%
              </span>
              <span class="text-slate-700 dark:text-slate-300 w-28 text-right">
                {{ formatCurrency(sub.total) }}
              </span>
            </div>
          </div>
        </template>
      </div>
    </div>
    
    <!-- Loading State -->
    <div v-if="loading" class="text-center py-12">
      <div class="animate-spin w-8 h-8 border-4 border-primary-600 border-t-transparent rounded-full mx-auto"></div>
      <p class="mt-4 text-slate-500">Cargando reportes...</p>
    </div>
  </div>
</template>
