import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      name: 'home',
      component: () => import('@/views/HomeView.vue'),
    },
    {
      path: '/families',
      name: 'families',
      component: () => import('@/views/FamiliesView.vue'),
    },
    {
      path: '/distribute',
      name: 'distribute',
      component: () => import('@/views/DistributeView.vue'),
    },
    {
      path: '/search',
      name: 'search',
      component: () => import('@/views/SearchView.vue'),
    },
  ],
})

export default router
