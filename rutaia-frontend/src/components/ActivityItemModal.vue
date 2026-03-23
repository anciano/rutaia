Modal para crear/editar **actividades**.
```vue
<template>
  <Dialog v-model:visible="localVisible" :header="mode==='create'?'Añadir actividad':'Editar actividad'" modal>
    <div class="flex flex-col gap-4">
      <span class="p-float-label">
        <InputText id="desc" v-model="form.description" />
        <label for="desc">Descripción</label>
      </span>
      <Dropdown v-model="form.level" :options="niveles" optionLabel="label" optionValue="value" placeholder="Intensidad" />
      <InputNumber v-model="form.day" :min="1" placeholder="Día" />
      <InputNumber v-model="form.cost_clp" mode="currency" currency="CLP" locale="es-CL" placeholder="Costo" />
    </div>
    <template #footer>
      <Button label="Cancelar" text @click="close" />
      <Button :label="mode==='create'?'Guardar':'Actualizar'" @click="submit" />
    </template>
  </Dialog>
</template>
<script setup>
import { reactive, computed } from 'vue'
import { usePlanDetailStore } from '@/stores/planDetail'
import Dialog from 'primevue/dialog'; import InputText from 'primevue/inputtext'
import InputNumber from 'primevue/inputnumber'; import Dropdown from 'primevue/dropdown'
import Button from 'primevue/button'

const props = defineProps({ visible:Boolean, mode:{type:String,default:'create'}, item:Object})
const emit = defineEmits(['update:visible'])
const localVisible = computed({get:()=>props.visible,set:v=>emit('update:visible',v)})
const store = usePlanDetailStore()
const niveles=[{label:'Baja',value:'baja'},{label:'Media',value:'media'},{label:'Alta',value:'alta'}]
const form = reactive({ description:'', level:'media', day:null, cost_clp:null })
function close(){emit('update:visible',false)}
function submit(){ if(!form.description) return; const payload={description:form.description,level:form.level,day:form.day,cost_clp:form.cost_clp}; props.mode==='create'?store.create('activities',payload):store.update('activities',props.item.id,payload); close()}
</script>