<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useAccountsStore } from '@/stores/accounts'
import { useCategoriesStore } from '@/stores/categories'
import { useTransactionsStore } from '@/stores/transactions'
import { useUiStore } from '@/stores/ui'
import { formatMoney } from '@/composables/useCurrency'
import Modal from './Modal.vue'
import DateInput from './DateInput.vue'
import { BugAntIcon } from '@heroicons/vue/24/outline'

const props = defineProps({
  transaction: {
    type: Object,
    default: null
  }
})

const emit = defineEmits(['close', 'saved'])

const accountsStore = useAccountsStore()
const categoriesStore = useCategoriesStore()
const transactionsStore = useTransactionsStore()
const uiStore = useUiStore()

const loading = ref(false)

const form = ref({
  transaction_type: 'gasto',
  amount: '',
  description: '',
  notes: '',
  date: new Date().toISOString().split('T')[0],
  account: null,
  destination_account: null,
  category: null,
  subcategory: null,
  is_ant_expense: false,
})

const isEditing = computed(() => !!props.transaction)

const title = computed(() => isEditing.value ? 'Editar transacción' : 'Nueva transacción')

const parentCategories = computed(() => {
  const categories = form.value.transaction_type === 'ingreso' 
    ? categoriesStore.incomeCategories 
    : categoriesStore.expenseCategories
  return categories.filter(c => !c.parent)
})

const selectedCategorySubcategories = computed(() => {
  if (!form.value.category) return []
  const parent = parentCategories.value.find(c => c.id === form.value.category)
  return parent?.subcategories || []
})

watch(() => form.value.category, () => {
  form.value.subcategory = null
})

const transactionTypes = [
  { value: 'gasto', label: 'Gasto', color: 'text-red-600 bg-red-100 dark:bg-red-900/30' },
  { value: 'ingreso', label: 'Ingreso', color: 'text-emerald-600 bg-emerald-100 dark:bg-emerald-900/30' },
  { value: 'transferencia', label: 'Transferencia', color: 'text-blue-600 bg-blue-100 dark:bg-blue-900/30' },
]

watch(() => form.value.transaction_type, (newType) => {
  if (newType === 'transferencia') {
    form.value.category = null
    form.value.is_ant_expense = false
  }
  if (newType !== 'gasto') {
    form.value.is_ant_expense = false
  }
})

async function handleSubmit() {
  if (!form.value.amount || !form.value.account) {
    uiStore.showError('Por favor completa los campos requeridos')
    return
  }
  
  if (form.value.transaction_type === 'transferencia' && !form.value.destination_account) {
    uiStore.showError('Selecciona una cuenta destino')
    return
  }
  
  loading.value = true
  
  try {
    const data = {
      ...form.value,
      amount: parseFloat(form.value.amount),
      category: form.value.subcategory || form.value.category,
    }
    delete data.subcategory
    
    if (data.transaction_type !== 'transferencia') {
      delete data.destination_account
    }
    
    if (isEditing.value) {
      await transactionsStore.updateTransaction(props.transaction.id, data)
      uiStore.showSuccess('Transacción actualizada')
    } else {
      await transactionsStore.createTransaction(data)
      uiStore.showSuccess('Transacción creada')
    }
    
    await accountsStore.fetchAccounts()
    emit('saved')
    emit('close')
  } catch (error) {
    uiStore.showError('Error al guardar la transacción')
  } finally {
    loading.value = false
  }
}

onMounted(async () => {
  if (accountsStore.accounts.length === 0) {
    await accountsStore.fetchAccounts()
  }
  if (categoriesStore.categories.length === 0) {
    await categoriesStore.fetchCategories()
  }
  
  if (props.transaction) {
    const catId = props.transaction.category
    let parentCatId = catId
    let subCatId = null
    
    if (catId) {
      const allCats = props.transaction.transaction_type === 'ingreso' 
        ? categoriesStore.incomeCategories 
        : categoriesStore.expenseCategories
      const parentCats = allCats.filter(c => !c.parent)
      
      for (const parent of parentCats) {
        if (parent.id === catId) {
          parentCatId = catId
          break
        }
        const sub = parent.subcategories?.find(s => s.id === catId)
        if (sub) {
          parentCatId = parent.id
          subCatId = catId
          break
        }
      }
    }
    
    form.value = {
      transaction_type: props.transaction.transaction_type,
      amount: props.transaction.amount,
      description: props.transaction.description,
      notes: props.transaction.notes || '',
      date: props.transaction.date,
      account: props.transaction.account,
      destination_account: props.transaction.destination_account,
      category: parentCatId,
      subcategory: subCatId,
      is_ant_expense: props.transaction.is_ant_expense || false,
    }
  } else if (accountsStore.accounts.length > 0) {
    form.value.account = accountsStore.accounts[0].id
  }
})
</script>

