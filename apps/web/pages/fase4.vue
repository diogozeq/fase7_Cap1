<template>
  <div class="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-50 p-4 md:p-8">
    <div class="max-w-7xl mx-auto">
      <!-- Header -->
      <div class="mb-8">
        <NuxtLink to="/" class="text-blue-600 hover:text-blue-700 mb-4 inline-flex items-center gap-2 transition-colors">
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18"/>
          </svg>
          Voltar
        </NuxtLink>
        <div class="flex items-center justify-between">
          <div>
            <h1 class="text-4xl font-bold text-gray-800 mb-2">Fase 4: Analytics & IA</h1>
            <p class="text-gray-600">Dashboard Inteligente com Simulação de Cenários e Insights Preditivos</p>
          </div>
          <div class="hidden md:flex items-center gap-3">
            <div class="px-4 py-2 bg-green-100 text-green-800 rounded-lg font-semibold text-sm">
              {{ totalRecords }} registros
            </div>
            <div v-if="totalAlerts > 0" class="px-4 py-2 bg-red-100 text-red-800 rounded-lg font-semibold text-sm animate-pulse">
              {{ totalAlerts }} alertas
            </div>
          </div>
        </div>
      </div>

      <!-- Alertas Proativos -->
      <div v-if="alerts.length > 0" class="mb-6">
        <div class="bg-white rounded-xl shadow-lg p-6 border-l-4" :class="getAlertBorderClass(alerts[0].level)">
          <div class="flex items-start gap-4">
            <div class="flex-shrink-0">
              <svg v-if="alerts[0].level === 'critical'" class="w-8 h-8 text-red-500" fill="currentColor" viewBox="0 0 20 20">
                <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd"/>
              </svg>
              <svg v-else-if="alerts[0].level === 'warning'" class="w-8 h-8 text-yellow-500" fill="currentColor" viewBox="0 0 20 20">
                <path fill-rule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clip-rule="evenodd"/>
              </svg>
              <svg v-else class="w-8 h-8 text-blue-500" fill="currentColor" viewBox="0 0 20 20">
                <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clip-rule="evenodd"/>
              </svg>
            </div>
            <div class="flex-1">
              <h3 class="text-lg font-bold text-gray-800 mb-1">{{ alerts[0].message }}</h3>
              <p class="text-gray-600 text-sm mb-3">{{ getAlertDescription(alerts[0]) }}</p>
              <div class="flex flex-wrap gap-2">
                <span v-for="(rec, idx) in recommendations.slice(0, 2)" :key="idx"
                  class="px-3 py-1 bg-blue-50 text-blue-700 rounded-full text-xs font-medium">
                  {{ rec.action }}
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Grid Principal -->
      <div class="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-6">
        <!-- What-If Simulator -->
        <div class="lg:col-span-2 bg-white rounded-xl shadow-lg p-6">
          <div class="flex items-center justify-between mb-6">
            <h2 class="text-2xl font-bold text-gray-800 flex items-center gap-2">
              <svg class="w-6 h-6 text-indigo-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 7h6m0 10v-3m-3 3h.01M9 17h.01M9 14h.01M12 14h.01M15 11h.01M12 11h.01M9 11h.01M7 21h10a2 2 0 002-2V5a2 2 0 00-2-2H7a2 2 0 00-2 2v14a2 2 0 002 2z"/>
              </svg>
              Simulador "What-If"
            </h2>
            <button @click="resetSimulation" class="px-4 py-2 text-sm bg-gray-100 hover:bg-gray-200 text-gray-700 rounded-lg transition-colors">
              Resetar
            </button>
          </div>

          <!-- Controles do Simulador -->
          <div class="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
            <div>
              <label class="block text-sm font-semibold text-gray-700 mb-2">Umidade (%)</label>
              <input
                v-model.number="whatIfParams.umidade"
                type="range"
                min="0"
                max="100"
                step="1"
                class="w-full h-2 bg-blue-200 rounded-lg appearance-none cursor-pointer"
                @input="runWhatIfSimulation"
              />
              <div class="flex justify-between items-center mt-2">
                <span class="text-xs text-gray-500">0%</span>
                <span class="text-lg font-bold text-blue-600">{{ whatIfParams.umidade }}%</span>
                <span class="text-xs text-gray-500">100%</span>
              </div>
            </div>

            <div>
              <label class="block text-sm font-semibold text-gray-700 mb-2">pH</label>
              <input
                v-model.number="whatIfParams.ph"
                type="range"
                min="0"
                max="14"
                step="0.1"
                class="w-full h-2 bg-green-200 rounded-lg appearance-none cursor-pointer"
                @input="runWhatIfSimulation"
              />
              <div class="flex justify-between items-center mt-2">
                <span class="text-xs text-gray-500">0</span>
                <span class="text-lg font-bold text-green-600">{{ whatIfParams.ph.toFixed(1) }}</span>
                <span class="text-xs text-gray-500">14</span>
              </div>
            </div>

            <div>
              <label class="block text-sm font-semibold text-gray-700 mb-2">Temperatura (°C)</label>
              <input
                v-model.number="whatIfParams.temperatura"
                type="range"
                min="-10"
                max="50"
                step="0.5"
                class="w-full h-2 bg-orange-200 rounded-lg appearance-none cursor-pointer"
                @input="runWhatIfSimulation"
              />
              <div class="flex justify-between items-center mt-2">
                <span class="text-xs text-gray-500">-10°C</span>
                <span class="text-lg font-bold text-orange-600">{{ whatIfParams.temperatura }}°C</span>
                <span class="text-xs text-gray-500">50°C</span>
              </div>
            </div>
          </div>

          <!-- Resultados da Simulação -->
          <div v-if="whatIfResults" class="space-y-4">
            <div class="bg-gradient-to-r from-indigo-50 to-blue-50 rounded-lg p-4">
              <h3 class="font-bold text-gray-800 mb-3 flex items-center gap-2">
                <svg class="w-5 h-5 text-indigo-600" fill="currentColor" viewBox="0 0 20 20">
                  <path fill-rule="evenodd" d="M6 2a1 1 0 00-1 1v1H4a2 2 0 00-2 2v10a2 2 0 002 2h12a2 2 0 002-2V6a2 2 0 00-2-2h-1V3a1 1 0 10-2 0v1H7V3a1 1 0 00-1-1zm0 5a1 1 0 000 2h8a1 1 0 100-2H6z" clip-rule="evenodd"/>
                </svg>
                Análise de Impacto
              </h3>
              <div class="grid grid-cols-1 md:grid-cols-3 gap-3">
                <div v-for="impact in whatIfResults.impact_analysis" :key="impact.variable"
                  class="bg-white rounded-lg p-3 border-l-4"
                  :class="getImpactBorderClass(impact.delta)">
                  <p class="text-xs text-gray-500 uppercase">{{ impact.variable }}</p>
                  <p class="text-2xl font-bold" :class="getDeltaColorClass(impact.delta)">
                    {{ impact.delta > 0 ? '+' : '' }}{{ impact.delta }}
                  </p>
                  <p class="text-xs text-gray-600 mt-1">{{ impact.impact }}</p>
                  <p class="text-xs text-gray-400 mt-1">Base: {{ impact.baseline }}</p>
                </div>
              </div>
            </div>

            <!-- Classificação de Risco -->
            <div class="grid grid-cols-2 gap-4">
              <div class="bg-white border-2 rounded-lg p-4" :class="getRiskBorderClass(whatIfResults.risk_classification.baseline)">
                <p class="text-xs text-gray-500 uppercase mb-1">Risco Atual (Baseline)</p>
                <p class="text-xl font-bold" :class="getRiskColorClass(whatIfResults.risk_classification.baseline)">
                  {{ whatIfResults.risk_classification.baseline }}
                </p>
              </div>
              <div class="bg-white border-2 rounded-lg p-4" :class="getRiskBorderClass(whatIfResults.risk_classification.adjusted)">
                <p class="text-xs text-gray-500 uppercase mb-1">Risco Simulado</p>
                <p class="text-xl font-bold" :class="getRiskColorClass(whatIfResults.risk_classification.adjusted)">
                  {{ whatIfResults.risk_classification.adjusted }}
                  <span v-if="whatIfResults.risk_classification.changed" class="text-sm ml-2">⚠️</span>
                </p>
              </div>
            </div>

            <!-- Previsão Comparativa -->
            <div class="bg-white rounded-lg p-4 border border-gray-200">
              <h4 class="font-semibold text-gray-800 mb-3">Previsão de Umidade (7 dias)</h4>
              <div class="grid grid-cols-2 gap-4">
                <div>
                  <p class="text-xs text-gray-500 mb-2">Baseline</p>
                  <p class="text-3xl font-bold text-blue-600">{{ whatIfResults.forecasts.baseline.next_week_avg }}%</p>
                </div>
                <div>
                  <p class="text-xs text-gray-500 mb-2">Simulado</p>
                  <p class="text-3xl font-bold text-indigo-600">{{ whatIfResults.forecasts.adjusted.next_week_avg }}%</p>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Previsões ARIMA -->
        <div class="bg-gradient-to-br from-blue-600 to-indigo-600 rounded-xl shadow-lg p-6 text-white">
          <h2 class="text-xl font-bold mb-4 flex items-center gap-2">
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"/>
            </svg>
            Previsões ARIMA
          </h2>
          <div class="space-y-4">
            <div class="bg-white bg-opacity-20 backdrop-blur-sm rounded-lg p-4">
              <p class="text-sm opacity-90 mb-1">Próxima Semana</p>
              <p class="text-4xl font-bold">{{ predictions.nextWeek }}%</p>
              <p class="text-xs opacity-75 mt-1">Umidade prevista</p>
            </div>
            <div class="bg-white bg-opacity-20 backdrop-blur-sm rounded-lg p-4">
              <p class="text-sm opacity-90 mb-1">Próximo Mês</p>
              <p class="text-4xl font-bold">{{ predictions.nextMonth }}%</p>
              <p class="text-xs opacity-75 mt-1">Tendência futura</p>
            </div>
            <div class="bg-white bg-opacity-20 backdrop-blur-sm rounded-lg p-4">
              <p class="text-sm opacity-90 mb-1">Confiança</p>
              <div class="flex items-end gap-2">
                <p class="text-4xl font-bold">{{ predictions.confidence }}%</p>
                <div class="flex-1">
                  <div class="w-full bg-white bg-opacity-30 rounded-full h-2">
                    <div class="bg-white h-2 rounded-full transition-all" :style="{ width: predictions.confidence + '%' }"></div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Clusterização Interativa -->
      <div class="bg-white rounded-xl shadow-lg p-6 mb-6">
        <h2 class="text-2xl font-bold text-gray-800 mb-6 flex items-center gap-2">
          <svg class="w-6 h-6 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 12l3-3 3 3 4-4M8 21l4-4 4 4M3 4h18M4 4h16v12a1 1 0 01-1 1H5a1 1 0 01-1-1V4z"/>
          </svg>
          Mapa de Clusterização Dinâmico
        </h2>

        <div v-if="clusterInsights.length > 0" class="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div
            v-for="cluster in clusterInsights"
            :key="cluster.id"
            @click="selectedCluster = selectedCluster === cluster.id ? null : cluster.id"
            class="cursor-pointer rounded-xl p-5 transition-all duration-300 transform hover:scale-105"
            :class="selectedCluster === cluster.id ? 'ring-4 ring-offset-2' : 'hover:shadow-xl'"
            :style="{
              backgroundColor: getClusterColor(cluster.id) + '15',
              borderLeft: `6px solid ${getClusterColor(cluster.id)}`
            }">

            <div class="flex items-center justify-between mb-3">
              <h3 class="text-lg font-bold text-gray-800">{{ cluster.name }}</h3>
              <span class="px-3 py-1 bg-white rounded-full text-sm font-semibold" :style="{ color: getClusterColor(cluster.id) }">
                {{ cluster.size }} registros
              </span>
            </div>

            <p class="text-sm text-gray-600 mb-4">{{ cluster.description }}</p>

            <!-- Características -->
            <div class="flex flex-wrap gap-2 mb-4">
              <span
                v-for="char in cluster.characteristics"
                :key="char"
                class="px-2 py-1 bg-white rounded-md text-xs font-medium text-gray-700 border">
                {{ char }}
              </span>
            </div>

            <!-- Centróide -->
            <div class="grid grid-cols-3 gap-2 mb-4 p-3 bg-white rounded-lg">
              <div>
                <p class="text-xs text-gray-500">Umidade</p>
                <p class="text-sm font-bold text-blue-600">{{ cluster.center.umidade }}%</p>
              </div>
              <div>
                <p class="text-xs text-gray-500">pH</p>
                <p class="text-sm font-bold text-green-600">{{ cluster.center.ph }}</p>
              </div>
              <div>
                <p class="text-xs text-gray-500">Temp</p>
                <p class="text-sm font-bold text-orange-600">{{ cluster.center.temperatura }}°C</p>
              </div>
            </div>

            <!-- Recomendações (expandido) -->
            <div v-if="selectedCluster === cluster.id" class="mt-4 space-y-2 animate-fadeIn">
              <div class="border-t pt-3">
                <h4 class="font-semibold text-gray-800 mb-2 text-sm">Recomendações:</h4>
                <ul class="space-y-2">
                  <li v-for="(rec, idx) in cluster.recommendations" :key="idx" class="flex items-start gap-2 text-sm">
                    <svg class="w-4 h-4 text-green-500 mt-0.5 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                      <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd"/>
                    </svg>
                    <span class="text-gray-700">{{ rec }}</span>
                  </li>
                </ul>
              </div>

              <!-- Amostra de Registros -->
              <div v-if="cluster.sample_records && cluster.sample_records.length > 0" class="border-t pt-3">
                <h4 class="font-semibold text-gray-800 mb-2 text-sm">Registros Recentes:</h4>
                <div class="space-y-1 max-h-40 overflow-y-auto">
                  <div v-for="(record, idx) in cluster.sample_records" :key="idx"
                    class="text-xs bg-white p-2 rounded border border-gray-200">
                    <div class="flex justify-between">
                      <span class="text-gray-500">ID: {{ record.id }}</span>
                      <span class="text-gray-400">{{ formatDate(record.timestamp) }}</span>
                    </div>
                    <div class="flex gap-3 mt-1 text-gray-700">
                      <span>U: {{ record.umidade }}%</span>
                      <span>pH: {{ record.ph }}</span>
                      <span>T: {{ record.temperatura }}°C</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <div v-else class="text-center">
              <button class="text-sm text-blue-600 hover:text-blue-700 font-medium">
                Clique para ver detalhes
              </button>
            </div>
          </div>
        </div>
        <div v-else class="text-center py-8 text-gray-500">
          <p>Dados insuficientes para clusterização</p>
        </div>
      </div>

      <!-- Modelos ML e Recomendações -->
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <!-- Comparação de Modelos -->
        <div class="bg-white rounded-xl shadow-lg p-6">
          <h2 class="text-xl font-bold text-gray-800 mb-4 flex items-center gap-2">
            <svg class="w-6 h-6 text-teal-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z"/>
            </svg>
            Modelos de ML
          </h2>
          <div class="space-y-3">
            <div v-for="model in models" :key="model.name"
              class="p-4 bg-gradient-to-r from-gray-50 to-white rounded-lg border border-gray-200 hover:shadow-md transition-shadow">
              <div class="flex justify-between items-center mb-2">
                <div>
                  <span class="font-semibold text-gray-800">{{ model.name }}</span>
                  <p v-if="model.type" class="text-xs text-gray-500 mt-1">{{ model.type }}</p>
                </div>
                <span class="text-2xl font-bold text-teal-600">{{ model.accuracy }}%</span>
              </div>
              <div class="w-full bg-gray-200 rounded-full h-3 overflow-hidden">
                <div
                  class="h-3 rounded-full transition-all duration-1000 ease-out"
                  :class="model.accuracy > 80 ? 'bg-gradient-to-r from-teal-500 to-emerald-500' : 'bg-gradient-to-r from-yellow-500 to-orange-500'"
                  :style="{ width: model.accuracy + '%' }">
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Recomendações Personalizadas -->
        <div class="bg-gradient-to-br from-purple-600 to-pink-600 rounded-xl shadow-lg p-6 text-white">
          <h2 class="text-xl font-bold mb-4 flex items-center gap-2">
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z"/>
            </svg>
            Recomendações Inteligentes
          </h2>
          <div class="space-y-3">
            <div v-for="(rec, idx) in recommendations" :key="idx"
              class="bg-white bg-opacity-20 backdrop-blur-sm rounded-lg p-4 hover:bg-opacity-30 transition-all">
              <div class="flex items-start gap-3">
                <span class="flex-shrink-0 px-2 py-1 bg-white bg-opacity-30 rounded text-xs font-bold uppercase">
                  {{ rec.priority }}
                </span>
                <div class="flex-1">
                  <p class="font-semibold mb-1">{{ rec.action }}</p>
                  <p class="text-sm opacity-90">{{ rec.reason }}</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'

