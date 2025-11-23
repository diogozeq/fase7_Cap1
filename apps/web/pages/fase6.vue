<template>
  <div class="min-h-screen bg-gradient-to-b from-slate-50 to-emerald-50 py-10">
    <div class="max-w-6xl mx-auto px-4">
      <NuxtLink to="/" class="text-emerald-700 hover:text-emerald-800 mb-4 inline-block text-sm font-semibold">
        <- Voltar
      </NuxtLink>

      <div class="flex flex-col gap-1 mb-6">
        <p class="text-sm text-slate-500">Fase 6 - Visao Computacional</p>
        <div class="flex flex-wrap items-center gap-3">
          <h1 class="text-3xl font-bold text-slate-900">Monitoramento visual com YOLO</h1>
          <span class="px-3 py-1 text-xs rounded-full bg-emerald-100 text-emerald-700">Virtual, sem hardware</span>
        </div>
        <p class="text-slate-600">Tudo pronto apenas com algoritmos: usamos a pasta de imagens da fase 6 como se fosse uma ESP32-CAM.</p>
      </div>

      <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div class="lg:col-span-2 space-y-6">
          <div class="bg-white rounded-2xl border border-slate-100 shadow-sm p-6">
            <div class="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
              <div>
                <p class="text-sm text-slate-500">Feed virtual / imagens estaticas</p>
                <h2 class="text-xl font-semibold text-slate-900">Pipeline pronto ao iniciar</h2>
                <p class="text-sm text-slate-600">Processamos automaticamente o lote de imagens da fase 6 para popular o historico real.</p>
              </div>
              <div class="text-xs text-right text-slate-500 space-y-1">
                <p>Modelo: <span class="font-semibold text-slate-800">{{ status?.model_source || 'yolov8n.pt' }}</span></p>
                <p v-if="status?.static_images_dir">Fonte: <span class="font-semibold text-slate-800">{{ status.static_images_dir }}</span></p>
              </div>
            </div>

            <div class="mt-4 flex flex-wrap gap-3">
              <button
                @click="runStaticIngestion({ reset: true, limit: 40 })"
                :disabled="ingesting || bootstrapRunning"
                class="px-5 py-2 rounded-lg bg-emerald-600 text-white text-sm font-semibold hover:bg-emerald-700 disabled:bg-emerald-400 transition-colors"
              >
                {{ ingesting ? 'Processando lote...' : 'Reprocessar pasta base' }}
              </button>
              <button
                @click="runStaticIngestion({ reset: false, limit: 20 })"
                :disabled="ingesting || bootstrapRunning"
                class="px-5 py-2 rounded-lg border border-emerald-200 text-emerald-700 text-sm font-semibold hover:border-emerald-400 transition-colors"
              >
                Acrescentar novas leituras
              </button>
              <button
                @click="fetchHistory"
                :disabled="ingesting"
                class="px-4 py-2 rounded-lg border border-slate-200 text-slate-700 text-sm font-semibold hover:border-slate-400 transition-colors"
              >
                Recarregar historico
              </button>
            </div>

            <p v-if="lastBootstrapMessage" class="text-xs text-slate-500 mt-2">{{ lastBootstrapMessage }}</p>
            <p v-if="error" class="text-sm text-red-600 mt-2">{{ error }}</p>

            <div class="mt-4 grid gap-3 sm:grid-cols-3">
              <div class="rounded-xl bg-emerald-50 border border-emerald-100 p-4">
                <p class="text-xs uppercase text-emerald-700 font-semibold tracking-wide">Imagens processadas</p>
                <p class="text-2xl font-bold text-emerald-900">{{ ingestSummary?.images_processed ?? detectionHistory.length }}</p>
              </div>
              <div class="rounded-xl bg-sky-50 border border-sky-100 p-4">
                <p class="text-xs uppercase text-sky-700 font-semibold tracking-wide">Detecoes salvas</p>
                <p class="text-2xl font-bold text-sky-900">{{ ingestSummary?.detections_saved ?? detectedObjects }}</p>
              </div>
              <div class="rounded-xl bg-amber-50 border border-amber-100 p-4">
                <p class="text-xs uppercase text-amber-700 font-semibold tracking-wide">Classes encontradas</p>
                <p class="text-2xl font-bold text-amber-900">{{ uniqueClasses }}</p>
              </div>
            </div>

            <div class="mt-3">
              <p class="text-xs font-semibold text-slate-700 mb-1">Classes identificadas</p>
              <div class="flex flex-wrap gap-2">
                <span
                  v-for="classe in (ingestSummary?.classes || classBreakdown.map(c => c.classe))"
                  :key="classe"
                  class="px-3 py-1 rounded-full bg-slate-100 text-slate-700 text-xs font-semibold"
                >
                  {{ classe }}
                </span>
                <span v-if="!ingestSummary?.classes?.length && classBreakdown.length === 0" class="text-xs text-slate-500">
                  Nenhuma classe identificada ainda.
                </span>
              </div>
            </div>
          </div>

          <div class="bg-white rounded-2xl border border-slate-100 shadow-sm p-6">
            <h2 class="text-xl font-semibold text-slate-900 mb-2">Upload de imagem</h2>
            <p class="text-sm text-slate-600 mb-4">Envie qualquer foto que queira analisar. O arquivo e enviado para o backend FastAPI e processado pelo YOLO.</p>
            <div class="border-2 border-dashed border-emerald-200 rounded-lg p-8 text-center bg-emerald-50/40">
              <p class="text-slate-700 mb-4">Arraste uma imagem aqui ou clique para selecionar</p>
              <input type="file" @change="handleImageUpload" accept="image/*" class="hidden" ref="fileInput" />
              <button
                @click="triggerFileInput"
                class="px-6 py-2 bg-emerald-600 hover:bg-emerald-700 text-white rounded-md transition-colors text-sm font-semibold"
              >
                Selecionar imagem
              </button>
            </div>

            <div v-if="uploadedImageName" class="mt-6">
              <p class="font-semibold mb-2 text-slate-800">Imagem carregada</p>
              <div class="bg-slate-50 rounded-lg p-4 flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
                <p class="text-slate-700 truncate">{{ uploadedImageName }}</p>
                <button
                  @click="analyzeImage"
                  :disabled="loading"
                  class="px-6 py-2 bg-emerald-600 hover:bg-emerald-700 disabled:bg-emerald-400 text-white rounded-md transition-colors text-sm font-semibold"
                >
                  {{ loading ? 'Analisando...' : 'Analisar com YOLOv8' }}
                </button>
              </div>
              <p v-if="error" class="text-red-600 mt-2 text-sm">{{ error }}</p>
            </div>
          </div>

          <div v-if="detectionResults.length > 0" class="bg-white rounded-2xl border border-slate-100 shadow-sm p-6">
            <h2 class="text-xl font-semibold text-slate-900 mb-4">Resultados da deteccao</h2>
            <div class="space-y-3">
              <div
                v-for="(result, idx) in detectionResults"
                :key="idx"
                class="p-3 bg-slate-50 rounded-lg flex items-center justify-between gap-4"
              >
                <div>
                  <p class="font-semibold text-slate-900">{{ result.class }}</p>
                  <p class="text-xs text-slate-500" v-if="result.image">Imagem: {{ result.image }}</p>
                </div>
                <div class="flex items-center gap-3 w-56">
                  <div class="w-full bg-slate-200 rounded-full h-2">
                    <div class="bg-emerald-600 h-2 rounded-full" :style="{ width: result.confidence + '%' }"></div>
                  </div>
                  <span class="font-bold text-emerald-700 w-12 text-right">{{ result.confidence }}%</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div class="space-y-6">
          <div class="bg-white rounded-2xl border border-slate-100 shadow-sm p-6">
            <h3 class="text-lg font-semibold text-slate-900 mb-4">Painel rapido</h3>
            <div class="space-y-3">
              <div class="p-3 rounded-lg bg-emerald-50 border border-emerald-100 flex items-center justify-between">
                <span class="text-slate-700 text-sm">Total de detecoes</span>
                <span class="text-2xl font-bold text-emerald-800">{{ totalDetections }}</span>
              </div>
              <div class="p-3 rounded-lg bg-sky-50 border border-sky-100 flex items-center justify-between">
                <span class="text-slate-700 text-sm">Confianca media</span>
                <span class="text-2xl font-bold text-sky-800">{{ averageConfidence }}%</span>
              </div>
              <div class="p-3 rounded-lg bg-amber-50 border border-amber-100 flex items-center justify-between">
                <span class="text-slate-700 text-sm">Objetos registrados</span>
                <span class="text-2xl font-bold text-amber-800">{{ detectedObjects }}</span>
              </div>
            </div>
          </div>

          <div class="bg-white rounded-2xl border border-slate-100 shadow-sm p-6">
            <h3 class="text-lg font-semibold text-slate-900 mb-3">Classes mais frequentes</h3>
            <div class="space-y-3" v-if="classBreakdown.length">
              <div v-for="item in classBreakdown" :key="item.classe" class="space-y-1">
                <div class="flex items-center justify-between text-sm text-slate-700">
                  <span class="font-semibold text-slate-800">{{ item.classe }}</span>
                  <span class="text-slate-600">{{ item.count }}x</span>
                </div>
                  <div class="w-full bg-slate-200 h-2 rounded-full overflow-hidden">
                  <div class="h-2 bg-emerald-600" :style="{ width: Math.min((item.count / ((classBreakdown[0]?.count || 1))) * 100, 100) + '%' }"></div>
                </div>
              </div>
            </div>
            <p v-else class="text-sm text-slate-500">Nenhuma classe registrada ainda.</p>
          </div>

          <div class="bg-white rounded-2xl border border-slate-100 shadow-sm p-6" v-if="latestDetection">
            <h3 class="text-lg font-semibold text-slate-900 mb-2">Ultima deteccao</h3>
            <p class="text-sm text-slate-600 mb-1">{{ latestDetection.timestamp }}</p>
            <p class="text-sm text-slate-700">Imagem: <span class="font-semibold text-slate-900">{{ latestDetection.image }}</span></p>
            <p class="text-sm text-slate-700">Classe: <span class="font-semibold text-slate-900">{{ latestDetection.classe }}</span></p>
            <p class="text-sm text-slate-700">Confianca: <span class="font-semibold text-emerald-700">{{ latestDetection.confidence }}%</span></p>
          </div>
        </div>
      </div>

      <div class="bg-white rounded-2xl border border-slate-100 shadow-sm p-6 mt-8">
        <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 mb-4">
          <h3 class="text-xl font-semibold text-slate-900">Historico de detecoes reais</h3>
          <div class="flex gap-2">
            <button
              @click="fetchHistory"
              class="px-4 py-2 rounded-lg border border-slate-200 text-slate-700 text-sm font-semibold hover:border-slate-400 transition-colors"
            >
              Recarregar
            </button>
          </div>
        </div>
        <div class="overflow-x-auto">
          <table class="w-full text-sm">
            <thead class="bg-slate-100 border-b">
              <tr>
                <th class="px-4 py-2 text-left">Data/Hora</th>
                <th class="px-4 py-2 text-left">Imagem</th>
                <th class="px-4 py-2 text-left">Classe</th>
                <th class="px-4 py-2 text-left">Objetos</th>
                <th class="px-4 py-2 text-left">Confianca</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(history, idx) in detectionHistory" :key="idx" class="border-b hover:bg-slate-50">
                <td class="px-4 py-2 whitespace-nowrap">{{ history.timestamp }}</td>
                <td class="px-4 py-2">{{ history.image }}</td>
                <td class="px-4 py-2">{{ history.classe || '-' }}</td>
                <td class="px-4 py-2">{{ history.objects }}</td>
                <td class="px-4 py-2">{{ history.confidence }}%</td>
              </tr>
              <tr v-if="detectionHistory.length === 0">
                <td colspan="5" class="px-4 py-3 text-center text-slate-500">Nenhuma deteccao ainda. Use o lote estatico ou envie uma imagem.</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'

