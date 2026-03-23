<template>
  <Transition
    enter-active-class="transform transition ease-out duration-300"
    enter-from-class="translate-x-full opacity-0"
    enter-to-class="translate-x-0 opacity-100"
    leave-active-class="transform transition ease-in duration-200"
    leave-from-class="translate-x-0 opacity-100"
    leave-to-class="translate-x-full opacity-0"
  >
    <div v-if="visible" class="fixed top-[64px] right-4 bottom-8 w-80 bg-white shadow-2xl rounded-3xl z-[1100] border border-blue-100 flex flex-col overflow-hidden">
      <!-- Header -->
      <div class="px-6 py-4 bg-gradient-to-r from-blue-600 to-indigo-600 text-white flex justify-between items-center shrink-0">
        <div class="flex items-center space-x-2">
          <i class="pi pi-sparkles text-sm text-blue-200"></i>
          <h3 class="font-black text-xs uppercase tracking-widest">Sugerencias IA</h3>
        </div>
        <button @click="$emit('close')" class="hover:bg-white/20 p-1.5 rounded-xl transition-colors">
          <i class="pi pi-times text-[10px]"></i>
        </button>
      </div>

      <!-- Suggestions List -->
      <div class="flex-1 overflow-y-auto p-4 space-y-4 custom-scrollbar">
        <!-- Loading State -->
        <div v-if="loading" class="h-full flex flex-col items-center justify-center text-center p-6 space-y-4">
          <div class="w-16 h-16 bg-blue-50 rounded-2xl flex items-center justify-center text-blue-600">
            <i class="pi pi-spin pi-spinner text-3xl"></i>
          </div>
          <div>
            <h4 class="text-sm font-bold text-gray-700">Analizando tu ruta...</h4>
            <p class="text-[11px] text-gray-400 mt-1">La IA está buscando las mejores opciones para tu viaje.</p>
          </div>
        </div>

        <!-- Empty State -->
        <div v-else-if="suggestions.length === 0" class="h-full flex flex-col items-center justify-center text-center p-6 space-y-4">
          <div class="w-16 h-16 bg-blue-50 rounded-2xl flex items-center justify-center text-blue-200">
            <i class="pi pi-sparkles text-3xl"></i>
          </div>
          <div>
            <h4 class="text-sm font-bold text-gray-700">Sin sugerencias aún</h4>
            <p class="text-[11px] text-gray-400 mt-1">Presiona "Optimizar con IA" en el itinerario para que la IA analice tu ruta.</p>
          </div>
        </div>

        <div 
          v-else
          v-for="sug in suggestions" 
          :key="sug.id"
          class="bg-gray-50 rounded-2xl p-4 border border-transparent hover:border-blue-200 transition-all group relative overflow-hidden"
        >
          <!-- Background Decoration -->
          <div class="absolute -right-4 -top-4 w-16 h-16 bg-blue-500/5 rounded-full blur-xl group-hover:bg-blue-500/10 transition-colors"></div>

          <!-- Type Badge -->
          <div class="flex items-center justify-between mb-2">
            <span :class="['text-[9px] font-black uppercase px-2 py-0.5 rounded-lg border', getTypeStyles(sug.tipo)]">
              {{ sug.tipo }}
            </span>
          </div>

          <!-- Content -->
          <h4 class="font-bold text-gray-800 text-sm mb-1">{{ sug.titulo }}</h4>
          <p class="text-[11px] text-gray-500 leading-relaxed mb-3">
            {{ sug.descripcion }}
          </p>

          <!-- Justification -->
          <div class="bg-blue-50/50 rounded-xl p-2 mb-3 border border-blue-100/50">
            <p class="text-[10px] text-blue-700 italic">
              "{{ sug.justificacion }}"
            </p>
          </div>

          <!-- Impact Tags -->
          <div class="flex items-center space-x-2 mb-4">
            <div class="flex items-center text-[10px] font-bold text-gray-400 bg-white px-2 py-1 rounded-lg border border-gray-100">
              <i class="pi pi-clock mr-1 text-blue-400"></i>
              {{ sug.impacto.tiempo }}
            </div>
            <div class="flex items-center text-[10px] font-bold text-gray-400 bg-white px-2 py-1 rounded-lg border border-gray-100">
              <i class="pi pi-wallet mr-1 text-green-400"></i>
              {{ formatCLP(sug.impacto.presupuesto) }}
            </div>
          </div>

          <!-- Actions -->
          <div class="flex space-x-2">
            <button 
              @click="$emit('accept', sug)"
              class="flex-1 bg-blue-600 hover:bg-blue-700 text-white py-2 rounded-xl text-[10px] font-black shadow-md active:scale-95 transition-all flex items-center justify-center"
            >
              ACEPTAR
            </button>
            <button 
              @click="$emit('discard', sug)"
              class="flex-1 bg-white border border-gray-200 text-gray-400 hover:text-red-500 hover:bg-red-50 py-2 rounded-xl text-[10px] font-black active:scale-95 transition-all flex items-center justify-center"
            >
              DESCARTAR
            </button>
          </div>
        </div>
      </div>

      <!-- Footer Info -->
      <div class="p-4 bg-gray-50 border-t border-gray-100">
        <p class="text-[9px] text-gray-400 text-center font-bold uppercase tracking-tighter">
          IA optimizada • Carretera Austral v5.4
        </p>
      </div>
    </div>
  </Transition>
</template>

<script setup>
defineProps({
  visible: Boolean,
  loading: Boolean,
  suggestions: {
    type: Array,
    default: () => []
  }
})

defineEmits(['close', 'accept', 'discard'])

const formatCLP = (v) => new Intl.NumberFormat('es-CL', { style: 'currency', currency: 'CLP', maximumFractionDigits: 0 }).format(v || 0)

const getTypeStyles = (type) => {
  switch (type) {
    case 'agregar': return 'text-green-600 bg-green-50 border-green-100'
    case 'reemplazar': return 'text-orange-600 bg-orange-50 border-orange-100'
    case 'mover': return 'text-blue-600 bg-blue-50 border-blue-100'
    case 'eliminar': return 'text-red-600 bg-red-50 border-red-100'
    default: return 'text-gray-600 bg-gray-50 border-gray-100'
  }
}
</script>

<style scoped>
.custom-scrollbar::-webkit-scrollbar {
  width: 4px;
}
.custom-scrollbar::-webkit-scrollbar-thumb {
  background: #cbd5e1;
  border-radius: 10px;
}
</style>
