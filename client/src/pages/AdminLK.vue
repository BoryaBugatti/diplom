<template>
  <div class="admin-cabinet">
    <header class="cabinet-header">
      <div class="logo-area">
        <i class="pi pi-shield"></i>
        <span>Панель администратора</span>
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
      <div class="greeting-stat">
        <div class="greeting">
          <h1>Здравствуйте, {{ adminName }}</h1>
          <p>Управление анализами и отчётами</p>
        </div>
        <div class="stat-cards">
          <Card class="small-stat">
            <template #content>
              <div class="stat-value">{{ totalAnalyses }}</div>
              <div class="stat-label">Всего анализов</div>
            </template>
          </Card>
          <Card class="small-stat">
            <template #content>
              <div class="stat-value">{{ totalUsers }}</div>
              <div class="stat-label">Пользователей</div>
            </template>
          </Card>
          <Card class="small-stat">
            <template #content>
              <div class="stat-value">{{ totalReports }}</div>
              <div class="stat-label">Сгенерировано отчётов</div>
            </template>
          </Card>
        </div>
      </div>

      <TabView class="admin-tabs">
        <TabPanel header="📄 Все анализы">
          <div class="table-toolbar">
            <div class="filters">
              <Dropdown 
                v-model="selectedUserId" 
                :options="userOptions" 
                optionLabel="label" 
                optionValue="value"
                placeholder="Все пользователи" 
                clearable 
                style="width: 250px"
              />
              <Button 
                icon="pi pi-download" 
                label="Экспорт таблицы (CSV)" 
                severity="info" 
                outlined 
                @click="exportAllToCSV"
              />
            </div>
            <DataTable 
              :value="filteredDocuments" 
              paginator 
              :rows="10" 
              stripedRows
              class="p-datatable-sm"
              :loading="loading"
            >
              <Column field="user_name" header="Пользователь" sortable></Column>
              <Column field="file_name" header="Файл" sortable></Column>
              <Column field="tender_name" header="Название тендера" sortable></Column>
              <Column field="created_at" header="Дата анализа" sortable></Column>
              <Column header="Действия">
                <template #body="{ data }">
                  <Button 
                    icon="pi pi-eye" 
                    text 
                    rounded 
                    @click="showDetails(data)" 
                    tooltip="Подробнее"
                  />
                  <Dropdown 
                    v-model="data.selectedFormat" 
                    :options="reportFormats" 
                    optionLabel="label" 
                    optionValue="value"
                    placeholder="Формат отчёта"
                    class="format-dropdown"
                    @change="generateReport(data)"
                  >
                    <template #value="slotProps">
                      <div v-if="slotProps.value">
                        <i :class="getFormatIcon(slotProps.value)"></i> {{ getFormatLabel(slotProps.value) }}
                      </div>
                      <div v-else>📄 Отчёт</div>
                    </template>
                    <template #option="slotProps">
                      <i :class="getFormatIcon(slotProps.option.value)"></i> {{ slotProps.option.label }}
                    </template>
                  </Dropdown>
                </template>
              </Column>
            </DataTable>
          </div>
        </TabPanel>

        <TabPanel header="👥 Пользователи">
          <DataTable :value="users" stripedRows class="p-datatable-sm" :loading="usersLoading">
            <Column field="user_name" header="Имя пользователя" sortable></Column>
            <Column field="user_email" header="Email" sortable></Column>
            <Column field="user_role" header="Роль" sortable>
              <template #body="{ data }">
                <Dropdown 
                  v-model="data.user_role" 
                  :options="roleOptions" 
                  optionLabel="label" 
                  optionValue="value"
                  :disabled="data.user_id === currentAdminId"
                  @change="updateUserRole(data)"
                />
              </template>
            </Column>
            <Column field="created_at" header="Дата регистрации" sortable></Column>
          </DataTable>
        </TabPanel>
      </TabView>
    </div>

    <Dialog 
      v-model:visible="detailsDialog" 
      header="Детали анализа" 
      :modal="true" 
      :style="{ width: '750px' }"
    >
      <div v-if="selectedDoc" class="dialog-content">
        <h3>{{ selectedDoc.file_name }}</h3>
        <p><strong>Пользователь:</strong> {{ selectedDoc.user_name }}</p>
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
import Dropdown from 'primevue/dropdown'
import TabView from 'primevue/tabview'
import TabPanel from 'primevue/tabpanel'
import Toast from 'primevue/toast'

