<template>
  <div class="min-h-screen bg-gray-50 p-8">
    <div class="max-w-[1400px] mx-auto">
      <!-- Header -->
      <div class="bg-white rounded-2xl shadow-sm p-6 mb-6 border border-gray-100">
        <div class="flex items-center justify-between">
          <div>
            <h1 class="text-3xl font-black text-gray-800 flex items-center">
              <i class="pi pi-calendar mr-3 text-rose-600 text-2xl"></i>
              Agenda Local (Eventos)
            </h1>
            <p class="text-gray-500 mt-1">Gestión de ferias, festivales, mercados y actividades temporales</p>
          </div>
          <div class="flex gap-3">
            <button 
              @click="openCreateDialog"
              class="bg-rose-600 hover:bg-rose-700 text-white px-6 py-3 rounded-xl font-bold shadow-lg shadow-rose-200 transition-all flex items-center"
            >
              <i class="pi pi-plus-circle mr-2"></i>
              Nuevo Evento
            </button>
          </div>
        </div>

        <!-- Filters -->
        <div class="grid grid-cols-1 md:grid-cols-3 gap-4 mt-6">
          <span class="p-input-icon-left w-full">
            <i class="pi pi-search" />
            <InputText v-model="filters.search" placeholder="Buscar evento..." class="w-full rounded-xl" @keyup.enter="loadItems" />
          </span>
          <Dropdown 
            v-model="filters.category_id" 
            :options="eventCategories" 
            optionLabel="name" 
            optionValue="id"
            placeholder="Filtrar por categoría" 
            class="w-full rounded-xl shadow-sm"
            showClear
            @change="loadItems"
          />
          <button @click="loadItems" class="bg-gray-800 text-white font-bold rounded-xl px-4 py-2 hover:bg-gray-900 transition-all">
            <i class="pi pi-sync mr-2"></i> Actualizar
          </button>
        </div>
      </div>

      <!-- Main Content: List -->
      <div class="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden">
        <DataTable 
          :value="items" 
          :loading="loading" 
          paginator 
          :rows="15"
          responsiveLayout="scroll"
          class="p-datatable-sm"
          stripedRows
        >
          <template #empty><div class="p-8 text-center text-gray-500">No se encontraron eventos programados.</div></template>
          
          <Column header="Evento" sortable field="name" style="min-width: 300px">
            <template #body="{ data }">
              <div class="flex flex-col">
                <span class="font-bold text-gray-800">{{ data.name }}</span>
                <span class="text-[10px] text-gray-400 uppercase font-bold tracking-wider">{{ data.category_name }}</span>
              </div>
            </template>
          </Column>

          <Column header="Fecha / Horario" sortable style="width: 250px">
            <template #body="{ data }">
              <div v-if="data.event_info" class="text-xs space-y-1">
                <div class="flex items-center text-rose-600 font-bold">
                  <i class="pi pi-calendar mr-2"></i>
                  {{ formatDate(data.event_info.start_date) }}
                </div>
                <div v-if="data.event_info.end_date" class="flex items-center text-gray-400">
                  <i class="pi pi-arrow-right mr-2 text-[8px]"></i>
                  {{ formatDate(data.event_info.end_date) }}
                </div>
                <div v-if="data.event_info.is_recurring" class="text-[9px] text-rose-400 italic">
                  <i class="pi pi-sync mr-1"></i> Recurrente
                </div>
              </div>
            </template>
          </Column>


          <Column header="Estado" field="is_active" style="width: 100px">
            <template #body="{ data }">
              <Tag :severity="data.is_active ? 'success' : 'danger'" :value="data.is_active ? 'Visible' : 'Oculto'" />
            </template>
          </Column>

          <Column header="Acciones" style="width: 100px">
            <template #body="{ data }">
              <div class="flex gap-2">
                <Button icon="pi pi-pencil" class="p-button-text p-button-sm p-button-info" @click="editItem(data)" />
                <Button icon="pi pi-trash" class="p-button-text p-button-sm p-button-danger" @click="confirmDeleteItem(data)" />
              </div>
            </template>
          </Column>
        </DataTable>
      </div>
    </div>

    <!-- Edit/Create Dialog -->
    <Dialog 
      v-model:visible="itemDialog" 
      :header="editMode ? 'Editar Evento' : 'Nuevo Evento de Agenda'" 
      :modal="true" 
      class="p-fluid"
      :style="{ width: '90vw', maxWidth: '1000px' }"
    >
      <div class="grid grid-cols-1 lg:grid-cols-12 gap-6 py-2">
        <!-- Form Side -->
        <div class="lg:col-span-6 space-y-5 overflow-y-auto pr-2" style="max-height: 70vh;">
          <div>
            <label class="block text-sm font-bold text-gray-700 mb-1.5">Nombre del Evento *</label>
            <InputText v-model="formData.name" placeholder="Ejem: Feria Costumbrista Puerto Cisnes" class="rounded-xl shadow-sm" />
          </div>

          <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label class="block text-sm font-bold text-gray-700 mb-1.5">Categoría de Agenda *</label>
              <Dropdown 
                v-model="formData.category_id" 
                :options="eventCategories" 
                optionLabel="name" 
                optionValue="id" 
                filter 
                class="rounded-xl shadow-sm" 
                placeholder="Seleccione..." 
              />
            </div>
             <div>
              <label class="block text-sm font-bold text-gray-700 mb-1.5">Costo sugerido / Entrada</label>
              <InputNumber v-model="formData.approx_cost_clp" mode="currency" currency="CLP" locale="es-CL" class="rounded-xl shadow-sm" />
            </div>
          </div>

          <div class="p-4 bg-rose-50/50 rounded-2xl border border-rose-100 space-y-4">
            <label class="block text-[10px] uppercase font-black text-rose-900 tracking-widest flex items-center">
              <i class="pi pi-clock mr-2"></i> Programación Temporal
            </label>
            <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <label class="text-[9px] uppercase font-bold text-rose-400 block mb-1">Fecha Inicio</label>
                <Calendar v-model="formData.event_info.start_date" showTime hourFormat="24" dateFormat="dd/mm/yy" class="p-inputtext-sm" placeholder="Seleccionar..." />
              </div>
              <div>
                <label class="text-[9px] uppercase font-bold text-rose-400 block mb-1">Fecha Fin (Opcional)</label>
                <Calendar v-model="formData.event_info.end_date" showTime hourFormat="24" dateFormat="dd/mm/yy" class="p-inputtext-sm" placeholder="Seleccionar..." />
              </div>
            </div>
            <div class="flex items-center">
              <Checkbox v-model="formData.event_info.is_recurring" :binary="true" id="check_recur_agenda" />
              <label for="check_recur_agenda" class="ml-2 text-xs font-bold text-rose-800">Recurrencia Anual / Periódica</label>
            </div>
          </div>

          <div>
            <label class="block text-sm font-bold text-gray-700 mb-1.5">Descripción / Programa</label>
            <Textarea v-model="formData.description" rows="3" autoResize class="rounded-xl shadow-sm" placeholder="Detalles de la actividad, artistas, stands, etc." />
          </div>

          <div class="p-4 bg-blue-50/50 rounded-2xl border border-blue-100 space-y-4">
            <label class="block text-[10px] uppercase font-black text-blue-900 tracking-widest flex items-center">
              <i class="pi pi-map-marker mr-2"></i> ¿Dónde será? (Ubicación)
            </label>
            
            <div class="relative">
              <label class="text-[9px] uppercase font-bold text-blue-400 block mb-1">Buscar dirección o lugar</label>
              <span class="p-input-icon-left w-full">
                <i class="pi pi-search" v-if="!searchingLoc"></i>
                <i class="pi pi-spin pi-spinner" v-else></i>
                <InputText 
                  v-model="searchQuery" 
                  placeholder="Ejem: Plaza de Armas Coyhaique..." 
                  class="rounded-xl border-blue-100 p-inputtext-sm w-full"
                  @input="onSearchInput"
                />
              </span>
              <!-- Results -->
              <div v-if="searchResults.length > 0" class="absolute z-[1000] w-full bg-white border border-gray-100 rounded-xl shadow-2xl mt-1 max-h-[200px] overflow-y-auto">
                <div 
                  v-for="res in searchResults" 
                  :key="res.place_id"
                  @click="selectLocation(res)"
                  class="p-2 hover:bg-blue-50 cursor-pointer border-b border-gray-50 last:border-0 transition-colors"
                >
                  <div class="text-xs font-bold text-gray-800">{{ res.display_name.split(',')[0] }}</div>
                  <div class="text-[9px] text-gray-500 truncate">{{ res.display_name }}</div>
                </div>
              </div>
            </div>

            <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
              <div>
                <label class="text-[9px] uppercase font-bold text-blue-400 block mb-1">Referencia / Dirección</label>
                <InputText v-model="formData.extra.address" placeholder="Ej: Calle Principal s/n" class="p-inputtext-sm" />
              </div>
              <div class="grid grid-cols-2 gap-2">
                <div>
                  <label class="text-[9px] uppercase font-bold text-gray-400 block mb-1">Lat</label>
                  <InputNumber v-model="formData.lat" :minFractionDigits="6" class="p-inputtext-sm" />
                </div>
                <div>
                  <label class="text-[9px] uppercase font-bold text-gray-400 block mb-1">Lng</label>
                  <InputNumber v-model="formData.lng" :minFractionDigits="6" class="p-inputtext-sm" />
                </div>
              </div>
            </div>
          </div>

           <div class="flex items-center justify-between pt-2">
            <label class="flex items-center space-x-3 cursor-pointer p-2 hover:bg-gray-50 rounded-xl transition-colors">
              <Checkbox v-model="formData.is_active" :binary="true" />
              <span class="text-sm font-bold text-gray-700">Evento visible al público</span>
            </label>
            <div v-if="formData.extra?.geo_source" class="text-[9px] px-2 py-0.5 bg-blue-100 text-blue-600 rounded-full font-black uppercase">
                Ubicación: {{ formData.extra.geo_source }}
            </div>
          </div>
        </div>

        <!-- Map Side -->
        <div class="lg:col-span-6 h-[350px] lg:h-[70vh] border border-gray-200 rounded-2xl overflow-hidden relative shadow-inner bg-gray-50">
           <LMap 
            v-if="itemDialog"
            :zoom="12" 
            :center="mapCenter"
            @click="onMapClick"
            class="w-full h-full z-0"
          >
            <LTileLayer url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" layer-type="base" name="OpenStreetMap" />
            <LMarker v-if="formData.lat && formData.lng" :lat-lng="[formData.lat, formData.lng]" />
          </LMap>
        </div>
      </div>

      <template #footer>
        <div class="flex justify-between items-center w-full">
          <span class="text-xs text-gray-400 italic">* Todos los campos son importantes para el turista</span>
          <div class="flex gap-2">
            <Button label="Cancelar" class="p-button-text p-button-secondary" @click="itemDialog = false" />
            <Button :label="editMode ? 'Actualizar Evento' : 'Publicar en Agenda'" icon="pi pi-check" class="p-button-primary bg-rose-600" @click="saveItem" :loading="saving" />
          </div>
        </div>
      </template>
    </Dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from '@/services/axios'
