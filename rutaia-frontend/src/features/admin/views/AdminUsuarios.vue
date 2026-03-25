<template>
  <div class="p-6">
    <div class="flex items-center gap-3 mb-6">
      <i class="pi pi-users text-3xl text-blue-600"></i>
      <h1 class="text-3xl font-black tracking-tight">Gestión de Usuarios</h1>
    </div>

    <Card class="shadow-sm border-0">
      <template #content>
        <DataTable :value="usuarios" :loading="loading" responsiveLayout="scroll" class="p-datatable-sm">
          <Column field="nombre" header="Nombre" sortable></Column>
          <Column field="correo" header="Correo" sortable></Column>
          <Column field="role" header="Rol">
            <template #body="slotProps">
              <Dropdown 
                v-model="slotProps.data.role" 
                :options="roles" 
                @change="updateRole(slotProps.data)" 
                class="w-full"
                :disabled="slotProps.data.correo === 'admin@rutaia.cl'"
              />
            </template>
          </Column>
          <Column field="creado_en" header="Registrado" sortable>
            <template #body="slotProps">
              {{ formatDate(slotProps.data.creado_en) }}
            </template>
          </Column>
        </DataTable>
      </template>
    </Card>
    <Toast />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'
import Dropdown from 'primevue/dropdown'
import Card from 'primevue/card'
import Toast from 'primevue/toast'
import { useToast } from 'primevue/usetoast'

const usuarios = ref([])
const loading = ref(false)
const toast = useToast()
const roles = ['admin', 'gestor', 'user']

const apiBase = import.meta.env.VITE_API_URL === '/api' ? '/api' : (import.meta.env.VITE_API_URL || '')

async function fetchUsuarios() {
  loading.value = true
  try {
    const { data } = await axios.get(`${apiBase}/usuarios`)
    usuarios.value = data
  } catch (err) {
    toast.add({ severity: 'error', summary: 'Error', detail: 'No se pudieron cargar los usuarios' })
  } finally {
    loading.value = false
  }
}

async function updateRole(user) {
  try {
    await axios.patch(`${apiBase}/usuarios/${user.id}/role`, { role: user.role })
    toast.add({ severity: 'success', summary: 'Actualizado', detail: `Rol de ${user.nombre} cambiado a ${user.role}` })
  } catch (err) {
    toast.add({ severity: 'error', summary: 'Error', detail: 'No se pudo actualizar el rol' })
    fetchUsuarios() // Revertir cambios locales
  }
}

function formatDate(dateStr) {
  if (!dateStr) return '-'
  return new Date(dateStr).toLocaleDateString()
}

onMounted(fetchUsuarios)
</script>

<style scoped>
:deep(.p-dropdown) {
  border: 1px solid #e5e7eb;
}
:deep(.p-datatable-thead > tr > th) {
  background-color: #f9fafb;
  color: #374151;
  font-weight: 700;
}
</style>
