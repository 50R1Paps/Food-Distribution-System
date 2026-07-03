<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import type { CooldownWarning, Family, PackageType, Person } from '@/types'
import { createDistribution, listPackageTypes } from '@/api/distributions'
import { getFamily, listFamilies } from '@/api/families'

const router = useRouter()

const mode = ref<'fingerprint' | 'manual'>('fingerprint')

// identificazione per impronta
const fingerprintId = ref('')
const scanning = ref(false)

// identificazione manuale
const familySearch = ref('')
const familyResults = ref<Family[]>([])
const selectedFamilyMembers = ref<Person[]>([])
const selectedFamilyName = ref('')
const selectedPerson = ref<Person | null>(null)

// pacco e note
const packageTypes = ref<PackageType[]>([])
const selectedPackageTypeId = ref<number | null>(null)
const notes = ref('')

const cooldownWarning = ref<CooldownWarning | null>(null)
const error = ref('')
const loading = ref(false)

onMounted(async () => {
  try {
    packageTypes.value = await listPackageTypes()
    if (packageTypes.value.length) {
      selectedPackageTypeId.value = packageTypes.value[0].id
    }
  } catch {
    error.value = 'Errore nel caricamento dei tipi di pacco'
  }
})

function simulateScan() {
  scanning.value = true
  setTimeout(() => {
    scanning.value = false
  }, 1000)
}

async function searchFamilies() {
  selectedPerson.value = null
  selectedFamilyMembers.value = []
  try {
    const data = await listFamilies({ search: familySearch.value, page_size: 10 })
    familyResults.value = data.items
  } catch {
    error.value = 'Errore nella ricerca'
  }
}

async function selectFamily(family: Family) {
  try {
    const detail = await getFamily(family.id)
    selectedFamilyMembers.value = detail.members
    selectedFamilyName.value = detail.family_name
    familyResults.value = []
  } catch {
    error.value = 'Errore nel caricamento della famiglia'
  }
}

async function submit(isEmergency = false) {
  if (!selectedPackageTypeId.value) {
    error.value = 'Seleziona un tipo di pacco'
    return
  }
  error.value = ''
  cooldownWarning.value = null
  loading.value = true
  try {
    const receipt = await createDistribution({
      person_id: mode.value === 'manual' ? selectedPerson.value?.id : undefined,
      fingerprint_id: mode.value === 'fingerprint' ? fingerprintId.value : undefined,
      package_type_id: selectedPackageTypeId.value,
      notes: notes.value || null,
      is_emergency: isEmergency,
    })
    router.push(`/distributions/${receipt.id}`)
  } catch (e: any) {
    if (e?.response?.status === 409 && e.response.data?.warning) {
      cooldownWarning.value = e.response.data
    } else {
      error.value = e?.response?.data?.detail ?? 'Errore durante la distribuzione'
    }
  } finally {
    loading.value = false
  }
}

function formatDate(iso: string) {
  return new Date(iso).toLocaleDateString('it-IT')
}
</script>

