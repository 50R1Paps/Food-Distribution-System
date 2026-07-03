<script setup lang="ts">
import { ref, watch } from 'vue'
import type { Person } from '@/types'
import type { MemberPayload } from '@/api/families'

const props = defineProps<{
  member?: Person | null
  loading?: boolean
}>()

const emit = defineEmits<{
  submit: [payload: MemberPayload]
  cancel: []
}>()

const firstName = ref('')
const lastName = ref('')
const dateOfBirth = ref('')
const fingerprintId = ref<string | null>(null)
const scanning = ref(false)

watch(
  () => props.member,
  (m) => {
    firstName.value = m?.first_name ?? ''
    lastName.value = m?.last_name ?? ''
    dateOfBirth.value = m?.date_of_birth ?? ''
    fingerprintId.value = m?.fingerprint_id ?? null
  },
  { immediate: true }
)

function simulateScan() {
  scanning.value = true
  setTimeout(() => {
    fingerprintId.value = `FP-${Date.now()}-${Math.random().toString(36).slice(2, 8).toUpperCase()}`
    scanning.value = false
  }, 1000)
}

function handleSubmit() {
  emit('submit', {
    first_name: firstName.value,
    last_name: lastName.value,
    date_of_birth: dateOfBirth.value,
    fingerprint_id: fingerprintId.value,
  })
}
</script>

<template>
  <form @submit.prevent="handleSubmit" class="space-y-4">
    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
      <div>
        <label class="block text-sm font-medium text-gray-700 mb-1">Nome</label>
        <input
          v-model="firstName"
          type="text"
          required
          class="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-gray-600"
        />
      </div>
      <div>
        <label class="block text-sm font-medium text-gray-700 mb-1">Cognome</label>
        <input
          v-model="lastName"
          type="text"
          required
          class="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-gray-600"
        />
      </div>
    </div>

    <div>
      <label class="block text-sm font-medium text-gray-700 mb-1">Data di nascita</label>
      <input
        v-model="dateOfBirth"
        type="date"
        required
        class="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-gray-600"
      />
    </div>

    <div>
      <label class="block text-sm font-medium text-gray-700 mb-1">Impronta digitale</label>
      <div class="flex items-center gap-3">
        <button
          type="button"
          @click="simulateScan"
          :disabled="scanning"
          class="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-md text-sm transition-colors disabled:opacity-50"
        >
          {{ scanning ? 'Scansione in corso…' : 'Scansiona impronta' }}
        </button>
        <span v-if="fingerprintId" class="text-sm text-green-700 font-mono">
          {{ fingerprintId }}
        </span>
        <span v-else class="text-sm text-gray-400">Nessuna impronta registrata</span>
      </div>
    </div>

    <div class="flex gap-3">
      <button
        type="submit"
        :disabled="loading"
        class="bg-gray-800 hover:bg-gray-700 text-white px-4 py-2 rounded-md text-sm transition-colors disabled:opacity-50"
      >
        {{ member ? 'Salva modifiche' : 'Aggiungi membro' }}
      </button>
      <button
        type="button"
        @click="emit('cancel')"
        class="bg-gray-200 hover:bg-gray-300 text-gray-800 px-4 py-2 rounded-md text-sm transition-colors"
      >
        Annulla
      </button>
    </div>
  </form>
</template>
