<template>
  <div class="admin-appointments">
    <!-- Appointments Table -->
    <div class="card border-0 shadow-sm">
      <div class="card-body p-0">
        <DataTable
          :columns="columns"
          :data="appointments"
          :loading="loading.appointments"
          searchable
          search-placeholder="Search doctor or patient..."
          :per-page="10"
          empty-message="No appointments found"
          show-download-button
          file-name="all-appointments.csv"
          @download-requested="exportAppointmentsCSV"
        >
          <!-- Custom Date Column -->
          <template #column-date="{ row }">
            <div class="d-flex flex-column">
              <span>{{ formatDate(row.date) }}</span>
              <small class="text-muted">{{ formatTime(row.time) }}</small>
            </div>
          </template>

          <!-- Custom Doctor Column -->
          <template #column-doctor_name="{ value }">
            <span class="fw-medium">Dr. {{ value }}</span>
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

          <!-- Actions Column -->
          <template #actions="{ row }">
            <div class="btn-group btn-group-sm">
              <button
                class="btn btn-outline-primary"
                title="View Details"
                @click="viewDetails(row)"
              >
                <i class="bi bi-eye" />
              </button>
              <button
                class="btn btn-outline-danger"
                title="Delete"
                @click="deleteAppointment(row)"
              >
                <i class="bi bi-trash" />
              </button>
            </div>
          </template>
        </DataTable>
      </div>
    </div>

    <!-- Appointment Details Modal -->
    <Modal
      v-model="showViewModal"
      title="Appointment Details"
      size="large"
      :show-default-footer="false"
    >
      <div
        v-if="selectedAppt"
        class="row g-4"
      >
        <!-- Info Column -->
        <div class="col-lg-4">
          <div class="text-center mb-4">
            <div class="avatar-circle-lg bg-primary-subtle text-primary mx-auto mb-3">
              <i class="bi bi-calendar-check" />
            </div>
            <h4 class="fw-bold mb-1">
              Appointment #{{ selectedAppt.id }}
            </h4>
            <span
              class="badge rounded-pill mt-2"
              :class="{
                'bg-primary-subtle text-primary': selectedAppt.status === 'Booked',
                'bg-success-subtle text-success': selectedAppt.status === 'Completed',
                'bg-secondary-subtle text-secondary': selectedAppt.status === 'Cancelled'
              }"
            >
              {{ selectedAppt.status }}
            </span>
          </div>

          <div class="card bg-light border-0 mb-3">
            <div class="card-body">
              <div class="d-flex justify-content-between mb-2">
                <span class="text-muted">Date</span>
                <span class="fw-medium">{{ formatDate(selectedAppt.date) }}</span>
              </div>
              <div class="d-flex justify-content-between mb-2">
                <span class="text-muted">Time</span>
                <span class="fw-medium">{{ formatTime(selectedAppt.time) }}</span>
              </div>
            </div>
          </div>

          <div class="card bg-light border-0">
            <div class="card-body">
              <h6 class="fw-bold mb-3">
                Participants
              </h6>
              <div class="d-flex align-items-center mb-3">
                <div class="avatar-circle-sm bg-white text-primary me-3 border">
                  <i class="bi bi-person-badge" />
                </div>
                <div>
                  <small class="text-muted d-block">Doctor</small>
                  <span class="fw-medium">Dr. {{ selectedAppt.doctor_name }}</span>
                </div>
              </div>
              <div class="d-flex align-items-center">
                <div class="avatar-circle-sm bg-white text-success me-3 border">
                  <i class="bi bi-person" />
                </div>
                <div>
                  <small class="text-muted d-block">Patient</small>
                  <span class="fw-medium">{{ selectedAppt.patient_name }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Details Column -->
        <div class="col-lg-8">
          <h6 class="fw-bold mb-3">
            Medical Records
          </h6>
          
          <div class="card border-0 shadow-sm mb-4">
            <div class="card-body">
              <h6 class="text-muted text-uppercase small fw-bold mb-2">
                Diagnosis
              </h6>
              <p class="mb-0">
                {{ selectedAppt.diagnosis || 'No diagnosis recorded.' }}
              </p>
            </div>
          </div>

          <div class="card border-0 shadow-sm mb-4">
            <div class="card-body">
              <h6 class="text-muted text-uppercase small fw-bold mb-2">
                Prescription
              </h6>
              <div class="bg-light p-3 rounded border font-monospace small">
                {{ selectedAppt.prescription || 'No prescription recorded.' }}
              </div>
            </div>
          </div>

          <div
            v-if="selectedAppt.notes"
            class="card border-0 shadow-sm"
          >
            <div class="card-body">
              <h6 class="text-muted text-uppercase small fw-bold mb-2">
                Notes
              </h6>
              <p class="mb-0 text-muted">
                {{ selectedAppt.notes }}
              </p>
            </div>
          </div>
        </div>
      </div>
    </Modal>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import { useAdminStore } from '@/stores/admin'
import { storeToRefs } from 'pinia'
import { adminAPI } from '@/services/api'
import DataTable from '@/components/shared/DataTable.vue'
import Modal from '@/components/shared/Modal.vue'

export default {
  name: 'AdminAppointments',
  components: {
    DataTable,
    Modal
  },
  setup() {
    const adminStore = useAdminStore()
    const { appointments, loading } = storeToRefs(adminStore)
    
    const showViewModal = ref(false)
    const selectedAppt = ref(null)

    const columns = [
      { key: 'doctor_name', label: 'Doctor', sortable: true },
      { key: 'patient_name', label: 'Patient', sortable: true },
      { key: 'date', label: 'Date & Time', sortable: true },
      { key: 'status', label: 'Status', sortable: true }
    ]

    const viewDetails = (appt) => {
      selectedAppt.value = appt
      showViewModal.value = true
    }

    const deleteAppointment = async (appt) => {
      if (!confirm('Delete this appointment?')) return
      await adminStore.deleteAppointment(appt.id)
    }

    const formatDate = (date) => {
      return new Date(date).toLocaleDateString('en-US', { 
        year: 'numeric', 
        month: 'short', 
        day: 'numeric' 
      })
    }

    const formatTime = (time) => {
      return time.substring(0, 5)
    }

    const exportAppointmentsCSV = async () => {
      try {
        const response = await adminAPI.exportAppointmentsEmail();
        // Since this is now an email-based export, we just show a message
        alert('Appointments CSV export initiated. You will receive an email with the file shortly.');
      } catch (err) {
        console.error('Export failed:', err);
        alert('Failed to initiate appointments export. Please try again.');
      }
    };

    onMounted(() => {
      adminStore.fetchAppointments()
    })

    return {
      appointments,
      loading,
      columns,
      showViewModal,
      selectedAppt,
      viewDetails,
      deleteAppointment,
      formatDate,
      formatTime,
      exportAppointmentsCSV
    }
  }
}
</script>

<style scoped>
.admin-appointments { animation: fadeInUp 0.4s ease-out; }
.avatar-circle-lg { width: 80px; height: 80px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 2rem; font-weight: 600; }
.avatar-circle-sm { width: 32px; height: 32px; border-radius: 50%; display: flex; align-items: center; justify-content: center; }
.bg-primary-subtle { background-color: #e5f2ff; }
.bg-success-subtle { background-color: #e6f9eb; }
.bg-secondary-subtle { background-color: #f5f5f7; }
</style>
