import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/login',
      name: 'login',
      component: () => import('@/views/LoginView.vue'),
      meta: { guest: true }
    },
    {
      path: '/register',
      name: 'register',
      component: () => import('@/views/RegisterView.vue'),
      meta: { guest: true }
    },
    {
      path: '/',
      component: () => import('@/layouts/MainLayout.vue'),
      meta: { requiresAuth: true },
      children: [
        {
          path: '',
          redirect: '/dashboard'
        },
        {
          path: 'dashboard',
          name: 'dashboard',
          component: () => import('@/views/DashboardView.vue')
        },
        {
          path: 'transactions',
          name: 'transactions',
          component: () => import('@/views/TransactionsView.vue')
        },
        {
          path: 'accounts',
          name: 'accounts',
          component: () => import('@/views/AccountsView.vue')
        },
        {
          path: 'categories',
          name: 'categories',
          component: () => import('@/views/CategoriesView.vue')
        },
        {
          path: 'secondary-categories',
          name: 'secondary-categories',
          component: () => import('@/views/SecondaryCategoriesView.vue')
        },
        {
          path: 'budgets',
          name: 'budgets',
          component: () => import('@/views/BudgetsView.vue')
        },
        {
          path: 'goals',
          name: 'goals',
          component: () => import('@/views/GoalsView.vue')
        },
        {
          path: 'investments',
          name: 'investments',
          component: () => import('@/views/InvestmentsView.vue')
        },
        {
          path: 'debts',
          name: 'debts',
          component: () => import('@/views/DebtsView.vue')
        },
        {
          path: 'bets',
          name: 'bets',
          component: () => import('@/views/BetsView.vue')
        },
        {
          path: 'reports',
          name: 'reports',
          component: () => import('@/views/ReportsView.vue')
        },
        {
          path: 'habits-analysis',
          name: 'habits-analysis',
          component: () => import('@/views/HabitsAnalysisView.vue')
        },
        {
          path: 'recurring',
          name: 'recurring',
          component: () => import('@/views/RecurringView.vue')
        },
        {
          path: 'profile',
          name: 'profile',
          component: () => import('@/views/ProfileView.vue')
        }
      ]
    },
    {
      path: '/:pathMatch(.*)*',
      redirect: '/dashboard'
    }
  ]
})

router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('access_token')
  const isAuthenticated = !!token
  
  if (to.meta.requiresAuth && !isAuthenticated) {
    next('/login')
  } else if (to.meta.guest && isAuthenticated) {
    next('/dashboard')
  } else {
    next()
  }
})

export default router












