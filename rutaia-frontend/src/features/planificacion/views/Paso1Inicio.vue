<template>
  <div class="w-full max-w-3xl mx-auto px-4 py-4 sm:py-8">
    <WizardProgress :current-step="1" />

    <div class="bg-white p-8 rounded-2xl shadow-xl border border-gray-100 space-y-8 animate-fade-in">
      <div class="text-center">
        <h2 class="text-3xl font-extrabold text-blue-900 mb-2">¡Empecemos tu aventura!</h2>
        <p class="text-gray-500">Cuéntanos desde dónde iniciarás tu viaje para darte las mejores opciones.</p>
      </div>

      <!-- Selección de ciudad -->
      <div class="space-y-4">
        <label class="block text-sm font-bold text-gray-700 uppercase tracking-wider">Ciudad de inicio</label>
        <div class="relative group">
          <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
            <i class="pi pi-map-marker text-blue-500 group-focus-within:text-blue-600 transition-colors"></i>
          </div>
          <select
            v-model="form.origen"
            class="block w-full pl-10 pr-4 py-4 bg-gray-50 border-2 border-gray-200 rounded-xl focus:border-blue-500 focus:bg-white focus:ring-4 focus:ring-blue-100 transition-all outline-none appearance-none text-lg font-medium text-gray-900"
          >
            <option disabled :value="null">-- Selecciona una ciudad --</option>
            <option v-for="c in ciudades" :key="c.id" :value="c">
              {{ c.nombre }}
            </option>
          </select>
          <div class="absolute inset-y-0 right-0 pr-3 flex items-center pointer-events-none">
            <i class="pi pi-chevron-down text-gray-400"></i>
          </div>
        </div>
      </div>

      <!-- Navegación -->
      <div class="flex justify-end pt-4">
        <button
          @click="nextStep"
          class="group bg-blue-600 hover:bg-blue-700 text-white px-8 py-4 rounded-xl font-bold text-lg shadow-blue-200 shadow-lg transform active:scale-95 transition-all flex items-center space-x-2"
        >
          <span>Siguiente</span>
          <i class="pi pi-arrow-right group-hover:translate-x-1 transition-transform"></i>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from '@/services/axios'
import { useRouter } from 'vue-router'
import { usePlanStore } from '../store'
import WizardProgress from '../components/WizardProgress.vue'

const planStore = usePlanStore()
const form = planStore.pasos

// Lista reactiva de ciudades
const ciudades = ref([])

// Router para navegación
const router = useRouter()

// Al montar, carga las ciudades activas desde el backend
onMounted(async () => {
  try {
    const { data } = await axios.get('/ciudades')
    ciudades.value = data
  } catch (err) {
    console.error('Error al cargar ciudades:', err)
    // alert('No se pudieron cargar las ciudades. Intenta más tarde.')
  }
})

// Avanza al siguiente paso validando selección
function nextStep() {
  if (!form.origen) {
    alert('Por favor selecciona una ciudad para continuar.')
    return
  }
  router.push('/plan/2')
}
</script>
