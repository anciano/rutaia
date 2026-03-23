<template>
  <div class="h-screen overflow-y-auto md:overflow-hidden flex flex-col bg-gray-50">
    <!-- Header Refinado -->
    <header class="bg-white border-b border-gray-200 px-4 sm:px-6 py-1.5 sm:py-2 flex items-center justify-between shadow-sm z-[1010] shrink-0 sticky top-0 md:relative md:top-auto">
      <div class="truncate flex items-baseline space-x-3">
        <h1 class="text-sm sm:text-lg font-black text-blue-900 leading-none truncate">
          {{ store.plan?.ciudad_nombre || store.plan?.origen_id || 'Mi Itinerario' }} 
          <span class="text-blue-500 font-bold ml-1">{{ store.days.length }} Días</span>
        </h1>
        <p class="hidden sm:block text-[9px] text-gray-400 font-bold uppercase tracking-wider leading-none">
          {{ getTransportModeLabel(store.plan?.transport_mode) }} • Optimización activa
        </p>
      </div>

      <div class="flex items-center space-x-2 sm:space-x-4">
        <!-- Mobile View Toggle (Header) -->
        <div class="md:hidden flex bg-gray-100 p-1 rounded-xl">
          <button 
            @click="activeMobileTab = 'itinerary'"
            :class="['px-3 py-1.5 rounded-lg text-[10px] font-black tracking-tight transition-all', 
                     activeMobileTab === 'itinerary' ? 'bg-white text-blue-600 shadow-sm' : 'text-gray-400']"
          >
            LISTA
          </button>
          <button 
            @click="activeMobileTab = 'map'"
            :class="['px-3 py-1.5 rounded-lg text-[10px] font-black tracking-tight transition-all', 
                     activeMobileTab === 'map' ? 'bg-white text-blue-600 shadow-sm' : 'text-gray-400']"
          >
            MAPA
          </button>
        </div>

        <div class="flex items-center space-x-2">
          <span class="text-[8px] sm:text-[10px] font-bold text-gray-400 uppercase leading-none">Presupuesto:</span>
          <span :class="['text-sm sm:text-base font-black leading-none', budgetRemaining < 0 ? 'text-red-500' : 'text-green-600']">
            {{ formatCLP(budgetRemaining) }}
          </span>
        </div>
        <button class="bg-blue-600 hover:bg-blue-700 text-white p-1.5 sm:p-2 rounded-lg shadow-lg transition-transform active:scale-95 shrink-0 hidden sm:block">
          <i class="pi pi-share-alt text-[10px] sm:text-sm"></i>
        </button>
      </div>
    </header>

    <div class="flex-1 min-h-0 flex flex-row relative overflow-hidden">
      <!-- Mobile Floating Action Button (FAB) -->
      <button 
        v-if="activeMobileTab === 'itinerary'"
        @click="openAddDialog(null)"
        class="md:hidden fixed bottom-24 right-6 w-14 h-14 bg-blue-600 text-white rounded-full shadow-2xl z-[1001] flex items-center justify-center active:scale-95 transition-transform"
      >
        <i class="pi pi-plus text-xl"></i>
      </button>

      <!-- Middle Pane: Timeline -->
      <aside 
        :class="[
          'w-[500px] shrink-0 min-w-0 bg-white border-r border-gray-100 flex flex-col overflow-hidden transition-all duration-300',
          activeMobileTab === 'itinerary' ? 'max-md:flex max-md:fixed max-md:top-[48px] max-md:bottom-0 max-md:left-0 max-md:right-0 max-md:z-[1000]' : 'max-md:invisible max-md:opacity-0 max-md:fixed max-md:pointer-events-none'
        ]"
      >
        <!-- Header del Sidebar (Compacto) -->
        <div class="px-4 py-2 border-b border-gray-50 bg-gray-50/10 flex justify-between items-center shrink-0">
          <h2 class="text-xs font-black text-gray-400 uppercase tracking-widest flex items-center">
            <i class="pi pi-calendar mr-2 text-blue-400"></i>
            Itinerario
          </h2>
          <button @click="regenerate" class="text-[9px] font-black text-blue-600 hover:text-blue-700 bg-blue-50 px-2 py-1.5 rounded-lg uppercase flex items-center">
            <i class="pi pi-sparkles mr-1.5 text-[8px]"></i>
            Optimizar con IA
          </button>
        </div>

        <div class="flex-1 overflow-y-auto p-4 sm:p-6 space-y-12 custom-scrollbar pb-24">
          <!-- ... existing timeline content ... -->
          <!-- Note: I will need to use multi_replace to handle the internal content -->
          <!-- Estado Vacío -->
          <!-- Estado Vacío -->
          <div v-if="!store.days.length" class="flex flex-col items-center justify-center h-full text-center space-y-4 px-4">
            <div class="w-24 h-24 bg-blue-50 rounded-full flex items-center justify-center">
              <i class="pi pi-map text-4xl text-blue-200"></i>
            </div>
            <div>
              <h3 class="font-bold text-gray-800 text-lg">Itinerario Vacío</h3>
              <p class="text-gray-400 text-sm">No hay días planificados. ¡Comienza agregando uno!</p>
            </div>
            <div class="flex space-x-2">
                <button 
                  @click="regenerate"
                  class="bg-white text-blue-600 border border-blue-200 px-6 py-2 rounded-xl font-bold hover:bg-blue-50 transition-colors flex items-center"
                >
                  <i class="pi pi-sparkles mr-2 text-xs"></i>
                  Optimizar con IA
                </button>
                <button 
                  @click="handleAddDay"
                  class="bg-blue-600 text-white px-6 py-2 rounded-xl font-bold shadow-lg hover:bg-blue-700 transition-colors"
                >
                  + Agregar Primer Día
                </button>
            </div>
          </div>

          <div v-else class="space-y-12">
            <div v-for="day in store.days" :key="day.id" class="relative group/day">
            <!-- Marcador de Día Integrado a la Timeline -->
            <div class="flex items-start mb-6 relative z-30 pt-4 -mx-4 px-4 sm:-mx-6 sm:px-6">
              <!-- Círculo del Día sobre la línea -->
               <div class="w-14 h-14 bg-white border-4 border-blue-100 rounded-full flex flex-col items-center justify-center shadow-sm shrink-0 relative z-20">
                 <span class="text-[9px] uppercase font-bold text-blue-400 leading-tight">{{ day.date ? dayjs(day.date).format('MMM') : 'Día' }}</span>
                 <span class="text-xl font-black text-blue-900 leading-none">{{ day.date ? dayjs(day.date).format('DD') : day.number }}</span>
               </div>
               
               <div class="ml-4 flex-1 flex items-center justify-between pt-1 border-b border-gray-100 pb-4">
                 <div>
                   <h3 class="font-black text-gray-800 text-lg capitalize flex items-center">
                     {{ day.date ? dayjs(day.date).format('dddd, DD MMMM') : `Día ${day.number}` }}
                   </h3>
                   <p class="text-gray-400 text-xs mt-0.5">{{ day.items?.length || 0 }} actividades programadas</p>
                 </div>
                 
                 <!-- Eliminar Día -->
                 <button 
                   @click="confirmDeleteDay(day)" 
                   class="opacity-0 group-hover/day:opacity-100 text-gray-300 hover:text-red-500 hover:bg-red-50 p-2 rounded-xl transition-all shrink-0"
                   title="Eliminar este día"
                 >
                   <i class="pi pi-trash"></i>
                 </button>
               </div>
            </div>

            <!-- Contenedor Timeline -->
            <div class="relative pt-2 pb-8">
              <!-- Línea principal continua -->
              <div class="absolute left-[26px] top-0 bottom-0 w-[4px] bg-blue-100 rounded-full"></div>

              <template v-for="(item, index) in day.items" :key="item.id">
                
                <!-- Parada (Lugar/Actividad/Hospedaje) -->
                <div 
                  @click="focusMarker(item)"
                  class="relative pl-14 pr-4 sm:pr-0 mb-3 group cursor-pointer z-10"
                >
                  <!-- Nodo de la parada (Círculo sobre la línea) -->
                  <div class="absolute left-[14px] top-6 w-6 h-6 min-w-[24px] max-w-[24px] min-h-[24px] max-h-[24px] shrink-0 rounded-full border-[3px] border-white flex items-center justify-center shadow-sm transition-transform group-hover:scale-110 z-20"
                       :class="item.item_type === 'lodging' ? 'bg-indigo-500' : 'bg-blue-600'">
                     <i :class="[getItemIcon(item.item_type), 'text-[10px] text-white']"></i>
                  </div>

                  <!-- Tarjeta de Parada -->
                  <div class="bg-white border border-gray-100 p-4 rounded-2xl shadow-sm hover:shadow-md hover:border-blue-200 transition-all overflow-hidden flex flex-col w-full">
                     <div class="flex justify-between items-start">
                       <div class="flex-1 pr-4">
                         <div class="flex flex-col mb-1 items-start">
                           <span v-if="item.start_time" class="text-[10px] font-bold bg-blue-50 text-blue-600 px-2 py-0.5 rounded-md uppercase mb-1 inline-block">
                             {{ item.start_time.substring(0,5) }}
                           </span>
                           <h4 class="font-black text-gray-800 text-sm sm:text-base leading-tight group-hover:text-blue-600 transition-colors break-words">
                             {{ item.metadata_json?.name || item.name || 'Sin nombre' }}
                           </h4>
                           <p class="text-[11px] sm:text-xs text-gray-400 mt-1 line-clamp-2 leading-relaxed h-[34px]">
                             {{ item.metadata_json?.vicinity || item.metadata_json?.description || item.metadata_json?.address || 'Sin descripción' }}
                           </p>
                         </div>
                       </div>
                       
                       <div class="flex flex-col items-end gap-2 shrink-0 h-full justify-between">
                         <!-- Precio -->
                         <span class="text-xs font-black text-gray-800 bg-gray-50 px-2 py-1 rounded-lg border border-gray-100">{{ formatCLP(item.cost_clp) }}</span>
                         
                         <!-- Acciones (Editar / Eliminar) -->
                         <div class="flex space-x-1 mt-6">
                           <button v-if="item.item_type !== 'transport' && item.item_type !== 'route'" @click.stop="openEditDialog(item)" class="p-1.5 text-gray-400 hover:text-blue-600 hover:bg-blue-50 rounded-lg transition-colors" title="Editar">
                             <i class="pi pi-pencil text-sm"></i>
                           </button>
                           <button @click.stop="confirmDeleteItem(item)" class="p-1.5 text-gray-400 hover:text-red-500 hover:bg-red-50 rounded-lg transition-colors" title="Eliminar">
                             <i class="pi pi-trash text-sm"></i>
                           </button>
                         </div>
                       </div>
                     </div>
                  </div>
                </div>

                <!-- Transport / Connector -->
                <div class="relative pl-14 py-1 z-0 group mb-3" v-if="index < day.items.length - 1">
                  <!-- Nodo del Tramo -->
                  <div class="flex items-center">
                    <TransportSegmentSelector 
                      v-if="day.day_segments?.[index]"
                      :segment="day.day_segments[index]"
                      @change-mode="(mode) => handleSegmentChange(day.day_segments[index].id, mode)"
                      class="-ml-2"
                    />
                    <!-- Fallback Conector (Haversine) -->
                    <div v-else-if="getDistanceText(item, day.items[index+1]) !== null" 
                         class="bg-blue-50 text-blue-600 text-[10px] font-bold px-3 py-1.5 rounded-full border border-blue-100 shadow-sm flex items-center -ml-2">
                        <i class="pi pi-car text-[10px] mr-1.5 opacity-80"></i>
                        {{ getDistanceText(item, day.items[index+1]) }} (~{{ getTravelTime(item, day.items[index+1]) }})
                    </div>
                  </div>
                </div>
              </template>

              <!-- Botón Añadir Parada -->
              <div class="relative pl-14 mt-2 pr-4 sm:pr-0 z-10">
                <!-- Nodo vacío -->
                <div class="absolute left-[18px] top-1/2 -translate-y-1/2 w-[20px] h-[20px] rounded-full border-2 border-dashed border-blue-400 bg-white flex items-center justify-center z-20"></div>
                <button 
                  @click="openAddDialog(day.id)"
                  class="w-full py-3 bg-white border-2 border-dashed border-blue-100 rounded-xl text-blue-500 hover:bg-blue-50 hover:border-blue-300 transition-all flex items-center justify-center font-bold text-xs shadow-sm active:scale-[0.98] uppercase tracking-wider"
                >
                  <i class="pi pi-plus text-xs mr-2"></i> Añadir parada al itinerario
                </button>
              </div>

              <!-- Sugerencia de Hospedaje (Generada por Backend) -->
              <div v-if="day.lodging_suggestion" class="relative pl-14 mt-6 pr-4 sm:pr-0 z-10">
                <div class="absolute left-[16px] top-6 w-6 h-6 rounded-full border-[3px] border-white bg-indigo-300 flex items-center justify-center shadow-sm z-20">
                     <i class="pi pi-sparkles text-[10px] text-white"></i>
                </div>
                <div class="bg-indigo-50/50 border border-indigo-100 p-4 rounded-xl flex flex-col sm:flex-row items-start sm:items-center space-y-3 sm:space-y-0 sm:space-x-3 relative overflow-hidden group/suggestion">
                  <div class="absolute -right-6 -top-6 w-24 h-24 bg-indigo-500/5 rounded-full blur-xl"></div>
                  
                  <div class="flex-1 min-w-0">
                    <div class="flex items-center space-x-2">
                      <span class="text-[10px] font-black text-indigo-600 uppercase tracking-widest bg-indigo-100 px-2 py-0.5 rounded">Sugerencia Mágica</span>
                      <span class="text-[10px] text-gray-400 uppercase tracking-widest font-bold">Hospedaje</span>
                    </div>
                    <h4 class="font-bold text-gray-800 text-sm mt-1 truncate">{{ day.lodging_suggestion.name }}</h4>
                    <p class="text-[10px] text-gray-400 line-clamp-1 mt-0.5">La mejor opción cerca de tu última parada</p>
                  </div>
                  
                  <div class="flex sm:flex-col items-center sm:items-end justify-between w-full sm:w-auto shrink-0">
                    <span class="text-xs font-black text-gray-800 sm:mb-2">{{ formatCLP(day.lodging_suggestion.approx_cost_clp) }}</span>
                    <button 
                      @click="addSuggestedLodging(day, day.lodging_suggestion)"
                      class="text-[10px] bg-white border border-indigo-200 text-indigo-600 hover:bg-indigo-600 hover:text-white px-3 py-1.5 rounded-lg font-bold transition-colors shadow-sm z-10 relative"
                    >
                      Añadir al día
                    </button>
                  </div>
                </div>
              </div>

            </div>
          </div>
          
          <!-- Botón Agregar Día Global -->
          <button 
             @click="handleAddDay"
             class="w-full py-4 bg-gray-50 hover:bg-gray-100 text-gray-400 hover:text-blue-600 rounded-2xl border-2 border-dashed border-gray-200 hover:border-blue-200 transition-all font-bold flex items-center justify-center space-x-2"
          >
            <i class="pi pi-calendar-plus"></i>
            <span>Agregar Día Extra</span>
          </button>

          <!-- Bolsa de Intereses (Wishlist) -->
          <div v-if="store.wishlist.length > 0" class="mt-12 bg-gray-50 rounded-3xl p-6 border-2 border-dashed border-gray-200">
            <div class="flex items-center justify-between mb-4">
              <h3 class="text-sm font-black text-gray-400 uppercase tracking-widest flex items-center">
                <i class="pi pi-heart-fill mr-2 text-pink-400"></i>
                Bolsa de Intereses
              </h3>
              <button 
                @click="organizeTrip"
                class="text-[10px] font-bold bg-blue-600 text-white px-3 py-1.5 rounded-lg shadow-md hover:bg-blue-700 transition-all uppercase"
              >
                Organizar Todo
              </button>
            </div>
            
            <div class="space-y-3">
              <div 
                v-for="item in store.wishlist" :key="item.id"
                @click="focusMarker(item)"
                class="bg-white p-4 rounded-2xl border border-gray-100 shadow-sm hover:shadow-md transition-all cursor-pointer group flex items-center justify-between"
              >
                <div class="flex items-center space-x-3 overflow-hidden">
                  <div class="w-8 h-8 rounded-lg bg-gray-50 flex items-center justify-center text-gray-400 group-hover:text-blue-500 transition-colors">
                    <i :class="getItemIcon(item.item_type)"></i>
                  </div>
                  <div class="truncate">
                    <h5 class="text-sm font-bold text-gray-700 truncate group-hover:text-blue-600">{{ item.metadata_json?.name || 'Cualquier lugar' }}</h5>
                    <p class="text-[10px] text-gray-400 uppercase font-bold tracking-tighter">{{ item.item_type }}</p>
                  </div>
                </div>
                <div class="flex items-center space-x-1">
                  <button @click.stop="confirmDeleteItem(item)" class="p-2 text-gray-300 hover:text-red-500 transition-colors">
                    <i class="pi pi-trash text-xs"></i>
                  </button>
                </div>
              </div>
            </div>
          </div>
          </div>
        </div>
      </aside>

      <!-- Right Pane: Map -->
      <main 
        :class="[
          'w-full md:flex-1 min-w-0 relative transition-all duration-300',
          activeMobileTab === 'map' ? 'max-md:fixed max-md:top-[48px] max-md:bottom-0 max-md:left-0 max-md:right-0 max-md:z-[1000]' : 'max-md:absolute max-md:inset-0 max-md:z-0 max-md:h-screen max-md:overflow-hidden'
        ]"
      >
        <LMap 
          ref="mapRef"
          :zoom="12" 
          :center="mapCenter" 
          class="h-full w-full"
          :options="{ zoomControl: false }"
        >
            <LTileLayer 
              url="https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png" 
              attribution="&copy; OpenStreetMap" 
            />

            <!-- Marcadores Itinerario -->
            <LMarker 
              v-for="p in store.points" 
              :key="p.id" 
              :lat-lng="[p.lat, p.lng]"
              :opacity="p.is_wishlist ? 0.6 : 1"
            >
              <LIcon v-if="p.is_wishlist">
                <div class="bg-white p-1 rounded-full border-2 border-pink-400 shadow-lg">
                  <i class="pi pi-heart-fill text-pink-400 text-xs"></i>
                </div>
              </LIcon>
              <LPopup>
                <div class="p-2 font-black text-blue-900 text-sm">
                  {{ p.name }}
                  <span v-if="p.is_wishlist" class="block text-[10px] text-pink-400 uppercase mt-1">En Bolsa de Intereses</span>
                </div>
              </LPopup>
            </LMarker>

            <!-- Polilíneas de Segmentos Reales (OSRM) -->
            <template v-if="store.all_segments.length > 0">
              <LPolyline
                v-for="(seg, index) in store.all_segments"
                :key="seg.id"
                :lat-lngs="seg.route_geometry.coordinates.map(c => [c[1], c[0]])"
                :color="getSegmentColor(index)"
                :weight="6"
                :opacity="0.9"
                :options="{ smoothFactor: 1.5, lineJoin: 'round' }"
              >
                <LPopup>
                  <div class="p-2 space-y-1">
                    <div class="flex items-center space-x-2">
                       <i :class="getTransportIcon(seg.transport_mode)" class="text-blue-600"></i>
                       <span class="font-black text-gray-800 uppercase text-xs">Tramo de {{ seg.transport_mode }}</span>
                    </div>
                    <div class="text-xs text-gray-500 font-bold">
                       {{ (seg.distance_km || 0).toFixed(1) }} km • {{ seg.duration_minutes || 0 }} min
                    </div>
                  </div>
                </LPopup>
              </LPolyline>
            </template>

            <!-- Polilínea del Recorrido (Fallback Línea Recta) -->
            <LPolyline
              v-else-if="store.itineraryPoints.length >= 2"
              :lat-lngs="store.itineraryPoints.map(p => [p.lat, p.lng])"
              color="#1e3a8a"
              :weight="4"
              :opacity="0.6"
              dash-array="10, 10"
            />
        </LMap>

        <!-- Widgets Flotantes -->
        <div class="absolute bottom-8 right-8 z-[1000] flex flex-col space-y-4">
          <button @click="resetView" class="w-12 h-12 bg-white rounded-2xl shadow-2xl flex items-center justify-center text-gray-700 hover:text-blue-600 transition-colors">
            <i class="pi pi-home text-lg"></i>
          </button>
        </div>
      </main>
    </div>

    <PlanItemDialog
      v-model:visible="showItemDialog"
      :edit-item="selectedItem"
      :day-id="selectedDayId"
      :plan-id="route.params.planId"
      @save="handleSaveItem"
    />

    <!-- Panel de Sugerencias IA (Desktop) -->
    <AISuggestionsPanel 
      :visible="showSuggestions"
      :suggestions="store.activeSuggestions"
      :loading="store.isFetchingIA"
      @close="showSuggestions = false"
      @accept="handleAcceptSuggestion"
      @discard="handleDiscardSuggestion"
    />

    <!-- Chat Flotante (Mobile Suggestions) -->
    <ChatBubble 
      ref="chatRef"
      :plan-id="route.params.planId"
      :external-toggle="!isMobile"
      :active="showSuggestions"
      @click-bubble="handleBubbleClick"
      @accept-suggestion="handleAcceptSuggestion"
      @discard-suggestion="handleDiscardSuggestion"
    />
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch, nextTick, onBeforeUnmount } from 'vue'
import { useRoute } from 'vue-router'
import axios from '@/services/axios'
import dayjs from 'dayjs'
import 'dayjs/locale/es'
import ChatBubble from '@/components/ChatBubble.vue'
import AISuggestionsPanel from '@/features/planificacion/components/AISuggestionsPanel.vue'
import PlanItemDialog from '@/features/planificacion/components/PlanItemDialog.vue'
import TransportSegmentSelector from '@/features/planificacion/components/TransportSegmentSelector.vue'
import { LMap, LTileLayer, LMarker, LPopup, LPolyline, LIcon } from '@vue-leaflet/vue-leaflet'
import 'leaflet/dist/leaflet.css'

