import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/login',
      name: 'login',
      component: () => import('@/views/LoginView.vue'),
      meta: { public: true },
    },
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
      path: '/families/:id',
      name: 'family-details',
      component: () => import('@/views/FamilyDetailsView.vue'),
    },
    {
      path: '/distribute',
      name: 'distribute',
      component: () => import('@/views/DistributeView.vue'),
    },
    {
      path: '/distributions/:id',
      name: 'receipt',
      component: () => import('@/views/ReceiptView.vue'),
    },
    {
      path: '/search',
      name: 'search',
      component: () => import('@/views/SearchView.vue'),
    },
  ],
})

router.beforeEach((to) => {
  const auth = useAuthStore()
  if (!to.meta.public && !auth.isAuthenticated) {
    return { name: 'login' }
  }
  if (to.name === 'login' && auth.isAuthenticated) {
    return { name: 'home' }
  }
})

export default router
