<template>
  <div class="doctor-patients">
    <div class="card h-100 border-0 shadow-sm">
      <div class="card-body p-0">
        <DataTable
          :columns="columns"
          :data="patients"
          :loading="loading.patients"
          searchable
          search-placeholder="Search by name, contact, or email..."
          :per-page="10"
          empty-message="No patients found"
          :show-download-button="true"
          file-name="patients.csv"
          @download-requested="exportPatientsCSV"
        >
          <!-- Custom Name Column -->
          <template #column-name="{ row }">
            <div class="d-flex align-items-center">
              <div class="avatar-circle-sm bg-secondary-subtle text-secondary me-2">
                {{ row.name.charAt(0) }}
              </div>
              <span class="fw-medium">{{ row.name }}</span>
            </div>
          </template>

          <!-- Custom Email Column -->
          <template #column-email="{ value }">
            <a
              v-if="value"
              :href="`mailto:${value}`"
              class="text-decoration-none text-muted"
            >
              {{ value }}
            </a>
            <span
              v-else
              class="text-muted"
            >
              N/A
            </span>
          </template>

          <!-- Custom Contact Column -->
          <template #column-contact="{ value }">
            <a
              v-if="value"
              :href="`tel:${value}`"
              class="text-decoration-none"
            >
              {{ value }}
            </a>
            <span
              v-else
              class="text-muted"
            >
              N/A
            </span>
          </template>

          <!-- Custom Visits Column -->
          <template #column-appointment_count="{ value }">
            <div class="text-center">
              <span class="badge bg-light text-dark border">{{ value }}</span>
            </div>
          </template>

          <!-- Actions Column -->
          <template #actions="{ row }">
            <button
              class="btn btn-sm btn-outline-primary"
              @click="viewProfile(row)"
            >
              <i class="bi bi-person-lines-fill me-1" /> Profile
            </button>
          </template>
        </DataTable>
      </div>
    </div>

    <!-- Patient Profile Modal -->
    <Modal
      v-model="showProfileModal"
      title="Patient Profile"
      size="xl"
      :show-default-footer="false"
    >
      <div v-if="selectedPatient">
        <!-- Patient Info Card -->
        <div class="card mb-4 border-0 shadow-sm bg-light">
          <div class="card-body">
            <div class="d-flex align-items-center mb-4">
              <div class="avatar-circle bg-primary text-white me-3">
                {{ selectedPatient.name.charAt(0) }}
              </div>
              <div>
                <h4 class="mb-0 fw-bold">
                  {{ selectedPatient.name }}
                </h4>
                <p class="text-muted mb-0">
                  {{ selectedPatient.email }}
                </p>
              </div>
            </div>
            <div class="row g-4">
              <div class="col-md-3">
                <small class="text-muted text-uppercase fw-bold">Age</small>
                <p class="mb-0 fw-medium">
                  {{ selectedPatient.age }} years
                </p>
              </div>
              <div class="col-md-3">
                <small class="text-muted text-uppercase fw-bold">Contact</small>
                <p class="mb-0 fw-medium">
                  {{ selectedPatient.contact }}
                </p>
              </div>
              <div class="col-md-3">
                <small class="text-muted text-uppercase fw-bold">Email</small>
                <p class="mb-0 fw-medium">
                  <a
                    v-if="selectedPatient.email"
                    :href="`mailto:${selectedPatient.email}`"
                    class="text-decoration-none"
                  >
                    {{ selectedPatient.email }}
                  </a>
                  <span v-else>N/A</span>
                </p>
              </div>
              <div class="col-md-3">
                <small class="text-muted text-uppercase fw-bold">Total Visits</small>
                <p class="mb-0 fw-medium">
                  {{ selectedPatient.appointment_count }}
                </p>
              </div>
            </div>
          </div>
        </div>

        <div class="row g-4">
          <!-- Appointment History -->
          <div class="col-lg-6">
            <div class="card h-100 border-0 shadow-sm">
              <div class="card-header bg-white border-bottom py-3">
                <h6 class="mb-0 fw-semibold">
                  <i class="bi bi-calendar-check me-2" />Recent Visits
                </h6>
              </div>
              <div class="card-body p-0">
                <div
                  v-if="loadingHistory"
                  class="text-center py-4"
                >
                  <div
                    class="spinner-border text-primary spinner-sm"
                    role="status"
                  />
                </div>
                <div
                  v-else
                  class="table-responsive"
                >
                  <table class="table table-hover mb-0 align-middle">
                    <thead class="bg-light">
                      <tr>
                        <th class="ps-4">
                          Date
                        </th>
                        <th>Status</th>
                        <th>Diagnosis</th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr
                        v-for="appt in appointmentHistory"
                        :key="appt.id"
                      >
                        <td class="ps-4">
                          <div class="d-flex flex-column">
                            <span>{{ formatDate(appt.date) }}</span>
                            <small class="text-muted">{{ formatTime(appt.time) }}</small>
                          </div>
                        </td>
                        <td>
                          <span
                            class="badge rounded-pill"
                            :class="getStatusBadgeClass(appt.status)"
                          >
                            {{ appt.status }}
                          </span>
                        </td>
                        <td
                          class="text-truncate"
                          style="max-width: 150px;"
                        >
                          {{ appt.diagnosis || 'N/A' }}
                        </td>
                      </tr>
                      <tr v-if="appointmentHistory.length === 0">
                        <td
                          colspan="3"
                          class="text-center text-muted py-4"
                        >
                          No visits yet
                        </td>
                      </tr>
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          </div>

          <!-- Prescription History -->
          <div class="col-lg-6">
            <div class="card h-100 border-0 shadow-sm">
              <div class="card-header bg-white border-bottom py-3">
                <h6 class="mb-0 fw-semibold">
                  <i class="bi bi-prescription2 me-2" />Prescriptions
                </h6>
              </div>
              <div class="card-body p-0">
                <div
                  v-if="loadingHistory"
                  class="text-center py-4"
                >
                  <div
                    class="spinner-border text-primary spinner-sm"
                    role="status"
                  />
                </div>
                <div
                  v-else
                  class="table-responsive"
                >
                  <table class="table table-hover mb-0 align-middle">
                    <thead class="bg-light">
                      <tr>
                        <th class="ps-4">
                          Date
                        </th>
                        <th>Prescription</th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr
                        v-for="record in prescriptionHistory"
                        :key="record.id"
                      >
                        <td class="ps-4">
                          {{ formatDate(record.date) }}
                        </td>
                        <td>
                          <div class="font-monospace small bg-light p-2 rounded">
                            {{ record.prescription }}
                          </div>
                        </td>
                      </tr>
                      <tr v-if="prescriptionHistory.length === 0">
                        <td
                          colspan="2"
                          class="text-center text-muted py-4"
                        >
                          No prescriptions yet
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
    </Modal>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import { useDoctorStore } from '@/stores/doctor'
