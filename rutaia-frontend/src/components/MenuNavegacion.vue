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

      <!-- Chat: Admin -->
      <router-link v-if="role === 'admin'" to="/chat" class="text-sm font-bold text-gray-500 hover:text-blue-600 transition-colors">Chat</router-link>

      <!-- Planificaciones: Todos -->
      <router-link to="/historial" class="text-sm font-bold text-gray-500 hover:text-blue-600 transition-colors">Planificaciones</router-link>

      <div class="w-px h-6 bg-gray-200"></div>

      <!-- Catálogo: Admin, Gestor -->
      <router-link v-if="role === 'admin' || role === 'gestor'" to="/admin/catalog" class="text-sm font-bold text-gray-500 hover:text-blue-600 transition-colors">Catálogo</router-link>

      <!-- Explorador: Todos -->
      <router-link to="/admin/explorer" class="text-sm font-bold text-gray-500 hover:text-blue-600 transition-colors">Explorador</router-link>

      <!-- Usuarios: Admin -->
      <router-link v-if="role === 'admin'" to="/admin/usuarios" class="text-sm font-bold text-gray-500 hover:text-blue-600 transition-colors">Usuarios</router-link>

      <!-- Taxonomía: Admin -->
      <router-link v-if="role === 'admin'" to="/admin/taxonomy" class="text-sm font-bold text-gray-500 hover:text-blue-600 transition-colors">Taxonomía</router-link>

      <!-- Localidades: Admin -->
      <router-link v-if="role === 'admin'" to="/admin/localities" class="text-sm font-bold text-gray-500 hover:text-blue-600 transition-colors">Localidades</router-link>

      <!-- Agenda Local: Admin, Gestor -->
      <router-link v-if="role === 'admin' || role === 'gestor'" to="/admin/agenda" class="text-sm font-bold text-gray-500 hover:text-blue-600 transition-colors">Agenda Local</router-link>

      <router-link to="/login" class="text-sm font-bold text-gray-400 hover:text-gray-800 transition-colors" @click="logout" title="Cerrar sesión">
        <i class="pi pi-sign-out"></i>
      </router-link>
    </div>
  </nav>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'

const isDark = ref(false)
const usuario = ref({})

const role = computed(() => {
  return usuario.value?.role || 'user'
})

function loadUser() {
  try {
    const data = localStorage.getItem('usuario')
    if (data && data !== 'undefined') {
      usuario.value = JSON.parse(data)
    }
  } catch (e) {
    console.error('Error loading user', e)
    usuario.value = {}
  }
}

function toggleTheme() {
  const element = document.documentElement
  element.classList.toggle('dark')
  isDark.value = element.classList.contains('dark')
  localStorage.setItem('theme', isDark.value ? 'dark' : 'light')
}

onMounted(() => {
  loadUser()
  if (localStorage.theme === 'dark') {
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