const config = useRuntimeConfig()
const apiBase = config.public.apiBase.replace(/\/$/, '')

// State
const models = ref<{ name: string; accuracy: number; type?: string }[]>([])
const predictions = ref<{ nextWeek: number; nextMonth: number; confidence: number }>({
  nextWeek: 0,
  nextMonth: 0,
  confidence: 0
})
const clusterInsights = ref<any[]>([])
const selectedCluster = ref<number | null>(null)
const alerts = ref<any[]>([])
const recommendations = ref<any[]>([])
const totalAlerts = ref(0)
const totalRecords = ref(0)

// What-If Simulator
const whatIfParams = ref({
  umidade: 60,
  ph: 7.0,
  temperatura: 20
})
const whatIfResults = ref<any>(null)
const whatIfTimeout = ref<any>(null)

// Cores para clusters
const clusterColors = ['#10b981', '#3b82f6', '#ef4444', '#f59e0b', '#8b5cf6', '#ec4899']

const getClusterColor = (id: number) => clusterColors[id % clusterColors.length]

const getAlertBorderClass = (level: string) => {
  if (level === 'critical') return 'border-red-500'
  if (level === 'warning') return 'border-yellow-500'
  return 'border-blue-500'
}

const getAlertDescription = (alert: any) => {
  if (alert.value) {
    return `Valor atual: ${alert.value}${alert.type.includes('umidade') ? '%' : ''}`
  }
  return ''
}

