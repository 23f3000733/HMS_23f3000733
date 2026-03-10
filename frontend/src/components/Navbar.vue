<template>
  <nav class="navbar navbar-expand-lg sticky-top">
    <div class="container-fluid px-4">
      <a
        class="navbar-brand d-flex align-items-center"
        href="#"
      >
        <i class="bi bi-hospital-fill me-2" />
        <span class="fw-semibold">HMS</span>
      </a>
      
      <button 
        class="navbar-toggler" 
        type="button" 
        data-bs-toggle="collapse" 
        data-bs-target="#navbarNav"
      >
        <span class="navbar-toggler-icon" />
      </button>
      
      <div
        id="navbarNav"
        class="collapse navbar-collapse"
      >
        <ul class="navbar-nav ms-auto align-items-center">
          <!-- User Info -->
          <li
            v-if="isLoggedIn"
            class="nav-item"
          >
            <div class="d-flex align-items-center me-3">
              <div class="user-avatar me-2">
                <i class="bi bi-person-circle" />
              </div>
              <div class="user-info">
                <div class="user-email">
                  {{ userEmail }}
                </div>
                <span
                  class="badge"
                  :class="getRoleBadgeClass()"
                >{{ roleDisplay }}</span>
              </div>
            </div>
          </li>
          
          <!-- Dashboard Link -->
          <li
            v-if="isLoggedIn && role === 'admin'"
            class="nav-item"
          >
            <router-link
              class="nav-link"
              to="/admin"
            >
              <i class="bi bi-speedometer2 me-1" /> Dashboard
            </router-link>
          </li>
          <li
            v-if="isLoggedIn && role === 'doctor'"
            class="nav-item"
          >
            <router-link
              class="nav-link"
              to="/doctor"
            >
              <i class="bi bi-clipboard-pulse me-1" /> Dashboard
            </router-link>
          </li>
          <li
            v-if="isLoggedIn && role === 'patient'"
            class="nav-item"
          >
            <router-link
              class="nav-link"
              to="/patient"
            >
              <i class="bi bi-heart-pulse me-1" /> Dashboard
            </router-link>
          </li>
          
          <!-- Auth Links -->
          <li
            v-if="!isLoggedIn"
            class="nav-item"
          >
            <router-link
              class="nav-link"
              to="/login"
            >
              <i class="bi bi-box-arrow-in-right me-1" /> Login
            </router-link>
          </li>
          <li
            v-if="!isLoggedIn"
            class="nav-item"
          >
            <router-link
              class="nav-link"
              to="/register"
            >
              <i class="bi bi-person-plus me-1" /> Register
            </router-link>
          </li>
          
          <!-- Logout -->
          <li
            v-if="isLoggedIn"
            class="nav-item"
          >
            <button
              class="btn btn-sm btn-outline-danger"
              @click="logout"
            >
              <i class="bi bi-box-arrow-right me-1" /> Logout
            </button>
          </li>
        </ul>
      </div>
    </div>
  </nav>
</template>

<script>
import { useAuthStore } from '@/stores/auth'

export default {
  name: 'Navbar',
  data() {
    return {
      isLoggedIn: false,
      role: '',
      userEmail: ''
    }
  },
  computed: {
    roleDisplay() {
      if (this.role === 'admin') return 'Admin'
      if (this.role === 'doctor') return 'Doctor'
      if (this.role === 'patient') return 'Patient'
      return ''
    }
  },
  watch: {
    $route() {
      this.checkLogin()
    }
  },
  created() {
    this.checkLogin()
  },
  methods: {
    checkLogin() {
      const token = localStorage.getItem('access_token') || localStorage.getItem('token')
      this.role = localStorage.getItem('role')
      this.userEmail = localStorage.getItem('email') || ''
      this.isLoggedIn = !!token
    },
    getRoleBadgeClass() {
      const classes = {
        'admin': 'bg-danger',
        'doctor': 'bg-primary',
        'patient': 'bg-success'
      }
      return classes[this.role] || 'bg-secondary'
    },
    async logout() {
      const authStore = useAuthStore()
      await authStore.logout()
      window.location.href = '/login'
    }
  }
}
</script>

<style scoped>
.navbar {
  background-color: rgba(255, 255, 255, 0.95);
  border-bottom: 1px solid var(--color-gray-200);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
}

.navbar-brand {
  font-size: 1.25rem;
  color: var(--color-gray-900);
  transition: color var(--transition-base);
}

.navbar-brand:hover {
  color: var(--color-primary);
}

.nav-link {
  color: var(--color-gray-700);
  font-weight: 500;
  padding: 0.5rem 1rem;
  border-radius: var(--radius-md);
  transition: all var(--transition-base);
  display: flex;
  align-items: center;
}

.nav-link:hover {
  color: var(--color-primary);
  background-color: var(--color-gray-50);
}

.nav-link.router-link-active {
  color: var(--color-primary);
  font-weight: 600;
}

.user-avatar {
  color: var(--color-gray-600);
  font-size: 1.5rem;
}

.user-info {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
}

.user-email {
  font-size: var(--font-size-sm);
  color: var(--color-gray-700);
  font-weight: 500;
}

.badge {
  font-size: 0.65rem;
  padding: 0.25rem 0.5rem;
  margin-top: 0.125rem;
}

@media (max-width: 991px) {
  .user-info {
    margin-bottom: 1rem;
  }
  
  .nav-item {
    margin-bottom: 0.5rem;
  }
}
</style>
