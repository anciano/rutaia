<template>
  <div class="w-full max-w-3xl mx-auto px-4 py-4 sm:py-8">
    <WizardProgress :current-step="6" />

    <div class="bg-white p-8 rounded-2xl shadow-xl border border-gray-100 space-y-8 animate-fade-in relative overflow-hidden">
      <!-- Loading Overlay -->
      <div v-if="planStore.loading" class="absolute inset-0 bg-white/80 backdrop-blur-sm z-50 flex flex-col items-center justify-center space-y-4">
        <div class="w-16 h-16 border-4 border-blue-600 border-t-transparent rounded-full animate-spin"></div>
        <p class="text-blue-900 font-bold text-xl animate-pulse">{{ planStore.generationStatus || 'Generando tu ruta ideal...' }}</p>
        <p class="text-gray-500 text-sm">Estamos buscando los mejores lugares para ti.</p>
      </div>

      <div class="text-center">
        <h2 class="text-3xl font-extrabold text-blue-900 mb-2">¡Todo listo!</h2>
        <p class="text-gray-500">Revisa los detalles finales antes de generar tu itinerario.</p>
      </div>

      <div class="space-y-6">
        <!-- Card Resumen Principal -->
        <div class="bg-blue-50 rounded-2xl p-6 border border-blue-100 grid grid-cols-1 sm:grid-cols-3 gap-6">
          <div class="text-center sm:text-left">
            <span class="text-[10px] font-bold text-blue-400 uppercase tracking-widest">Destino</span>
            <p class="text-xl font-black text-blue-900">{{ resumen.origen }}</p>
          </div>
          <div class="text-center border-x border-blue-100 px-4">
            <span class="text-[10px] font-bold text-blue-400 uppercase tracking-widest">Duración</span>
            <p class="text-xl font-black text-blue-900">{{ resumen.dias }} Días</p>
          </div>
          <div class="text-center sm:text-right">
            <span class="text-[10px] font-bold text-blue-400 uppercase tracking-widest">Presupuesto</span>
            <p class="text-xl font-black text-blue-900">${{ resumen.presupuesto.toLocaleString() }}</p>
          </div>
        </div>

        <!-- Transporte -->
        <div class="bg-gray-50 rounded-2xl p-4 border border-gray-100 flex items-center justify-between">
          <div class="flex items-center space-x-3">
            <div class="w-10 h-10 bg-white rounded-xl shadow-sm flex items-center justify-center text-blue-600">
              <i :class="resumen.transportIcon"></i>
            </div>
            <div>
              <span class="text-[9px] font-bold text-gray-400 uppercase tracking-wider leading-none">Movilidad Seleccionada</span>
              <p class="text-sm font-bold text-gray-700 leading-tight">{{ resumen.transportModeLabel }}</p>
            </div>
          </div>
          <div class="text-right">
             <span class="text-[9px] font-bold text-gray-400 uppercase tracking-wider leading-none sm:block hidden">Fechas</span>
             <p class="text-[10px] font-bold text-blue-600">{{ resumen.fechas }}</p>
          </div>
        </div>

        <!-- Participantes Recap -->
        <div class="space-y-3">
          <h3 class="text-sm font-bold text-gray-400 uppercase tracking-wider">Grupo de viaje</h3>
          <div class="flex flex-wrap gap-2">
            <div 
              v-for="(p, i) in resumen.participantes" 
              :key="i"
              class="bg-white border border-gray-200 px-4 py-2 rounded-xl text-sm font-semibold flex items-center space-x-2 shadow-sm"
            >
              <i class="pi pi-user text-blue-500"></i>
              <span>{{ p.edad }} años</span>
              <i v-if="p.discapacidad" class="pi pi-accessibility text-blue-600 ml-1" title="Accesibilidad requerida"></i>
            </div>
          </div>
        </div>

        <!-- Preferencias Recap -->
        <div class="space-y-3">
          <h3 class="text-sm font-bold text-gray-400 uppercase tracking-wider">Perfiles de viaje</h3>
          <div class="flex flex-wrap gap-2">
            <span 
              v-for="(nombre, idx) in resumen.preferencias" 
              :key="idx"
              class="bg-blue-100 text-blue-600 px-4 py-2 rounded-full text-xs font-bold"
            >
              {{ nombre }}
            </span>
          </div>
        </div>

        <!-- Bolsa de Intereses Recap -->
        <div v-if="planStore.pasos.intereses.length > 0" class="space-y-3">
          <h3 class="text-sm font-bold text-gray-400 uppercase tracking-wider">Bolsa de intereses</h3>
          <div class="p-4 bg-pink-50 rounded-xl border border-pink-100 flex items-center justify-between">
            <div class="flex items-center space-x-3">
              <i class="pi pi-heart-fill text-pink-500"></i>
              <span class="text-sm font-bold text-pink-900">{{ planStore.pasos.intereses.length }} lugares seleccionados</span>
            </div>
            <router-link to="/plan/5" class="text-xs font-bold text-pink-600 hover:underline">Ver / Editar</router-link>
          </div>
        </div>
      </div>

      <!-- Navegación -->
      <div class="flex justify-between items-center pt-8 border-t border-gray-100">
        <router-link
          to="/plan/5"
          class="flex items-center space-x-2 text-gray-500 hover:text-gray-700 font-bold transition-colors"
        >
          <i class="pi pi-arrow-left"></i>
          <span>Volver</span>
        </router-link>
        <button
          @click="confirmar"
          :disabled="planStore.loading"
          class="group bg-green-600 hover:bg-green-700 text-white px-10 py-4 rounded-2xl font-black text-xl shadow-green-200 shadow-xl transform active:scale-95 transition-all flex items-center space-x-3 disabled:opacity-50"
        >
          <i class="pi pi-sparkles"></i>
          <span>¡Generar Itinerario!</span>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { usePlanStore } from '../store'
