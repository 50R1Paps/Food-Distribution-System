<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import type { FamilyDetail, Person } from '@/types'
import {
  addMember,
  deleteFamily,
  deleteMember,
  getFamily,
  updateFamily,
  updateMember,
  type MemberPayload,
} from '@/api/families'
import MemberForm from '@/components/MemberForm.vue'

const route = useRoute()
const router = useRouter()
const familyId = Number(route.params.id)

const family = ref<FamilyDetail | null>(null)
const loading = ref(false)
const error = ref('')

const editingFamily = ref(false)
const editName = ref('')
const editAddress = ref('')
const editContact = ref('')

const showMemberForm = ref(false)
const editingMember = ref<Person | null>(null)

async function load() {
  try {
    family.value = await getFamily(familyId)
  } catch {
    error.value = 'Famiglia non trovata'
  }
}

onMounted(load)

function startEditFamily() {
  if (!family.value) return
  editName.value = family.value.family_name
  editAddress.value = family.value.address
  editContact.value = family.value.contact_number ?? ''
  editingFamily.value = true
}

async function saveFamily() {
  loading.value = true
  error.value = ''
  try {
    await updateFamily(familyId, {
      family_name: editName.value,
      address: editAddress.value,
      contact_number: editContact.value || null,
    })
    editingFamily.value = false
    await load()
  } catch (e: any) {
    error.value = e?.response?.data?.detail ?? 'Errore durante il salvataggio'
  } finally {
    loading.value = false
  }
}

async function removeFamily() {
  if (!confirm('Eliminare questa famiglia e tutti i suoi membri?')) return
  error.value = ''
  try {
    await deleteFamily(familyId)
    router.push('/families')
  } catch (e: any) {
    error.value = e?.response?.data?.detail ?? "Errore durante l'eliminazione"
  }
}

function startAddMember() {
  editingMember.value = null
  showMemberForm.value = true
}

function startEditMember(member: Person) {
  editingMember.value = member
  showMemberForm.value = true
}

async function submitMember(payload: MemberPayload) {
  loading.value = true
  error.value = ''
  try {
    if (editingMember.value) {
      await updateMember(editingMember.value.id, payload)
      showMemberForm.value = false
    } else {
      await addMember(familyId, payload)
      // "aggiungi un altro membro": il form resta aperto e vuoto
      editingMember.value = null
      showMemberForm.value = false
      await load()
      showMemberForm.value = true
      loading.value = false
      return
    }
    await load()
  } catch (e: any) {
    error.value = e?.response?.data?.detail ?? 'Errore durante il salvataggio del membro'
  } finally {
    loading.value = false
  }
}

async function removeMember(member: Person) {
  if (!confirm(`Eliminare ${member.first_name} ${member.last_name}?`)) return
  error.value = ''
  try {
    await deleteMember(member.id)
    await load()
  } catch (e: any) {
    error.value = e?.response?.data?.detail ?? "Errore durante l'eliminazione del membro"
  }
}

function formatDate(iso: string) {
  return new Date(iso).toLocaleDateString('it-IT')
}

function formatDateTime(iso: string) {
  return new Date(iso).toLocaleString('it-IT')
}

function memberName(personId: number) {
  const m = family.value?.members.find((p) => p.id === personId)
  return m ? `${m.first_name} ${m.last_name}` : `#${personId}`
}
</script>