type DetectionResult = {
  class: string
  confidence: number
  bbox?: number[]
  image?: string
}

type DetectionHistoryItem = {
  timestamp: string
  image: string
  classe: string
  objects: number
  confidence: number
}

const uploadedImageName = ref('')
const selectedFile = ref<File | null>(null)
const detectionResults = ref<DetectionResult[]>([])
const fileInput = ref<HTMLInputElement | null>(null)
const loading = ref(false)
const error = ref('')

const detectionHistory = ref<DetectionHistoryItem[]>([])
const ingesting = ref(false)
const ingestSummary = ref<any | null>(null)
const status = ref<any | null>(null)
const bootstrapRunning = ref(false)
const lastBootstrapMessage = ref('')

const config = useRuntimeConfig()
const apiBase = config.public.apiBase
const historyLimit = 40

const fetchStatus = async () => {
  try {
    status.value = await $fetch(`${apiBase}/cv/status`)
  } catch (e) {
    console.error('Failed to load CV status', e)
  }
}

const fetchHistory = async () => {
  error.value = ''
  try {
    const data = await $fetch<DetectionHistoryItem[]>(`${apiBase}/cv/history`, {
      params: { limit: historyLimit }
    })
    detectionHistory.value = data || []
  } catch (e) {
    console.error('Failed to fetch history', e)
    error.value = 'Nao foi possivel carregar o historico de detecoes.'
  }
}

