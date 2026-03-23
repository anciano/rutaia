<!-- src/components/AdminLugares.vue -->
<template>
  <div class="p-4">
    <div class="p-d-flex p-jc-between p-ai-center mb-4">
      <h2>Gestión de Lugares</h2>
      <Button label="Nuevo Lugar" icon="pi pi-plus" @click="onCreate" />
    </div>

    <DataTable
      :value="lugares"
      :paginator="true"
      :rows="pageSize"
      :totalRecords="total"
      :lazy="true"
      @page="onPage"
      @sort="onSort"
      @filter="onFilter"
      :loading="loading"
      dataKey="id"
    >
      <Column field="nombre" header="Nombre" sortable filter filterPlaceholder="Buscar…" />
      <Column field="categoria" header="Categoría" sortable filter filterPlaceholder="Filtrar…" />
      <Column field="precio_aprox" header="Precio" sortable />
      <Column header="Acciones" :body="actionTemplate" style="width:150px" />
    </DataTable>

    <Dialog header="Lugar" v-model:visible="dialogVisible" :modal="true" :closable="false">
      <div class="p-fluid">
        <div class="p-field">
          <label for="nombre">Nombre</label>
          <InputText id="nombre" v-model="form.nombre" />
        </div>
        <div class="p-field">
          <label for="categoria">Categoría</label>
          <InputText id="categoria" v-model="form.categoria" />
        </div>
        <div class="p-field">
          <label for="precio">Precio aprox</label>
          <InputText id="precio" v-model.number="form.precio_aprox" />
        </div>
      </div>
      <template #footer>
        <Button label="Cancelar" icon="pi pi-times" @click="dialogVisible=false" class="p-button-text" />
        <Button label="Guardar" icon="pi pi-check" @click="save" />
      </template>
    </Dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'
import { useToast } from 'primevue/usetoast'

const toast = useToast()

// datos de la tabla
const lugares = ref([])
const total   = ref(0)
const loading = ref(false)

const page    = ref(0)
const pageSize = ref(10)
const sortField = ref(null)
const sortOrder = ref(null)
const filters   = ref({})

// diálogo y formulario
const dialogVisible = ref(false)
const form = ref({ id: null, nombre: '', categoria: '', precio_aprox: null })

function loadData() {
  loading.value = true
  const params = {
    page: page.value + 1,
    page_size: pageSize.value,
    sort_field: sortField.value,
    sort_order: sortOrder.value,
    ...filters.value
  }
  axios.get('/admin/lugares', { params })
    .then(({ data, headers }) => {
      lugares.value = data
      total.value   = parseInt(headers['x-total-count'] || data.length)
    })
    .finally(() => loading.value = false)
}

function onPage(event) {
  page.value = event.page
  pageSize.value = event.rows
  loadData()
}

function onSort(event) {
  sortField.value = event.sortField
  sortOrder.value = event.sortOrder === 1 ? 'asc' : 'desc'
  loadData()
}

function onFilter(event) {
  filters.value = {}
  for (const f in event.filters) {
    const m = event.filters[f]
    if (m && m.value != null) filters.value[f] = m.value
  }
  loadData()
}

function onCreate() {
  form.value = { id: null, nombre: '', categoria: '', precio_aprox: null }
  dialogVisible.value = true
}

function onEdit(row) {
  form.value = { ...row }
  dialogVisible.value = true
}

function save() {
  const api = form.value.id
    ? axios.put(`/admin/lugares/${form.value.id}`, form.value)
    : axios.post('/admin/lugares', form.value)

  api.then(() => {
    toast.add({ severity:'success', summary:'Éxito', detail:'Guardado correctamente' })
    dialogVisible.value = false
    loadData()
  })
  .catch(() => {
    toast.add({ severity:'error', summary:'Error', detail:'No se pudo guardar' })
  })
}

function onDelete(row) {
  if (confirm(`Eliminar lugar “${row.nombre}”?`)) {
    axios.delete(`/admin/lugares/${row.id}`)
      .then(() => {
        toast.add({ severity:'warn', summary:'Eliminado', detail:'Registro borrado' })
        loadData()
      })
  }
}

// Template para las acciones
function actionTemplate({ data }) {
  return (
    <>
      <Button icon="pi pi-pencil" class="p-button-text p-button-sm" onClick={() => onEdit(data)} />
      <Button icon="pi pi-trash" class="p-button-text p-button-sm p-button-danger" onClick={() => onDelete(data)} />
    </>
  )
}

onMounted(loadData)
</script>

<style scoped>
/* ajustes menores si quieres */
</style>