<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import {
  getOverview,
  getDistributionStats,
  getFamilyCoverage,
  getTrends,
  downloadDistributionsReport,
  downloadFamiliesReport,
} from '@/api/stats'
import type {
  OverviewStats,
  DistributionStats,
  FamilyCoverageStats,
  TrendsStats,
} from '@/types'

const overview = ref<OverviewStats | null>(null)
const distStats = ref<DistributionStats | null>(null)
const familyCoverage = ref<FamilyCoverageStats | null>(null)
const trends = ref<TrendsStats | null>(null)
const loading = ref(true)
const error = ref('')

const granularity = ref<'monthly' | 'weekly'>('monthly')

const dateFrom = ref('')
const dateTo = ref('')

async function loadAll() {
  loading.value = true
  error.value = ''
  try {
    const [ov, ds, fc, tr] = await Promise.all([
      getOverview(),
      getDistributionStats({
        date_from: dateFrom.value || undefined,
        date_to: dateTo.value || undefined,
      }),
      getFamilyCoverage(),
      getTrends({ granularity: granularity.value }),
    ])
    overview.value = ov
    distStats.value = ds
    familyCoverage.value = fc
    trends.value = tr
  } catch (e: any) {
    error.value = e.response?.data?.detail || 'Errore durante il caricamento dei dati'
  } finally {
    loading.value = false
  }
}

async function reloadTrends() {
  try {
    trends.value = await getTrends({ granularity: granularity.value })
  } catch (e: any) {
    error.value = e.response?.data?.detail || 'Errore durante il caricamento dei trend'
  }
}

async function reloadDistStats() {
  try {
    distStats.value = await getDistributionStats({
      date_from: dateFrom.value || undefined,
      date_to: dateTo.value || undefined,
    })
  } catch (e: any) {
    error.value = e.response?.data?.detail || 'Errore durante il caricamento delle statistiche'
  }
}

function applyDateFilter() {
  reloadDistStats()
}

function downloadBlob(blob: Blob, filename: string) {
  const url = window.URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = filename
  document.body.appendChild(a)
  a.click()
  document.body.removeChild(a)
  window.URL.revokeObjectURL(url)
}

async function handleDistributionsReport() {
  try {
    const blob = await downloadDistributionsReport({
      date_from: dateFrom.value || undefined,
      date_to: dateTo.value || undefined,
    })
    const stamp = new Date().toISOString().slice(0, 10)
    downloadBlob(blob, `report_distribuzioni_${stamp}.csv`)
  } catch (e: any) {
    error.value = e.response?.data?.detail || 'Errore durante la generazione del report'
  }
}

async function handleFamiliesReport() {
  try {
    const blob = await downloadFamiliesReport()
    const stamp = new Date().toISOString().slice(0, 10)
    downloadBlob(blob, `report_famiglie_${stamp}.csv`)
  } catch (e: any) {
    error.value = e.response?.data?.detail || 'Errore durante la generazione del report'
  }
}

// --- Simple SVG chart computations ---

const maxTrendCount = computed(() => {
  if (!trends.value || trends.value.points.length === 0) return 1
  return Math.max(...trends.value.points.map(p => p.count), 1)
})

const trendChartWidth = 600
const trendChartHeight = 200
const trendBarWidth = computed(() => {
  if (!trends.value || trends.value.points.length === 0) return 0
  return Math.max(8, Math.floor(trendChartWidth / trends.value.points.length) - 6)
})

const maxPackageCount = computed(() => {
  if (!distStats.value || distStats.value.by_package_type.length === 0) return 1
  return Math.max(...distStats.value.by_package_type.map(p => p.count), 1)
})

const coveragePercent = computed(() => {
  if (!familyCoverage.value || familyCoverage.value.total_families === 0) return 0
  return Math.round(
    (familyCoverage.value.families_served / familyCoverage.value.total_families) * 100
  )
})

onMounted(() => {
  loadAll()
})
</script>

