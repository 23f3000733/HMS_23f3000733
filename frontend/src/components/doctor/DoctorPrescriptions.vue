<template>
  <div class="doctor-prescriptions">
    <div class="card h-100 border-0 shadow-sm">
      <div class="card-body p-0">
        <DataTable
          :columns="columns"
          :data="prescriptions"
          :loading="loading.prescriptions"
          searchable
          search-placeholder="Search patient, diagnosis..."
          :per-page="10"
          empty-message="No prescriptions found"
          :show-download-button="true"
          file-name="prescriptions.csv"
          @download-requested="exportPrescriptionsCSV"
        >
          <!-- Custom Date Column -->
          <template #column-date="{ value }">
            {{ formatDate(value) }}
          </template>

          <!-- Custom Patient Column -->
          <template #column-patient_name="{ value }">
            <span class="fw-medium">{{ value }}</span>
          </template>

          <!-- Custom Diagnosis Column -->
          <template #column-diagnosis="{ value }">
            <span
              class="text-truncate d-inline-block"
              style="max-width: 150px;"
            >{{ value }}</span>
          </template>

          <!-- Custom Prescription Column -->
          <template #column-prescription="{ value }">
            <span
              class="text-truncate d-inline-block"
              style="max-width: 150px;"
            >{{ value }}</span>
          </template>

          <!-- Custom Email Status Column -->
          <template #column-email_sent="{ value }">
            <span
              v-if="value"
              class="badge bg-success-subtle text-success rounded-pill"
            >
              <i class="bi bi-check-circle-fill me-1" />Sent
            </span>
            <span
              v-else
              class="badge bg-secondary-subtle text-secondary rounded-pill"
            >
              Not Sent
            </span>
          </template>

          <!-- Custom Resend Count Column -->
          <template #column-resend_count="{ value }">
            <span v-if="value && value > 0" class="badge bg-warning-subtle text-warning rounded-pill">
              {{ value }} time{{ value > 1 ? 's' : '' }}
            </span>
            <span v-else class="badge bg-light-subtle text-muted rounded-pill">
              0
            </span>
          </template>

          <!-- Actions Column -->
          <template #actions="{ row }">
            <div class="btn-group btn-group-sm">
              <button
                class="btn btn-outline-primary"
                title="View"
                @click="viewDetails(row)"
              >
                <i class="bi bi-eye" />
              </button>
              <button 
                class="btn btn-outline-secondary" 
                :disabled="sendingEmail === row.id"
                :title="row.email_sent ? 'Resend Email' : 'Send Email'"
                @click="sendEmail(row)"
              >
                <i
                  class="bi"
                  :class="row.email_sent ? 'bi-arrow-repeat' : 'bi-envelope'"
                />
              </button>
            </div>
          </template>
        </DataTable>
      </div>
    </div>

    <!-- Details Modal -->
    <Modal
      v-model="showDetailsModal"
      title="Prescription Details"
      size="large"
      :show-default-footer="false"
    >
      <div v-if="selectedPrescription">
        <div class="card border-0 shadow-sm mb-3">
          <div class="card-body">
            <div class="d-flex justify-content-between align-items-start mb-3">
              <div>
                <h5 class="fw-bold mb-0">
                  {{ selectedPrescription.patient_name }}
                </h5>
                <p class="text-muted small mb-0">
                  {{ selectedPrescription.patient_age }} years • {{ selectedPrescription.patient_contact }}
                </p>
              </div>
              <div class="text-end">
                <span class="badge bg-light text-dark border">{{ formatDate(selectedPrescription.date) }}</span>
              </div>
            </div>
            <hr class="my-2">
            <div class="mb-3">
              <small class="text-muted text-uppercase fw-bold">Diagnosis</small>
              <p class="fw-medium mb-0">
                {{ selectedPrescription.diagnosis }}
              </p>
            </div>
            <div class="mb-3">
              <small class="text-muted text-uppercase fw-bold">Prescription</small>
              <div class="bg-light p-3 rounded border font-monospace mt-1">
                {{ selectedPrescription.prescription }}
              </div>
            </div>
            <div v-if="selectedPrescription.notes">
              <small class="text-muted text-uppercase fw-bold">Notes</small>
              <p class="mb-0 text-muted">
                {{ selectedPrescription.notes }}
              </p>
            </div>
          </div>
        </div>
        <div class="d-flex justify-content-between">
          <button
            type="button"
            class="btn btn-outline-secondary"
            @click="printPrescription"
          >
            <i class="bi bi-printer me-1" /> Print
          </button>
          <button
            type="button"
            class="btn btn-primary"
            @click="showDetailsModal = false"
          >
            Close
          </button>
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
  name: 'DoctorPrescriptions',
  components: {
    DataTable,
    Modal
  },
  setup() {
    const doctorStore = useDoctorStore()
    const { prescriptions, loading } = storeToRefs(doctorStore)
    
    const showDetailsModal = ref(false)
    const selectedPrescription = ref(null)
    const sendingEmail = ref(null)

    const columns = [
      { key: 'date', label: 'Date', sortable: true },
      { key: 'patient_name', label: 'Patient', sortable: true },
      { key: 'diagnosis', label: 'Diagnosis', sortable: true },
      { key: 'prescription', label: 'Prescription', sortable: true },
      { key: 'email_sent', label: 'Email Status', sortable: true },
      { key: 'resend_count', label: 'Resends', sortable: true }
    ]

    onMounted(() => {
      doctorStore.fetchPrescriptions()
    })

    const viewDetails = (prescription) => {
      selectedPrescription.value = prescription
      showDetailsModal.value = true
    }

const sendEmail = async (prescription) => {
      if (!prescription?.id) {
        alert('Invalid prescription')
        return
      }
      
      try {
        sendingEmail.value = prescription.id
        const response = await doctorAPI.sendPrescriptionEmail(prescription.id)
        console.log('Send prescription email response:', response)
        
        // If task ID returned, track its status
        const taskId = response?.data?.data?.task_id
        if (taskId) {
          alert('Sending prescription email...')
          
          // Poll task status
          const checkStatus = setInterval(async () => {
            try {
              const { taskAPI } = await import('@/services/api')
              const statusResponse = await taskAPI.getStatus(taskId)
              console.log('Task status response:', statusResponse)
              const status = statusResponse.data.data.status
              
              if (status === 'SUCCESS') {
                clearInterval(checkStatus)
                sendingEmail.value = null
                alert('Prescription email sent successfully!')
                // Refresh prescriptions to show updated email status
                await doctorStore.fetchPrescriptions()
              } else if (status === 'FAILURE') {
                clearInterval(checkStatus)
                sendingEmail.value = null
                alert('Failed to send prescription email. Please try again.')
              } else if (status === 'PENDING' || status === 'STARTED') {
                console.log(`Task is still ${status}, continuing to poll...`)
              }
            } catch (err) {
              console.error('Error checking task status:', err)
              clearInterval(checkStatus)
              sendingEmail.value = null
            }
          }, 2000)
          
          // Auto-stop polling after 30 seconds
          setTimeout(() => {
            clearInterval(checkStatus)
            sendingEmail.value = null
          }, 30000)
        } else {
          sendingEmail.value = null
          alert('Email sent!')
          // Refresh prescriptions to show updated email status
          await doctorStore.fetchPrescriptions()
        }
      } catch (err) {
        sendingEmail.value = null
        const errorMessage = err.response?.data?.message || 'Failed to send email'
        console.error('Error sending prescription email:', err)
        alert(`Error: ${errorMessage}`)
      }
    }

    const printPrescription = () => {
      window.print()
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

    const exportPrescriptionsCSV = async () => {
      try {
        const response = await doctorAPI.exportPrescriptionsEmail();
        // Since this is now an email-based export, we just show a message
        alert('Prescriptions CSV export initiated. You will receive an email with the file shortly.');
      } catch (err) {
        console.error('Export failed:', err);
        alert('Failed to initiate prescriptions export. Please try again.');
      }
    };

    return {
      prescriptions,
      loading,
      columns,
      showDetailsModal,
      selectedPrescription,
      sendingEmail,
      viewDetails,
      sendEmail,
      printPrescription,
      formatDate,
      exportPrescriptionsCSV
    }
  }
}
</script>

<style scoped>
.doctor-prescriptions {
  animation: fadeInUp 0.4s ease-out;
}

.bg-success-subtle { background-color: #e6f9eb; }
.bg-secondary-subtle { background-color: #f5f5f7; }
.bg-warning-subtle { background-color: #fff3cd; }
.bg-light-subtle { background-color: #f8f9fa; }

@media print {
  .modal-header, .modal-footer { display: none; }
  .modal-body { background-color: white !important; }
  .card { border: none !important; shadow: none !important; }
}
</style>