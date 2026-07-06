<script setup lang="ts">
import { ref } from 'vue'
import { exportData } from '@/api/dataTransfer'

const loading = ref(false)
const error = ref('')
const success = ref('')

async function handleExport() {
  loading.value = true
  error.value = ''
  success.value = ''
  try {
    const blob = await exportData()
    const url = window.URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    const now = new Date()
    const stamp = `${now.getFullYear()}${String(now.getMonth() + 1).padStart(2, '0')}${String(now.getDate()).padStart(2, '0')}_${String(now.getHours()).padStart(2, '0')}${String(now.getMinutes()).padStart(2, '0')}${String(now.getSeconds()).padStart(2, '0')}`
    a.download = `export_${stamp}.json`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    window.URL.revokeObjectURL(url)
    success.value = 'Esportazione completata con successo'
  } catch (e: any) {
    error.value = e.response?.data?.detail || 'Errore durante l\'esportazione'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="max-w-2xl mx-auto">
    <h1 class="text-3xl font-bold mb-6">Esporta Dati</h1>

    <div class="bg-white rounded-lg shadow p-6">
      <p class="text-gray-600 mb-4">
        Esporta tutti i dati del sistema (famiglie, membri, distribuzioni e tipi di pacco)
        in un singolo file JSON per backup o trasferimento offline.
      </p>

      <button
        @click="handleExport"
        :disabled="loading"
        class="bg-blue-600 hover:bg-blue-700 text-white font-semibold px-6 py-3 rounded-md transition-colors disabled:opacity-50"
      >
        {{ loading ? 'Esportazione in corso...' : 'Scarica File JSON' }}
      </button>

      <p v-if="success" class="mt-4 text-green-600 font-medium">{{ success }}</p>
      <p v-if="error" class="mt-4 text-red-600 font-medium">{{ error }}</p>
    </div>
  </div>
</template>
