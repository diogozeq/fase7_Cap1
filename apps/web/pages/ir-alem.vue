<template>
  <div class="min-h-screen bg-gradient-to-br from-emerald-50 via-lime-50 to-amber-50">
    <div class="max-w-7xl mx-auto px-4 md:px-8 py-10 space-y-10">
      <!-- Hero -->
      <div class="flex flex-col gap-4">
        <div class="flex items-center gap-3 text-sm text-emerald-700 font-semibold">
          <NuxtLink to="/" class="inline-flex items-center gap-2 hover:translate-x-[-2px] transition-transform">
            <span class="material-symbols-outlined text-base">arrow_back</span>
            Voltar
          </NuxtLink>
          <span class="px-3 py-1 bg-white rounded-full shadow-sm border border-emerald-100">Ir Além do Além</span>
          <span class="px-3 py-1 bg-white rounded-full shadow-sm border border-emerald-100">Dados reais do SQLite</span>
        </div>
        <div class="flex flex-col lg:flex-row lg:items-start gap-6">
          <div class="flex-1 space-y-3">
            <h1 class="text-4xl md:text-5xl font-black text-emerald-950 leading-tight">
              “Ir Além” – Otimização de Recursos com Algoritmos Genéticos
            </h1>
            <p class="text-lg text-emerald-900 max-w-3xl">
              Adaptamos o algoritmo genético da fase de IA para o problema agrícola de alocação de insumos e água,
              comparando variantes de seleção/crossover/mutação e exibindo a evolução em tempo real.
              Tudo roda sobre os dados reais do banco FarmTech (Fases 1-6) e salva a entrada em arquivo para reuso.
            </p>
            <div class="flex flex-wrap gap-3">
              <span class="px-3 py-2 rounded-lg bg-white shadow border border-emerald-100 text-emerald-800 text-sm">
                Entrada persistida: <strong>{{ datasetInfo.input_file || '—' }}</strong>
              </span>
              <span class="px-3 py-2 rounded-lg bg-white shadow border border-emerald-100 text-emerald-800 text-sm">
                Gerada em: <strong>{{ datasetInfo.generated_at || '—' }}</strong>
              </span>
              <span class="px-3 py-2 rounded-lg bg-white shadow border border-emerald-100 text-emerald-800 text-sm">
                {{ datasetInfo.stats?.items || 0 }} combinações reais analisadas
              </span>
            </div>
          </div>
          <div class="w-full lg:w-80 bg-white rounded-2xl shadow-lg border border-emerald-100 p-5">
            <p class="text-xs uppercase text-emerald-600 font-semibold">Sinais do campo</p>
            <div class="mt-3 space-y-3">
              <div class="flex items-center justify-between">
                <span class="text-emerald-900 font-semibold">Umidade média</span>
                <span class="text-lg font-bold text-emerald-700">{{ datasetInfo.stats?.avg_umidade ?? 0 }}%</span>
              </div>
              <div class="flex items-center justify-between">
                <span class="text-emerald-900 font-semibold">Chuva média</span>
                <span class="text-lg font-bold text-emerald-700">{{ datasetInfo.stats?.avg_precipitacao ?? 0 }} mm</span>
              </div>
              <div class="flex items-center justify-between">
                <span class="text-emerald-900 font-semibold">Culturas</span>
                <span class="text-emerald-700 text-sm">{{ (datasetInfo.stats?.culturas || []).slice(0, 3).join(', ') }}...</span>
              </div>
              <div class="pt-3 border-t border-emerald-100">
                <p class="text-xs text-emerald-700">
                  Dados extraídos de <strong>producao_agricola</strong>, <strong>insumos_cultura</strong> e
                  leituras de sensores, garantindo contextualização real.
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Main grid -->
      <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <!-- Visualizador -->
        <div class="lg:col-span-2 bg-white rounded-2xl shadow-lg border border-emerald-100 p-6 space-y-4">
          <div class="flex items-center justify-between gap-3">
            <div>
              <p class="text-xs uppercase text-emerald-600 font-semibold">Visualizador Dinâmico</p>
              <h2 class="text-2xl font-bold text-emerald-950">Processo evolutivo em tempo real</h2>
              <p class="text-sm text-emerald-700">
                Fitness, custo de insumos e água sendo otimizados geração a geração (baseline vs. elitista adaptativo).
              </p>
            </div>
            <div class="text-right">
              <p class="text-xs text-emerald-600 font-semibold">Status</p>
              <p class="text-sm text-emerald-800">{{ statusMessage }}</p>
            </div>
          </div>
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div class="bg-gradient-to-br from-emerald-50 to-white rounded-xl border border-emerald-100 p-4">
              <div class="flex items-center justify-between">
                <h3 class="font-semibold text-emerald-900">Evolução do Fitness</h3>
                <span class="text-xs px-2 py-1 bg-emerald-100 text-emerald-700 rounded-full">elitismo + torneio</span>
              </div>
              <canvas ref="fitnessCanvas" class="w-full h-56"></canvas>
            </div>
            <div class="bg-gradient-to-br from-amber-50 to-white rounded-xl border border-amber-100 p-4">
              <div class="flex items-center justify-between">
                <h3 class="font-semibold text-amber-900">Uso de recursos</h3>
                <span class="text-xs px-2 py-1 bg-amber-100 text-amber-700 rounded-full">insumos + água</span>
              </div>
              <canvas ref="resourcesCanvas" class="w-full h-56"></canvas>
            </div>
          </div>
          <div class="flex flex-wrap gap-3 text-sm">
            <span class="px-3 py-1 bg-emerald-100 text-emerald-800 rounded-full">
              Melhor fitness: {{ formatFitness(bestSolution?.fitness) }}
            </span>
            <span class="px-3 py-1 bg-amber-100 text-amber-800 rounded-full">
              Custo total: {{ formatCurrencyK(bestSolution?.cost) }}
            </span>
            <span class="px-3 py-1 bg-sky-100 text-sky-800 rounded-full">
              Água: {{ formatWater(bestSolution?.water) }}
            </span>
            <span class="px-3 py-1 bg-slate-100 text-slate-800 rounded-full">
              Geração: {{ bestSolution?.generation ?? '—' }}
            </span>
          </div>
        </div>

        <!-- Controle -->
        <div class="space-y-4">
          <div class="bg-white rounded-2xl shadow-lg border border-emerald-100 p-5 space-y-3">
            <div class="flex items-center justify-between">
              <h3 class="text-lg font-bold text-emerald-950">Cenários pré-definidos</h3>
              <span class="text-xs text-emerald-600">Organico, Irrigação mínima, Alta produtividade</span>
            </div>
            <div class="space-y-3">
              <div
                v-for="(scenario, key) in scenarios"
                :key="key"
                class="p-3 rounded-xl border transition-all"
                :class="selectedScenario === key ? 'border-emerald-400 bg-emerald-50' : 'border-emerald-100 bg-white'"
              >
                <label class="flex items-start gap-3 cursor-pointer">
                  <input type="radio" class="mt-1 text-emerald-600" :value="key" v-model="selectedScenario" />
                  <div class="flex-1">
                    <p class="font-semibold text-emerald-900">{{ scenario.name }}</p>
                    <p class="text-sm text-emerald-700">{{ scenario.description }}</p>
                    <div class="flex gap-3 mt-2 text-xs text-emerald-800">
                      <span class="px-2 py-1 bg-white rounded-lg border border-emerald-100">
                        Budget: {{ formatCurrencyK(scenario.budget_k) }}
                      </span>
                      <span class="px-2 py-1 bg-white rounded-lg border border-emerald-100">
                        Água: {{ formatWater(scenario.water_limit_m3) }}
                      </span>
                    </div>
                  </div>
                </label>
              </div>
            </div>
          </div>

          <div class="bg-white rounded-2xl shadow-lg border border-emerald-100 p-5 space-y-4">
            <div class="flex items-center justify-between">
              <div>
                <h3 class="text-lg font-bold text-emerald-950">Sugestão automática de parâmetros</h3>
                <p class="text-sm text-emerald-700">Ajustada pelos sinais do dataset salvo.</p>
              </div>
              <button
                class="px-3 py-2 rounded-lg bg-emerald-600 text-white text-sm font-semibold hover:bg-emerald-700 transition"
                @click="applySuggestion"
              >
                Aplicar sugestão
              </button>
            </div>
            <div class="grid grid-cols-2 gap-3 text-sm text-emerald-900">
              <label class="space-y-1">
                <span class="font-semibold">População</span>
                <input v-model.number="params.population_size" type="number" min="20" class="w-full border rounded-lg px-3 py-2" />
              </label>
              <label class="space-y-1">
                <span class="font-semibold">Gerações</span>
                <input v-model.number="params.generations" type="number" min="10" class="w-full border rounded-lg px-3 py-2" />
              </label>
              <label class="space-y-1">
                <span class="font-semibold">Mutação</span>
                <input v-model.number="params.mutation_rate" type="number" step="0.01" min="0" max="0.5" class="w-full border rounded-lg px-3 py-2" />
              </label>
              <label class="space-y-1">
                <span class="font-semibold">Crossover</span>
                <input v-model.number="params.crossover_rate" type="number" step="0.01" min="0" max="1" class="w-full border rounded-lg px-3 py-2" />
              </label>
              <label class="space-y-1">
                <span class="font-semibold">Elitismo</span>
                <input v-model.number="params.elitism" type="number" min="1" class="w-full border rounded-lg px-3 py-2" />
              </label>
              <label class="space-y-1">
                <span class="font-semibold">Seed</span>
                <input v-model.number="params.seed" type="number" class="w-full border rounded-lg px-3 py-2" />
              </label>
            </div>
            <button
              class="w-full inline-flex items-center justify-center gap-2 px-4 py-3 rounded-xl bg-emerald-600 text-white font-semibold hover:bg-emerald-700 transition disabled:opacity-60"
              :disabled="running"
              @click="runAlgorithm"
            >
              <span class="material-symbols-outlined text-base animate-spin" v-if="running">progress_activity</span>
              {{ running ? 'Executando com dados reais...' : 'Rodar algoritmo genético' }}
            </button>
            <p class="text-xs text-emerald-700">
              Comparação automática com baseline (roleta + single point) e registro do tempo de execução para cada abordagem.
            </p>
          </div>
        </div>
      </div>

      <!-- Resultados -->
      <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div class="lg:col-span-2 bg-white rounded-2xl shadow-lg border border-emerald-100 p-6 space-y-4">
          <div class="flex items-center justify-between">
            <div>
              <p class="text-xs uppercase text-emerald-600 font-semibold">Melhor indivíduo</p>
              <h3 class="text-2xl font-bold text-emerald-950">Solução encontrada</h3>
            </div>
            <div class="text-right">
              <p class="text-sm text-emerald-800">Fitness: {{ formatFitness(bestSolution?.fitness) }}</p>
              <p class="text-xs text-emerald-700">Geração {{ bestSolution?.generation ?? '—' }}</p>
            </div>
          </div>
          <div class="grid grid-cols-2 md:grid-cols-4 gap-3">
            <div class="p-3 rounded-lg bg-emerald-50 border border-emerald-100">
              <p class="text-xs text-emerald-700">Valor (R$k)</p>
              <p class="text-xl font-bold text-emerald-900">{{ formatCurrencyK(bestSolution?.value) }}</p>
            </div>
            <div class="p-3 rounded-lg bg-amber-50 border border-amber-100">
              <p class="text-xs text-amber-700">Custo insumos</p>
              <p class="text-xl font-bold text-amber-900">{{ formatCurrencyK(bestSolution?.cost) }}</p>
            </div>
            <div class="p-3 rounded-lg bg-sky-50 border border-sky-100">
              <p class="text-xs text-sky-700">Água (m³)</p>
              <p class="text-xl font-bold text-sky-900">{{ formatWater(bestSolution?.water) }}</p>
            </div>
            <div class="p-3 rounded-lg bg-slate-50 border border-slate-200">
              <p class="text-xs text-slate-700">Itens selecionados</p>
              <p class="text-xl font-bold text-slate-900">{{ bestSolution?.selected_items?.length || 0 }}</p>
            </div>
          </div>
          <div class="overflow-auto rounded-xl border border-emerald-100">
            <table class="min-w-full text-sm">
              <thead class="bg-emerald-50 text-emerald-800">
                <tr>
                  <th class="px-3 py-2 text-left">Cultura</th>
                  <th class="px-3 py-2 text-left">Área (ha)</th>
                  <th class="px-3 py-2 text-left">Valor (R$k)</th>
                  <th class="px-3 py-2 text-left">Custo (R$k)</th>
                  <th class="px-3 py-2 text-left">Água (m³)</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="item in (bestSolution?.selected_items || []).slice(0, 12)" :key="item.id" class="border-b last:border-none">
                  <td class="px-3 py-2 text-emerald-900">{{ item.cultura }}</td>
                  <td class="px-3 py-2 text-emerald-800">{{ item.area_ha }}</td>
                  <td class="px-3 py-2 text-emerald-800">{{ item.valor_estimado_k }}</td>
                  <td class="px-3 py-2 text-emerald-800">{{ item.insumo_custo_k }}</td>
                  <td class="px-3 py-2 text-emerald-800">{{ item.agua_m3 }}</td>
                </tr>
              </tbody>
            </table>
          </div>
          <p class="text-xs text-emerald-700">
            Lista usa somente dados reais da FarmTech (sem mocks) e respeita o budget/água do cenário escolhido.
          </p>
        </div>

        <div class="bg-white rounded-2xl shadow-lg border border-emerald-100 p-6 space-y-4">
          <p class="text-xs uppercase text-emerald-600 font-semibold">Baseline x Estratégia avançada</p>
          <h3 class="text-xl font-bold text-emerald-950">Comparação de qualidade e tempo</h3>
          <div class="space-y-3">
            <div class="p-3 rounded-lg bg-emerald-50 border border-emerald-100">
              <p class="text-sm text-emerald-800 font-semibold">Fitness ganho</p>
              <p class="text-2xl font-bold text-emerald-900">
                {{ formatFitness(benchmark?.delta?.fitness_gain) }}
              </p>
              <p class="text-xs text-emerald-700">elitismo + uniforme x roleta single-point</p>
            </div>
            <div class="p-3 rounded-lg bg-amber-50 border border-amber-100">
              <p class="text-sm text-amber-800 font-semibold">Tempo adicional</p>
              <p class="text-2xl font-bold text-amber-900">
                {{ benchmark?.delta?.runtime_diff_ms ?? 0 }} ms
              </p>
              <p class="text-xs text-amber-700">positivo = mais lento, negativo = mais rápido</p>
            </div>
            <div class="divide-y divide-emerald-100 border border-emerald-100 rounded-lg">
              <div class="p-3 flex items-center justify-between">
                <div>
                  <p class="text-sm text-emerald-800 font-semibold">Baseline</p>
                  <p class="text-xs text-emerald-600">Roleta + single point + mutação fixa</p>
                </div>
                <p class="text-lg font-bold text-emerald-900">{{ formatFitness(benchmark?.baseline?.fitness) }}</p>
              </div>
              <div class="p-3 flex items-center justify-between">
                <div>
                  <p class="text-sm text-emerald-800 font-semibold">Avançada</p>
                  <p class="text-xs text-emerald-600">Torneio + elitismo + mutação adaptativa</p>
                </div>
                <p class="text-lg font-bold text-emerald-900">{{ formatFitness(benchmark?.improved?.fitness) }}</p>
              </div>
            </div>
            <div class="p-3 rounded-lg bg-slate-50 border border-slate-200 text-xs text-slate-700">
              Entrada salva em <strong>{{ datasetInfo.input_file || '—' }}</strong> para reuso e comparabilidade.
            </div>
          </div>
        </div>
      </div>

      <!-- Comparações e dataset -->
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div class="bg-white rounded-2xl shadow-lg border border-emerald-100 p-6 space-y-3">
          <div class="flex items-center justify-between">
            <div>
              <p class="text-xs uppercase text-emerald-600 font-semibold">Cenários comparados</p>
              <h3 class="text-xl font-bold text-emerald-950">Impacto visual por estratégia</h3>
            </div>
            <span class="text-xs text-emerald-700">{{ comparisons.length }} execuções rápidas</span>
          </div>
          <div class="overflow-auto rounded-xl border border-emerald-100">
            <table class="min-w-full text-sm">
              <thead class="bg-emerald-50 text-emerald-800">
                <tr>
                  <th class="px-3 py-2 text-left">Cenário</th>
                  <th class="px-3 py-2 text-left">Fitness</th>
                  <th class="px-3 py-2 text-left">Custo (R$k)</th>
                  <th class="px-3 py-2 text-left">Água (m³)</th>
                  <th class="px-3 py-2 text-left">Tempo (ms)</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="row in comparisons" :key="row.scenario" class="border-b last:border-none">
                  <td class="px-3 py-2 text-emerald-900">{{ scenarios[row.scenario]?.name || row.scenario }}</td>
                  <td class="px-3 py-2 text-emerald-800">{{ formatFitness(row.fitness) }}</td>
                  <td class="px-3 py-2 text-emerald-800">{{ formatCurrencyK(row.cost) }}</td>
                  <td class="px-3 py-2 text-emerald-800">{{ formatWater(row.water) }}</td>
                  <td class="px-3 py-2 text-emerald-800">{{ row.runtime_ms }}</td>
                </tr>
              </tbody>
            </table>
          </div>
          <p class="text-xs text-emerald-700">
            Cada cenário é executado rapidamente para contraste visual (orgânico, irrigação mínima, alta produtividade).
          </p>
        </div>

        <div class="bg-white rounded-2xl shadow-lg border border-emerald-100 p-6 space-y-3">
          <div class="flex items-center justify-between">
            <div>
              <p class="text-xs uppercase text-emerald-600 font-semibold">Amostra do dataset</p>
              <h3 class="text-xl font-bold text-emerald-950">Entrada salva para reprodutibilidade</h3>
            </div>
            <span class="text-xs text-emerald-700">Path: {{ datasetInfo.input_file || '—' }}</span>
          </div>
          <div class="overflow-auto rounded-xl border border-emerald-100">
            <table class="min-w-full text-sm">
              <thead class="bg-emerald-50 text-emerald-800">
                <tr>
                  <th class="px-3 py-2 text-left">Cultura</th>
                  <th class="px-3 py-2 text-left">Área (ha)</th>
                  <th class="px-3 py-2 text-left">Valor (R$k)</th>
                  <th class="px-3 py-2 text-left">Custo (R$k)</th>
                  <th class="px-3 py-2 text-left">Água (m³)</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="item in datasetInfo.sample || []" :key="item.id" class="border-b last:border-none">
                  <td class="px-3 py-2 text-emerald-900">{{ item.cultura }}</td>
                  <td class="px-3 py-2 text-emerald-800">{{ item.area_ha }}</td>
                  <td class="px-3 py-2 text-emerald-800">{{ item.valor_estimado_k }}</td>
                  <td class="px-3 py-2 text-emerald-800">{{ item.insumo_custo_k }}</td>
                  <td class="px-3 py-2 text-emerald-800">{{ item.agua_m3 }}</td>
                </tr>
              </tbody>
            </table>
          </div>
          <p class="text-xs text-emerald-700">
            Entrada salva automaticamente em arquivo para reexecutar o GA quantas vezes quiser com o mesmo conjunto real.
          </p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onBeforeUnmount, onMounted, ref } from 'vue'
