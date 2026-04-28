<template>
  <div class="flex align-items-center justify-content-center min-h-screen bg-gradient">
    <div class="w-full max-w-md p-8">
      <Card>
        <template #title>
          <div class="flex flex-column align-items-center gap-2">
            <i class="pi pi-lock text-4xl text-primary"></i>
            <h2 class="text-2xl font-bold m-0">Регистрация</h2>
            <p class="text-color-secondary m-0">Добро пожаловать</p>
          </div>
        </template>

        <template #content>
          <Form class="flex flex-column gap-4">

            <FormField v-slot="$field" name="FullName" initial-value="">
              <label for="login" class="font-semibold block mb-1">ФИО</label>
              <InputText
                id="FullName"
                type="text"
                v-model="UserName"
                placeholder="Ляпин Борис Сергеевич"
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

            <FormField v-slot="$field" name="email" initial-value="">
              <label for="login" class="font-semibold block mb-1">Email</label>
              <InputText
                id="email"
                type="email"
                v-model="UserEmail"
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
                v-model="UserPassword"
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
              <a href="#" class="text-sm text-primary hover:underline">Забыли пароль?</a>
            </div>

            <Button type="submit" label="Зарегистрироваться" icon="pi pi-sign-in" class="w-full" size="large" @click="Reg"/>

            <Divider align="center" type="dashed">
              <span class="text-color-secondary text-sm">или</span>
            </Divider>

            <div class="text-center">
              <span class="text-color-secondary">Есть аккаунт? </span>
              <RouterLink to="/" class="font-semibold text-primary hover:underline">Войти</RouterLink>
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
import Card from 'primevue/card'
import Form from '@primevue/forms/form'
import FormField from '@primevue/forms/formfield'
import InputText from 'primevue/inputtext'
import Password from 'primevue/password'
import Button from 'primevue/button'
import Divider from 'primevue/divider'
import Message from 'primevue/message'
import axios from 'axios'

const router = useRouter();

const UserName = ref('');
const UserEmail = ref('');
const UserPassword = ref('');

const Reg = async () => {
  const response = await axios.post("http://127.0.0.1:8000/reg", {
    user_email: UserEmail.value,
    user_name: UserName.value,
    user_password: UserPassword.value
  });
  if (response.data.status == "OK"){
    UserName = '';
    UserEmail = '';
    UserPassword = '';
    alert('Вы успешно зарегистрировались, теперь вы будете перенаправлены на странциу авторизации');
    router.push('/');
  }
  alert(reponse.data.status);
}

</script>

<style scoped>
.bg-gradient {
  background: linear-gradient(135deg, #1e1e2f 0%, #2a2a3b 100%);
}
</style>