// src/features/lugares/routes.js

import LugaresList  from './views/LugaresList.vue'
import LugaresAdmin from './views/LugaresAdmin.vue'

export default [
  {
    path: 'lugares',
    name: 'LugaresList',
    component: LugaresList,
    meta: { requiresAuth: true }        // usuario normal
  },
  {
    path: 'admin/lugares',
    name: 'LugaresAdmin',
    component: LugaresAdmin,
    meta: { requiresAuth: true, role: 'admin' }
  }
]