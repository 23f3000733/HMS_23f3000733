<template>
  <div class="admin-doctors">
    <!-- Header & Actions -->
    <div class="d-flex justify-content-between align-items-center mb-4">
      <h5 class="mb-0 fw-bold text-dark">
        Doctors Management
      </h5>
      <button
        class="btn btn-primary shadow-sm"
        @click="showAddModal = true"
      >
        <i class="bi bi-plus-lg me-2" />Add Doctor
      </button>
    </div>

    <!-- Doctors Table -->
    <div class="card border-0 shadow-sm">
      <div class="card-body p-0">
        <DataTable
          :columns="columns"
          :data="doctors"
          :loading="loading.doctors"
          searchable
          search-placeholder="Search by name or specialization..."
          :per-page="10"
          empty-message="No doctors found"
          show-download-button
          file-name="all-doctors.csv"
          @download-requested="exportDoctorsCSV"
        >
          <!-- Custom Name Column -->
          <template #column-name="{ row }">
            <div class="d-flex align-items-center">
              <div class="avatar-circle bg-primary-subtle text-primary me-3">
                {{ row.name.charAt(0) }}
              </div>
              <div>
                <div class="fw-medium">
                  {{ row.name }}
                </div>
                <small class="text-muted">{{ row.experience }} years exp.</small>
              </div>
            </div>
          </template>

          <!-- Custom Status Column -->
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
                class="btn btn-outline-secondary"
                title="View"
                @click="viewDoctor(row)"
              >
                <i class="bi bi-eye" />
              </button>
              <button
                class="btn btn-outline-primary"
                title="Edit"
                @click="editDoctor(row)"
              >
                <i class="bi bi-pencil" />
              </button>
               <button 
                class="btn" 
                :class="row?.flagged ? 'btn-outline-success' : 'btn-outline-warning'"
                :title="row?.flagged ? 'Unflag' : 'Flag'"
                @click="toggleFlag(row)"
              >
                <i :class="row?.flagged ? 'bi bi-flag-fill' : 'bi bi-flag'" />
              </button>
              <button
                v-if="!row?.active"
                class="btn btn-outline-success"
                title="Reactivate"
                @click="reactivateDoctor(row)"
              >
                <i class="bi bi-arrow-repeat" />
              </button>
              <button
                class="btn btn-outline-danger"
                title="Delete"
                @click="deleteDoctor(row)"
              >
                <i class="bi bi-trash" />
              </button>
            </div>
          </template>
        </DataTable>
      </div>
    </div>

    <!-- Add/Edit Modal -->
    <Modal
      v-model="showFormModal"
      :title="isEditing ? 'Edit Doctor' : 'New Doctor Registration'"
      :confirm-text="isEditing ? 'Save Changes' : 'Create Account'"
      @confirm="handleSubmit"
    >
      <form
        id="doctorForm"
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
              :disabled="isEditing"
            >
          </div>
          <div
            v-if="!isEditing"
            class="col-md-6"
          >
            <label class="form-label small text-muted text-uppercase fw-bold">Password</label>
            <input
              v-model="formData.password"
              type="password"
              class="form-control"
              required
            >
          </div>
          <div class="col-md-6">
            <label class="form-label small text-muted text-uppercase fw-bold">Specialization</label>
            <input
              v-model="formData.specialization"
              type="text"
              class="form-control"
              required
            >
          </div>
          <div class="col-md-6">
            <label class="form-label small text-muted text-uppercase fw-bold">Experience (Years)</label>
            <input
              v-model="formData.experience"
              type="number"
              class="form-control"
              required
            >
          </div>
        </div>
      </form>
    </Modal>

    <!-- View Details Modal -->
    <Modal
      v-model="showViewModal"
      title="Doctor Profile"
      size="large"
      :show-default-footer="false"
    >
      <div
        v-if="viewingDoctor"
        class="row g-4"
      >
        <!-- Info Column -->
        <div class="col-lg-4">
          <div class="text-center mb-4">
            <div class="avatar-circle-lg bg-primary-subtle text-primary mx-auto mb-3">
              {{ viewingDoctor.doctor.name.charAt(0) }}
            </div>
            <h4 class="fw-bold mb-1">
              {{ viewingDoctor.doctor.name }}
            </h4>
            <p class="text-muted">
              {{ viewingDoctor.doctor.specialization }}
            </p>
          </div>
          
          <div class="card bg-light border-0 mb-3">
            <div class="card-body">
              <div class="d-flex justify-content-between mb-2">
                <span class="text-muted">Status</span>
                <span class="badge bg-success-subtle text-success">Active</span>
              </div>
              <div class="d-flex justify-content-between mb-2">
                <span class="text-muted">Email</span>
                <span
                  class="fw-medium text-truncate"
                  style="max-width: 150px;"
                >{{ viewingDoctor.doctor.email }}</span>
              </div>
              <div class="d-flex justify-content-between">
                <span class="text-muted">Experience</span>
                <span class="fw-medium">{{ viewingDoctor.doctor.experience }} Years</span>
              </div>
            </div>
          </div>

          <div class="row g-2 text-center">
            <div class="col-4">
              <div class="p-2 bg-primary-subtle rounded">
                <div class="h5 mb-0 text-primary fw-bold">
                  {{ viewingDoctor.total_appointments }}
                </div>
                <small
                  class="text-muted"
                  style="font-size: 0.7rem;"
                >Total</small>
              </div>
            </div>
            <div class="col-4">
              <div class="p-2 bg-success-subtle rounded">
                <div class="h5 mb-0 text-success fw-bold">
                  {{ viewingDoctor.completed_count }}
                </div>
                <small
                  class="text-muted"
                  style="font-size: 0.7rem;"
                >Done</small>
              </div>
            </div>
            <div class="col-4">
              <div class="p-2 bg-warning-subtle rounded">
                <div class="h5 mb-0 text-warning fw-bold">
                  {{ viewingDoctor.upcoming_count }}
                </div>
                <small
                  class="text-muted"
                  style="font-size: 0.7rem;"
                >Next</small>
              </div>
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
                v-if="viewingDoctor.activity_logs.length > 0"
                class="list-group list-group-flush"
              >
                <div
                  v-for="log in viewingDoctor.activity_logs"
                  :key="log.id"
                  class="list-group-item"
                >
                  <div class="d-flex justify-content-between">
                    <div>
                      <span class="badge bg-light text-dark border me-2">{{ log.activity_type }}</span>
                      <span>{{ log.description }}</span>
                    </div>
                    <small class="text-muted">{{ new Date(log.timestamp).toLocaleDateString() }}</small>
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
            Upcoming Appointments
          </h6>
          <div class="card border-0 shadow-sm">
            <div class="card-body p-0">
              <div
                v-if="viewingDoctor.upcoming_appointments.length > 0"
                class="table-responsive"
              >
                <table class="table table-hover mb-0">
                  <thead class="bg-light">
                    <tr><th>Patient</th><th>Date</th><th>Status</th></tr>
                  </thead>
                  <tbody>
                    <tr
                      v-for="appt in viewingDoctor.upcoming_appointments"
                      :key="appt.id"
                    >
                      <td>{{ appt.patient_name }}</td>
                      <td>{{ appt.date }} {{ appt.time }}</td>
                      <td><span class="badge bg-warning-subtle text-warning">{{ appt.status }}</span></td>
                    </tr>
                  </tbody>
                </table>
              </div>
              <div
                v-else
                class="text-center py-3 text-muted"
              >
                No upcoming appointments
              </div>
            </div>
          </div>
        </div>
      </div>
    </Modal>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import { useAdminStore } from '@/stores/admin'
