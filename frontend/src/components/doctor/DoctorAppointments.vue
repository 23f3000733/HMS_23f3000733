<template>
  <div class="doctor-appointments">
    <div class="card h-100 border-0 shadow-sm">
      <div class="card-body p-0">
        <DataTable
          :columns="columns"
          :data="appointments"
          :loading="loading.appointments"
          searchable
          search-placeholder="Search patient name..."
          :per-page="10"
          empty-message="No appointments found"
          :show-download-button="true"
          file-name="appointments.csv"
          @download-requested="exportAppointmentsCSV"
        >
          <!-- Custom Patient Column -->
          <template #column-patient_name="{ row }">
            <div class="d-flex align-items-center">
              <div class="avatar-circle-sm bg-primary-subtle text-primary me-2">
                {{ row.patient_name.charAt(0) }}
              </div>
              <div>
                <div class="fw-medium">
                  {{ row.patient_name }}
                </div>
                <small class="text-muted">{{ row.patient_age }} yrs</small>
              </div>
            </div>
          </template>

          <!-- Custom Date Column -->
          <template #column-date="{ row }">
            <div class="d-flex flex-column">
              <span>{{ formatDate(row.date) }}</span>
              <small class="text-muted">{{ formatTime(row.time) }}</small>
            </div>
          </template>

          <!-- Custom Status Column -->
          <template #column-status="{ value }">
            <span
              class="badge rounded-pill"
              :class="getStatusBadgeClass(value)"
            >
              {{ value }}
            </span>
          </template>

          <!-- Actions Column -->
          <template #actions="{ row }">
            <div class="btn-group btn-group-sm">
              <button 
                v-if="row.status === 'Booked'" 
                class="btn btn-primary"
                title="Complete Appointment"
                @click="openTreatmentModal(row)"
              >
                <i class="bi bi-check-lg" />
              </button>
              <button 
                v-if="row.status === 'Booked'" 
                class="btn btn-outline-secondary"
                title="Reschedule"
                @click="openRescheduleModal(row)"
              >
                <i class="bi bi-calendar2-event" />
              </button>
              <button 
                v-if="row.status === 'Booked'" 
                class="btn btn-outline-danger"
                title="Cancel"
                :disabled="processingId === row.id"
                @click="cancelAppointment(row.id)"
              >
                <span v-if="processingId === row.id" class="spinner-border spinner-border-sm" role="status"></span>
                <i v-else class="bi bi-x-lg" />
              </button>
              <button 
                v-if="row.status === 'Completed'" 
                class="btn btn-outline-info"
                title="View History"
                @click="viewHistory(row.patient_id)"
              >
                <i class="bi bi-clock-history" />
              </button>
            </div>
          </template>
        </DataTable>
      </div>
    </div>

    <!-- Treatment Modal -->
    <Modal
      v-model="showTreatmentModal"
      title="Complete Appointment"
      size="large"
      confirm-text="Complete Appointment"
      @confirm="submitTreatment"
    >
      <div v-if="selectedAppt">
        <div class="d-flex align-items-center mb-4 p-3 bg-light rounded">
          <div class="avatar-circle bg-primary text-white me-3">
            {{ selectedAppt.patient_name.charAt(0) }}
          </div>
          <div>
            <h6 class="mb-0">
              {{ selectedAppt.patient_name }}
            </h6>
            <small class="text-muted">
              {{ formatDate(selectedAppt.date) }} at {{ formatTime(selectedAppt.time) }}
            </small>
          </div>
        </div>

        <div class="mb-3">
          <label class="form-label small text-muted text-uppercase fw-bold">Diagnosis</label>
          <textarea 
            v-model="treatment.diagnosis" 
            :class="['form-control', { 'is-invalid': formErrors.diagnosis }]" 
            rows="3" 
            placeholder="Enter diagnosis..."
            required
            @input="formErrors.diagnosis = false"
          />
          <div class="invalid-feedback">Diagnosis is required</div>
        </div>

        <div class="mb-3">
          <label class="form-label small text-muted text-uppercase fw-bold">Prescription</label>
          <textarea 
            v-model="treatment.prescription" 
            :class="['form-control', 'font-monospace', 'bg-light', { 'is-invalid': formErrors.prescription }]" 
            rows="4" 
            placeholder="Rx..."
            required
            @input="formErrors.prescription = false"
          />
          <div class="invalid-feedback">Prescription is required</div>
        </div>

        <div class="mb-3">
          <label class="form-label small text-muted text-uppercase fw-bold">Notes</label>
          <textarea 
            v-model="treatment.notes" 
            class="form-control" 
            rows="2"
            placeholder="Internal notes..."
          />
        </div>
      </div>
    </Modal>

    <!-- Reschedule Modal -->
    <Modal
      v-model="showRescheduleModal"
      title="Reschedule Appointment"
      confirm-text="Confirm Reschedule"
      @confirm="submitReschedule"
    >
      <div v-if="rescheduleAppt">
        <div class="alert alert-light border mb-3">
          <small class="text-muted d-block">Current Schedule</small>
          <strong>{{ formatDate(rescheduleAppt.date) }}</strong> at <strong>{{ formatTime(rescheduleAppt.time) }}</strong>
        </div>
        <div class="row g-3">
          <div class="col-md-6">
            <label class="form-label">New Date</label>
            <input 
              v-model="rescheduleData.date" 
              type="date" 
              class="form-control"
              :min="getTodayDate()"
              required
            >
          </div>
          <div class="col-md-6">
            <label class="form-label">New Time</label>
            <input 
              v-model="rescheduleData.time" 
              type="time" 
              class="form-control"
              required
            >
          </div>
          <div class="col-12">
            <label class="form-label">Reason</label>
            <textarea 
              v-model="rescheduleData.reason" 
              class="form-control" 
              rows="2"
              placeholder="Reason for rescheduling..."
            />
          </div>
        </div>
      </div>
    </Modal>

    <!-- History Modal -->
    <Modal
      v-model="showHistoryModal"
      :title="patientInfo ? `${patientInfo.name}'s History` : 'Patient History'"
      size="large"
      :show-default-footer="false"
    >
      <div v-if="patientInfo" class="alert alert-light border mb-3">
        <div class="row">
          <div class="col-md-4">
            <small class="text-muted d-block">Patient Name</small>
            <strong>{{ patientInfo.name }}</strong>
          </div>
          <div class="col-md-4">
            <small class="text-muted d-block">Age</small>
            <strong>{{ patientInfo.age }} years</strong>
          </div>
          <div class="col-md-4">
            <small class="text-muted d-block">Contact</small>
            <strong>{{ patientInfo.contact }}</strong>
          </div>
        </div>
      </div>

      <div class="table-responsive">
        <table class="table table-hover mb-0 align-middle">
          <thead class="bg-light">
            <tr>
              <th class="ps-4">Date</th>
              <th>Diagnosis</th>
              <th>Prescription</th>
            </tr>
          </thead>
          <tbody>
            <tr v-if="loadingHistory">
              <td colspan="3" class="text-center py-4">
                <div class="spinner-border spinner-border-sm text-primary" role="status">
                  <span class="visually-hidden">Loading...</span>
                </div>
                <span class="ms-2 text-muted">Loading history...</span>
              </td>
            </tr>
            <tr v-else-if="patientHistory.length === 0">
              <td colspan="3" class="text-center text-muted py-4">
                <i class="bi bi-inbox fs-3 d-block mb-2"></i>
                No history available
              </td>
            </tr>
            <tr v-else v-for="(record, index) in patientHistory" :key="index">
              <td class="ps-4 text-nowrap">
                {{ formatDate(record.date) }}
              </td>
              <td>{{ record.diagnosis || 'N/A' }}</td>
              <td class="font-monospace small">
                {{ record.prescription || 'N/A' }}
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </Modal>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import { useDoctorStore } from '@/stores/doctor'
import { storeToRefs } from 'pinia'
import { doctorAPI } from '@/services/api'
import { useToast } from '@/composables/useToast'
import DataTable from '@/components/shared/DataTable.vue'
import Modal from '@/components/shared/Modal.vue'

