<template>
  <div class="mb-8">
    <div class="flex items-center justify-between relative">
      <!-- Linea de fondo -->
      <div class="absolute top-1/2 left-0 w-full h-1 bg-gray-200 -z-10 -translate-y-1/2"></div>
      
      <!-- Pasos -->
      <div 
        v-for="step in 6" 
        :key="step"
        class="flex flex-col items-center"
      >
        <div 
          :class="[
            'w-8 h-8 sm:w-10 sm:h-10 rounded-full flex items-center justify-center border-2 transition-all duration-300',
            currentStep >= step ? 'bg-blue-600 border-blue-600 text-white shadow-lg' : 'bg-white border-gray-300 text-gray-400'
          ]"
        >
          <i v-if="currentStep > step" class="pi pi-check text-xs"></i>
          <span v-else class="font-bold text-xs sm:text-base">{{ step }}</span>
        </div>
        <span 
          :class="[
            'mt-2 text-xs font-semibold hidden sm:block',
            currentStep >= step ? 'text-blue-700' : 'text-gray-400'
          ]"
        >
          {{ stepNames[step-1] }}
        </span>
      </div>
    </div>
  </div>
</template>

<script setup>
defineProps({
  currentStep: {
    type: Number,
    required: true
  }
})

const stepNames = [
  'Inicio',
  'Duración',
  'Presupuesto',
  'Intereses',
  'Bolsa',
  'Resumen'
]
</script>
