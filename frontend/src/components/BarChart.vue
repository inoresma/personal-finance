<script setup>
import { computed } from 'vue'
import { Bar } from 'vue-chartjs'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend
} from 'chart.js'
import { formatMoney } from '@/composables/useCurrency'

ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend
)

const props = defineProps({
  data: {
    type: Array,
    default: () => []
  },
  labels: {
    type: Array,
    default: () => []
  },
  datasets: {
    type: Array,
    default: () => []
  },
  height: {
    type: Number,
    default: 300
  },
  horizontal: {
    type: Boolean,
    default: false
  }
})

const chartData = computed(() => {
  if (props.datasets && props.datasets.length > 0) {
    return {
      labels: props.labels,
      datasets: props.datasets
    }
  }
  
  return {
    labels: props.labels,
    datasets: [{
      label: 'Datos',
      data: props.data,
      backgroundColor: '#6366f1',
      borderRadius: 4
    }]
  }
})

const chartOptions = computed(() => ({
  indexAxis: props.horizontal ? 'y' : 'x',
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      display: props.datasets && props.datasets.length > 1,
      position: 'top',
    },
    tooltip: {
      backgroundColor: '#1e293b',
      padding: 12,
      cornerRadius: 8,
      callbacks: {
        label: function(context) {
          return formatMoney(context.parsed.y || context.parsed.x)
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
      ticks: props.horizontal ? {
        callback: function(value) {
          return formatMoney(value)
        }
      } : {},
      grid: {
        display: !props.horizontal,
        color: props.horizontal ? 'rgba(148, 163, 184, 0.1)' : 'transparent'
      }
    }
  }
}))
</script>

<template>
  <div :style="{ height: `${height}px` }">
    <Bar :data="chartData" :options="chartOptions" />
  </div>
</template>







