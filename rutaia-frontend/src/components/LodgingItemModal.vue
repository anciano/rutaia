<template>
  <Dialog v-model:visible="localVisible" :header="mode==='create'?'Añadir hospedaje':'Editar hospedaje'" modal>
    <div class="flex flex-col gap-4">
      <InputText v-model="form.name" placeholder="Nombre" />
      <Calendar v-model="form.check_in" dateFormat="dd/mm/yy" placeholder="Check‑in" />
      <Calendar v-model="form.check_out" dateFormat="dd/mm/yy" placeholder="Check‑out" />
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
import InputNumber from 'primevue/inputnumber'; import Calendar from 'primevue/calendar'
import Button from 'primevue/button'
const props=defineProps({visible:Boolean,mode:{type:String,default:'create'},item:Object}); const emit=defineEmits(['update:visible']);
const localVisible=computed({get:()=>props.visible,set:v=>emit('update:visible',v)}); const store=usePlanDetailStore();
const form=reactive({name:'',check_in:null,check_out:null,cost_clp:null});
function close(){emit('update:visible',false)}
function submit(){if(!form.name||!form.check_in||!form.check_out)return; const payload={name:form.name,check_in:form.check_in,check_out:form.check_out,cost_clp:form.cost_clp}; props.mode==='create'?store.create('lodging',payload):store.update('lodging',props.item.id,payload); close()}
</script>