const getImpactBorderClass = (delta: number) => {
  if (delta > 10) return 'border-red-500'
  if (delta < -10) return 'border-blue-500'
  return 'border-gray-300'
}

const getDeltaColorClass = (delta: number) => {
  if (delta > 10) return 'text-red-600'
  if (delta < -10) return 'text-blue-600'
  return 'text-gray-600'
}

const getRiskBorderClass = (risk: string) => {
  if (risk === 'Alto') return 'border-red-500'
  if (risk === 'Médio') return 'border-yellow-500'
  return 'border-green-500'
}

const getRiskColorClass = (risk: string) => {
  if (risk === 'Alto') return 'text-red-600'
  if (risk === 'Médio') return 'text-yellow-600'
  return 'text-green-600'
}

const formatDate = (dateStr: string) => {
  if (!dateStr) return 'N/A'
  try {
    const date = new Date(dateStr)
    return date.toLocaleString('pt-BR', {
      day: '2-digit',
      month: '2-digit',
      hour: '2-digit',
      minute: '2-digit'
    })
  } catch {
    return 'N/A'
  }
}

const loadModels = async () => {
  try {
    const data = await $fetch<{ models: any[] }>(`${apiBase}/ml/models`)
    models.value = (data.models || []).map((m, idx) => ({
      name: m.name || `Modelo ${idx + 1}`,
      accuracy: m.metric && m.metric <= 1 ? Math.round(m.metric * 100) : Math.round(m.metric || 0),
      type: m.type
    }))
    if (!models.value.length) {
      models.value = [{ name: 'Sem modelos', accuracy: 0 }]
    }
  } catch (e) {
    console.error('load_models_failed', e)
    models.value = [{ name: 'Falha ao carregar', accuracy: 0 }]
  }
}

