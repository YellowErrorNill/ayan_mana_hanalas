<script setup>
import MapStreet from './components/mapstreet.vue'
</script>
<template>
  <h1>hello</h1>
  

  <div>
    <nav>
      <router-link to="/">Главная</router-link> |
      <router-link to="/map">Карта</router-link> |
      <router-link to="/cart">Карточки</router-link>
    </nav>

    <router-view />
  </div>
<p class="blur-on-scroll">Этот текст плавно размывается при скролле страницы.</p>
  
</template>

<style scoped>

.blur-on-scroll {

  animation: blur-effect linear both;
  animation-timeline: view();
  
 
  animation-range: exit 0% exit 100%;
}

@keyframes blur-effect {
  from {
    filter: blur(0px);
    opacity: 1;
  }
  to {
    filter: blur(12px);
    opacity: 0.2;
  }
}




</style>
