<script setup lang="ts">
import { ref } from 'vue'
import { RouterLink, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const auth = useAuthStore()
const searchQuery = ref('')

function handleSearch() {
  if (searchQuery.value.trim()) {
    router.push({ name: 'search', query: { q: searchQuery.value.trim() } })
    searchQuery.value = ''
  }
}

function handleLogout() {
  auth.logout()
  router.push('/login')
}

const navItems = [
  { to: '/', label: 'Home' },
  { to: '/families', label: 'Famiglie' },
  { to: '/distribute', label: 'Distribuzione' },
  { to: '/search', label: 'Ricerca' },
]

const dataMenuOpen = ref(false)

function toggleDataMenu() {
  dataMenuOpen.value = !dataMenuOpen.value
}

function closeDataMenu() {
  dataMenuOpen.value = false
}
</script>

<template>
  <nav class="bg-gray-800 text-white shadow-md">
    <div class="container mx-auto px-4">
      <div class="flex items-center justify-between h-16">
        <RouterLink to="/" class="text-xl font-bold">
          Distribuzione Alimentare
        </RouterLink>
        <ul class="flex items-center space-x-6">
          <li v-for="item in navItems" :key="item.to">
            <RouterLink
              :to="item.to"
              class="hover:text-gray-300 transition-colors"
              active-class="text-gray-300 border-b-2 border-gray-300 pb-1"
            >
              {{ item.label }}
            </RouterLink>
          </li>
          <li>
            <form @submit.prevent="handleSearch" class="flex items-center">
              <input
                v-model="searchQuery"
                type="text"
                placeholder="Cerca..."
                class="bg-gray-700 text-white text-sm px-3 py-1.5 rounded-l-md border-0 focus:ring-2 focus:ring-blue-500 focus:outline-none w-40"
              />
              <button
                type="submit"
                class="bg-blue-600 hover:bg-blue-700 text-white text-sm px-3 py-1.5 rounded-r-md transition-colors"
              >
                🔍
              </button>
            </form>
          </li>
          <li class="relative" @mouseleave="closeDataMenu">
            <button
              @click="toggleDataMenu"
              @mouseenter="dataMenuOpen = true"
              class="hover:text-gray-300 transition-colors flex items-center space-x-1"
              :class="{ 'text-gray-300 border-b-2 border-gray-300 pb-1': dataMenuOpen }"
            >
              <span>Gestione Dati</span>
              <svg class="w-4 h-4 transition-transform" :class="{ 'rotate-180': dataMenuOpen }" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
              </svg>
            </button>
            <ul
              v-if="dataMenuOpen"
              class="absolute right-0 mt-2 w-48 bg-gray-700 rounded-md shadow-lg py-1 z-50"
            >
              <li>
                <RouterLink
                  to="/export"
                  class="block px-4 py-2 text-sm hover:bg-gray-600 transition-colors"
                  @click="closeDataMenu"
                >
                  Esporta Dati
                </RouterLink>
              </li>
              <li>
                <RouterLink
                  to="/import"
                  class="block px-4 py-2 text-sm hover:bg-gray-600 transition-colors"
                  @click="closeDataMenu"
                >
                  Importa Dati
                </RouterLink>
              </li>
            </ul>
          </li>
          <li>
            <button
              @click="handleLogout"
              class="bg-gray-700 hover:bg-gray-600 text-white text-sm px-3 py-1.5 rounded-md transition-colors"
            >
              Esci
            </button>
          </li>
        </ul>
      </div>
    </div>
  </nav>
</template>