import Chart from 'chart.js/auto'

definePageMeta({ ssr: false })

const config = useRuntimeConfig()
const apiBase = config.public.apiBase.replace(/\/$/, '')

const scenarios = ref<Record<string, any>>({})
const selectedScenario = ref('alta_produtividade')
const suggestion = ref<any>(null)
const datasetInfo = ref<any>({ stats: {}, sample: [] })
const params = ref({
  population_size: 80,
  generations: 40,
  mutation_rate: 0.08,
  crossover_rate: 0.82,
  elitism: 6,
  seed: Date.now(),
  strategy: 'elitist_adaptive'
})

const bestSolution = ref<any>(null)
const benchmark = ref<any>(null)
const comparisons = ref<any[]>([])
const statusMessage = ref('Aguardando execução com dados reais...')
const running = ref(false)
const fitnessCanvas = ref<HTMLCanvasElement | null>(null)
const resourcesCanvas = ref<HTMLCanvasElement | null>(null)

let fitnessChart: Chart<'line'> | null = null
let resourcesChart: Chart<'line'> | null = null
let animationTimer: any = null

const formatCurrencyK = (val?: number) => (val !== undefined && val !== null ? `R$ ${val.toLocaleString('pt-BR', { maximumFractionDigits: 0 })}k` : '—')
const formatWater = (val?: number) => (val !== undefined && val !== null ? `${val.toLocaleString('pt-BR', { maximumFractionDigits: 0 })} m³` : '—')
const formatFitness = (val?: number) => (val !== undefined && val !== null ? val.toLocaleString('pt-BR', { maximumFractionDigits: 2 }) : '—')

