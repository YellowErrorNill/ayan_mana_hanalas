<script setup>
import { ref } from 'vue'

const API = 'http://127.0.0.1:8000'

const regUsername = ref('')
const regPassword = ref('')
const loginUsername = ref('')
const loginPassword = ref('')
const message = ref('')
const currentUser = ref(localStorage.getItem('username') || '')
const token = ref(localStorage.getItem('token') || '')

async function register() {
  const res = await fetch(`${API}/register`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username: regUsername.value, password: regPassword.value }),
  })
  const data = await res.json()
  message.value = data.detail || data.message
}

async function login() {
  const res = await fetch(`${API}/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username: loginUsername.value, password: loginPassword.value }),
  })
  const data = await res.json()
  if (res.ok) {
    token.value = data.token
    currentUser.value = data.username
    localStorage.setItem('token', data.token)
    localStorage.setItem('username', data.username)
    message.value = ''
  } else {
    message.value = data.detail
  }
}

async function logout() {
  await fetch(`${API}/logout`, {
    method: 'POST',
    headers: { Authorization: `Bearer ${token.value}` },
  })
  token.value = ''
  currentUser.value = ''
  localStorage.removeItem('token')
  localStorage.removeItem('username')
}
</script>

<template>
  <div v-if="!currentUser">
    <h2>Регистрация</h2>
    <input v-model="regUsername" placeholder="E-mail">
    <input v-model="regPassword" type="password" placeholder="Пароль">
    <button @click="register">Зарегистрироваться</button>

    <h2>Вход</h2>
    <input v-model="loginUsername" placeholder="E-mail">
    <input v-model="loginPassword" type="password" placeholder="Пароль">
    <button @click="login">Войти</button>

    <p>{{ message }}</p>
  </div>

  <div v-else>
    <p>Вы вошли как {{ currentUser }}</p>
    <button @click="logout">Выйти</button>
  </div>
</template>

<style scoped>
div {
  padding: 8px 16px;
}

input {
  display: block;
  margin-bottom: 8px;
  padding: 9px 12px;
  border: 1px solid #555;
  border-radius: 6px;
  background: #2c2d2c;
  color: #eee;
  font-size: 14px;
}

input:focus {
  outline: none;
  border-color: #cafb87;
}

button {
  padding: 9px 16px;
  border: 1px solid #cafb87;
  border-radius: 0;
  background: transparent;
  color: #cafb87;
  cursor: pointer;
}

h2 {
  color: #eee;
}
</style>
