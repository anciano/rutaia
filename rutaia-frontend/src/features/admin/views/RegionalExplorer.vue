<template>
  <Toast />
  <div class="min-h-screen bg-gray-50 p-8">
    <div class="max-w-[1600px] mx-auto">
      <!-- Header -->
      <div class="bg-white rounded-2xl shadow-sm p-6 mb-6 border border-gray-100">
        <div class="flex items-center justify-between">
          <div>
            <h1 class="text-3xl font-black text-gray-800 flex items-center">
              <i class="pi pi-compass mr-3 text-emerald-600 text-2xl"></i>
              Explorador Regional (Radar)
            </h1>
            <p class="text-gray-500 mt-1">Detección radial de recursos y atractivos en el territorio</p>
          </div>
        </div>
      </div>

      <!-- Radar Interface -->
      <div class="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden p-4">
        <div class="grid grid-cols-1 lg:grid-cols-12 gap-6 h-[75vh]">
          <!-- Control & Results Panel -->
          <div class="lg:col-span-4 flex flex-col min-w-0 bg-gray-50 rounded-2xl border border-gray-100 p-6 overflow-hidden">
            <div class="space-y-6 mb-6">
              <div>
                <div class="flex items-center justify-between mb-2">
                  <label class="text-xs font-black uppercase tracking-widest text-gray-500">Radio de Búsqueda</label>
                  <Tag severity="info" :value="explorerRadius + ' km'" class="px-3" />
                </div>
                <Slider v-model="explorerRadius" :min="1" :max="100" class="w-full" @slideend="loadNearby" />
              </div>
              
              <div>
                <label class="text-xs font-black uppercase tracking-widest text-gray-500 mb-2 block">Filtrar por Categoría</label>
                <Dropdown 
                  v-model="explorerTypeFilter" 
                  :options="itemTypes" 
                  optionLabel="label" 
                  optionValue="value" 
                  placeholder="Todos los tipos" 
                  class="w-full border-0 shadow-sm rounded-xl"
                  showClear
                  @change="loadNearby"
                />
              </div>

              <div class="p-4 bg-blue-50 rounded-xl border border-blue-100 space-y-3">
                <div class="flex items-start gap-3">
                  <i class="pi pi-info-circle text-blue-500 mt-1"></i>
                  <p class="text-[11px] text-blue-700 leading-relaxed font-medium">
                    Haz clic en cualquier punto del mapa para mover tu posición o usa las herramientas de ubicación:
                  </p>
                </div>
                
                <div class="grid grid-cols-2 gap-2">
                  <Button 
                    @click="triggerGPS" 
                    icon="pi pi-map-marker" 
                    label="GPS" 
                    class="p-button-sm p-button-outlined p-button-info text-[10px] font-black"
                  />
                  <Dropdown 
                    v-model="selectedBaseTown" 
                    :options="baseTowns" 
                    optionLabel="name" 
                    placeholder="Elegir Pueblo" 
                    class="p-inputtext-sm text-[10px]"
                    @change="onBaseTownChange"
                    filter
                  />
                </div>
              </div>
            </div>

            <div class="flex items-center justify-between mb-4 border-b border-gray-200 pb-2">
              <span class="text-xs font-black uppercase tracking-widest text-gray-400">Resultados Cercanos</span>
              <span v-if="loadingExplorer" class="pi pi-spin pi-spinner text-blue-500 text-sm"></span>
            </div>

            <!-- Results Scrollable List -->
            <div class="flex-1 overflow-y-auto space-y-3 pr-2 custom-scrollbar">
              <div v-if="!explorerResults.length && !loadingExplorer" class="text-center py-20 text-gray-400">
                <i class="pi pi-map-marker text-5xl mb-4 block opacity-10"></i>
                <p class="text-sm font-bold opacity-30 italic">No se detectan recursos en este radio</p>
              </div>
              
              <div 
                v-for="res in explorerResults" 
                :key="res.id"
                class="bg-white p-4 rounded-2xl border border-gray-100 hover:border-emerald-200 transition-all cursor-pointer shadow-sm group hover:shadow-md"
              >
                <div class="flex justify-between items-start mb-2">
                  <div class="min-w-0 pr-2">
                    <div class="text-sm font-black text-gray-800 truncate">{{ res.name }}</div>
                    <div class="text-[10px] uppercase font-bold text-emerald-600 tracking-wider mt-0.5">
                      {{ translateType(res.item_type) }}
                    </div>
                  </div>
                  <div class="bg-emerald-50 text-emerald-600 text-[10px] font-black px-2 py-1 rounded-lg shrink-0">
                    {{ res.distance_km.toFixed(1) }} km
                  </div>
                </div>
                <div class="text-[11px] text-gray-500 line-clamp-2 italic leading-relaxed">
                  {{ res.description || 'Sin descripción disponible' }}
                </div>
              </div>
            </div>
          </div>

          <!-- Interactive Map -->
          <div class="lg:col-span-8 rounded-2xl overflow-hidden border border-gray-100 shadow-inner relative bg-gray-100">
            <LMap 
              :zoom="11" 
              :center="explorerCenter"
              @click="onExplorerMapClick"
              class="w-full h-full z-0"
              :options="{ zoomControl: true }"
            >
              <LTileLayer url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" layer-type="base" name="OpenStreetMap" />
              
              <!-- Radius Visualization -->
              <LCircle 
                :lat-lng="explorerCenter" 
                :radius="explorerRadius * 1000" 
                :color="'#10b981'" 
                :fill-color="'#10b981'" 
                :fill-opacity="0.08" 
                :weight="2"
                :dash-array="'10, 10'"
              />
              
              <!-- Self / Center Marker -->
              <LMarker :lat-lng="explorerCenter">
                <LIcon :icon-anchor="[16, 32]" :icon-size="[32, 32]">
                  <div class="w-8 h-8 bg-black rounded-full border-4 border-white shadow-xl flex items-center justify-center">
                    <i class="pi pi-user text-white text-xs"></i>
                  </div>
                </LIcon>
              </LMarker>

              <!-- Results on Map -->
              <LMarker 
                v-for="res in explorerResults" 
                :key="'marker-' + res.id" 
                :lat-lng="[res.lat, res.lng]"
              >
                <LIcon :icon-anchor="[16, 32]" :icon-size="[32, 32]">
                  <div 
                    class="w-8 h-8 rounded-full border-2 border-white shadow-lg flex items-center justify-center text-white"
                    :class="getTypeMarkerColor(res.item_type)"
                  >
                    <i :class="['pi text-[10px]', getItemIcon(res.item_type)]"></i>
                  </div>
                </LIcon>
                <LTooltip v-if="res.name">
                    <span class="font-bold text-xs">{{ res.name }}</span>
                </LTooltip>
              </LMarker>
            </LMap>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from '@/services/axios'