<template>
  <div class="max-w-2xl mx-auto">
    <h1 class="text-3xl font-bold mb-6">Distribuzione</h1>

    <p v-if="error" class="text-red-600 mb-4">{{ error }}</p>

    <!-- Avviso cooldown -->
    <div
      v-if="cooldownWarning"
      class="bg-yellow-50 border border-yellow-300 rounded-lg p-4 mb-6"
    >
      <h3 class="font-semibold text-yellow-800 mb-2">Attenzione: distribuzione recente</h3>
      <p class="text-yellow-800 text-sm mb-1">{{ cooldownWarning.warning }}</p>
      <p class="text-yellow-700 text-sm mb-3">
        Prossima distribuzione consentita dal
        <strong>{{ formatDate(cooldownWarning.next_allowed_date) }}</strong>
        (attesa di {{ cooldownWarning.cooldown_days }} giorni).
      </p>
      <div class="flex gap-3">
        <button
          @click="submit(true)"
          :disabled="loading"
          class="bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded-md text-sm transition-colors disabled:opacity-50"
        >
          Distribuzione d'emergenza
        </button>
        <button
          @click="cooldownWarning = null"
          class="bg-gray-200 hover:bg-gray-300 text-gray-800 px-4 py-2 rounded-md text-sm transition-colors"
        >
          Annulla
        </button>
      </div>
    </div>

    <div class="bg-white rounded-lg shadow p-6 space-y-6">
      <!-- Selettore modalità -->
      <div class="flex rounded-md overflow-hidden border border-gray-300 w-fit">
        <button
          @click="mode = 'fingerprint'"
          :class="mode === 'fingerprint' ? 'bg-gray-800 text-white' : 'bg-white text-gray-700'"
          class="px-4 py-2 text-sm transition-colors"
        >
          Impronta digitale
        </button>
        <button
          @click="mode = 'manual'"
          :class="mode === 'manual' ? 'bg-gray-800 text-white' : 'bg-white text-gray-700'"
          class="px-4 py-2 text-sm transition-colors"
        >
          Ricerca manuale
        </button>
      </div>

      <!-- Impronta -->
      <div v-if="mode === 'fingerprint'">
        <label class="block text-sm font-medium text-gray-700 mb-1">
          Codice impronta digitale
        </label>
        <div class="flex gap-3">
          <input
            v-model="fingerprintId"
            type="text"
            placeholder="Es. FP-…"
            class="flex-1 border border-gray-300 rounded-md px-3 py-2 font-mono text-sm focus:outline-none focus:ring-2 focus:ring-gray-600"
          />
          <button
            type="button"
            @click="simulateScan"
            :disabled="scanning"
            class="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-md text-sm transition-colors disabled:opacity-50"
          >
            {{ scanning ? 'Scansione…' : 'Scansiona' }}
          </button>
        </div>
        <p class="text-xs text-gray-400 mt-1">
          Sensore simulato: inserisci il codice impronta del membro registrato.
        </p>
      </div>

      <!-- Ricerca manuale -->
      <div v-else class="space-y-4">
        <form @submit.prevent="searchFamilies" class="flex gap-3">
          <input
            v-model="familySearch"
            type="text"
            placeholder="Cerca famiglia per nome…"
            class="flex-1 border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-gray-600"
          />
          <button
            type="submit"
            class="bg-gray-800 hover:bg-gray-700 text-white px-4 py-2 rounded-md text-sm transition-colors"
          >
            Cerca
          </button>
        </form>

        <ul v-if="familyResults.length" class="border border-gray-200 rounded-md divide-y">
          <li
            v-for="f in familyResults"
            :key="f.id"
            @click="selectFamily(f)"
            class="px-4 py-2 hover:bg-gray-50 cursor-pointer text-sm"
          >
            <span class="font-medium">{{ f.family_name }}</span>
            <span class="text-gray-500"> — {{ f.address }}</span>
          </li>
        </ul>

        <div v-if="selectedFamilyMembers.length">
          <label class="block text-sm font-medium text-gray-700 mb-1">
            Membro della famiglia {{ selectedFamilyName }}
          </label>
          <select
            v-model="selectedPerson"
            class="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-gray-600"
          >
            <option :value="null" disabled>Seleziona un membro…</option>
            <option v-for="m in selectedFamilyMembers" :key="m.id" :value="m">
              {{ m.first_name }} {{ m.last_name }}
            </option>
          </select>
        </div>
      </div>

      <!-- Tipo pacco -->
      <div>
        <label class="block text-sm font-medium text-gray-700 mb-1">Tipo di pacco</label>
        <select
          v-model="selectedPackageTypeId"
          class="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-gray-600"
        >
          <option v-for="pt in packageTypes" :key="pt.id" :value="pt.id">
            {{ pt.name }} (attesa {{ pt.cooldown_days }} giorni)
          </option>
        </select>
      </div>

      <!-- Note -->
      <div>
        <label class="block text-sm font-medium text-gray-700 mb-1">Note (opzionale)</label>
        <textarea
          v-model="notes"
          rows="2"
          class="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-gray-600"
        ></textarea>
      </div>

      <button
        @click="submit(false)"
        :disabled="loading || (mode === 'fingerprint' ? !fingerprintId : !selectedPerson)"
        class="w-full bg-gray-800 hover:bg-gray-700 text-white py-2 rounded-md font-medium transition-colors disabled:opacity-50"
      >
        {{ loading ? 'Registrazione…' : 'Registra distribuzione' }}
      </button>
    </div>
  </div>
</template>
