import { createRouter, createWebHistory } from 'vue-router'
import App from "@/App.vue";
import AuthPage from "@/pages/AuthPage.vue";
import MainPage from '@/pages/MainPage.vue';
import UserLK from '@/pages/UserLK.vue';
import Reg from "@/components/RegisterForm.vue"
const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      component: AuthPage,
    },
    {
      path: '/MainPage',
      component: MainPage,
    },
    {
      path: '/UserLK',
      component: UserLK,
    },
    {
      path: '/Register',
      component: Reg,
    }
  ],
})


export default router