// Pinia
import { usePlanDetailStore } from '@/stores/planDetail'
import { storeToRefs } from 'pinia'
import { useConfirm } from 'primevue/useconfirm'
import { useToast } from 'primevue/usetoast'

dayjs.locale('es')

const store = usePlanDetailStore()
const { budgetRemaining } = storeToRefs(store)
const route = useRoute()
const confirm = useConfirm()
const toast = useToast()

const mapRef = ref(null)
const mapCenter = ref([-45.5752, -72.0662]) // Coyhaique (Aysén) por defecto
const activeMobileTab = ref('itinerary') // 'itinerary' | 'map'

// Dialogos Manuales
const organizationPacing = ref('normal') // relaxed, normal, compact
const chatRef = ref(null)
const showSuggestions = ref(false)

const isMobile = computed(() => window.innerWidth < 768)

const handleBubbleClick = () => {
  console.log('ChatBubble clicked. isMobile:', isMobile.value, 'showSuggestions before:', showSuggestions.value)
  if (!isMobile.value) {
    showSuggestions.value = !showSuggestions.value
    console.log('showSuggestions after toggle:', showSuggestions.value)
  }
}

const invalidateMap = async () => {
  await nextTick()
  // vue-leaflet expone el objeto Leaflet así (normalmente):
  const map = mapRef.value?.leafletObject
  if (map) map.invalidateSize()
}

