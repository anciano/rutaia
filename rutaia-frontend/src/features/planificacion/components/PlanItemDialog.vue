<template>
  <Dialog 
    :visible="visible" 
    :header="isEdit ? 'Editar Parada' : 'Agregar Parada'"
    modal
    class="p-fluid w-full max-w-lg"
    @update:visible="$emit('update:visible', $event)"
  >
    <div class="space-y-4">
      <!-- Tipo de Ítem -->
      <div>
        <label class="block text-sm font-bold text-gray-700 mb-2">Tipo de Parada</label>
        <div class="flex flex-wrap gap-2">
           <button 
            v-for="t in itemTypes" 
            :key="t.value"
            @click="form.item_type = t.value"
            :class="[
              'px-3 py-2 rounded-xl text-xs font-bold border transition-all',
              form.item_type === t.value ? 'bg-blue-600 border-blue-600 text-white shadow-md shadow-blue-100' : 'bg-white border-gray-200 text-gray-500 hover:border-blue-200'
            ]"
          >
            <i :class="[t.icon, 'mr-1']"></i> {{ t.label }}
          </button>
        </div>
      </div>

      <!-- Buscador Unificado -->
      <div>
        <label class="block text-sm font-bold text-gray-700 mb-2">
          Buscar en Catálogo
        </label>
        <Dropdown 
          v-model="selectedCatalogItem" 
          :options="catalogOptions" 
          optionLabel="name" 
          filter 
          placeholder="Escribe para buscar..."
          :loading="loadingCatalog"
          @filter="onFilterCatalog"
          @change="onCatalogSelect"
          class="w-full rounded-xl"
        >
          <template #option="slotProps">
            <div class="flex flex-col">
              <span class="font-bold text-sm">{{ slotProps.option.name }}</span>
              <span class="text-[10px] uppercase text-gray-400 font-bold tracking-tighter">{{ slotProps.option.category_name || slotProps.option.item_type }}</span>
            </div>
          </template>
        </Dropdown>
      </div>
      
      <!-- Nombre de Item (Manual override o visualización) -->
      <div>
        <label class="block text-sm font-bold text-gray-700 mb-2">Nombre Personalizado</label>
        <InputText v-model="form.name_manual" placeholder="Ejem: Almuerzo en el bosque" class="w-full rounded-xl" />
      </div>

      <!-- Horarios y Costo (Solo si se agrega a un día específico) -->
      <div v-if="!isWishlist" class="space-y-4">
        <div class="grid grid-cols-2 gap-4">
          <div>
            <label class="block text-sm font-bold text-gray-700 mb-2">Hora Inicio</label>
            <InputMask v-model="form.start_time" mask="99:99" placeholder="09:00" class="w-full rounded-xl" />
          </div>
          <div>
            <label class="block text-sm font-bold text-gray-700 mb-2">Duración (min)</label>
            <InputNumber v-model="form.duration_minutes" suffix=" min" class="w-full rounded-xl" />
          </div>
        </div>

        <div>
          <label class="block text-sm font-bold text-gray-700 mb-2">Costo (CLP)</label>
          <InputNumber v-model="form.cost_clp" mode="currency" currency="CLP" locale="es-CL" class="w-full rounded-xl" />
        </div>
      </div>
      
      <div v-else class="p-4 bg-blue-50 rounded-xl border border-blue-100">
        <p class="text-[10px] text-blue-700 font-bold flex items-start">
          <i class="pi pi-info-circle mr-2 mt-0.5"></i>
          <span>Agregando a tu bolsa de intereses. Podrás asignar horarios y costos específicos una vez que organices tu itinerario.</span>
        </p>
      </div>

    </div>

    <template #footer>
      <div class="flex justify-between items-center w-full px-2">
        <span class="text-[10px] text-gray-400 italic">* Puedes editar el costo y duración sugeridos</span>
        <div class="flex gap-2">
          <button 
            @click="$emit('update:visible', false)"
            class="px-4 py-2 text-gray-500 hover:bg-gray-100 rounded-xl font-bold transition-all"
          >
            Cancelar
          </button>
          <button 
            @click="save"
            class="px-8 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-xl font-bold shadow-lg shadow-blue-100 transition-all flex items-center justify-center min-w-[120px]"
            :disabled="saving"
          >
            <i v-if="saving" class="pi pi-spin pi-spinner mr-2"></i>
            {{ isEdit ? 'Actualizar' : 'Agregar' }}
          </button>
        </div>
      </div>
    </template>
  </Dialog>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import Dialog from 'primevue/dialog'
