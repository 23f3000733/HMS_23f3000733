<template>
  <div class="patient-appointments">
    <div class="card border-0 shadow-sm h-100">
      <div class="card-header bg-white border-bottom py-3 d-flex justify-content-between align-items-center">
        <h5 class="mb-0 fw-semibold">
          <i class="bi bi-calendar-check me-2 text-primary" />My Appointments
        </h5>
        <div class="d-flex gap-2">
          <div
            class="btn-group"
            role="group"
          >
            <button 
              type="button" 
              class="btn btn-sm" 
              :class="viewMode === 'list' ? 'btn-primary' : 'btn-outline-primary'"
              @click="viewMode = 'list'"
            >
              <i class="bi bi-list-ul" />
            </button>
            <button 
              type="button" 
              class="btn btn-sm" 
              :class="viewMode === 'calendar' ? 'btn-primary' : 'btn-outline-primary'"
              @click="viewMode = 'calendar'"
            >
              <i class="bi bi-calendar3" />
            </button>
          </div>
          <button
            class="btn btn-sm btn-outline-success"
            @click="exportHistory"
          >
            <i class="bi bi-download" />
          </button>
        </div>
      </div>
      
      <div
        v-if="viewMode === 'list'"
        class="card-body p-0"
      >
        <DataTable
          :columns="columns"
          :data="appointments"
          :loading="loading.history"
          searchable
          search-placeholder="Search doctor..."
          :per-page="10"
          empty-message="No appointments found"
          show-download-button
          file-name="my-appointments.csv"
        >
          <!-- Custom Doctor Column -->
          <template #column-doctor_name="{ value }">
            <span class="fw-medium">Dr. {{ value }}</span>
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
              :class="{
                'bg-primary-subtle text-primary': value === 'Booked',
                'bg-success-subtle text-success': value === 'Completed',
                'bg-secondary-subtle text-secondary': value === 'Cancelled'
              }"
            >
              {{ value }}
            </span>
          </template>

          <!-- Custom Prescription Column -->
          <template #column-prescription="{ value }">
            <span
              v-if="value"
              class="badge bg-light text-dark border"
            >
              <i class="bi bi-file-text me-1" />Available
            </span>
            <span
              v-else
              class="text-muted small"
            >-</span>
          </template>


          <!-- Actions Column -->
          <template #actions="{ row }">
            <div class="btn-group btn-group-sm">
              <button
                class="btn btn-outline-primary"
                @click="viewDetails(row)"
              >
                <i class="bi bi-eye" />
              </button>
              <button 
                v-if="row?.status === 'Booked'" 
                class="btn btn-outline-secondary" 
                title="Reschedule"
                @click="openReschedule(row)"
              >
                <i class="bi bi-calendar-range" />
              </button>
              <button 
                v-if="row?.status === 'Booked'" 
                class="btn btn-outline-danger" 
                title="Cancel"
                @click="cancelAppointment(row?.id)"
              >
                <i class="bi bi-x-lg" />
              </button>
            </div>
          </template>
        </DataTable>
      </div>

      <!-- Calendar View -->
      <div
        v-if="viewMode === 'calendar'"
        class="card-body"
      >
        <PatientCalendar @reschedule="openReschedule" />
      </div>
    </div>

    <!-- Reschedule Modal -->
    <Modal
      v-model="showRescheduleModal"
      title="Reschedule Appointment"
      confirm-text="Confirm Reschedule"
      @confirm="confirmReschedule"
    >
      <p
        v-if="reschedulingAppt"
        class="text-muted mb-4"
      >
        Current: {{ formatDate(reschedulingAppt.date) }} at {{ formatTime(reschedulingAppt.time) }}
      </p>
      <div class="mb-3">
        <label class="form-label small text-muted text-uppercase fw-bold">New Date</label>
        <input
          v-model="rescheduleForm.date"
          type="date"
          class="form-control"
          required
          :min="new Date().toISOString().split('T')[0]"
        >
      </div>
      <div class="mb-4">
        <label class="form-label small text-muted text-uppercase fw-bold">New Time</label>
        <input
          v-model="rescheduleForm.time"
          type="time"
          class="form-control"
          required
        >
      </div>
    </Modal>

    <!-- Details Modal -->
    <Modal
      v-model="showDetailsModal"
      title="Appointment Details"
      :show-default-footer="false"
    >
      <div v-if="viewingAppt">
        <div class="text-center mb-4">
          <div class="avatar-circle bg-primary-subtle text-primary mx-auto mb-2">
            {{ viewingAppt?.doctor_name?.charAt(0) || '?' }}
          </div>
          <h5 class="fw-bold mb-0">
            Dr. {{ viewingAppt.doctor_name }}
          </h5>
          <span
            class="badge rounded-pill mt-2"
            :class="{
              'bg-primary-subtle text-primary': viewingAppt.status === 'Booked',
              'bg-success-subtle text-success': viewingAppt.status === 'Completed',
              'bg-secondary-subtle text-secondary': viewingAppt.status === 'Cancelled'
            }"
          >
            {{ viewingAppt.status }}
          </span>
        </div>

        <div class="row g-3 mb-4">
          <div class="col-6">
            <div class="p-2 bg-light rounded text-center">
              <small class="text-muted d-block">Date</small>
              <span class="fw-medium">{{ formatDate(viewingAppt.date) }}</span>
            </div>
          </div>
          <div class="col-6">
            <div class="p-2 bg-light rounded text-center">
              <small class="text-muted d-block">Time</small>
              <span class="fw-medium">{{ formatTime(viewingAppt.time) }}</span>
            </div>
          </div>
        </div>

        <div
          v-if="viewingAppt.diagnosis"
          class="mb-3"
        >
          <small class="text-muted text-uppercase fw-bold">Diagnosis</small>
          <p class="mb-0">
            {{ viewingAppt.diagnosis }}
          </p>
        </div>
        
        <div
          v-if="viewingAppt.prescription"
          class="mb-3"
        >
          <small class="text-muted text-uppercase fw-bold">Prescription</small>
          <div class="bg-light p-3 rounded border font-monospace mt-1">
            {{ viewingAppt.prescription }}
          </div>
        </div>

        <div
          v-if="!viewingAppt.diagnosis && !viewingAppt.prescription"
          class="text-center text-muted py-3 border rounded border-dashed"
        >
          <small>No medical records available yet.</small>
        </div>
      </div>
    </Modal>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import { usePatientStore } from '@/stores/patient'
