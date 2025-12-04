<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { formatDate as formatDateUtil } from '@/composables/useCurrency'

const props = defineProps({
  modelValue: {
    type: String,
    default: ''
  },
  placeholder: {
    type: String,
    default: 'dd/mm/aaaa'
  }
})

const emit = defineEmits(['update:modelValue'])

const displayValue = ref('')
const showNativePicker = ref(false)
const nativeInputRef = ref(null)

function formatToDDMMYYYY(isoDate) {
  if (!isoDate) return ''
  const date = new Date(isoDate + 'T00:00:00')
  const day = String(date.getDate()).padStart(2, '0')
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const year = date.getFullYear()
  return `${day}/${month}/${year}`
}

function parseDDMMYYYY(dateString) {
  if (!dateString) return ''
  
  const cleaned = dateString.replace(/[^\d/]/g, '')
  const parts = cleaned.split('/')
  
  if (parts.length !== 3) return ''
  
  const day = parts[0].padStart(2, '0')
  const month = parts[1].padStart(2, '0')
  const year = parts[2]
  
  if (day.length !== 2 || month.length !== 2 || year.length !== 4) return ''
  
  const dayNum = parseInt(day, 10)
  const monthNum = parseInt(month, 10)
  const yearNum = parseInt(year, 10)
  
  if (dayNum < 1 || dayNum > 31 || monthNum < 1 || monthNum > 12 || yearNum < 1900 || yearNum > 2100) {
    return ''
  }
  
  return `${year}-${month}-${day}`
}

function handleInput(event) {
  let value = event.target.value
  
  value = value.replace(/[^\d/]/g, '')
  
  if (value.length > 10) {
    value = value.slice(0, 10)
  }
  
  const parts = value.split('/')
  let formatted = ''
  
  if (parts.length > 0 && parts[0]) {
    formatted += parts[0].slice(0, 2)
  }
  if (parts.length > 1 && parts[1]) {
    formatted += '/' + parts[1].slice(0, 2)
  }
  if (parts.length > 2 && parts[2]) {
    formatted += '/' + parts[2].slice(0, 4)
  }
  
  displayValue.value = formatted
  
  if (formatted.length === 10) {
    const isoDate = parseDDMMYYYY(formatted)
    if (isoDate) {
      emit('update:modelValue', isoDate)
    }
  } else {
    emit('update:modelValue', '')
  }
}

function handleBlur() {
  if (props.modelValue) {
    displayValue.value = formatToDDMMYYYY(props.modelValue)
  } else {
    displayValue.value = ''
  }
}

function handleNativeDateChange(event) {
  const isoDate = event.target.value
  if (isoDate) {
    emit('update:modelValue', isoDate)
    displayValue.value = formatToDDMMYYYY(isoDate)
  }
  showNativePicker.value = false
}

function openNativePicker(event) {
  event.preventDefault()
  event.stopPropagation()
  if (nativeInputRef.value) {
    if (typeof nativeInputRef.value.showPicker === 'function') {
      nativeInputRef.value.showPicker()
    } else {
      nativeInputRef.value.focus()
      setTimeout(() => {
        nativeInputRef.value.click()
      }, 0)
    }
  }
}

watch(() => props.modelValue, (newValue) => {
  if (newValue) {
    displayValue.value = formatToDDMMYYYY(newValue)
  } else {
    displayValue.value = ''
  }
}, { immediate: true })

onMounted(() => {
  if (props.modelValue) {
    displayValue.value = formatToDDMMYYYY(props.modelValue)
  }
})
</script>

<template>
  <div class="relative">
    <input
      :value="displayValue"
      @input="handleInput"
      @blur="handleBlur"
      type="text"
      :placeholder="placeholder"
      class="input pr-10"
      maxlength="10"
    />
    <div class="absolute right-3 top-1/2 -translate-y-1/2 w-5 h-5">
      <input
        ref="nativeInputRef"
        :value="modelValue"
        @change="handleNativeDateChange"
        type="date"
        class="absolute inset-0 opacity-0 cursor-pointer w-full h-full"
        tabindex="-1"
      />
      <button
        type="button"
        @click="openNativePicker"
        class="text-slate-400 hover:text-slate-600 dark:hover:text-slate-300 relative z-10 pointer-events-auto"
        tabindex="-1"
      >
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
        </svg>
      </button>
    </div>
  </div>
</template>

