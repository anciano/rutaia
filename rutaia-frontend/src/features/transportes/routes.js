// src/features/transportes/routes.js

import TransportesList  from './views/TransportesList.vue'
import TransportesAdmin from './views/TransportesAdmin.vue'

export default [
  {
    path: 'transportes',
    name: 'TransportesList',
    component: TransportesList,
    meta: { requiresAuth: true }     // listado público para usuarios autenticados
  },
  {
    path: 'admin/transportes',
    name: 'TransportesAdmin',
    component: TransportesAdmin,
    meta: { requiresAuth: true, role: 'admin' }  // CRUD completo solo para admins
  }
]