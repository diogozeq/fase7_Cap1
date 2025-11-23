<template>
  <div class="min-h-screen bg-gray-50 p-8">
    <div class="max-w-7xl mx-auto">
      <NuxtLink to="/" class="text-blue-600 hover:text-blue-700 mb-6 inline-block">← Voltar</NuxtLink>
      <h1 class="text-3xl font-bold text-gray-800 mb-6">Fase 1: Dados & Clima</h1>

      <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
        <!-- Weather Data -->
        <div class="bg-white rounded-lg shadow-md p-6">
          <h2 class="text-xl font-bold mb-4">Dados Meteorológicos / Solo (reais)</h2>
          <div class="space-y-3">
            <div>
              <p class="text-gray-600 text-sm">Temperatura (última leitura)</p>
              <p class="text-2xl font-bold text-blue-600">{{ weatherData.temperature }}°C</p>
            </div>
            <div>
              <p class="text-gray-600 text-sm">Umidade do Solo</p>
              <p class="text-2xl font-bold text-blue-600">{{ weatherData.humidity }}%</p>
            </div>
            <div>
              <p class="text-gray-600 text-sm">Precipitação (CPTEC)</p>
              <p class="text-2xl font-bold text-blue-600">{{ weatherData.precipitation }}mm</p>
            </div>
          </div>
        </div>

        <!-- Crop Inputs Calculator -->
        <div class="bg-white rounded-lg shadow-md p-6">
          <h2 class="text-xl font-bold mb-4">Cálculo de Insumos</h2>
          <div class="space-y-3">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Cultura</label>
              <select v-model="selectedCrop" class="w-full px-3 py-2 border border-gray-300 rounded-md">
                <option value="milho">Milho</option>
                <option value="soja">Soja</option>
                <option value="trigo">Trigo</option>
                <option value="mandioca">Mandioca</option>
                <option value="cana">Cana de Açúcar</option>
              </select>
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Área (m²)</label>
              <input v-model.number="cropArea" type="number" class="w-full px-3 py-2 border border-gray-300 rounded-md" />
            </div>
            <button @click="calculateInputs" :disabled="loading" class="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-blue-400 text-white font-medium py-2 rounded-md transition-colors">
              {{ loading ? 'Calculando...' : 'Calcular' }}
            </button>
            <div v-if="error" class="mt-4 p-3 bg-red-50 text-red-700 rounded-md text-sm">
              {{ error }}
            </div>
            <div v-if="calculatedInputs" class="mt-4 p-3 bg-blue-50 rounded-md">
              <p class="text-sm text-gray-700"><strong>Insumo Necessário:</strong> {{ calculatedInputs.insumo_necessario }} L</p>
              <p class="text-sm text-gray-700"><strong>Custo Estimado:</strong> R$ {{ calculatedInputs.custo_estimado }}</p>
              <p class="text-xs text-gray-500 mt-2">Fonte: {{ calculatedInputs.breakdown?.fonte === 'db' ? 'Dados da Fase 1 (CSV)' : 'Padrão' }}</p>
            </div>
          </div>
        </div>
      </div>

      <!-- Production Data from CSV -->
      <div class="mt-6 bg-white rounded-lg shadow-md p-6">
        <h2 class="text-xl font-bold mb-4">Dados de Produção (CSV Fase 1)</h2>
        <div v-if="productionData.length > 0" class="overflow-x-auto">
          <table class="w-full text-sm">
            <thead class="bg-gray-100">
              <tr>
                <th class="px-4 py-2 text-left">Cultura</th>
                <th class="px-4 py-2 text-left">Área Plantada (m²)</th>
                <th class="px-4 py-2 text-left">Insumo (L)</th>
                <th class="px-4 py-2 text-left">Custo Estimado (R$)</th>
                <th class="px-4 py-2 text-left">Data</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="item in productionData" :key="item.id" class="border-b hover:bg-gray-50">
                <td class="px-4 py-2">{{ item.cultura }}</td>
                <td class="px-4 py-2">{{ item.area_plantada.toFixed(1) }}</td>
                <td class="px-4 py-2">{{ item.quantidade_produzida.toFixed(2) }}</td>
                <td class="px-4 py-2">{{ item.valor_estimado.toFixed(2) }}</td>
                <td class="px-4 py-2">{{ formatDate(item.data_colheita) }}</td>
              </tr>
            </tbody>
          </table>
          <p class="text-xs text-gray-500 mt-2">Total de registros: {{ totalProduction }}</p>
        </div>
        <div v-else class="text-gray-500 text-center py-4">
          Carregando dados...
        </div>
      </div>

      <!-- Features List -->
      <div class="mt-6 bg-white rounded-lg shadow-md p-6">
        <h2 class="text-xl font-bold mb-4">Funcionalidades</h2>
        <ul class="space-y-2">
          <li class="text-gray-700">✔ Cálculo de insumos por cultura (dados reais da Fase 1)</li>
          <li class="text-gray-700">✔ Integração com API meteorológica CPTEC</li>
          <li class="text-gray-700">✔ Dados reais do banco (umidade/temperatura)</li>
          <li class="text-gray-700">✔ Visualização de dados importados do CSV</li>
        </ul>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'

const config = useRuntimeConfig()
const apiBase = config.public.apiBase.replace(/\/$/, '')

const weatherData = reactive({
  temperature: 0,
  humidity: 0,
  precipitation: 0
})

const selectedCrop = ref('milho')
const cropArea = ref(100)
const calculatedInputs = ref<any>(null)
const loading = ref(false)
const error = ref('')
const productionData = ref<any[]>([])
const totalProduction = ref(0)

const loadWeatherAndSensors = async () => {
  try {
    const data = await $fetch<any>(`${apiBase}/analytics/overview`)
    const latest = data?.sensors?.latest
    if (latest) {
      weatherData.temperature = latest.temperatura ?? latest.temperature ?? 0
      weatherData.humidity = latest.umidade ?? 0
      weatherData.precipitation = latest.precipitacao ?? 0
    }
    const forecasts = data?.weather?.forecasts || []
    if (!weatherData.precipitation && forecasts.length) {
      weatherData.precipitation = Number(forecasts[0]?.chuvaprevista || forecasts[0]?.maxima || 0)
    }
  } catch (e) {
    console.error('load_overview_failed', e)
  }
}

const loadProductionData = async () => {
  try {
    const data = await $fetch<any>(`${apiBase}/calculations/producao-agricola?limit=10`)
    if (data) {
      productionData.value = data.data || []
      totalProduction.value = data.total || 0
    }
  } catch (e) {
    console.error('load_production_failed', e)
  }
}

const calculateInputs = async () => {
  loading.value = true
  error.value = ''
  calculatedInputs.value = null

  try {
    const data = await $fetch(`${apiBase}/calculations/insumos`, {
      method: 'POST',
      body: {
        cultura: selectedCrop.value,
        area: cropArea.value
      }
    })

    if (data) {
      calculatedInputs.value = data
    }
  } catch (e) {
    console.error(e)
    error.value = 'Falha ao calcular insumos. Verifique se o backend está rodando.'
  } finally {
    loading.value = false
  }
}

const formatDate = (dateStr: string | null) => {
  if (!dateStr) return '-'
  try {
    return new Date(dateStr).toLocaleDateString('pt-BR')
  } catch {
    return '-'
  }
}

onMounted(() => {
  loadWeatherAndSensors()
  loadProductionData()
})
</script>
