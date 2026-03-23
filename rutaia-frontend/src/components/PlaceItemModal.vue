<!-- src/components/PlaceItemModal.vue -->
<template>
  <Dialog
    v-model:visible="localVisible"
    :header="mode === 'create' ? 'Añadir lugar' : 'Editar lugar'"
    modal
  >
    <div class="flex flex-col gap-4">
      <!-- Selección de lugar (catálogo global) -->
      <Dropdown
        v-model="form.lugar_id"
        :options="lugaresCatalogo"
        optionLabel="nombre"
        optionValue="id"
        placeholder="Selecciona un lugar"
        filter
      />

      <span class="p-float-label">
        <InputNumber
          v-model="form.day"
          :min="1"
          :max="store.totalDays"
        />
        <label>Día</label>
      </span>

      <!-- Horario de entrada (solo hora) -->
      <span class="p-float-label">
        <Calendar
          id="hora-entrada"
          v-model="form.horario_entrada"
          timeOnly
          hourFormat="24"
        />
        <label for="hora-entrada">Hora de entrada</label>
      </span>

      <!-- Duración en horas -->
      <span class="p-float-label">
        <InputNumber
          id="duracion"
          v-model="form.duracion_horas"
          :min="0.5"
          :step="0.5"
        />
        <label for="duracion">Duración (h)</label>
      </span>
    </div>

    <template #footer>
      <Button label="Cancelar" text @click="close" />
      <Button
        :label="mode === 'create' ? 'Guardar' : 'Actualizar'"
        icon="pi pi-check"
        @click="submit"
      />
    </template>
  </Dialog>
</template>

<script setup>
import { reactive, computed, onMounted, ref, watch } from 'vue'
import { usePlanDetailStore } from '@/stores/planDetail'
import Dialog     from 'primevue/dialog'
import Dropdown   from 'primevue/dropdown'
import Calendar   from 'primevue/calendar'
import InputNumber from 'primevue/inputnumber'
import Button     from 'primevue/button'
import axios      from '@/services/axios'

/* ---------- Props / emits ---------- */
const props = defineProps({
  visible: Boolean,
  mode:    { type: String, default: 'create' }, // create | edit
  item:    { type: Object, default: null },     // registro cuando edita
})
const emit = defineEmits(['update:visible'])

const localVisible = computed({
  get: () => props.visible,
  set: v  => emit('update:visible', v),
})

/* ---------- Catálogo de lugares ---------- */
const lugaresCatalogo = ref([])

async function fetchCatalogo() {
  const { data } = await axios.get('/lugares/')   // endpoint global
  lugaresCatalogo.value = data
}

/* ---------- Form ---------- */
const form = reactive({
  lugar_id: null,
  day: null,                          // ← NUEVO
  horario_entrada: null,
  duracion_horas: null,
})

function reset() {
  form.lugar_id        = null
  form.horario_entrada = null
  form.duracion_horas  = null
}

/* ---------- Sincroniza props -> form ---------- */
onMounted(fetchCatalogo)

watch(
  () => props.item,
  val => {
    if (props.mode === 'edit' && val) {
      form.lugar_id        = val.lugar_id
      form.horario_entrada = val.horario_entrada
        ? new Date(val.horario_entrada)
        : null
      form.duracion_horas  = val.duracion_horas
    } else {
      reset()
    }
  },
  { immediate: true }
)

/* ---------- Store ---------- */
const store = usePlanDetailStore()

function close() {
  emit('update:visible', false)
}

/* ---------- Submit ---------- */
async function submit() {
  if (!form.lugar_id || !form.day) return   // valida

  const payload = {
    lugar_id: form.lugar_id,
    day:      form.day,
    horario_entrada: form.horario_entrada.toISOString(),  // DateTime completo
    duracion_horas:  form.duracion_horas,
  }

  try {
    if (props.mode === 'create') {
      await store.create('places', payload)
    } else if (props.item) {
      await store.update('places', props.item.id, payload)
    }
    close()
  } catch (e) {
    console.error(e)
  }
}
</script>