<template>
  <div v-if="family">
    <div class="flex items-center justify-between mb-6">
      <h1 class="text-3xl font-bold">{{ family.family_name }}</h1>
      <div class="flex gap-2">
        <button
          @click="startEditFamily"
          class="bg-gray-800 hover:bg-gray-700 text-white px-4 py-2 rounded-md text-sm transition-colors"
        >
          Modifica
        </button>
        <button
          @click="removeFamily"
          class="bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded-md text-sm transition-colors"
        >
          Elimina famiglia
        </button>
      </div>
    </div>

    <p v-if="error" class="text-red-600 mb-4">{{ error }}</p>

    <!-- Dati famiglia -->
    <div class="bg-white rounded-lg shadow p-6 mb-6">
      <template v-if="!editingFamily">
        <div class="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
          <div>
            <span class="text-gray-500 block">Indirizzo</span>
            <span class="font-medium">{{ family.address }}</span>
          </div>
          <div>
            <span class="text-gray-500 block">Telefono</span>
            <span class="font-medium">{{ family.contact_number || '—' }}</span>
          </div>
          <div>
            <span class="text-gray-500 block">Registrata il</span>
            <span class="font-medium">{{ formatDate(family.created_at) }}</span>
          </div>
        </div>
      </template>
      <form v-else @submit.prevent="saveFamily" class="space-y-4">
        <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Nome famiglia</label>
            <input v-model="editName" type="text" required class="w-full border border-gray-300 rounded-md px-3 py-2" />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Indirizzo</label>
            <input v-model="editAddress" type="text" required class="w-full border border-gray-300 rounded-md px-3 py-2" />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Telefono</label>
            <input v-model="editContact" type="text" class="w-full border border-gray-300 rounded-md px-3 py-2" />
          </div>
        </div>
        <div class="flex gap-3">
          <button type="submit" :disabled="loading" class="bg-gray-800 hover:bg-gray-700 text-white px-4 py-2 rounded-md text-sm disabled:opacity-50">
            Salva
          </button>
          <button type="button" @click="editingFamily = false" class="bg-gray-200 hover:bg-gray-300 text-gray-800 px-4 py-2 rounded-md text-sm">
            Annulla
          </button>
        </div>
      </form>
    </div>

    <!-- Membri -->
    <div class="bg-white rounded-lg shadow p-6 mb-6">
      <div class="flex items-center justify-between mb-4">
        <h2 class="text-xl font-semibold">Membri ({{ family.members.length }})</h2>
        <button
          v-if="!showMemberForm"
          @click="startAddMember"
          class="bg-gray-800 hover:bg-gray-700 text-white px-4 py-2 rounded-md text-sm transition-colors"
        >
          Aggiungi membro
        </button>
      </div>

      <div v-if="showMemberForm" class="border border-gray-200 rounded-md p-4 mb-4 bg-gray-50">
        <h3 class="font-medium mb-3">
          {{ editingMember ? 'Modifica membro' : 'Nuovo membro' }}
        </h3>
        <MemberForm
          :member="editingMember"
          :loading="loading"
          @submit="submitMember"
          @cancel="showMemberForm = false"
        />
      </div>

      <table v-if="family.members.length" class="w-full text-sm">
        <thead>
          <tr class="text-left text-gray-500 border-b">
            <th class="py-2">Nome</th>
            <th class="py-2">Data di nascita</th>
            <th class="py-2">Impronta</th>
            <th class="py-2 text-right">Azioni</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="m in family.members" :key="m.id" class="border-b last:border-0">
            <td class="py-2 font-medium">{{ m.first_name }} {{ m.last_name }}</td>
            <td class="py-2">{{ formatDate(m.date_of_birth) }}</td>
            <td class="py-2">
              <span v-if="m.fingerprint_id" class="text-green-700 font-mono text-xs">{{ m.fingerprint_id }}</span>
              <span v-else class="text-gray-400">—</span>
            </td>
            <td class="py-2 text-right">
              <button @click="startEditMember(m)" class="text-blue-600 hover:underline mr-3">Modifica</button>
              <button @click="removeMember(m)" class="text-red-600 hover:underline">Elimina</button>
            </td>
          </tr>
        </tbody>
      </table>
      <p v-else class="text-gray-500">Nessun membro registrato.</p>
    </div>

    <!-- Storico distribuzioni -->
    <div class="bg-white rounded-lg shadow p-6">
      <h2 class="text-xl font-semibold mb-4">
        Storico distribuzioni ({{ family.distributions.length }})
      </h2>
      <table v-if="family.distributions.length" class="w-full text-sm">
        <thead>
          <tr class="text-left text-gray-500 border-b">
            <th class="py-2">Data</th>
            <th class="py-2">Membro</th>
            <th class="py-2">Tipo pacco</th>
            <th class="py-2">Note</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="d in family.distributions" :key="d.id" class="border-b last:border-0">
            <td class="py-2">{{ formatDateTime(d.distribution_date) }}</td>
            <td class="py-2">{{ memberName(d.person_id) }}</td>
            <td class="py-2">{{ d.package_type }}</td>
            <td class="py-2 text-gray-500">{{ d.notes || '—' }}</td>
          </tr>
        </tbody>
      </table>
      <p v-else class="text-gray-500">Nessuna distribuzione registrata.</p>
    </div>
  </div>

  <div v-else class="text-center py-12">
    <p class="text-gray-500">{{ error || 'Caricamento…' }}</p>
  </div>
</template>
