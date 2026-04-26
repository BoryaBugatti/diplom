<template>
  <div class="dashboard">
    <header class="dashboard-header">
      <div class="logo-area">
        <i class="pi pi-file-contract"></i>
        <span>Тендерный портал</span>
      </div>
      <div class="user-area">
        <span class="user-name">{{ user_name }}</span>
        <Avatar icon="pi pi-user" class="user-avatar" @click="GoToUserLk" />
        <Button icon="pi pi-sign-out" severity="danger" text rounded @click="logout" />
      </div>
    </header>

    <div class="dashboard-content">
      <div class="main-column">
        <Card class="upload-card">
          <template #title>
            <i class="pi pi-cloud-upload"></i> Загрузить тендерную документацию
          </template>
          <template #subtitle>Поддерживаются форматы PDF, DOCX, XLSX, ZIP (до 50 МБ)</template>
          <template #content>
            <FileUpload
              name="tender-doc"
              :multiple="false"
              accept=".pdf,.docx,.xlsx,.zip"
              :maxFileSize="52428800"
              @select="onFileSelect"
              @clear="clearFile"
              :auto="false"
              chooseLabel="Выберите файл"
              cancelLabel="Отмена"
              mode="advanced"
              dragDrop
            >
              <template #header="{ files, chooseCallback, clearCallback }">
                <div class="flex justify-content-between align-items-center">
                  <div class="flex gap-2">
                    <Button @click="chooseCallback" icon="pi pi-file" label="Выбрать" severity="secondary" />
                    <Button @click="clearCallback" icon="pi pi-times" label="Очистить" severity="danger" outlined />
                  </div>
                </div>
              </template>
              <template #content="{ files, removeFileCallback }">
                <div v-if="files && files.length > 0" class="selected-file">
                  <div class="file-info">
                    <i class="pi pi-file-pdf"></i>
                    <span>{{ files[0].name }} ({{ formatFileSize(files[0].size) }})</span>
                    <Button icon="pi pi-times" severity="danger" text rounded @click="removeFileCallback" />
                  </div>
                  <ProgressBar v-if="uploadProgress > 0" :value="uploadProgress" class="upload-progress" />
                  <Button
                    v-if="uploadProgress === 0"
                    label="Загрузить и добавить в список"
                    icon="pi pi-upload"
                    severity="primary"
                    class="upload-btn"
                    @click="simulateUpload"
                  />
                </div>
                <div v-if="!files || files.length === 0" class="p-text-center p-m-3">
                  <i class="pi pi-cloud-upload" style="font-size: 2rem;"></i>
                  <p>Перетащите файл или нажмите "Выбрать"</p>
                </div>
              </template>
            </FileUpload>
          </template>
        </Card>

        <!-- Статистика (3 карточки) -->
        <div class="stats-grid">
          <Card class="stat-card">
            <template #content>
              <div class="stat-content">
                <i class="pi pi-folder-open stat-icon"></i>
                <div class="stat-info">
                  <h3>124</h3>
                  <p>Всего тендеров</p>
                </div>
              </div>
            </template>
          </Card>
          <Card class="stat-card">
            <template #content>
              <div class="stat-content">
                <i class="pi pi-chart-line stat-icon"></i>
                <div class="stat-info">
                  <h3>86</h3>
                  <p>Проанализировано</p>
                </div>
              </div>
            </template>
          </Card>
          <Card class="stat-card">
            <template #content>
              <div class="stat-content">
                <i class="pi pi-exclamation-triangle stat-icon"></i>
                <div class="stat-info">
                  <h3>12</h3>
                  <p>Высоких рисков</p>
                </div>
              </div>
            </template>
          </Card>
        </div>
      </div>

      <div class="side-column">
        <Card class="recent-card">
          <template #title>
            <i class="pi pi-history"></i> Недавние документы
          </template>
          <template #content>
            <div class="recent-list">
              <div v-for="doc in recentDocuments" :key="doc.id" class="recent-item">
                <i class="pi pi-file-alt doc-icon"></i>
                <div class="doc-info">
                  <div class="doc-name">{{ doc.name }}</div>
                  <div class="doc-meta">{{ doc.date }} • {{ doc.status }}</div>
                </div>
                <Button icon="pi pi-microscope" severity="info" text rounded @click="analyzeDocument(doc)" />
              </div>
              <div v-if="recentDocuments.length === 0" class="empty-message">
                <i class="pi pi-inbox"></i> Нет загруженных документов
              </div>
            </div>
          </template>
        </Card>

        <Card class="active-tenders">
          <template #title>
            <i class="pi pi-tasks"></i> Активные тендеры
          </template>
          <template #content>
            <div class="tender-list">
              <div class="tender-item">
                <div class="tender-title">Поставка медоборудования</div>
                <div class="tender-deadline">Дедлайн: 30.05.2026</div>
                <Badge value="На анализе" severity="warn" />
              </div>
              <div class="tender-item">
                <div class="tender-title">Строительство автодороги</div>
                <div class="tender-deadline">Дедлайн: 15.06.2026</div>
                <Badge value="Низкий риск" severity="success" />
              </div>
              <div class="tender-item">
                <div class="tender-title">ИТ-инфраструктура</div>
                <div class="tender-deadline">Дедлайн: 01.06.2026</div>
                <Badge value="Высокий риск" severity="danger" />
              </div>
            </div>
            <Button label="Все тендеры →" link class="more-btn" />
          </template>
        </Card>
      </div>
    </div>

    <Toast position="bottom-right" />
  </div>
</template>