import { storeToRefs } from 'pinia'
import { doctorAPI } from '@/services/api'
import DataTable from '@/components/shared/DataTable.vue'
import Modal from '@/components/shared/Modal.vue'

export default {
  name: 'DoctorPatients',
  components: {
    DataTable,
    Modal
  },
  emits: ['view-history'],
  setup() {
    const doctorStore = useDoctorStore()
    const { patients, loading } = storeToRefs(doctorStore)

    const showProfileModal = ref(false)
    const selectedPatient = ref(null)
    const loadingHistory = ref(false)
    const appointmentHistory = ref([])
    const prescriptionHistory = ref([])

    const columns = [
      { key: 'name', label: 'Name', sortable: true },
      { key: 'age', label: 'Age', sortable: true },
      { key: 'contact', label: 'Contact', sortable: false },
      { key: 'email', label: 'Email', sortable: false },
      { key: 'appointment_count', label: 'Visits', sortable: true }
    ]

    onMounted(() => {
      doctorStore.fetchPatients()
    })

    const viewProfile = async (patient) => {
      selectedPatient.value = patient
      showProfileModal.value = true
      loadingHistory.value = true
      
      try {
        const response = await doctorAPI.getPatientHistory(patient.id)
        const history = response.data.data.appointments || []
        
        appointmentHistory.value = history.map(record => ({
          id: record.id || Math.random(),
          date: record.date,
          time: record.time || '00:00',
          status: record.status || 'Completed',
          diagnosis: record.diagnosis
        }))
        
        prescriptionHistory.value = history.filter(record => record.prescription).map(record => ({
          id: record.id || Math.random(),
          date: record.date,
          diagnosis: record.diagnosis,
          prescription: record.prescription,
          notes: record.notes
        }))
      } catch (err) {
        console.error('Failed to load patient history:', err)
        appointmentHistory.value = []
        prescriptionHistory.value = []
      } finally {
        loadingHistory.value = false
      }
    }

    const formatDate = (dateString) => {
      if (!dateString) return 'N/A'
      
      try {
        // Handle different date formats
        let dateObj
        
        if (typeof dateString === 'string') {
          // Try parsing as ISO date string first
          dateObj = new Date(dateString)
          
          // If that fails or results in invalid date, try other formats
          if (isNaN(dateObj.getTime())) {
            // Try parsing as YYYY-MM-DD format
            const parts = dateString.split('-')
            if (parts.length === 3) {
              // Create date with year, month (0-indexed), day
              dateObj = new Date(parts[0], parts[1] - 1, parts[2])
            }
          }
        } else if (dateString instanceof Date) {
          dateObj = dateString
        } else {
          // Assume it's a timestamp or other format that Date constructor can handle
          dateObj = new Date(dateString)
        }
        
        // Final validation
        if (isNaN(dateObj.getTime())) {
          console.warn('Invalid date provided:', dateString)
          return 'Invalid Date'
        }
        
        return dateObj.toLocaleDateString('en-US', { 
          year: 'numeric', 
          month: 'short', 
          day: 'numeric' 
        })
      } catch (error) {
        console.error('Error formatting date:', error, 'Input:', dateString)
        return 'Invalid Date'
      }
    }

    const formatTime = (timeString) => {
      if (!timeString) return 'N/A'
      
      try {
        // If it's already a string in HH:MM format, return as is
        if (typeof timeString === 'string' && timeString.includes(':')) {
          return timeString.substring(0, 5)
        }
        
        // If it's a time object, convert to string
        if (typeof timeString === 'object') {
          return timeString.toString().substring(0, 5)
        }
        
        return timeString.toString().substring(0, 5)
      } catch (error) {
        console.error('Error formatting time:', error, 'Input:', timeString)
        return 'N/A'
      }
    }

    const getStatusBadgeClass = (status) => {
      const classes = {
        'Booked': 'bg-primary-subtle text-primary',
        'Completed': 'bg-success-subtle text-success',
        'Cancelled': 'bg-danger-subtle text-danger'
      }
      return classes[status] || 'bg-secondary-subtle text-secondary'
    }

    const exportPatientsCSV = async () => {
      try {
        const response = await doctorAPI.exportPatientsEmail();
        // Since this is now an email-based export, we just show a message
        alert('Patients CSV export initiated. You will receive an email with the file shortly.');
      } catch (err) {
        console.error('Export failed:', err);
        alert('Failed to initiate patients export. Please try again.');
      }
    };

    return {
      patients,
      loading,
      columns,
      showProfileModal,
      selectedPatient,
      loadingHistory,
      appointmentHistory,
      prescriptionHistory,
      viewProfile,
      formatDate,
      formatTime,
      getStatusBadgeClass,
      exportPatientsCSV
    }
  }
}
</script>

<style scoped>
.doctor-patients {
  animation: fadeInUp 0.4s ease-out;
}

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

.avatar-circle {
  width: 64px;
  height: 64px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  font-size: 1.75rem;
}

.bg-secondary-subtle { background-color: #f5f5f7; }
.bg-primary-subtle { background-color: #e5f2ff; }
.bg-success-subtle { background-color: #e6f9eb; }
.bg-danger-subtle { background-color: #ffeef0; }
</style>