import { storeToRefs } from 'pinia'
import { patientAPI } from '@/services/api'
import { useToast } from '@/composables/useToast'
import DataTable from '@/components/shared/DataTable.vue'
import Modal from '@/components/shared/Modal.vue'
import PatientCalendar from './PatientCalendar.vue'

export default {
  name: 'PatientAppointments',
  components: { DataTable, Modal, PatientCalendar },
  emits: ['navigate'],
  setup() {
    const patientStore = usePatientStore()
    const { history, loading } = storeToRefs(patientStore)
    const toast = useToast()

    const viewMode = ref('list')
    const showRescheduleModal = ref(false)
    const showDetailsModal = ref(false)
    const reschedulingAppt = ref(null)
    const rescheduleForm = ref({ date: '', time: '' })
    const viewingAppt = ref(null)

    const columns = [
      { key: 'doctor_name', label: 'Doctor', sortable: true },
      { key: 'date', label: 'Date & Time', sortable: true },
      { key: 'status', label: 'Status', sortable: true },
      { key: 'prescription', label: 'Prescription', sortable: false }
    ]

    onMounted(() => {
      patientStore.fetchHistory()
    })

    const cancelAppointment = async (id) => {
      if (!confirm('Cancel this appointment?')) return
      const result = await patientStore.cancelAppointment(id)
      if (result.success) {
        toast.showSuccess('Appointment cancelled')
      } else {
        toast.showError(result.error || 'Failed to cancel')
      }
    }

const exportHistory = async () => {
      try {
        console.log('Initiating patient history export');
        const response = await patientAPI.exportHistory()
        console.log('Export history response:', response);
        
        // If task ID returned, track its status
        const taskId = response?.data?.data?.task_id
        if (taskId) {
          toast.showInfo('Generating export. You will receive an email when ready...')
          
          // Poll task status
          const checkStatus = setInterval(async () => {
            try {
              const { taskAPI } = await import('@/services/api')
              const statusResponse = await taskAPI.getStatus(taskId)
              console.log('Task status response:', statusResponse);
              const status = statusResponse.data.data.status
              
              if (status === 'SUCCESS') {
                clearInterval(checkStatus)
                toast.showSuccess('Export complete! Check your email.')
                // Refresh data to show any updates
                await patientStore.fetchHistory()
              } else if (status === 'FAILURE') {
                clearInterval(checkStatus)
                toast.showError('Export failed')
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
        } else {
          toast.showInfo('Export initiated')
        }
      } catch (err) {
        console.error('Failed to export history:', err);
        toast.showError('Failed to export history')
      }
    }

    const openReschedule = (appt) => {
      reschedulingAppt.value = appt
      rescheduleForm.value = { date: '', time: '' }
      showRescheduleModal.value = true
    }

    const confirmReschedule = async () => {
      if (!rescheduleForm.value.date || !rescheduleForm.value.time) {
        toast.showWarning('Select date and time')
        return
      }
      try {
        await patientAPI.rescheduleAppointment(reschedulingAppt.value.id, rescheduleForm.value)
        toast.showSuccess('Rescheduled successfully')
        showRescheduleModal.value = false
        patientStore.fetchHistory()
      } catch (err) {
        toast.showError(err.response?.data?.message || 'Failed')
      }
    }

    const viewDetails = (appt) => {
      viewingAppt.value = appt
      showDetailsModal.value = true
    }

    const formatDate = (date) => {
      return new Date(date).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })
    }

    const formatTime = (time) => {
      return time.substring(0, 5)
    }

    return {
      appointments: history, // Use history instead of appointments
      loading,
      viewMode,
      columns,
      showRescheduleModal,
      showDetailsModal,
      reschedulingAppt,
      rescheduleForm,
      viewingAppt,
      cancelAppointment,
      exportHistory,
      openReschedule,
      confirmReschedule,
      viewDetails,
      formatDate,
      formatTime
    }
  }
}
</script>

<style scoped>
.patient-appointments { animation: fadeInUp 0.4s ease-out; }
.avatar-circle { width: 48px; height: 48px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: 600; font-size: 1.2rem; }
.bg-primary-subtle { background-color: #e5f2ff; }
.bg-success-subtle { background-color: #e6f9eb; }
.bg-secondary-subtle { background-color: #f5f5f7; }
</style>
