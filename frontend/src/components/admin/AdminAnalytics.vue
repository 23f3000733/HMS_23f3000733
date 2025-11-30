<template>
  <div class="admin-analytics">
    <!-- Header -->
    <div class="d-flex justify-content-between align-items-center mb-4">
      <h5 class="mb-0 fw-bold text-dark">
        Analytics Overview
      </h5>
      <div class="text-muted small">
        Last 7 Days
      </div>
    </div>

    <!-- Key Metrics Row -->
    <div class="row g-4 mb-4">
      <div class="col-md-3">
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
      <div class="col-md-3">
        <div class="card border-0 shadow-sm h-100">
          <div class="card-body">
            <h6 class="text-muted text-uppercase small fw-bold mb-2">
              Active Doctors
            </h6>
            <h2 class="fw-bold mb-0 text-success">
              {{ totalDoctors }}
            </h2>
          </div>
        </div>
      </div>
      <div class="col-md-3">
        <div class="card border-0 shadow-sm h-100">
          <div class="card-body">
            <h6 class="text-muted text-uppercase small fw-bold mb-2">
              Total Patients
            </h6>
            <h2 class="fw-bold mb-0 text-info">
              {{ totalPatients }}
            </h2>
          </div>
        </div>
      </div>
      <div class="col-md-3">
        <div class="card border-0 shadow-sm h-100">
          <div class="card-body">
            <h6 class="text-muted text-uppercase small fw-bold mb-2">
              Completion Rate
            </h6>
            <h2 class="fw-bold mb-0 text-warning">
              {{ completionRate }}%
            </h2>
          </div>
        </div>
      </div>
    </div>

    <div class="row g-4 mb-4">
      <!-- Appointment Trends -->
      <div class="col-lg-8">
        <div class="card border-0 shadow-sm h-100">
          <div class="card-header bg-white border-0 pt-4 px-4 pb-0">
            <h6 class="fw-bold mb-0">
              Appointment Trends
            </h6>
          </div>
          <div class="card-body px-4">
            <SimpleBarChart 
              v-if="trendsData.length" 
              :data="trendsData" 
              color="#007aff" 
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
              Status Distribution
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

    <div class="row g-4">
      <!-- Top Doctors -->
      <div class="col-lg-6">
        <div class="card border-0 shadow-sm h-100">
          <div class="card-header bg-white border-0 pt-4 px-4 pb-0">
            <h6 class="fw-bold mb-0">
              Top Performing Doctors
            </h6>
          </div>
          <div class="card-body p-0">
            <div class="list-group list-group-flush">
              <div
                v-for="(doc, index) in topDoctors"
                :key="index"
                class="list-group-item px-4 py-3 border-0"
              >
                <div class="d-flex align-items-center justify-content-between">
                  <div class="d-flex align-items-center">
                    <div class="avatar-circle bg-light text-primary me-3 fw-bold">
                      {{ index + 1 }}
                    </div>
                    <span class="fw-medium">Dr. {{ doc.name }}</span>
                  </div>
                  <span class="badge bg-primary-subtle text-primary rounded-pill">
                    {{ doc.count }} Appts
                  </span>
                </div>
              </div>
              <div
                v-if="topDoctors.length === 0"
                class="text-center text-muted py-4"
              >
                No data available
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Patient Demographics -->
      <div class="col-lg-6">
        <div class="card border-0 shadow-sm h-100">
          <div class="card-header bg-white border-0 pt-4 px-4 pb-0">
            <h6 class="fw-bold mb-0">
              Patient Age Groups
            </h6>
          </div>
          <div class="card-body px-4">
            <SimpleBarChart 
              v-if="demographicsData.length" 
              :data="demographicsData" 
              color="#34c759" 
              :height="200" 
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
import { useAdminStore } from '@/stores/admin'
import { storeToRefs } from 'pinia'
import SimpleBarChart from '../common/charts/SimpleBarChart.vue'
import DonutChart from '../common/charts/DonutChart.vue'

export default {
  name: 'AdminAnalytics',
  components: {
    SimpleBarChart,
    DonutChart
  },
  setup() {
    const adminStore = useAdminStore()
    const { analytics, stats } = storeToRefs(adminStore)

    // Computed properties for metrics
    const totalDoctors = computed(() => stats.value?.doctors || 0)
    const totalPatients = computed(() => stats.value?.patients || 0)
    const totalAppointments = computed(() => stats.value?.appointments || 0)

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
      const colors = { 'Completed': '#34c759', 'Booked': '#007aff', 'Cancelled': '#8e8e93' }
      return analytics.value.status_distribution.map(s => ({
        label: s.status,
        value: s.count,
        color: colors[s.status] || '#ffcc00'
      }))
    })

    const topDoctors = computed(() => analytics.value?.top_doctors || [])

    const demographicsData = computed(() => {
      if (!analytics.value?.demographics) return []
      return analytics.value.demographics.map(d => ({
        label: d.group,
        value: d.count
      }))
    })

    const completionRate = computed(() => {
      if (!statusData.value.length) return 0
      const completed = statusData.value.find(s => s.label === 'Completed')?.value || 0
      const total = statusData.value.reduce((acc, curr) => acc + curr.value, 0)
      return total ? Math.round((completed / total) * 100) : 0
    })

    onMounted(() => {
      adminStore.fetchAnalytics()
      adminStore.fetchStats()
    })

    return {
      trendsData,
      statusData,
      topDoctors,
      demographicsData,
      totalAppointments,
      totalDoctors,
      totalPatients,
      completionRate
    }
  }
}
</script>

<style scoped>
.admin-analytics { animation: fadeInUp 0.4s ease-out; }
.avatar-circle { width: 32px; height: 32px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 0.85rem; }
.bg-primary-subtle { background-color: #e5f2ff; }
</style>
