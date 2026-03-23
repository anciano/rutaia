<template>
  <div class="locality-manager p-4">
    <div class="flex justify-content-between align-items-center mb-4">
      <h2 class="text-2xl font-bold m-0">Gestión de Localidades</h2>
      <Button label="Nueva Localidad" icon="pi pi-plus" @click="openNew" class="p-button-success" />
    </div>

    <DataTable :value="localities" :loading="loading" stripedRows responsiveLayout="stack" breakpoint="960px">
      <template #empty>No se encontraron localidades.</template>
      
      <Column field="name" header="Nombre" sortable />
      <Column field="type" header="Tipo">
        <template #body="{ data }">
          <Tag :value="data.type" :severity="getSeverity(data.type)" />
        </template>
      </Column>
      <Column field="comuna" header="Comuna" />
      <Column field="region" header="Región" />
      <Column header="Coordenadas">
        <template #body="{ data }">
          <span class="text-sm monospace">{{ data.lat.toFixed(4) }}, {{ data.lng.toFixed(4) }}</span>
        </template>
      </Column>
      <Column field="is_active" header="Estado">
        <template #body="{ data }">
          <i class="pi" :class="data.is_active ? 'pi-check-circle text-green-500' : 'pi-times-circle text-red-500'"></i>
        </template>
      </Column>
      <Column header="Acciones" class="text-right">
        <template #body="{ data }">
          <Button icon="pi pi-pencil" @click="editLocality(data)" class="p-button-text p-button-rounded mr-2" />
          <Button icon="pi pi-trash" @click="confirmDelete(data)" class="p-button-text p-button-rounded p-button-danger" />
        </template>
      </Column>
    </DataTable>

    <Dialog v-model:visible="localityDialog" :header="editing ? 'Editar Localidad' : 'Nueva Localidad'" :modal="true" :style="{width: '500px'}">
      <div class="flex flex-column gap-3 mt-2">
        <div class="flex flex-column gap-1">
          <label for="name" class="font-semibold">Nombre</label>
          <InputText id="name" v-model="form.name" required autofocus />
        </div>
        
        <div class="flex flex-column gap-1">
          <label for="slug" class="font-semibold">Slug (URL)</label>
          <InputText id="slug" v-model="form.slug" placeholder="pueblo-ejemplo" />
        </div>

        <div class="flex flex-column gap-1">
          <label class="font-semibold">Tipo de Localidad</label>
          <Dropdown v-model="form.type" :options="localityTypes" optionLabel="label" optionValue="value" placeholder="Seleccionar Tipo" />
        </div>

        <div class="grid">
          <div class="col-6 flex flex-column gap-1">
            <label for="lat" class="font-semibold">Latitud</label>
            <InputNumber id="lat" v-model="form.lat" :minFractionDigits="6" mode="decimal" />
          </div>
          <div class="col-6 flex flex-column gap-1">
            <label for="lng" class="font-semibold">Longitud</label>
            <InputNumber id="lng" v-model="form.lng" :minFractionDigits="6" mode="decimal" />
          </div>
        </div>

        <div class="grid">
          <div class="col-6 flex flex-column gap-1">
            <label for="region" class="font-semibold">Región</label>
            <Dropdown id="region" v-model="form.region" :options="regionOptions" placeholder="Región" />
          </div>
          <div class="col-6 flex flex-column gap-1">
            <label for="comuna" class="font-semibold">Comuna</label>
            <Dropdown id="comuna" v-model="form.comuna" :options="comunaOptions" placeholder="Comuna" filter />
          </div>
        </div>

        <div class="flex flex-column gap-1">
          <label for="desc" class="font-semibold">Descripción</label>
          <Textarea id="desc" v-model="form.description" rows="3" />
        </div>

        <div class="flex align-items-center gap-2">
          <Checkbox v-model="form.is_active" :binary="true" id="active" />
          <label for="active">Activa</label>
        </div>
      </div>
      
      <template #footer>
        <Button label="Cancelar" icon="pi pi-times" class="p-button-text" @click="localityDialog = false" />
        <Button label="Guardar" icon="pi pi-check" @click="saveLocality" :loading="saving" />
      </template>
    </Dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue';
