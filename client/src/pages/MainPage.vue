<template>
  <div class="dashboard">
    <div class="bg-blur blur-1"></div>
    <div class="bg-blur blur-2"></div>
    <div class="bg-pattern"></div>

    <header class="dashboard-header">
      <div class="logo-area">
        <i class="fas fa-file-contract"></i>
        <span>Тендерный портал</span>
      </div>
      <div class="user-area">
        <span class="user-name">{{ user_name }}</span>
        <div class="avatar" @click="GoToUserLk">
          <i class="fas fa-user-astronaut"></i>
        </div>
        <button class="logout-btn" @click="logout">
          <i class="fas fa-sign-out-alt"></i>
        </button>
      </div>
    </header>

    <div class="dashboard-content">
      <div class="main-column">
        <div class="card upload-card">
          <h2><i class="fas fa-cloud-upload-alt"></i> Загрузить тендерную документацию</h2>
          <p class="subtitle">Поддерживаются форматы PDF, DOCX, XLSX, ZIP (до 50 МБ)</p>

          <div
            class="dropzone"
            :class="{ 'drag-over': isDragOver }"
            @dragenter.prevent="isDragOver = true"
            @dragleave.prevent="isDragOver = false"
            @dragover.prevent
            @drop.prevent="handleDrop"
            @click="triggerFileInput"
          >
            <i class="fas fa-file-upload"></i>
            <p>Перетащите файл сюда или <span>нажмите для выбора</span></p>
            <input
              type="file"
              ref="fileInput"
              style="display: none"
              accept=".pdf,.docx,.xlsx,.zip"
              @change="handleFileSelect"
            />
          </div>

          <div v-if="selectedFile" class="selected-file">
            <div class="file-info">
              <i class="fas fa-file-pdf"></i>
              <span>{{ selectedFile.name }} ({{ formatFileSize(selectedFile.size) }})</span>
              <button class="remove-file" @click.stop="clearFile">
                <i class="fas fa-times-circle"></i>
              </button>
            </div>
            <div v-if="uploadProgress > 0" class="progress-bar">
              <div class="progress-fill" :style="{ width: uploadProgress + '%' }"></div>
              <span class="progress-text">{{ uploadProgress }}%</span>
            </div>
            <button
              v-if="selectedFile && uploadProgress === 0"
              class="upload-btn"
              @click="simulateUpload"
            >
              <i class="fas fa-upload"></i> Загрузить и добавить в список
            </button>
          </div>
        </div>

        <div class="stats-grid">
          <div class="stat-card">
            <i class="fas fa-folder-open"></i>
            <div class="stat-info">
              <h3>124</h3>
              <p>Всего тендеров</p>
            </div>
          </div>
          <div class="stat-card">
            <i class="fas fa-chart-line"></i>
            <div class="stat-info">
              <h3>86</h3>
              <p>Проанализировано</p>
            </div>
          </div>
          <div class="stat-card">
            <i class="fas fa-exclamation-triangle"></i>
            <div class="stat-info">
              <h3>12</h3>
              <p>Высоких рисков</p>
            </div>
          </div>
        </div>
      </div>

      <div class="side-column">
        <!-- Недавние загрузки -->
        <div class="card recent-card">
          <h3><i class="fas fa-history"></i> Недавние документы</h3>
          <div class="recent-list">
            <div
              v-for="doc in recentDocuments"
              :key="doc.id"
              class="recent-item"
            >
              <i class="fas fa-file-alt"></i>
              <div class="doc-info">
                <div class="doc-name">{{ doc.name }}</div>
                <div class="doc-meta">{{ doc.date }} • {{ doc.status }}</div>
              </div>
              <button class="analyze-btn" @click="analyzeDocument(doc)">
                <i class="fas fa-microscope"></i>
              </button>
            </div>
            <div v-if="recentDocuments.length === 0" class="empty-message">
              <i class="fas fa-inbox"></i> Нет загруженных документов
            </div>
          </div>
        </div>

        <div class="card active-tenders">
          <h3><i class="fas fa-tasks"></i> Активные тендеры</h3>
          <div class="tender-list">
            <div class="tender-item">
              <div class="tender-title">Поставка медоборудования</div>
              <div class="tender-deadline">Дедлайн: 30.05.2026</div>
              <span class="status-badge warning">На анализе</span>
            </div>
            <div class="tender-item">
              <div class="tender-title">Строительство автодороги</div>
              <div class="tender-deadline">Дедлайн: 15.06.2026</div>
              <span class="status-badge success">Низкий риск</span>
            </div>
            <div class="tender-item">
              <div class="tender-title">ИТ-инфраструктура</div>
              <div class="tender-deadline">Дедлайн: 01.06.2026</div>
              <span class="status-badge danger">Высокий риск</span>
            </div>
          </div>
          <button class="more-btn">Все тендеры →</button>
        </div>
      </div>
    </div>

    <div v-if="toast.show" class="toast" :class="toast.type">
      <i :class="toast.icon"></i>
      <span>{{ toast.message }}</span>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onUnmounted } from 'vue'
