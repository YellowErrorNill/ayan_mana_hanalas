import { createApp } from 'vue';
import { createYmaps } from 'vue-yandex-maps';
import router from './router'
import App from './App.vue';


const app = createApp(App);


app.use(createYmaps({
  apikey: 'fd5498a7-5f45-4c46-a7b2-4d6d18f39519',
}));
app.use(router)


app.mount('#app');

