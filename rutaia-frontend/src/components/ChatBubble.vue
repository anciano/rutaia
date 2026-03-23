<template>
  <div class="fixed bottom-8 right-8 z-[2000] flex flex-col items-end">
    <!-- Chat Window -->
    <transition name="chat-window">
      <div v-if="isOpen" class="mb-4 w-80 sm:w-96 h-[500px] bg-white rounded-3xl shadow-2xl border border-gray-100 flex flex-col overflow-hidden">
        <!-- Chat Header -->
        <header class="bg-blue-600 p-4 text-white flex items-center justify-between">
          <div class="flex items-center space-x-2">
            <div class="bg-white/20 p-2 rounded-lg">
              <i class="pi pi-sparkles"></i>
            </div>
            <div>
              <p class="font-bold leading-none">Asistente RutaIA</p>
              <p class="text-[10px] opacity-70">IA Determinística Activa</p>
            </div>
          </div>
          <button @click="isOpen = false" class="hover:bg-white/10 p-1 rounded">
            <i class="pi pi-minus"></i>
          </button>
        </header>

        <!-- Messages Area -->
        <div class="flex-1 overflow-y-auto p-4 space-y-4 bg-gray-50/50 custom-scrollbar">
          <div v-for="(msg, i) in chatHistory" :key="i" :class="['flex', msg.role === 'user' ? 'justify-end' : 'justify-start']">
            <div :class="[
              'max-w-[90%] px-4 py-3 rounded-2xl text-sm shadow-sm transition-all',
              msg.role === 'user' ? 'bg-blue-600 text-white rounded-tr-none' : 'bg-white text-gray-800 border border-gray-100 rounded-tl-none'
            ]">
              <p :class="msg.role === 'user' ? '' : 'text-gray-700'">{{ msg.text }}</p>
              
              <!-- Sugerencias específicas de IA -->
              <div v-if="msg.suggestions" class="mt-4 space-y-3">
                <div v-for="sug in msg.suggestions" :key="sug.id" class="bg-blue-50/50 border border-blue-100 p-3 rounded-xl">
                  <span class="text-[9px] font-black uppercase text-blue-500 bg-blue-100 px-1.5 py-0.5 rounded-md mb-2 inline-block">{{ sug.tipo }}</span>
                  <h4 class="font-bold text-gray-800 text-xs mb-1">{{ sug.titulo }}</h4>
                  <p class="text-[10px] text-gray-500 mb-2 leading-relaxed">{{ sug.descripcion }}</p>
                  
                  <div class="flex space-x-2">
                    <button 
                      @click="$emit('accept-suggestion', sug)" 
                      class="flex-1 bg-blue-600 text-white py-1.5 rounded-lg text-[9px] font-black active:scale-95 transition-transform"
                    >
                      ACEPTAR
                    </button>
                    <button 
                      @click="$emit('discard-suggestion', sug)" 
                      class="flex-1 bg-white border border-gray-200 text-gray-400 py-1.5 rounded-lg text-[9px] font-black active:scale-95 transition-transform"
                    >
                      DESCARTAR
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>
          <div v-if="loading" class="flex justify-start">
             <div class="bg-white px-4 py-2 rounded-2xl border border-gray-100 flex space-x-1">
                <div class="w-1 h-1 bg-gray-400 rounded-full animate-bounce"></div>
                <div class="w-1 h-1 bg-gray-400 rounded-full animate-bounce [animation-delay:-0.15s]"></div>
                <div class="w-1 h-1 bg-gray-400 rounded-full animate-bounce [animation-delay:-0.3s]"></div>
             </div>
          </div>
        </div>

        <!-- Input Area -->
        <footer class="p-4 bg-white border-t border-gray-100 flex items-center space-x-2">
          <input 
            v-model="input" 
            @keyup.enter="send"
            placeholder="Escribe algo..." 
            class="flex-1 bg-gray-100 rounded-xl px-4 py-3 outline-none focus:ring-2 focus:ring-blue-600 transition-all text-sm"
          />
          <button @click="send" class="bg-blue-600 text-white p-3 rounded-xl hover:bg-blue-700 transition-colors shadow-lg shadow-blue-100">
            <i class="pi pi-send"></i>
          </button>
        </footer>
      </div>
    </transition>

    <!-- Bubble Button -->
    <button 
      @click="handleBubbleClick"
      :class="[
        'w-16 h-16 rounded-3xl shadow-2xl flex items-center justify-center transition-all transform active:scale-90 relative',
        (active || isOpen) ? 'bg-gray-100 text-gray-500' : 'bg-blue-600 text-white hover:bg-blue-700 hover:-translate-y-1'
      ]"
    >
      <i :class="[(active || isOpen) ? 'pi pi-times' : 'pi pi-sparkles', 'text-2xl']"></i>
      <div v-if="!(active || isOpen)" class="absolute -top-1 -right-1 w-4 h-4 bg-red-500 rounded-full border-2 border-white animate-pulse"></div>
    </button>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const props = defineProps({
  externalToggle: {
    type: Boolean,
    default: false
  },
  active: {
    type: Boolean,
    default: false
  },
  planId: {
    type: String,
    default: ''
  }
})

