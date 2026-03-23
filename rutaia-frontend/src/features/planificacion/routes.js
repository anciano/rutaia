// features/planificacion/routes.js
import Paso1Inicio       from './views/Paso1Inicio.vue'
import Paso2Dias         from './views/Paso2Dias.vue'
import Paso3Presupuesto  from './views/Paso3Presupuesto.vue'
import Paso4Preferencias from './views/Paso4Preferencias.vue'
import Paso5Bolsa        from './views/Paso5BolsaIntereses.vue'
import Paso6Resumen      from './views/Paso6Resumen.vue'

export default [
  {
    path: 'plan/1',
    name: 'Paso1',
    component: Paso1Inicio,
    meta: { requiresAuth: true, isWizard: true }
  },
  {
    path: 'plan/2',
    name: 'Paso2',
    component: Paso2Dias,
    meta: { requiresAuth: true, isWizard: true }
  },
  {
    path: 'plan/3',
    name: 'Paso3',
    component: Paso3Presupuesto,
    meta: { requiresAuth: true, isWizard: true }
  },
  {
    path: 'plan/4',
    name: 'Paso4',
    component: Paso4Preferencias,
    meta: { requiresAuth: true, isWizard: true }
  },
  {
    path: 'plan/5',
    name: 'Paso5',
    component: Paso5Bolsa,
    meta: { requiresAuth: true, isWizard: true }
  },
  {
    path: 'plan/6',
    name: 'Paso6',
    component: Paso6Resumen,
    meta: { requiresAuth: true, isWizard: true }
  }
]