onMounted(async () => {
  if (route.params.planId) {
    await store.setPlanContext(route.params.planId)
    await invalidateMap()
    // Centrar mapa si hay puntos, sino intentar centrar en la ciudad destino
    if (store.points.length > 0) {
      mapCenter.value = [store.points[0].lat, store.points[0].lng]
    } else if (store.plan?.lat && store.plan?.lon) {
       // Si el backend entrega lat/lon de la ciudad en el objeto plan
       mapCenter.value = [store.plan.lat, store.plan.lon]
    }
    await nextTick()
    fitMapToRoute()
  }
})
const onResize = () => invalidateMap()
window.addEventListener('resize', onResize)
onBeforeUnmount(() => window.removeEventListener('resize', onResize))

// Redirección si cambia el ID
watch(() => route.params.planId, (newId) => {
  if (newId) store.setPlanContext(newId)
})

watch(activeMobileTab, async (val) => {
  if (val === 'map') {
    await invalidateMap()
  }
})

// Computed para polilínea
const polyline = computed(() => store.points.map(p => [p.lat, p.lng]))

// Persistir sugerencias cuando cambien
watch(() => store.activeSuggestions, () => {
  store.saveSuggestions()
}, { deep: true })

// Helpers UI
const formatCLP = (v) => new Intl.NumberFormat('es-CL', { style: 'currency', currency: 'CLP' }).format(v || 0)