import { useToast } from 'primevue/usetoast'
import { useConfirm } from 'primevue/useconfirm'

// Leaflet
import "leaflet/dist/leaflet.css"
import { LMap, LTileLayer, LMarker } from "@vue-leaflet/vue-leaflet"

// PrimeVue
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'
import Button from 'primevue/button'
import InputText from 'primevue/inputtext'
import Dropdown from 'primevue/dropdown'
import Dialog from 'primevue/dialog'
import Textarea from 'primevue/textarea'
import InputNumber from 'primevue/inputnumber'
import Checkbox from 'primevue/checkbox'
import Tag from 'primevue/tag'
import Calendar from 'primevue/calendar'

const toast = useToast()
const confirm = useConfirm()

// State
const items = ref([])
const eventCategories = ref([])
const loading = ref(false)
const saving = ref(false)
const itemDialog = ref(false)
const editMode = ref(false)
const mapCenter = ref([-45.5752, -72.0662])

const filters = ref({
  search: '',
  category_id: null
})

const formData = ref({
  item_type: 'event',
  name: '',
  description: '',
  category_id: null,
  lat: null,
  lng: null,
  approx_cost_clp: null,
  is_active: true,
  extra: {
    address: '',
    geo_source: null,
    geo_ref: null
  },
  event_info: {
    start_date: null,
    end_date: null,
    is_recurring: false
  }
})

