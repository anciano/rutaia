<template>
  <Dialog v-model:visible="localVisible" :header="mode==='create'?'Añadir transporte':'Editar transporte'" modal>
    <div class="flex flex-col gap-4">
      <InputText v-model="form.origin_name" placeholder="Origen" />
      <InputText v-model="form.destination_name" placeholder="Destino" />
      <Dropdown v-model="form.mode" :options="modos" optionLabel="label" optionValue="value" placeholder="Modo" />
      <InputNumber v-model="form.distance_km" :min="0" placeholder="Distancia (km)" />
      <InputNumber v-model="form.duration_minutes" :min="0" placeholder="Duración (min)" />
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
const props=defineProps({visible:Boolean,mode:{type:String,default:'create'},item:Object});
const emit=defineEmits(['update:visible']); const localVisible=computed({get:()=>props.visible,set:v=>emit('update:visible',v)}); const store=usePlanDetailStore();
const modos=[{label:'Auto',value:'auto'},{label:'Bus',value:'bus'},{label:'Avión',value:'avion'},{label:'Barco',value:'barco'}]
const form=reactive({origin_name:'',destination_name:'',mode:'auto',distance_km:null,duration_minutes:null,cost_clp:null});
function close(){emit('update:visible',false)}
function submit(){if(!form.origin_name||!form.destination_name)return; const payload={...form}; props.mode==='create'?store.create('transport',payload):store.update('transport',props.item.id,payload); close()}
</script>