const loadForecast = async () => {
  try {
    const data = await $fetch<any>(`${apiBase}/ml/forecast?steps=8`)
    const preds = data?.predictions || []
    predictions.value = {
      nextWeek: preds[0] ? Math.round(preds[0]) : 0,
      nextMonth: preds[3] ? Math.round(preds[3]) : 0,
      confidence: data?.confidence_intervals?.length ? 90 : 80
    }
  } catch (e) {
    console.error('load_forecast_failed', e)
    predictions.value = { nextWeek: 0, nextMonth: 0, confidence: 0 }
  }
}

const loadClusterInsights = async () => {
  try {
    const data = await $fetch<any>(`${apiBase}/ml/clusters/insights?n_clusters=3`)
    clusterInsights.value = data?.clusters || []
    totalRecords.value = data?.total_records || 0
  } catch (e) {
    console.error('load_clusters_insights_failed', e)
    clusterInsights.value = []
  }
}

const loadAlerts = async () => {
  try {
    const data = await $fetch<any>(`${apiBase}/ml/alerts`)
    alerts.value = data?.alerts || []
    recommendations.value = data?.recommendations || []
    totalAlerts.value = data?.total_alerts || 0
  } catch (e) {
    console.error('load_alerts_failed', e)
    alerts.value = []
    recommendations.value = []
  }
}