import { useRouter } from 'vue-router';

const user_name = localStorage.getItem("user_name");

const selectedFile = ref(null)
const uploadProgress = ref(0)
const isDragOver = ref(false)
const fileInput = ref(null)
const recentDocuments = ref([])

const router = useRouter();

const toast = reactive({
  show: false,
  message: '',
  type: 'info',
  icon: 'fas fa-info-circle'
})
let toastTimeout = null


function GoToUserLk(){
  router.push('/UserLK');
}


function showToast(message, type = 'success') {
  if (toastTimeout) clearTimeout(toastTimeout)
  toast.message = message
  toast.type = type
  toast.icon = type === 'success' ? 'fas fa-check-circle' : (type === 'error' ? 'fas fa-exclamation-circle' : 'fas fa-info-circle')
  toast.show = true
  toastTimeout = setTimeout(() => {
    toast.show = false
  }, 3000)
}

function formatFileSize(bytes) {
  if (bytes === 0) return '0 Bytes'
  const k = 1024
  const sizes = ['Bytes', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i]
}
-
function triggerFileInput() {
  fileInput.value.click()
}

function handleFileSelect(event) {
  const file = event.target.files[0]
  if (file) processFile(file)
}

function handleDrop(event) {
  isDragOver.value = false
  const file = event.dataTransfer.files[0]
  if (file) processFile(file)
}

