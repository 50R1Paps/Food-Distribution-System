<script setup lang="ts">
import { ref, computed } from 'vue'
import { importData } from '@/api/dataTransfer'
import type { ImportPreview } from '@/types'

const file = ref<File | null>(null)
const fileContent = ref<Record<string, unknown> | null>(null)
const loading = ref(false)
const error = ref('')
const preview = ref<ImportPreview | null>(null)
const mode = ref<'merge' | 'replace'>('merge')
const confirmed = ref(false)
const result = ref<ImportPreview | null>(null)

const summaryLabels: Record<string, string> = {
  package_types: 'Tipi di pacco',
  families: 'Famiglie',
  persons: 'Membri',
  distributions: 'Distribuzioni',
}

const hasConflicts = computed(() => {
  return preview.value && preview.value.conflicts.length > 0
})

function handleFileChange(e: Event) {
  const target = e.target as HTMLInputElement
  error.value = ''
  preview.value = null
  result.value = null
  confirmed.value = false

  if (!target.files || target.files.length === 0) {
    file.value = null
    fileContent.value = null
    return
  }

  file.value = target.files[0]
  const reader = new FileReader()
  reader.onload = (ev) => {
    try {
      fileContent.value = JSON.parse(ev.target?.result as string)
    } catch {
      error.value = 'File JSON non valido'
      fileContent.value = null
    }
  }
  reader.readAsText(file.value)
}

async function handlePreview() {
  if (!fileContent.value) return
  loading.value = true
  error.value = ''
  preview.value = null
  result.value = null
  confirmed.value = false

  try {
    preview.value = await importData(fileContent.value, {
      dry_run: true,
      mode: mode.value,
    })
  } catch (e: any) {
    error.value = e.response?.data?.detail || 'Errore durante l\'anteprima'
  } finally {
    loading.value = false
  }
}

async function handleConfirm() {
  if (!fileContent.value) return
  loading.value = true
  error.value = ''

  try {
    result.value = await importData(fileContent.value, {
      dry_run: false,
      mode: mode.value,
    })
    confirmed.value = true
    preview.value = null
  } catch (e: any) {
    error.value = e.response?.data?.detail || 'Errore durante l\'importazione'
  } finally {
    loading.value = false
  }
}

function reset() {
  file.value = null
  fileContent.value = null
  preview.value = null
  result.value = null
  error.value = ''
  confirmed.value = false
}
</script>

