<template>
  <div class="user-cabinet">
    <header class="cabinet-header">
      <div class="logo-area">
        <i class="pi pi-user"></i>
        <span>Личный кабинет</span>
      </div>
      <Button 
        icon="pi pi-arrow-left" 
        label="На главную" 
        severity="secondary" 
        text 
        @click="$router.push('/MainPage')" 
      />
    </header>

    <div class="cabinet-content">
      <!-- Приветствие и статистика -->
      <div class="greeting-stat">
        <div class="greeting">
          <h1>Здравствуйте, {{ userName }}</h1>
          <p>Ваши проанализированные тендеры</p>
        </div>
        <div class="stat-cards">
          <Card class="small-stat">
            <template #content>
              <div class="stat-value">{{ totalDocs }}</div>
              <div class="stat-label">Всего документов</div>
            </template>
          </Card>
          <Card class="small-stat">
            <template #content>
              <div class="stat-value">{{ totalDocs }}</div>
              <div class="stat-label">Проанализировано</div>
            </template>
          </Card>
          <Card class="small-stat">
            <template #content>
              <div class="stat-value">{{ highRiskCount }}</div>
              <div class="stat-label">Высокого риска*</div>
            </template>
          </Card>
        </div>
      </div>

      <!-- Таблица документов -->
      <Card class="docs-table-card">
        <template #title>
          <div class="table-title">
            <i class="pi pi-file-pdf"></i> Мои документы
            <!-- Фильтр можно расширить, пока оставляем простой -->
          </div>
        </template>
        <template #content>
          <DataTable 
            :value="documents" 
            paginator 
            :rows="5" 
            stripedRows
            class="p-datatable-sm"
            :loading="loading"
          >
            <Column field="file_name" header="Название файла" sortable></Column>
            <Column field="created_at" header="Дата анализа" sortable></Column>
            <Column field="tender_name" header="Название тендера" sortable></Column>
            <Column header="Действия">
              <template #body="{ data }">
                <Button 
                  icon="pi pi-eye" 
                  text 
                  rounded 
                  @click="showDetails(data)" 
                  tooltip="Подробнее"
                />
              </template>
            </Column>
          </DataTable>
        </template>
      </Card>
    </div>

    <!-- Диалог детального анализа -->
    <Dialog 
      v-model:visible="detailsDialog" 
      header="Детали анализа документа" 
      :modal="true" 
      :style="{ width: '700px' }"
    >
      <div v-if="selectedDoc" class="dialog-content">
        <h3>{{ selectedDoc.file_name }}</h3>
        <p><strong>Название тендера:</strong> {{ selectedDoc.tender_name || '—' }}</p>
        <p><strong>Описание тендера:</strong> {{ selectedDoc.tender_description || '—' }}</p>
        <p><strong>Дата анализа:</strong> {{ selectedDoc.created_at }}</p>
        
        <div class="analysis-block">
          <div class="requirement-section">
            <strong>📋 Все требования:</strong>
            <ul class="requirement-list" v-if="selectedDoc.all_requirements?.length">
              <li v-for="(req, idx) in selectedDoc.all_requirements" :key="idx">{{ req }}</li>
            </ul>
            <div v-else class="empty-msg">Требования не извлечены</div>
          </div>
          <div class="requirement-section">
            <strong>⭐ Ключевые требования:</strong>
            <ul class="requirement-list key-requirements" v-if="selectedDoc.key_requirements?.length">
              <li v-for="(req, idx) in selectedDoc.key_requirements" :key="idx">{{ req }}</li>
            </ul>
            <div v-else class="empty-msg">Ключевые требования не выделены</div>
          </div>
        </div>
      </div>
      <template #footer>
        <Button label="Закрыть" icon="pi pi-times" @click="detailsDialog = false" autofocus />
      </template>
    </Dialog>

    <Toast position="bottom-right" />
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import axios from 'axios'
import { useToast } from 'primevue/usetoast'
import Card from 'primevue/card'
import Button from 'primevue/button'
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'
import Dialog from 'primevue/dialog'
import Toast from 'primevue/toast'

const toast = useToast()
const userName = ref(localStorage.getItem('user_name') || 'Пользователь')
const documents = ref([])
const loading = ref(false)

// Статистика
const totalDocs = computed(() => documents.value.length)
const highRiskCount = computed(() => {
  // Пример: считаем высокорисковыми те документы, у которых ключевых требований больше 5
  return documents.value.filter(doc => (doc.key_requirements?.length || 0) > 5).length
})

// Загрузка списка анализов с сервера
async function loadDocuments() {
  loading.value = true
  try {
    const response = await axios.get('http://localhost:8000/user/documents', {
      withCredentials: true
    });
    documents.value = response.data
  } catch (error) {
    console.error('Ошибка загрузки:', error)
    let msg = 'Не удалось загрузить список документов'
    if (error.response?.status === 401) {
      msg = 'Сессия истекла. Перенаправление на страницу входа...'
      toast.add({ severity: 'error', summary: 'Ошибка', detail: msg, life: 3000 })
      setTimeout(() => {
        localStorage.removeItem('user_email')
        localStorage.removeItem('user_name')
        window.location.href = '/'
      }, 2000)
    } else if (error.response?.data?.detail) {
      msg = error.response.data.detail
      toast.add({ severity: 'error', summary: 'Ошибка', detail: msg, life: 5000 })
    } else {
      toast.add({ severity: 'error', summary: 'Ошибка', detail: msg, life: 5000 })
    }
  } finally {
    loading.value = false
  }
}

// Диалог деталей
const detailsDialog = ref(false)
const selectedDoc = ref(null)

function showDetails(doc) {
  selectedDoc.value = doc
  detailsDialog.value = true
}

onMounted(() => {
  loadDocuments()
})
</script>

<style scoped>
.user-cabinet {
  min-height: 100vh;
  background: #f8fafc;
  font-family: 'Inter', sans-serif;
}

.cabinet-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 2rem;
  background: white;
  border-bottom: 1px solid #e2e8f0;
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

.cabinet-content {
  max-width: 1200px;
  margin: 2rem auto;
  padding: 0 2rem;
}

.greeting-stat {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 1.5rem;
  margin-bottom: 2rem;
}
.greeting h1 {
  margin: 0;
  font-size: 1.8rem;
}
.greeting p {
  margin: 0.25rem 0 0;
  color: #475569;
}
.stat-cards {
  display: flex;
  gap: 1rem;
}
.small-stat :deep(.p-card-content) {
  padding: 0.75rem 1.5rem;
  text-align: center;
}
.stat-value {
  font-size: 1.8rem;
  font-weight: bold;
  color: #3b9bd5;
}
.stat-label {
  font-size: 0.8rem;
  color: #475569;
}

.table-title {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 1rem;
}

.dialog-content h3 {
  margin-top: 0;
}
.dialog-content p {
  margin: 0.5rem 0;
}
.analysis-block {
  margin-top: 1rem;
}
.requirement-section {
  margin-bottom: 1rem;
}
.requirement-list {
  list-style: disc;
  margin: 0.5rem 0 1rem 1.5rem;
  padding: 0;
  max-height: 200px;
  overflow-y: auto;
  background: #f1f5f9;
  padding: 0.5rem 1rem;
  border-radius: 12px;
}
.key-requirements {
  list-style: circle;
  color: #0f3b5c;
  font-weight: 500;
}
.empty-msg {
  background: #f1f5f9;
  padding: 0.5rem;
  border-radius: 8px;
  color: #64748b;
  margin-top: 0.25rem;
}
</style>