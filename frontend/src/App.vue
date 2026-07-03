<script setup lang="ts">
import { useRoute } from 'vue-router'
import NavBar from '@/components/NavBar.vue'

const route = useRoute()
</script>

<template>
  <div class="min-h-screen flex flex-col">
    <NavBar v-if="route.name !== 'login'" />
    <main class="flex-1" :class="route.name !== 'login' ? 'container mx-auto px-4 py-8' : ''">
      <router-view />
    </main>
    <footer
      v-if="route.name !== 'login'"
      class="bg-gray-800 text-gray-300 text-center py-4 text-sm"
    >
      Sistema di Distribuzione Alimentare
    </footer>
  </div>
</template>
