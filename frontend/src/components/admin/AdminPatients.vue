<template>
  <div class="admin-patients">
    <!-- Header & Actions -->
    <div class="d-flex justify-content-between align-items-center mb-4">
      <h5 class="mb-0 fw-bold text-dark">
        Patients Management
      </h5>
      <button
        class="btn btn-primary shadow-sm"
        @click="showAddModal = true"
      >
        <i class="bi bi-plus-lg me-2" />Add Patient
      </button>
    </div>

    <!-- Patients Table -->
    <div class="card border-0 shadow-sm">
      <div class="card-body p-0">
        <DataTable
          :columns="columns"
          :data="processedPatients"
          :loading="loading.patients"
          searchable
          search-placeholder="Search by name or email..."
          :per-page="10"
          empty-message="No patients found"
          show-download-button
          file-name="all-patients.csv"
          @download-requested="exportPatientsCSV"
        >
          <!-- Custom Name Column -->
          <template #column-name="{ row }">
            <div class="d-flex align-items-center">
              <div class="avatar-circle bg-success-subtle text-success me-3">
                {{ row?.name?.charAt(0) || '?' }}
              </div>
              <span class="fw-medium">{{ row?.name || 'Unknown' }}</span>
            </div>
          </template>

          <!-- Custom Status Column -->
          <template #column-active="{ value, row }">
            <span
              v-if="row?.flagged"
              class="badge rounded-pill bg-danger-subtle text-danger"
            >Flagged</span>
            <span
              v-else
              class="badge rounded-pill"
              :class="value ? 'bg-success-subtle text-success' : 'bg-secondary-subtle text-secondary'"
            >
              {{ value ? 'Active' : 'Inactive' }}
            </span>
          </template>

          <!-- Actions Column -->
          <template #actions="{ row }">
            <div class="btn-group btn-group-sm">
              <button
                class="btn btn-outline-primary"
                title="View Profile"
                @click="viewProfile(row)"
                :disabled="!row"
              >
                <i class="bi bi-person-lines-fill" />
              </button>
              <button 
                class="btn" 
                :class="(row?.flagged) ? 'btn-outline-success' : 'btn-outline-warning'"
                :title="(row?.flagged) ? 'Unflag' : 'Flag'"
                @click="toggleFlag(row)"
                :disabled="!row"
              >
                <i :class="(row?.flagged) ? 'bi bi-flag-fill' : 'bi bi-flag'" />
              </button>
              <button
                v-if="!row?.active"
                class="btn btn-outline-success"
                title="Reactivate"
                @click="reactivatePatient(row)"
                :disabled="!row"
              >
                <i class="bi bi-arrow-repeat" />
              </button>
              <button
                class="btn btn-outline-danger"
                title="Delete"
                @click="deletePatient(row)"
                :disabled="!row"
              >
                <i class="bi bi-trash" />
              </button>
            </div>
          </template>
        </DataTable>
      </div>
    </div>

    <!-- Add Patient Modal -->
    <Modal
      v-model="showAddModal"
      title="New Patient Registration"
      confirm-text="Create Account"
      @confirm="handleSubmit"
    >
      <form
        id="patientForm"
        @submit.prevent="handleSubmit"
      >
        <div class="row g-3">
          <div class="col-md-6">
            <label class="form-label small text-muted text-uppercase fw-bold">Name</label>
            <input
              v-model="formData.name"
              type="text"
              class="form-control"
              required
            >
          </div>
          <div class="col-md-6">
            <label class="form-label small text-muted text-uppercase fw-bold">Email</label>
            <input
              v-model="formData.email"
              type="email"
              class="form-control"
              required
            >
          </div>
          <div class="col-md-6">
            <label class="form-label small text-muted text-uppercase fw-bold">Password</label>
            <input
              v-model="formData.password"
              type="password"
              class="form-control"
              required
            >
          </div>
          <div class="col-md-6">
            <label class="form-label small text-muted text-uppercase fw-bold">Age</label>
            <input
              v-model="formData.age"
              type="number"
              class="form-control"
              required
            >
          </div>
          <div class="col-md-6">
            <label class="form-label small text-muted text-uppercase fw-bold">Contact</label>
            <input
              v-model="formData.contact"
              type="text"
              class="form-control"
              required
            >
          </div>
        </div>
      </form>
    </Modal>

    <!-- Patient Profile Modal -->
    <Modal
      v-model="showViewModal"
      title="Patient Profile"
      size="large"
      :show-default-footer="false"
    >
      <div
        v-if="viewingPatient"
        class="row g-4"
      >
        <!-- Info Column -->
        <div class="col-lg-4">
          <div class="text-center mb-4">
            <div class="avatar-circle-lg bg-success-subtle text-success mx-auto mb-3">
              {{ viewingPatient.patient?.name?.charAt(0) || '?' }}
            </div>
            <h4 class="fw-bold mb-1">
              {{ viewingPatient.patient?.name || 'Unknown' }}
            </h4>
            <p class="text-muted">
              {{ viewingPatient.patient?.email || 'No email' }}
            </p>
          </div>
          
          <div class="card bg-light border-0 mb-3">
            <div class="card-body">
              <div class="d-flex justify-content-between mb-2">
                <span class="text-muted">Age</span>
                <span class="fw-medium">{{ viewingPatient.patient?.age || 'N/A' }} Years</span>
              </div>
              <div class="d-flex justify-content-between mb-2">
                <span class="text-muted">Contact</span>
                <span class="fw-medium">{{ viewingPatient.patient?.contact || 'N/A' }}</span>
              </div>
              <div class="d-flex justify-content-between">
                <span class="text-muted">Joined</span>
                <span class="fw-medium">{{ viewingPatient.patient?.created_at ? new Date(viewingPatient.patient.created_at).toLocaleDateString() : 'N/A' }}</span>
              </div>
            </div>
          </div>

          <div class="card bg-light border-0">
            <div class="card-body">
              <h6 class="fw-bold mb-2">
                Medical History
              </h6>
              <p class="small text-muted mb-0">
                {{ viewingPatient.patient?.medical_history || 'No medical history recorded.' }}
              </p>
            </div>
          </div>
        </div>

        <!-- Details Column -->
        <div class="col-lg-8">
          <h6 class="fw-bold mb-3">
            Activity Log
          </h6>
          <div class="card border-0 shadow-sm mb-4">
            <div class="card-body p-0">
              <div
                v-if="viewingPatient.activity_logs && viewingPatient.activity_logs.length > 0"
                class="list-group list-group-flush"
                style="max-height: 300px; overflow-y: auto;"
              >
                <div
                  v-for="log in viewingPatient.activity_logs"
                  :key="log.id"
                  class="list-group-item"
                >
                  <div class="d-flex justify-content-between">
                    <div>
                      <span class="badge bg-light text-dark border me-2">{{ log.activity_type }}</span>
                      <span>{{ log.description }}</span>
                    </div>
                    <small class="text-muted">{{ log.timestamp ? new Date(log.timestamp).toLocaleDateString() : 'N/A' }}</small>
                  </div>
                </div>
              </div>
              <div
                v-else
                class="text-center py-3 text-muted"
              >
                No activity recorded
              </div>
            </div>
          </div>

          <h6 class="fw-bold mb-3">
            Recent Appointments
          </h6>
          <div class="card border-0 shadow-sm">
            <div class="card-body p-0">
              <div
                v-if="viewingPatient.appointments && viewingPatient.appointments.length > 0"
                class="table-responsive"
              >
                <table class="table table-hover mb-0">
                  <thead class="bg-light">
                    <tr>
                      <th>Date</th>
                      <th>Doctor</th>
                      <th>Diagnosis</th>
                      <th>Status</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr
                      v-for="appt in viewingPatient.appointments"
                      :key="appt.id"
                    >
                      <td>{{ appt.date || 'N/A' }}</td>
                      <td>{{ appt.doctor_name ? `Dr. ${appt.doctor_name}` : 'Unknown Doctor' }}</td>
                      <td>
                        <div v-if="appt.diagnosis">
                          <span class="fw-medium">{{ appt.diagnosis }}</span>
                          <div
                            v-if="appt.prescription"
                            class="small text-muted text-truncate"
                            style="max-width: 200px;"
                          >
                            {{ appt.prescription }}
                          </div>
                        </div>
                        <span
                          v-else
                          class="text-muted small"
                        >-</span>
                      </td>
                      <td>
                        <span
                          class="badge rounded-pill"
                          :class="{
                            'bg-primary-subtle text-primary': appt.status === 'Booked',
                            'bg-success-subtle text-success': appt.status === 'Completed',
                            'bg-secondary-subtle text-secondary': appt.status === 'Cancelled'
                          }"
                        >{{ appt.status || 'Unknown' }}</span>
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>
              <div
                v-else
                class="text-center py-3 text-muted"
              >
                No appointments found
              </div>
            </div>
          </div>
        </div>
      </div>
    </Modal>
  </div>
