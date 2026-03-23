<template>
  <div class="flex items-center relative origin-left w-max z-50">

    <div 
      @click.stop="showMenu = !showMenu"
      class="group/segment cursor-pointer bg-white border px-2 py-1 rounded-full shadow-sm flex items-center relative z-10 transition-all hover:shadow-md hover:border-blue-300 active:scale-95"
      :class="containerClass"
      :title="'Modo: ' + segment.transport_mode"
    >
      <i :class="[modeIcon, 'text-[10px] mr-1.5', iconColorClass]"></i>
      
      <span class="text-[10px] font-black mr-1" :class="textColorClass">
        {{ segment.distance_km }} km
      </span>
      
      <span class="text-[9px] text-gray-400 font-bold opacity-60 group-hover/segment:opacity-100 transition-opacity">
        ~{{ segment.duration_minutes }} min
      </span>

      <!-- Mini Dropdown Indicator -->
      <i class="pi pi-chevron-down text-[8px] ml-1.5 text-gray-300 group-hover/segment:text-blue-400 transition-colors"></i>
    </div>

    <!-- Modal de Selección de Transporte -->
    <Dialog 
      v-model:visible="showMenu" 
      modal 
      header="Medio de Transporte" 
      :style="{ width: '95vw', maxWidth: '320px' }" 
      :dismissableMask="true"
      class="transport-modal"
    >
      <div class="flex flex-col space-y-1 mt-1">
        <button 
          v-for="mode in modesCycle" 
          :key="mode"
          @click.stop="selectMode(mode)"
          class="flex items-center space-x-3 px-3 py-2 rounded-xl border border-transparent transition-all active:scale-[0.98]"
          :class="mode === segment.transport_mode ? 'bg-blue-50 text-blue-700 font-bold border-blue-100' : 'bg-white text-gray-700 hover:bg-gray-50'"
        >
          <div class="w-8 h-8 min-w-[32px] max-w-[32px] min-h-[32px] max-h-[32px] rounded-full flex flex-col justify-center items-center shrink-0" :class="mode === segment.transport_mode ? 'bg-blue-100 text-blue-600' : 'bg-gray-100 text-gray-500'">
            <i :class="[getIcon(mode), 'text-sm']"></i>
          </div>
          <span class="text-sm flex-1 text-left uppercase font-black tracking-wide">{{ getLabel(mode) }}</span>
          <i v-if="mode === segment.transport_mode" class="pi pi-check-circle text-xl text-blue-500"></i>
        </button>
      </div>
    </Dialog>

    <!-- Puntos de carga (opcional si está recalculando) -->
    <i v-if="loading" class="pi pi-spin pi-spinner text-[10px] text-blue-400 ml-2"></i>
  </div>
</template>

<script setup>
import { computed, ref } from 'vue'

const props = defineProps({
  segment: {
    type: Object,
    required: true
  },
  loading: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['change-mode'])

const showMenu = ref(false)

const getIcon = (mode) => {
  const icons = {
    car: 'pi pi-car',
    walk: 'pi pi-walking',
    bus: 'pi pi-bus',
    ferry: 'pi pi-ship',
    flight: 'pi pi-send',
    unknown: 'pi pi-question-circle'
  }
  return icons[mode] || icons.unknown
}

const getLabel = (mode) => {
  const labels = {
    car: 'Auto / Vehículo',
    walk: 'Caminar',
    bus: 'Bus / Transfer',
    ferry: 'Barco / Ferry',
    flight: 'Vuelo / Avión'
  }
  return labels[mode] || mode
}

const modeIcon = computed(() => getIcon(props.segment.transport_mode))


const containerClass = computed(() => {
  const modes = {
    car: 'border-blue-100',
    walk: 'border-orange-100',
    bus: 'border-indigo-100',
    ferry: 'border-cyan-100',
    flight: 'border-gray-100',
    unknown: 'border-gray-100'
  }
  return modes[props.segment.transport_mode] || modes.unknown
})

const iconColorClass = computed(() => {
  const modes = {
    car: 'text-blue-500',
    walk: 'text-orange-500',
    bus: 'text-indigo-500',
    ferry: 'text-cyan-600',
    flight: 'text-gray-500',
    unknown: 'text-gray-400'
  }
  return modes[props.segment.transport_mode] || modes.unknown
})

const textColorClass = computed(() => {
  const modes = {
    car: 'text-blue-700',
    walk: 'text-orange-700',
    bus: 'text-indigo-700',
    ferry: 'text-cyan-800',
    flight: 'text-gray-700',
    unknown: 'text-gray-600'
  }
  return modes[props.segment.transport_mode] || modes.unknown
})

const modesCycle = ['car', 'walk', 'bus', 'ferry', 'flight']

const selectMode = (mode) => {
  showMenu.value = false
  if (mode !== props.segment.transport_mode) {
    emit('change-mode', mode)
  }
}
</script>

<style scoped>
.group\/segment:hover .pi-chevron-down {
  transform: translateY(1px);
}
</style>