const destroyCharts = () => {
  if (fitnessChart) {
    fitnessChart.destroy()
    fitnessChart = null
  }
  if (resourcesChart) {
    resourcesChart.destroy()
    resourcesChart = null
  }
}

const initCharts = () => {
  destroyCharts()
  if (fitnessCanvas.value) {
    fitnessChart = new Chart(fitnessCanvas.value, {
      type: 'line',
      data: {
        labels: [],
        datasets: [
          {
            label: 'Melhor fitness',
            data: [],
            borderColor: '#047857',
            backgroundColor: 'rgba(4,120,87,0.15)',
            tension: 0.35,
            fill: true
          },
          {
            label: 'Fitness médio',
            data: [],
            borderColor: '#16a34a',
            backgroundColor: 'rgba(22,163,74,0.15)',
            tension: 0.35,
            fill: true
          }
        ]
      },
      options: {
        animation: false,
        responsive: true,
        plugins: { legend: { display: false } },
        scales: { y: { ticks: { color: '#064e3b' }, grid: { color: 'rgba(6,78,59,0.1)' } } }
      }
    })
  }
  if (resourcesCanvas.value) {
    resourcesChart = new Chart(resourcesCanvas.value, {
      type: 'line',
      data: {
        labels: [],
        datasets: [
          {
            label: 'Custo insumos (R$k)',
            data: [],
            borderColor: '#d97706',
            backgroundColor: 'rgba(217,119,6,0.18)',
            tension: 0.35,
            fill: true
          },
          {
            label: 'Água (m³)',
            data: [],
            borderColor: '#0284c7',
            backgroundColor: 'rgba(2,132,199,0.15)',
            tension: 0.35,
            fill: true
          }
        ]
      },
      options: {
        animation: false,
        responsive: true,
        plugins: { legend: { display: false } },
        scales: { y: { ticks: { color: '#334155' }, grid: { color: 'rgba(148,163,184,0.2)' } } }
      }
    })
  }
}

