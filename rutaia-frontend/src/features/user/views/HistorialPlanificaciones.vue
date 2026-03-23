<template>
  <div class="max-w-3xl mx-auto p-6 space-y-6">
    <div class="flex justify-between items-center">
      <h1 class="text-2xl font-bold text-blue-700">Tus Planificaciones</h1>
      <router-link
        to="/plan/1"
        class="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg font-bold shadow transition-colors flex items-center"
      >
        <i class="pi pi-plus mr-2"></i>
        Nueva
      </router-link>
    </div>

    <!-- Estado de carga -->
    <div v-if="loading" class="text-center text-gray-500 py-12">
      <i class="pi pi-spin pi-spinner text-2xl mb-2"></i>
      <p>Cargando planificaciones…</p>
    </div>

    <!-- Sin planificaciones -->
    <div v-else-if="plans.length === 0" class="text-center text-gray-600 py-12 bg-white rounded-xl border border-gray-100 shadow-sm">
      <div class="w-20 h-20 bg-blue-50 rounded-full flex items-center justify-center mx-auto mb-4">
        <i class="pi pi-compass text-3xl text-blue-500"></i>
      </div>
      <p class="mb-6 text-lg">No tienes planificaciones aún.</p>
      <router-link
        to="/plan/1"
        class="inline-block bg-blue-600 text-white px-6 py-3 rounded-xl font-bold hover:bg-blue-700 shadow-lg transition-transform hover:scale-105"
      >
        ¡Crea tu primera ruta!
      </router-link>
    </div>

    <!-- Lista de planificaciones -->
    <ul v-else class="space-y-4">
      <li
        v-for="plan in plans"
        :key="plan.id"
        class="border rounded-lg hover:shadow p-4 transition"
      >
        <router-link
          :to="`/plan/${plan.id}`"
          class="block"
        >
          <div class="flex justify-between items-center bg-transparent group/row">
            <div class="flex-1 min-w-0 pr-4">
              <h2 class="text-lg font-semibold text-gray-800">
                {{ plan.origen }} — {{ plan.fecha_inicio }}  
                <span class="text-sm text-gray-500">→ {{ plan.fecha_fin }}</span>
              </h2>
              <p class="text-sm text-gray-600">
                {{ plan.dias }} día{{ plan.dias > 1 ? 's' : '' }},
                Presupuesto: ${{ plan.presupuesto.toLocaleString() }}
              </p>
            </div>
            <!-- Delete Button -->
            <button
              @click.prevent="confirmDelete(plan)"
              class="ml-4 p-2 text-red-500 hover:text-red-700 bg-red-50 hover:bg-red-100 rounded-lg transition-colors shrink-0"
              title="Eliminar planificación"
            >
              <i class="pi pi-trash"></i>
            </button>
          </div>
        </router-link>
      </li>
    </ul>

    <!-- Dialogo de confirmacion global de primevue (si no lo hay arriba lo inyecto por si acaso o uso alert) -->
    <!-- Como ya existe en el App.vue o usamos el de primevue... aseguramos usando ConfirmDialog si se necesita, pero mejor el useConfirm normal. -->
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import { useUserStore } from '../store'
import { storeToRefs } from 'pinia'
import { useConfirm } from 'primevue/useconfirm'
import { useToast } from 'primevue/usetoast'

const userStore = useUserStore()
const { plans, loading } = storeToRefs(userStore)
const confirm = useConfirm()
const toast = useToast()

const confirmDelete = (plan) => {
  confirm.require({
    message: `¿Estás seguro de que deseas eliminar la planificación a "${plan.origen}"?`,
    header: 'Confirmar Eliminación',
    icon: 'pi pi-exclamation-triangle',
    acceptClass: 'p-button-danger',
    accept: async () => {
      try {
        await userStore.deletePlan(plan.id)
        toast.add({ severity: 'success', summary: 'Eliminado', detail: 'Planificación eliminada exitosamente', life: 3000 })
      } catch (e) {
        toast.add({ severity: 'error', summary: 'Error', detail: 'No se pudo eliminar la planificación', life: 3000 })
      }
    }
  })
}

onMounted(async () => {
  await userStore.loadPlans()
})
</script>

<style scoped>
/* Opcional: ajustar el hover */
li:hover {
  background-color: #f9fafe;
}
</style>
