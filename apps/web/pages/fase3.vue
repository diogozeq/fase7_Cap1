<template>
  <div class="min-h-screen bg-gray-50 p-8">
    <div class="max-w-6xl mx-auto">
      <NuxtLink to="/" class="text-blue-600 hover:text-blue-700 mb-6 inline-block">← Voltar</NuxtLink>
      <h1 class="text-3xl font-bold text-gray-800 mb-6">📡 Fase 3: Monitoramento IoT</h1>
      
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-6">
        <!-- Sensor 1 -->
        <div class="bg-white rounded-lg shadow-md p-6">
          <h3 class="text-lg font-bold mb-4">💧 Sensor de Umidade</h3>
          <div class="text-center">
            <p class="text-4xl font-bold text-blue-600">{{ sensors.humidity }}%</p>
            <p class="text-gray-600 text-sm mt-2">Status: <span class="text-green-600 font-semibold">Ativo</span></p>
            <div class="mt-4 w-full bg-gray-200 rounded-full h-2">
              <div class="bg-blue-600 h-2 rounded-full" :style="{ width: sensors.humidity + '%' }"></div>
            </div>
          </div>
        </div>

        <!-- Sensor 2 -->
        <div class="bg-white rounded-lg shadow-md p-6">
          <h3 class="text-lg font-bold mb-4">🌡️ Sensor de Temperatura</h3>
          <div class="text-center">
            <p class="text-4xl font-bold text-orange-600">{{ sensors.temperature }}°C</p>
            <p class="text-gray-600 text-sm mt-2">Status: <span class="text-green-600 font-semibold">Ativo</span></p>
            <div class="mt-4 w-full bg-gray-200 rounded-full h-2">
              <div class="bg-orange-600 h-2 rounded-full" :style="{ width: (sensors.temperature / 50) * 100 + '%' }"></div>
            </div>
          </div>
        </div>

        <!-- Pump Status -->
        <div class="bg-white rounded-lg shadow-md p-6">
          <h3 class="text-lg font-bold mb-4">💦 Bomba de Irrigação</h3>
          <div class="text-center">
            <p class="text-4xl mb-4" :class="pumpStatus === 'Ligada' ? 'text-green-600' : 'text-red-600'">
              {{ pumpStatus === 'Ligada' ? '✓' : '✗' }}
            </p>
            <p class="text-2xl font-bold" :class="pumpStatus === 'Ligada' ? 'text-green-600' : 'text-red-600'">
              {{ pumpStatus }}
            </p>
            <button @click="togglePump" class="mt-4 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-md transition-colors">
              {{ pumpStatus === 'Ligada' ? 'Desligar' : 'Ligar' }}
            </button>
          </div>
        </div>
      </div>

      <!-- Decision Logic -->
      <div class="bg-white rounded-lg shadow-md p-6 mb-6">
        <h2 class="text-xl font-bold mb-4">🤖 Lógica de Decisão</h2>
        <div class="space-y-3">
          <div class="p-3 bg-blue-50 rounded-md">
            <p class="text-sm"><strong>Condição:</strong> Se umidade < 40% → Ligar bomba</p>
            <p class="text-sm text-gray-600">Atual: {{ sensors.humidity }}% - {{ sensors.humidity < 40 ? '✓ Ativar' : '✗ Desativar' }}</p>
          </div>
          <div class="p-3 bg-blue-50 rounded-md">
            <p class="text-sm"><strong>Condição:</strong> Se temperatura > 35°C → Aumentar irrigação</p>
            <p class="text-sm text-gray-600">Atual: {{ sensors.temperature }}°C - {{ sensors.temperature > 35 ? '✓ Aumentar' : '✗ Normal' }}</p>
          </div>
          <div class="p-3 bg-blue-50 rounded-md">
          <div class="p-3 bg-blue-50 rounded-md">
            <p class="text-sm"><strong>Decisão do Sistema:</strong></p>
            <p class="text-lg font-medium text-gray-800 mt-1">{{ decision }}</p>
          </div>
          </div>
        </div>
      </div>

      <!-- Features List -->
      <div class="bg-white rounded-lg shadow-md p-6">
        <h2 class="text-xl font-bold mb-4">✅ Funcionalidades</h2>
        <ul class="space-y-2">
          <li class="text-gray-700">✓ Gráficos real-time de sensores</li>
          <li class="text-gray-700">✓ Status da bomba de irrigação</li>
          <li class="text-gray-700">✓ Visualização da lógica de decisão</li>
        </ul>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'

const config = useRuntimeConfig()
const apiBase = config.public.apiBase.replace(/\/$/, '')

const sensors = ref({
  humidity: 0,
  temperature: 0,
  ph: 0
})

const pumpStatus = ref('Desligada')
const decision = ref('Aguardando dados...')
const loading = ref(true)

const fetchSensorData = async () => {
  try {
    const data = await $fetch(`${apiBase}/iot/sensors`)
    if (data) {
      const result = data as { umidade: number; temperatura: number; ph: number; bomba_ligada: boolean; decisao: string }
      sensors.value.humidity = result.umidade
      sensors.value.temperature = result.temperatura
      sensors.value.ph = result.ph
      pumpStatus.value = result.bomba_ligada ? 'Ligada' : 'Desligada'
      decision.value = result.decisao
    }
  } catch (e) {
    console.error('Erro ao buscar sensores:', e)
  } finally {
    loading.value = false
  }
}

const togglePump = async () => {
  try {
    const data = await $fetch(`${apiBase}/iot/pump/toggle`, { method: 'POST' })
    if (data) {
      const result = data as { bomba_ligada: boolean }
      pumpStatus.value = result.bomba_ligada ? 'Ligada' : 'Desligada'
    }
  } catch (e) {
    console.error('Erro ao alternar bomba:', e)
  }
}

let intervalId: any

onMounted(() => {
  fetchSensorData()
  intervalId = setInterval(fetchSensorData, 3000)
})

onUnmounted(() => {
  if (intervalId) clearInterval(intervalId)
})
</script>