import { useUserStore } from '@/features/user/store'
import { useRouter } from 'vue-router'
import dayjs from 'dayjs'
import 'dayjs/locale/es'

dayjs.locale('es')

const planStore = usePlanStore()
const userStore = useUserStore()
const router = useRouter()

const form = planStore.pasos

// Construimos el resumen para la vista
const resumen = {
  origen       : form.origen?.nombre || '',
  dias         : form.dias,
  presupuesto  : form.presupuesto,
  participantes: form.participantes,
  preferencias : form.preferencias.map(p => p.nombre || p),
  transportModeLabel: getTransportModeLabel(form.transport_mode),
  transportIcon: getTransportModeIcon(form.transport_mode),
  fechas: `${dayjs(form.fecha_inicio).format('DD MMM')} - ${dayjs(form.fecha_fin).format('DD MMM YYYY')}`
}

function getTransportModeLabel(mode) {
  const modes = {
    'auto_propio': 'Auto propio',
    'arrendar_auto': 'Arrendar auto',
    'transporte_publico': 'Transporte público',
    'movilidad_local': 'Movilidad local'
  }
  return modes[mode] || 'Cualquier medio'
}

function getTransportModeIcon(mode) {
  const icons = {
    'auto_propio': 'pi pi-car',
    'arrendar_auto': 'pi pi-key',
    'transporte_publico': 'pi pi-bus',
    'movilidad_local': 'pi pi-users'
  }
  return icons[mode] || 'pi pi-directions'
}

async function confirmar() {
  try {
    if (!userStore.user?.id) {
       alert('Usuario no identificado. Por favor reingresa.')
       return
    }
    
    planStore.setUserId(userStore.user.id)
    const data = await planStore.crearPlan()
    
    localStorage.setItem('planCompletado', 'true')
    
    // Refrescar planes del usuario en el store global
    await userStore.loadPlans()
    
    // Redirigir al historial o al detalle del nuevo plan
    if (data.plan_id) {
      router.push(`/plan/${data.plan_id}`)
    } else {
      router.push('/historial')
    }
  } catch (err) {
    console.error('Error al guardar planificación:', err)
    alert('Ocurrió un error al guardar: ' + (err.response?.data?.detail || err.message))
  }
}
</script>

<style scoped>
/* Ajustes opcionales */
table th,
table td {
  vertical-align: middle;
}
</style>
