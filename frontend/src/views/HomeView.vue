<script setup lang="ts">
</script>

<template>
  <div class="text-center">
    <h1 class="text-4xl font-bold mb-4">Sistema di Distribuzione Alimentare</h1>
    <p class="text-gray-600 mb-8">Gestione delle distribuzioni di pacchi alimentari alle famiglie</p>
    <div class="grid grid-cols-1 md:grid-cols-3 gap-6 max-w-4xl mx-auto">
      <router-link to="/families" class="bg-white rounded-lg shadow p-6 hover:shadow-lg transition-shadow">
        <h2 class="text-xl font-semibold mb-2">Famiglie</h2>
        <p class="text-gray-500">Registra e gestisci le famiglie e i loro membri</p>
      </router-link>
      <router-link to="/distribute" class="bg-white rounded-lg shadow p-6 hover:shadow-lg transition-shadow">
        <h2 class="text-xl font-semibold mb-2">Distribuzione</h2>
        <p class="text-gray-500">Distribuisci pacchi alimentari tramite impronta digitale</p>
      </router-link>
      <router-link to="/search" class="bg-white rounded-lg shadow p-6 hover:shadow-lg transition-shadow">
        <h2 class="text-xl font-semibold mb-2">Ricerca</h2>
        <p class="text-gray-500">Cerca famiglie e persone registrate</p>
      </router-link>
    </div>
  </div>
</template>
