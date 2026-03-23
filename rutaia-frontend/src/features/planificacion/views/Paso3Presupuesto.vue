<template>
  <div class="w-full max-w-3xl mx-auto px-4 py-4 sm:py-8">
    <WizardProgress :current-step="3" />

    <div class="bg-white p-8 rounded-2xl shadow-xl border border-gray-100 space-y-8 animate-fade-in">
      <div class="text-center">
        <h2 class="text-3xl font-extrabold text-blue-900 mb-2">Presupuesto y Compañeros</h2>
        <p class="text-gray-500">Ajusta tu presupuesto total y detalla quiénes te acompañarán.</p>
      </div>

      <!-- Presupuesto total -->
      <div class="space-y-4">
        <label class="block text-sm font-bold text-gray-700 uppercase tracking-wider text-center">Presupuesto total (CLP)</label>
        <div class="relative max-w-sm mx-auto group">
          <div class="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
            <span class="text-2xl font-bold text-blue-500">$</span>
          </div>
          <input
            v-model.number="form.presupuesto"
            type="number"
            min="0"
            step="10000"
            placeholder="Ej: 600.000"
            class="block w-full pl-10 pr-4 py-4 bg-blue-50 border-2 border-blue-100 rounded-2xl focus:border-blue-500 focus:bg-white focus:ring-4 focus:ring-blue-100 transition-all outline-none text-3xl font-black text-blue-700 text-center"
          />
        </div>
      </div>

      <!-- Participantes -->
      <div class="space-y-6">
        <div class="flex items-center justify-between border-b border-gray-100 pb-4">
          <h3 class="text-xl font-bold text-gray-800">Grupo de Viaje</h3>
          <button
            @click="addPersona"
            class="flex items-center space-x-2 bg-blue-50 text-blue-600 hover:bg-blue-100 px-4 py-2 rounded-lg font-bold transition-colors"
          >
            <i class="pi pi-plus-circle"></i>
            <span>Añadir persona</span>
          </button>
        </div>

        <div class="grid grid-cols-1 gap-4">
          <div
            v-for="(p, i) in form.participantes"
            :key="i"
            class="group relative bg-gray-50 p-6 rounded-2xl border-2 border-transparent hover:border-blue-200 hover:bg-white hover:shadow-md transition-all flex flex-wrap items-center gap-6"
          >
            <!-- Badge Numero -->
            <div class="w-10 h-10 bg-blue-100 text-blue-600 rounded-full flex items-center justify-center font-bold">
              {{ i + 1 }}
            </div>

            <!-- Edad -->
            <div class="flex-1 min-w-[120px] space-y-1">
              <label class="text-[10px] font-bold text-gray-400 uppercase">Edad</label>
              <input
                v-model.number="p.edad"
                type="number"
                min="0"
                placeholder="Años"
                class="w-full bg-transparent border-b-2 border-gray-200 focus:border-blue-500 outline-none py-1 font-semibold text-lg text-gray-900"
              />
            </div>

            <!-- Discapacidad Toggle -->
            <div class="flex items-center space-x-3 bg-white px-4 py-2 rounded-xl border border-gray-100 shadow-sm">
              <i class="pi pi-accessibility" :class="p.discapacidad ? 'text-blue-600' : 'text-gray-300'"></i>
              <label class="flex items-center cursor-pointer select-none">
                <input
                  type="checkbox"
                  v-model="p.discapacidad"
                  class="sr-only peer"
                />
                <div class="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full rtl:peer-checked:after:-translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:start-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600 relative"></div>
                <span class="ms-3 text-sm font-medium text-gray-700">Necesita acceso PMR</span>
              </label>
            </div>

            <!-- Tipo Discapacidad -->
            <div v-if="p.discapacidad" class="flex-1 min-w-[150px] space-y-1 animate-scale-in">
              <label class="text-[10px] font-bold text-gray-400 uppercase">Tipo</label>
              <select
                v-model="p.tipo_discapacidad"
                class="w-full bg-transparent border-b-2 border-gray-200 focus:border-blue-500 outline-none py-1 font-semibold text-gray-900"
              >
                <option disabled value="">Selecciona...</option>
                <option value="motora">Motora</option>
                <option value="visual">Visual</option>
                <option value="auditiva">Auditiva</option>
                <option value="intelectual">Intelectual</option>
                <option value="multiple">Múltiple</option>
              </select>
            </div>

            <!-- Eliminar -->
            <button
              v-if="form.participantes.length > 1"
              @click.stop="remove(i)"
              class="absolute -top-2 -right-2 bg-red-100 text-red-600 w-8 h-8 rounded-full flex items-center justify-center shadow-sm hover:bg-red-600 hover:text-white transition-colors z-10"
              title="Eliminar persona"
            >
              <i class="pi pi-times text-xs"></i>
            </button>
          </div>
        </div>
      </div>

      <!-- Navegación -->
      <div class="flex justify-between items-center pt-8 border-t border-gray-100">
        <button
          @click="router.push('/plan/2')"
          class="flex items-center space-x-2 text-gray-500 hover:text-gray-700 font-bold transition-colors"
        >
          <i class="pi pi-arrow-left"></i>
          <span>Volver</span>
        </button>
        <button
          @click="siguiente"
          class="group bg-blue-600 hover:bg-blue-700 text-white px-8 py-4 rounded-xl font-bold shadow-blue-200 shadow-lg transform active:scale-95 transition-all flex items-center space-x-2"
        >
          <span>Siguiente</span>
          <i class="pi pi-arrow-right group-hover:translate-x-1 transition-transform"></i>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { usePlanStore } from '../store'
import WizardProgress from '../components/WizardProgress.vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const planStore = usePlanStore()
const form = planStore.pasos

// Inicializa el array de participantes si está vacío
if (!Array.isArray(form.participantes) || form.participantes.length === 0) {
  form.participantes = [
    { edad: null, discapacidad: false, tipo_discapacidad: '' }
  ]
}

// Añade una nueva fila de participante
function addPersona() {
  form.participantes.push({
    edad: null,
    discapacidad: false,
    tipo_discapacidad: ''
  })
}

// Elimina la fila de participante, manteniendo al menos uno
function remove(idx) {
  if (form.participantes.length > 1) {
    form.participantes.splice(idx, 1)
  }
}

function siguiente() {
  // Validar que todos tengan edad
  const invalid = form.participantes.some(p => p.edad === null || p.edad === '' || p.edad < 0)
  if (invalid) {
    alert('Por favor, ingresa la edad de todos los participantes.')
    return
  }
  
  // Validar discapacidad
  const invalidDisability = form.participantes.some(p => p.discapacidad && !p.tipo_discapacidad)
  if (invalidDisability) {
    alert('Por favor, selecciona el tipo de discapacidad para quienes lo requieran.')
    return
  }

  router.push('/plan/4')
}
</script>

<style scoped>
/* Opcional: ajustar alturas de inputs para mejor alineación */
input[type="number"],
select {
  height: 2.5rem;
}
</style>
