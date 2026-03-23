// features/user/routes.js
import Home    from './views/Home.vue'
import Chat    from './views/Chat.vue'
import HistorialPlanificaciones from './views/HistorialPlanificaciones.vue'
import PlanDetalle from './views/PlanDetalle.vue'

export default [
  { path: '',       name: 'Home',    component: Home,    meta: { requiresAuth: true } },
  { path: 'chat',   name: 'Chat',    component: Chat,    meta: { requiresAuth: true } },
  {
    path: 'historial',
    name: 'Historial',
    component: HistorialPlanificaciones,
    meta: { requiresAuth: true }
  },
  {
    path: 'plan/:planId',           //  ⬅️ cambia “:id” → “:planId”
    name: 'PlanDetalle',
    component: PlanDetalle,
    meta: { requiresAuth: true },
  }
]