// Geocoding State
const searchQuery = ref('')
const searchResults = ref([])
const searchingLoc = ref(false)
let searchTimeout = null

// Logic
async function loadCategories() {
  try {
    const { data } = await axios.get('/admin/categories')
    // Buscamos la raíz "Agenda Local" y sus hijos
    const root = data.find(c => c.name === 'Agenda Local' && !c.parent_id)
    if (root) {
      eventCategories.value = data.filter(c => c.parent_id === root.id)
    }
  } catch (err) {
    console.error('Err categories:', err)
  }
}

async function loadItems() {
  loading.value = true
  try {
    const params = {
      search: filters.value.search || undefined,
      category_id: filters.value.category_id || undefined,
      item_type: 'event' // Solo eventos aquí
    }
    const { data } = await axios.get('/admin/items', { params })
    items.value = data
  } catch (err) {
    toast.add({ severity: 'error', summary: 'Error', detail: 'No se pudieron cargar los eventos' })
  } finally {
    loading.value = false
  }
}

function formatDate(val) {
  if (!val) return ''
  const d = new Date(val)
  return d.toLocaleDateString('es-CL', { day: '2-digit', month: 'short', hour: '2-digit', minute: '2-digit' })
}

function openCreateDialog() {
  editMode.value = false
  formData.value = {
    item_type: 'event',
    name: '',
    description: '',
    category_id: eventCategories.value[0]?.id || null,
    lat: -45.5752,
    lng: -72.0662,
    approx_cost_clp: null,
    is_active: true,
    extra: {
      address: '',
      geo_source: null,
      geo_ref: null
    },
    event_info: {
      start_date: new Date(),
      end_date: null,
      is_recurring: false
    }
  }
  searchQuery.value = ''
  searchResults.value = []
  itemDialog.value = true
}

