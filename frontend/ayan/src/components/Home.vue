<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const glowing = ref(false)

function startJourney() {
  if (glowing.value) return
  glowing.value = true
  
  setTimeout(() => router.push('/map'), 400)
}
</script>

<template>
  <div class="home">
    <img src="/design/map-bg.png" alt="" class="map-bg">

    <div class="container">
      <h1 class="blur-text">Добро пожаловать<br>в Мегино-Кангаласский район!</h1>
    </div>

    <button class="start-btn" :class="{ glowing }" @click="startJourney">
      начать путешествие!
    </button>
  </div>
</template>

<style scoped>
.home {
  position: relative;
  min-height: 160vh;
  overflow: hidden;
}

.map-bg {
  position: absolute;
  top: 237px;
  left: 0;
  width: 122%;
  pointer-events: none;
}

.container {
  position: sticky;
  top: 65px;
  text-align: left;
  padding: 0 37px;
}

.blur-text {
  margin: 0;
  max-width: 305px;
  font-family: 'Cousine', monospace;
  font-size: 40px;
  font-weight: 400;
  line-height: 45px;
  color: #cafb87;

  animation: blurOnScroll linear forwards;
  animation-timeline: scroll();

  animation-range: 0px 300px;
}

@keyframes blurOnScroll {
  from {
    filter: blur(0px);
    opacity: 1;
  }
  to {
    filter: blur(15px);
    opacity: 0.2;
  }
}

.start-btn {
  position: absolute;
  left: 50%;
  top: calc(100dvh - 208px);
  transform: translateX(-50%);
  width: 240px;
  height: 60px;
  border: none;
  border-radius: 0;
  background: #565857;
  color: #cafb87;
  font-family: 'Cousine', monospace;
  font-size: 16px;
  white-space: nowrap;
  cursor: pointer;
  transition: box-shadow 0.3s ease, background-color 0.3s ease, color 0.3s ease;
}

.start-btn:active,
.start-btn.glowing {
  background: #cafb87;
  color: #383938;
  box-shadow: 0 0 18px #cafb87, 0 0 42px rgba(202, 251, 135, 0.7);
}
</style>
