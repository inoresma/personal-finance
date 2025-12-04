<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useAccountsStore } from '@/stores/accounts'
import { useCategoriesStore } from '@/stores/categories'
import { useSecondaryCategoriesStore } from '@/stores/secondaryCategories'
import { useTransactionsStore } from '@/stores/transactions'
import { useUiStore } from '@/stores/ui'
import { formatMoney } from '@/composables/useCurrency'
import Modal from './Modal.vue'
import DateInput from './DateInput.vue'
import PurchaseItemForm from './PurchaseItemForm.vue'
import CategoryIcon from './CategoryIcon.vue'
import { BugAntIcon, PlusIcon, XMarkIcon } from '@heroicons/vue/24/outline'

const props = defineProps({
  transaction: {
    type: Object,
    default: null
  }
})

const emit = defineEmits(['close', 'saved'])

const accountsStore = useAccountsStore()
const categoriesStore = useCategoriesStore()
const secondaryCategoriesStore = useSecondaryCategoriesStore()
const transactionsStore = useTransactionsStore()
const uiStore = useUiStore()

const loading = ref(false)
const useMultipleProducts = ref(false)
const items = ref([])

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
  secondary_categories: [],
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

const selectedSecondaryCategory = ref(null)

const availableSecondaryCategories = computed(() => {
  const selectedIds = form.value.secondary_categories.map(c => typeof c === 'object' ? c.id : c)
  return secondaryCategoriesStore.secondaryCategories.filter(c => !selectedIds.includes(c.id))
})

function addSecondaryCategory() {
  if (!selectedSecondaryCategory.value) return
  const category = secondaryCategoriesStore.getSecondaryCategoryById(selectedSecondaryCategory.value)
  if (category && !form.value.secondary_categories.some(c => (typeof c === 'object' ? c.id : c) === category.id)) {
    form.value.secondary_categories.push(category)
    selectedSecondaryCategory.value = null
  }
}

function removeSecondaryCategory(category) {
  const index = form.value.secondary_categories.findIndex(c => 
    (typeof c === 'object' ? c.id : c) === (typeof category === 'object' ? category.id : category)
  )
  if (index > -1) {
    form.value.secondary_categories.splice(index, 1)
  }
}

function getSecondaryCategoryName(id) {
  const cat = secondaryCategoriesStore.getSecondaryCategoryById(id)
  return cat ? cat.name : ''
}

function getSecondaryCategoryColor(id) {
  const cat = secondaryCategoriesStore.getSecondaryCategoryById(id)
  return cat ? cat.color : '#6366F1'
}

function getSecondaryCategoryIcon(id) {
  const cat = secondaryCategoriesStore.getSecondaryCategoryById(id)
  return cat ? cat.icon : 'otros'
}

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
    useMultipleProducts.value = false
  }
  if (newType !== 'gasto') {
    form.value.is_ant_expense = false
    useMultipleProducts.value = false
  }
})

watch(useMultipleProducts, (enabled) => {
  if (!enabled) {
    items.value = []
  } else if (items.value.length === 0) {
    addItem()
  }
})

const totalAmount = computed(() => {
  if (!useMultipleProducts.value || items.value.length === 0) {
    return parseFloat(form.value.amount) || 0
  }
  return items.value.reduce((sum, item) => {
    const amount = parseFloat(item.amount) || 0
    const quantity = parseInt(item.quantity) || 1
    return sum + (amount * quantity)
  }, 0)
})

function addItem() {
  items.value.push({
    name: '',
    amount: '',
    quantity: 1,
    category: null,
    is_ant_expense: false
  })
}

function updateItem({ index, ...itemData }) {
  if (index >= 0 && index < items.value.length) {
    items.value[index] = { ...items.value[index], ...itemData }
  }
}

function removeItem(index) {
  items.value.splice(index, 1)
}

