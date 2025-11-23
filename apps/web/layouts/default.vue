<template>
  <div class="relative flex min-h-screen w-full" style="background-color: #f6f8f7;" :class="{ 'dark': isDark }">
    <!-- SideNavBar -->
    <aside class="flex h-screen w-64 flex-col justify-between bg-white dark:bg-[#1a2f24] p-4 border-r border-gray-200 dark:border-gray-900/50 sticky top-0 shrink-0">
      <div class="flex flex-col gap-4">
        <!-- Logo Section -->
        <div class="flex items-center gap-3">
          <div class="flex items-center justify-center w-10 h-10 rounded-full bg-primary text-white font-bold text-lg">
            🌾
          </div>
          <div class="flex flex-col">
            <h1 class="text-gray-900 dark:text-white text-base font-medium leading-normal">FarmTech</h1>
            <p class="text-primary text-sm font-normal leading-normal">Consolidado</p>
          </div>
        </div>

        <!-- Navigation -->
        <ClientOnly>
          <nav class="flex flex-col gap-2 mt-4">
            <NuxtLink to="/" class="flex items-center gap-3 px-3 py-2 rounded-lg text-gray-900 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-background-dark" :class="{ 'bg-primary/20 text-primary dark:text-white': $route.path === '/' }">
              <span class="material-symbols-outlined text-base">dashboard</span>
              <p class="text-sm font-medium leading-normal">Dashboard</p>
            </NuxtLink>
            
            <NuxtLink to="/fase1" class="flex items-center gap-3 px-3 py-2 rounded-lg text-gray-900 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-background-dark" :class="{ 'bg-primary/20 text-primary dark:text-white': $route.path.includes('fase1') }">
              <span class="material-symbols-outlined text-base">cloud</span>
              <p class="text-sm font-medium leading-normal">Dados & Clima</p>
            </NuxtLink>

            <NuxtLink to="/database" class="flex items-center gap-3 px-3 py-2 rounded-lg text-gray-900 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-background-dark" :class="{ 'bg-primary/20 text-primary dark:text-white': $route.path === '/database' }">
              <span class="material-symbols-outlined text-base">database</span>
              <p class="text-sm font-medium leading-normal">Banco de Dados (Visual)</p>
            </NuxtLink>

            <NuxtLink to="/fase2" class="flex items-center gap-3 px-3 py-2 rounded-lg text-gray-900 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-background-dark" :class="{ 'bg-primary/20 text-primary dark:text-white': $route.path.includes('fase2') }">
              <span class="material-symbols-outlined text-base">edit_note</span>
              <p class="text-sm font-medium leading-normal">Lançamentos de Dados</p>
            </NuxtLink>

            <NuxtLink to="/fase3" class="flex items-center gap-3 px-3 py-2 rounded-lg text-gray-900 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-background-dark" :class="{ 'bg-primary/20 text-primary dark:text-white': $route.path.includes('fase3') }">
              <span class="material-symbols-outlined text-base">wifi</span>
              <p class="text-sm font-medium leading-normal">IoT</p>
            </NuxtLink>

            <NuxtLink to="/fase4" class="flex items-center gap-3 px-3 py-2 rounded-lg text-gray-900 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-background-dark" :class="{ 'bg-primary/20 text-primary dark:text-white': $route.path.includes('fase4') }">
              <span class="material-symbols-outlined text-base">bar_chart</span>
              <p class="text-sm font-medium leading-normal">Analytics</p>
            </NuxtLink>

            <NuxtLink to="/fase5" class="flex items-center gap-3 px-3 py-2 rounded-lg text-gray-900 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-background-dark" :class="{ 'bg-primary/20 text-primary dark:text-white': $route.path.includes('fase5') }">
              <span class="material-symbols-outlined text-base">cloud_upload</span>
              <p class="text-sm font-medium leading-normal">AWS</p>
            </NuxtLink>

            <NuxtLink to="/fase6" class="flex items-center gap-3 px-3 py-2 rounded-lg text-gray-900 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-background-dark" :class="{ 'bg-primary/20 text-primary dark:text-white': $route.path.includes('fase6') }">
              <span class="material-symbols-outlined text-base">center_focus_strong</span>
              <p class="text-sm font-medium leading-normal">Visão Computacional</p>
            </NuxtLink>

            <NuxtLink to="/fase7" class="flex items-center gap-3 px-3 py-2 rounded-lg text-gray-900 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-background-dark" :class="{ 'bg-primary/20 text-primary dark:text-white': $route.path.includes('fase7') }">
              <span class="material-symbols-outlined text-base">notifications</span>
              <p class="text-sm font-medium leading-normal">Alertas</p>
            </NuxtLink>

            <NuxtLink to="/ir-alem" class="flex items-center gap-3 px-3 py-2 rounded-lg text-gray-900 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-background-dark" :class="{ 'bg-primary/20 text-primary dark:text-white': $route.path.includes('ir-alem') }">
              <span class="material-symbols-outlined text-base">rocket_launch</span>
              <p class="text-sm font-medium leading-normal">Ir Além do Além</p>
            </NuxtLink>
          </nav>
        </ClientOnly>
      </div>

      <!-- Bottom Section -->
      <div class="flex flex-col gap-2">

        <div class="flex flex-col gap-1 mt-2">
          <a class="flex items-center gap-3 px-3 py-2 rounded-lg text-gray-900 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-background-dark" href="#">
            <span class="material-symbols-outlined text-base">settings</span>
            <p class="text-sm font-medium leading-normal">Configurações</p>
          </a>
          <a class="flex items-center gap-3 px-3 py-2 rounded-lg text-gray-900 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-background-dark" href="#">
            <span class="material-symbols-outlined text-base">help</span>
            <p class="text-sm font-medium leading-normal">Ajuda</p>
          </a>
        </div>
      </div>
    </aside>

    <!-- Main Content -->
    <main class="flex-1 overflow-y-auto">
      <slot />
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'

const isDark = ref(false)

// Check for dark mode preference
if (process.client) {
  isDark.value = document.documentElement.classList.contains('dark')
}
</script>

<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;900&display=swap');
@import url('https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:wght,FILL@100..700,0..1&display=swap');

.material-symbols-outlined {
  font-variation-settings: 'FILL' 0, 'wght' 400, 'GRAD' 0, 'opsz' 24;
}
</style>