const isOpen = ref(false)
const input = ref('')
const loading = ref(false)

const emit = defineEmits(['accept-suggestion', 'discard-suggestion', 'click-bubble'])

const handleBubbleClick = () => {
  emit('click-bubble')
  if (!props.externalToggle) {
    isOpen.value = !isOpen.value
  }
}

// Provisionals: Conectar esto al store de usuario/chat en el futuro
const chatHistory = ref([
  { role: 'ai', text: '¡Hola! Soy tu asistente de RutaIA. ¿Quieres ajustar algo de tu itinerario?' }
])

const send = async () => {
  if (!input.value.trim()) return
  
  const text = input.value
  chatHistory.value.push({ role: 'user', text })
  input.value = ''
  loading.value = true
  saveHistory()
  
  // Mock AI response
  setTimeout(() => {
    chatHistory.value.push({ role: 'ai', text: 'Estoy analizando tu solicitud. Pronto podré modificar el itinerario directamente.' })
    loading.value = false
    saveHistory()
  }, 1500)
}

// Permitir que el padre añada mensajes (ej: de sugerencias AI)
const addAIMessage = (text, suggestions = null) => {
  chatHistory.value.push({
    role: 'ai',
    text,
    suggestions
  })
  if (suggestions) isOpen.value = true
  saveHistory()
}

// Persistencia
const loadHistory = () => {
  if (!props.planId) return
  const saved = localStorage.getItem(`chat_history_${props.planId}`)
  if (saved) {
    chatHistory.value = JSON.parse(saved)
  }
}

const saveHistory = () => {
  if (!props.planId) return
  localStorage.setItem(`chat_history_${props.planId}`, JSON.stringify(chatHistory.value))
}

import { onMounted, watch } from 'vue'
onMounted(() => {
  loadHistory()
})

watch(() => props.planId, () => {
  loadHistory()
})

const removeSuggestion = (sugId) => {
  chatHistory.value = chatHistory.value.map(msg => {
    if (msg.suggestions) {
      return {
        ...msg,
        suggestions: msg.suggestions.filter(s => s.id !== sugId)
      }
    }
    return msg
  })
  saveHistory()
}

defineExpose({ addAIMessage, removeSuggestion, isOpen })
</script>

<style scoped>
.chat-window-enter-active, .chat-window-leave-active {
  transition: all 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275);
}
.chat-window-enter-from, .chat-window-leave-to {
  opacity: 0;
  transform: translateY(20px) scale(0.9);
}

.custom-scrollbar::-webkit-scrollbar {
  width: 4px;
}
.custom-scrollbar::-webkit-scrollbar-thumb {
  background: #cbd5e1;
  border-radius: 10px;
}
</style>