import Dropdown from 'primevue/dropdown'
import InputText from 'primevue/inputtext'
import InputMask from 'primevue/inputmask'
import InputNumber from 'primevue/inputnumber'
import axios from '@/services/axios'

const props = defineProps({
  visible: Boolean,
  editItem: Object,
  dayId: String, // UUID of the day or null for wishlist
  planId: String  // ID of the plan (UserPlan.id)
})

const emit = defineEmits(['update:visible', 'save'])

const saving = ref(false)
const loadingCatalog = ref(false)
const catalogOptions = ref([])
const selectedCatalogItem = ref(null)

const itemTypes = [
  { label: 'Lugar', value: 'place', icon: 'pi pi-map-marker' },
  { label: 'Actividad', value: 'activity', icon: 'pi pi-compass' },
  { label: 'Hospedaje', value: 'lodging', icon: 'pi pi-home' }
]

const form = ref({
  item_type: 'place',
  catalog_item_id: null,
  name_manual: '',
  start_time: null,
  duration_minutes: 60,
  cost_clp: 0,
  sort_order: 0
})

const isEdit = computed(() => !!props.editItem)
const isWishlist = computed(() => !props.dayId)

// Load items based on type and search
async function searchCatalog(query = '') {
  loadingCatalog.value = true
  try {
    const params = {
      item_type: form.value.item_type || undefined,
      search: query || undefined,
      active_only: true
    }
    const { data } = await axios.get('/admin/items', { params })
    catalogOptions.value = data
  } catch (e) {
    console.error('Catalog error:', e)
  } finally {
    loadingCatalog.value = false
  }
}

function onFilterCatalog(event) {
  const query = event.filter
  if (query.length > 2) {
    searchCatalog(query)
  }
}

function onCatalogSelect() {
  if (selectedCatalogItem.value) {
    const item = selectedCatalogItem.value
    form.value.catalog_item_id = item.id
    form.value.name_manual = item.name
    form.value.cost_clp = item.approx_cost_clp || 0
    form.value.duration_minutes = item.estimated_duration_minutes || 60
    // Sincronizar item_type si el catálogo lo tiene (evita conflictos de validación)
    if (item.item_type) {
      form.value.item_type = item.item_type
    }
  }
}

watch(() => form.value.item_type, () => {
  searchCatalog() // Refresh list when type changes
})

watch(() => props.visible, (val) => {
  if (val) {
    console.log('PlanItemDialog visible with planId:', props.planId)
    if (props.editItem) {
      const i = props.editItem
      form.value = {
        item_type: i.item_type,
        catalog_item_id: i.catalog_item_id,
        name_manual: i.metadata_json?.name || '',
        start_time: i.start_time ? i.start_time.substring(0,5) : null,
        duration_minutes: i.metadata_json?.duration_minutes || 60,
        cost_clp: i.cost_clp,
        sort_order: i.sort_order
      }
      // Attempt to load current catalog item info for display
      if (i.catalog_item_id) {
         axios.get(`/admin/items/${i.catalog_item_id}`).then(res => {
           selectedCatalogItem.value = res.data
         })
      }
    } else {
      form.value = {
        item_type: 'place',
        catalog_item_id: null,
        name_manual: '',
        start_time: null,
        duration_minutes: 60,
        cost_clp: 0,
        sort_order: 0
      }
      selectedCatalogItem.value = null
      searchCatalog()
    }
  }
})

async function save() {
  saving.value = true
  try {
    const payload = {
      plan_id: props.planId, 
      item_type: form.value.item_type,
      catalog_item_id: form.value.catalog_item_id,
      day_id: props.dayId || null, 
      start_time: (props.dayId && form.value.start_time) ? form.value.start_time + ':00' : null,
      cost_clp: form.value.cost_clp || 0,
      sort_order: form.value.sort_order,
      metadata_json: {
        name: form.value.name_manual || selectedCatalogItem.value?.name,
        duration_minutes: form.value.duration_minutes,
        lat: selectedCatalogItem.value?.lat,
        lng: selectedCatalogItem.value?.lng,
        description: selectedCatalogItem.value?.description || 'Agregado desde catálogo'
      }
    }
    console.log('Emitting save with payload:', payload)
    
    emit('save', payload)
  } catch (e) {
    console.error(e)
  } finally {
    saving.value = false
  }
}
</script>