import axios from '@/services/axios';
import { useToast } from 'primevue/usetoast';

const localities = ref([]);
const loading = ref(false);
const saving = ref(false);
const localityDialog = ref(false);
const editing = ref(false);
const toast = useToast();

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const localityTypes = [
  { label: 'Ciudad (Mayor)', value: 'city' },
  { label: 'Pueblo (Town)', value: 'town' },
  { label: 'Villa (Village)', value: 'village' },
  { label: 'Caserío (Hamlet)', value: 'hamlet' },
  { label: 'Puerto', value: 'port' },
  { label: 'Sector Geográfico', value: 'sector' },
  { label: 'Base Destino', value: 'destination' }
];

const regionOptions = ['Aysén', 'Magallanes', 'Los Lagos'];

const comunaOptions = [
  'Coyhaique', 'Lago Verde', 'Aysén', 'Cisnes', 'Guaitecas', 
  'Cochrane', 'O\'Higgins', 'Tortel', 'Chile Chico', 'Río Ibáñez'
];

const form = ref({
  id: null,
  name: '',
  slug: '',
  type: 'village',
  lat: -45.57,
  lng: -72.06,
  comuna: 'Coyhaique',
  region: 'Aysén',
  description: '',
  is_active: true
});

watch(() => form.value.name, (newVal) => {
  if (!form.value.id && newVal) {
    form.value.slug = newVal.toLowerCase()
      .normalize("NFD").replace(/[\u0300-\u036f]/g, "")
      .replace(/ /g, '-')
      .replace(/[^\w-]/g, '');
  }
});

const loadLocalities = async () => {
  loading.value = true;
  try {
    const res = await axios.get('/admin/localities');
    localities.value = res.data;
  } catch (err) {
    console.error(err);
    toast.add({ severity: 'error', summary: 'Error', detail: 'No se pudieron cargar las localidades' });
  } finally {
    loading.value = false;
  }
};

const openNew = () => {
  form.value = {
    id: null,
    name: '',
    slug: '',
    type: 'village',
    lat: -45.57,
    lng: -72.06,
    comuna: 'Coyhaique',
    region: 'Aysén',
    description: '',
    is_active: true
  };
  editing.value = false;
  localityDialog.value = true;
};

const editLocality = (data) => {
  form.value = { ...data };
  editing.value = true;
  localityDialog.value = true;
};

const saveLocality = async () => {
  if (!form.value.name || !form.value.slug) return;
  
  saving.value = true;
  try {
    if (editing.value) {
      await axios.put(`/admin/localities/${form.value.id}`, form.value);
      toast.add({ severity: 'success', summary: 'Éxito', detail: 'Localidad actualizada' });
    } else {
      await axios.post('/admin/localities', form.value);
      toast.add({ severity: 'success', summary: 'Éxito', detail: 'Localidad creada' });
    }
    localityDialog.value = false;
    loadLocalities();
  } catch (err) {
    console.error(err);
    toast.add({ severity: 'error', summary: 'Error', detail: 'No se pudo guardar la localidad' });
  } finally {
    saving.value = false;
  }
};

const confirmDelete = async (data) => {
  if (confirm(`¿Eliminar la localidad ${data.name}?`)) {
    try {
      await axios.delete(`/admin/localities/${data.id}`);
      toast.add({ severity: 'success', summary: 'Éxito', detail: 'Localidad eliminada' });
      loadLocalities();
    } catch (err) {
      console.error(err);
      toast.add({ severity: 'error', summary: 'Error', detail: 'No se pudo eliminar' });
    }
  }
};

const getSeverity = (type) => {
  switch (type) {
    case 'city': return 'success';
    case 'town': return 'info';
    case 'village': return 'warning';
    case 'port': return 'secondary';
    default: return null;
  }
};

onMounted(loadLocalities);
</script>

<style scoped>
.monospace {
  font-family: monospace;
}
</style>
