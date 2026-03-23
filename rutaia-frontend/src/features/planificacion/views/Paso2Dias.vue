<template>
  <div class="w-full max-w-3xl mx-auto px-4 py-4 sm:py-8">
    <WizardProgress :current-step="2" />

    <div class="bg-white p-8 rounded-2xl shadow-xl border border-gray-100 space-y-8 animate-fade-in">
      <div class="text-center">
        <h2 class="text-3xl font-extrabold text-blue-900 mb-2">¿Cuándo viajas?</h2>
        <p class="text-gray-500">Define la duración de tu estancia para organizar mejor tus días.</p>
      </div>

      <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
        <!-- Fecha Inicio -->
        <div class="space-y-2">
          <label class="block text-sm font-bold text-gray-700 uppercase tracking-wider">Fecha de inicio</label>
          <div class="relative group">
            <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
              <i class="pi pi-calendar text-blue-500"></i>
            </div>
            <input 
              v-model="fechaInicio" 
              type="date" 
              class="block w-full pl-10 pr-4 py-3 bg-gray-50 border-2 border-gray-200 rounded-xl focus:border-blue-500 focus:bg-white focus:ring-4 focus:ring-blue-100 transition-all outline-none text-gray-900" 
            />
          </div>
        </div>

        <!-- Cantidad de Días -->
        <div class="space-y-2">
          <label class="block text-sm font-bold text-gray-700 uppercase tracking-wider">Cantidad de días</label>
          <div class="relative group">
            <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
              <i class="pi pi-clock text-blue-500"></i>
            </div>
            <input 
              v-model.number="dias" 
              type="number" 
              min="1" 
              max="30"
              class="block w-full pl-10 pr-4 py-3 bg-gray-50 border-2 border-gray-200 rounded-xl focus:border-blue-500 focus:bg-white focus:ring-4 focus:ring-blue-100 transition-all outline-none text-gray-900" 
              placeholder="Ej: 5"
            />
          </div>
        </div>
      </div>

      <div v-if="fechaFin" class="bg-blue-50 p-4 rounded-xl border border-blue-100 flex items-center space-x-3 mt-4">
        <div class="bg-white p-2 rounded-lg shadow-sm">
          <i class="pi pi-info-circle text-blue-600"></i>
        </div>
        <div>
          <p class="text-blue-900 font-semibold text-sm">Fin de aventura:</p>
          <p class="text-blue-700 font-mono text-xs">{{ dayjs(fechaFin).format('DD MMM YYYY') }}</p>
        </div>
      </div>

      <!-- Selección de Transporte -->
      <div class="space-y-4 pt-4 border-t border-gray-100">
        <label class="block text-sm font-bold text-gray-700 uppercase tracking-wider">Modo de Transporte (MVP)</label>
        <div class="grid grid-cols-2 gap-3">
          <button 
            v-for="mode in transportModes" 
            :key="mode.id"
            @click="form.transport_mode = mode.id"
            :class="[
              'p-4 rounded-xl border-2 transition-all flex flex-col items-center justify-center space-y-2 text-center',
              form.transport_mode === mode.id 
                ? 'bg-blue-600 border-blue-600 text-white shadow-lg' 
                : 'bg-gray-50 border-gray-100 text-gray-500 hover:border-blue-200'
            ]"
          >
            <i :class="[mode.icon, 'text-xl']"></i>
            <span class="text-[10px] font-bold uppercase leading-tight">{{ mode.label }}</span>
          </button>
        </div>
      </div>

      <div class="mt-8 flex justify-between items-center pt-6 border-t border-gray-100">
        <button 
          @click="volver" 
          class="flex items-center space-x-2 text-gray-500 hover:text-gray-700 font-bold transition-colors"
        >
          <i class="pi pi-arrow-left"></i>
          <span>Volver</span>
        </button>
        <button 
          @click="siguiente" 
          class="group bg-blue-600 hover:bg-blue-700 text-white px-8 py-3 rounded-xl font-bold shadow-blue-200 shadow-lg transform active:scale-95 transition-all flex items-center space-x-2"
        >
          <span>Siguiente</span>
          <i class="pi pi-arrow-right group-hover:translate-x-1 transition-transform"></i>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import dayjs from 'dayjs'
import { usePlanStore } from '../store'
import WizardProgress from '../components/WizardProgress.vue'

const router = useRouter()
const planStore = usePlanStore()
const form = planStore.pasos

const dias = ref(form.dias || 1)
const fechaInicio = ref(form.fecha_inicio || '')
const fechaFin = ref('')

const transportModes = [
  { id: 'auto_propio', label: 'Auto propio', icon: 'pi pi-car' },
  { id: 'arrendar_auto', label: 'Arrendar auto', icon: 'pi pi-key' },
  { id: 'transporte_publico', label: 'Transporte público', icon: 'pi pi-bus' },
  { id: 'movilidad_local', label: 'Movilidad local', icon: 'pi pi-users' }
]

// Initialize default if not set
if (!form.transport_mode) {
  form.transport_mode = 'auto_propio'
}

// Calcular fecha fin automáticamente
const updateFechaFin = () => {
  if (fechaInicio.value && dias.value > 0) {
    fechaFin.value = dayjs(fechaInicio.value).add(dias.value - 1, 'day').format('YYYY-MM-DD')
  } else {
    fechaFin.value = ''
  }
}

watch([fechaInicio, dias], updateFechaFin)
onMounted(updateFechaFin)

function siguiente() {
  if (!fechaInicio.value || !dias.value) {
    alert("Completa los campos para continuar.")
    return
  }

  form.dias = dias.value
  form.fecha_inicio = fechaInicio.value
  form.fecha_fin = fechaFin.value

  router.push('/plan/3')
}

function volver() {
  router.push('/plan/1')
}
</script>