</template>

<script>
import { ref, onMounted, computed } from 'vue'
import { useAdminStore } from '@/stores/admin'
import { storeToRefs } from 'pinia'
import { adminAPI } from '@/services/api'
import DataTable from '@/components/shared/DataTable.vue'
import Modal from '@/components/shared/Modal.vue'

export default {
  name: 'AdminPatients',
  components: {
    DataTable,
    Modal
  },
  setup() {
    const adminStore = useAdminStore()
    const { patients, loading } = storeToRefs(adminStore)
    
    // Modal states
    const showAddModal = ref(false)
    const showViewModal = ref(false)
    
    // Form data
    const formData = ref({
      name: '',
      email: '',
      password: '',
      age: '',
      contact: ''
    })
    
    const viewingPatient = ref(null)

    // Process patients data to ensure correct structure
    const processedPatients = computed(() => {
      if (!patients.value) return []
      
      // Handle both array and object responses
      if (Array.isArray(patients.value)) {
        return patients.value
      }
      
      // Handle paginated response
      if (patients.value.patients && Array.isArray(patients.value.patients)) {
        return patients.value.patients
      }
      
      // Handle single patient object
      if (patients.value.id) {
        return [patients.value]
      }
      
      return []
    })

    // Table columns
    const columns = [
      { key: 'name', label: 'Name', sortable: true },
      { key: 'email', label: 'Email', sortable: true },
      { key: 'age', label: 'Age', sortable: true },
      { key: 'contact', label: 'Contact', sortable: true },
      { key: 'active', label: 'Status', sortable: true, align: 'center' }
    ]

    // Methods
    const handleSubmit = async () => {
      const result = await adminStore.addPatient(formData.value)
      if (result.success) {
        showAddModal.value = false
        formData.value = { name: '', email: '', password: '', age: '', contact: '' }
        alert('Patient added successfully')
      } else {
        alert(result.error)
      }
    }

    const deletePatient = async (patient) => {
      if (!confirm('Delete this patient?')) return
      await adminStore.deletePatient(patient.id)
    }

    const viewProfile = async (patient) => {
      try {
        const response = await adminAPI.getPatientDetails(patient.id)
        viewingPatient.value = response.data.data
        showViewModal.value = true
      } catch (err) {
        alert('Failed to load profile')
      }
    }

    const toggleFlag = async (patient) => {
      if (!confirm(`Toggle flag for ${patient?.name || 'this patient'}?`)) return
      
      try {
        console.log('Toggling flag for patient:', patient);
        const result = await adminStore.flagPatient(patient.id)
        console.log('Flag patient result:', result);
        
        // If task ID returned, track its status
        const taskId = result?.data?.data?.task_id
        if (taskId) {
          alert('Sending notification email...')
          
          // Poll task status
          const checkStatus = setInterval(async () => {
            try {
              const { taskAPI } = await import('@/services/api')
              const statusResponse = await taskAPI.getStatus(taskId)
              console.log('Task status response:', statusResponse);
              const status = statusResponse.data.data.status
              
              if (status === 'SUCCESS') {
                clearInterval(checkStatus)
                alert('Email notification sent successfully!')
                await adminStore.fetchPatients() // Refresh list
              } else if (status === 'FAILURE') {
                clearInterval(checkStatus)
                alert('Failed to send email notification')
              } else if (status === 'PENDING' || status === 'STARTED') {
                console.log(`Task is still ${status}, continuing to poll...`)
              }
            } catch (err) {
              console.error('Error checking task status:', err)
              clearInterval(checkStatus)
            }
          }, 2000)
          
          // Auto-stop polling after 30 seconds
          setTimeout(() => {
            clearInterval(checkStatus)
          }, 30000)
        }
      } catch (err) {
        console.error('Failed to toggle flag:', err);
        alert('Failed to toggle flag')
      }
    }

    const reactivatePatient = async (patient) => {
      if (!confirm(`Reactivate patient ${patient?.name || 'this patient'}?`)) return
      const result = await adminStore.reactivatePatient(patient.id)
      if (result.success) {
        alert('Patient reactivated successfully')
      } else {
        alert(result.error)
      }
    }

    const exportPatientsCSV = async () => {
      try {
        const response = await adminAPI.exportPatientsEmail();
        // Since this is now an email-based export, we just show a message
        alert('Patients CSV export initiated. You will receive an email with the file shortly.');
      } catch (err) {
        console.error('Export failed:', err);
        alert('Failed to initiate patients export. Please try again.');
      }
    };

    onMounted(() => {
      adminStore.fetchPatients()
    })

    return {
      patients,
      processedPatients,
      loading,
      columns,
      showAddModal,
      showViewModal,
      formData,
      viewingPatient,
      handleSubmit,
      deletePatient,
      viewProfile,
      toggleFlag,
      reactivatePatient,
      exportPatientsCSV
    }
  }
}
</script>

<style scoped>
.admin-patients { animation: fadeInUp 0.4s ease-out; }
.avatar-circle { width: 40px; height: 40px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: 600; }
.avatar-circle-lg { width: 80px; height: 80px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 2rem; font-weight: 600; }
.bg-success-subtle { background-color: #e6f9eb; }
.bg-primary-subtle { background-color: #e5f2ff; }
.bg-secondary-subtle { background-color: #f5f5f7; }
</style>