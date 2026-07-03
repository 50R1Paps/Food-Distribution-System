<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import type { Family } from '@/types'
import { createFamily, listFamilies } from '@/api/families'

const families = ref<Family[]>([])
const total = ref(0)
const page = ref(1)
const pageSize = 20
const search = ref('')
const loading = ref(false)
const error = ref('')

const showForm = ref(false)
const formName = ref('')
const formAddress = ref('')
const formContact = ref('')

const totalPages = computed(() => Math.max(1, Math.ceil(total.value / pageSize)))

async function load() {
  loading.value = true
  error.value = ''
  try {
    const data = await listFamilies({
      search: search.value || undefined,
      page: page.value,
      page_size: pageSize,
    })
    families.value = data.items
    total.value = data.total
  } catch {
    error.value = 'Errore nel caricamento delle famiglie'
  } finally {
    loading.value = false
  }
}

onMounted(load)

function doSearch() {
  page.value = 1
  load()
}

function changePage(delta: number) {
  const next = page.value + delta
  if (next < 1 || next > totalPages.value) return
  page.value = next
  load()
}

async function submitFamily() {
  loading.value = true
  error.value = ''
  try {
    await createFamily({
      family_name: formName.value,
      address: formAddress.value,
      contact_number: formContact.value || null,
    })
    formName.value = ''
    formAddress.value = ''
    formContact.value = ''
    showForm.value = false
    await load()
  } catch (e: any) {
    error.value = e?.response?.data?.detail ?? 'Errore durante la registrazione'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div>
    <div class="flex items-center justify-between mb-6">
      <h1 class="text-3xl font-bold">Famiglie</h1>
      <button
        @click="showForm = !showForm"
        class="bg-gray-800 hover:bg-gray-700 text-white px-4 py-2 rounded-md text-sm transition-colors"
      >
        {{ showForm ? 'Chiudi' : 'Registra famiglia' }}
      </button>
    </div>

    <p v-if="error" class="text-red-600 mb-4">{{ error }}</p>

    <!-- Form registrazione -->
    <div v-if="showForm" class="bg-white rounded-lg shadow p-6 mb-6">
      <h2 class="text-xl font-semibold mb-4">Nuova famiglia</h2>
      <form @submit.prevent="submitFamily" class="space-y-4">
        <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Nome famiglia</label>
            <input
              v-model="formName"
              type="text"
              required
              class="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-gray-600"
            />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Indirizzo</label>
            <input
              v-model="formAddress"
              type="text"
              required
              class="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-gray-600"
            />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Telefono (opzionale)</label>
            <input
              v-model="formContact"
              type="text"
              class="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-gray-600"
            />
          </div>
        </div>
        <button
          type="submit"
          :disabled="loading"
          class="bg-gray-800 hover:bg-gray-700 text-white px-4 py-2 rounded-md text-sm transition-colors disabled:opacity-50"
        >
          Registra
        </button>
      </form>
    </div>

    <!-- Ricerca -->
    <form @submit.prevent="doSearch" class="flex gap-3 mb-6">
      <input
        v-model="search"
        type="text"
        placeholder="Cerca per nome famiglia…"
        class="flex-1 border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-gray-600"
      />
      <button
        type="submit"
        class="bg-gray-800 hover:bg-gray-700 text-white px-4 py-2 rounded-md text-sm transition-colors"
      >
        Cerca
      </button>
    </form>

    <!-- Lista -->
    <div class="bg-white rounded-lg shadow overflow-hidden">
      <table v-if="families.length" class="w-full text-sm">
        <thead>
          <tr class="text-left text-gray-500 border-b bg-gray-50">
            <th class="py-3 px-4">Nome famiglia</th>
            <th class="py-3 px-4">Indirizzo</th>
            <th class="py-3 px-4">Telefono</th>
            <th class="py-3 px-4"></th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="f in families" :key="f.id" class="border-b last:border-0 hover:bg-gray-50">
            <td class="py-3 px-4 font-medium">{{ f.family_name }}</td>
            <td class="py-3 px-4">{{ f.address }}</td>
            <td class="py-3 px-4">{{ f.contact_number || '—' }}</td>
            <td class="py-3 px-4 text-right">
              <router-link :to="`/families/${f.id}`" class="text-blue-600 hover:underline">
                Dettagli
              </router-link>
            </td>
          </tr>
        </tbody>
      </table>
      <p v-else-if="!loading" class="text-gray-500 p-6">Nessuna famiglia trovata.</p>
      <p v-else class="text-gray-500 p-6">Caricamento…</p>
    </div>

    <!-- Paginazione -->
    <div v-if="totalPages > 1" class="flex items-center justify-center gap-4 mt-6">
      <button
        @click="changePage(-1)"
        :disabled="page <= 1"
        class="bg-gray-200 hover:bg-gray-300 px-3 py-1.5 rounded-md text-sm disabled:opacity-50"
      >
        Precedente
      </button>
      <span class="text-sm text-gray-600">Pagina {{ page }} di {{ totalPages }}</span>
      <button
        @click="changePage(1)"
        :disabled="page >= totalPages"
        class="bg-gray-200 hover:bg-gray-300 px-3 py-1.5 rounded-md text-sm disabled:opacity-50"
      >
        Successiva
      </button>
    </div>
  </div>
</template>