async function handleSubmit() {
  if (!form.value.account) {
    uiStore.showError('Por favor selecciona una cuenta')
    return
  }
  
  if (form.value.transaction_type === 'transferencia' && !form.value.destination_account) {
    uiStore.showError('Selecciona una cuenta destino')
    return
  }
  
  if (useMultipleProducts.value) {
    if (items.value.length === 0) {
      uiStore.showError('Agrega al menos un producto')
      return
    }
    const hasInvalidItems = items.value.some(item => !item.name || !item.amount)
    if (hasInvalidItems) {
      uiStore.showError('Completa todos los productos (nombre y precio)')
      return
    }
  } else {
    if (!form.value.amount) {
      uiStore.showError('Por favor ingresa el monto')
      return
    }
  }
  
  loading.value = true
  
  try {
    const data = {
      ...form.value,
      amount: useMultipleProducts.value ? totalAmount.value : parseFloat(form.value.amount),
      category: form.value.subcategory || form.value.category,
      secondary_categories: form.value.secondary_categories.map(c => typeof c === 'object' ? c.id : c),
    }
    delete data.subcategory
    
    if (data.transaction_type !== 'transferencia') {
      delete data.destination_account
    }
    
    if (useMultipleProducts.value && items.value.length > 0) {
      data.items = items.value.map(item => ({
        name: item.name,
        amount: parseFloat(item.amount) || 0,
        quantity: parseInt(item.quantity) || 1,
        category: item.category || null,
        secondary_categories: item.secondary_categories ? item.secondary_categories.map(c => typeof c === 'object' ? c.id : c) : [],
        is_ant_expense: item.is_ant_expense || false
      }))
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
    console.error('Error saving transaction:', error)
    console.error('Error response:', error.response?.data)
    
    // Mostrar mensaje de error más descriptivo
    let errorMessage = 'Error al guardar la transacción'
    if (error.response?.data) {
      const errorData = error.response.data
      if (errorData.non_field_errors) {
        errorMessage = Array.isArray(errorData.non_field_errors) 
          ? errorData.non_field_errors[0] 
          : errorData.non_field_errors
      } else if (errorData.items) {
        errorMessage = Array.isArray(errorData.items) 
          ? errorData.items[0] 
          : errorData.items
      } else if (errorData.amount) {
        errorMessage = Array.isArray(errorData.amount) 
          ? errorData.amount[0] 
          : errorData.amount
      } else if (typeof errorData === 'string') {
        errorMessage = errorData
      } else if (errorData.detail) {
        errorMessage = errorData.detail
      }
    }
    uiStore.showError(errorMessage)
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
  if (secondaryCategoriesStore.secondaryCategories.length === 0) {
    await secondaryCategoriesStore.fetchSecondaryCategories()
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
      secondary_categories: props.transaction.secondary_categories || [],
      is_ant_expense: props.transaction.is_ant_expense || false,
    }
    
    if (props.transaction.items && props.transaction.items.length > 0) {
      useMultipleProducts.value = true
      items.value = props.transaction.items.map(item => ({
        name: item.name || '',
        amount: item.amount || '',
        quantity: item.quantity || 1,
        category: item.category || null,
        secondary_categories: item.secondary_categories || [],
        is_ant_expense: item.is_ant_expense || false
      }))
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
      
      <!-- Multiple Products Toggle (only for expenses) -->
      <div v-if="form.transaction_type === 'gasto'" class="flex items-center gap-3 p-3 bg-blue-50 dark:bg-blue-900/20 rounded-xl">
        <button
          type="button"
          @click="useMultipleProducts = !useMultipleProducts"
          :class="[
            'relative w-11 h-6 rounded-full transition-colors flex-shrink-0',
            useMultipleProducts ? 'bg-blue-500' : 'bg-slate-300 dark:bg-slate-600'
          ]"
        >
          <span 
            :class="[
              'absolute top-0.5 left-0.5 w-5 h-5 rounded-full bg-white shadow-sm transition-transform duration-200',
              useMultipleProducts ? 'translate-x-5' : 'translate-x-0'
            ]"
          />
        </button>
        <div class="flex-1">
          <p class="text-sm font-medium text-slate-700 dark:text-slate-300">Compra con múltiples productos</p>
          <p class="text-xs text-slate-500 dark:text-slate-400">Agrega varios productos a una sola compra</p>
        </div>
      </div>
      
      <!-- Amount (single) -->
      <div v-if="!useMultipleProducts">
        <label class="label">Monto *</label>
        <div class="relative">
          <span class="absolute left-4 top-1/2 -translate-y-1/2 text-slate-400 font-medium">$</span>
          <input
            v-model="form.amount"
            type="number"
            step="0.01"
            min="0"
            placeholder="0"
            class="input pl-10 text-xl font-semibold"
            required
          />
        </div>
      </div>
      
      <!-- Multiple Products Section -->
      <div v-if="useMultipleProducts" class="space-y-4">
        <div class="flex items-center justify-between">
          <label class="label">Productos</label>
          <button
            type="button"
            @click="addItem"
            class="btn-secondary btn-sm flex items-center gap-2"
          >
            <PlusIcon class="w-4 h-4" />
            Agregar producto
          </button>
        </div>
        
        <div v-if="items.length === 0" class="text-center py-8 text-slate-500 dark:text-slate-400">
          <p class="text-sm">No hay productos agregados</p>
          <p class="text-xs mt-1">Haz clic en "Agregar producto" para comenzar</p>
        </div>
        
        <div v-else class="space-y-3">
          <PurchaseItemForm
            v-for="(item, index) in items"
            :key="`item-${index}-${item.name || ''}-${item.amount || ''}`"
            :item="item"
            :index="index"
            @update:item="updateItem"
            @remove="removeItem"
          />
        </div>
        
        <div v-if="items.length > 0" class="p-4 bg-slate-100 dark:bg-slate-800 rounded-xl border-2 border-slate-200 dark:border-slate-700">
          <div class="flex items-center justify-between">
            <span class="font-semibold text-slate-900 dark:text-white">Total:</span>
            <span class="text-2xl font-bold text-slate-900 dark:text-white">{{ formatMoney(totalAmount) }}</span>
          </div>
        </div>
      </div>
      
      <!-- Ant Expense Toggle (only for expenses, and only when NOT using multiple products) -->
      <div v-if="form.transaction_type === 'gasto' && !useMultipleProducts" class="flex items-center gap-3 p-3 bg-orange-50 dark:bg-orange-900/20 rounded-xl">
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
      
      <!-- Secondary Categories -->
      <div v-if="form.transaction_type !== 'transferencia'">
        <label class="label">Categorías Secundarias</label>
        <div class="space-y-2">
          <select 
            v-model="selectedSecondaryCategory" 
            class="input"
            @change="addSecondaryCategory"
          >
            <option :value="null">Selecciona una categoría secundaria</option>
            <option 
              v-for="secCat in availableSecondaryCategories" 
              :key="secCat.id" 
              :value="secCat.id"
            >
              {{ secCat.name }}
            </option>
          </select>
          <div v-if="form.secondary_categories.length > 0" class="flex flex-wrap gap-2">
            <div
              v-for="secCat in form.secondary_categories"
              :key="typeof secCat === 'object' ? secCat.id : secCat"
              class="flex items-center gap-2 px-3 py-1.5 rounded-full text-sm"
              :style="{ 
                backgroundColor: (typeof secCat === 'object' ? secCat.color : getSecondaryCategoryColor(secCat)) + '20',
                color: typeof secCat === 'object' ? secCat.color : getSecondaryCategoryColor(secCat)
              }"
            >
              <CategoryIcon 
                :icon="typeof secCat === 'object' ? secCat.icon : getSecondaryCategoryIcon(secCat)" 
                class="w-4 h-4"
                :style="{ color: typeof secCat === 'object' ? secCat.color : getSecondaryCategoryColor(secCat) }"
              />
              <span>{{ typeof secCat === 'object' ? secCat.name : getSecondaryCategoryName(secCat) }}</span>
              <button
                type="button"
                @click="removeSecondaryCategory(secCat)"
                class="ml-1 hover:opacity-70"
              >
                <XMarkIcon class="w-4 h-4" />
              </button>
            </div>
          </div>
        </div>
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

