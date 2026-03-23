<!-- src/features/hospedajes/views/HospedajesAdmin.vue -->
<template>
  <div class="p-4">
    <!-- Encabezado -->
    <div class="p-d-flex p-jc-between p-ai-center mb-4">
      <h2>Administrar hospedajes</h2>
      <Button label="Nuevo" icon="pi pi-plus" @click="onCreate" />
    </div>

    <!-- Tabla -->
    <DataTable
      :value="items"
      :lazy="true"
      :paginator="true"
      :rows="pageSize"
      :totalRecords="total"
      :loading="loading"
      dataKey="id"
      @page="onPage"
      @sort="onSort"
      @filter="onFilter"
    >
      <Column field="nombre"     header="Nombre"     sortable filter />
      <Column field="direccion"  header="Dirección"  sortable />
      <Column field="categoria"  header="Categoría"  sortable filter />
      <Column field="precio"     header="Precio"     sortable />

      <!-- Acciones -->
      <Column header="Acciones" style="width: 140px">
        <template #body="{ data }">
          <Button
            icon="pi pi-pencil"
            class="p-button-text p-button-sm"
            @click="onEdit(data)"
          />
          <Button
            icon="pi pi-trash"
            class="p-button-text p-button-sm p-button-danger"
            @click="onDelete(data)"
          />
        </template>
      </Column>
    </DataTable>

    <!-- Diálogo de edición / creación -->
    <Dialog
      v-model:visible="dialogVisible"
      :header="isEditing ? 'Editar hospedaje' : 'Nuevo hospedaje'"
      :modal="true"
      :closable="false"
      :style="{ width: '400px' }"
    >
      <form @submit.prevent="save">
        <div class="p-field">
          <label for="nombre">Nombre</label>
          <InputText id="nombre" v-model="form.nombre" required />
        </div>
        <div class="p-field">
          <label for="direccion">Dirección</label>
          <InputText id="direccion" v-model="form.direccion" />
        </div>
        <div class="p-field">
          <label for="categoria">Categoría</label>
          <InputText id="categoria" v-model="form.categoria" />
        </div>
        <div class="p-field">
          <label for="precio">Precio</label>
          <InputText id="precio" v-model.number="form.precio" type="number" />
        </div>
        <div class="p-d-flex p-jc-end p-mt-3" style="gap: 0.5rem">
          <Button type="button" label="Cancelar" class="p-button-text" @click="dialogVisible=false" />
          <Button type="submit"   label="Guardar"  :loading="saving" />
        </div>
      </form>
    </Dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useToast } from 'primevue/usetoast'

import DataTable from 'primevue/datatable'
import Column    from 'primevue/column'
import Button    from 'primevue/button'
import Dialog    from 'primevue/dialog'
import InputText from 'primevue/inputtext'

import * as api from '../api'   // Asegúrate de tener listHospedajes, create, update, delete

/* ---------- estado ---------- */
const toast      = useToast()
const items      = ref([])
const total      = ref(0)
const loading    = ref(false)
const page       = ref(0)
const pageSize   = ref(10)
const sortField  = ref(null)
const sortOrder  = ref(null)
const filters    = ref({})

/* diálogo */
const dialogVisible = ref(false)
const isEditing     = ref(false)
const saving        = ref(false)
const currentId     = ref(null)
const form = ref({
  nombre: '',
  direccion: '',
  categoria: '',
  precio: null
})

/* ---------- CRUD ---------- */
async function loadData () {
  loading.value = true
  const params = {
    page: page.value + 1,
    page_size: pageSize.value,
    sort_field: sortField.value,
    sort_order: sortOrder.value,
    ...filters.value
  }
  const { data, headers } = await api.listHospedajes(params)
  items.value = data
  total.value = Number(headers['x-total-count'] ?? data.length)
  loading.value = false
}

function onPage (e) {
  page.value = e.page
  pageSize.value = e.rows
  loadData()
}
function onSort (e) {
  sortField.value = e.sortField
  sortOrder.value = e.sortOrder === 1 ? 'asc' : 'desc'
  loadData()
}
function onFilter (e) {
  filters.value = Object.fromEntries(
    Object.entries(e.filters || {}).map(([k, v]) => [k, v.value])
  )
  loadData()
}

function onCreate () {
  resetForm()
  isEditing.value = false
  dialogVisible.value = true
}
function onEdit (row) {
  form.value = { ...row }
  currentId.value = row.id
  isEditing.value = true
  dialogVisible.value = true
}
async function onDelete (row) {
  if (confirm(`¿Eliminar “${row.nombre}”?`)) {
    await api.deleteHospedaje(row.id)
    toast.add({ severity: 'warn', summary: 'Eliminado', detail: 'Hospedaje borrado' })
    loadData()
  }
}

async function save () {
  saving.value = true
  try {
    if (isEditing.value) {
      await api.updateHospedaje(currentId.value, form.value)
      toast.add({ severity: 'success', summary: 'Actualizado', detail: 'Hospedaje guardado' })
    } else {
      await api.createHospedaje(form.value)
      toast.add({ severity: 'success', summary: 'Creado', detail: 'Hospedaje creado' })
    }
    dialogVisible.value = false
    loadData()
  } finally {
    saving.value = false
  }
}
function resetForm () {
  form.value = { nombre: '', direccion: '', categoria: '', precio: null }
}

onMounted(loadData)
</script>

<style scoped>
/* Ajustes rápidos de la tabla */
:deep(.p-datatable .p-column-title) {
  font-weight: 600;
}
</style>
