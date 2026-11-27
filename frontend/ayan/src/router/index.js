import { createRouter, createWebHistory } from 'vue-router'
import Home from '../components/Home.vue'
import MapStreeet from '../components/mapstreet.vue'

import Cart from '../components/cart.vue'
import Auth from '../components/Auth.vue'
import Profile from '../components/Profile.vue'


const routes = [
  { path: '/', name: 'home', component: Home },
  { path: '/map', name: 'map', component: MapStreeet },
   {path: '/cart', name: 'cart', component: Cart },
   {path: '/auth', name: 'auth', component: Auth },
   {path: '/profile', name: 'profile', component: Profile }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
