// src/main.js  – PrimeVue 4 en “styled mode”

import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import { createPinia } from 'pinia'

// PrimeVue
import PrimeVue from 'primevue/config'
import Lara from '@primevue/themes/lara'          // preset JS del tema (NO es CSS)

// Estilos que SÍ existen
import 'primeicons/primeicons.css'     // iconos
import 'primeflex/primeflex.css'       // utilidades flex
import './assets/style.css'            // tus estilos globales
import 'leaflet/dist/leaflet.css'      // mapas

// Solución para iconos de Leaflet en Vite
import L from 'leaflet'
import markerIcon2x from 'leaflet/dist/images/marker-icon-2x.png'
import markerIcon from 'leaflet/dist/images/marker-icon.png'
import markerShadow from 'leaflet/dist/images/marker-shadow.png'

delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: markerIcon2x,
  iconUrl: markerIcon,
  shadowUrl: markerShadow,
});

// (opc.) servicios y componentes globales
import ToastService from 'primevue/toastservice'
import ConfirmationService from 'primevue/confirmationservice'
import Button from 'primevue/button'
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'
import Dialog from 'primevue/dialog'
import InputText from 'primevue/inputtext'
import Password from 'primevue/password'
import Card from 'primevue/card'
import Dropdown from 'primevue/dropdown'
import InputNumber from 'primevue/inputnumber'
import Textarea from 'primevue/textarea'
import Toast from 'primevue/toast'
import Tag from 'primevue/tag'
import Checkbox from 'primevue/checkbox'
import TreeTable from 'primevue/treetable'
import ConfirmDialog from 'primevue/confirmdialog'
import { LMap, LTileLayer, LMarker, LPopup, LPolyline } from '@vue-leaflet/vue-leaflet';

const app = createApp(App)

/* ─── Plugins ──────────────────────────────────────────────── */
app.use(router)
app.use(createPinia())

app.use(PrimeVue, {
  ripple: true,
  theme: {            // ✅ así sí carga Lara
    preset: Lara,
    options: {
      darkModeSelector: '.dark',
    }
  },
  locale: {
    dayNames: ["Domingo", "Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado"],
    dayNamesShort: ["Dom", "Lun", "Mar", "Mié", "Jue", "Vie", "Sáb"],
    dayNamesMin: ["D", "L", "M", "X", "J", "V", "S"],
    monthNames: ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"],
    monthNamesShort: ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"],
    today: 'Hoy',
    clear: 'Limpiar',
    firstDayOfWeek: 1,
    dateFormat: 'dd/mm/yy'
  }
})
app.use(ToastService)
app.use(ConfirmationService)
/* ─── Componentes globales ─────────────────────────────────── */
app.component('Button', Button)
app.component('DataTable', DataTable)
app.component('Column', Column)
app.component('Dialog', Dialog)
app.component('InputText', InputText)
app.component('Password', Password)
app.component('Card', Card)
app.component('Dropdown', Dropdown)
app.component('InputNumber', InputNumber)
app.component('Textarea', Textarea)
app.component('Toast', Toast)
app.component('Tag', Tag)
app.component('Checkbox', Checkbox)
app.component('TreeTable', TreeTable)
app.component('ConfirmDialog', ConfirmDialog)
app.component('LMap', LMap);
app.component('LTileLayer', LTileLayer);
app.component('LMarker', LMarker);
app.component('LPopup', LPopup);
app.component('LPolyline', LPolyline);

app.mount('#app')