const getItemIcon = (type) => {
  const icons = {
    'place': 'pi pi-map-marker',
    'activity': 'pi pi-compass',
    'transport': 'pi pi-car',
    'lodging': 'pi pi-home',
    'route': 'pi pi-directions'
  }
  return icons[type] || 'pi pi-info-circle'
}

const getTransportModeLabel = (mode) => {
  const modes = {
    'auto_propio': 'Auto propio',
    'arrendar_auto': 'Arrendar auto',
    'transporte_publico': 'Transporte público',
    'movilidad_local': 'Movilidad local'
  }
  return modes[mode] || 'Transporte no definido'
}

// Haversine distance calculation
const haversine = (lat1, lon1, lat2, lon2) => {
  if (!lat1 || !lon1 || !lat2 || !lon2) return null;
  const R = 6371.0;
  const dLat = (lat2 - lat1) * Math.PI / 180;
  const dLon = (lon2 - lon1) * Math.PI / 180;
  const a = Math.sin(dLat/2) * Math.sin(dLat/2) +
            Math.cos(lat1 * Math.PI / 180) * Math.cos(lat2 * Math.PI / 180) *
            Math.sin(dLon/2) * Math.sin(dLon/2);
  const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a));
  return R * c;
}

const getCoordinates = (item) => {
  // Check catalog_item first if available and has coords (frontend might not have it populated fully, but try)
  // Usually we fall back to metadata_json which the backend populates
  const lat = item.metadata_json?.lat || item.catalog_item?.lat
  const lng = item.metadata_json?.lng || item.catalog_item?.lng
  return { lat, lng }
}

