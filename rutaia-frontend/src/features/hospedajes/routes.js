// src/features/hospedajes/routes.js

import HospedajesList  from './views/HospedajesList.vue'
import HospedajesAdmin from './views/HospedajesAdmin.vue'

export default [
  {
    path: 'hospedajes',
    name: 'HospedajesList',
    component: HospedajesList,
    meta: { requiresAuth: true }     // listado de hospedajes para usuarios autenticados
  },
  {
    path: 'admin/hospedajes',
    name: 'HospedajesAdmin',
    component: HospedajesAdmin,
    meta: { requiresAuth: true, role: 'admin' }  // CRUD completo solo para administradores
  }
]
