<template>
  <div class="min-h-screen bg-gray-50 p-8">
    <div class="max-w-6xl mx-auto">
      <NuxtLink to="/" class="text-blue-600 hover:text-blue-700 mb-6 inline-block">← Voltar</NuxtLink>
      <h1 class="text-3xl font-bold text-gray-800 mb-6">🔔 Fase 7: Alertas Integrados</h1>
      
      <!-- Active Alerts -->
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-6">
        <div v-for="alert in activeAlerts" :key="alert.id" class="bg-white rounded-lg shadow-md p-6 border-l-4" :style="{ borderColor: alert.color }">
          <div class="flex items-start justify-between mb-3">
            <h3 class="font-bold text-lg">{{ alert.title }}</h3>
            <span class="px-2 py-1 rounded text-xs font-semibold" :style="{ backgroundColor: alert.color + '20', color: alert.color }">
              {{ alert.severity }}
            </span>
          </div>
          <p class="text-gray-700 text-sm mb-3">{{ alert.message }}</p>
          <p class="text-xs text-gray-500">{{ alert.timestamp }}</p>
        </div>
      </div>

      <!-- Alert Management -->
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
        <!-- Create Alert -->
        <div class="bg-white rounded-lg shadow-md p-6">
          <h2 class="text-xl font-bold mb-4">➕ Criar Novo Alerta</h2>
          <div class="space-y-3">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Título</label>
              <input v-model="newAlert.title" placeholder="Título do alerta" class="w-full px-3 py-2 border border-gray-300 rounded-md" />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Mensagem</label>
              <textarea v-model="newAlert.message" placeholder="Descrição do alerta" class="w-full px-3 py-2 border border-gray-300 rounded-md" rows="3"></textarea>
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Severidade</label>
              <select v-model="newAlert.severity" class="w-full px-3 py-2 border border-gray-300 rounded-md">
                <option value="Baixa">Baixa</option>
                <option value="Média">Média</option>
                <option value="Alta">Alta</option>
                <option value="Crítica">Crítica</option>
              </select>
            </div>
            <button @click="createAlert" class="w-full bg-blue-600 hover:bg-blue-700 text-white font-medium py-2 rounded-md transition-colors">
              Criar Alerta
            </button>
          </div>
        </div>

        <!-- Alert Statistics -->
        <div class="bg-white rounded-lg shadow-md p-6">
          <h2 class="text-xl font-bold mb-4">📊 Estatísticas de Alertas</h2>
          <div class="space-y-3">
            <div class="p-3 bg-red-50 rounded-md flex justify-between items-center">
              <span class="font-semibold">Críticos</span>
              <span class="text-2xl font-bold text-red-600">{{ alertStats.critical }}</span>
            </div>
            <div class="p-3 bg-orange-50 rounded-md flex justify-between items-center">
              <span class="font-semibold">Altos</span>
              <span class="text-2xl font-bold text-orange-600">{{ alertStats.high }}</span>
            </div>
            <div class="p-3 bg-yellow-50 rounded-md flex justify-between items-center">
              <span class="font-semibold">Médios</span>
              <span class="text-2xl font-bold text-yellow-600">{{ alertStats.medium }}</span>
            </div>
            <div class="p-3 bg-blue-50 rounded-md flex justify-between items-center">
              <span class="font-semibold">Baixos</span>
              <span class="text-2xl font-bold text-blue-600">{{ alertStats.low }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Consolidated Logs -->
      <div class="bg-white rounded-lg shadow-md p-6 mb-6">
        <h2 class="text-xl font-bold mb-4">📋 Logs Consolidados</h2>
        <div class="space-y-2 max-h-80 overflow-y-auto">
          <div v-for="(log, idx) in consolidatedLogs" :key="idx" class="p-3 bg-gray-50 rounded text-sm font-mono" :class="log.level === 'ERROR' ? 'text-red-600' : log.level === 'WARN' ? 'text-orange-600' : 'text-gray-700'">
            <span class="text-gray-500">[{{ log.timestamp }}]</span>
            <span class="font-semibold">[{{ log.level }}]</span>
            {{ log.message }}
          </div>
        </div>
      </div>

      <!-- Integrated Monitoring -->
      <div class="bg-white rounded-lg shadow-md p-6 mb-6">
        <h2 class="text-xl font-bold mb-4">🔍 Monitoramento Integrado</h2>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div class="p-4 bg-blue-50 rounded-md">
            <p class="text-sm font-semibold mb-2">Sistema</p>
            <p class="text-2xl font-bold text-blue-600">{{ systemStatus }}</p>
          </div>
          <div class="p-4 bg-green-50 rounded-md">
            <p class="text-sm font-semibold mb-2">Uptime</p>
            <p class="text-2xl font-bold text-green-600">{{ uptime }}%</p>
          </div>
          <div class="p-4 bg-orange-50 rounded-md">
            <p class="text-sm font-semibold mb-2">Alertas Ativos</p>
            <p class="text-2xl font-bold text-orange-600">{{ activeAlerts.length }}</p>
          </div>
          <div class="p-4 bg-purple-50 rounded-md">
            <p class="text-sm font-semibold mb-2">Última Sincronização</p>
            <p class="text-2xl font-bold text-purple-600">{{ lastSync }}</p>
          </div>
        </div>
      </div>

      <!-- Features List -->
      <div class="bg-white rounded-lg shadow-md p-6">
        <h2 class="text-xl font-bold mb-4">✅ Funcionalidades</h2>
        <ul class="space-y-2">
          <li class="text-gray-700">✓ Alertas AWS SNS</li>
          <li class="text-gray-700">✓ Logs consolidados</li>
          <li class="text-gray-700">✓ Monitoramento integrado</li>
        </ul>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'

const activeAlerts = ref([
  { id: 1, title: 'Umidade Baixa', message: 'Umidade do solo abaixo de 40%', severity: 'Alta', color: '#ef4444', timestamp: '2025-01-22 14:32' },
  { id: 2, title: 'Temperatura Elevada', message: 'Temperatura acima de 35°C', severity: 'Média', color: '#f97316', timestamp: '2025-01-22 14:15' },
  { id: 3, title: 'Sensor Desconectado', message: 'Sensor 3 sem comunicação há 5 minutos', severity: 'Crítica', color: '#dc2626', timestamp: '2025-01-22 14:05' }
])

const newAlert = ref({
  title: '',
  message: '',
  severity: 'Média'
})

const alertStats = ref({
  critical: 1,
  high: 2,
  medium: 3,
  low: 5
})

const consolidatedLogs = ref([
  { timestamp: '14:32:15', level: 'ERROR', message: 'Sensor 3 connection lost' },
  { timestamp: '14:31:42', level: 'WARN', message: 'Soil moisture below threshold' },
  { timestamp: '14:30:18', level: 'INFO', message: 'Irrigation pump activated' },
  { timestamp: '14:29:05', level: 'INFO', message: 'Data sync completed' },
  { timestamp: '14:28:33', level: 'WARN', message: 'Temperature threshold exceeded' }
])

const systemStatus = ref('Operacional')
const uptime = ref(99.8)
const lastSync = ref('2 min atrás')

const createAlert = () => {
  if (newAlert.value.title && newAlert.value.message) {
    const severityColors = {
      'Crítica': '#dc2626',
      'Alta': '#ef4444',
      'Média': '#f97316',
      'Baixa': '#3b82f6'
    }
    
    activeAlerts.value.unshift({
      id: activeAlerts.value.length + 1,
      title: newAlert.value.title,
      message: newAlert.value.message,
      severity: newAlert.value.severity,
      color: severityColors[newAlert.value.severity as keyof typeof severityColors],
      timestamp: new Date().toLocaleString('pt-BR')
    })
    
    newAlert.value = { title: '', message: '', severity: 'Média' }
  }
}
</script>
