// src/features/public/api.js

import axios from '@/services/axios'

export function login(correo, password) {
  return axios.post('/auth/login', { correo, password })
}