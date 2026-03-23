<template>
  <div class="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 p-8">
    <div class="max-w-7xl mx-auto">
      <!-- Header -->
      <div class="bg-white rounded-2xl shadow-xl p-6 mb-6">
        <div class="flex items-center justify-between">
          <div>
            <h1 class="text-3xl font-black text-blue-900">Gestión de Lugares</h1>
            <p class="text-gray-500 mt-1">Administra el catálogo de puntos de interés</p>
          </div>
          <button 
            @click="openCreateDialog"
            class="bg-blue-600 hover:bg-blue-700 text-white px-6 py-3 rounded-xl font-bold shadow-lg transition-all flex items-center space-x-2"
          >
            <i class="pi pi-plus"></i>
            <span>Nuevo Lugar</span>
          </button>
        </div>

        <!-- Filters -->
        <div class="grid grid-cols-1 md:grid-cols-3 gap-4 mt-6">
          <div>
            <label class="block text-sm font-bold text-gray-700 mb-2">Ciudad</label>
            <Dropdown 
              v-model="filters.ciudad_id" 
              :options="ciudades" 
              optionLabel="nombre" 
              optionValue="id"
              placeholder="Todas las ciudades"
              class="w-full"
              showClear
            />
          </div>
          <div>
            <label class="block text-sm font-bold text-gray-700 mb-2">Categoría</label>
            <Dropdown 
              v-model="filters.categoria_id" 
              :options="categorias" 
              optionLabel="nombre"
              optionValue="id"
              placeholder="Todas las categorías"
              class="w-full"
              showClear
            />
          </div>
          <div class="flex items-end">
            <button 
              @click="fetchLugares"
              class="bg-indigo-600 hover:bg-indigo-700 text-white px-6 py-3 rounded-xl font-bold w-full transition-all"
            >
              <i class="pi pi-filter mr-2"></i>
              Aplicar Filtros
            </button>
          </div>
        </div>
      </div>

      <!-- DataTable -->
      <div class="bg-white rounded-2xl shadow-xl overflow-hidden">
        <DataTable 
          :value="lugares" 
          :loading="loading"
          paginator 
          :rows="10"
          :rowsPerPageOptions="[10, 25, 50]"
          class="p-datatable-sm"
          stripedRows
          responsiveLayout="scroll"
        >
          <Column field="id" header="ID" :sortable="true" style="width: 80px"></Column>
          <Column field="nombre" header="Nombre" :sortable="true" style="min-width: 200px"></Column>
          <Column field="categoria_id" header="Categoría" :sortable="true" style="width: 150px">
            <template #body="slotProps">
              <span class="px-3 py-1 rounded-full text-xs font-bold bg-blue-100 text-blue-800">
                {{ categorias.find(c => c.id === slotProps.data.categoria_id)?.nombre || slotProps.data.categoria }}
              </span>
            </template>
          </Column>
          <Column field="precio_aprox" header="Precio" :sortable="true" style="width: 120px">
            <template #body="slotProps">
              ${{ slotProps.data.precio_aprox?.toLocaleString() || 0 }}
            </template>
          </Column>
          <Column field="calificacion" header="Rating" :sortable="true" style="width: 100px">
            <template #body="slotProps">
              <div class="flex items-center space-x-1">
                <i class="pi pi-star-fill text-yellow-400"></i>
                <span class="font-bold">{{ slotProps.data.calificacion || 'N/A' }}</span>
              </div>
            </template>
          </Column>
          <Column field="estimated_duration_minutes" header="Duración (min)" :sortable="true" style="width: 140px"></Column>
          <Column header="Acciones" style="width: 150px">
            <template #body="slotProps">
              <div class="flex space-x-2">
                <button 
                  @click="openEditDialog(slotProps.data)"
                  class="text-blue-600 hover:text-blue-800 font-bold"
                  title="Editar"
                >
                  <i class="pi pi-pencil"></i>
                </button>
                <button 
                  @click="confirmDelete(slotProps.data)"
                  class="text-red-600 hover:text-red-800 font-bold"
                  title="Eliminar"
                >
                  <i class="pi pi-trash"></i>
                </button>
              </div>
            </template>
          </Column>
        </DataTable>
      </div>
    </div>

    <!-- Edit/Create Dialog -->
    <Dialog 
      v-model:visible="dialogVisible" 
      :header="editMode ? 'Editar Lugar' : 'Nuevo Lugar'"
      :modal="true"
      :style="{ width: '600px' }"
      class="p-fluid"
    >
      <div class="space-y-4">
        <div>
          <label class="block text-sm font-bold text-gray-700 mb-2">Nombre *</label>
          <InputText v-model="formData.nombre" class="w-full" />
        </div>
        <div class="grid grid-cols-2 gap-4">
          <div>
            <label class="block text-sm font-bold text-gray-700 mb-2">Ciudad</label>
            <Dropdown v-model="formData.ciudad_id" :options="ciudades" optionLabel="nombre" optionValue="id" class="w-full" />
          </div>
          <div>
            <label class="block text-sm font-bold text-gray-700 mb-2">Categoría</label>
            <Dropdown v-model="formData.categoria_id" :options="categorias" optionLabel="nombre" optionValue="id" class="w-full" />
          </div>
        </div>
        <div>
          <label class="block text-sm font-bold text-gray-700 mb-2">Descripción</label>
          <Textarea v-model="formData.descripcion_breve" rows="3" class="w-full" />
        </div>
        <div class="grid grid-cols-2 gap-4">
          <div>
            <label class="block text-sm font-bold text-gray-700 mb-2">Precio Aprox.</label>
            <InputNumber v-model="formData.precio_aprox" mode="currency" currency="CLP" locale="es-CL" class="w-full" />
          </div>
          <div>
            <label class="block text-sm font-bold text-gray-700 mb-2">Duración (min)</label>
            <InputNumber v-model="formData.estimated_duration_minutes" class="w-full" />
          </div>
        </div>
        <div class="grid grid-cols-2 gap-4">
          <div>
            <label class="block text-sm font-bold text-gray-700 mb-2">Latitud</label>
            <InputNumber v-model="formData.latitud" mode="decimal" :minFractionDigits="6" class="w-full" />
          </div>
          <div>
            <label class="block text-sm font-bold text-gray-700 mb-2">Longitud</label>
            <InputNumber v-model="formData.longitud" mode="decimal" :minFractionDigits="6" class="w-full" />
          </div>
        </div>
        <div>
          <label class="block text-sm font-bold text-gray-700 mb-2">Rango Etario</label>
          <InputText v-model="formData.rango_etario" placeholder="Ej: Adultos, Niños, Todas las edades" class="w-full" />
        </div>
        <div>
          <label class="block text-sm font-bold text-gray-700 mb-2">Accesibilidad</label>
          <Textarea v-model="formData.accesibilidad" rows="2" class="w-full" />
        </div>
      </div>

      <template #footer>
        <button 
          @click="dialogVisible = false"
          class="px-4 py-2 text-gray-700 hover:bg-gray-100 rounded-lg font-bold transition-all"
        >
          Cancelar
        </button>
        <button 
          @click="saveLugar"
          class="px-6 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-bold transition-all ml-2"
        >
          {{ editMode ? 'Actualizar' : 'Crear' }}
        </button>
      </template>
    </Dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from '@/services/axios'
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'
import Dropdown from 'primevue/dropdown'
import Dialog from 'primevue/dialog'
import InputText from 'primevue/inputtext'
import InputNumber from 'primevue/inputnumber'
import Textarea from 'primevue/textarea'
import { useConfirm } from 'primevue/useconfirm'
import { useToast } from 'primevue/usetoast'

