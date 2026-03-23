<template>
  <div class="w-full max-w-6xl mx-auto px-2 sm:px-4 py-4 sm:py-8">
    <WizardProgress :current-step="5" />

    <div class="bg-white p-8 rounded-2xl shadow-xl border border-gray-100 space-y-8 animate-fade-in mt-6">
      <div class="text-center">
        <h2 class="text-3xl font-extrabold text-blue-900 mb-2 font-display">Tu Bolsa de Intereses</h2>
        <p class="text-gray-500 max-w-xl mx-auto">
          Selecciona los lugares y actividades que no quieres perderte. 
          Los organizaremos automáticamente en tu itinerario según su cercanía.
        </p>
      </div>

      <!-- Buscador y Filtros -->
      <div class="flex flex-col md:flex-row gap-4">
        <div class="relative flex-1 group">
          <i class="pi pi-search absolute left-4 top-1/2 -translate-y-1/2 text-gray-400 group-focus-within:text-blue-500 transition-colors"></i>
          <input 
            v-model="searchQuery" 
            type="text" 
            placeholder="Buscar lugares o actividades..."
            class="w-full pl-12 pr-4 py-3 bg-gray-50 border-2 border-transparent rounded-xl focus:bg-white focus:border-blue-500 transition-all outline-none"
            @input="handleSearch"
          >
        </div>
        <div class="flex gap-2 overflow-x-auto pb-2 scrollbar-none">
          <button 
            @click="selectedCategoryId = null"
            :class="[
              'px-4 py-3 rounded-xl font-bold text-xs uppercase tracking-widest whitespace-nowrap border-2 transition-all',
              !selectedCategoryId 
                ? 'bg-blue-600 border-blue-600 text-white shadow-lg shadow-blue-100' 
                : 'bg-white border-gray-100 text-gray-400 hover:border-blue-200 hover:text-blue-600'
            ]"
          >
            Todos
          </button>
          <button 
            v-for="cat in rootCategories" 
            :key="cat.id"
            @click="toggleCategory(cat.id)"
            :class="[
              'px-4 py-3 rounded-xl font-bold text-xs uppercase tracking-widest whitespace-nowrap border-2 transition-all',
              selectedCategoryId === cat.id 
                ? 'bg-blue-600 border-blue-600 text-white shadow-lg shadow-blue-100' 
                : 'bg-white border-gray-100 text-gray-400 hover:border-blue-200 hover:text-blue-600'
            ]"
          >
            {{ cat.name || 'Categoría' }}
          </button>
        </div>
      </div>

      <!-- Grid de Items -->
      <div v-if="loading" class="flex flex-col items-center justify-center py-20">
        <i class="pi pi-spin pi-spinner text-4xl text-blue-500 mb-4"></i>
        <p class="text-gray-400 font-bold uppercase tracking-widest text-xs">Cargando catálogo...</p>
      </div>

      <div v-else-if="filteredItems.length === 0" class="text-center py-20 bg-gray-50 rounded-2xl border-2 border-dashed border-gray-100">
        <i class="pi pi-search text-4xl text-gray-300 mb-4"></i>
        <p class="text-gray-400 font-medium">No encontramos resultados para tu búsqueda.</p>
      </div>

      <div v-else class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
        <div 
          v-for="item in filteredItems" 
          :key="item.id"
          class="group bg-white rounded-2xl border border-gray-100 shadow-sm hover:shadow-xl hover:border-blue-200 transition-all overflow-hidden flex flex-col relative"
          :class="{ 'ring-2 ring-blue-500 border-blue-500': isSelected(item.id) }"
        >
          <!-- Badge de Tipo -->
          <div class="absolute top-4 right-4 z-10">
            <span :class="[getTypeColor(item.item_type), 'px-2 py-1 rounded-lg text-[10px] font-black uppercase tracking-widest shadow-sm']">
              {{ item.item_type }}
            </span>
          </div>

          <div class="p-5 flex-1">
            <h3 class="font-bold text-gray-800 group-hover:text-blue-600 transition-colors mb-2 line-clamp-1">
              {{ item.name || 'Lugar sin nombre' }}
            </h3>
            <p class="text-[11px] text-gray-400 line-clamp-2 mb-4 leading-relaxed h-[32px]">
              {{ item.description || 'Sin descripción disponible.' }}
            </p>
            
            <div class="flex items-center justify-between mt-auto pt-4 border-t border-gray-50">
              <div class="flex flex-col">
                <span v-if="item.approx_cost_clp" class="text-xs font-black text-gray-700">
                  {{ formatCurrency(item.approx_cost_clp) }}
                </span>
                <span v-else class="text-[10px] font-bold text-green-600 uppercase">Gratuito / Libread</span>
                <span class="text-[9px] text-gray-400 font-medium truncate max-w-[120px]">
                  <i class="pi pi-map-marker mr-1"></i>{{ item.locality_name || 'Región Aysén' }}
                </span>
              </div>
              
              <button 
                @click="planStore.toggleInteres(item.id)"
                :class="[
                  'w-10 h-10 rounded-xl flex items-center justify-center transition-all transform active:scale-95',
                  isSelected(item.id) 
                    ? 'bg-blue-600 text-white shadow-lg' 
                    : 'bg-gray-50 text-gray-400 hover:bg-blue-50 hover:text-blue-600'
                ]"
              >
                <i :class="isSelected(item.id) ? 'pi pi-heart-fill' : 'pi pi-heart'"></i>
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Resumen Flotante / Inferior -->
      <div v-if="planStore.pasos.intereses.length > 0" class="bg-blue-900 text-white p-6 rounded-2xl shadow-2xl flex flex-col md:flex-row items-center justify-between animate-slide-up sticky bottom-4 z-50">
        <div class="flex items-center space-x-4 mb-4 md:mb-0">
          <div class="w-12 h-12 bg-blue-800 rounded-xl flex items-center justify-center text-xl">
             <i class="pi pi-heart-fill text-pink-400"></i>
          </div>
          <div>
            <h4 class="font-black text-lg">{{ planStore.pasos.intereses.length }} Intereses Seleccionados</h4>
            <p class="text-blue-300 text-xs">Se distribuirán estratégicamente en tu viaje.</p>
          </div>
        </div>
        <div class="flex space-x-2">
            <button @click="planStore.pasos.intereses = []" class="px-4 py-2 text-xs font-bold text-blue-300 hover:text-white transition-colors uppercase">Limpiar Todo</button>
        </div>
      </div>

      <!-- Navegación -->
      <div class="flex justify-between items-center pt-8 border-t border-gray-100 mt-12">
        <router-link
          to="/plan/4"
          class="flex items-center space-x-2 text-gray-400 hover:text-gray-700 font-bold transition-colors group"
        >
          <i class="pi pi-arrow-left group-hover:-translate-x-1 transition-transform"></i>
          <span>Volver</span>
        </router-link>
        
        <div class="flex items-center space-x-6">
          <span class="hidden md:block text-[10px] text-gray-400 font-bold uppercase tracking-widest">
            Paso 5 de 6
          </span>
          <router-link
            to="/plan/6"
            class="group bg-blue-600 hover:bg-blue-700 text-white px-10 py-4 rounded-xl font-bold text-lg shadow-blue-200 shadow-xl transform active:scale-95 transition-all flex items-center space-x-3"
          >
            <span>Continuar</span>
            <i class="pi pi-arrow-right group-hover:translate-x-1 transition-transform"></i>
          </router-link>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { usePlanStore } from '../store'
