<template>
  <div class="min-h-screen bg-gray-50 p-8">
    <div class="max-w-6xl mx-auto">
      <NuxtLink to="/" class="text-blue-600 hover:text-blue-700 mb-6 inline-block">← Voltar</NuxtLink>
      <h1 class="text-3xl font-bold text-gray-800 mb-6">🗄️ Lançamentos de Dados</h1>

      <!-- Error Alert -->
      <div v-if="error" class="mb-6 bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative" role="alert">
        <strong class="font-bold">Erro: </strong>
        <span class="block sm:inline">{{ error }}</span>
      </div>

      <!-- Success Alert -->
      <div v-if="success" class="mb-6 bg-green-100 border border-green-400 text-green-700 px-4 py-3 rounded relative" role="alert">
        <strong class="font-bold">Sucesso! </strong>
        <span class="block sm:inline">{{ success }}</span>
      </div>

      <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <!-- Table Selector -->
        <div class="bg-white rounded-lg shadow-md p-6">
          <h2 class="text-xl font-bold mb-4">📋 Tabelas</h2>
          <div v-if="loadingTables" class="text-center py-4">
            <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
          </div>
          <div v-else class="space-y-2">
            <button
              v-for="table in availableTables"
              :key="table"
              @click="selectTable(table)"
              :class="['w-full text-left px-3 py-2 rounded-md transition-colors', selectedTable === table ? 'bg-blue-600 text-white' : 'bg-gray-100 hover:bg-gray-200']"
            >
              {{ formatTableName(table) }}
            </button>
          </div>
        </div>

        <!-- Data Display -->
        <div class="lg:col-span-2 bg-white rounded-lg shadow-md p-6">
          <div class="flex justify-between items-center mb-4">
            <h2 class="text-xl font-bold">📊 {{ formatTableName(selectedTable) }}</h2>
            <button @click="refreshData" class="p-2 text-gray-500 hover:text-blue-600 transition-colors" title="Atualizar">
              <span class="material-symbols-outlined">refresh</span>
            </button>
          </div>

          <!-- Add New Record Form -->
          <div class="mb-6 p-4 bg-blue-50 rounded-md">
            <h3 class="font-semibold mb-3">Adicionar Novo Registro</h3>

            <div v-if="selectedTable === 'culturas'" class="space-y-3">
              <input
                v-model="formData.nome_cultura"
                placeholder="Nome da Cultura (ex: Milho)"
                class="w-full px-3 py-2 border border-gray-300 rounded-md"
              />
              <button @click="createRecord" :disabled="creating" class="w-full bg-blue-600 hover:bg-blue-700 text-white font-medium py-2 rounded-md transition-colors disabled:opacity-50">
                {{ creating ? 'Adicionando...' : 'Adicionar Cultura' }}
              </button>
            </div>

            <div v-else-if="selectedTable === 'talhoes'" class="space-y-3">
              <input
                v-model="formData.nome_talhao"
                placeholder="Nome do Talhão (ex: Talhão Norte)"
                class="w-full px-3 py-2 border border-gray-300 rounded-md"
              />
              <input
                v-model.number="formData.area_hectares"
                type="number"
                step="0.01"
                placeholder="Área em Hectares (ex: 15.5)"
                class="w-full px-3 py-2 border border-gray-300 rounded-md"
              />
              <select
                v-model="formData.id_cultura_atual"
                class="w-full px-3 py-2 border border-gray-300 rounded-md"
              >
                <option :value="null">Sem cultura plantada</option>
                <option v-for="cultura in culturas" :key="cultura.id_cultura" :value="cultura.id_cultura">
                  {{ cultura.nome_cultura }}
                </option>
              </select>
              <button @click="createRecord" :disabled="creating" class="w-full bg-blue-600 hover:bg-blue-700 text-white font-medium py-2 rounded-md transition-colors disabled:opacity-50">
                {{ creating ? 'Adicionando...' : 'Adicionar Talhão' }}
              </button>
            </div>

            <div v-else-if="selectedTable === 'tipos_sensor'" class="space-y-3">
              <input
                v-model="formData.nome_tipo_sensor"
                placeholder="Nome do Tipo de Sensor (ex: Temperatura)"
                class="w-full px-3 py-2 border border-gray-300 rounded-md"
              />
              <input
                v-model="formData.unidade_medida_padrao"
                placeholder="Unidade de Medida (ex: °C, %, ppm)"
                class="w-full px-3 py-2 border border-gray-300 rounded-md"
              />
              <button @click="createRecord" :disabled="creating" class="w-full bg-blue-600 hover:bg-blue-700 text-white font-medium py-2 rounded-md transition-colors disabled:opacity-50">
                {{ creating ? 'Adicionando...' : 'Adicionar Tipo de Sensor' }}
              </button>
            </div>

            <div v-else-if="selectedTable === 'sensores'" class="space-y-3">
              <input
                v-model="formData.identificacao_fabricante"
                placeholder="Identificação do Fabricante (ex: ESP32-001)"
                class="w-full px-3 py-2 border border-gray-300 rounded-md"
              />
              <input
                v-model="formData.data_instalacao"
                type="date"
                class="w-full px-3 py-2 border border-gray-300 rounded-md"
              />
              <select
                v-model="formData.id_tipo_sensor"
                class="w-full px-3 py-2 border border-gray-300 rounded-md"
              >
                <option :value="null">Selecione o tipo de sensor</option>
                <option v-for="tipo in tiposSensor" :key="tipo.id_tipo_sensor" :value="tipo.id_tipo_sensor">
                  {{ tipo.nome_tipo_sensor }} ({{ tipo.unidade_medida_padrao }})
                </option>
              </select>
              <select
                v-model="formData.id_talhao"
                class="w-full px-3 py-2 border border-gray-300 rounded-md"
              >
                <option :value="null">Selecione o talhão</option>
                <option v-for="talhao in talhoes" :key="talhao.id_talhao" :value="talhao.id_talhao">
                  {{ talhao.nome_talhao }} ({{ talhao.area_hectares }}ha)
                </option>
              </select>
              <button @click="createRecord" :disabled="creating" class="w-full bg-blue-600 hover:bg-blue-700 text-white font-medium py-2 rounded-md transition-colors disabled:opacity-50">
                {{ creating ? 'Adicionando...' : 'Adicionar Sensor' }}
              </button>
            </div>

            <div v-else class="text-center text-gray-500 py-4">
              Esta tabela não permite criação via interface genérica.
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

          <!-- Records Table -->
          <div v-else class="overflow-x-auto">
            <table class="w-full text-sm">
              <thead class="bg-gray-100 border-b">
                <tr>
                  <th v-for="col in columns" :key="col" class="px-4 py-2 text-left">{{ col }}</th>
                  <th class="px-4 py-2 text-left">Ações</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="(row, idx) in tableData" :key="idx" class="border-b hover:bg-gray-50">
                  <td v-for="col in columns" :key="col" class="px-4 py-2 whitespace-nowrap max-w-xs truncate">
                    {{ formatValue(row[col]) }}
                  </td>
                  <td class="px-4 py-2">
                    <button @click="deleteRecord(row)" class="text-red-600 hover:text-red-700 font-medium">
                      Deletar
                    </button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>

          <!-- Pagination Info -->
          <div class="mt-4 text-sm text-gray-500">
            <span>Mostrando {{ tableData.length }} de {{ totalRecords }} registros</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'

