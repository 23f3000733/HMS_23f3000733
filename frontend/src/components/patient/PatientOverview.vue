<template>
  <div class="patient-overview">
    <!-- Stats Cards -->
    <div class="row g-4 mb-4">
      <!-- Skeleton Loading State -->
      <template v-if="loading.stats">
        <div
          v-for="n in 2"
          :key="n"
          class="col-md-6"
        >
          <CardSkeleton />
        </div>
      </template>
      
      <!-- Actual Stats Cards -->
      <template v-else>
        <div class="col-md-6">
          <div class="card border-0 shadow-sm h-100 hover-lift">
            <div class="card-body p-4">
              <div class="d-flex justify-content-between align-items-center">
                <div>
                  <p class="text-muted text-uppercase small fw-bold mb-1">
                    Total Appointments
                  </p>
                  <h2 class="display-6 fw-bold mb-0 text-primary">
                    {{ stats?.total_appointments || 0 }}
                  </h2>
                </div>
                <div class="icon-box bg-primary-subtle text-primary rounded-circle p-3">
                  <i class="bi bi-calendar-event fs-4" />
                </div>
              </div>
            </div>
          </div>
        </div>
        <div class="col-md-6">
          <div class="card border-0 shadow-sm h-100 hover-lift">
            <div class="card-body p-4">
              <div class="d-flex justify-content-between align-items-center">
                <div>
                  <p class="text-muted text-uppercase small fw-bold mb-1">
                    Completed Visits
                  </p>
                  <h2 class="display-6 fw-bold mb-0 text-success">
                    {{ stats?.completed_appointments || 0 }}
                  </h2>
                </div>
                <div class="icon-box bg-success-subtle text-success rounded-circle p-3">
                  <i class="bi bi-check-circle fs-4" />
                </div>
              </div>
            </div>
          </div>
        </div>
      </template>
    </div>

    <div class="row g-4">
      <!-- Upcoming Appointment -->
      <div class="col-lg-6">
        <div class="card border-0 shadow-sm h-100">
          <div class="card-header bg-white border-bottom py-3">
            <h5 class="mb-0 fw-semibold">
              <i class="bi bi-clock-history me-2 text-primary" />Next Appointment
            </h5>
          </div>
          <div class="card-body p-4 d-flex flex-column justify-content-center">
            <div
              v-if="upcomingAppointment"
              class="text-center"
            >
              <div class="mb-4">
                <div class="display-6 fw-bold text-dark mb-1">
                  {{ upcomingAppointment.date }}
                </div>
                <div class="fs-4 text-muted">
                  {{ upcomingAppointment.time }}
                </div>
              </div>
              
              <div
                class="p-3 bg-light rounded-3 mb-4 text-start d-inline-block w-100"
                style="max-width: 400px;"
              >
                <div class="d-flex align-items-center">
                  <div class="avatar-circle bg-primary text-white me-3">
                    {{ upcomingAppointment.doctor_name.charAt(0) }}
                  </div>
                  <div>
                    <h6 class="fw-bold mb-0">
                      Dr. {{ upcomingAppointment.doctor_name }}
                    </h6>
                    <small class="text-muted">{{ upcomingAppointment.specialization }}</small>
                  </div>
                </div>
              </div>

              <button
                class="btn btn-outline-primary w-100"
                @click="$emit('navigate', 'appointments')"
              >
                View Details
              </button>
            </div>
            <div
              v-else
              class="text-center py-5"
            >
              <div class="mb-3 text-muted opacity-25">
                <i
                  class="bi bi-calendar-x"
                  style="font-size: 4rem;"
                />
              </div>
              <h5 class="text-muted fw-normal mb-3">
                No upcoming appointments
              </h5>
              <button
                class="btn btn-primary px-4"
                @click="$emit('navigate', 'booking')"
              >
                Book Now
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Recent Activity -->
      <div class="col-lg-6">
        <div class="card border-0 shadow-sm h-100">
          <div class="card-header bg-white border-bottom py-3">
            <h5 class="mb-0 fw-semibold">
              <i class="bi bi-activity me-2 text-primary" />Recent Activity
            </h5>
          </div>
          <div class="card-body p-0">
            <div
              v-if="recentActivity.length > 0"
              class="list-group list-group-flush"
            >
              <div
                v-for="(activity, index) in recentActivity"
                :key="index"
                class="list-group-item p-3 border-bottom-0"
              >
                <div class="d-flex">
                  <div class="me-3 mt-1">
                    <i class="bi bi-circle-fill text-primary small-dot" />
                  </div>
                  <div>
                    <p class="mb-1 fw-medium">
                      {{ activity.description }}
                    </p>
                    <small class="text-muted">{{ formatTimestamp(activity.timestamp) }}</small>
                  </div>
                </div>
              </div>
            </div>
            <div
              v-else
              class="text-center py-5 text-muted"
            >
              <p class="mb-0">
                No recent activity
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { computed, onMounted } from 'vue'
import { usePatientStore } from '@/stores/patient'
import { storeToRefs } from 'pinia'
import CardSkeleton from '../shared/CardSkeleton.vue'

export default {
  name: 'PatientOverview',
  components: {
    CardSkeleton
  },
  setup() {
    const patientStore = usePatientStore()
    const { stats, loading } = storeToRefs(patientStore)

    // Computed properties for dashboard data
    const upcomingAppointment = computed(() => stats.value?.upcoming_appointment || null)
    const recentActivity = computed(() => stats.value?.recent_activity || [])

    onMounted(() => {
      patientStore.fetchDashboard()
    })

    const formatTimestamp = (timestamp) => {
      return new Date(timestamp).toLocaleDateString('en-US', {
        month: 'short', day: 'numeric', hour: 'numeric', minute: '2-digit'
      })
    }

    return {
      stats,
      loading,
      upcomingAppointment,
      recentActivity,
      formatTimestamp
    }
  }
}
</script>

<style scoped>
.patient-overview {
  animation: fadeInUp 0.4s ease-out;
}

.hover-lift {
  transition: transform 0.2s, box-shadow 0.2s;
}

.hover-lift:hover {
  transform: translateY(-2px);
  box-shadow: 0 .5rem 1rem rgba(0,0,0,.05)!important;
}

.icon-box {
  width: 56px;
  height: 56px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.avatar-circle {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  font-size: 1.2rem;
}

.small-dot {
  font-size: 0.5rem;
  opacity: 0.5;
}

.bg-primary-subtle { background-color: #e5f2ff; }
.bg-success-subtle { background-color: #e6f9eb; }
</style>
