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
        @click="$router.push('/')" 
      />
    </header>

    <div class="cabinet-content">
      <!-- Приветствие и статистика -->
      <div class="greeting-stat">
        <div class="greeting">
          <h1>Здравствуйте, {{ userName }} 👋</h1>
          <p>Ваши документы и результаты их анализа</p>
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
              <div class="stat-value">{{ analyzedDocs }}</div>
              <div class="stat-label">Проанализировано</div>
            </template>
          </Card>
          <Card class="small-stat">
            <template #content>
              <div class="stat-value">{{ highRiskDocs }}</div>
              <div class="stat-label">С высоким риском</div>
            </template>
          </Card>
        </div>
      </div>

      <!-- Фильтр и таблица документов -->
      <Card class="docs-table-card">
        <template #title>
          <div class="table-title">
            <i class="pi pi-file-pdf"></i> Мои документы
            <div class="filter-group">
              <SelectButton 
                v-model="filterStatus" 
                :options="filterOptions" 
                optionLabel="label" 
                optionValue="value"
              />
            </div>
          </div>
        </template>
        <template #content>
          <DataTable 
            :value="filteredDocuments" 
            paginator 
            :rows="5" 
            stripedRows
            class="p-datatable-sm"
          >
            <Column field="name" header="Название" sortable></Column>
            <Column field="uploadDate" header="Дата загрузки" sortable></Column>
            <Column field="analysisStatus" header="Статус анализа">
              <template #body="{ data }">
                <Badge :value="data.analysisStatus" :severity="getStatusSeverity(data.analysisStatus)" />
              </template>
            </Column>
            <Column field="risk" header="Результат анализа">
              <template #body="{ data }">
                <span v-if="data.risk" :class="getRiskClass(data.risk)">{{ data.risk }}</span>
                <span v-else class="text-muted">—</span>
              </template>
            </Column>
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

    <!-- Диалог подробного анализа -->
    <Dialog 
      v-model:visible="detailsDialog" 
      header="Детали анализа документа" 
      :modal="true" 
      :style="{ width: '550px' }"
    >
      <div v-if="selectedDoc" class="dialog-content">
        <h3>{{ selectedDoc.name }}</h3>
        <p><strong>Дата загрузки:</strong> {{ selectedDoc.uploadDate }}</p>
        <p><strong>Статус анализа:</strong> 
          <Badge :value="selectedDoc.analysisStatus" :severity="getStatusSeverity(selectedDoc.analysisStatus)" />
        </p>
        <div class="analysis-block">
          <strong>Результаты анализа (заглушка):</strong>
          <div class="analysis-placeholder">
            <div v-if="selectedDoc.risk === 'Высокий риск'" class="risk-high">
              ⚠️ Обнаружены критические риски: несоответствие требованиям, завышенная цена.
            </div>
            <div v-else-if="selectedDoc.risk === 'Средний риск'" class="risk-medium">
              ⚠️ Есть некоторые замечания по срокам и гарантийным обязательствам.
            </div>
            <div v-else-if="selectedDoc.risk === 'Низкий риск'" class="risk-low">
              ✅ Документ соответствует основным критериям, риски минимальны.
            </div>
            <div v-else>
              📄 Анализ ещё не выполнен. После обработки здесь появятся рекомендации.
            </div>
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
import { ref, computed } from 'vue'
import { useToast } from 'primevue/usetoast'
import Card from 'primevue/card'
import Button from 'primevue/button'
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'
import Badge from 'primevue/badge'
import SelectButton from 'primevue/selectbutton'
import Dialog from 'primevue/dialog'
import Toast from 'primevue/toast'

const toast = useToast()
const userName = ref(localStorage.getItem('user_name') || 'Пользователь')

// Моковые данные документов (в будущем заменим на запрос к API)
const documents = ref([
  {
    id: 1,
    name: 'Тендер_медоборудование.pdf',
    uploadDate: '20.04.2026',
    analysisStatus: 'Завершён',
    risk: 'Средний риск',
    details: 'Обнаружены замечания по срокам поставки.'
  },
  {
    id: 2,
    name: 'Анализ_рисков_дорога.docx',
    uploadDate: '18.04.2026',
    analysisStatus: 'Завершён',
    risk: 'Низкий риск',
    details: 'Документ соответствует критериям.'
  },
  {
    id: 3,
    name: 'Финансовая_модель.xlsx',
    uploadDate: '15.04.2026',
    analysisStatus: 'Завершён',
    risk: 'Высокий риск',
    details: 'Завышенные финансовые показатели, несоответствие НМЦК.'
  },
  {
    id: 4,
    name: 'Техническое_задание.pdf',
    uploadDate: '10.04.2026',
    analysisStatus: 'В процессе',
    risk: null,
    details: 'Анализ запущен, ожидайте результат.'
  },
  {
    id: 5,
    name: 'Договор_оферта.docx',
    uploadDate: '05.04.2026',
    analysisStatus: 'Завершён',
    risk: 'Низкий риск',
    details: 'Риски отсутствуют, рекомендуется к участию.'
  }
])

// Фильтрация
const filterStatus = ref('all')
const filterOptions = [
  { label: 'Все', value: 'all' },
  { label: 'Завершён', value: 'Завершён' },
  { label: 'В процессе', value: 'В процессе' },
  { label: 'Загружен', value: 'Загружен' }
]

const filteredDocuments = computed(() => {
  if (filterStatus.value === 'all') return documents.value
  return documents.value.filter(doc => doc.analysisStatus === filterStatus.value)
})

// Подсчёт статистики
const totalDocs = computed(() => documents.value.length)
const analyzedDocs = computed(() => documents.value.filter(d => d.analysisStatus === 'Завершён').length)
const highRiskDocs = computed(() => documents.value.filter(d => d.risk === 'Высокий риск').length)

// Вспомогательные функции для отображения статусов и рисков
function getStatusSeverity(status) {
  switch (status) {
    case 'Завершён': return 'success'
    case 'В процессе': return 'warning'
    case 'Загружен': return 'info'
    default: return 'secondary'
  }
}

function getRiskClass(risk) {
  if (risk === 'Высокий риск') return 'risk-high-text'
  if (risk === 'Средний риск') return 'risk-medium-text'
  if (risk === 'Низкий риск') return 'risk-low-text'
  return ''
}

// Диалог деталей
const detailsDialog = ref(false)
const selectedDoc = ref(null)

function showDetails(doc) {
  selectedDoc.value = doc
  detailsDialog.value = true
}
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
.filter-group {
  display: flex;
  gap: 0.5rem;
}

.dialog-content p {
  margin: 0.5rem 0;
}
.analysis-block {
  margin-top: 1rem;
}
.analysis-placeholder {
  background: #f1f5f9;
  padding: 0.75rem;
  border-radius: 8px;
  margin-top: 0.5rem;
}
.risk-high {
  color: #b91c1c;
}
.risk-medium {
  color: #b45309;
}
.risk-low {
  color: #1f7840;
}
.risk-high-text {
  color: #b91c1c;
  font-weight: 600;
}
.risk-medium-text {
  color: #b45309;
  font-weight: 600;
}
.risk-low-text {
  color: #1f7840;
  font-weight: 600;
}
.text-muted {
  color: #94a3b8;
}
</style>