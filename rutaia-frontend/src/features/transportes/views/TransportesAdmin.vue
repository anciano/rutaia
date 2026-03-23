<!-- src/features/transportes/views/TransportesAdmin.vue -->
<template>
  <div class="p-4">
    <!-- Encabezado -->
    <div class="p-d-flex p-jc-between p-ai-center mb-4">
      <h2>Administrar transportes</h2>
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
      <Column field="tipo"                 header="Tipo"            sortable filter />
      <Column field="ubicacion_origen"     header="Origen"          sortable />
      <Column field="ubicacion_destino"    header="Destino"         sortable />
      <Column field="tiempo_estimado_horas" header="Tiempo (h)"     sortable body-class="text-right" />
      <Column field="costo"                header="Costo"           sortable body-class="text-right" />

      <!-- Acciones -->
      <Column header="Acciones" style="width:140px">
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

    <!-- Diálogo de nuevo / edición -->
    <Dialog
      v-model:visible="dialogVisible"
      :header="isEditing ? 'Editar transporte' : 'Nuevo transporte'"
      :modal="true"
      :closable="false"
      :style="{ width: '450px' }"
    >
      <form @submit.prevent="save">
        <div class="p-field">
          <label for="tipo">Tipo</label>
          <InputText id="tipo" v-model="form.tipo" required />
        </div>

        <div class="p-field">
          <label for="origen">Ubicación origen</label>
          <InputText id="origen" v-model="form.ubicacion_origen" />
        </div>

        <div class="p-field">
          <label for="destino">Ubicación destino</label>
          <InputText id="destino" v-model="form.ubicacion_destino" />
        </div>

        <div class="p-field">
          <label for="tiempo">Tiempo estimado (h)</label>
          <InputText id="tiempo" v-model.number="form.tiempo_estimado_horas" type="number" />
        </div>

        <div class="p-field">
          <label for="costo">Costo</label>
          <InputText id="costo" v-model.number="form.costo" type="number" />
        </div>

        <div class="p-d-flex p-jc-end p-mt-3" style="gap:.5rem">
          <Button label="Cancelar" type="button" class="p-button-text" @click="dialogVisible=false" />
          <Button label="Guardar"  type="submit" :loading="saving" />
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

import * as api from '../api' // listTransportes, createTransporte, updateTransporte, deleteTransporte

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
  tipo: '',
  ubicacion_origen: '',
  ubicacion_destino: '',
  tiempo_estimado_horas: null,
  costo: null
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
  const { data, headers } = await api.listTransportes(params)
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
  if (confirm(`¿Eliminar transporte de tipo “${row.tipo}”?`)) {
    await api.deleteTransporte(row.id)
    toast.add({ severity:'warn', summary:'Eliminado', detail:'Transporte borrado' })
    loadData()
  }
}

async function save () {
  saving.value = true
  try {
    if (isEditing.value) {
      await api.updateTransporte(currentId.value, form.value)
      toast.add({ severity:'success', summary:'Actualizado', detail:'Transporte guardado' })
    } else {
      await api.createTransporte(form.value)
      toast.add({ severity:'success', summary:'Creado', detail:'Transporte creado' })
    }
    dialogVisible.value = false
    loadData()
  } finally {
    saving.value = false
  }
}
function resetForm () {
  form.value = {
    tipo: '',
    ubicacion_origen: '',
    ubicacion_destino: '',
    tiempo_estimado_horas: null,
    costo: null
  }
}

onMounted(loadData)
</script>

<style scoped>
:deep(.p-datatable .p-column-title) {
  font-weight: 600;
}
.text-right { text-align: right; }
</style>
