<template>
  <div class="admin-dashboard">
    <!-- Hero Section -->
    <div class="dashboard-hero bg-dark text-white py-5 mb-4">
      <div class="container-fluid px-4">
        <div class="d-flex justify-content-between align-items-center">
          <div>
            <h1 class="display-5 fw-bold mb-2">
              Admin Portal
            </h1>
            <p class="lead mb-0 opacity-75">
              Hospital Operations Center
            </p>
          </div>
          <button
            class="btn btn-light btn-lg px-4 shadow-sm"
            @click="logout"
          >
            <i class="bi bi-box-arrow-right me-2" />Logout
          </button>
        </div>
      </div>
    </div>
    
    <!-- Main Content -->
    <div class="container-fluid px-4 pb-5">
      <!-- Navigation Tabs -->
      <div class="card border-0 shadow-sm mb-4">
        <div class="card-body p-2">
          <ul class="nav nav-pills nav-fill modern-tabs">
            <li class="nav-item">
              <a 
                class="nav-link" 
                :class="{ active: activeTab === 'overview' }" 
                href="#" 
                @click.prevent="activeTab = 'overview'"
              >
                <i class="bi bi-speedometer2 me-2" />Overview
              </a>
            </li>
            <li class="nav-item">
              <a 
                class="nav-link" 
                :class="{ active: activeTab === 'analytics' }" 
                href="#" 
                @click.prevent="activeTab = 'analytics'"
              >
                <i class="bi bi-graph-up me-2" />Analytics
              </a>
            </li>
            <li class="nav-item">
              <a 
                class="nav-link" 
                :class="{ active: activeTab === 'doctors' }" 
                href="#" 
                @click.prevent="activeTab = 'doctors'"
              >
                <i class="bi bi-person-badge me-2" />Doctors
              </a>
            </li>
            <li class="nav-item">
              <a 
                class="nav-link" 
                :class="{ active: activeTab === 'patients' }" 
                href="#" 
                @click.prevent="activeTab = 'patients'"
              >
                <i class="bi bi-people me-2" />Patients
              </a>
            </li>
            <li class="nav-item">
              <a 
                class="nav-link" 
                :class="{ active: activeTab === 'appointments' }" 
                href="#" 
                @click.prevent="activeTab = 'appointments'"
              >
                <i class="bi bi-calendar3 me-2" />Appointments
              </a>
            </li>
            <li class="nav-item">
              <a 
                class="nav-link" 
                :class="{ active: activeTab === 'settings' }" 
                href="#" 
                @click.prevent="activeTab = 'settings'"
              >
                <i class="bi bi-gear me-2" />Settings
              </a>
            </li>
          </ul>
        </div>
      </div>
      
      <!-- Content -->
      <transition
        name="fade"
        mode="out-in"
      >
        <div
          v-if="activeTab === 'overview'"
          class="mt-4"
        >
          <AdminOverview @switch-tab="activeTab = $event" />
        </div>
        <div
          v-else-if="activeTab === 'analytics'"
          class="mt-4"
        >
          <AdminAnalytics />
        </div>
        <div
          v-else-if="activeTab === 'doctors'"
          class="mt-4"
        >
          <AdminDoctors />
        </div>
        <div
          v-else-if="activeTab === 'patients'"
          class="mt-4"
        >
          <AdminPatients />
        </div>
        <div
          v-else-if="activeTab === 'appointments'"
          class="mt-4"
        >
          <AdminAppointments />
        </div>
        <div
          v-else-if="activeTab === 'settings'"
          class="mt-4"
        >
          <AdminSettings />
        </div>
      </transition>
    </div>
  </div>
</template>

<script>
import AdminOverview from './admin/AdminOverview.vue'
import AdminAnalytics from './admin/AdminAnalytics.vue'
import AdminDoctors from './admin/AdminDoctors.vue'
import AdminPatients from './admin/AdminPatients.vue'
import AdminAppointments from './admin/AdminAppointments.vue'
import AdminSettings from './admin/AdminSettings.vue'
import { useAuthStore } from '../stores/auth.js'

export default {
  components: {
    AdminOverview,
    AdminAnalytics,
    AdminDoctors,
    AdminPatients,
    AdminAppointments,
    AdminSettings,
  },
  data() {
    return {
      activeTab: 'overview'
    }
  },
  methods: {
    async logout() {
      const authStore = useAuthStore()
      await authStore.logout()
      this.$router.push('/login')
    }
  }
}
</script>

<style scoped>
.admin-dashboard {
  min-height: 100vh;
  background-color: #f8f9fa;
}

.dashboard-hero {
  background-color: #1c1c1e; /* Apple Dark Gray */
  border-bottom: 1px solid rgba(0,0,0,0.05);
}

.modern-tabs .nav-link {
  border-radius: 8px;
  padding: 0.75rem 1rem;
  color: var(--color-text-secondary);
  font-weight: 500;
  transition: all 0.2s ease;
}

.modern-tabs .nav-link:hover {
  background-color: rgba(0,0,0,0.03);
  color: var(--color-primary);
}

.modern-tabs .nav-link.active {
  background-color: var(--color-primary-subtle);
  color: var(--color-primary);
  font-weight: 600;
}

/* Fade transition */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
