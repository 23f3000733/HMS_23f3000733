<template>
  <div class="patient-analytics">
    <!-- Header -->
    <div class="d-flex justify-content-between align-items-center mb-4">
      <h5 class="mb-0 fw-bold text-dark">
        My Health Overview
      </h5>
      <div class="text-muted small">
        All Time
      </div>
    </div>

    <!-- Key Metrics Row -->
    <div class="row g-4 mb-4">
      <div class="col-md-6">
        <div class="card border-0 shadow-sm h-100">
          <div class="card-body">
            <h6 class="text-muted text-uppercase small fw-bold mb-2">
              Total Visits
            </h6>
            <h2 class="fw-bold mb-0 text-primary">
              {{ totalVisits }}
            </h2>
          </div>
        </div>
      </div>
      <div class="col-md-6">
        <div class="card border-0 shadow-sm h-100">
          <div class="card-body">
            <h6 class="text-muted text-uppercase small fw-bold mb-2">
              Top Doctor
            </h6>
            <h2
              class="fw-bold mb-0 text-success"
              style="font-size: 1.5rem;"
            >
              {{ topDoctorName }}
            </h2>
          </div>
        </div>
      </div>
    </div>

    <div class="row g-4">
      <!-- Visit Status -->
      <div class="col-lg-6">
        <div class="card border-0 shadow-sm h-100">
          <div class="card-header bg-white border-0 pt-4 px-4 pb-0">
            <h6 class="fw-bold mb-0">
              Visit History
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

      <!-- Top Doctors List -->
      <div class="col-lg-6">
        <div class="card border-0 shadow-sm h-100">
          <div class="card-header bg-white border-0 pt-4 px-4 pb-0">
            <h6 class="fw-bold mb-0">
              Most Visited Doctors
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
                    {{ doc.count }} Visits
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
    </div>
  </div>
</template>

<script>
import { computed, onMounted } from 'vue'
import { usePatientStore } from '@/stores/patient'
import { storeToRefs } from 'pinia'
import  DonutChart from '../common/charts/DonutChart.vue'

export default {
  name: 'PatientAnalytics',
  components: {
    DonutChart
  },
  setup() {
    const patientStore = usePatientStore()
    const { analytics } = storeToRefs(patientStore)

    const totalVisits = computed(() => analytics.value?.total_visits || 0)

    const statusData = computed(() => {
      if (!analytics.value?.status_distribution) return []
      const colors = { 'Completed': '#34c759', 'Booked': '#007aff', 'Cancelled': '#ff3b30' }
      return analytics.value.status_distribution.map(s => ({
        label: s.status,
        value: s.count,
        color: colors[s.status] || '#8e8e93'
      }))
    })

    const topDoctors = computed(() => analytics.value?.top_doctors || [])
    
    const topDoctorName = computed(() => {
      return topDoctors.value.length > 0 ? `Dr. ${  topDoctors.value[0].name}` : 'N/A'
    })

    onMounted(() => {
      patientStore.fetchAnalytics()
    })

    return {
      statusData,
      topDoctors,
      totalVisits,
      topDoctorName
    }
  }
}
</script>

<style scoped>
.patient-analytics { animation: fadeInUp 0.4s ease-out; }
.avatar-circle { width: 32px; height: 32px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 0.85rem; }
.bg-primary-subtle { background-color: #e5f2ff; }
</style>
