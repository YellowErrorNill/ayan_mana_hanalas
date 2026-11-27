<script setup>
import { computed, ref } from 'vue'
import { auth, setAuth, clearAuth } from '../store'

const API = 'http://127.0.0.1:8000'

const activeTab = ref('login') // 'login' | 'register'
const message = ref('')

const loginEmail = ref('')
const loginPassword = ref('')

const regFirstName = ref('')
const regLastName = ref('')
const regEmail = ref('')
const regPassword = ref('')

const currentUser = computed(() => auth.username)

function switchTab(tab) {
  activeTab.value = tab
  message.value = ''
}

async function register() {
  const res = await fetch(`${API}/register`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      username: regEmail.value,
      password: regPassword.value,
      first_name: regFirstName.value,
      last_name: regLastName.value,
    }),
  })
  const data = await res.json()
  if (res.ok) {
    message.value = 'Регистрация успешна — теперь войдите'
    activeTab.value = 'login'
    loginEmail.value = regEmail.value
  } else {
    message.value = data.detail || 'Ошибка регистрации'
  }
}

async function login() {
  const res = await fetch(`${API}/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username: loginEmail.value, password: loginPassword.value }),
  })
  const data = await res.json()
  if (res.ok) {
    setAuth(data.token, data.username)
    message.value = ''
  } else {
    message.value = data.detail
  }
}

async function logout() {
  await fetch(`${API}/logout`, {
    method: 'POST',
    headers: { Authorization: `Bearer ${auth.token}` },
  })
  clearAuth()
}
</script>

<template>
  <div class="auth">
    <div class="band band-top"></div>

    <div v-if="currentUser" class="logged-in">
      <p>Вы вошли как {{ currentUser }}</p>
      <button class="submit-btn" @click="logout">Выйти</button>
    </div>

    <div v-else class="auth-form">
      <div class="tabs">
        <button :class="['tab', { active: activeTab === 'login' }]" @click="switchTab('login')">
          Вход
        </button>
        <button :class="['tab', { active: activeTab === 'register' }]" @click="switchTab('register')">
          Регистрация
        </button>
      </div>

      <form v-if="activeTab === 'login'" class="fields" @submit.prevent="login">
        <input v-model="loginEmail" type="email" placeholder="E-mail" required>
        <input v-model="loginPassword" type="password" placeholder="Пароль" required>
        <button type="submit" class="submit-btn">Войти</button>
      </form>

      <form v-else class="fields" @submit.prevent="register">
        <h3 class="section-title">Личные данные</h3>
        <input v-model="regFirstName" type="text" placeholder="Имя" required>
        <input v-model="regLastName" type="text" placeholder="Фамилия" required>

        <h3 class="section-title">Данные для входа</h3>
        <input v-model="regEmail" type="email" placeholder="E-mail" required>
        <input v-model="regPassword" type="password" placeholder="Пароль" required>
        <button type="submit" class="submit-btn">Зарегистрироваться</button>
      </form>

      <p v-if="message" class="message">{{ message }}</p>
    </div>

    <div class="band band-bottom"></div>
  </div>
</template>

<style scoped>
.auth {
  min-height: calc(100dvh - 68px);
  display: flex;
  flex-direction: column;
  font-family: 'Cousine', monospace;
  background: #383938;
}

.band {
  flex-shrink: 0;
  height: 80px;
  background: #383938 url('/design/pixel-band.png') repeat-x top / auto 100%;
}

.band-bottom {
  margin-top: auto;
  transform: scaleY(-1);
}

.auth-form,
.logged-in {
  width: 316px;
  max-width: calc(100% - 32px);
  margin: 60px auto 40px;
}

.tabs {
  display: flex;
  gap: 24px;
  margin-bottom: 48px;
}

.tab {
  padding: 0 0 6px;
  border: none;
  border-bottom: 2px solid transparent;
  background: none;
  color: #cafb87;
  font-family: 'Cousine', monospace;
  font-size: 24px;
  cursor: pointer;
}

.tab.active {
  border-bottom-color: #cafb87;
}

.fields {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.section-title {
  margin: 14px 0 2px;
  color: #cafb87;
  font-size: 18px;
  font-weight: 400;
}

.fields input {
  width: 100%;
  box-sizing: border-box;
  height: 50px;
  padding: 0 17px;
  border: 1px solid #cdcdcd;
  border-radius: 0;
  background: transparent;
  color: #eee;
  font-family: 'Cousine', monospace;
  font-size: 16px;
}

.fields input::placeholder {
  color: #cdcdcd;
}

.fields input:focus {
  outline: none;
  border-color: #cafb87;
}

.submit-btn {
  width: 100%;
  height: 44px;
  margin-top: 16px;
  border: none;
  border-radius: 0;
  background: #cafb87;
  color: #383938;
  font-family: 'Cousine', monospace;
  font-size: 16px;
  cursor: pointer;
}

.message {
  margin-top: 16px;
  color: #cafb87;
  font-size: 14px;
}

.logged-in p {
  color: #eee;
  font-size: 16px;
}
</style>
