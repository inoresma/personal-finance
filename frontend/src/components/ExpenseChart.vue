<script setup>
import { computed, ref } from 'vue'
import { Doughnut } from 'vue-chartjs'
import {
  Chart as ChartJS,
  ArcElement,
  Tooltip,
  Legend,
} from 'chart.js'
import { formatMoney } from '@/composables/useCurrency'
import { ChevronDownIcon, ChevronRightIcon } from '@heroicons/vue/24/outline'

ChartJS.register(ArcElement, Tooltip, Legend)

const props = defineProps({
  data: {
    type: Array,
    default: () => []
  }
})

const expandedCategories = ref(new Set())

const groupedData = computed(() => {
  if (!props.data || props.data.length === 0) return []
  
  const groups = new Map()
  
  props.data.forEach(item => {
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
          subcategories: []
        })
      }
      
      const group = groups.get(parentId)
      group.total += parseFloat(item.total || 0)
      group.subcategories.push({
        id: item.category__id,
        name: item.category__name,
        color: item.category__color || '#6366f1',
        total: parseFloat(item.total || 0)
      })
    } else {
      const catId = item.category__id
      
      if (groups.has(catId)) {
        const group = groups.get(catId)
        group.total += parseFloat(item.total || 0)
        group.hasDirectExpenses = true
        group.directTotal = (group.directTotal || 0) + parseFloat(item.total || 0)
      } else {
        groups.set(catId, {
          id: catId,
          name: item.category__name || 'Sin categoría',
          color: item.category__color || '#6366f1',
          total: parseFloat(item.total || 0),
          subcategories: [],
          hasDirectExpenses: true,
          directTotal: parseFloat(item.total || 0)
        })
      }
    }
  })
  
  return Array.from(groups.values()).sort((a, b) => b.total - a.total)
})

const chartData = computed(() => {
  if (groupedData.value.length === 0) {
    return {
      labels: ['Sin datos'],
      datasets: [{
        data: [1],
        backgroundColor: ['#e2e8f0'],
        borderWidth: 0,
      }]
    }
  }
  
  return {
    labels: groupedData.value.map(item => item.name),
    datasets: [{
      data: groupedData.value.map(item => item.total),
      backgroundColor: groupedData.value.map(item => item.color),
      borderWidth: 0,
      hoverOffset: 8,
    }]
  }
})

const chartOptions = computed(() => ({
  responsive: true,
  maintainAspectRatio: false,
  cutout: '70%',
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
        title: function(context) {
          const index = context[0].dataIndex
          const category = groupedData.value[index]
          return category?.name || 'Sin categoría'
        },
        label: function(context) {
          const value = context.parsed || 0
          return formatMoney(value)
        },
        afterLabel: function(context) {
          const index = context.dataIndex
          const category = groupedData.value[index]
          if (category?.subcategories?.length > 0) {
            return `(${category.subcategories.length} subcategorías)`
          }
          return ''
        }
      }
    }
  }
}))

const total = computed(() => {
  return groupedData.value.reduce((sum, item) => sum + item.total, 0)
})

function formatCurrency(value) {
  return formatMoney(value)
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

function getPercentage(value) {
  if (total.value === 0) return 0
  return ((value / total.value) * 100).toFixed(1)
}
</script>

<template>
  <div class="flex flex-col lg:flex-row gap-6">
    <!-- Chart -->
    <div class="relative w-full lg:w-64 h-64 mx-auto flex-shrink-0">
      <Doughnut :data="chartData" :options="chartOptions" />
      <div class="absolute inset-0 flex flex-col items-center justify-center pointer-events-none">
        <p class="text-sm text-slate-500 dark:text-slate-400">Total</p>
        <p class="text-xl font-bold text-slate-900 dark:text-white">{{ formatCurrency(total) }}</p>
      </div>
    </div>
    
    <!-- Legend -->
    <div class="flex-1 space-y-1 max-h-64 overflow-y-auto pr-1">
      <template v-for="category in groupedData" :key="category.id">
        <!-- Parent Category -->
        <div 
          class="flex items-center gap-2 p-2 rounded-lg transition-colors"
          :class="[
            hasSubcategories(category) 
              ? 'cursor-pointer hover:bg-slate-100 dark:hover:bg-slate-800' 
              : 'hover:bg-slate-50 dark:hover:bg-slate-800/50'
          ]"
          @click="hasSubcategories(category) && toggleCategory(category.id)"
        >
          <!-- Expand/Collapse Icon -->
          <div class="w-5 h-5 flex items-center justify-center flex-shrink-0">
            <template v-if="hasSubcategories(category)">
              <ChevronDownIcon 
                v-if="isExpanded(category.id)" 
                class="w-4 h-4 text-slate-500 dark:text-slate-400 transition-transform" 
              />
              <ChevronRightIcon 
                v-else 
                class="w-4 h-4 text-slate-500 dark:text-slate-400 transition-transform" 
              />
            </template>
          </div>
          
          <!-- Color Indicator -->
          <div 
            class="w-3 h-3 rounded-full flex-shrink-0"
            :style="{ backgroundColor: category.color }"
          />
          
          <!-- Name -->
          <span class="flex-1 text-sm text-slate-700 dark:text-slate-300 truncate font-medium">
            {{ category.name }}
          </span>
          
          <!-- Subcategories Count Badge -->
          <span 
            v-if="hasSubcategories(category)"
            class="text-xs px-1.5 py-0.5 rounded-full bg-slate-100 dark:bg-slate-700 text-slate-500 dark:text-slate-400"
          >
            {{ category.subcategories.length }}
          </span>
          
          <!-- Percentage -->
          <span class="text-xs text-slate-400 dark:text-slate-500 w-10 text-right">
            {{ getPercentage(category.total) }}%
          </span>
          
          <!-- Amount -->
          <span class="text-sm font-semibold text-slate-900 dark:text-white min-w-[80px] text-right">
            {{ formatCurrency(category.total) }}
          </span>
        </div>
        
        <!-- Subcategories (Expanded) -->
        <div 
          v-if="hasSubcategories(category) && isExpanded(category.id)"
          class="ml-5 pl-2 border-l-2 border-slate-200 dark:border-slate-700 space-y-0.5"
        >
          <div 
            v-for="sub in category.subcategories" 
            :key="sub.id"
            class="flex items-center gap-2 py-1.5 px-2 rounded-lg hover:bg-slate-50 dark:hover:bg-slate-800/50 transition-colors group"
          >
            <!-- Color Indicator (smaller) -->
            <div 
              class="w-2 h-2 rounded-full flex-shrink-0"
              :style="{ backgroundColor: sub.color }"
            />
            
            <!-- Name with parent reference on hover -->
            <span 
              class="flex-1 text-sm text-slate-600 dark:text-slate-400 truncate"
              :title="`${category.name} > ${sub.name}`"
            >
              {{ sub.name }}
            </span>
            
            <!-- Percentage of parent -->
            <span class="text-xs text-slate-400 dark:text-slate-500 w-10 text-right">
              {{ getPercentage(sub.total) }}%
            </span>
            
            <!-- Amount -->
            <span class="text-sm text-slate-600 dark:text-slate-400 min-w-[80px] text-right">
              {{ formatCurrency(sub.total) }}
            </span>
          </div>
        </div>
      </template>
      
      <!-- Empty State -->
      <div v-if="groupedData.length === 0" class="text-center py-8 text-slate-500 dark:text-slate-400">
        No hay gastos este mes
      </div>
    </div>
  </div>
</template>
