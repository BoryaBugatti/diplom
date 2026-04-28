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
        <!-- Карточка загрузки -->
        <Card class="upload-card">
          <template #title>
            <i class="pi pi-cloud-upload"></i> Загрузить тендерную документацию
          </template>
          <template #subtitle>Поддерживаются форматы PDF, DOCX, XLSX, TXT (до 10 МБ)</template>
          <template #content>
            <FileUpload
              name="tender-doc"
              :multiple="false"
              accept=".pdf,.docx,.xlsx,.txt"
              :maxFileSize="10485760"
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
                    <Button icon="pi pi-times" severity="danger" text rounded @click="removeFileCallbackAndClear" />
                  </div>
                  <ProgressBar v-if="uploadProgress > 0" :value="uploadProgress" class="upload-progress" />
                  <Button
                    v-if="uploadProgress === 0"
                    label="Загрузить и проанализировать"
                    icon="pi pi-upload"
                    severity="primary"
                    class="upload-btn"
                    :disabled="!selectedFile"
                    @click="uploadAndAnalyze"
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

        <!-- Результаты анализа -->
        <Card v-if="analysisResult" class="analysis-card">
          <template #title>
            <i class="pi pi-chart-line"></i> Результаты анализа
          </template>
          <template #content>
            <div class="analysis-content">
              <div class="analysis-section">
                <h4><i class="pi pi-info-circle"></i> Название тендера</h4>
                <p>{{ analysisResult.tender_summary.name || 'Не указано' }}</p>
              </div>
              <div class="analysis-section">
                <h4><i class="pi pi-align-left"></i> Краткое описание</h4>
                <p>{{ analysisResult.tender_summary.description || 'Нет описания' }}</p>
              </div>
              <div class="analysis-section">
                <h4><i class="pi pi-list"></i> Все требования</h4>
                <ul class="requirements-list">
                  <li v-for="(req, idx) in analysisResult.all_requirements" :key="idx">{{ req }}</li>
                  <li v-if="analysisResult.all_requirements.length === 0">Не найдены</li>
                </ul>
              </div>
              <div class="analysis-section">
                <h4><i class="pi pi-star-fill"></i> Ключевые требования</h4>
                <ul class="requirements-list key">
                  <li v-for="(req, idx) in analysisResult.key_requirements" :key="idx">{{ req }}</li>
                  <li v-if="analysisResult.key_requirements.length === 0">Не выделены</li>
                </ul>
              </div>
            </div>
            <Button label="Очистить результаты" icon="pi pi-trash" severity="secondary" outlined class="clear-btn" @click="clearAnalysis" />
          </template>
        </Card>

        <!-- Статистика (3 карточки) -->
        <div class="stats-grid">
          <Card class="stat-card">
            <template #content>
              <div class="stat-content">
                <i class="pi pi-folder-open stat-icon"></i>
                <div class="stat-info">
                  <h3>{{ recentDocuments.length }}</h3>
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
                  <h3>{{ analyzedCount }}</h3>
                  <p>Проанализировано</p>
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
                <Button icon="pi pi-microscope" severity="info" text rounded @click="viewAnalysis(doc)" />
              </div>
              <div v-if="recentDocuments.length === 0" class="empty-message">
                <i class="pi pi-inbox"></i> Нет загруженных документов
              </div>
            </div>
          </template>
        </Card>
      </div>
    </div>

    <Toast position="bottom-right" />
  </div>
</template>

<script setup>
import { ref, computed, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { useToast } from 'primevue/usetoast'
import axios from 'axios'

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
const analysisResult = ref(null)

const router = useRouter()
const toast = useToast()

const analyzedCount = computed(() => recentDocuments.value.filter(doc => doc.status === 'Проанализирован').length)
const highRiskCount = computed(() => recentDocuments.value.filter(doc => doc.risk === 'high').length)

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
    if (file.size > 10 * 1024 * 1024) {
      toast.add({ severity: 'error', summary: 'Ошибка', detail: 'Файл превышает 10 МБ', life: 3000 })
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

function removeFileCallbackAndClear() {
  selectedFile.value = null
  uploadProgress.value = 0
}

function clearAnalysis() {
  analysisResult.value = null
}

async function uploadAndAnalyze() {
  if (!selectedFile.value) {
    toast.add({ severity: 'warn', summary: 'Нет файла', detail: 'Выберите файл для анализа', life: 3000 })
    return
  }

  const formData = new FormData()
  formData.append('file', selectedFile.value)

  uploadProgress.value = 0
  const interval = setInterval(() => {
    if (uploadProgress.value < 90) {
      uploadProgress.value += 10
    }
  }, 100)

  try {
    const response = await axios.post('http://localhost:8000/TenderAnalysis', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
      timeout: 300000,
      withCredentials: true
    })
    clearInterval(interval)
    uploadProgress.value = 100

    const resultData = response.data
    analysisResult.value = resultData

    const newDoc = {
      id: Date.now(),
      name: selectedFile.value.name,
      date: new Date().toLocaleDateString('ru-RU'),
      status: 'Проанализирован',
      risk: resultData.key_requirements?.length > 5 ? 'high' : 'low',
      analysis: resultData
    }
    recentDocuments.value.unshift(newDoc)

    toast.add({ severity: 'success', summary: 'Анализ завершён', detail: `Файл "${selectedFile.value.name}" успешно проанализирован`, life: 5000 })

    clearFile()
  } catch (error) {
    clearInterval(interval)
    uploadProgress.value = 0
    console.error('Ошибка анализа:', error)
    let errorMsg = 'Ошибка при анализе документа'
    if (error.response?.data?.detail) {
      errorMsg = error.response.data.detail
    } else if (error.message) {
      errorMsg = error.message
    }
    toast.add({ severity: 'error', summary: 'Ошибка', detail: errorMsg, life: 7000 })
  }
}

function viewAnalysis(doc) {
  if (doc.analysis) {
    analysisResult.value = doc.analysis
    toast.add({ severity: 'info', summary: 'Загружен результат', detail: `Показан анализ документа "${doc.name}"`, life: 3000 })
  } else {
    toast.add({ severity: 'warn', summary: 'Нет данных', detail: 'Для этого документа анализ ещё не проводился', life: 3000 })
  }
}

function GoToUserLk() {
  router.push('/UserLK')
}

function logout() {
  toast.add({ severity: 'info', summary: 'Выход', detail: 'Вы вышли из системы', life: 3000 })
  setTimeout(() => {
    localStorage.removeItem('user_email');
    localStorage.removeItem('user_name');
    router.push('/');
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
  display: flex;
  justify-content: space-around;
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

/* Карточка анализа */
.analysis-card {
  margin-top: 0;
}
.analysis-section {
  margin-bottom: 1.2rem;
}
.analysis-section h4 {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 1rem;
  margin-bottom: 0.5rem;
  color: #1e293b;
}
.analysis-section p {
  margin: 0;
  line-height: 1.4;
  background: #f1f5f9;
  padding: 0.6rem;
  border-radius: 12px;
}
.requirements-list {
  list-style: none;
  padding: 0;
  margin: 0;
  background: #f1f5f9;
  border-radius: 12px;
  max-height: 200px;
  overflow-y: auto;
}
.requirements-list li {
  padding: 0.6rem;
  border-bottom: 1px solid #e2e8f0;
  font-size: 0.85rem;
}
.requirements-list.key li {
  font-weight: 600;
  color: #0f3b5c;
}
.clear-btn {
  margin-top: 0.8rem;
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