const toast = useToast()
const adminName = ref(localStorage.getItem('user_name') || 'Администратор')
const currentAdminId = ref(parseInt(localStorage.getItem('user_id') || '0'))

const allDocuments = ref([])       
const users = ref([])             
const loading = ref(false)
const usersLoading = ref(false)
const totalReports = ref(0)      

const selectedUserId = ref(null)

const reportFormats = ref([
  { label: 'PDF', value: 'pdf', icon: 'pi-file-pdf' },
  { label: 'CSV', value: 'csv', icon: 'pi-file-excel' },
  { label: 'Excel (XLSX)', value: 'xlsx', icon: 'pi-file-excel' },
  { label: 'JSON', value: 'json', icon: 'pi-file' }
])

const roleOptions = ref([
  { label: 'Пользователь', value: 'user' },
  { label: 'Администратор', value: 'admin' }
])

const totalAnalyses = computed(() => allDocuments.value.length)
const totalUsers = computed(() => users.value.length)

const userOptions = computed(() => {
  const uniqueUsers = new Map()
  allDocuments.value.forEach(doc => {
    if (!uniqueUsers.has(doc.user_id)) {
      uniqueUsers.set(doc.user_id, { label: doc.user_name, value: doc.user_id })
    }
  })
  return Array.from(uniqueUsers.values())
})

const filteredDocuments = computed(() => {
  if (!selectedUserId.value) return allDocuments.value
  return allDocuments.value.filter(doc => doc.user_id === selectedUserId.value)
})

async function loadAllDocuments() {
  loading.value = true
  try {
    const response = await axios.get('http://localhost:8000/admin/analyses', {
      withCredentials: true
    })
    allDocuments.value = response.data.map(doc => ({
      ...doc,
      all_requirements: doc.all_requirements || [],
      key_requirements: doc.key_requirements || [],
      selectedFormat: null 
    }))
  } catch (error) {
    console.error('Ошибка загрузки анализов:', error)
    handleApiError(error)
  } finally {
    loading.value = false
  }
}

async function loadUsers() {
  usersLoading.value = true
  try {
    const response = await axios.get('http://localhost:8000/admin/users', {
      withCredentials: true
    })
    users.value = response.data
  } catch (error) {
    console.error('Ошибка загрузки пользователей:', error)
    handleApiError(error)
  } finally {
    usersLoading.value = false
  }
}

async function updateUserRole(user) {
  try {
    await axios.put(`http://localhost:8000/admin/users/${user.user_id}/role`, 
      { role: user.user_role },
      { withCredentials: true }
    )
    toast.add({ severity: 'success', summary: 'Успех', detail: `Роль пользователя ${user.user_name} изменена на ${user.user_role}`, life: 3000 })
  } catch (error) {
    console.error('Ошибка обновления роли:', error)
    toast.add({ severity: 'error', summary: 'Ошибка', detail: 'Не удалось обновить роль', life: 5000 })
    await loadUsers()
  }
}

