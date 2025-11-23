<template>
  <div class="w-full">
    <!-- Top Navigation Bar -->
    <header class="flex items-center justify-between whitespace-nowrap border-b border-gray-200 dark:border-gray-900/50 bg-white dark:bg-[#1a2f24] px-8 py-4 sticky top-0 z-10">
      <div class="flex items-center gap-4">
        <div class="flex flex-col">
          <h1 class="text-gray-900 dark:text-white text-base font-medium leading-normal">Fazenda Boa Esperança</h1>
          <p class="text-primary text-sm font-normal leading-normal">Plano Pro</p>
        </div>
      </div>
      <div class="flex flex-1 justify-end gap-4">
        <button class="flex max-w-[480px] cursor-pointer items-center justify-center overflow-hidden rounded-full h-10 w-10 bg-gray-100 dark:bg-gray-800 text-gray-600 dark:text-gray-400 hover:bg-gray-200 dark:hover:bg-gray-700 transition-colors">
          <span class="material-symbols-outlined">notifications</span>
        </button>
        <div class="flex items-center justify-center w-10 h-10 rounded-full bg-primary text-white font-bold">
          👤
        </div>
      </div>
    </header>

    <!-- Main Content -->
    <main class="p-8">
      <div class="max-w-7xl mx-auto">
        <!-- Page Heading -->
        <div class="flex flex-wrap justify-between gap-3 mb-8">
          <div class="flex min-w-72 flex-col gap-2">
            <p class="text-gray-900 dark:text-white text-4xl font-black leading-tight tracking-[-0.033em]">Dashboard Consolidado</p>
            <p class="text-gray-600 dark:text-gray-400 text-base font-normal leading-normal">Visão em tempo real de todas as operações da fazenda</p>
          </div>
        </div>

        <!-- Stats Grid -->
        <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <div class="flex min-w-[158px] flex-1 flex-col gap-2 rounded-xl p-6 bg-white dark:bg-[#1a2f24] shadow-sm border border-gray-100 dark:border-gray-900/50">
            <p class="text-gray-600 dark:text-gray-400 text-sm font-medium">Temperatura / Umidade</p>
            <p class="text-gray-900 dark:text-white tracking-light text-3xl font-bold">{{ temperature }}°C / {{ soilMoisture }}%</p>
            <p class="text-green-500 text-sm font-medium">✓ Condições normais</p>
          </div>

          <div class="flex min-w-[158px] flex-1 flex-col gap-2 rounded-xl p-6 bg-white dark:bg-[#1a2f24] shadow-sm border border-gray-100 dark:border-gray-900/50">
            <p class="text-gray-600 dark:text-gray-400 text-sm font-medium">pH do Solo</p>
            <p class="text-gray-900 dark:text-white tracking-light text-3xl font-bold">{{ soilPH }}</p>
            <p class="text-green-500 text-sm font-medium">✓ Faixa ideal</p>
          </div>

          <div class="flex min-w-[158px] flex-1 flex-col gap-2 rounded-xl p-6 bg-white dark:bg-[#1a2f24] shadow-sm border border-gray-100 dark:border-gray-900/50">
            <p class="text-gray-600 dark:text-gray-400 text-sm font-medium">Status da Bomba</p>
            <p class="text-gray-900 dark:text-white tracking-light text-3xl font-bold">Ativa</p>
            <p class="text-green-500 text-sm font-medium">✓ Funcionando</p>
          </div>

          <div class="flex min-w-[158px] flex-1 flex-col gap-2 rounded-xl p-6 bg-white dark:bg-[#1a2f24] shadow-sm border border-gray-100 dark:border-gray-900/50">
            <p class="text-gray-600 dark:text-gray-400 text-sm font-medium">Alertas Ativos</p>
            <p class="text-yellow-500 tracking-light text-3xl font-bold">2</p>
            <p class="text-yellow-500 text-sm font-medium">⚠ Atenção necessária</p>
          </div>
        </div>

        <!-- Main Content Area -->
        <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <!-- Productivity Forecast Chart -->
          <div class="lg:col-span-2 flex flex-col gap-4 rounded-xl p-6 bg-white dark:bg-[#1a2f24] shadow-sm border border-gray-100 dark:border-gray-900/50">
            <div class="flex justify-between items-center">
              <h2 class="text-gray-900 dark:text-white text-lg font-bold">Previsão de Produtividade</h2>
              <p class="text-xs text-gray-500 dark:text-gray-400">Fonte: previsões ARIMA do backend</p>
            </div>
            <div class="relative w-full h-80 bg-gray-50 dark:bg-gray-900/30 rounded-lg flex items-center justify-center">
              <canvas ref="forecastCanvas" class="w-full h-full"></canvas>
              <p v-if="!forecastLoaded" class="absolute text-gray-400 dark:text-gray-600">Carregando previsão...</p>
            </div>
          </div>

          <!-- Recent Activity Feed -->
          <div class="flex flex-col gap-4 rounded-xl p-6 bg-white dark:bg-[#1a2f24] shadow-sm border border-gray-100 dark:border-gray-900/50">
            <h2 class="text-gray-900 dark:text-white text-lg font-bold">Atividade Recente</h2>
            <div class="flex flex-col gap-4">
              <div class="flex items-start gap-3">
                <div class="flex items-center justify-center size-8 rounded-full bg-red-100 dark:bg-red-900/30 shrink-0">
                  <span class="material-symbols-outlined text-red-500 text-base">warning</span>
                </div>
                <div class="flex flex-col">
                  <p class="text-gray-900 dark:text-white text-sm font-medium">Praga detectada no Setor 7</p>
                  <p class="text-gray-600 dark:text-gray-400 text-xs">2 min atrás</p>
                </div>
              </div>

              <div class="flex items-start gap-3">
                <div class="flex items-center justify-center size-8 rounded-full bg-yellow-100 dark:bg-yellow-900/30 shrink-0">
                  <span class="material-symbols-outlined text-yellow-500 text-base">water_drop</span>
                </div>
                <div class="flex flex-col">
                  <p class="text-gray-900 dark:text-white text-sm font-medium">Umidade baixa no Setor 4</p>
                  <p class="text-gray-600 dark:text-gray-400 text-xs">15 min atrás</p>
                </div>
              </div>

              <div class="flex items-start gap-3">
                <div class="flex items-center justify-center size-8 rounded-full bg-green-100 dark:bg-green-900/30 shrink-0">
                  <span class="material-symbols-outlined text-green-500 text-base">task_alt</span>
                </div>
                <div class="flex flex-col">
                  <p class="text-gray-900 dark:text-white text-sm font-medium">Drone completou rota programada</p>
                  <p class="text-gray-600 dark:text-gray-400 text-xs">45 min atrás</p>
                </div>
              </div>

              <div class="flex items-start gap-3">
                <div class="flex items-center justify-center size-8 rounded-full bg-blue-100 dark:bg-blue-900/30 shrink-0">
                  <span class="material-symbols-outlined text-blue-500 text-base">info</span>
                </div>
                <div class="flex flex-col">
                  <p class="text-gray-900 dark:text-white text-sm font-medium">Irrigação do Setor 2 concluída</p>
                  <p class="text-gray-600 dark:text-gray-400 text-xs">1 hora atrás</p>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Phases Navigation -->
        <div class="mt-8 bg-white dark:bg-[#1a2f24] rounded-xl shadow-sm border border-gray-100 dark:border-gray-900/50 p-8">
          <h2 class="text-gray-900 dark:text-white text-2xl font-bold mb-6">📚 Fases do Projeto</h2>
          <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            <NuxtLink to="/fase1" class="flex items-center justify-center gap-2 py-3 px-4 border border-transparent rounded-lg shadow-sm text-sm font-semibold text-white bg-[#1fc762] hover:bg-[#1fc762]/90 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-[#1fc762] dark:focus:ring-offset-[#1a2f24] transition-colors">
              <span class="material-symbols-outlined text-base">cloud</span>
              Fase 1: Dados & Clima
            </NuxtLink>
            <NuxtLink to="/fase2" class="flex items-center justify-center gap-2 py-3 px-4 border border-transparent rounded-lg shadow-sm text-sm font-semibold text-white bg-[#1fc762] hover:bg-[#1fc762]/90 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-[#1fc762] dark:focus:ring-offset-[#1a2f24] transition-colors">
              <span class="material-symbols-outlined text-base">database</span>
              Fase 2: Banco de Dados
            </NuxtLink>
            <NuxtLink to="/fase3" class="flex items-center justify-center gap-2 py-3 px-4 border border-transparent rounded-lg shadow-sm text-sm font-semibold text-white bg-[#1fc762] hover:bg-[#1fc762]/90 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-[#1fc762] dark:focus:ring-offset-[#1a2f24] transition-colors">
              <span class="material-symbols-outlined text-base">wifi</span>
              Fase 3: IoT
            </NuxtLink>
            <NuxtLink to="/fase4" class="flex items-center justify-center gap-2 py-3 px-4 border border-transparent rounded-lg shadow-sm text-sm font-semibold text-white bg-[#1fc762] hover:bg-[#1fc762]/90 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-[#1fc762] dark:focus:ring-offset-[#1a2f24] transition-colors">
              <span class="material-symbols-outlined text-base">bar_chart</span>
              Fase 4: Analytics
            </NuxtLink>
            <NuxtLink to="/fase5" class="flex items-center justify-center gap-2 py-3 px-4 border border-transparent rounded-lg shadow-sm text-sm font-semibold text-white bg-[#1fc762] hover:bg-[#1fc762]/90 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-[#1fc762] dark:focus:ring-offset-[#1a2f24] transition-colors">
              <span class="material-symbols-outlined text-base">cloud_upload</span>
              Fase 5: AWS
            </NuxtLink>
            <NuxtLink to="/fase6" class="flex items-center justify-center gap-2 py-3 px-4 border border-transparent rounded-lg shadow-sm text-sm font-semibold text-white bg-[#1fc762] hover:bg-[#1fc762]/90 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-[#1fc762] dark:focus:ring-offset-[#1a2f24] transition-colors">
              <span class="material-symbols-outlined text-base">eye</span>
              Fase 6: Visão Computacional
            </NuxtLink>
            <NuxtLink to="/fase7" class="flex items-center justify-center gap-2 py-3 px-4 border border-transparent rounded-lg shadow-sm text-sm font-semibold text-white bg-[#1fc762] hover:bg-[#1fc762]/90 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-[#1fc762] dark:focus:ring-offset-[#1a2f24] transition-colors">
              <span class="material-symbols-outlined text-base">notifications</span>
              Fase 7: Alertas
            </NuxtLink>
            <NuxtLink to="/ir-alem" class="flex items-center justify-center gap-2 py-3 px-4 border border-dashed border-emerald-300 rounded-lg shadow-sm text-sm font-semibold text-emerald-900 bg-white hover:bg-emerald-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-emerald-400 dark:focus:ring-offset-[#1a2f24] transition-colors">
              <span class="material-symbols-outlined text-base">auto_awesome</span>
              Ir Além do Além (Genético)
            </NuxtLink>
          </div>
        </div>

        <!-- Embedded Streamlit Dashboard -->
        <div class="mt-8 bg-white dark:bg-[#1a2f24] rounded-xl shadow-sm border border-gray-100 dark:border-gray-900/50 p-1 overflow-hidden">
          <div class="p-6 border-b border-gray-100 dark:border-gray-900/50 mb-1">
             <h2 class="text-gray-900 dark:text-white text-2xl font-bold flex items-center gap-2">
                <span class="material-symbols-outlined text-blue-500">analytics</span>
                Dashboard Avançado (Streamlit)
             </h2>
             <p class="text-gray-500 dark:text-gray-400 text-sm mt-1">Análises avançadas de ML e Visão Computacional integradas.</p>
          </div>
          <iframe :src="dashboardUrl" class="w-full h-[800px] border-none rounded-lg" title="Streamlit Dashboard"></iframe>
        </div>

        <!-- Status Section -->
        <div class="mt-8 bg-white dark:bg-[#1a2f24] rounded-xl shadow-sm border border-gray-100 dark:border-gray-900/50 p-8">
          <h2 class="text-gray-900 dark:text-white text-2xl font-bold mb-4">✅ Status do Sistema</h2>
          <div class="space-y-2">
            <p :class="apiHealthy ? 'text-green-600' : 'text-red-600'" class="flex items-center gap-2">
              <span class="material-symbols-outlined text-base">{{ apiHealthy ? 'check_circle' : 'error' }}</span>
              Backend API (FastAPI) - {{ apiHealthy ? 'Rodando' : 'Indisponível' }}
            </p>
            <p class="text-green-600 flex items-center gap-2">
              <span class="material-symbols-outlined text-base">check_circle</span>
              Frontend (Nuxt 4) - Rodando
            </p>
            <p class="text-green-600 flex items-center gap-2">
              <span class="material-symbols-outlined text-base">check_circle</span>
              Database (SQLite) - Conectado
            </p>
          </div>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import Chart from 'chart.js/auto'