import axios from '@/services/axios'
import WizardProgress from '../components/WizardProgress.vue'

const planStore = usePlanStore()
const loading = ref(true)
const items = ref([])
const allCategories = ref([])
const rootCategories = ref([])
const selectedCategoryId = ref(null)
const searchQuery = ref('')

onMounted(async () => {
  try {
    // Cargar todas las categorías
    const { data: cats } = await axios.get('/admin/categories')
    allCategories.value = cats
    // Filtrar solo las raíces que son de naturaleza o aventura o lo que sea relevante
    rootCategories.value = cats.filter(c => !c.parent_id && c.is_active)
    
    // Cargar items (solo los activos y con coordenadas)
    const { data: catItems } = await axios.get('/admin/items', { 
        params: { active_only: true } 
    })
    // Filtrar los que tengan sentido para un viaje (places y activities)
    // Permitir cualquier item con coordenadas
    items.value = catItems.filter(i => i.lat && i.lng)
  } catch (err) {
    console.error('Error cargando catálogo:', err)
  } finally {
    loading.value = false
  }
})

// Función para verificar si una categoría es descendiente de otra
const isDescendant = (childId, rootId) => {
  if (!childId) return false
  if (childId === rootId) return true
  
  const child = allCategories.value.find(c => c.id === childId)
  if (!child || !child.parent_id) return false
  
  return isDescendant(child.parent_id, rootId)
}

const filteredItems = computed(() => {
  return items.value.filter(item => {
    // 1. Búsqueda por texto
    const q = searchQuery.value.toLowerCase()
    const matchesSearch = !searchQuery.value || 
                          (item.name && item.name.toLowerCase().includes(q)) ||
                          (item.description && item.description.toLowerCase().includes(q))
    
    // 2. Filtro por Categoría (Jerárquico)
    const matchesCategory = !selectedCategoryId.value || isDescendant(item.category_id, selectedCategoryId.value)
    
    return matchesSearch && matchesCategory
  })
})

const toggleCategory = (id) => {
  if (selectedCategoryId.value === id) selectedCategoryId.value = null
  else selectedCategoryId.value = id
}

const isSelected = (id) => planStore.pasos.intereses.includes(id)

const formatCurrency = (val) => new Intl.NumberFormat('es-CL', { style: 'currency', currency: 'CLP', maximumFractionDigits: 0 }).format(val)

const getTypeColor = (type) => {
  switch(type) {
    case 'place': return 'bg-orange-100 text-orange-600'
    case 'activity': return 'bg-blue-100 text-blue-600'
    case 'lodging': return 'bg-indigo-100 text-indigo-600'
    default: return 'bg-gray-100 text-gray-600'
  }
}

const handleSearch = () => {
  // debounce if needed, but for small sets it's fine
}
</script>

<style scoped>
.font-display { font-family: 'Outfit', sans-serif; }
.scrollbar-none::-webkit-scrollbar { display: none; }
.scrollbar-none { -ms-overflow-style: none; scrollbar-width: none; }

.animate-slide-up {
  animation: slideUp 0.4s ease-out;
}

@keyframes slideUp {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}
</style>
