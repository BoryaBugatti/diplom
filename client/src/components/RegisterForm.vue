<template>
  <form @submit.prevent="handleRegister">
    <div class="input-group">
      <label>Полное имя</label>
      <div class="input-icon">
        <i class="fas fa-user"></i>
        <input
          type="text"
          v-model="name"
          placeholder="Иванов Иван Иванович"
        />
      </div>
    </div>

    <div class="input-group">
      <label>Email</label>
      <div class="input-icon">
        <i class="fas fa-at"></i>
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
        <i class="fas fa-key"></i>
        <input
          type="password"
          v-model="password"
          placeholder="минимум 6 символов"
        />
      </div>
    </div>

    <div class="input-group">
      <label>Подтверждение пароля</label>
      <div class="input-icon">
        <i class="fas fa-check-circle"></i>
        <input
          type="password"
          v-model="confirm_password"
          placeholder="повторите пароль"
        />
      </div>
    </div>

    <div class="checkbox-row">
      <label class="checkbox-label">
        <input type="checkbox" v-model="agreeTerms" />
        <span>Я соглашаюсь с <a href="#" class="terms-link" @click.prevent="showTerms">условиями обработки данных</a></span>
      </label>
    </div>

    <button type="submit" class="submit-btn">
      <i class="fas fa-user-check"></i> Зарегистрироваться
    </button>
  </form>
</template>

<script setup>
import { reactive, ref, computed } from 'vue'
import axios from 'axios';
import { useRouter } from 'vue-router';
const name = ref();
const email = ref();
const password = ref();
const confirm_password = ref();

const router = useRouter();

//const emailRegex = /^[^\s@]+@([^\s@]+\.)+[^\s@]+$/;
//const isEmailValid = computed(() => emailRegex.test(email.value));

const handleRegister = async () => {
  if (password.value == confirm_password.value){
    const response = await axios.post("http://127.0.0.1:8000/reg", {
      user_name: name.value,
      user_email: email.value,
      user_password: password.value,
    });
    if (response.data.status == "OK"){
      alert("Учетная запись успешно создана!!!");
      router.push('/');
    }
  }
  else
    alert("Пароли не совпадают");
  name.value = "";
  email.value = "";
  password.value = "";
  confirm_password.value = "";
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
  margin: 1rem 0 1.5rem;
}
.checkbox-label {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #2c4b62;
  cursor: pointer;
  font-size: 0.85rem;
}
.terms-link {
  color: #1A6A8A;
  text-decoration: none;
  font-weight: 500;
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
  cursor: pointer;
  transition: 0.2s;
  box-shadow: 0 6px 14px rgba(22, 108, 140, 0.3);
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}
.submit-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
}
.submit-btn:hover:not(:disabled) {
  background: linear-gradient(95deg, #1C7FA3, #126280);
  transform: scale(1.01);
}
</style>