const getDistanceText = (itemA, itemB) => {
  const coordsA = getCoordinates(itemA)
  const coordsB = getCoordinates(itemB)
  
  const dist = haversine(coordsA.lat, coordsA.lng, coordsB.lat, coordsB.lng)
  if (dist === null) return null
  
  if (dist < 1) {
    return `${Math.round(dist * 1000)} m`
  }
  return `${dist.toFixed(1)} km`
}

const getTravelTime = (itemA, itemB) => {
  const coordsA = getCoordinates(itemA)
  const coordsB = getCoordinates(itemB)
  
  const dist = haversine(coordsA.lat, coordsA.lng, coordsB.lat, coordsB.lng)
  if (dist === null) return null

  // assuming roughly 50km/h average speed in car
  // time in minutes = (distance / 50) * 60 = distance * 1.2
  // add 5 mins base overhead
  const mins = Math.round(dist * 1.2) + 5
  return `${mins} min`
}

const focusMarker = (item) => {
  if (item.metadata_json?.lat && item.metadata_json?.lng) {
    mapCenter.value = [item.metadata_json.lat, item.metadata_json.lng]
  }
}

const resetView = () => {
  fitMapToRoute()
}

const fitMapToRoute = () => {
  const map = mapRef.value?.leafletObject
  if (!map) return

  const bounds = []
  
  // Incluir todos los puntos del itinerario y bolsa
  store.points.forEach(p => bounds.push([p.lat, p.lng]))
  
  // Incluir las polilíneas para asegurar que se vean las curvas
  store.all_segments.forEach(seg => {
    seg.route_geometry.coordinates.forEach(c => bounds.push([c[1], c[0]]))
  })

  if (bounds.length > 0) {
    map.fitBounds(bounds, { padding: [50, 50], maxZoom: 15 })
  }
}

