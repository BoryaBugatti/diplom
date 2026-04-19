import { createRouter, createWebHistory } from 'vue-router'
import App from "@/App.vue";
import AuthPage from "@/pages/AuthPage.vue";
import MainPage from '@/pages/MainPage.vue';
import UserLK from '@/pages/UserLK.vue';
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
      meta: { requiresAuth: true }
    },
    {
      path: '/UserLK',
      component: UserLK,
    }
  ],
})

router.beforeEach((to, from, next) => {
  const isAuthenticated = !!localStorage.getItem("user_email");
  if (to.meta.requiresAuth && !isAuthenticated)
    next('/');
  else if (to.path === '/login' && isAuthenticated)
    next('/MainPage');
  else
    next();
})

export default router
