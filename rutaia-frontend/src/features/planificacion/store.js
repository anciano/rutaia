// src/features/planificacion/store.js
import { defineStore } from 'pinia'
import * as api from './api'

export const usePlanStore = defineStore('planificacion', {
  state: () => ({
    userId: null,
    planId: null,
    pasos: {
      origen: null,       // {id, nombre}
      fecha_inicio: null,
      fecha_fin: null,
      dias: 1,
      presupuesto: 0,
      participantes: [
        { edad: null, discapacidad: false, tipo_discapacidad: '' }
      ],
      preferencias: [],   // Array of preference objects or IDs
      tipo_aventura: 'cultural', // default
      transport_mode: 'auto_propio', // auto_propio, arrendar_auto, transporte_publico, movilidad_local
      intereses: []       // Selected catalog item IDs (Bolsa de intereses)
    },
    completed: false,
    loading: false,
    generationStatus: '',
    error: null
  }),
  actions: {
    setUserId(id) {
      this.userId = id
    },
    async crearPlan() {
      this.loading = true
      this.error = null
      this.generationStatus = 'Guardando tus preferencias...'
      try {
        const payload = {
          user_id: this.userId,
          origen_id: this.pasos.origen?.id,
          dias: this.pasos.dias,
          presupuesto: this.pasos.presupuesto,
          participantes: this.pasos.participantes,
          preferencias: this.pasos.preferencias.map(p => p.id || p),
          fecha_inicio: this.pasos.fecha_inicio || new Date().toISOString().split('T')[0],
          fecha_fin: this.pasos.fecha_fin || new Date(Date.now() + this.pasos.dias * 86400000).toISOString().split('T')[0],
          transport_mode: this.pasos.transport_mode
        }

        const { data } = await api.crearPlan(payload)
        this.planId = data.plan_id

        // Fase 2: Guardar Intereses (Bolsa)
        this.generationStatus = 'Guardando tus intereses...'
        if (this.pasos.intereses?.length > 0) {
          try {
            await api.guardarInteresesMasivos(data.plan_id, this.pasos.intereses)
          } catch (intErr) {
            console.warn('Error al guardar intereses:', intErr)
          }
        }

        // Fase 3: Organizar Itinerario (prioriza bolsa + cercanía)
        this.generationStatus = 'Organizando tus intereses...'
        try {
          await api.organizarViaje(data.plan_id, 'normal')
        } catch (genErr) {
          console.warn('Organización automática de intereses falló:', genErr)
        }

        // Fase 4: Completar Itinerario con sugerencias IA
        this.generationStatus = 'Completando con sugerencias locales...'
        try {
          await api.generarItinerario(data.plan_id, 'append')
        } catch (genErr) {
          console.warn('Completación automática de itinerario falló:', genErr)
        }

        this.generationStatus = '¡Todo listo!'
        this.completed = true
        return data
      } catch (err) {
        this.error = err.message || 'Error al procesar el plan'
        throw err
      } finally {
        this.loading = false
        this.generationStatus = ''
      }
    },
    async cargarPlanes() {
      this.loading = true
      const { data } = await api.listarPlanes(this.userId)
      this.loading = false
      return data
    },
    async obtenerPlan(planId) {
      this.loading = true
      const { data } = await api.obtenerPlan(planId, this.userId)
      this.loading = false
      return data
    },
    async activar(planId) {
      await api.activarPlan(planId, this.userId)
    },
    toggleInteres(itemId) {
      const idx = this.pasos.intereses.indexOf(itemId)
      if (idx > -1) {
        this.pasos.intereses.splice(idx, 1)
      } else {
        this.pasos.intereses.push(itemId)
      }
    }
  }
})