const regenerate = async () => {
  if (store.isFetchingIA) return

  confirm.require({
    message: 'Esta acción consultará a la IA para sugerir mejoras basadas en tus preferencias y presupuesto. ¿Continuar?',
    header: 'Optimización Inteligente',
    icon: 'pi pi-sparkles',
    accept: async () => {
      store.isFetchingIA = true
      toast.add({ severity: 'info', summary: 'Consultando IA...', detail: 'Analizando tu ruta para encontrar mejoras', life: 3000 })
      
      try {
        const payload = {
          ciudad_inicio: store.plan?.ciudad_nombre || 'Coyhaique',
          dias: store.days.length,
          presupuesto: Number(store.plan?.presupuesto_clp || store.plan?.presupuesto || 150000),
          num_personas: Number(store.plan?.num_personas || 2),
          preferencias: store.plan?.preferencias || ['naturaleza', 'gastronomia'],
          itinerario: store.days.map(d => ({
            dia: d.number,
            items: d.items.map(i => ({
              id: i.id,
              nombre: i.metadata_json?.name || i.name || 'Lugar',
              duracion: Number(i.estimated_duration_minutes || 60),
              precio: Number(i.cost_clp || 0)
            }))
          })),
          wishlist: store.wishlist.map(i => ({
            id: i.id,
            nombre: i.metadata_json?.name || i.name || 'Lugar',
            duracion: Number(i.estimated_duration_minutes || 60),
            precio: Number(i.cost_clp || 0)
          }))
        }

        const { data } = await axios.post('/ia/sugerencias', payload)
        
        if (data.sugerencias && data.sugerencias.length > 0) {
          store.activeSuggestions = data.sugerencias
          
          if (isMobile.value) {
            chatRef.value?.addAIMessage(
              'He analizado tu viaje y tengo algunas sugerencias interesantes para ti:',
              data.sugerencias
            )
          } else {
            showSuggestions.value = true
          }
          
          toast.add({ severity: 'success', summary: 'Sugerencias Listas', detail: `He encontrado ${data.sugerencias.length} posibles mejoras`, life: 3000 })
        } else {
          toast.add({ severity: 'warn', summary: 'Sin sugerencias', detail: 'Tu itinerario ya parece estar bien optimizado.', life: 3000 })
        }
      } catch (e) {
        console.error('IA Error:', e)
        toast.add({ severity: 'error', summary: 'Error IA', detail: 'No pudimos obtener las sugerencias en este momento.', life: 4000 })
      } finally {
        store.isFetchingIA = false
      }
    }
  })
}

