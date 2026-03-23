<!-- src/features/actividades/views/ActividadesAdmin.vue -->
<template>
  <div class="p-4">
    <!-- Encabezado -->
    <div class="p-d-flex p-jc-between p-ai-center mb-4">
      <h2>Administrar actividades</h2>
      <Button label="Nueva" icon="pi pi-plus" @click="onCreate" />
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
      <Column field="nombre"           header="Nombre"      sortable filter />
      <Column field="categoria"        header="Categoría"   sortable filter />
      <Column field="duracion_horas"   header="Duración (h)" sortable />
      <Column field="nivel_intensidad" header="Intensidad"   sortable />

      <!-- Columna de acciones -->
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
      :header="isEditing ? 'Editar actividad' : 'Nueva actividad'"
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
          <label for="categoria">Categoría</label>
          <InputText id="categoria" v-model="form.categoria" />
        </div>

        <div class="p-field">
          <label for="duracion">Duración (horas)</label>
          <InputText id="duracion" v-model.number="form.duracion_horas" type="number" />
        </div>

        <div class="p-field">
          <label for="intensidad">Intensidad</label>
          <InputText id="intensidad" v-model="form.nivel_intensidad" placeholder="Baja / Media / Alta" />
        </div>

        <div class="p-d-flex p-jc-end p-mt-3" style="gap: 0.5rem">
          <Button type="button" label="Cancelar" class="p-button-text" @click="dialogVisible = false" />
          <Button type="submit" label="Guardar" :loading="saving" />
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

import * as api from '../api'   // Debe exponer listActividades, create, update, delete

/* ---------- estado ---------- */
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
  categoria: '',
  duracion_horas: null,
  nivel_intensidad: ''
})

const toast = useToast()

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
  const { data, headers } = await api.listActividades(params)
  items.value = data
  total.value = Number(headers['x-total-count'] ?? data.length)
  loading.value = false
}

function onPage ({ page: p, rows }) {
  page.value = p
  pageSize.value = rows
  loadData()
}
function onSort ({ sortField: sf, sortOrder: so }) {
  sortField.value = sf
  sortOrder.value = so === 1 ? 'asc' : 'desc'
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
    await api.deleteActividad(row.id)
    toast.add({ severity: 'warn', summary: 'Eliminada', detail: 'Actividad borrada' })
    loadData()
  }
}

async function save () {
  saving.value = true
  try {
    if (isEditing.value) {
      await api.updateActividad(currentId.value, form.value)
      toast.add({ severity: 'success', summary: 'Actualizada', detail: 'Actividad guardada' })
    } else {
      await api.createActividad(form.value)
      toast.add({ severity: 'success', summary: 'Creada', detail: 'Actividad creada' })
    }
    dialogVisible.value = false
    loadData()
  } finally {
    saving.value = false
  }
}
function resetForm () {
  form.value = { nombre: '', categoria: '', duracion_horas: null, nivel_intensidad: '' }
}

onMounted(loadData)
</script>

<style scoped>
:deep(.p-datatable .p-column-title) {
  font-weight: 600;
}
</style>
