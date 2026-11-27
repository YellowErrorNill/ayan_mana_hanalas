<script setup>
import { ref } from 'vue'

const menuOpen = ref(false)

function closeMenu() {
  menuOpen.value = false
}
</script>
<template>
  <header class="topbar">
    <button
      class="burger"
      :class="{ open: menuOpen }"
      aria-label="Меню"
      @click="menuOpen = !menuOpen"
    >
      <span></span>
      <span></span>
      <span></span>
    </button>
  </header>

  <div v-if="menuOpen" class="menu-overlay" @click="closeMenu"></div>

  <nav class="menu" :class="{ open: menuOpen }">
    <router-link to="/" @click="closeMenu">Главная</router-link>
    <router-link to="/map" @click="closeMenu">Карта</router-link>
    <router-link to="/auth" @click="closeMenu">Вход</router-link>
    <router-link to="/cart" @click="closeMenu">Карточки</router-link>
    <router-link to="/profile" @click="closeMenu">Профиль</router-link>
  </nav>

  <router-view />
</template>

<style>
:root {
  color-scheme: dark;
}

body {
  margin: 0;
  font-family: sans-serif;
  background: #383938;
  color: #eee;
}
</style>

<style scoped>
.topbar {
  position: sticky;
  top: 0;
  z-index: 30;
  display: flex;
  justify-content: flex-end;
  padding: 14px 16px;
  background: transparent;
}

.burger {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  justify-content: center;
  gap: 4px;
  width: 40px;
  height: 40px;
  padding: 8px;
  border: none;
  background: none;
  cursor: pointer;
}

.burger span {
  display: block;
  width: 20px;
  height: 2px;
  background: #cafb87;
  transition: transform 0.2s, opacity 0.2s, width 0.2s;
}

.burger span:nth-child(3) {
  width: 10px;
}

.burger.open span:nth-child(1) {
  transform: translateY(6px) rotate(45deg);
}

.burger.open span:nth-child(2) {
  opacity: 0;
}

.burger.open span:nth-child(3) {
  width: 20px;
  transform: translateY(-6px) rotate(-45deg);
}

.menu-overlay {
  position: fixed;
  inset: 0;
  z-index: 20;
  background: rgba(0, 0, 0, 0.4);
}

.menu {
  position: fixed;
  top: 0;
  left: 0;
  bottom: 0;
  z-index: 25;
  display: flex;
  flex-direction: column;
  gap: 4px;
  width: 240px;
  padding: 70px 20px 20px;
  background: #2c2d2c;
  box-shadow: 2px 0 12px rgba(0, 0, 0, 0.5);
  transform: translateX(-100%);
  transition: transform 0.25s ease;
}

.menu.open {
  transform: translateX(0);
}

.menu a {
  padding: 12px 8px;
  color: #eee;
  text-decoration: none;
  font-size: 17px;
  border-bottom: 1px solid #454645;
}

.menu a.router-link-active {
  color: #cafb87;
  font-weight: 700;
}
</style>
