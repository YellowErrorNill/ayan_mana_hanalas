<script setup>
import { ref, onMounted } from 'vue'

const API = 'http://127.0.0.1:8000'

const username = ref('')
const want = ref([])
const visited = ref([])
const activeTab = ref('want') // 'want' | 'visited'
const loading = ref(true)
const error = ref('')
const authorized = ref(true)
const pending = ref(new Set())

onMounted(async () => {
  const token = localStorage.getItem('token')
  if (!token) {
    authorized.value = false
    loading.value = false
    return
  }
  try {
    const res = await fetch(`${API}/profile`, {
      headers: { Authorization: `Bearer ${token}` },
    })
    if (res.status === 401) {
      authorized.value = false
      return
    }
    const data = await res.json()
    username.value = data.username
    want.value = data.want
    visited.value = data.visited
  } catch {
    error.value = 'Не удалось загрузить профиль'
  } finally {
    loading.value = false
  }
})

async function markVisited(card) {
  if (pending.value.has(card.id)) return
  pending.value.add(card.id)
  try {
    const res = await fetch(`${API}/saved/${card.id}/visit`, {
      method: 'POST',
      headers: { Authorization: `Bearer ${localStorage.getItem('token')}` },
    })
    if (res.ok) {
      want.value = want.value.filter((c) => c.id !== card.id)
      visited.value.push(card)
    }
  } finally {
    pending.value.delete(card.id)
  }
}

async function markWant(card) {
  if (pending.value.has(card.id)) return
  pending.value.add(card.id)
  try {
    const res = await fetch(`${API}/saved/${card.id}/unvisit`, {
      method: 'POST',
      headers: { Authorization: `Bearer ${localStorage.getItem('token')}` },
    })
    if (res.ok) {
      visited.value = visited.value.filter((c) => c.id !== card.id)
      want.value.push(card)
    }
  } finally {
    pending.value.delete(card.id)
  }
}
</script>

<template>
  <div class="profile">
    <p v-if="loading">Загрузка…</p>

    <div v-else-if="!authorized">
      <p>Вы не авторизованы</p>
      <router-link to="/auth">Войти</router-link>
    </div>

    <p v-else-if="error">{{ error }}</p>

    <template v-else>
      <h1>Профиль: {{ username }}</h1>

      <div class="tabs">
        <button
          :class="['tab', { active: activeTab === 'want' }]"
          @click="activeTab = 'want'"
        >
          Хочу побывать ({{ want.length }})
        </button>
        <button
          :class="['tab', { active: activeTab === 'visited' }]"
          @click="activeTab = 'visited'"
        >
          Побывал(а) ({{ visited.length }})
        </button>
      </div>

      <div v-if="activeTab === 'want'">
        <p v-if="!want.length">Пока пусто — посвайпайте карточки</p>
        <div v-for="card in want" :key="card.id" class="place">
          <div
            class="place-photo"
            :style="card.image ? { backgroundImage: `url(${API}${card.image})` } : {}"
          ></div>
          <div class="place-text">
            <h3>{{ card.name }}</h3>
            <p>{{ card.description }}</p>
          </div>
          <button :disabled="pending.has(card.id)" @click="markVisited(card)">
            Побывал(а)
          </button>
        </div>
      </div>

      <div v-else>
        <p v-if="!visited.length">Вы ещё нигде не отметились</p>
        <div v-for="card in visited" :key="card.id" class="place">
          <div
            class="place-photo"
            :style="card.image ? { backgroundImage: `url(${API}${card.image})` } : {}"
          ></div>
          <div class="place-text">
            <h3>{{ card.name }}</h3>
            <p>{{ card.description }}</p>
          </div>
          <button :disabled="pending.has(card.id)" @click="markWant(card)">
            Назад
          </button>
        </div>
      </div>
    </template>
  </div>
</template>

<style scoped>
.profile {
  max-width: 430px;
  margin: 0 auto;
  padding: 8px 12px;
}

.tabs {
  display: flex;
  gap: 8px;
  margin-bottom: 12px;
}

.tab {
  flex: 1;
  padding: 10px 0;
  border: none;
  border-bottom: 3px solid transparent;
  background: none;
  font-size: 15px;
  color: #999;
  cursor: pointer;
}

.tab.active {
  color: #cafb87;
  border-bottom-color: #cafb87;
  font-weight: 600;
}

.place {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px 0;
  border-bottom: 1px solid #4a4b4a;
}

.place-photo {
  width: 72px;
  height: 72px;
  flex-shrink: 0;
  border-radius: 10px;
  background: #cfd8dc center/cover no-repeat;
}

.place-text {
  flex: 1;
}

.place-text h3 {
  margin: 0 0 4px;
}

.place-text p {
  margin: 0;
  font-size: 13px;
  color: #bbb;
}

.place button {
  padding: 8px 10px;
  border: 1px solid #cafb87;
  border-radius: 0;
  background: transparent;
  color: #cafb87;
  cursor: pointer;
  white-space: nowrap;
}

.place button:disabled {
  opacity: 0.5;
}
</style>