const confirm = useConfirm()
const toast = useToast()

const lugares = ref([])
const loading = ref(false)
const dialogVisible = ref(false)
const editMode = ref(false)
const formData = ref({})
const ciudades = ref([])
const categorias = ref([])
const filters = ref({ ciudad_id: null, categoria_id: null })

onMounted(async () => {
  await fetchCiudades()
  await fetchCategorias()
  await fetchLugares()
})

async function fetchCiudades() {
  try {
    const { data } = await axios.get('/ciudades')
    ciudades.value = data
  } catch (err) {
    console.error('Error fetching cities:', err)
  }
}

async function fetchCategorias() {
  try {
    const { data } = await axios.get('/lugares/categorias')
    categorias.value = data
  } catch (err) {
    console.error('Error fetching categories:', err)
  }
}

async function fetchLugares() {
  loading.value = true
  try {
    const params = {}
    if (filters.value.ciudad_id) params.ciudad_id = filters.value.ciudad_id
    if (filters.value.categoria_id) params.categoria_id = filters.value.categoria_id
    
    const { data } = await axios.get('/lugares', { params })
    lugares.value = data
  } catch (err) {
    toast.add({ severity: 'error', summary: 'Error', detail: 'No se pudieron cargar los lugares', life: 3000 })
  } finally {
    loading.value = false
  }
}

function openCreateDialog() {
  editMode.value = false
  // Default to first city and category if available, or 1
  const defaultCity = ciudades.value.length > 0 ? ciudades.value[0].id : 1
  const defaultCat = categorias.value.length > 0 ? categorias.value[0].id : 2
  
  formData.value = { 
    ciudad_id: defaultCity, 
    categoria_id: defaultCat, 
    precio_aprox: 0, 
    estimated_duration_minutes: 60 
  }
  dialogVisible.value = true
}

function openEditDialog(lugar) {
  editMode.value = true
  formData.value = { ...lugar }
  dialogVisible.value = true
}

async function saveLugar() {
  try {
    if (editMode.value) {
      await axios.put(`/lugares/${formData.value.id}`, formData.value)
      toast.add({ severity: 'success', summary: 'Actualizado', detail: 'Lugar actualizado correctamente', life: 3000 })
    } else {
      await axios.post('/lugares', formData.value)
      toast.add({ severity: 'success', summary: 'Creado', detail: 'Lugar creado correctamente', life: 3000 })
    }
    dialogVisible.value = false
    await fetchLugares()
  } catch (err) {
    toast.add({ severity: 'error', summary: 'Error', detail: 'No se pudo guardar el lugar', life: 3000 })
  }
}

function confirmDelete(lugar) {
  confirm.require({
    message: `¿Estás seguro de eliminar "${lugar.nombre}"?`,
    header: 'Confirmar Eliminación',
    icon: 'pi pi-exclamation-triangle',
    acceptLabel: 'Sí, eliminar',
    rejectLabel: 'Cancelar',
    accept: async () => {
      try {
        await axios.delete(`/lugares/${lugar.id}`)
        toast.add({ severity: 'success', summary: 'Eliminado', detail: 'Lugar eliminado correctamente', life: 3000 })
        await fetchLugares()
      } catch (err) {
        toast.add({ severity: 'error', summary: 'Error', detail: 'No se pudo eliminar el lugar', life: 3000 })
      }
    }
  })
}
</script>
