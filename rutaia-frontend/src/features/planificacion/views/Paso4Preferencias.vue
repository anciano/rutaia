<template>
  <div class="w-full max-w-3xl mx-auto px-4 py-4 sm:py-8">
    <WizardProgress :current-step="4" />

    <div class="bg-white p-8 rounded-2xl shadow-xl border border-gray-100 space-y-8 animate-fade-in">
      <div class="text-center">
        <h2 class="text-3xl font-extrabold text-blue-900 mb-2">Tus intereses</h2>
        <p class="text-gray-500">Selecciona lo que más te motiva. Personalizaremos tu ruta según estas opciones.</p>
      </div>

      <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <div
          v-for="pref in preferenciasDisponibles"
          :key="pref.id"
          @click="toggleSeleccion(pref)"
          :class="[
            'group cursor-pointer p-6 rounded-2xl border-2 transition-all relative overflow-hidden',
            estaSeleccionada(pref) 
              ? 'bg-blue-600 border-blue-600 text-white shadow-lg shadow-blue-200 ring-4 ring-blue-50' 
              : 'bg-gray-50 border-gray-100 text-gray-700 hover:border-blue-300 hover:bg-white'
          ]"
        >
          <!-- Icono de fondo decorativo -->
          <div class="absolute -right-4 -bottom-4 opacity-10 transition-transform group-hover:scale-110">
             <i class="pi pi-compass text-6xl"></i>
          </div>

          <div class="flex items-start space-x-4 relative z-10">
            <div 
              :class="[
                'w-12 h-12 rounded-xl flex items-center justify-center text-xl transition-colors',
                estaSeleccionada(pref) ? 'bg-blue-500 text-white' : 'bg-white text-blue-600 shadow-sm'
              ]"
            >
              <i :class="getIcon(pref.nombre)"></i>
            </div>
            <div class="flex-1">
              <h3 class="font-bold text-lg leading-tight">{{ pref.nombre }}</h3>
              <p :class="['text-xs mt-1', estaSeleccionada(pref) ? 'text-blue-100' : 'text-gray-500']">
                {{ pref.descripcion }}
              </p>
            </div>
            <div v-if="estaSeleccionada(pref)" class="animate-bounce-in">
              <i class="pi pi-check-circle text-xl"></i>
            </div>
          </div>
        </div>
      </div>

      <!-- Navegación -->
      <div class="flex justify-between items-center pt-8 border-t border-gray-100">
        <router-link
          to="/plan/3"
          class="flex items-center space-x-2 text-gray-500 hover:text-gray-700 font-bold transition-colors"
        >
          <i class="pi pi-arrow-left"></i>
          <span>Volver</span>
        </router-link>
        <router-link
          to="/plan/5"
          :class="[
            'group px-8 py-4 rounded-xl font-bold shadow-lg transform active:scale-95 transition-all flex items-center space-x-2',
            form.preferencias.length > 0 ? 'bg-blue-600 text-white shadow-blue-200' : 'bg-gray-200 text-gray-400 cursor-not-allowed shadow-none'
          ]"
        >
          <span>Siguiente</span>
          <i class="pi pi-arrow-right group-hover:translate-x-1 transition-transform"></i>
        </router-link>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from '@/services/axios'
import { usePlanStore } from '../store'
import WizardProgress from '../components/WizardProgress.vue'

const planStore = usePlanStore()
const form = planStore.pasos
const preferenciasDisponibles = ref([])

const getIcon = (nombre) => {
  const icons = {
    'Cultura': 'pi pi-palette',
    'Naturaleza': 'pi pi-sun',
    'Aventura': 'pi pi-bolt',
    'Gastronomía': 'pi pi-utensils',
    'Relajación': 'pi pi-coffee',
    'Deportes': 'pi pi-target',
    'Historia': 'pi pi-book',
    'Vida Nocturna': 'pi pi-moon'
  }
  return icons[nombre] || 'pi pi-tag'
}

onMounted(async () => {
  try {
    const res = await axios.get('/preferencias')
    preferenciasDisponibles.value = res.data
  } catch (error) {
    console.error('Error cargando preferencias:', error)
  }
})

const toggleSeleccion = (pref) => {
  const index = form.preferencias.findIndex(p => p.id === pref.id)
  if (index === -1) {
    form.preferencias.push(pref)
  } else {
    form.preferencias.splice(index, 1)
  }
}

const estaSeleccionada = (pref) => {
  return form.preferencias.some(p => p.id === pref.id)
}
</script>