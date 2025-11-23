<template>
  <div class="min-h-screen bg-gray-50 p-8">
    <div class="max-w-6xl mx-auto">
      <NuxtLink to="/" class="text-blue-600 hover:text-blue-700 mb-6 inline-block">← Voltar</NuxtLink>
      <h1 class="text-3xl font-bold text-gray-800 mb-6">☁️ Fase 5: Infraestrutura AWS</h1>
      
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-6">
        <!-- AWS Services Status -->
        <div v-for="service in awsServices" :key="service.name" class="bg-white rounded-lg shadow-md p-6">
          <h3 class="text-lg font-bold mb-3">{{ service.icon }} {{ service.name }}</h3>
          <div class="space-y-2">
            <p class="text-sm text-gray-700"><strong>Status:</strong> <span :class="service.status === 'Ativo' ? 'text-green-600' : 'text-red-600'">{{ service.status }}</span></p>
            <p class="text-sm text-gray-700"><strong>Instâncias:</strong> {{ service.instances }}</p>
            <p class="text-sm text-gray-700"><strong>Custo/mês:</strong> R$ {{ service.cost }}</p>
          </div>
        </div>
      </div>

      <!-- CloudWatch Logs -->
      <div class="bg-white rounded-lg shadow-md p-6 mb-6">
        <h2 class="text-xl font-bold mb-4">📋 Logs CloudWatch</h2>
        <div class="space-y-2 max-h-64 overflow-y-auto">
          <div v-for="(log, idx) in logs" :key="idx" class="p-2 bg-gray-50 rounded text-sm font-mono text-gray-700">
            <span class="text-gray-500">[{{ log.timestamp }}]</span> {{ log.message }}
          </div>
        </div>
      </div>

      <!-- Cost Analysis -->
      <div class="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
        <div class="bg-white rounded-lg shadow-md p-6">
          <h2 class="text-xl font-bold mb-4">💰 Análise de Custos</h2>
          <div class="space-y-3">
            <div class="flex justify-between items-center p-2 bg-blue-50 rounded">
              <span>EC2</span>
              <span class="font-bold">R$ 450</span>
            </div>
            <div class="flex justify-between items-center p-2 bg-blue-50 rounded">
              <span>RDS</span>
              <span class="font-bold">R$ 280</span>
            </div>
            <div class="flex justify-between items-center p-2 bg-blue-50 rounded">
              <span>S3</span>
              <span class="font-bold">R$ 120</span>
            </div>
            <div class="flex justify-between items-center p-2 bg-green-50 rounded border-t-2 border-green-200">
              <span class="font-bold">Total/mês</span>
              <span class="font-bold text-green-600">R$ 850</span>
            </div>
          </div>
        </div>

        <div class="bg-white rounded-lg shadow-md p-6">
          <h2 class="text-xl font-bold mb-4">📈 Uso de Recursos</h2>
          <div class="space-y-4">
            <div>
              <p class="text-sm font-semibold mb-1">CPU</p>
              <div class="w-full bg-gray-200 rounded-full h-2">
                <div class="bg-blue-600 h-2 rounded-full" style="width: 65%"></div>
              </div>
              <p class="text-xs text-gray-600 mt-1">65% utilizado</p>
            </div>
            <div>
              <p class="text-sm font-semibold mb-1">Memória</p>
              <div class="w-full bg-gray-200 rounded-full h-2">
                <div class="bg-orange-600 h-2 rounded-full" style="width: 78%"></div>
              </div>
              <p class="text-xs text-gray-600 mt-1">78% utilizado</p>
            </div>
            <div>
              <p class="text-sm font-semibold mb-1">Armazenamento</p>
              <div class="w-full bg-gray-200 rounded-full h-2">
                <div class="bg-green-600 h-2 rounded-full" style="width: 42%"></div>
              </div>
              <p class="text-xs text-gray-600 mt-1">42% utilizado</p>
            </div>
          </div>
        </div>
      </div>

      <!-- Features List -->
      <div class="bg-white rounded-lg shadow-md p-6">
        <h2 class="text-xl font-bold mb-4">✅ Funcionalidades</h2>
        <ul class="space-y-2">
          <li class="text-gray-700">✓ Status dos serviços AWS</li>
          <li class="text-gray-700">✓ Visualização de logs CloudWatch</li>
          <li class="text-gray-700">✓ Análise de custos</li>
        </ul>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'

const awsServices = ref([
  { icon: '🖥️', name: 'EC2', status: 'Ativo', instances: 3, cost: '450' },
  { icon: '🗄️', name: 'RDS', status: 'Ativo', instances: 1, cost: '280' },
  { icon: '📦', name: 'S3', status: 'Ativo', instances: 5, cost: '120' },
  { icon: '🔐', name: 'IAM', status: 'Ativo', instances: 12, cost: '0' },
  { icon: '📨', name: 'SNS', status: 'Ativo', instances: 2, cost: '15' },
  { icon: '📊', name: 'CloudWatch', status: 'Ativo', instances: 1, cost: '85' }
])

const logs = ref([
  { timestamp: '2025-01-22 14:32:15', message: '[INFO] EC2 instance i-0123456789 started' },
  { timestamp: '2025-01-22 14:31:42', message: '[INFO] RDS backup completed successfully' },
  { timestamp: '2025-01-22 14:30:18', message: '[WARN] CPU usage exceeded 80% threshold' },
  { timestamp: '2025-01-22 14:29:05', message: '[INFO] S3 sync operation completed' },
  { timestamp: '2025-01-22 14:28:33', message: '[INFO] SNS notification sent to subscribers' }
])
</script>