export default {
  name: 'DoctorAppointments',
  components: {
    DataTable,
    Modal
  },
  setup() {
    const doctorStore = useDoctorStore()
    const { appointments, loading } = storeToRefs(doctorStore)
    const toast = useToast()

    // Modal states
    const showTreatmentModal = ref(false)
    const showRescheduleModal = ref(false)
    const showHistoryModal = ref(false)

    // Data states
    const selectedAppt = ref(null)
    const treatment = ref({ diagnosis: '', prescription: '', notes: '' })
    const rescheduleAppt = ref(null)
    const rescheduleData = ref({ date: '', time: '', reason: '' })
    const patientHistory = ref([])
    const patientInfo = ref(null)
    const loadingHistory = ref(false)
    const formErrors = ref({ diagnosis: false, prescription: false })
    const processingId = ref(null)

    // Table columns
    const columns = [
      { key: 'patient_name', label: 'Patient', sortable: true },
      { key: 'patient_contact', label: 'Contact', sortable: true },
      { key: 'date', label: 'Date & Time', sortable: true },
      { key: 'status', label: 'Status', sortable: true }
    ]

    onMounted(() => {
      doctorStore.fetchAppointments()
    })

    // Treatment Methods
    const openTreatmentModal = (appt) => {
      selectedAppt.value = appt
      treatment.value = { diagnosis: '', prescription: '', notes: '' }
      showTreatmentModal.value = true
    }

    const submitTreatment = async () => {
      formErrors.value = {
        diagnosis: !treatment.value.diagnosis,
        prescription: !treatment.value.prescription
      }
      if (!treatment.value.diagnosis || !treatment.value.prescription) {
        toast.showWarning('Please fill in diagnosis and prescription')
        return
      }
      const result = await doctorStore.completeAppointment(selectedAppt.value.id, treatment.value)
      if (result.success) {
        toast.showSuccess('Treatment saved successfully!')
        showTreatmentModal.value = false
        selectedAppt.value = null
      } else {
        toast.showError(result.error)
      }
    }

    // Reschedule Methods
    const openRescheduleModal = (appt) => {
      rescheduleAppt.value = appt
      rescheduleData.value = { 
        date: appt.date, 
        time: appt.time.substring(0, 5), 
        reason: '' 
      }
      showRescheduleModal.value = true
    }

    const submitReschedule = async () => {
      if (!rescheduleData.value.date || !rescheduleData.value.time) {
        toast.showWarning('Please select both date and time')
        return
      }
      try {
        await doctorAPI.rescheduleAppointment(rescheduleAppt.value.id, rescheduleData.value)
        toast.showSuccess('Appointment rescheduled successfully!')
        showRescheduleModal.value = false
        doctorStore.fetchAppointments()
      } catch (err) {
        toast.showError(err.response?.data?.message || 'Failed to reschedule appointment')
      }
    }

    // Other Methods
    const cancelAppointment = async (id) => {
      if (confirm('Are you sure you want to cancel this appointment?')) {
        processingId.value = id
        const result = await doctorStore.cancelAppointment(id)
        processingId.value = null
        if (result.success) {
          toast.showSuccess('Appointment cancelled')
        } else {
          toast.showError(result.error)
        }
      }
    }

    const viewHistory = async (patientId) => {
      loadingHistory.value = true
      try {
        const response = await doctorAPI.getPatientHistory(patientId)
        if (response.data.success) {
            const historyData = response.data.data
            patientHistory.value = historyData.appointments
            patientInfo.value = historyData.patient
            showHistoryModal.value = true
        } else {
             toast.showError('Failed to load patient history')
        }
      } catch (err) {
        console.error('Failed to load patient history:', err)
        toast.showError('Failed to load patient history')
      } finally {
        loadingHistory.value = false
      }
    }

    // Helpers
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

    const getTodayDate = () => {
      return new Date().toISOString().split('T')[0]
    }

    const getStatusBadgeClass = (status) => {
      const classes = {
        'Booked': 'bg-primary-subtle text-primary',
        'Completed': 'bg-success-subtle text-success',
        'Cancelled': 'bg-danger-subtle text-danger'
      }
      return classes[status] || 'bg-secondary-subtle text-secondary'
    }

    const exportAppointmentsCSV = async () => {
      try {
        console.log('=== Initiating appointment export ===');
        console.log('Calling doctorAPI.exportAppointmentsEmail()');
        const response = await doctorAPI.exportAppointmentsEmail();
        console.log('Export response received:', response);
        // Since this is now an email-based export, we just show a message
        toast.showSuccess('Appointments CSV export initiated. You will receive an email shortly.');
      } catch (err) {
        console.error('!!! Export failed:', err);
        console.error('Error details:', {
          message: err.message,
          status: err.response?.status,
          statusText: err.response?.statusText,
          data: err.response?.data
        });
        toast.showError('Failed to initiate appointments export. Please try again.');
      }
    };

    return {
      appointments,
      loading,
      columns,
      showTreatmentModal,
      showRescheduleModal,
      showHistoryModal,
      selectedAppt,
      treatment,
      rescheduleAppt,
      rescheduleData,
      patientHistory,
      patientInfo,
      loadingHistory,
      formErrors,
      processingId,
      openTreatmentModal,
      submitTreatment,
      openRescheduleModal,
      submitReschedule,
      cancelAppointment,
      viewHistory,
      formatDate,
      formatTime,
      getTodayDate,
      getStatusBadgeClass,
      exportAppointmentsCSV
    }
  }
}
</script>

<style scoped>
.doctor-appointments {
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
  width: 48px;
  height: 48px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  font-size: 1.25rem;
}

.bg-primary-subtle { background-color: #e5f2ff; }
.bg-success-subtle { background-color: #e6f9eb; }
.bg-danger-subtle { background-color: #ffeef0; }
.bg-secondary-subtle { background-color: #f5f5f7; }
</style>