function editItem(item) {
  editMode.value = true
  formData.value = JSON.parse(JSON.stringify(item))
  if (!formData.value.extra) formData.value.extra = { address: '' }
  
  if (formData.value.event_info) {
    if (formData.value.event_info.start_date) formData.value.event_info.start_date = new Date(formData.value.event_info.start_date)
    if (formData.value.event_info.end_date) formData.value.event_info.end_date = new Date(formData.value.event_info.end_date)
  } else {
    formData.value.event_info = { start_date: null, end_date: null, is_recurring: false }
  }

  searchQuery.value = ''
  searchResults.value = []

  if (item.lat && item.lng) {
    mapCenter.value = [item.lat, item.lng]
  }
  itemDialog.value = true
}

async function saveItem() {
  if (!formData.value.name || !formData.value.category_id) {
    toast.add({ severity: 'warn', summary: 'Incompleto', detail: 'Nombre y Categoría son obligatorios' })
    return
  }
  
  saving.value = true
  try {
    if (editMode.value) {
      await axios.put(`/admin/items/${formData.value.id}`, formData.value)
      toast.add({ severity: 'success', summary: 'Éxito', detail: 'Evento actualizado' })
    } else {
      await axios.post('/admin/items', formData.value)
      toast.add({ severity: 'success', summary: 'Éxito', detail: 'Evento publicado' })
    }
    itemDialog.value = false
    loadItems()
  } catch (err) {
    console.error('Save error details:', err.response?.data || err)
    toast.add({ severity: 'error', summary: 'Error', detail: 'No se pudo guardar el evento' })
  } finally {
    saving.value = false
  }
}

function confirmDeleteItem(item) {
  confirm.require({
    message: `¿Seguro deseas eliminar "${item.name}" de la agenda?`,
    header: 'Confirmar Eliminación',
    icon: 'pi pi-exclamation-triangle',
    acceptClass: 'p-button-danger',
    accept: async () => {
      try {
        await axios.delete(`/admin/items/${item.id}`)
        toast.add({ severity: 'success', summary: 'Eliminado', detail: 'Evento removido' })
        loadItems()
      } catch (err) {
        toast.add({ severity: 'error', summary: 'Error', detail: 'No se pudo eliminar' })
      }
    }
  })
}

function onMapClick(e) {
  formData.value.lat = parseFloat(e.latlng.lat.toFixed(8))
  formData.value.lng = parseFloat(e.latlng.lng.toFixed(8))
  
  if (!formData.value.extra) formData.value.extra = {}
  formData.value.extra.geo_source = 'manual'
  formData.value.extra.geo_ref = null
}

function onSearchInput() {
  if (searchTimeout) clearTimeout(searchTimeout)
  if (!searchQuery.value || searchQuery.value.length < 3) {
    searchResults.value = []
    return
  }
  
  searchTimeout = setTimeout(async () => {
    searchingLoc.value = true
    try {
      const url = `https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(searchQuery.value)}&limit=5&addressdetails=1`
      const response = await fetch(url, { headers: { 'Accept-Language': 'es' } })
      const data = await response.json()
      searchResults.value = data
    } catch (err) {
      console.error('Geo error:', err)
    } finally {
      searchingLoc.value = false
    }
  }, 600)
}

function selectLocation(res) {
  const lat = parseFloat(res.lat)
  const lon = parseFloat(res.lon)
  
  formData.value.lat = lat
  formData.value.lng = lon
  mapCenter.value = [lat, lon]
  
  if (!formData.value.extra) formData.value.extra = {}
  formData.value.extra.geo_source = 'geocoder'
  formData.value.extra.geo_ref = res.display_name
  
  if (!formData.value.extra.address) {
     formData.value.extra.address = res.display_name.split(',')[0]
  }
  
  searchResults.value = []
  searchQuery.value = res.display_name.split(',')[0]
}

onMounted(() => {
  loadCategories()
  loadItems()
})
</script>