function processFile(file) {
  const allowedTypes = ['application/pdf', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', 'application/zip']
  const maxSize = 50 * 1024 * 1024 // 50 MB

  if (!allowedTypes.includes(file.type) && !file.name.match(/\.(pdf|docx|xlsx|zip)$/i)) {
    showToast('Неподдерживаемый формат файла', 'error')
    return
  }
  if (file.size > maxSize) {
    showToast('Файл превышает 50 МБ', 'error')
    return
  }
  selectedFile.value = file
  uploadProgress.value = 0
}

function clearFile() {
  selectedFile.value = null
  uploadProgress.value = 0
  if (fileInput.value) fileInput.value.value = ''
}

function simulateUpload() {
  if (!selectedFile.value) return

  let progress = 0
  const interval = setInterval(() => {
    progress += 10
    uploadProgress.value = progress
    if (progress >= 100) {
      clearInterval(interval)
      // Добавляем документ в недавние
      const newDoc = {
        id: Date.now(),
        name: selectedFile.value.name,
        date: new Date().toLocaleDateString('ru-RU'),
        status: 'Загружен',
        file: selectedFile.value
      }
      recentDocuments.value.unshift(newDoc) // добавляем в начало
      showToast(`Файл "${selectedFile.value.name}" успешно загружен`, 'success')
      clearFile()
    }
  }, 150)
}

function analyzeDocument(doc) {
  showToast(`Запущен анализ документа "${doc.name}" (демо-режим)`, 'info')
  // Здесь можно было бы эмитировать событие или перейти на страницу анализа
}

// --- Выход (имитация) ---
function logout() {
  showToast('Вы вышли из системы (демо-режим)', 'info')
  // Здесь можно вызвать emit для смены компонента, но для демонстрации просто редирект
  setTimeout(() => {
    alert('В реальном приложении здесь будет переход на страницу авторизации')
  }, 500)
}

onUnmounted(() => {
  if (toastTimeout) clearTimeout(toastTimeout)
})
</script>

<style scoped>
.dashboard {
  min-height: 100vh;
  background: radial-gradient(ellipse at 20% 30%, #0B2A3B 0%, #03161F 100%);
  font-family: 'Inter', sans-serif;
  position: relative;
  overflow-x: hidden;
}
.bg-blur {
  position: fixed;
  width: 50vw;
  height: 50vw;
  border-radius: 50%;
  filter: blur(80px);
  opacity: 0.4;
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
  position: fixed;
  inset: 0;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 200 200'%3E%3Cpath fill='none' stroke='rgba(255,255,255,0.03)' stroke-width='1' d='M0 0 L200 200 M200 0 L0 200'/%3E%3C/svg%3E");
  background-size: 30px 30px;
  pointer-events: none;
}

/* Header */
.dashboard-header {
  position: relative;
  z-index: 10;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 2rem;
  background: rgba(15, 35, 45, 0.85);
  backdrop-filter: blur(12px);
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}
.logo-area {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 1.4rem;
  font-weight: 700;
  color: white;
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
  color: #e2e8f0;
  font-weight: 500;
}
.avatar {
  width: 40px;
  height: 40px;
  background: linear-gradient(135deg, #2c6e8f, #1a4c63);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  cursor: pointer;
}
.logout-btn {
  background: none;
  border: none;
  color: #f87171;
  font-size: 1.2rem;
  cursor: pointer;
  transition: 0.2s;
}
.logout-btn:hover {
  transform: scale(1.05);
  color: #ff9f9f;
}

/* Контент */
.dashboard-content {
  position: relative;
  z-index: 10;
  max-width: 1400px;
  margin: 2rem auto;
  padding: 0 2rem;
  display: grid;
  grid-template-columns: 1fr 360px;
  gap: 1.8rem;
}
@media (max-width: 900px) {
  .dashboard-content {
    grid-template-columns: 1fr;
  }
}

.card {
  background: rgba(255, 255, 255, 0.96);
  border-radius: 32px;
  padding: 1.5rem;
  box-shadow: 0 15px 35px rgba(0, 0, 0, 0.2);
  margin-bottom: 1.8rem;
  backdrop-filter: blur(2px);
}
.upload-card h2, .recent-card h3, .active-tenders h3 {
  font-size: 1.3rem;
  margin-bottom: 0.5rem;
  display: flex;
  align-items: center;
  gap: 8px;
  color: #1f3a4b;
}
.subtitle {
  font-size: 0.8rem;
  color: #5b6e8c;
  margin-bottom: 1.2rem;
}
.dropzone {
  border: 2px dashed #b9d0e0;
  border-radius: 28px;
  padding: 2rem;
  text-align: center;
  cursor: pointer;
  transition: 0.2s;
  background: #f9fdfe;
}
.dropzone i {
  font-size: 2.5rem;
  color: #2c9cd4;
  margin-bottom: 0.5rem;
}
.dropzone p {
  color: #3a5a6e;
}
.dropzone span {
  color: #166C8C;
  font-weight: 600;
}
.dropzone.drag-over {
  border-color: #166C8C;
  background: #e6f4fa;
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
.remove-file {
  background: none;
  border: none;
  color: #e53e3e;
  cursor: pointer;
  font-size: 1.1rem;
}
.progress-bar {
  margin: 0.8rem 0;
  height: 8px;
  background: #ddd;
  border-radius: 10px;
  overflow: hidden;
  position: relative;
}
.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #2c9cd4, #166C8C);
  width: 0%;
  transition: width 0.2s;
}
.progress-text {
  position: absolute;
  right: 0;
  top: -18px;
  font-size: 0.7rem;
  font-weight: bold;
}
.upload-btn {
  background: linear-gradient(95deg, #166C8C, #0F4B63);
  border: none;
  padding: 0.6rem 1rem;
  border-radius: 40px;
  color: white;
  font-weight: 600;
  cursor: pointer;
  width: 100%;
  margin-top: 0.5rem;
}
.stats-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1rem;
}
.stat-card {
  background: rgba(255, 255, 255, 0.96);
  border-radius: 28px;
  padding: 1rem;
  display: flex;
  align-items: center;
  gap: 0.8rem;
  box-shadow: 0 5px 12px rgba(0,0,0,0.05);
}
.stat-card i {
  font-size: 2rem;
  color: #2c9cd4;
}
.stat-info h3 {
  font-size: 1.6rem;
  margin: 0;
  line-height: 1;
}
.stat-info p {
  font-size: 0.7rem;
  color: #5b6e8c;
}
.recent-list, .tender-list {
  margin-top: 1rem;
}
.recent-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 0.7rem 0;
  border-bottom: 1px solid #eef2f6;
}
.recent-item i {
  font-size: 1.3rem;
  color: #2c9cd4;
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
.analyze-btn {
  background: none;
  border: none;
  font-size: 1.1rem;
  cursor: pointer;
  color: #166C8C;
}
.empty-message {
  text-align: center;
  padding: 1.5rem;
  color: #8ba0b5;
}
.tender-item {
  padding: 0.8rem 0;
  border-bottom: 1px solid #eef2f6;
}
.tender-title {
  font-weight: 600;
}
.tender-deadline {
  font-size: 0.7rem;
  color: #6c86a3;
}
.status-badge {
  display: inline-block;
  font-size: 0.7rem;
  padding: 0.2rem 0.6rem;
  border-radius: 30px;
  margin-top: 0.3rem;
}
.status-badge.warning {
  background: #fff3e0;
  color: #b45309;
}
.status-badge.success {
  background: #e0f2e9;
  color: #1f7840;
}
.status-badge.danger {
  background: #ffe6e6;
  color: #b91c1c;
}
.more-btn {
  background: none;
  border: none;
  color: #166C8C;
  font-weight: 600;
  margin-top: 1rem;
  cursor: pointer;
  width: 100%;
  text-align: center;
}
.toast {
  position: fixed;
  bottom: 2rem;
  right: 2rem;
  background: white;
  padding: 0.8rem 1.2rem;
  border-radius: 40px;
  display: flex;
  align-items: center;
  gap: 8px;
  box-shadow: 0 10px 20px rgba(0,0,0,0.2);
  z-index: 1000;
  animation: slideIn 0.2s ease;
}
.toast.success { border-left: 5px solid #2ecc71; }
.toast.error { border-left: 5px solid #e74c3c; }
.toast.info { border-left: 5px solid #3498db; }
@keyframes slideIn {
  from { opacity: 0; transform: translateX(50px); }
  to { opacity: 1; transform: translateX(0); }
}
</style>