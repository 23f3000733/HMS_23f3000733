<template>
  <div class="doctor-analytics">
    <!-- Header -->
    <div class="d-flex justify-content-between align-items-center mb-4">
      <h5 class="mb-0 fw-bold text-dark">
        My Performance
      </h5>
      <div class="text-muted small">
        Last 7 Days
      </div>
    </div>

    <!-- Key Metrics Row -->
    <div class="row g-4 mb-4">
      <div class="col-md-4">
        <div class="card border-0 shadow-sm h-100">
          <div class="card-body">
            <h6 class="text-muted text-uppercase small fw-bold mb-2">
              Total Appointments
            </h6>
            <h2 class="fw-bold mb-0 text-primary">
              {{ totalAppointments }}
            </h2>
          </div>
        </div>
      </div>
      <div class="col-md-4">
        <div class="card border-0 shadow-sm h-100">
          <div class="card-body">
            <h6 class="text-muted text-uppercase small fw-bold mb-2">
              Unique Patients
            </h6>
            <h2 class="fw-bold mb-0 text-info">
              {{ uniquePatients }}
            </h2>
          </div>
        </div>
      </div>
      <div class="col-md-4">
        <div class="card border-0 shadow-sm h-100">
          <div class="card-body">
            <h6 class="text-muted text-uppercase small fw-bold mb-2">
              Completion Rate
            </h6>
            <h2 class="fw-bold mb-0 text-success">
              {{ completionRate }}%
            </h2>
          </div>
        </div>
      </div>
    </div>

    <div class="row g-4">
      <!-- Appointment Trends -->
      <div class="col-lg-8">
        <div class="card border-0 shadow-sm h-100">
          <div class="card-header bg-white border-0 pt-4 px-4 pb-0">
            <h6 class="fw-bold mb-0">
              Appointment Activity
            </h6>
          </div>
          <div class="card-body px-4">
            <SimpleBarChart 
              v-if="trendsData.length" 
              :data="trendsData" 
              color="#5856d6" 
              :height="250" 
            />
            <div
              v-else
              class="text-center text-muted py-5"
            >
              No data available
            </div>
          </div>
        </div>
      </div>

      <!-- Status Distribution -->
      <div class="col-lg-4">
        <div class="card border-0 shadow-sm h-100">
          <div class="card-header bg-white border-0 pt-4 px-4 pb-0">
            <h6 class="fw-bold mb-0">
              Appointment Status
            </h6>
          </div>
          <div class="card-body d-flex align-items-center justify-content-center">
            <DonutChart 
              v-if="statusData.length" 
              :data="statusData" 
            />
            <div
              v-else
              class="text-center text-muted py-5"
            >
              No data available
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { onMounted, computed } from 'vue'
import { useDoctorStore } from '@/stores/doctor'
import { storeToRefs } from 'pinia'
import SimpleBarChart from '../common/charts/SimpleBarChart.vue'
import DonutChart from '../common/charts/DonutChart.vue'

export default {
  name: 'DoctorAnalytics',
  components: {
    SimpleBarChart,
    DonutChart
  },
  setup() {
    const doctorStore = useDoctorStore()
    const { analytics } = storeToRefs(doctorStore)

    // Computed properties for metrics
    const totalAppointments = computed(() => analytics.value?.total_appointments || 0)
    const uniquePatients = computed(() => analytics.value?.unique_patients || 0)
    
    // Computed properties for charts
    const trendsData = computed(() => {
      if (!analytics.value?.trends) return []
      return analytics.value.trends.map(t => ({
        label: new Date(t.date).toLocaleDateString('en-US', { weekday: 'short' }),
        value: t.count
      }))
    })

    const statusData = computed(() => {
      if (!analytics.value?.status_distribution) return []
      const colors = { 'Completed': '#34c759', 'Pending': '#007aff', 'Cancelled': '#ff3b30', 'Booked': '#5856d6' }
      return analytics.value.status_distribution.map(s => ({
        label: s.status,
        value: s.count,
        color: colors[s.status] || '#8e8e93'
      }))
    })

    const completionRate = computed(() => {
      if (!totalAppointments.value) return 0
      const completed = statusData.value.find(s => s.label === 'Completed')?.value || 0
      return Math.round((completed / totalAppointments.value) * 100)
    })

    onMounted(() => {
      doctorStore.fetchAnalytics()
    })

    return {
      trendsData,
      statusData,
      totalAppointments,
      uniquePatients,
      completionRate
    }
  }
}
</script>

<style scoped>
.doctor-analytics { animation: fadeInUp 0.4s ease-out; }
</style>