const runWhatIfSimulation = () => {
  // Debounce para não fazer muitas requisições
  if (whatIfTimeout.value) {
    clearTimeout(whatIfTimeout.value)
  }

  whatIfTimeout.value = setTimeout(async () => {
    try {
      const data = await $fetch<any>(`${apiBase}/ml/whatif`, {
        method: 'POST',
        body: {
          umidade: whatIfParams.value.umidade,
          ph: whatIfParams.value.ph,
          temperatura: whatIfParams.value.temperatura
        }
      })
      whatIfResults.value = data
    } catch (e) {
      console.error('whatif_simulation_failed', e)
      whatIfResults.value = null
    }
  }, 500)
}

const resetSimulation = async () => {
  // Reset para valores médios do banco
  try {
    const data = await $fetch<any>(`${apiBase}/ml/whatif`, {
      method: 'POST',
      body: {}
    })

    if (data?.baseline) {
      whatIfParams.value = {
        umidade: Math.round(data.baseline.umidade),
        ph: parseFloat(data.baseline.ph.toFixed(1)),
        temperatura: Math.round(data.baseline.temperatura)
      }
    }
    whatIfResults.value = data
  } catch (e) {
    console.error('reset_simulation_failed', e)
  }
}

onMounted(() => {
  loadModels()
  loadForecast()
  loadClusterInsights()
  loadAlerts()
  resetSimulation() // Inicializar o simulador com valores baseline
})
</script>

<style scoped>
@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.animate-fadeIn {
  animation: fadeIn 0.3s ease-out;
}

/* Custom range slider styling */
input[type="range"]::-webkit-slider-thumb {
  appearance: none;
  width: 20px;
  height: 20px;
  border-radius: 50%;
  background: white;
  cursor: pointer;
  box-shadow: 0 2px 6px rgba(0,0,0,0.3);
  border: 3px solid currentColor;
}

input[type="range"]::-moz-range-thumb {
  width: 20px;
  height: 20px;
  border-radius: 50%;
  background: white;
  cursor: pointer;
  box-shadow: 0 2px 6px rgba(0,0,0,0.3);
  border: 3px solid currentColor;
}
</style>