const config = useRuntimeConfig()
const apiBase = config.public.apiBase

// Tables that allow creation via generic interface
const allowedCreateTables = ['culturas', 'talhoes', 'tipos_sensor', 'sensores']

// State
const availableTables = ref<string[]>([])
const selectedTable = ref('culturas')
const tableData = ref<any[]>([])
const columns = ref<string[]>([])
const totalRecords = ref(0)
const loading = ref(false)
const loadingTables = ref(false)
const creating = ref(false)
const error = ref('')
const success = ref('')

// Form data - dynamic based on selected table
const formData = ref<any>({})

// Related data for foreign keys
const culturas = ref<any[]>([])
const talhoes = ref<any[]>([])
const tiposSensor = ref<any[]>([])

// Format table name for display
const formatTableName = (name: string) => {
  return name.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())
}

// Format cell value
const formatValue = (val: any) => {
  if (val === null || val === undefined) return '-'
  if (typeof val === 'boolean') return val ? 'Sim' : 'Não'
  return val
}

// Clear messages after 5 seconds
const clearMessages = () => {
  setTimeout(() => {
    error.value = ''
    success.value = ''
  }, 5000)
}

// Fetch available tables
const fetchTables = async () => {
  loadingTables.value = true
  error.value = ''
  try {
    const data = await $fetch<string[]>(`${apiBase}/database/tables`)
    // Filter to only show tables that allow creation
    availableTables.value = data.filter(t => allowedCreateTables.includes(t))
    if (availableTables.value.length > 0 && availableTables.value[0]) {
      selectedTable.value = availableTables.value[0] as string
      await fetchData()
    }
  } catch (e) {
    console.error('Failed to fetch tables', e)
    error.value = 'Erro ao carregar tabelas: ' + (e instanceof Error ? e.message : String(e))
    clearMessages()
  } finally {
    loadingTables.value = false
  }
}

