// src/router/index.js
import { createRouter, createWebHistory } from 'vue-router'
import { useUserStore } from '@/features/user/store'   // ⭐ Pinia
import LayoutBase from '@/layouts/LayoutBase.vue'

/* Lazy imports (vistas) */
const Login = () => import('@/features/public/views/Login.vue')
const Chat = () => import('@/features/user/views/Chat.vue')
const Historial = () => import('@/features/user/views/HistorialPlanificaciones.vue')
const PlanDetalle = () => import('@/features/user/views/PlanDetalle.vue')

/* Wizard */
const Paso1 = () => import('@/features/planificacion/views/Paso1Inicio.vue')
const Paso2 = () => import('@/features/planificacion/views/Paso2Dias.vue')
const Paso3 = () => import('@/features/planificacion/views/Paso3Presupuesto.vue')
const Paso4 = () => import('@/features/planificacion/views/Paso4Preferencias.vue')
const Paso5 = () => import('@/features/planificacion/views/Paso5BolsaIntereses.vue')
const Paso6 = () => import('@/features/planificacion/views/Paso6Resumen.vue')

/* Admin */
const GestionLugares = () => import('@/features/admin/views/GestionLugares.vue')
const AdminCatalog = () => import('@/features/admin/views/AdminCatalog.vue')
const RegionalExplorer = () => import('@/features/admin/views/RegionalExplorer.vue')
const LocalAgenda = () => import('@/features/admin/views/LocalAgenda.vue')
const TaxonomyManager = () => import('@/features/admin/views/TaxonomyManager.vue')
const LocalityManager = () => import('@/features/admin/views/LocalityManager.vue')
const AdminUsuarios = () => import('@/features/admin/views/AdminUsuarios.vue')

/* ─── Definición de rutas ─────────────────────────────────────────── */
const routes = [
  /* 1️⃣ Login fuera del layout */
  { path: '/login', name: 'Login', component: Login },

  /* 2️⃣ Resto con LayoutBase */
  {
    path: '/',
    component: LayoutBase,
    children: [
      { path: '', name: 'Home', component: Historial }, // raíz = historial
      { path: 'chat', name: 'Chat', component: Chat },
      { path: 'historial', name: 'Historial', component: Historial },

      /* Wizard */
      { path: 'plan/1', name: 'Paso1', component: Paso1 },
      { path: 'plan/2', name: 'Paso2', component: Paso2 },
      { path: 'plan/3', name: 'Paso3', component: Paso3 },
      { path: 'plan/4', name: 'Paso4', component: Paso4 },
      { path: 'plan/5', name: 'Paso5', component: Paso5 },
      { path: 'plan/6', name: 'Paso6', component: Paso6 },

      /* Detalle de un plan existente */
      { path: 'plan/:planId', name: 'PlanDetalle', component: PlanDetalle },

      /* Admin */
      { path: 'admin/lugares', name: 'GestionLugares', component: GestionLugares },
      { path: 'admin/catalog', name: 'AdminCatalog', component: AdminCatalog },
      { path: 'admin/explorer', name: 'RegionalExplorer', component: RegionalExplorer },
      { path: 'admin/agenda', name: 'LocalAgenda', component: LocalAgenda },
      { path: 'admin/taxonomy', name: 'AdminTaxonomy', component: TaxonomyManager },
      { path: 'admin/localities', name: 'AdminLocalities', component: LocalityManager },
      { path: 'admin/usuarios', name: 'AdminUsuarios', component: AdminUsuarios },
    ]
  }
]

/* ─── Router ─────────────────────────────────────────────────────── */
const router = createRouter({
  history: createWebHistory(),
  routes
})

/* ─── Guardia global ─────────────────────────────────────────────── */
router.beforeEach(async (to, from, next) => {
  const store = useUserStore()
  const userLS = JSON.parse(localStorage.getItem('usuario') || 'null')

  /* 0. Token devuelto por OAuth → Login.vue se encarga, dejamos pasar */
  if (to.query.token) return next()

  /* 1. Ruta pública: /login --------------------------------------- */
  if (to.name === 'Login') {
    if (!userLS) return next()                // sin sesión → mostrar login
    // con sesión: poblar store (si no estaba) y decidir destino
    if (!store.user) {
      store.$patch({ user: userLS })
      await store.loadPlans()
    }
    return next(store.plans.length ? { name: 'Historial' } : { name: 'Paso1' })
  }

  /* 2. Protegidas: requiere sesión -------------------------------- */
  if (!userLS) return next({ name: 'Login' })

  /* 3. Poblamos el store la primera vez --------------------------- */
  if (!store.user) {
    store.$patch({ user: userLS })
    await store.loadPlans()
  }

  const tienePlanes = store.plans.length > 0
  const esWizard = /^\/plan\/[1-6](\/|$)/.test(to.path)
  const esAdmin = to.path.startsWith('/admin') || to.path === '/chat' || to.path === '/usuarios'

  /* 4. Sin planes y fuera del wizard/admin → forzamos Paso1 */
  if (!tienePlanes && !esWizard && !esAdmin) return next('/plan/1')

  /* 5. Con planes y quiere ir al wizard manualmente → permitido */
  // if (tienePlanes && esWizard && to.name === 'Paso1') {
  //   return next({ name: 'Historial' })
  // }

  next()   // ✅ permitido
})

export default router
