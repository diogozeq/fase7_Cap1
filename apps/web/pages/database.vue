<template>
  <div class="min-h-screen bg-gray-50 p-8">
    <div class="max-w-7xl mx-auto">
      <h1 class="text-3xl font-bold text-gray-800 mb-6">🗄️ Banco de Dados Visual</h1>
      
      <div class="grid grid-cols-1 lg:grid-cols-4 gap-6">
        <!-- Error Alert -->
        <div v-if="error" class="lg:col-span-4 bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative" role="alert">
          <strong class="font-bold">Erro: </strong>
          <span class="block sm:inline">{{ error }}</span>
        </div>

        <!-- Table List -->
        <div class="bg-white rounded-lg shadow-md p-4">
          <h2 class="text-lg font-bold mb-4 text-gray-700">Tabelas</h2>
          <div class="space-y-1">
            <button 
              v-for="table in tables" 
              :key="table"
              @click="selectTable(table)"
              :class="['w-full text-left px-3 py-2 rounded-md text-sm transition-colors', currentTable === table ? 'bg-blue-100 text-blue-700 font-medium' : 'text-gray-600 hover:bg-gray-50']"
            >
              {{ formatTableName(table) }}
            </button>
          </div>
        </div>

        <!-- Data View -->
        <div class="lg:col-span-3 bg-white rounded-lg shadow-md p-6 overflow-hidden">
          <div class="flex justify-between items-center mb-6">
            <h2 class="text-xl font-bold text-gray-800">{{ formatTableName(currentTable) }}</h2>
            <div class="flex gap-2">
              <button @click="refreshData" class="p-2 text-gray-500 hover:text-blue-600 transition-colors" title="Atualizar">
                <span class="material-symbols-outlined">refresh</span>
              </button>
            </div>
          </div>

          <!-- Loading State -->
          <div v-if="loading" class="flex justify-center py-12">
            <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
          </div>

          <!-- Empty State -->
          <div v-else-if="tableData.length === 0" class="text-center py-12 bg-gray-50 rounded-lg border-2 border-dashed border-gray-200">
            <p class="text-gray-500">Nenhum registro encontrado nesta tabela.</p>
          </div>

          <!-- Data Table -->
          <div v-else class="overflow-x-auto">
            <table class="w-full text-sm text-left">
              <thead class="text-xs text-gray-700 uppercase bg-gray-50">
                <tr>
                  <th v-for="col in columns" :key="col" class="px-6 py-3 whitespace-nowrap">
                    {{ col }}
                  </th>
                  <th class="px-6 py-3 text-right">Ações</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="(row, idx) in tableData" :key="idx" class="bg-white border-b hover:bg-gray-50">
                  <td v-for="col in columns" :key="col" class="px-6 py-4 whitespace-nowrap max-w-xs truncate">
                    {{ formatValue(row[col]) }}
                  </td>
                  <td class="px-6 py-4 text-right">
                    <button @click="deleteRow(row)" class="text-red-600 hover:text-red-900">
                      <span class="material-symbols-outlined text-sm">delete</span>
                    </button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
          
          <!-- Pagination Info -->
          <div class="mt-4 text-sm text-gray-500 flex justify-between items-center">
            <span>Mostrando {{ tableData.length }} de {{ totalRecords }} registros</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'

const tables = ref<string[]>([])
const currentTable = ref('')
const tableData = ref<any[]>([])
const columns = ref<string[]>([])
const totalRecords = ref(0)
const loading = ref(false)

const formatTableName = (name: string) => {
  return name.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())
}

const formatValue = (val: any) => {
  if (val === null || val === undefined) return '-'
  if (typeof val === 'boolean') return val ? 'Sim' : 'Não'
  return val
}

const error = ref('')

const fetchTables = async () => {
  loading.value = true
  error.value = ''
  try {
    const data = await $fetch<string[]>('http://localhost:8000/api/database/tables')
    if (data) {
      tables.value = data
      if (data.length > 0 && !currentTable.value && data[0]) {
        selectTable(data[0] as string)
      }
    }
  } catch (e) {
    console.error('Failed to fetch tables', e)
    error.value = 'Erro ao carregar tabelas: ' + (e instanceof Error ? e.message : String(e))
  } finally {
    loading.value = false
  }
}

const selectTable = (table: string) => {
  currentTable.value = table
  refreshData()
}

const refreshData = async () => {
  if (!currentTable.value) return
  
  loading.value = true
  error.value = ''
  try {
    const data = await $fetch<any>(`http://localhost:8000/api/database/data/${currentTable.value}`)
    if (data) {
      columns.value = data.columns
      tableData.value = data.data
      totalRecords.value = data.total
    }
  } catch (e) {
    console.error('Failed to fetch data', e)
    error.value = 'Erro ao carregar dados: ' + (e instanceof Error ? e.message : String(e))
  } finally {
    loading.value = false
  }
}

const deleteRow = async (row: any) => {
  if (!confirm('Tem certeza que deseja excluir este registro?')) return
  
  // Try to find ID column (usually first one or containing 'id')
  const idCol = columns.value.find(c => c.startsWith('id_')) || columns.value[0]
  if (!idCol) return
  const id = row[idCol]
  
  try {
    await $fetch(`http://localhost:8000/api/database/data/${currentTable.value}/${id}`, {
      method: 'DELETE'
    })
    refreshData()
  } catch (e) {
    alert('Erro ao deletar registro: ' + e)
  }
}

onMounted(() => {
  fetchTables()
})
</script>
