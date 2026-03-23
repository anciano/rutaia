// src/stores/planDetail.js
import { defineStore } from 'pinia'
import axios from '@/services/axios'

/*
  Backend en ESPAÑOL:
    /plan/{id}/lugares
    /plan/{id}/actividades
    /plan/{id}/transporte
    /plan/{id}/hospedaje
*/
const API_DETAIL = '/plan'
const API_PLAN = '/planificacion/planificaciones' // ← para PATCH de presupuesto/días

const endpointMap = {
  places: 'lugares',
  activities: 'actividades',
  transport: 'transporte',
  lodging: 'hospedaje',
}

export const usePlanDetailStore = defineStore('planDetail', {
  state: () => ({
    planId: '',
    plan: null,         // full V2 response (contains .days and .all_items)
    loading: false,
    error: null,
    activeSuggestions: [],
    isFetchingIA: false,
  }),

  getters: {
    days: (state) => state.plan?.days || [],
    all_items: (state) => state.plan?.all_items || [],
    wishlist: (state) => (state.plan?.all_items || []).filter(item => !item.day_id),

    points: (state) => {
      const pts = []
      state.plan?.all_items?.forEach(item => {
        if (item.metadata_json?.lat && item.metadata_json?.lng) {
          pts.push({
            id: item.id,
            lat: item.metadata_json.lat,
            lng: item.metadata_json.lng,
            name: item.metadata_json.name || item.name || 'Lugar',
            is_wishlist: !item.day_id
          })
        }
      })
      return pts
    },

    itineraryPoints: (state) => {
      // Solo items con day_id, ordenados por número de día y sort_order
      const scheduled = (state.plan?.all_items || []).filter(i => !!i.day_id)
      // Necesitamos los números de día para ordenar correctamente
      const dayMap = {}
      state.plan?.days?.forEach(d => { dayMap[d.id] = d.number })

      return scheduled
        .sort((a, b) => {
          const dayA = dayMap[a.day_id] || 0
          const dayB = dayMap[b.day_id] || 0
          if (dayA !== dayB) return dayA - dayB
          return (a.sort_order || 0) - (b.sort_order || 0)
        })
        .filter(i => i.metadata_json?.lat && i.metadata_json?.lng)
        .map(i => ({ lat: i.metadata_json.lat, lng: i.metadata_json.lng }))
    },

    all_segments: (state) => {
      return state.plan?.route_segments || []
    },

    budgetRemaining(state) {
      const budgetClp = state.plan?.budget_clp || state.plan?.presupuesto || 0
      // El gasto se calcula sobre TODO el plan (wishlist + agenda)
      const spent = state.plan?.all_items?.reduce((sum, i) => sum + (Number(i.cost_clp) || 0), 0) || 0
      return budgetClp - spent
    },
  },

  actions: {
    /* ---------- Carga inicial ---------- */
    async setPlanContext(planId) {
      this.planId = planId
      this.loadSuggestions() // Recuperar sugerencias de la sesión
      await this.fetchPlanV2()
    },

    loadSuggestions() {
      if (!this.planId) return
      const saved = localStorage.getItem(`ia_sug_${this.planId}`)
      this.activeSuggestions = saved ? JSON.parse(saved) : []
    },

    saveSuggestions() {
      if (!this.planId) return
      localStorage.setItem(`ia_sug_${this.planId}`, JSON.stringify(this.activeSuggestions))
    },

    async fetchPlanV2() {
      if (!this.planId) return
      this.loading = true
      try {
        const { data } = await axios.get(`${API_DETAIL}/v2/${this.planId}`)
        this.plan = data
      } catch (err) {
        this.error = err?.response?.data ?? err.message
        console.error('fetchPlanV2 error', err)
      } finally {
        this.loading = false
      }
    },

    async generateItinerary(planId, mode = 'replace') {
      try {
        await axios.post(`${API_DETAIL}/${planId}/generate?mode=${mode}`)
        await this.fetchPlanV2()
      } catch (err) {
        console.error('generateItinerary error', err)
        throw err
      }
    },

    async createUnifiedItem(payload) {
      try {
        // Siempre inyectamos el planId activo
        const finalPayload = { ...payload, plan_id: this.planId }
        await axios.post(`${API_DETAIL}/${this.planId}/unified/items`, finalPayload)
        await this.fetchPlanV2() // Recargar para ver el cambio en wishlist o timeline
      } catch (err) {
        console.error('createUnifiedItem error', err)
        throw err
      }
    },

    async updateUnifiedItem(itemId, payload) {
      try {
        await axios.put(`${API_DETAIL}/${this.planId}/unified/items/${itemId}`, payload)
        await this.fetchPlanV2()
      } catch (err) {
        console.error('updateUnifiedItem error', err)
        throw err
      }
    },

    async deleteUnifiedItem(itemId) {
      try {
        await axios.delete(`${API_DETAIL}/${this.planId}/unified/items/${itemId}`)
        await this.fetchPlanV2()
      } catch (err) {
        console.error('deleteUnifiedItem error', err)
        throw err
      }
    },

    // Nueva acción para mover items entre días (o a la wishlist)
    async moveItem(itemId, dayId) {
      try {
        await this.updateUnifiedItem(itemId, { day_id: dayId })
      } catch (err) {
        console.error('moveItem error', err)
      }
    },

    async addDay() {
      try {
        await axios.post(`${API_DETAIL}/${this.planId}/days`)
        await this.fetchPlanV2()
      } catch (err) {
        console.error('addDay error', err)
        throw err
      }
    },

    async deleteDay(dayId) {
      try {
        await axios.delete(`${API_DETAIL}/${this.planId}/days/${dayId}`)
        await this.fetchPlanV2()
      } catch (err) {
        console.error('deleteDay error', err)
        throw err
      }
    },

    async updateSegmentMode(segmentId, mode) {
      this.loading = true
      try {
        // We use the same unified items endpoint but for segments it's the plan_segments table
        // Actually, I should check if I have a specific endpoint for segments
        await axios.patch(`${API_DETAIL}/${this.planId}/segments/${segmentId}`, { transport_mode: mode })
        await this.fetchPlanV2()
      } catch (err) {
        console.error('updateSegmentMode error', err)
        throw err
      } finally {
        this.loading = false
      }
    }
  },
})