<script setup>
import { ref, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { useToast } from 'primevue/usetoast'
import Card from 'primevue/card'
import Button from 'primevue/button'
import Avatar from 'primevue/avatar'
import Badge from 'primevue/badge'
import Toast from 'primevue/toast'
import ProgressBar from 'primevue/progressbar'
import FileUpload from 'primevue/fileupload'

const user_name = localStorage.getItem('user_name') || 'Пользователь'

const selectedFile = ref(null)
const uploadProgress = ref(0)
const recentDocuments = ref([])

const router = useRouter()
const toast = useToast()

function formatFileSize(bytes) {
  if (bytes === 0) return '0 Bytes'
  const k = 1024
  const sizes = ['Bytes', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i]
}

function onFileSelect(event) {
  const file = event.files[0]
  if (file) {
    if (file.size > 50 * 1024 * 1024) {
      toast.add({ severity: 'error', summary: 'Ошибка', detail: 'Файл превышает 50 МБ', life: 3000 })
      return
    }
    selectedFile.value = file
    uploadProgress.value = 0
  }
}

function clearFile() {
  selectedFile.value = null
  uploadProgress.value = 0
}

function simulateUpload() {
  if (!selectedFile.value) return

  let progress = 0
  const interval = setInterval(() => {
    progress += 10
    uploadProgress.value = progress
    if (progress >= 100) {
      clearInterval(interval)
      const newDoc = {
        id: Date.now(),
        name: selectedFile.value.name,
        date: new Date().toLocaleDateString('ru-RU'),
        status: 'Загружен',
        file: selectedFile.value
      }
      recentDocuments.value.unshift(newDoc)
      toast.add({ severity: 'success', summary: 'Успешно', detail: `Файл "${selectedFile.value.name}" загружен`, life: 3000 })
      clearFile()
    }
  }, 150)
}

function analyzeDocument(doc) {
  toast.add({ severity: 'info', summary: 'Анализ', detail: `Запущен анализ документа "${doc.name}" (демо-режим)`, life: 3000 })
}

function GoToUserLk() {
  router.push('/UserLK')
}

function logout() {
  toast.add({ severity: 'info', summary: 'Выход', detail: 'Вы вышли из системы (демо-режим)', life: 3000 })
  setTimeout(() => {
    alert('В реальном приложении здесь будет переход на страницу авторизации')
  }, 500)
}

onUnmounted(() => {
})
</script>

<style scoped>
/* Светлый фон */
.dashboard {
  min-height: 100vh;
  background: #f8fafc;
  font-family: 'Inter', sans-serif;
}

.dashboard-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 2rem;
  background: white;
  border-bottom: 1px solid #e2e8f0;
  box-shadow: 0 1px 3px rgba(0,0,0,0.05);
}
.logo-area {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 1.4rem;
  font-weight: 700;
  color: #1e293b;
}
.logo-area i {
  font-size: 1.6rem;
  color: #3b9bd5;
}
.user-area {
  display: flex;
  align-items: center;
  gap: 1rem;
}
.user-name {
  color: #334155;
  font-weight: 500;
}
.user-avatar {
  cursor: pointer;
  background: linear-gradient(135deg, #64748b, #475569);
}

.dashboard-content {
  max-width: 1400px;
  margin: 2rem auto;
  padding: 0 2rem;
  display: grid;
  grid-template-columns: 1fr 360px;
  gap: 1.8rem;
  align-items: start;
}
@media (max-width: 900px) {
  .dashboard-content {
    grid-template-columns: 1fr;
  }
}

.main-column {
  display: flex;
  flex-direction: column;
  gap: 1.8rem;
}

.side-column {
  display: flex;
  flex-direction: column;
  gap: 1.8rem;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1rem;
}
.stat-card :deep(.p-card-content) {
  padding: 0.75rem;
}
.stat-content {
  display: flex;
  align-items: center;
  gap: 0.8rem;
}
.stat-icon {
  font-size: 2rem;
  color: #3b9bd5;
}
.stat-info h3 {
  font-size: 1.6rem;
  margin: 0;
  line-height: 1;
}
.stat-info p {
  font-size: 0.7rem;
  color: #5b6e8c;
  margin: 0;
}

.recent-list {
  margin-top: 0.5rem;
}
.recent-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 0.7rem 0;
  border-bottom: 1px solid #eef2f6;
}
.doc-icon {
  font-size: 1.3rem;
  color: #3b9bd5;
}
.doc-info {
  flex: 1;
}
.doc-name {
  font-weight: 600;
  font-size: 0.9rem;
}
.doc-meta {
  font-size: 0.7rem;
  color: #6c86a3;
}
.empty-message {
  text-align: center;
  padding: 1.5rem;
  color: #8ba0b5;
}

.tender-list {
  margin-top: 0.5rem;
}
.tender-item {
  padding: 0.8rem 0;
  border-bottom: 1px solid #eef2f6;
  display: flex;
  flex-wrap: wrap;
  justify-content: space-between;
  align-items: center;
}
.tender-title {
  font-weight: 600;
  flex: 1;
}
.tender-deadline {
  font-size: 0.7rem;
  color: #6c86a3;
  margin-left: 1rem;
}
.more-btn {
  margin-top: 1rem;
  width: 100%;
  text-align: center;
}

.selected-file {
  margin-top: 1rem;
  padding: 0.8rem;
  background: #f0f6fa;
  border-radius: 20px;
}
.file-info {
  display: flex;
  align-items: center;
  gap: 8px;
  justify-content: space-between;
}
.upload-progress {
  margin: 0.8rem 0;
}
.upload-btn {
  margin-top: 0.5rem;
  width: 100%;
}
</style>