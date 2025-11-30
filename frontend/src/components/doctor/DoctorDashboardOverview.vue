<template>
  <div class="doctor-overview">
    <!-- Stats Row -->
    <div class="row g-4 mb-4">
      <!-- Skeleton Loading State -->
      <template v-if="loading.stats">
        <div
          v-for="n in 4"
          :key="n"
          class="col-md-3"
        >
          <CardSkeleton />
        </div>
      </template>

      <!-- Actual Stats Cards -->
      <template v-else>
        <div class="col-md-3">
          <div class="card h-100 hover-lift">
            <div class="card-body">
              <div class="d-flex justify-content-between align-items-start">
                <div>
                  <p class="text-muted small mb-2 text-uppercase fw-semibold">
                    Total Appointments
                  </p>
                  <h2 class="fw-bold mb-0 text-primary">
                    {{ stats?.statistics?.total_appointments || 0 }}
                  </h2>
                </div>
                <div class="stat-icon bg-primary-subtle text-primary">
                  <i class="bi bi-calendar-check" />
                </div>
              </div>
            </div>
          </div>
        </div>

        <div class="col-md-3">
          <div class="card h-100 hover-lift">
            <div class="card-body">
              <div class="d-flex justify-content-between align-items-start">
                <div>
                  <p class="text-muted small mb-2 text-uppercase fw-semibold">
                    Today's Schedule
                  </p>
                  <h2 class="fw-bold mb-0 text-success">
                    {{ stats?.statistics?.today_appointments || 0 }}
                  </h2>
                </div>
                <div class="stat-icon bg-success-subtle text-success">
                  <i class="bi bi-calendar-event" />
                </div>
              </div>
            </div>
          </div>
        </div>

        <div class="col-md-3">
          <div class="card h-100 hover-lift">
            <div class="card-body">
              <div class="d-flex justify-content-between align-items-start">
                <div>
                  <p class="text-muted small mb-2 text-uppercase fw-semibold">
                    Total Patients
                  </p>
                  <h2 class="fw-bold mb-0 text-info">
                    {{ stats?.statistics?.total_patients || 0 }}
                  </h2>
                </div>
                <div class="stat-icon bg-info-subtle text-info">
                  <i class="bi bi-people" />
                </div>
              </div>
            </div>
          </div>
        </div>

        <div class="col-md-3">
          <div class="card h-100 hover-lift">
            <div class="card-body">
              <div class="d-flex justify-content-between align-items-start">
                <div>
                  <p class="text-muted small mb-2 text-uppercase fw-semibold">
                    Completed
                  </p>
                  <h2 class="fw-bold mb-0 text-warning">
                    {{ stats?.statistics?.completed_appointments || 0 }}
                  </h2>
                </div>
                <div class="stat-icon bg-warning-subtle text-warning">
                  <i class="bi bi-check-circle" />
                </div>
              </div>
            </div>
          </div>
        </div>
      </template>
    </div>

    <div class="row g-4">
      <!-- Recent Patients -->
      <div class="col-md-6">
        <div class="card h-100">
          <div class="card-header d-flex justify-content-between align-items-center bg-white border-bottom">
            <h5 class="mb-0 fw-semibold">
              Recent Patients
            </h5>
            <button
              class="btn btn-sm btn-link text-decoration-none"
              @click="$emit('change-tab', 'patients')"
            >
              View All
            </button>
          </div>
          <div class="card-body p-0">
            <div
              v-if="loading.stats"
              class="text-center py-5"
            >
              <div
                class="spinner-border text-primary spinner-sm"
                role="status"
              />
            </div>
            <div
              v-else-if="!stats?.recent_patients?.length"
              class="text-center text-muted py-5"
            >
              <p class="mb-0">
                No patients yet
              </p>
            </div>
            <div
              v-else
              class="table-responsive"
            >
              <table class="table table-hover mb-0 align-middle">
                <thead class="bg-light">
                  <tr>
                    <th class="ps-4">
                      Name
                    </th>
                    <th>Age</th>
                    <th>Contact</th>
                  </tr>
                </thead>
                <tbody>
                  <tr
                    v-for="patient in stats.recent_patients"
                    :key="patient.id"
                  >
                    <td class="ps-4">
                      <div class="d-flex align-items-center">
                        <div class="avatar-circle-sm bg-secondary-subtle text-secondary me-2">
                          {{ patient.name.charAt(0) }}
                        </div>
                        <span class="fw-medium">{{ patient.name }}</span>
                      </div>
                    </td>
                    <td>{{ patient.age }}</td>
                    <td>{{ patient.contact }}</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>

      <!-- Recent Appointments -->
      <div class="col-md-6">
        <div class="card h-100">
          <div class="card-header d-flex justify-content-between align-items-center bg-white border-bottom">
            <h5 class="mb-0 fw-semibold">
              Recent Appointments
            </h5>
            <button
              class="btn btn-sm btn-link text-decoration-none"
              @click="$emit('change-tab', 'appointments')"
            >
              View All
            </button>
          </div>
          <div class="card-body p-0">
            <div
              v-if="loading.stats"
              class="text-center py-5"
            >
              <div
                class="spinner-border text-primary spinner-sm"
                role="status"
              />
            </div>
            <div
              v-else-if="!stats?.recent_appointments?.length"
              class="text-center text-muted py-5"
            >
              <p class="mb-0">
                No appointments yet
              </p>
            </div>
            <div
              v-else
              class="table-responsive"
            >
              <table class="table table-hover mb-0 align-middle">
                <thead class="bg-light">
                  <tr>
                    <th class="ps-4">
                      Patient
                    </th>
                    <th>Date & Time</th>
                    <th>Status</th>
                  </tr>
                </thead>
                <tbody>
                  <tr
                    v-for="appointment in stats.recent_appointments"
                    :key="appointment.id"
                  >
                    <td class="ps-4">
                      <span class="fw-medium">{{ appointment.patient_name }}</span>
                    </td>
                    <td>
                      <div class="d-flex flex-column">
                        <span>{{ formatDate(appointment.date) }}</span>
                        <small class="text-muted">{{ formatTime(appointment.time) }}</small>
                      </div>
                    </td>
                    <td>
                      <span
                        class="badge rounded-pill"
                        :class="getStatusBadgeClass(appointment.status)"
                      >
                        {{ appointment.status }}
                      </span>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { onMounted } from 'vue'
