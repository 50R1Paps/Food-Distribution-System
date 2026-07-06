<script setup lang="ts">
import { ref, watch, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { search as searchApi } from '@/api/search'
import type { SearchResult } from '@/types'

const route = useRoute()
const router = useRouter()

const query = ref((route.query.q as string) || '')
const activeTab = ref<'families' | 'persons'>('families')
const loading = ref(false)
const error = ref('')
const result = ref<SearchResult | null>(null)
const currentPage = ref(1)
const pageSize = 20

async function performSearch() {
  if (!query.value.trim()) {
    result.value = null
    return
  }
  loading.value = true
  error.value = ''
  try {
    result.value = await searchApi(query.value.trim(), {
      page: currentPage.value,
      page_size: pageSize,
    })
    if (activeTab.value === 'families' && result.value.families.length === 0 && result.value.persons.length > 0) {
      activeTab.value = 'persons'
    } else if (activeTab.value === 'persons' && result.value.persons.length === 0 && result.value.families.length > 0) {
      activeTab.value = 'families'
    }
  } catch (e: any) {
    error.value = e.response?.data?.detail || 'Errore durante la ricerca'
  } finally {
    loading.value = false
  }
}

function handleSubmit() {
  currentPage.value = 1
  router.replace({ name: 'search', query: { q: query.value.trim() } })
  performSearch()
}

function goToFamily(id: number) {
  router.push({ name: 'family-details', params: { id } })
}

function goToPersonFamily(familyId: number) {
  router.push({ name: 'family-details', params: { id: familyId } })
}

function changePage(delta: number) {
  currentPage.value += delta
  performSearch()
}

watch(() => route.query.q, (newQ) => {
  if (newQ && newQ !== query.value) {
    query.value = newQ as string
    currentPage.value = 1
    performSearch()
  }
})

onMounted(() => {
  if (query.value.trim()) {
    performSearch()
  }
})
</script>

<template>
  <div>
    <h1 class="text-3xl font-bold mb-6">Ricerca</h1>

    <form @submit.prevent="handleSubmit" class="mb-6">
      <div class="flex gap-2">
        <input
          v-model="query"
          type="text"
          placeholder="Cerca famiglie o persone..."
          class="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
        />
        <button
          type="submit"
          class="bg-blue-600 hover:bg-blue-700 text-white px-6 py-2 rounded-lg transition-colors"
          :disabled="loading"
        >
          {{ loading ? 'Ricerca...' : 'Cerca' }}
        </button>
      </div>
    </form>

    <div v-if="error" class="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
      {{ error }}
    </div>

    <div v-if="result" class="mt-4">
      <p class="text-gray-600 mb-4">
        {{ result.total }} risultati per "{{ query }}"
      </p>

      <div class="flex border-b border-gray-200 mb-4">
        <button
          @click="activeTab = 'families'"
          class="px-4 py-2 font-medium transition-colors"
          :class="activeTab === 'families' ? 'text-blue-600 border-b-2 border-blue-600' : 'text-gray-500 hover:text-gray-700'"
        >
          Famiglie ({{ result.families.length }})
        </button>
        <button
          @click="activeTab = 'persons'"
          class="px-4 py-2 font-medium transition-colors"
          :class="activeTab === 'persons' ? 'text-blue-600 border-b-2 border-blue-600' : 'text-gray-500 hover:text-gray-700'"
        >
          Individui ({{ result.persons.length }})
        </button>
      </div>

      <div v-if="activeTab === 'families'">
        <div v-if="result.families.length === 0" class="text-gray-500 py-8 text-center">
          Nessuna famiglia trovata
        </div>
        <ul v-else class="space-y-2">
          <li
            v-for="family in result.families"
            :key="family.id"
            @click="goToFamily(family.id)"
            class="bg-white border border-gray-200 rounded-lg p-4 hover:shadow-md hover:border-blue-300 cursor-pointer transition-all"
          >
            <div class="flex items-center justify-between">
              <div>
                <h3 class="font-semibold text-lg text-gray-800">{{ family.family_name }}</h3>
                <p class="text-sm text-gray-500">{{ family.address }}</p>
                <p v-if="family.contact_number" class="text-sm text-gray-400">Tel: {{ family.contact_number }}</p>
              </div>
              <span class="text-blue-500 text-sm">Visualizza →</span>
            </div>
          </li>
        </ul>
      </div>

      <div v-if="activeTab === 'persons'">
        <div v-if="result.persons.length === 0" class="text-gray-500 py-8 text-center">
          Nessun individuo trovato
        </div>
        <ul v-else class="space-y-2">
          <li
            v-for="person in result.persons"
            :key="person.id"
            @click="goToPersonFamily(person.family_id)"
            class="bg-white border border-gray-200 rounded-lg p-4 hover:shadow-md hover:border-blue-300 cursor-pointer transition-all"
          >
            <div class="flex items-center justify-between">
              <div>
                <h3 class="font-semibold text-lg text-gray-800">{{ person.last_name }}, {{ person.first_name }}</h3>
                <p class="text-sm text-gray-500">Famiglia #{{ person.family_id }}</p>
                <p v-if="person.fingerprint_id" class="text-sm text-gray-400">Impronta: {{ person.fingerprint_id }}</p>
              </div>
              <span class="text-blue-500 text-sm">Vai alla famiglia →</span>
            </div>
          </li>
        </ul>
      </div>

      <div class="flex items-center justify-between mt-6" v-if="result.total > pageSize">
        <button
          @click="changePage(-1)"
          :disabled="currentPage === 1"
          class="px-4 py-2 text-sm rounded-lg border border-gray-300 disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-50 transition-colors"
        >
          ← Precedente
        </button>
        <span class="text-sm text-gray-600">Pagina {{ currentPage }}</span>
        <button
          @click="changePage(1)"
          :disabled="currentPage * pageSize >= result.total"
          class="px-4 py-2 text-sm rounded-lg border border-gray-300 disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-50 transition-colors"
        >
          Successiva →
        </button>
      </div>
    </div>

    <div v-if="!result && !loading && !error" class="text-gray-500 py-8 text-center">
      Inserisci un termine di ricerca per trovare famiglie e persone.
    </div>
  </div>
</template>