const runStaticIngestion = async (options: { reset?: boolean; limit?: number; confidence?: number } = {}) => {
  ingesting.value = true
  error.value = ''
  try {
    const data = await $fetch(`${apiBase}/cv/ingest-static`, {
      method: 'POST',
      params: {
        reset: options.reset ?? true,
        limit: options.limit ?? 30,
        confidence: options.confidence ?? 0.35
      }
    })
    ingestSummary.value = data as any
    lastBootstrapMessage.value = 'Dataset estatico processado pelo backend.'
    await fetchHistory()
  } catch (e) {
    console.error(e)
    const detail = (e as any)?.data?.detail
    if (detail === 'Not Found') {
      error.value = 'Falha ao processar a pasta estatica: endpoint /cv/ingest-static nao esta ativo. Reinicie o backend (npm run dev).'
    } else {
      error.value = detail ? `Falha ao processar a pasta estatica: ${detail}` : 'Falha ao processar a pasta estatica.'
    }
  } finally {
    ingesting.value = false
  }
}

const bootstrapCv = async () => {
  bootstrapRunning.value = true
  error.value = ''
  try {
    await fetchStatus()
    await fetchHistory()
    if (detectionHistory.value.length === 0) {
      await runStaticIngestion({ reset: true })
      lastBootstrapMessage.value = 'Lote de imagens da fase 6 processado automaticamente.'
    } else {
      lastBootstrapMessage.value = 'Historico real carregado do backend.'
    }
  } finally {
    bootstrapRunning.value = false
  }
}

