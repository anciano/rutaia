// src/features/planificacion/api.js
import axios from '@/services/axios'

export function crearPlan(payload) {
  return axios.post('/planificacion/guardar', payload)
}

export function listarPlanes(userId) {
  return axios.get('/planificacion/planificaciones', { params: { user_id: userId } })
}

export function obtenerPlan(planId, userId) {
  return axios.get(`/planificacion/planificaciones/${planId}`, {
    params: { user_id: userId }
  })
}

export function activarPlan(planId, userId) {
  return axios.patch(`/planificacion/planificaciones/activar/${planId}`, null, {
    params: { user_id: userId }
  })
}

export function generarItinerario(planId, mode = 'replace') {
  return axios.post(`/plan/${planId}/generate?mode=${mode}`)
}

export function guardarInteresesMasivos(planId, catalogItemIds) {
  return axios.post(`/plan/${planId}/interests/bulk`, { catalog_item_ids: catalogItemIds })
}

export function organizarViaje(planId, pacing = 'normal') {
  return axios.post(`/plan/${planId}/organize`, { pacing })
}