import { useDoctorStore } from '@/stores/doctor'
import { storeToRefs } from 'pinia'
import CardSkeleton from '../shared/CardSkeleton.vue'

export default {
  name: 'DoctorDashboardOverview',
  components: {
    CardSkeleton
  },
  setup() {
    const doctorStore = useDoctorStore()
    const { stats, loading } = storeToRefs(doctorStore)

    onMounted(() => {
      doctorStore.fetchDashboard()
    })

    const formatDate = (dateString) => {
      const date = new Date(dateString)
      return date.toLocaleDateString('en-US', { 
        month: 'short', 
        day: 'numeric' 
      })
    }

    const formatTime = (timeString) => {
      return timeString.substring(0, 5)
    }

    const getStatusBadgeClass = (status) => {
      const classes = {
        'Booked': 'bg-primary-subtle text-primary',
        'Completed': 'bg-success-subtle text-success',
        'Cancelled': 'bg-danger-subtle text-danger',
        'Pending': 'bg-warning-subtle text-warning'
      }
      return classes[status] || 'bg-secondary-subtle text-secondary'
    }

    return {
      stats,
      loading,
      formatDate,
      formatTime,
      getStatusBadgeClass
    }
  }
}
</script>

<style scoped>
.doctor-overview {
  animation: fadeInUp 0.4s ease-out;
}

.stat-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.5rem;
}

.bg-primary-subtle { background-color: #e5f2ff; }
.bg-success-subtle { background-color: #e6f9eb; }
.bg-info-subtle { background-color: #eef9fe; }
.bg-warning-subtle { background-color: #fff8e6; }
.bg-danger-subtle { background-color: #ffeef0; }
.bg-secondary-subtle { background-color: #f5f5f7; }

.avatar-circle-sm {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  font-size: 0.875rem;
}

.table th {
  font-weight: 600;
  font-size: 0.875rem;
  color: var(--color-gray-600);
  border-bottom-width: 1px;
}

.badge {
  font-weight: 500;
  padding: 0.35em 0.8em;
}
</style>
