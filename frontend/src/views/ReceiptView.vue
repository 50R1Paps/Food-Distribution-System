<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import type { DistributionReceipt } from '@/types'
import { getDistribution } from '@/api/distributions'

const route = useRoute()
const receipt = ref<DistributionReceipt | null>(null)
const error = ref('')

onMounted(async () => {
  try {
    receipt.value = await getDistribution(Number(route.params.id))
  } catch {
    error.value = 'Ricevuta non trovata'
  }
})

function printReceipt() {
  window.print()
}

function formatDateTime(iso: string) {
  return new Date(iso).toLocaleString('it-IT')
}
</script>

<template>
  <div v-if="receipt" class="max-w-lg mx-auto">
    <div class="flex items-center justify-between mb-6 print:hidden">
      <h1 class="text-3xl font-bold">Ricevuta</h1>
      <div class="flex gap-3">
        <button
          @click="printReceipt"
          class="bg-gray-800 hover:bg-gray-700 text-white px-4 py-2 rounded-md text-sm transition-colors"
        >
          Stampa
        </button>
        <router-link
          to="/distribute"
          class="bg-gray-200 hover:bg-gray-300 text-gray-800 px-4 py-2 rounded-md text-sm transition-colors"
        >
          Nuova distribuzione
        </router-link>
      </div>
    </div>

    <div class="bg-white rounded-lg shadow p-8 print:shadow-none">
      <div class="text-center border-b pb-4 mb-6">
        <h2 class="text-xl font-bold">Sistema di Distribuzione Alimentare</h2>
        <p class="text-gray-500 text-sm">Ricevuta di distribuzione n. {{ receipt.id }}</p>
      </div>

      <dl class="space-y-3 text-sm">
        <div class="flex justify-between">
          <dt class="text-gray-500">Data e ora</dt>
          <dd class="font-medium">{{ formatDateTime(receipt.distribution_date) }}</dd>
        </div>
        <div class="flex justify-between">
          <dt class="text-gray-500">Famiglia</dt>
          <dd class="font-medium">{{ receipt.family_name }}</dd>
        </div>
        <div class="flex justify-between">
          <dt class="text-gray-500">Ritirato da</dt>
          <dd class="font-medium">{{ receipt.person_name }}</dd>
        </div>
        <div class="flex justify-between">
          <dt class="text-gray-500">Tipo di pacco</dt>
          <dd class="font-medium">{{ receipt.package_type }}</dd>
        </div>
        <div v-if="receipt.is_emergency" class="flex justify-between">
          <dt class="text-gray-500">Modalità</dt>
          <dd class="font-medium text-red-600">Distribuzione d'emergenza</dd>
        </div>
        <div v-if="receipt.notes" class="flex justify-between">
          <dt class="text-gray-500">Note</dt>
          <dd class="font-medium">{{ receipt.notes }}</dd>
        </div>
      </dl>

      <div class="border-t mt-6 pt-4 text-center text-xs text-gray-400">
        Documento generato automaticamente
      </div>
    </div>
  </div>

  <div v-else class="text-center py-12">
    <p class="text-gray-500">{{ error || 'Caricamento…' }}</p>
  </div>
</template>
