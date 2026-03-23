<!-- src/features/public/views/Login.vue -->
<template>
  <div class="flex justify-content-center align-items-center min-h-screen surface-ground">
    <Card class="shadow-3 w-30rem">
      <!-- cuerpo -->
      <template #content>
        <h2 class="text-center mb-4">Iniciar sesión</h2>

        <!-- OAuth -->
        <div class="flex justify-content-center align-items-center gap-3 mb-3">
          <Button label="Google" icon="pi pi-google" outlined rounded @click="loginWith('google')" />
          <Button label="Facebook" icon="pi pi-facebook" outlined rounded @click="loginWith('facebook')" />
        </div>

        <small class="text-center block mb-3">o usa tu cuenta de correo</small>

        <form @submit.prevent="onSubmit" class="flex flex-column gap-3">
          <span class="p-float-label">
            <InputText id="correo" v-model="form.correo" class="w-full" />
            <label for="correo">Correo</label>
          </span>

          <span class="p-float-label">
            <Password id="password" v-model="form.password" toggleMask class="w-full" />
            <label for="password">Contraseña</label>
          </span>

          <div class="flex justify-content-between align-items-center">
            <a class="cursor-pointer" @click.prevent="goRegister">¿No tienes cuenta? Regístrate</a>
            <Button label="Ingresar" icon="pi pi-sign-in" :loading="loading" type="submit" />
          </div>
        </form>
      </template>

      <!-- pie -->
      <template #footer>
        <small class="text-center block w-full">© 2025 RutaIA</small>
      </template>
    </Card>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useToast } from 'primevue/usetoast'

import InputText from 'primevue/inputtext'
import Password  from 'primevue/password'
import Button    from 'primevue/button'
import Card      from 'primevue/card'

import { login } from '@/features/public/api'
import { useUserStore } from '@/features/user/store'

const form    = ref({ correo: '', password: '' })
const loading = ref(false)
const router  = useRouter()
const toast   = useToast()
const store   = useUserStore()

async function onSubmit () {
  loading.value = true
  try {
    const { data } = await login(form.value.correo, form.value.password)
    const token   = data.access_token
    localStorage.setItem('token', token)

    const payload = JSON.parse(atob(token.split('.')[1]))
    const user    = { id: payload.sub, role: payload.role }
    localStorage.setItem('usuario', JSON.stringify(user))

    await store.loadUser(user)
    await store.loadPlans()          // carga los planes antes de redirigir

    toast.add({ severity:'success', summary:'¡Bienvenido!', detail:'Inicio de sesión correcto' })
    router.push({ name: store.plans.length ? 'Historial' : 'Paso1' })
  } catch (err) {
    const msg = err.response?.status === 401
      ? { severity:'warn', summary:'No registrado', detail:'Usuario o contraseña inválidos' }
      : { severity:'error', summary:'Error', detail:'Inténtalo más tarde' }
    toast.add(msg)
  } finally {
    loading.value = false
  }
}

function goRegister () {
  router.push({ name: 'Register' })
}

function loginWith (provider) {
  window.location.href = `${import.meta.env.VITE_API_URL}/auth/${provider}`
}

onMounted(() => {
  const url = new URL(window.location.href)
  const token = url.searchParams.get('token')
  if (token) {
    localStorage.setItem('token', token)
    // decodifica payload:
    const payload = JSON.parse(atob(token.split('.')[1]))
    localStorage.setItem('usuario', JSON.stringify({ id: payload.sub, role: payload.role }))
    router.replace({ name: 'Historial' })   // o 'Paso1'
  }
})

</script>