<template>
  <div class="max-w-6xl mx-auto">
    <h1 class="text-3xl font-bold mb-6">Dashboard</h1>

    <div v-if="error" class="bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
      <p class="text-red-700 font-medium">{{ error }}</p>
    </div>

    <div v-if="loading" class="text-center py-12">
      <p class="text-gray-500 text-lg">Caricamento...</p>
    </div>

    <div v-else>
      <!-- Metric cards -->
      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        <div class="bg-white rounded-lg shadow p-6">
          <p class="text-sm text-gray-500 mb-1">Famiglie Totali</p>
          <p class="text-3xl font-bold text-blue-600">{{ overview?.total_families ?? 0 }}</p>
        </div>
        <div class="bg-white rounded-lg shadow p-6">
          <p class="text-sm text-gray-500 mb-1">Membri Totali</p>
          <p class="text-3xl font-bold text-indigo-600">{{ overview?.total_persons ?? 0 }}</p>
        </div>
        <div class="bg-white rounded-lg shadow p-6">
          <p class="text-sm text-gray-500 mb-1">Distribuzioni Totali</p>
          <p class="text-3xl font-bold text-green-600">{{ overview?.total_distributions ?? 0 }}</p>
        </div>
        <div class="bg-white rounded-lg shadow p-6">
          <p class="text-sm text-gray-500 mb-1">Distribuzioni Questo Mese</p>
          <p class="text-3xl font-bold text-orange-600">{{ overview?.distributions_this_month ?? 0 }}</p>
        </div>
      </div>

      <div class="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
        <!-- Trends chart -->
        <div class="bg-white rounded-lg shadow p-6">
          <div class="flex items-center justify-between mb-4">
            <h2 class="text-xl font-semibold">Andamento Distribuzioni</h2>
            <select
              v-model="granularity"
              @change="reloadTrends"
              class="text-sm border border-gray-300 rounded-md px-2 py-1 focus:ring-2 focus:ring-blue-500 focus:outline-none"
            >
              <option value="monthly">Mensile</option>
              <option value="weekly">Settimanale</option>
            </select>
          </div>

          <div v-if="trends && trends.points.length > 0">
            <svg :viewBox="`0 0 ${trendChartWidth} ${trendChartHeight}`" class="w-full" preserveAspectRatio="xMidYMid meet">
              <g>
                <rect
                  v-for="(point, i) in trends.points"
                  :key="i"
                  :x="i * (trendBarWidth + 6) + 3"
                  :y="trendChartHeight - (point.count / maxTrendCount) * (trendChartHeight - 30) - 20"
                  :width="trendBarWidth"
                  :height="(point.count / maxTrendCount) * (trendChartHeight - 30)"
                  class="fill-blue-500 hover:fill-blue-600 transition-colors"
                >
                  <title>{{ point.period }}: {{ point.count }}</title>
                </rect>
                <text
                  v-for="(point, i) in trends.points"
                  :key="'label-' + i"
                  :x="i * (trendBarWidth + 6) + 3 + trendBarWidth / 2"
                  :y="trendChartHeight - 5"
                  text-anchor="middle"
                  class="fill-gray-500 text-[10px]"
                  v-if="trends.points.length <= 12"
                >{{ point.period.slice(5) }}</text>
              </g>
            </svg>
          </div>
          <p v-else class="text-gray-400 text-center py-8">Nessun dato disponibile</p>
        </div>

        <!-- Package type breakdown -->
        <div class="bg-white rounded-lg shadow p-6">
          <h2 class="text-xl font-semibold mb-4">Distribuzioni per Tipo di Pacco</h2>
          <div v-if="distStats && distStats.by_package_type.length > 0" class="space-y-3">
            <div v-for="item in distStats.by_package_type" :key="item.package_type">
              <div class="flex justify-between text-sm mb-1">
                <span class="font-medium">{{ item.package_type }}</span>
                <span class="text-gray-500">{{ item.count }}</span>
              </div>
              <div class="w-full bg-gray-200 rounded-full h-4">
                <div
                  class="bg-blue-600 h-4 rounded-full transition-all"
                  :style="{ width: (item.count / maxPackageCount * 100) + '%' }"
                ></div>
              </div>
            </div>
          </div>
          <p v-else class="text-gray-400 text-center py-8">Nessun dato disponibile</p>
        </div>
      </div>

      <!-- Family coverage -->
      <div class="bg-white rounded-lg shadow p-6 mb-8">
        <h2 class="text-xl font-semibold mb-4">Copertura Famiglie</h2>
        <div v-if="familyCoverage" class="grid grid-cols-1 sm:grid-cols-3 gap-4">
          <div class="text-center">
            <p class="text-sm text-gray-500 mb-1">Famiglie Servite</p>
            <p class="text-2xl font-bold text-green-600">{{ familyCoverage.families_served }}</p>
          </div>
          <div class="text-center">
            <p class="text-sm text-gray-500 mb-1">Famiglie Non Servite</p>
            <p class="text-2xl font-bold text-orange-600">{{ familyCoverage.families_not_served }}</p>
          </div>
          <div class="text-center">
            <p class="text-sm text-gray-500 mb-1">Percentuale Copertura</p>
            <p class="text-2xl font-bold text-blue-600">{{ coveragePercent }}%</p>
          </div>
        </div>
      </div>

      <!-- Reports section -->
      <div class="bg-white rounded-lg shadow p-6">
        <h2 class="text-xl font-semibold mb-4">Report CSV</h2>

        <div class="flex flex-col sm:flex-row gap-4 mb-4">
          <div>
            <label class="block text-sm text-gray-500 mb-1">Data Inizio</label>
            <input
              v-model="dateFrom"
              type="date"
              class="border border-gray-300 rounded-md px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 focus:outline-none"
            />
          </div>
          <div>
            <label class="block text-sm text-gray-500 mb-1">Data Fine</label>
            <input
              v-model="dateTo"
              type="date"
              class="border border-gray-300 rounded-md px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 focus:outline-none"
            />
          </div>
          <div class="flex items-end">
            <button
              @click="applyDateFilter"
              class="bg-gray-600 hover:bg-gray-700 text-white text-sm font-semibold px-4 py-2 rounded-md transition-colors"
            >
              Applica Filtro
            </button>
          </div>
        </div>

        <div class="flex flex-col sm:flex-row gap-3">
          <button
            @click="handleDistributionsReport"
            class="bg-green-600 hover:bg-green-700 text-white font-semibold px-6 py-2.5 rounded-md transition-colors"
          >
            Scarica Report Distribuzioni (CSV)
          </button>
          <button
            @click="handleFamiliesReport"
            class="bg-indigo-600 hover:bg-indigo-700 text-white font-semibold px-6 py-2.5 rounded-md transition-colors"
          >
            Scarica Report Famiglie (CSV)
          </button>
        </div>
      </div>
    </div>
  </div>
</template>