<template>
  <Modal :title="title" size="md" @close="emit('close')">
    <form @submit.prevent="handleSubmit" class="space-y-5">
      <!-- Transaction Type -->
      <div>
        <label class="label">Tipo de transacción</label>
        <div class="grid grid-cols-3 gap-2">
          <button
            v-for="type in transactionTypes"
            :key="type.value"
            type="button"
            @click="form.transaction_type = type.value"
            :class="[
              'px-4 py-2.5 rounded-xl font-medium text-sm transition-all',
              form.transaction_type === type.value 
                ? type.color 
                : 'bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-400 hover:bg-slate-200 dark:hover:bg-slate-700'
            ]"
          >
            {{ type.label }}
          </button>
        </div>
      </div>
      
      <!-- Amount -->
      <div>
        <label class="label">Monto *</label>
        <div class="relative">
          <span class="absolute left-4 top-1/2 -translate-y-1/2 text-slate-400 font-medium">$</span>
          <input
            v-model="form.amount"
            type="number"
            step="1"
            min="0"
            placeholder="0"
            class="input pl-10 text-xl font-semibold"
            required
          />
        </div>
      </div>
      
      <!-- Ant Expense Toggle (only for expenses) -->
      <div v-if="form.transaction_type === 'gasto'" class="flex items-center gap-3 p-3 bg-orange-50 dark:bg-orange-900/20 rounded-xl">
        <button
          type="button"
          @click="form.is_ant_expense = !form.is_ant_expense"
          :class="[
            'relative w-11 h-6 rounded-full transition-colors flex-shrink-0',
            form.is_ant_expense ? 'bg-orange-500' : 'bg-slate-300 dark:bg-slate-600'
          ]"
        >
          <span 
            :class="[
              'absolute top-0.5 left-0.5 w-5 h-5 rounded-full bg-white shadow-sm transition-transform duration-200',
              form.is_ant_expense ? 'translate-x-5' : 'translate-x-0'
            ]"
          />
        </button>
        <div class="flex items-center gap-2">
          <BugAntIcon class="w-5 h-5 text-orange-500" />
          <div>
            <p class="text-sm font-medium text-slate-700 dark:text-slate-300">Gasto hormiga</p>
            <p class="text-xs text-slate-500 dark:text-slate-400">Pequeños gastos que suman</p>
          </div>
        </div>
      </div>
      
      <!-- Account -->
      <div>
        <label class="label">Cuenta origen *</label>
        <select v-model="form.account" class="input" required>
          <option :value="null" disabled>Selecciona una cuenta</option>
          <option 
            v-for="account in accountsStore.activeAccounts" 
            :key="account.id" 
            :value="account.id"
          >
            {{ account.name }} ({{ formatMoney(account.balance) }})
          </option>
        </select>
      </div>
      
      <!-- Destination Account (for transfers) -->
      <div v-if="form.transaction_type === 'transferencia'">
        <label class="label">Cuenta destino *</label>
        <select v-model="form.destination_account" class="input" required>
          <option :value="null" disabled>Selecciona cuenta destino</option>
          <option 
            v-for="account in accountsStore.activeAccounts.filter(a => a.id !== form.account)" 
            :key="account.id" 
            :value="account.id"
          >
            {{ account.name }}
          </option>
        </select>
      </div>
      
      <!-- Category (not for transfers) -->
      <div v-if="form.transaction_type !== 'transferencia'">
        <label class="label">Categoría</label>
        <select v-model="form.category" class="input">
          <option :value="null">Sin categoría</option>
          <option 
            v-for="category in parentCategories" 
            :key="category.id" 
            :value="category.id"
          >
            {{ category.name }}
          </option>
        </select>
      </div>
      
      <!-- Subcategory (only if parent has subcategories) -->
      <div v-if="form.transaction_type !== 'transferencia' && selectedCategorySubcategories.length > 0">
        <label class="label">Subcategoría</label>
        <select v-model="form.subcategory" class="input">
          <option :value="null">Sin subcategoría (usar categoría principal)</option>
          <option 
            v-for="sub in selectedCategorySubcategories" 
            :key="sub.id" 
            :value="sub.id"
          >
            {{ sub.name }}
          </option>
        </select>
      </div>
      
      <!-- Description -->
      <div>
        <label class="label">Descripción</label>
        <input
          v-model="form.description"
          type="text"
          placeholder="Ej: Compra supermercado"
          class="input"
        />
      </div>
      
      <!-- Date -->
      <div>
        <label class="label">Fecha</label>
        <DateInput v-model="form.date" />
      </div>
      
      <!-- Notes -->
      <div>
        <label class="label">Notas (opcional)</label>
        <textarea
          v-model="form.notes"
          rows="2"
          placeholder="Notas adicionales..."
          class="input resize-none"
        />
      </div>
    </form>
    
    <template #footer>
      <div class="flex justify-end gap-3">
        <button 
          type="button"
          @click="emit('close')"
          class="btn-secondary"
        >
          Cancelar
        </button>
        <button
          @click="handleSubmit"
          :disabled="loading"
          class="btn-primary"
        >
          {{ loading ? 'Guardando...' : isEditing ? 'Actualizar' : 'Crear transacción' }}
        </button>
      </div>
    </template>
  </Modal>
</template>

