<script setup lang="ts">
import NavBar from '@/components/NavBar.vue'
</script>

<template>
  <div class="min-h-screen flex flex-col">
    <NavBar />
    <main class="flex-1 container mx-auto px-4 py-8">
      <router-view />
    </main>
    <footer class="bg-gray-800 text-gray-300 text-center py-4 text-sm">
      Sistema di Distribuzione Alimentare
    </footer>
  </div>
</template>