onMounted(() => {
  bootstrapCv()
})

const totalDetections = computed(() => detectionHistory.value.length + detectionResults.value.length)
const averageConfidence = computed(() => {
  const historyConf = detectionHistory.value.map((h) => Number(h.confidence) || 0)
  const currentConf = detectionResults.value.map((r) => Number(r.confidence) || 0)
  const all = [...historyConf, ...currentConf]
  return all.length > 0 ? Math.round(all.reduce((sum, v) => sum + v, 0) / all.length) : 0
})
const detectedObjects = computed(() => {
  const fromHistory = detectionHistory.value.reduce((sum, item) => sum + (Number(item.objects) || 0), 0)
  return fromHistory + detectionResults.value.length
})
const uniqueClasses = computed(() => {
  const classes = new Set<string>()
  detectionHistory.value.forEach((d) => d.classe && classes.add(d.classe))
  detectionResults.value.forEach((d) => d.class && classes.add(d.class))
  return classes.size
})
const classBreakdown = computed(() => {
  const counts: Record<string, number> = {}
  detectionHistory.value.forEach((d) => {
    const key = d.classe || 'desconhecido'
    counts[key] = (counts[key] || 0) + 1
  })
  detectionResults.value.forEach((d) => {
    const key = d.class || 'detector'
    counts[key] = (counts[key] || 0) + 1
  })
  return Object.entries(counts)
    .map(([classe, count]) => ({ classe, count }))
    .sort((a, b) => b.count - a.count)
})
const latestDetection = computed(() => detectionHistory.value[0] || null)

const triggerFileInput = () => {
  fileInput.value?.click()
}

const handleImageUpload = (event: Event) => {
  const target = event.target as HTMLInputElement
  if (target.files?.[0]) {
    selectedFile.value = target.files[0]
    uploadedImageName.value = target.files[0].name
    detectionResults.value = []
    error.value = ''
  }
}

const analyzeImage = async () => {
  if (!selectedFile.value) return

  loading.value = true
  error.value = ''

  const formData = new FormData()
  formData.append('file', selectedFile.value)

  try {
    const data = await $fetch(`${apiBase}/cv/analyze`, {
      method: 'POST',
      body: formData
    })

    if (data) {
      const results = data as any[]
      detectionResults.value = results.map((d: any) => ({
        class: d.class,
        confidence: Math.round((Number(d.confidence) || 0) * 100),
        bbox: d.bbox,
        image: d.image || uploadedImageName.value
      }))
      await fetchHistory()
    }
  } catch (e) {
    console.error(e)
    const detail = (e as any)?.data?.detail
    error.value = detail ? `Falha ao analisar imagem: ${detail}` : 'Falha ao analisar imagem. Verifique o backend.'
  } finally {
    loading.value = false
  }
}
</script>