async function handleAcceptSuggestion(sug) {
  if (!sug.action_data) {
    toast.add({ severity: 'warn', summary: 'Acción no soportada', detail: 'Esta sugerencia no tiene datos técnicos para ejecutarse.' })
    return
  }

  try {
    const { tipo, action_data } = sug
    
    if (tipo === 'agregar') {
      const day = store.days.find(d => d.number === action_data.dia)
      await store.createUnifiedItem({
        item_type: 'place', // Asumimos lugar por ahora, o la IA podría especificar
        name: action_data.nombre,
        description: action_data.descripcion,
        day_id: day?.id,
        cost_clp: action_data.precio,
        estimated_duration_minutes: action_data.duracion,
        metadata_json: {
          name: action_data.nombre,
          // La IA podría dar lat/lng si las conoce, o dejarlo para el geocoder manual si no
          ...(action_data.lat && { lat: action_data.lat, lng: action_data.lng })
        }
      })
    } else if (tipo === 'eliminar') {
      await store.deleteUnifiedItem(action_data.item_id)
    } else if (tipo === 'mover') {
      const day = store.days.find(d => d.number === action_data.new_day)
      await store.moveItem(action_data.item_id, day?.id)
    } else if (tipo === 'reemplazar') {
      // Eliminar el viejo
      await store.deleteUnifiedItem(action_data.item_id_to_remove)
      // Agregar el nuevo
      const day = store.days.find(d => d.number === action_data.new_item.dia)
      await store.createUnifiedItem({
        item_type: 'place',
        name: action_data.new_item.nombre,
        description: action_data.new_item.descripcion,
        day_id: day?.id,
        cost_clp: action_data.new_item.precio,
        estimated_duration_minutes: action_data.new_item.duracion,
        metadata_json: { name: action_data.new_item.nombre }
      })
    }

    toast.add({ severity: 'success', summary: 'Cambio Aplicado', detail: `Se ha procesado: ${sug.titulo}`, life: 3000 })
    handleDiscardSuggestion(sug)
  } catch (err) {
    console.error('Error aplicando sugerencia:', err)
    toast.add({ severity: 'error', summary: 'Error al aplicar', detail: 'No se pudo aplicar el cambio automáticamente.' })
  }
}

function handleDiscardSuggestion(sug) {
  store.activeSuggestions = store.activeSuggestions.filter(s => s.id !== sug.id)
  if (store.activeSuggestions.length === 0) {
    showSuggestions.value = false
  }
  // También limpiar del historial del chat si está abierto
  chatRef.value?.removeSuggestion(sug.id)
}

async function addSuggestedLodging(day, suggestion) {
  const payload = {
    plan_id: route.params.planId,
    day_id: day.id,
    item_type: 'lodging',
    catalog_item_id: suggestion.catalog_item_id,
    cost_clp: suggestion.approx_cost_clp || 0,
    sort_order: (day.items?.length || 0) * 10
  }
  
  try {
    toast.add({ severity: 'info', summary: 'Agregando...', detail: 'Incorporando sugerencia al itinerario', life: 1500 })
    await store.createUnifiedItem(payload)
    toast.add({ severity: 'success', summary: 'Agregado', detail: 'Hospedaje agregado al final del día', life: 3000 })
  } catch(e) {
    toast.add({ severity: 'error', summary: 'Error', detail: 'No se pudo agregar la sugerencia', life: 3000 })
  }
}

// ---- Manual Editing Handlers ----

function openAddDialog(dayId) {
  selectedItem.value = null
  selectedDayId.value = dayId
  showItemDialog.value = true
}

function openEditDialog(item) {
  selectedItem.value = item
  selectedDayId.value = item.day_id // though not needed for update
  showItemDialog.value = true
}

async function handleSaveItem(payload) {
  try {
    if (selectedItem.value) {
      await store.updateUnifiedItem(selectedItem.value.id, payload)
      toast.add({ severity: 'success', summary: 'Actualizado', detail: 'Ítem actualizado', life: 3000 })
    } else {
      // Evitar duplicados si viene del catálogo
      if (payload.catalog_item_id) {
        const isDuplicate = store.all_items.some(i => i.catalog_item_id === payload.catalog_item_id)
        if (isDuplicate) {
          toast.add({ severity: 'warn', summary: 'Duplicado', detail: 'Este interés ya está en tu plan o bolsa.', life: 4000 })
          return // Abort save
        }
      }
      
      // payload ya incluye plan_id e incluye day_id (que puede ser null)
      await store.createUnifiedItem(payload)
      toast.add({ severity: 'success', summary: 'Agregado', detail: payload.day_id ? 'Agregado al día' : 'Agregado a la bolsa', life: 3000 })
    }
    showItemDialog.value = false
  } catch (e) {
    console.error('Save error:', e)
    const detail = e.response?.data?.detail || e.message || 'No se pudo guardar el ítem'
    toast.add({ severity: 'error', summary: 'Error', detail: typeof detail === 'string' ? detail : JSON.stringify(detail), life: 5000 })
  }
}

