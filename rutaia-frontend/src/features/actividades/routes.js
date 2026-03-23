// src/features/actividades/routes.js

import ActividadesList  from './views/ActividadesList.vue'
import ActividadesAdmin from './views/ActividadesAdmin.vue'

export default [
  {
    path: 'actividades',
    name: 'ActividadesList',
    component: ActividadesList,
    meta: { requiresAuth: true }     // listado de actividades para usuarios autenticados
  },
  {
    path: 'admin/actividades',
    name: 'ActividadesAdmin',
    component: ActividadesAdmin,
    meta: { requiresAuth: true, role: 'admin' }  // CRUD completo solo para administradores
  }
]
