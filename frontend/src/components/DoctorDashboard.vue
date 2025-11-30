<template>
  <div class="doctor-dashboard">
    <!-- Hero Section -->
    <div class="hero-section mb-4">
      <div class="container-fluid px-4 py-5 bg-primary text-white">
        <div class="row align-items-center">
          <div class="col-md-8">
            <h1 class="fw-bold mb-2">
              <i class="bi bi-heart-pulse-fill me-3" />Doctor Dashboard
            </h1>
            <p class="lead text-white-50 mb-0">
              Manage your appointments and patients
            </p>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Main Content -->
    <div class="container-fluid px-4">
      <!-- Tabs -->
      <ul class="nav nav-tabs modern-tabs mb-4">
        <li class="nav-item">
          <a
            class="nav-link"
            :class="{ active: activeTab === 'overview' }"
            href="#"
            @click.prevent="activeTab = 'overview'"
          >
            <i class="bi bi-speedometer2" /> Overview
          </a>
        </li>
        <li class="nav-item">
          <a
            class="nav-link"
            :class="{ active: activeTab === 'analytics' }"
            href="#"
            @click.prevent="activeTab = 'analytics'"
          >
            <i class="bi bi-graph-up" /> Analytics
          </a>
        </li>
        <li class="nav-item">
          <a
            class="nav-link"
            :class="{ active: activeTab === 'appointments' }"
            href="#"
            @click.prevent="activeTab = 'appointments'"
          >
            <i class="bi bi-calendar-check" /> Appointments
          </a>
        </li>
        <li class="nav-item">
          <a
            class="nav-link"
            :class="{ active: activeTab === 'patients' }"
            href="#"
            @click.prevent="activeTab = 'patients'"
          >
            <i class="bi bi-people" /> My Patients
          </a>
        </li>
        <li class="nav-item">
          <a
            class="nav-link"
            :class="{ active: activeTab === 'prescriptions' }"
            href="#"
            @click.prevent="activeTab = 'prescriptions'"
          >
            <i class="bi bi-prescription2" /> Prescriptions
          </a>
        </li>
        <li class="nav-item">
          <a
            class="nav-link"
            :class="{ active: activeTab === 'profile' }"
            href="#"
            @click.prevent="activeTab = 'profile'"
          >
            <i class="bi bi-person-circle" /> Profile
          </a>
        </li>
      </ul>
      
      <!-- Tab Content -->
      <transition
        name="fade"
        mode="out-in"
      >
        <div class="tab-content py-2">
          <DoctorDashboardOverview
            v-if="activeTab === 'overview'"
            @change-tab="changeTab"
          />
          <DoctorAnalytics v-if="activeTab === 'analytics'" />
          <DoctorAppointments v-if="activeTab === 'appointments'" />
          <DoctorPatients
            v-if="activeTab === 'patients'"
            @change-tab="changeTab"
          />
          <DoctorPrescriptions v-if="activeTab === 'prescriptions'" />
          <DoctorProfile v-if="activeTab === 'profile'" />
        </div>
      </transition>
    </div>
  </div>
</template>

<script>
import DoctorDashboardOverview from './doctor/DoctorDashboardOverview.vue'
import DoctorAnalytics from './doctor/DoctorAnalytics.vue'
import DoctorAppointments from './doctor/DoctorAppointments.vue'
import DoctorPatients from './doctor/DoctorPatients.vue'
import DoctorPrescriptions from './doctor/DoctorPrescriptions.vue'
import DoctorProfile from './doctor/DoctorProfile.vue'

export default {
  name: 'DoctorDashboard',
  components: {
    DoctorDashboardOverview,
    DoctorAnalytics,
    DoctorAppointments,
    DoctorPatients,
    DoctorPrescriptions,
    DoctorProfile
  },
  data() {
    return {
      activeTab: 'overview'
    }
  },
  methods: {
    changeTab(tabName) {
      this.activeTab = tabName
    }
  }
}
</script>

<style scoped>
.hero-section {
  margin-left: -1.5rem;
  margin-right: -1.5rem;
  margin-top: -1.5rem;
}

.modern-tabs .nav-link {
  color: var(--color-gray-600);
  border: none;
  border-bottom: 2px solid transparent;
  padding: 1rem 1.5rem;
  font-weight: 500;
  transition: all 0.2s ease;
}

.modern-tabs .nav-link:hover {
  color: var(--color-primary);
  background-color: transparent;
}

.modern-tabs .nav-link.active {
  color: var(--color-primary);
  border-bottom-color: var(--color-primary);
  background-color: transparent;
  font-weight: 600;
}

.modern-tabs .nav-link i {
  margin-right: 0.5rem;
}
</style>
