<script setup>
import { ref, computed, watch, nextTick } from 'vue'
import { useCategoriesStore } from '@/stores/categories'
import { useSecondaryCategoriesStore } from '@/stores/secondaryCategories'
import { formatMoney } from '@/composables/useCurrency'
import CategoryIcon from './CategoryIcon.vue'
import { XMarkIcon, BugAntIcon } from '@heroicons/vue/24/outline'

const props = defineProps({
  item: {
    type: Object,
    default: () => ({
      name: '',
      amount: '',
      quantity: 1,
      category: null
    })
  },
  index: {
    type: Number,
    required: true
  }
})

const emit = defineEmits(['update:item', 'remove'])

const categoriesStore = useCategoriesStore()
const secondaryCategoriesStore = useSecondaryCategoriesStore()

const selectedSecondaryCategory = ref(null)

const form = ref({
  name: props.item.name || '',
  amount: props.item.amount || '',
  quantity: props.item.quantity || 1,
  category: props.item.category || null,
  secondary_categories: props.item.secondary_categories || [],
  is_ant_expense: props.item.is_ant_expense || false
})

const total = computed(() => {
  const amount = parseFloat(form.value.amount) || 0
  const quantity = parseInt(form.value.quantity) || 1
  return amount * quantity
})

let isInternalUpdate = false

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
    updateForm()
  }
}

function removeSecondaryCategory(category) {
  const index = form.value.secondary_categories.findIndex(c => 
    (typeof c === 'object' ? c.id : c) === (typeof category === 'object' ? category.id : category)
  )
  if (index > -1) {
    form.value.secondary_categories.splice(index, 1)
    updateForm()
  }
}

watch(() => props.item, (newItem) => {
  if (isInternalUpdate) return
  
  form.value = {
    name: newItem.name || '',
    amount: newItem.amount || '',
    quantity: newItem.quantity || 1,
    category: newItem.category || null,
    secondary_categories: newItem.secondary_categories || [],
    is_ant_expense: newItem.is_ant_expense || false
  }
}, { deep: true, immediate: false })

function updateForm() {
  isInternalUpdate = true
  emit('update:item', {
    index: props.index,
    name: form.value.name,
    amount: form.value.amount,
    quantity: form.value.quantity,
    category: form.value.category,
    secondary_categories: form.value.secondary_categories.map(c => typeof c === 'object' ? c.id : c),
    is_ant_expense: form.value.is_ant_expense
  })
  nextTick(() => {
    isInternalUpdate = false
  })
}

const expenseCategories = computed(() => {
  return categoriesStore.expenseCategories.filter(c => !c.parent)
})

const selectedCategorySubcategories = computed(() => {
  if (!form.value.category) return []
  const parent = expenseCategories.value.find(c => c.id === form.value.category)
  return parent?.subcategories || []
})

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
</script>

<template>
  <div class="p-4 bg-slate-50 dark:bg-slate-800/50 rounded-xl border border-slate-200 dark:border-slate-700 space-y-3">
    <div class="flex items-start justify-between gap-3">
      <div class="flex-1 space-y-3">
        <div>
          <label class="label text-xs">Nombre del producto</label>
          <input
            v-model.lazy="form.name"
            @blur="updateForm()"
            type="text"
            placeholder="Ej: Leche, Pan, etc."
            class="input text-sm"
          />
        </div>
        
        <div class="grid grid-cols-3 gap-3">
          <div>
            <label class="label text-xs">Precio</label>
            <div class="relative">
              <span class="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400 text-sm">$</span>
              <input
                v-model.lazy="form.amount"
                @blur="updateForm()"
                type="number"
                step="0.01"
                min="0"
                placeholder="0"
                class="input text-sm pl-8"
              />
            </div>
          </div>
          
          <div>
            <label class="label text-xs">Cantidad</label>
            <input
              :value="form.quantity"
              @input="form.quantity = parseInt($event.target.value) || 1; updateForm()"
              type="number"
              min="1"
              placeholder="1"
              class="input text-sm"
            />
          </div>
          
          <div>
            <label class="label text-xs">Total</label>
            <div class="input text-sm font-semibold bg-slate-100 dark:bg-slate-700 text-slate-900 dark:text-white">
              {{ formatMoney(total) }}
            </div>
          </div>
        </div>
        
        <div>
          <label class="label text-xs">Categoría (opcional)</label>
          <select :value="form.category" @change="form.category = $event.target.value ? parseInt($event.target.value) : null; updateForm()" class="input text-sm">
            <option :value="null">Sin categoría</option>
            <option 
              v-for="category in expenseCategories" 
              :key="category.id" 
              :value="category.id"
            >
              {{ category.name }}
            </option>
          </select>
        </div>
        
        <div>
          <label class="label text-xs">Categorías Secundarias</label>
          <select 
            v-model="selectedSecondaryCategory" 
            @change="addSecondaryCategory"
            class="input text-sm"
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
          <div v-if="form.secondary_categories.length > 0" class="flex flex-wrap gap-1.5 mt-2">
            <div
              v-for="secCat in form.secondary_categories"
              :key="typeof secCat === 'object' ? secCat.id : secCat"
              class="flex items-center gap-1 px-2 py-0.5 rounded-full text-xs"
              :style="{ 
                backgroundColor: (typeof secCat === 'object' ? secCat.color : getSecondaryCategoryColor(secCat)) + '20',
                color: typeof secCat === 'object' ? secCat.color : getSecondaryCategoryColor(secCat)
              }"
            >
              <CategoryIcon 
                :icon="typeof secCat === 'object' ? secCat.icon : getSecondaryCategoryIcon(secCat)" 
                class="w-3 h-3"
              />
              <span>{{ typeof secCat === 'object' ? secCat.name : getSecondaryCategoryName(secCat) }}</span>
              <button
                type="button"
                @click="removeSecondaryCategory(secCat)"
                class="ml-0.5 hover:opacity-70"
              >
                <XMarkIcon class="w-3 h-3" />
              </button>
            </div>
          </div>
        </div>
        
        <div class="flex items-center gap-2">
          <input
            :id="`ant-expense-${index}`"
            type="checkbox"
            :checked="form.is_ant_expense"
            @change="form.is_ant_expense = $event.target.checked; updateForm()"
            class="w-4 h-4 rounded border-slate-300 dark:border-slate-600 text-red-600 focus:ring-red-500 dark:bg-slate-700"
          />
          <label :for="`ant-expense-${index}`" class="text-sm text-slate-700 dark:text-slate-300 cursor-pointer flex items-center gap-1">
            <BugAntIcon class="w-4 h-4 text-red-600 dark:text-red-400" />
            Gasto hormiga
          </label>
        </div>
      </div>
      
      <button
        type="button"
        @click="emit('remove', props.index)"
        class="p-2 rounded-lg hover:bg-red-100 dark:hover:bg-red-900/30 text-red-600 dark:text-red-400 flex-shrink-0 mt-6"
        title="Eliminar producto"
      >
        <XMarkIcon class="w-5 h-5" />
      </button>
    </div>
  </div>
</template>