// Генерация отчёта по одному анализу
async function generateReport(analysis) {
  const format = analysis.selectedFormat
  if (!format) return

  try {
    const response = await axios.post(`http://localhost:8000/admin/reports/generate`, 
      { analysis_id: analysis.id, format: format },
      { withCredentials: true, responseType: 'blob' }  
    )
    
    const blob = new Blob([response.data], { type: getMimeType(format) })
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.setAttribute('download', `report_analysis_${analysis.id}.${format === 'xlsx' ? 'xlsx' : format}`)
    document.body.appendChild(link)
    link.click()
    link.remove()
    window.URL.revokeObjectURL(url)
    
    toast.add({ severity: 'success', summary: 'Готово', detail: `Отчёт в формате ${format.toUpperCase()} сформирован`, life: 3000 })
    totalReports.value++ 
  } catch (error) {
    console.error('Ошибка генерации отчёта:', error)
    toast.add({ severity: 'error', summary: 'Ошибка', detail: 'Не удалось сгенерировать отчёт', life: 5000 })
  } finally {
    // Сбрасываем выбранный формат для этой строки
    analysis.selectedFormat = null
  }
}

// Экспорт текущей таблицы (отфильтрованной) в CSV
function exportAllToCSV() {
  const dataToExport = filteredDocuments.value.map(doc => ({
    'Пользователь': doc.user_name,
    'Файл': doc.file_name,
    'Название тендера': doc.tender_name,
    'Дата анализа': doc.created_at,
    'Количество требований': doc.all_requirements?.length || 0,
    'Количество ключевых требований': doc.key_requirements?.length || 0
  }))
  
  const headers = Object.keys(dataToExport[0] || {})
  const csvRows = []
  csvRows.push(headers.join(','))
  for (const row of dataToExport) {
    const values = headers.map(header => `"${(row[header] || '').toString().replace(/"/g, '""')}"`)
    csvRows.push(values.join(','))
  }
  const blob = new Blob([csvRows.join('\n')], { type: 'text/csv;charset=utf-8;' })
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.setAttribute('download', 'all_analyses.csv')
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  toast.add({ severity: 'success', summary: 'Экспорт', detail: 'Таблица выгружена в CSV', life: 3000 })
}

// Вспомогательные функции для отображения форматов
function getFormatIcon(format) {
  const f = reportFormats.value.find(f => f.value === format)
  return f ? f.icon : 'pi-file'
}

function getFormatLabel(format) {
  const f = reportFormats.value.find(f => f.value === format)
  return f ? f.label : format
}

function getMimeType(format) {
  switch (format) {
    case 'pdf': return 'application/pdf'
    case 'csv': return 'text/csv'
    case 'xlsx': return 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    default: return 'application/octet-stream'
  }
}

// Общий обработчик ошибок API (редирект при 401)
function handleApiError(error) {
  let msg = 'Ошибка сервера'
  if (error.response?.status === 401) {
    msg = 'Сессия истекла. Перенаправление на вход...'
    toast.add({ severity: 'error', summary: 'Ошибка', detail: msg, life: 3000 })
    setTimeout(() => {
      localStorage.clear()
      window.location.href = '/'
    }, 2000)
  } else if (error.response?.data?.detail) {
    msg = error.response.data.detail
    toast.add({ severity: 'error', summary: 'Ошибка', detail: msg, life: 5000 })
  } else {
    toast.add({ severity: 'error', summary: 'Ошибка', detail: msg, life: 5000 })
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
  loadAllDocuments()
  loadUsers()
  // Можно запросить общее количество сгенерированных отчётов с /admin/reports/count
})
</script>

<style scoped>
/* Переиспользуем стили из UserCabinet, добавляем новые */
.admin-cabinet {
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
  color: #e67e22;
}
.cabinet-content {
  max-width: 1400px;
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
  color: #e67e22;
}
.table-toolbar {
  margin-bottom: 1rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 1rem;
}
.filters {
  display: flex;
  gap: 1rem;
  align-items: center;
}
.format-dropdown {
  width: 120px;
  margin-left: 0.5rem;
}
.admin-tabs :deep(.p-tabview-nav) {
  background: white;
  border-radius: 12px 12px 0 0;
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
}
</style>