import { storeToRefs } from 'pinia'
import { adminAPI } from '@/services/api'
import DataTable from '@/components/shared/DataTable.vue'
import Modal from '@/components/shared/Modal.vue'

export default {
  name: 'AdminDoctors',
  components: {
    DataTable,
    Modal
  },
  setup() {
    const adminStore = useAdminStore()
    const { doctors, loading } = storeToRefs(adminStore)
    
    // Modal states
    const showAddModal = ref(false)
    const showEditModal = ref(false)
    const showViewModal = ref(false)
    
    // Form data
    const formData = ref({
      name: '',
      email: '',
      password: '',
      specialization: '',
      experience: null

    })
    
    const viewingDoctor = ref(null)
    const editingId = ref(null)

    // Table columns
    const columns = [
      { key: 'name', label: 'Name', sortable: true },
      { key: 'email', label: 'Email', sortable: true },
      { key: 'specialization', label: 'Specialization', sortable: true },
      { key: 'active', label: 'Status', sortable: true, align: 'center' }
    ]

    // Computed
    const showFormModal = computed({
      get: () => showAddModal.value || showEditModal.value,
      set: (val) => {
        if (!val) {
          showAddModal.value = false
          showEditModal.value = false
          resetForm()
        }
      }
    })

    const isEditing = computed(() => showEditModal.value)

    // Methods
    const resetForm = () => {
      formData.value = {
        name: '',
        email: '',
        password: '',
        specialization: '',
        experience: ''
      }
      editingId.value = null
    }

    const handleSubmit = async () => {
      const submitData = {
        ...formData.value,
        experience: formData.value.experience ? parseInt(formData.value.experience): 0
      }

      let result
      if (isEditing.value) {
        result = await adminStore.updateDoctor(editingId.value, formData.value)
      } else {
        result = await adminStore.addDoctor(formData.value)
      }

      if (result.success) {
        showFormModal.value = false
        alert(isEditing.value ? 'Doctor updated successfully' : 'Doctor added successfully')
      } else {
        alert(result.error)
      }
    }
    const addDoctor = () => {
      // Reset Form for adding new doctor
      resetForm()
      showAddModal.value = true
    }
    const editDoctor = (doctor) => {
      editingId.value = doctor.id
      formData.value = {
        name: doctor.name || '',
        specialization: doctor.specialization || '',
        experience: doctor.experience || ''
      }
      showEditModal.value = true
    }

    const viewDoctor = async (doctor) => {
      try {
        const response = await adminAPI.getDoctorDetails(doctor.id)
        viewingDoctor.value = response.data.data
        showViewModal.value = true
      } catch (err) {
        alert('Failed to load details')
      }
    }

    const toggleFlag = async (doctor) => {
      if (!confirm(`Toggle flag for ${doctor.name}?`)) return
      
      try {
        console.log('Toggling flag for doctor:', doctor);
        const result = await adminStore.flagDoctor(doctor.id)
        console.log('Flag doctor result:', result);
        
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
                await adminStore.fetchDoctors() // Refresh list
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
          }, 2000) // Poll every 2 seconds
          
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

    const reactivateDoctor = async (doctor) => {
      if (!confirm(`Reactivate doctor ${doctor.name}?`)) return
      const result = await adminStore.reactivateDoctor(doctor.id)
      if (result.success) {
        alert('Doctor reactivated successfully')
      } else {
        alert(result.error)
      }
    }

    const deleteDoctor = async (doctor) => {
      if (!confirm('Delete this doctor?')) return
      await adminStore.deleteDoctor(doctor.id)
    }

    const exportDoctorsCSV = async () => {
      try {
        const response = await adminAPI.exportDoctorsEmail();
        // Since this is now an email-based export, we just show a message
        alert('Doctors CSV export initiated. You will receive an email with the file shortly.');
      } catch (err) {
        console.error('Export failed:', err);
        alert('Failed to initiate doctors export. Please try again.');
      }
    };

    onMounted(() => {
      adminStore.fetchDoctors()
    })

    return {
      doctors,
      loading,
      columns,
      showAddModal,
      showEditModal,
      showViewModal,
      showFormModal,
      isEditing,
      formData,
      viewingDoctor,
      handleSubmit,
      editDoctor,
      viewDoctor,
      toggleFlag,
      reactivateDoctor,
      deleteDoctor,
      exportDoctorsCSV
    }
  }
}
</script>

<style scoped>
.admin-doctors { animation: fadeInUp 0.4s ease-out; }
.avatar-circle { width: 40px; height: 40px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: 600; }
.avatar-circle-lg { width: 80px; height: 80px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 2rem; font-weight: 600; }
.bg-primary-subtle { background-color: #e5f2ff; }
.bg-success-subtle { background-color: #e6f9eb; }
.bg-warning-subtle { background-color: #fff3cd; }
.bg-danger-subtle { background-color: #ffe6e6; }
.bg-secondary-subtle { background-color: #f5f5f7; }
</style>
