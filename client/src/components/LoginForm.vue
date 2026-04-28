<template>
  <div class="flex align-items-center justify-content-center min-h-screen bg-gradient">
    <div class="w-full max-w-md p-8">
      <Card>
        <template #title>
          <div class="flex flex-column align-items-center gap-2">
            <i class="pi pi-lock text-4xl text-primary"></i>
            <h2 class="text-2xl font-bold m-0">Вход в систему</h2>
            <p class="text-color-secondary m-0">Добро пожаловать</p>
          </div>
        </template>

        <template #content>
          <Form class="flex flex-column gap-4">
            <FormField v-slot="$field" name="login" initial-value="">
              <label for="login" class="font-semibold block mb-1">Email</label>
              <InputText
                id="login"
                v-model="email"
                type="text"
                placeholder="ivan@example.com"
                fluid
                :class="{ 'p-invalid': $field?.invalid }"
              />
              <Message
                v-if="$field?.invalid"
                severity="error"
                size="small"
                variant="simple"
              >
                {{ $field.error?.message }}
              </Message>
            </FormField>

            <FormField v-slot="$field" name="password" initial-value="">
              <label for="password" class="font-semibold block mb-1">Пароль</label>
              <Password
                id="password"
                v-model="password"
                placeholder="••••••••"
                :feedback="false"
                toggle-mask
                fluid
                :class="{ 'p-invalid': $field?.invalid }"
              />
              <Message
                v-if="$field?.invalid"
                severity="error"
                size="small"
                variant="simple"
              >
                {{ $field.error?.message }}
              </Message>
            </FormField>

            <div class="flex justify-content-between align-items-center">
              <div class="flex align-items-center gap-2">
                <Checkbox inputId="remember" v-model="remember" binary />
                <label for="remember" class="text-sm">Запомнить меня</label>
              </div>
              <a href="#" class="text-sm text-primary hover:underline">Забыли пароль?</a>
            </div>

            <Button type="submit" label="Войти" icon="pi pi-sign-in" class="w-full" size="large" @click="LogIn"/>

            <Divider align="center" type="dashed">
              <span class="text-color-secondary text-sm">или</span>
            </Divider>

            <div class="text-center">
              <span class="text-color-secondary">Нет аккаунта? </span>
              <RouterLink to="/Register" class="font-semibold text-primary hover:underline">Зарегистрироваться</RouterLink>
            </div>
          </Form>
        </template>
      </Card>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'
import Card from 'primevue/card'
import Form from '@primevue/forms/form'
import FormField from '@primevue/forms/formfield'
import InputText from 'primevue/inputtext'
import Password from 'primevue/password'
import Button from 'primevue/button'
import Checkbox from 'primevue/checkbox'
import Divider from 'primevue/divider'
import Message from 'primevue/message'


const router = useRouter();
const remember = ref(false);
const password = ref();



const email = ref();

async function LogIn() {
  try {
    const response = await axios.post('http://localhost:8000/auth/login', {
      user_email: email.value,
      user_password: password.value
    });
    const token = response.data.access_token;
    localStorage.setItem('access_token', token);
    localStorage.setItem('user_name', response.data.user_name);
    localStorage.setItem('user_role', response.data.user_role);
    localStorage.setItem('user_email', response.data.user_email);
    router.push('/MainPage');
  } catch (error) {
    alert(error);
  }
}
</script>

<style scoped>
.bg-gradient {
  background: linear-gradient(135deg, #1e1e2f 0%, #2a2a3b 100%);
}
</style>