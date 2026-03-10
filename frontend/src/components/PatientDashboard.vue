<template>
  <div class="patient-dashboard">
    <!-- Hero Section -->
    <div class="dashboard-hero bg-primary text-white py-5 mb-4">
      <div class="container">
        <div class="d-flex justify-content-between align-items-center">
          <div>
            <h1 class="display-5 fw-bold mb-2">
              Patient Portal
            </h1>
            <p class="lead mb-0 opacity-75">
              Manage your health journey with ease.
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
    <div class="container pb-5">
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
                :class="{ active: activeTab === 'booking' }" 
                href="#" 
                @click.prevent="activeTab = 'booking'"
              >
                <i class="bi bi-calendar-plus me-2" />Book Appointment
              </a>
            </li>
            <li class="nav-item">
              <a 
                class="nav-link" 
                :class="{ active: activeTab === 'appointments' }" 
                href="#" 
                @click.prevent="activeTab = 'appointments'"
              >
                <i class="bi bi-calendar-check me-2" />My Appointments
              </a>
            </li>
            <li class="nav-item">
              <a 
                class="nav-link" 
                :class="{ active: activeTab === 'profile' }" 
                href="#" 
                @click.prevent="activeTab = 'profile'"
              >
                <i class="bi bi-person-circle me-2" />My Profile
              </a>
            </li>
          </ul>
        </div>
      </div>

      <!-- Tab Content -->
      <transition
        name="fade"
        mode="out-in"
      >
        <div :key="activeTab">
          <PatientOverview
            v-if="activeTab === 'overview'"
            @navigate="activeTab = $event"
          />
          <PatientAnalytics v-if="activeTab === 'analytics'" />
          <PatientBooking
            v-if="activeTab === 'booking'"
            @appointment-booked="activeTab = 'appointments'"
          />
          <PatientAppointments v-if="activeTab === 'appointments'" />
          <PatientProfile v-if="activeTab === 'profile'" />
        </div>
      </transition>
    </div>
  </div>
</template>

<script>
import PatientOverview from './patient/PatientOverview.vue'
import PatientAnalytics from './patient/PatientAnalytics.vue'
import PatientBooking from './patient/PatientBooking.vue'
import PatientAppointments from './patient/PatientAppointments.vue'
import PatientProfile from './patient/PatientProfile.vue'
import { useAuthStore } from '@/stores/auth'

export default {
  name: 'PatientDashboard',
  components: {
    PatientOverview,
    PatientAnalytics,
    PatientBooking,
    PatientAppointments,
    PatientProfile
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
      window.location.href = '/login'
    }
  }
}
</script>

<style scoped>
.patient-dashboard {
  min-height: 100vh;
  background-color: #f8f9fa;
}

.dashboard-hero {
  background-color: var(--color-primary); /* Flat color, no gradient */
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
