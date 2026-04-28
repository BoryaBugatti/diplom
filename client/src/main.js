import './assets/main.css'

import { createApp } from 'vue'
import axios from 'axios'
import App from './App.vue'
import router from './router'
import PrimeVue from 'primevue/config'; 
import Aura from '@primevue/themes/aura';    
import 'primeicons/primeicons.css';
import 'primeflex/primeflex.css';
import ToastService from 'primevue/toastservice'

const app = createApp(App)

app.use(PrimeVue, {
    theme: {
        preset: Aura,
        options: {
            darkModeSelector: '.my-app-dark' 
        }
    }
});


axios.interceptors.request.use(config => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

app.use(router)
app.use(ToastService);
app.mount('#app')