const animateHistory = (hist: any[]) => {
  if (!fitnessCanvas.value || !resourcesCanvas.value) return
  initCharts()
  if (animationTimer) clearInterval(animationTimer)
  if (!hist || !hist.length) return

  let idx = 0
  animationTimer = setInterval(() => {
    const slice = hist[idx]
    if (fitnessChart && resourcesChart) {
      fitnessChart.data.labels?.push(`G${slice.generation}`)
      ;(fitnessChart.data.datasets[0].data as number[]).push(slice.best_fitness)
      ;(fitnessChart.data.datasets[1].data as number[]).push(slice.mean_fitness)
      resourcesChart.data.labels?.push(`G${slice.generation}`)
      ;(resourcesChart.data.datasets[0].data as number[]).push(slice.best_cost)
      ;(resourcesChart.data.datasets[1].data as number[]).push(slice.best_water)
      fitnessChart.update()
      resourcesChart.update()
    }
    idx += 1
    if (idx >= hist.length) {
      clearInterval(animationTimer)
    }
  }, 140)
}

const applySuggestion = () => {
  if (!suggestion.value) return
  params.value = { ...params.value, ...suggestion.value, seed: Date.now(), strategy: 'elitist_adaptive' }
}

const loadScenarios = async () => {
  try {
    const data = await $fetch<any>(`${apiBase}/genetic/scenarios`)
    scenarios.value = data.scenarios || {}
    suggestion.value = data.suggestion
    datasetInfo.value = data.dataset
    selectedScenario.value = Object.keys(scenarios.value)[0] || 'alta_produtividade'
    applySuggestion()
  } catch (err) {
    console.error('load_scenarios_failed', err)
  }
}

const runAlgorithm = async () => {
  running.value = true
  statusMessage.value = 'Executando algoritmo genético com dados reais...'
  try {
    const payload = {
      ...params.value,
      scenario: selectedScenario.value,
      compare_all: true
    }
    const data = await $fetch<any>(`${apiBase}/genetic/run`, {
      method: 'POST',
      body: payload
    })
    datasetInfo.value = data.dataset
    bestSolution.value = data.best_solution
    benchmark.value = data.benchmark
    comparisons.value = data.comparisons || []
    statusMessage.value = `Entrada salva em ${data.dataset?.input_file || ''}`
    animateHistory(data.history || [])
  } catch (err) {
    console.error('run_genetic_failed', err)
    statusMessage.value = 'Falha ao rodar algoritmo genético.'
  } finally {
    running.value = false
  }
}

onMounted(async () => {
  await loadScenarios()
  await runAlgorithm()
})

onBeforeUnmount(() => {
  if (animationTimer) clearInterval(animationTimer)
  destroyCharts()
})
</script>