async function organizeTrip() {
  const toastId = 'organize-toast'
  toast.add({ id: toastId, severity: 'info', summary: 'Organizando...', detail: 'Agrupando por cercanía geográfica', life: 2000 })
  
  try {
    const { data } = await axios.post(`/plan/${route.params.planId}/organize`, {
      pacing: organizationPacing.value
    })
    
    if (data.status === 'organized') {
      await store.fetchPlanV2() // Recargar todo el plan
      
      if (data.suggestions) {
        confirm.require({
          message: data.suggestions.message,
          header: 'Sugerencia de Extensión',
          icon: 'pi pi-calendar-plus',
          acceptLabel: 'Sí, extender',
          rejectLabel: 'No, dejar en bolsa',
          accept: async () => {
            try {
              toast.add({ severity: 'info', summary: 'Extendiendo...', detail: `Agregando ${data.suggestions.days_to_add} día(s)`, life: 2000 })
              // Add the required days
              for (let i = 0; i < data.suggestions.days_to_add; i++) {
                await store.addDay()
              }
              // Re-run organization now that we have enough empty days
              await organizeTrip()
            } catch (e) {
              toast.add({ severity: 'error', summary: 'Error', detail: 'No se pudo extender el viaje automáticamente', life: 3000 })
            }
          },
          reject: () => {
            toast.add({ severity: 'info', summary: 'Viaje Organizado', detail: `Se organizaron ${data.updates} ítems. El resto quedó en la bolsa.`, life: 5000 })
          }
        })
      } else {
        toast.add({ 
          severity: 'success', 
          summary: 'Viaje Organizado', 
          detail: data.message, 
          life: 5000 
        })
      }
    } else {
      toast.add({ severity: 'warn', summary: 'Info', detail: data.message, life: 3000 })
    }
  } catch (e) {
    console.error('Error organizing trip:', e)
    const detail = e.response?.data?.detail || e.message || 'Error desconocido al organizar'
    toast.add({ severity: 'error', summary: 'Error al organizar', detail: typeof detail === 'string' ? detail : JSON.stringify(detail), life: 6000 })
  }
}

function confirmDeleteItem(item) {
  confirm.require({
    message: '¿Eliminar este ítem?',
    header: 'Confirmar',
    icon: 'pi pi-trash',
    acceptClass: 'p-button-danger',
    accept: async () => {
      try {
        await store.deleteUnifiedItem(item.id)
        toast.add({ severity: 'success', summary: 'Eliminado', detail: 'Ítem eliminado', life: 3000 })
      } catch (e) {
        toast.add({ severity: 'error', summary: 'Error', detail: 'No se pudo eliminar', life: 3000 })
      }
    }
  })
}

async function handleAddDay() {
  try {
    await store.addDay()
    toast.add({ severity: 'success', summary: 'Día Agregado', life: 3000 })
  } catch (e) {
    toast.add({ severity: 'error', summary: 'Error', detail: 'No se pudo agregar día', life: 3000 })
  }
}

function confirmDeleteDay(day) {
  confirm.require({
    message: `¿Eliminar el Día ${day.number}? Todos sus ítems serán borrados.`,
    header: 'Eliminar Día',
    icon: 'pi pi-exclamation-triangle',
    acceptClass: 'p-button-danger',
    accept: async () => {
      try {
        await store.deleteDay(day.id)
        toast.add({ severity: 'success', summary: 'Día Eliminado', life: 3000 })
      } catch (e) {
        toast.add({ severity: 'error', summary: 'Error', detail: 'No se pudo eliminar el día', life: 3000 })
      }
    }
  })
}

async function handleSegmentChange(segmentId, newMode) {
  try {
    await store.updateSegmentMode(segmentId, newMode)
    toast.add({ severity: 'success', summary: 'Transporte Actualizado', detail: `Modo cambiado a ${newMode}`, life: 2000 })
  } catch (e) {
    toast.add({ severity: 'error', summary: 'Error', detail: 'No se pudo actualizar el modo de transporte', life: 3000 })
  }
}

const getSegmentColor = (index) => {
  const palette = [
    '#2563eb', // Blue
    '#ea580c', // Orange
    '#7c3aed', // Violet
    '#059669', // Emerald
    '#db2777', // Pink
    '#d97706', // Amber
    '#0891b2', // Cyan
    '#4f46e5', // Indigo
    '#dc2626', // Red
    '#65a30d', // Lime
    '#9333ea', // Purple
    '#0d9488'  // Teal
  ]
  return palette[index % palette.length]
}

const getTransportIcon = (mode) => {
  const icons = {
    car: 'pi pi-car',
    walk: 'pi pi-walking',
    bus: 'pi pi-bus',
    ferry: 'pi pi-ship',
    flight: 'pi pi-send'
  }
  return icons[mode] || 'pi pi-directions'
}
</script>

<style scoped>
.custom-scrollbar::-webkit-scrollbar {
  width: 6px;
}
.custom-scrollbar::-webkit-scrollbar-track {
  background: transparent;
}
.custom-scrollbar::-webkit-scrollbar-thumb {
  background: #e2e8f0;
  border-radius: 10px;
}
.custom-scrollbar::-webkit-scrollbar-thumb:hover {
  background: #cbd5e1;
}

.animate-fade-in {
  animation: fadeIn 0.5s ease-out;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}
</style>
