<template>
  <form @submit.prevent="handleLogin">
    <div class="input-group">
      <label>Email или логин</label>
      <div class="input-icon">
        <i class="fas fa-envelope"></i>
        <input
          type="email"
          v-model="email"
          placeholder="ivanov@tender.ru"
        />
      </div>
    </div>

    <div class="input-group">
      <label>Пароль</label>
      <div class="input-icon">
        <i class="fas fa-lock"></i>
        <input
          type="password"
          v-model="password"
          placeholder="••••••••"
        />
      </div>
    </div>

    <div class="checkbox-row">
      <a href="#" class="forgot-link" @click.prevent="">Забыли пароль?</a>
    </div>

    <button type="submit" class="submit-btn">
      <i class="fas fa-arrow-right-to-bracket"></i> Войти
    </button>
  </form>
</template>

<script setup>
import axios from 'axios';
import { reactive, ref } from 'vue';
import { useRouter } from 'vue-router';
import Cookies from 'js-cookie';

const email = ref();
const password = ref();
const rememberMe = ref();

const router = useRouter();

const handleLogin = async () => {
  const response = await axios.post("http://127.0.0.1:8000/auth", {
    user_email: email.value,
    user_password: password.value,
  }, {withCredentials: true});
  if (response.data.status == "OK"){
    localStorage.setItem("user_email", response.data.user_email);
    localStorage.setItem("user_name", response.data.user_name);
    localStorage.setItem("user_role", response.data.user_role);
    alert(response.data.message);
    router.push('/MainPage');
  }
  else{
    alert(response.data.message);
    email.value = "";
    password.value = "";
  }
}

</script>

<style scoped>
.input-group {
  margin-bottom: 1.3rem;
}
.input-group label {
  display: block;
  font-size: 0.8rem;
  font-weight: 600;
  margin-bottom: 0.4rem;
  color: #1f3a4b;
}
.input-icon {
  position: relative;
}
.input-icon i {
  position: absolute;
  left: 16px;
  top: 50%;
  transform: translateY(-50%);
  color: #8ca0bb;
  font-size: 1rem;
  pointer-events: none;
}
.input-icon input {
  width: 100%;
  padding: 0.85rem 1rem 0.85rem 2.8rem;
  border: 1px solid #e2e8f0;
  border-radius: 30px;
  font-size: 0.95rem;
  font-family: inherit;
  transition: 0.2s;
  background: white;
  outline: none;
  color: #0a2a38;
}
.input-icon input:focus {
  border-color: #2c9cd4;
  box-shadow: 0 0 0 3px rgba(44, 156, 212, 0.15);
}
.input-icon {
  border-color: #e53e3e;
  background-color: #fff8f8;
}

.checkbox-row {
  display: flex;
  justify-content: center;
  align-items: center;
  margin: 1rem 0 1.5rem;
  font-size: 0.85rem;
}
.checkbox-label {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #2c4b62;
  cursor: pointer;
}
.checkbox-label input {
  width: 16px;
  height: 16px;
  cursor: pointer;
  accent-color: #1A6A8A;
}
.forgot-link {
  color: #1A6A8A;
  text-decoration: none;
  font-weight: 500;
  font-size: 0.8rem;
}
.forgot-link:hover {
  text-decoration: underline;
}
.submit-btn {
  width: 100%;
  background: linear-gradient(95deg, #166C8C, #0F4B63);
  border: none;
  padding: 0.85rem;
  border-radius: 40px;
  font-weight: 700;
  font-size: 1rem;
  color: white;
  font-family: inherit;
  cursor: pointer;
  transition: all 0.2s;
  box-shadow: 0 6px 14px rgba(22, 108, 140, 0.3);
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}
.submit-btn:hover {
  background: linear-gradient(95deg, #1C7FA3, #126280);
  transform: scale(1.01);
}
</style>