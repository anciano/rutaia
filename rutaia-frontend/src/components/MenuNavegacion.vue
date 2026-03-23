<template>
  <nav class="bg-white shadow-sm border-b border-gray-100 flex justify-between items-center px-6 py-4 sticky top-0 z-50">
    <div class="flex items-center gap-2">
      <i class="pi pi-compass text-blue-600 text-2xl"></i>
      <h1 class="font-black text-2xl tracking-tighter text-gray-800">RutaIA</h1>
    </div>
    <div class="flex items-center space-x-6">
      <button @click="toggleTheme" class="text-gray-400 hover:text-gray-800 transition-colors" title="Cambiar tema">
        <i :class="isDark ? 'pi pi-moon' : 'pi pi-sun'"></i>
      </button>
      <div class="w-px h-6 bg-gray-200"></div>
      <router-link to="/chat" class="text-sm font-bold text-gray-500 hover:text-blue-600 transition-colors">Chat</router-link>
      <router-link to="/historial" class="text-sm font-bold text-gray-500 hover:text-blue-600 transition-colors">Planificaciones</router-link>
      <div class="w-px h-6 bg-gray-200"></div>
      <router-link to="/admin/catalog" class="text-sm font-bold text-gray-500 hover:text-blue-600 transition-colors">Catálogo</router-link>
      <router-link to="/admin/explorer" class="text-sm font-bold text-gray-500 hover:text-blue-600 transition-colors">Explorador</router-link>
      <router-link to="/admin/taxonomy" class="text-sm font-bold text-gray-500 hover:text-blue-600 transition-colors">Taxonomía</router-link>
      <router-link to="/admin/localities" class="text-sm font-bold text-gray-500 hover:text-blue-600 transition-colors">Localidades</router-link>
      <router-link to="/admin/agenda" class="text-sm font-bold text-gray-500 hover:text-blue-600 transition-colors">Agenda Local</router-link>
      <router-link to="/login" class="text-sm font-bold text-gray-400 hover:text-gray-800 transition-colors" @click="logout" title="Cerrar sesión">
        <i class="pi pi-sign-out"></i>
      </router-link>
    </div>
  </nav>
</template>

<script setup>
import { ref, onMounted } from 'vue'

const isDark = ref(false)

function toggleTheme() {
  const element = document.documentElement
  element.classList.toggle('dark')
  isDark.value = element.classList.contains('dark')
  localStorage.setItem('theme', isDark.value ? 'dark' : 'light')
}

onMounted(() => {
  if (localStorage.theme === 'dark' || (!('theme' in localStorage) && window.matchMedia('(prefers-color-scheme: dark)').matches)) {
    document.documentElement.classList.add('dark')
    isDark.value = true
  } else {
    document.documentElement.classList.remove('dark')
    isDark.value = false
  }
})

function logout() {
  localStorage.removeItem('usuario')
  localStorage.removeItem('planCompletado')
}
</script>