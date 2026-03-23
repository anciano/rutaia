import { defineStore } from 'pinia'
import * as api from './api'
import axios from '@/services/axios'  

export const useUserStore = defineStore('user', {
  state: () => ({
    user: null,
    plans: [],
    activePlan: null,
    chatHistory: [],
    planDetail: {
      lugares: [],
      hospedaje: [],
      actividades: [],
      transporte: []
    },
    loading: false
  }),
  actions: {
    setUser(userData) {
      this.user = userData
    },
    async loadUser(userData) {
      this.user = userData
      await this.fetchPlans()
      await this.fetchActivePlan()
      await this.fetchChatHistory()
    },
    async loadPlans () {           // ⭐ NUEVO
      if (!this.user) return
      const { data } = await axios.get('/planificacion/planificaciones', {
        params: { user_id: this.user.id }
      })
      this.plans = data
    },
    async fetchPlans() {
      if (!this.user) return
      this.loading = true
      try {
        const { data } = await api.listPlans(this.user.id)
        this.plans = data
      } finally {
        this.loading = false
      }
    },
    async deletePlan(planId) {
      this.loading = true
      try {
        await api.deletePlan(planId)
        // Refresh plans after deletion
        if (this.user) {
          const { data } = await api.listPlans(this.user.id)
          this.plans = data
        }
      } finally {
        this.loading = false
      }
    },
    async fetchActivePlan() {
      if (!this.user) return
      this.loading = true
      try {
        const { data } = await api.getActivePlan(this.user.id)
        this.activePlan = data
      } finally {
        this.loading = false
      }
    },
    async fetchChatHistory() {
      if (!this.user) return
      this.loading = true
      try {
        const { data } = await api.getChatHistory(this.user.id)
        this.chatHistory = data
      } finally {
        this.loading = false
      }
    },
    async sendMessage(text) {
      if (!this.user) return
      this.loading = true
      try {
        await api.sendMessage(this.user.id, text)
        await this.fetchChatHistory()
      } finally {
        this.loading = false
      }
    },
    async fetchPlanDetail(planId) {
      this.loading = true
      try {
        const { data } = await api.getPlanDetail(planId)
        this.planDetail = data
        return data
      } finally {
        this.loading = false
      }
    },
    async addLugar(planId, payload) {
      this.loading = true
      try {
        await api.addLugarToPlan(planId, payload)
        await this.fetchPlanDetail(planId)
      } finally {
        this.loading = false
      }
    },
    async deleteLugar(planId, recordId) {
      this.loading = true
      try {
        await api.deleteLugarFromPlan(planId, recordId)
        await this.fetchPlanDetail(planId)
      } finally {
        this.loading = false
      }
    },
    async addHospedaje(planId, payload) {
      this.loading = true
      try {
        await api.addHospedajeToPlan(planId, payload)
        await this.fetchPlanDetail(planId)
      } finally {
        this.loading = false
      }
    },
    async deleteHospedaje(planId, recordId) {
      this.loading = true
      try {
        await api.deleteHospedajeFromPlan(planId, recordId)
        await this.fetchPlanDetail(planId)
      } finally {
        this.loading = false
      }
    },
    async addActividad(planId, payload) {
      this.loading = true
      try {
        await api.addActividadToPlan(planId, payload)
        await this.fetchPlanDetail(planId)
      } finally {
        this.loading = false
      }
    },
    async deleteActividad(planId, recordId) {
      this.loading = true
      try {
        await api.deleteActividadFromPlan(planId, recordId)
        await this.fetchPlanDetail(planId)
      } finally {
        this.loading = false
      }
    },
    async addTransporte(planId, payload) {
      this.loading = true
      try {
        await api.addTransporteToPlan(planId, payload)
        await this.fetchPlanDetail(planId)
      } finally {
        this.loading = false
      }
    },
    async deleteTransporte(planId, recordId) {
      this.loading = true
      try {
        await api.deleteTransporteFromPlan(planId, recordId)
        await this.fetchPlanDetail(planId)
      } finally {
        this.loading = false
      }
    }
  }
})
