import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

// Lazy load all components for better performance
const Login = () => import('@/components/Login.vue')
const Register = () => import('@/components/Register.vue')
const AdminDashboard = () => import('@/components/AdminDashboard.vue')
const DoctorDashboard = () => import('@/components/DoctorDashboard.vue')
const PatientDashboard = () => import('@/components/PatientDashboard.vue')
const LandingPage = () => import('@/views/LandingPage.vue')

const routes = [
  {
    path: '/',
    name: 'LandingPage',
    component: LandingPage,
    meta: { requiresAuth: false }
  },
  {
    path: '/login',
    name: 'Login',
    component: Login,
    meta: { requiresAuth: false }
  },
  {
    path: '/register',
    name: 'Register',
    component: Register,
    meta: { requiresAuth: false }
  },
  {
    path: '/admin',
    name: 'AdminDashboard',
    component: AdminDashboard,
    meta: { requiresAuth: true, role: 'admin' }
  },
  {
    path: '/doctor',
    name: 'DoctorDashboard',
    component: DoctorDashboard,
    meta: { requiresAuth: true, role: 'doctor' }
  },
  {
    path: '/patient',
    name: 'PatientDashboard',
    component: PatientDashboard,
    meta: { requiresAuth: true, role: 'patient' }
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: () => import('@/views/NotFound.vue'),
    meta: { requiresAuth: false }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// Navigation guard for authentication
router.beforeEach((to, from, next) => {
  const authStore = useAuthStore()
  const requiresAuth = to.meta.requiresAuth
  const requiredRole = to.meta.role

  if (requiresAuth && !authStore.isAuthenticated) {
    // Redirect to login if not authenticated
    next('/login')
  } else if (requiredRole && authStore.role !== requiredRole) {
    // Redirect to correct dashboard if role doesn't match
    if (authStore.role === 'admin') {
      next('/admin')
    } else if (authStore.role === 'doctor') {
      next('/doctor')
    } else if (authStore.role === 'patient') {
      next('/patient')
    } else {
      next('/login')
    }
  } else {
    next()
  }
})

export default router
