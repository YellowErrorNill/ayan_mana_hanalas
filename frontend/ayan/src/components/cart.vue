<script setup>
import { ref, computed, onMounted } from 'vue'

const API = 'http://127.0.0.1:8000'

const cards = ref([])
const loading = ref(true)
const error = ref('')
const notice = ref('')

// верхней карточки
const dragX = ref(0)
const dragging = ref(false)
const flying = ref('') 
let startX = 0

const topCard = computed(() => cards.value[0])
const nextCard = computed(() => cards.value[1])

onMounted(async () => {
  try {
    const res = await fetch(`${API}/cards`)
    cards.value = await res.json()
  } catch {
    error.value = 'Не удалось загрузить карточки'
  } finally {
    loading.value = false
  }
})

function photoUrl(card) {
  return card.image ? `${API}${card.image}` : '/design/placeholder.png'
}

function onPointerDown(e) {
  if (flying.value) return
  dragging.value = true
  startX = e.clientX
  e.currentTarget.setPointerCapture(e.pointerId)
}

function onPointerMove(e) {
  if (!dragging.value) return
  dragX.value = e.clientX - startX
}

function onPointerUp() {
  if (!dragging.value) return
  dragging.value = false
  if (Math.abs(dragX.value) > 100) {
    swipe(dragX.value > 0 ? 'right' : 'left')
  } else {
    dragX.value = 0
  }
}

async function swipe(direction) {
  const card = topCard.value
  if (!card || flying.value) return
  flying.value = direction
  dragX.value = direction === 'right' ? 600 : -600

  if (direction === 'right') {
    savePlace(card.id)
  }

  setTimeout(() => {
    cards.value.shift()
    dragX.value = 0
    flying.value = ''
  }, 250)
}

async function savePlace(cardId) {
  const token = localStorage.getItem('token')
  if (!token) {
    notice.value = 'Войдите, чтобы сохранять места'
    return
  }
  const res = await fetch(`${API}/saved`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${token}`,
    },
    body: JSON.stringify({ card_id: cardId }),
  })
  if (res.status === 401) {
    notice.value = 'Сессия истекла, войдите снова'
  }
}

const cardStyle = computed(() => ({
  transform: `translateX(${dragX.value}px) rotate(${dragX.value / 20}deg)`,
  transition: dragging.value ? 'none' : 'transform 0.25s ease',
}))
</script>

<template>
  <div class="deck">
    <p v-if="loading" class="deck-msg">Загрузка…</p>
    <p v-else-if="error" class="deck-msg">{{ error }}</p>

    <div v-else-if="topCard" class="deck-inner">
            <div v-if="nextCard" class="card card-behind">
        <div class="band band-top"></div>
        <div class="lime">
          <div class="card-photo" :style="{ backgroundImage: `url(${photoUrl(nextCard)})` }"></div>
        </div>
        <div class="band band-bottom"></div>
      </div>

            <div
        class="card"
        :style="cardStyle"
        @pointerdown="onPointerDown"
        @pointermove="onPointerMove"
        @pointerup="onPointerUp"
        @pointercancel="onPointerUp"
      >
        <div class="band band-top"></div>

        <div class="lime">
          <div class="card-photo" :style="{ backgroundImage: `url(${photoUrl(topCard)})` }"></div>

          <div class="card-text">
            <div v-if="topCard.location" class="loc">
              <img src="/design/pin.svg" alt="" class="pin">
              <span>{{ topCard.location }}</span>
            </div>
            <h2 class="title">“{{ topCard.name }}”</h2>
            <p class="desc">{{ topCard.description }}</p>
          </div>
        </div>

        <div class="band band-bottom"></div>

        <div class="stamp stamp-like" :style="{ opacity: Math.max(0, Math.min(1, dragX / 80)) }">
          Хочу побывать
        </div>
        <div class="stamp stamp-nope" :style="{ opacity: Math.max(0, Math.min(1, -dragX / 80)) }">
          Нет
        </div>
      </div>

      <div class="deck-buttons">
        <button class="btn btn-nope" @click="swipe('left')">Нет</button>
        <button class="btn btn-like" @click="swipe('right')">Хочу побывать</button>
      </div>

      <p v-if="notice" class="notice">{{ notice }}</p>
    </div>

    <div v-else class="deck-msg">
      <p>Места закончились</p>
      <router-link to="/profile">Открыть профиль</router-link>
    </div>
  </div>
</template>

<style scoped>
.deck {
  height: calc(100dvh - 68px);
  display: flex;
  align-items: center;
  justify-content: center;
  background: #383938;
  font-family: 'Cousine', monospace;
}

.deck-msg {
  color: #cafb87;
  text-align: center;
}

.deck-msg a {
  color: #cafb87;
}

.deck-inner {
  position: relative;
  width: 100%;
  height: 100%;
  max-width: 430px;
  touch-action: none;
  user-select: none;
}

.card {
  position: absolute;
  inset: 0;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  background: #383938 url('/design/pixel-band.png') repeat-y top / 100% auto;
  cursor: grab;
}

.card-behind {
  transform: scale(0.97) translateY(6px);
}

.band {
  flex-shrink: 0;
}

.band-top {
  height: 12%;
}

.band-bottom {
  height: 11%;
  min-height: 72px;
}

.lime {
  flex: 1;
  display: flex;
  flex-direction: column;
  background: #cafb87;
  overflow: hidden;
}

.card-photo {
  height: 58%;
  flex-shrink: 0;
  margin: 4% 17px 0;
  border: 2px solid #383938;
  background: #9e9e9e center/cover no-repeat;
}

.card-text {
  padding: 14px 17px 0;
  color: #383938;
}

.loc {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 16px;
  line-height: 18px;
}

.pin {
  width: 10px;
  height: 12px;
}

.title {
  margin: 7px 0 10px;
  font-size: 24px;
  font-weight: 400;
  line-height: 27px;
}

.desc {
  margin: 0;
  font-size: 11px;
  line-height: 1.3;
}

.stamp {
  position: absolute;
  top: 24px;
  padding: 6px 12px;
  border: 3px solid #383938;
  background: rgba(202, 251, 135, 0.85);
  color: #383938;
  font-size: 18px;
  font-weight: 700;
  text-transform: uppercase;
  pointer-events: none;
}

.stamp-like {
  left: 16px;
  transform: rotate(-8deg);
}

.stamp-nope {
  right: 16px;
  transform: rotate(8deg);
}

.deck-buttons {
  position: absolute;
  left: 0;
  right: 0;
  bottom: 18px;
  display: flex;
  justify-content: center;
  gap: 14px;
  z-index: 5;
}

.btn {
  padding: 10px 20px;
  border: 2px solid #cafb87;
  border-radius: 0;
  background: #383938;
  color: #cafb87;
  font-family: 'Cousine', monospace;
  font-size: 14px;
  text-transform: uppercase;
  cursor: pointer;
}

.btn-like {
  background: #cafb87;
  border-color: #cafb87;
  color: #383938;
  font-weight: 700;
}

.notice {
  position: absolute;
  top: 12px;
  left: 0;
  right: 0;
  text-align: center;
  color: #cafb87;
  z-index: 6;
}
</style>
