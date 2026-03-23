<template>
  <div>
    <h2 class="text-xl font-bold mb-4">Chat con el Asesor</h2>
    <textarea v-model="mensaje" class="w-full border p-2 rounded" placeholder="Escribe tu pregunta..."></textarea>
    <button @click="enviar" class="mt-2 bg-green-500 text-white px-4 py-2 rounded">Enviar</button>
    <p v-if="respuesta" class="mt-4 bg-white p-2 rounded border">{{ respuesta }}</p>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import axios from 'axios'

const mensaje = ref('')
const respuesta = ref('')

const enviar = async () => {
  const res = await axios.post('http://localhost:8000/chat', { content: mensaje.value })
  respuesta.value = res.data.response
}
</script>