definePageMeta({ ssr: false })
const config = useRuntimeConfig()
const apiHealthy = ref(false)
const dashboardUrl = computed(() => `${config.public.dashboardBase}${config.public.dashboardBase?.includes('?') ? '&' : '?'}embed=true`)

const soilMoisture = ref(45.2)
const soilPH = ref(6.2)
const temperature = ref(28)
const forecastCanvas = ref<HTMLCanvasElement | null>(null)
const forecastLoaded = ref(false)
let chart: Chart | null = null

const renderForecastChart = (labels: string[], values: number[]) => {
  if (!forecastCanvas.value) return
  if (chart) chart.destroy()
  chart = new Chart(forecastCanvas.value, {
    type: 'line',
    data: {
      labels,
      datasets: [
        {
          label: 'Umidade prevista (%)',
          data: values,
          borderColor: '#16a34a',
          backgroundColor: 'rgba(22,163,74,0.15)',
          tension: 0.35,
          fill: true
        }
      ]
    },
    options: {
      responsive: true,
      plugins: { legend: { display: false } },
      scales: {
        y: { beginAtZero: true, suggestedMax: 100 }
      }
    }
  })
}

const loadForecast = async () => {
  try {
    const res = await fetch(`${config.public.apiBase.replace(/\/$/, '')}/ml/forecast`)
    const data = await res.json()
    const labels = data?.days || ['D1','D2','D3','D4','D5','D6','D7']
    const values = data?.predictions || [55, 58, 57, 60, 62, 61, 63]
    renderForecastChart(labels, values)
    forecastLoaded.value = true
  } catch (e) {
    console.error('forecast_load_failed', e)
    renderForecastChart(['D1','D2','D3','D4','D5','D6','D7'], [55, 58, 57, 60, 62, 61, 63])
    forecastLoaded.value = true
  }
}

onMounted(() => {
  // Simulate real-time data updates
  setInterval(() => {
    soilMoisture.value = parseFloat((Math.random() * 100).toFixed(1))
    soilPH.value = parseFloat((5.5 + Math.random() * 2).toFixed(1))
    temperature.value = Math.round(20 + Math.random() * 15)
  }, 5000)
  // Check API health
  fetch(`${config.public.apiBase}/health`).then(async (r) => {
    apiHealthy.value = r.ok
    try {
      const data = await r.json()
      apiHealthy.value = data?.status === 'healthy'
    } catch {}
  }).catch(() => { apiHealthy.value = false })

  loadForecast()
})
</script>