import { useToast } from 'primevue/usetoast'

// Leaflet
import "leaflet/dist/leaflet.css"
import { LMap, LTileLayer, LMarker, LCircle, LIcon, LTooltip } from "@vue-leaflet/vue-leaflet"

// PrimeVue
import Button from 'primevue/button'
import Dropdown from 'primevue/dropdown'
import Slider from 'primevue/slider'
import Tag from 'primevue/tag'
import Toast from 'primevue/toast'

const toast = useToast()

// Radar State
const explorerCenter = ref([-45.5752, -72.0662])
const explorerRadius = ref(10)
const explorerResults = ref([])
const loadingExplorer = ref(false)
const explorerTypeFilter = ref(null)

const itemTypes = [
  { label: 'Lugares', value: 'place' },
  { label: 'Actividades', value: 'activity' },
  { label: 'Rutas', value: 'route' },
  { label: 'Transporte', value: 'transport' },
  { label: 'Alojamiento', value: 'lodging' },
  { label: 'Eventos y Ferias', value: 'event' }
]

const baseTowns = ref([])
const selectedBaseTown = ref(null)

function translateType(type) {
  const t = itemTypes.find(i => i.value === type)
  return t ? t.label : type
}

function getItemIcon(type) {
  switch(type) {
    case 'place': return 'pi-map-marker'
    case 'activity': return 'pi-bolt'
    case 'route': return 'pi-map'
    case 'transport': return 'pi-directions'
    case 'lodging': return 'pi-home'
    case 'event': return 'pi-calendar'
    default: return 'pi-info-circle'
  }
}

function getTypeMarkerColor(type) {
  switch(type) {
    case 'place': return 'bg-blue-500'
    case 'activity': return 'bg-cyan-500'
    case 'route': return 'bg-emerald-500'
    case 'transport': return 'bg-purple-500'
    case 'lodging': return 'bg-indigo-500'
    case 'event': return 'bg-rose-500'
    default: return 'bg-gray-500'
  }
}

async function loadNearby() {
  loadingExplorer.value = true
  try {
    const params = {
      lat: explorerCenter.value[0],
      lng: explorerCenter.value[1],
      radius_km: explorerRadius.value,
      item_type: explorerTypeFilter.value || undefined
    }
    const { data } = await axios.get('/admin/explorer/nearby', { params })
    explorerResults.value = data
  } catch (err) {
    toast.add({ severity: 'error', summary: 'Error', detail: 'No se pudo cargar el radar' })
    console.error(err)
  } finally {
    loadingExplorer.value = false
  }
}

function onExplorerMapClick(e) {
  explorerCenter.value = [e.latlng.lat, e.latlng.lng]
  loadNearby()
}

async function loadBaseTowns() {
  try {
    // Filtramos lugares que sean pueblos o ciudades para el selector
    const { data } = await axios.get('/admin/items', { 
      params: { item_type: 'place' } 
    })
    baseTowns.value = data.filter(i => 
      ['town', 'city'].includes(i.extra?.place_subtype)
    )
  } catch (err) {
    console.error('Error cargando pueblos base:', err)
  }
}

function onBaseTownChange() {
  if (selectedBaseTown.value) {
    explorerCenter.value = [selectedBaseTown.value.lat, selectedBaseTown.value.lng]
    loadNearby()
  }
}

function triggerGPS() {
  if (navigator.geolocation) {
    navigator.geolocation.getCurrentPosition((pos) => {
      explorerCenter.value = [pos.coords.latitude, pos.coords.longitude]
      toast.add({ severity: 'success', summary: 'GPS Activo', detail: 'Ubicación actualizada correctamente', life: 2000 })
      loadNearby()
    }, () => {
      toast.add({ severity: 'warn', summary: 'GPS Denegado', detail: 'Usa el selector manual de pueblos', life: 3000 })
    })
  } else {
    toast.add({ severity: 'error', summary: 'No soportado', detail: 'Tu navegador no soporta GPS' })
  }
}

onMounted(async () => {
  await loadBaseTowns()
  triggerGPS() // Intentar GPS al inicio
})
</script>

<style scoped>
.custom-scrollbar::-webkit-scrollbar {
  width: 4px;
}
.custom-scrollbar::-webkit-scrollbar-track {
  background: transparent;
}
.custom-scrollbar::-webkit-scrollbar-thumb {
  background: #e5e7eb;
  border-radius: 10px;
}
.custom-scrollbar::-webkit-scrollbar-thumb:hover {
  background: #d1d5db;
}

:deep(.p-dropdown-label) {
  font-weight: 700;
  font-size: 0.875rem;
}

:deep(.p-tag-value) {
  font-weight: 900;
}
</style>