<template>
  <div class="max-w-3xl mx-auto">
    <h1 class="text-3xl font-bold mb-6">Importa Dati</h1>

    <!-- Step 1: File upload -->
    <div class="bg-white rounded-lg shadow p-6 mb-6">
      <h2 class="text-xl font-semibold mb-4">1. Seleziona File JSON</h2>
      <input
        type="file"
        accept="application/json,.json"
        @change="handleFileChange"
        class="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-md file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100"
      />
      <p v-if="file" class="mt-2 text-sm text-gray-500">
        File selezionato: <span class="font-medium">{{ file.name }}</span>
      </p>
    </div>

    <!-- Step 2: Mode selection + preview -->
    <div v-if="fileContent" class="bg-white rounded-lg shadow p-6 mb-6">
      <h2 class="text-xl font-semibold mb-4">2. Modalità di Importazione</h2>

      <div class="space-y-2 mb-4">
        <label class="flex items-center space-x-2 cursor-pointer">
          <input type="radio" v-model="mode" value="merge" class="text-blue-600" />
          <span>
            <strong>Unisci</strong> — Aggiungi solo dati nuovi, ignora duplicati esistenti
          </span>
        </label>
        <label class="flex items-center space-x-2 cursor-pointer">
          <input type="radio" v-model="mode" value="replace" class="text-blue-600" />
          <span>
            <strong>Sostituisci</strong> — Cancella tutti i dati esistenti e inserisci quelli del file
          </span>
        </label>
      </div>

      <button
        @click="handlePreview"
        :disabled="loading"
        class="bg-gray-600 hover:bg-gray-700 text-white font-semibold px-6 py-2.5 rounded-md transition-colors disabled:opacity-50"
      >
        {{ loading && !confirmed ? 'Elaborazione...' : 'Anteprima Importazione' }}
      </button>
    </div>

    <!-- Preview results -->
    <div v-if="preview" class="bg-white rounded-lg shadow p-6 mb-6">
      <h2 class="text-xl font-semibold mb-4">3. Anteprima</h2>

      <div class="overflow-x-auto mb-4">
        <table class="w-full text-sm">
          <thead>
            <tr class="border-b">
              <th class="text-left py-2 px-3">Entità</th>
              <th class="text-center py-2 px-3">Nuovi</th>
              <th class="text-center py-2 px-3">Esistenti</th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="(entry, key) in preview.summary"
              :key="key"
              class="border-b border-gray-100"
            >
              <td class="py-2 px-3 font-medium">{{ summaryLabels[key] || key }}</td>
              <td class="text-center py-2 px-3 text-green-600 font-semibold">{{ entry.new }}</td>
              <td class="text-center py-2 px-3 text-orange-600 font-semibold">{{ entry.existing }}</td>
            </tr>
          </tbody>
        </table>
      </div>

      <div v-if="hasConflicts" class="mb-4">
        <h3 class="font-semibold text-orange-600 mb-2">Conflitti rilevati ({{ preview.conflicts.length }})</h3>
        <ul class="text-sm text-gray-600 space-y-1 max-h-40 overflow-y-auto">
          <li
            v-for="(conflict, i) in preview.conflicts"
            :key="i"
            class="flex items-start space-x-2"
          >
            <span class="text-orange-500 mt-0.5">⚠</span>
            <span>
              <strong>{{ conflict.entity }}</strong> ({{ conflict.identifier }}): {{ conflict.message }}
            </span>
          </li>
        </ul>
        <p v-if="mode === 'merge'" class="text-sm text-gray-500 mt-2">
          In modalità "Unisci", i conflitti verranno ignorati (i dati esistenti non verranno modificati).
        </p>
        <p v-else class="text-sm text-red-600 mt-2">
          In modalità "Sostituisci", tutti i dati esistenti verranno cancellati.
        </p>
      </div>

      <div class="flex space-x-3">
        <button
          @click="handleConfirm"
          :disabled="loading"
          class="bg-red-600 hover:bg-red-700 text-white font-semibold px-6 py-2.5 rounded-md transition-colors disabled:opacity-50"
        >
          Conferma Importazione
        </button>
        <button
          @click="reset"
          class="bg-gray-200 hover:bg-gray-300 text-gray-700 font-semibold px-6 py-2.5 rounded-md transition-colors"
        >
          Annulla
        </button>
      </div>
    </div>

    <!-- Import result -->
    <div v-if="result && confirmed" class="bg-green-50 border border-green-200 rounded-lg shadow p-6 mb-6">
      <h2 class="text-xl font-semibold text-green-700 mb-4">Importazione Completata</h2>

      <div class="overflow-x-auto mb-4">
        <table class="w-full text-sm">
          <thead>
            <tr class="border-b">
              <th class="text-left py-2 px-3">Entità</th>
              <th class="text-center py-2 px-3">Nuovi</th>
              <th class="text-center py-2 px-3">Esistenti</th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="(entry, key) in result.summary"
              :key="key"
              class="border-b border-gray-100"
            >
              <td class="py-2 px-3 font-medium">{{ summaryLabels[key] || key }}</td>
              <td class="text-center py-2 px-3 text-green-600 font-semibold">{{ entry.new }}</td>
              <td class="text-center py-2 px-3 text-orange-600 font-semibold">{{ entry.existing }}</td>
            </tr>
          </tbody>
        </table>
      </div>

      <button
        @click="reset"
        class="bg-blue-600 hover:bg-blue-700 text-white font-semibold px-6 py-2.5 rounded-md transition-colors"
      >
        Nuova Importazione
      </button>
    </div>

    <!-- Error -->
    <div v-if="error" class="bg-red-50 border border-red-200 rounded-lg p-4 mt-4">
      <p class="text-red-700 font-medium">{{ error }}</p>
    </div>
  </div>
</template>
