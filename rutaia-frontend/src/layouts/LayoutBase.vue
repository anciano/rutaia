<template>
  <div class="min-h-screen bg-gray-100">
    <MenuNavegacion />
    <main class="p-4">
      <router-view />
    </main>
  </div>
</template>

<script setup>
import MenuNavegacion from '../components/MenuNavegacion.vue'
</script>