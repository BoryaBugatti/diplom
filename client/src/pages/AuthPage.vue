<template>
  <div class="auth-page">
    <div class="bg-blur blur-1"></div>
    <div class="bg-blur blur-2"></div>
    <div class="bg-pattern"></div>

    <div class="auth-container">
      <div class="auth-card">
        <div class="card-header">
          <div class="logo-badge">
            <img :src=auth_icon class="logo">
          </div>
          <h1>Модуль интеллектуального анализа тендерной документации</h1>
        </div>

        <div class="form-tabs">
          <button
            :class="['tab-btn', { active: activeForm === 'login' }]"
            @click="activeForm = 'login'"
          >
            <i class="fas fa-sign-in-alt"></i> Вход
          </button>
          <button
            :class="['tab-btn', { active: activeForm === 'register' }]"
            @click="activeForm = 'register'"
          >
            <i class="fas fa-user-plus"></i> Регистрация
          </button>
        </div>

        <div class="form-wrapper">
          <LoginForm
            v-if="activeForm === 'login'"
            @success="handleLoginSuccess"
          />
          <RegisterForm
            v-else
            @success="handleRegisterSuccess"
          />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import LoginForm from '@/components/LoginForm.vue'
import RegisterForm from '@/components/RegisterForm.vue'
import auth_icon from "@/pictures/free-icon-document-7519050.png"
const activeForm = ref('login')

const handleLoginSuccess = (credentials) => {
  console.log('Успешный вход:', credentials)
  alert(`Добро пожаловать, ${credentials.email || credentials.login}! (демо-вход)`)
}

const handleRegisterSuccess = (userData) => {
  console.log('Успешная регистрация:', userData)
  alert(`Регистрация выполнена! Добро пожаловать, ${userData.fullName}. Теперь войдите.`)
  activeForm.value = 'login'
}
</script>

<style scoped>
.auth-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 1.5rem;
  position: relative;
  background: radial-gradient(ellipse at 20% 30%, #0B2A3B 0%, #03161F 100%);
  font-family: 'Inter', sans-serif;
  overflow: hidden;
}

.bg-blur {
  position: absolute;
  width: 50vw;
  height: 50vw;
  border-radius: 50%;
  filter: blur(80px);
  opacity: 0.5;
  z-index: 0;
  pointer-events: none;
}
.blur-1 {
  top: -20vh;
  left: -15vw;
  background: radial-gradient(circle, rgba(56, 189, 248, 0.3), rgba(14, 116, 144, 0));
}
.blur-2 {
  bottom: -30vh;
  right: -20vw;
  background: radial-gradient(circle, rgba(99, 102, 241, 0.35), rgba(79, 70, 229, 0));
}
.bg-pattern {
  position: absolute;
  inset: 0;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 200 200'%3E%3Cpath fill='none' stroke='rgba(255,255,255,0.03)' stroke-width='1' d='M0 0 L200 200 M200 0 L0 200'/%3E%3C/svg%3E");
  background-size: 30px 30px;
  pointer-events: none;
}

.auth-container {
  width: 100%;
  max-width: 520px;
  position: relative;
  z-index: 10;
  animation: fadeSlideUp 0.5s ease-out;
}

@keyframes fadeSlideUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.auth-card {
  background: rgba(255, 255, 255, 0.98);
  border-radius: 40px;
  box-shadow: 0 25px 45px -12px rgba(0, 0, 0, 0.4), 0 0 0 1px rgba(255, 255, 255, 0.2);
  overflow: hidden;
  transition: all 0.2s;
}

.card-header {
  padding: 2rem 2rem 0.5rem 2rem;
  text-align: center;
  border-bottom: 1px solid #eef2f6;
}

.logo-badge {
  display: flex;
  justify-content: center;
  align-items: center;
}

.logo{
  width: 20%;
  height: 20%;
}

.card-header h1 {
  font-size: 1.8rem;
  font-weight: 700;
  background: linear-gradient(120deg, #1F5E7E, #0D3B4F);
  background-clip: text;
  -webkit-background-clip: text;
  color: transparent;
  letter-spacing: -0.5px;
}
.card-header p {
  color: #5b6e8c;
  font-size: 0.85rem;
  margin-top: 6px;
  font-weight: 500;
}

.form-tabs {
  display: flex;
  padding: 1.5rem 2rem 0 2rem;
  gap: 1rem;
  background: white;
}
.tab-btn {
  flex: 1;
  background: none;
  border: none;
  font-size: 1rem;
  font-weight: 600;
  padding: 0.75rem 0;
  cursor: pointer;
  color: #8A99B4;
  transition: all 0.2s;
  border-radius: 40px;
  font-family: inherit;
}
.tab-btn i {
  margin-right: 8px;
}
.tab-btn.active {
  background: #EFF6FC;
  color: #1A6A8A;
  box-shadow: inset 0 0 0 1px rgba(26, 106, 138, 0.1);
}

.form-wrapper {
  padding: 1.8rem 2rem 2rem 2rem;
}

.demo-note {
  text-align: center;
  margin-top: 1.2rem;
  font-size: 0.75rem;
  color: rgba(255, 255, 255, 0.65);
  background: rgba(0, 0, 0, 0.25);
  backdrop-filter: blur(4px);
  padding: 0.6rem 1rem;
  border-radius: 60px;
  width: fit-content;
  margin-left: auto;
  margin-right: auto;
}
</style>