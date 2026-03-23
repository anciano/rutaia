// src/features/user/api.js

import axios from '@/services/axios'

// — Chat —
export function getChatHistory(userId) {
  return axios.get('/chat/historial', {
    params: { user_id: userId }
  })
}

// Si tu backend expone un endpoint para enviar mensajes:
// export function sendMessage(userId, text) {
//   return axios.post('/chat/send', { user_id: userId, text })
// }

// — Planificaciones —
export function listPlans(userId) {
  return axios.get('/planificacion/planificaciones', {
    params: { user_id: userId }
  })
}

export function getActivePlan(userId) {
  return axios.get('/planificacion/planificaciones/activa', {
    params: { user_id: userId }
  })
}

export function deletePlan(planId) {
  return axios.delete(`/planificacion/planificaciones/${planId}`)
}


// — Detalle de plan —  
export function getPlanDetail(planId) {
  return axios.get(`/plandetalle/${planId}`)
}

// — Lugares en el plan —
export function addLugarToPlan(planId, payload) {
  // payload: { lugar_id?, nombre_custom?, ubicacion_custom?, horario_entrada, duracion_horas, costo_final? }
  return axios.post(`/plandetalle/${planId}/lugares`, payload)
}

export function deleteLugarFromPlan(planId, recordId) {
  return axios.delete(`/plandetalle/${planId}/lugares/${recordId}`)
}

// — Hospedajes en el plan —
export function addHospedajeToPlan(planId, payload) {
  // payload: { hospedaje_id?, nombre_custom?, direccion_custom?, fecha_check_in, fecha_check_out, costo_final? }
  return axios.post(`/plandetalle/${planId}/hospedaje`, payload)
}

export function deleteHospedajeFromPlan(planId, recordId) {
  return axios.delete(`/plandetalle/${planId}/hospedaje/${recordId}`)
}

// — Actividades en el plan —
export function addActividadToPlan(planId, payload) {
  // payload: { actividad_id?, nombre_custom?, duracion_horas, costo_final? }
  return axios.post(`/plandetalle/${planId}/actividades`, payload)
}

export function deleteActividadFromPlan(planId, recordId) {
  return axios.delete(`/plandetalle/${planId}/actividades/${recordId}`)
}

// — Transportes en el plan —
export function addTransporteToPlan(planId, payload) {
  // payload: { transporte_id?, tipo_custom?, origen_custom?, destino_custom?, tiempo_estimado_horas, costo_final? }
  return axios.post(`/plandetalle/${planId}/transporte`, payload)
}

export function deleteTransporteFromPlan(planId, recordId) {
  return axios.delete(`/plandetalle/${planId}/transporte/${recordId}`)
}
