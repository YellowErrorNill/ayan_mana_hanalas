import { createRouter, createWebHistory } from 'vue-router'
import App from '../App.vue'
import MapStreeet from '../components/mapstreet.vue'

import Cart from '../components/cart.vue'


const routes = [
  { path: '/', name: 'home', component: App },
  { path: '/map', name: 'map', component: MapStreeet },
   {path: '/cart', name: 'cart', component: Cart }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