// Fetch data for selected table
const fetchData = async () => {
  if (!selectedTable.value) return

  loading.value = true
  error.value = ''
  try {
    const data = await $fetch<any>(`${apiBase}/database/data/${selectedTable.value}`)
    if (data) {
      columns.value = data.columns
      tableData.value = data.data
      totalRecords.value = data.total
    }
  } catch (e) {
    console.error('Failed to fetch data', e)
    error.value = 'Erro ao carregar dados: ' + (e instanceof Error ? e.message : String(e))
    clearMessages()
  } finally {
    loading.value = false
  }
}

// Fetch related data for foreign keys
const fetchRelatedData = async () => {
  try {
    const [culturasData, talhoesData, tiposData] = await Promise.all([
      $fetch<any>(`${apiBase}/database/data/culturas`),
      $fetch<any>(`${apiBase}/database/data/talhoes`),
      $fetch<any>(`${apiBase}/database/data/tipos_sensor`)
    ])

    culturas.value = culturasData.data
    talhoes.value = talhoesData.data
    tiposSensor.value = tiposData.data
  } catch (e) {
    console.error('Failed to fetch related data', e)
  }
}

// Select table and refresh data
const selectTable = async (table: string) => {
  selectedTable.value = table
  formData.value = {}
  await fetchData()
}

// Refresh data
const refreshData = async () => {
  await fetchData()
  await fetchRelatedData()
}

// Create new record
const createRecord = async () => {
  if (creating.value) return

  error.value = ''
  success.value = ''
  creating.value = true

  try {
    // Validate required fields based on table
    if (selectedTable.value === 'culturas' && !formData.value.nome_cultura) {
      error.value = 'Nome da cultura é obrigatório'
      clearMessages()
      return
    }
    if (selectedTable.value === 'talhoes' && (!formData.value.nome_talhao || !formData.value.area_hectares)) {
      error.value = 'Nome do talhão e área são obrigatórios'
      clearMessages()
      return
    }
    if (selectedTable.value === 'tipos_sensor' && (!formData.value.nome_tipo_sensor || !formData.value.unidade_medida_padrao)) {
      error.value = 'Nome do tipo e unidade de medida são obrigatórios'
      clearMessages()
      return
    }
    if (selectedTable.value === 'sensores' && (!formData.value.identificacao_fabricante || !formData.value.data_instalacao || !formData.value.id_tipo_sensor || !formData.value.id_talhao)) {
      error.value = 'Todos os campos são obrigatórios para sensores'
      clearMessages()
      return
    }

    await $fetch(`${apiBase}/database/data/${selectedTable.value}`, {
      method: 'POST',
      body: formData.value
    })

    success.value = 'Registro criado com sucesso!'
    clearMessages()
    formData.value = {}
    await fetchData()
  } catch (e) {
    console.error('Failed to create record', e)
    error.value = 'Erro ao criar registro: ' + (e instanceof Error ? e.message : String(e))
    clearMessages()
  } finally {
    creating.value = false
  }
}

// Delete record
const deleteRecord = async (row: any) => {
  if (!confirm('Tem certeza que deseja excluir este registro?')) return

  error.value = ''
  success.value = ''

  try {
    // Find the primary key column (usually first column or contains 'id_')
    const idCol = columns.value.find(c => c.startsWith('id_')) || columns.value[0]
    if (!idCol) return
    const id = row[idCol]

    await $fetch(`${apiBase}/database/data/${selectedTable.value}/${id}`, {
      method: 'DELETE'
    })

    success.value = 'Registro deletado com sucesso!'
    clearMessages()
    await fetchData()
  } catch (e) {
    console.error('Failed to delete record', e)
    error.value = 'Erro ao deletar registro: ' + (e instanceof Error ? e.message : String(e))
    clearMessages()
  }
}

// Initialize
onMounted(async () => {
  await fetchTables()
  await fetchRelatedData()
})
</script>
