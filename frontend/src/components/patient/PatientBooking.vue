<template>
  <div class="patient-booking">
    <div class="card border-0 shadow-sm mb-4">
      <div class="card-body p-4">
        <h5 class="fw-bold mb-3">
          Find a Doctor
        </h5>
        <div class="input-group input-group-lg">
          <span class="input-group-text bg-white border-end-0 text-muted">
            <i class="bi bi-search" />
          </span>
          <input 
            v-model="searchQuery" 
            type="text" 
            class="form-control border-start-0 ps-0" 
            placeholder="Search by name or specialization..."
            @keyup.enter="searchDoctors"
          >
          <button
            class="btn btn-primary px-4"
            @click="searchDoctors"
          >
            Search
          </button>
        </div>
      </div>
    </div>

    <!-- Doctors Grid -->
    <div class="row g-4">
      <div
        v-for="doctor in doctors"
        :key="doctor.id"
        class="col-md-6 col-lg-4"
      >
        <div class="card h-100 border-0 shadow-sm hover-lift">
          <div class="card-body p-4 text-center">
            <div class="avatar-circle-lg bg-primary-subtle text-primary mx-auto mb-3">
              {{ (doctor.name && typeof doctor.name === 'string') ? doctor.name.charAt(0) : '?' }}
            </div>
            <h5 class="fw-bold mb-1">
              Dr. {{ doctor.name || 'Unknown Doctor' }}
            </h5>
            <p class="text-primary fw-medium mb-2">
              {{ doctor.specialization || 'Specialization not specified' }}
            </p>
            <p class="text-muted small mb-3">
              {{ doctor.experience || 0 }} years experience
            </p>
            
            <!-- Availability information would be displayed here if available -->

            <div class="d-grid gap-2">
              <button
                class="btn btn-primary"
                @click="openBookingModal(doctor)"
              >
                Book Appointment
              </button>
              <button
                class="btn btn-outline-secondary btn-sm"
                @click="viewDoctorProfile(doctor)"
              >
                View Profile
              </button>
            </div>
          </div>
        </div>
      </div>
      
      <div
        v-if="doctors.length === 0"
        class="col-12"
      >
        <div class="text-center py-5 text-muted">
          <i class="bi bi-search fs-1 mb-3 opacity-25" />
          <h5>{{ searchQuery ? 'No doctors found' : 'Search to find doctors' }}</h5>
          <p class="mb-0">
            Try searching by specialization like 'Cardiology' or 'Dentist'
          </p>
        </div>
      </div>
    </div>

    <!-- Booking Modal -->
    <Modal
      v-model="showBookingModal"
      title="Book Appointment"
      confirm-text="Confirm Booking"
      @confirm="bookAppointment"
    >
      <p
        v-if="selectedDoctor"
        class="text-muted mb-4"
      >
        with <span class="fw-semibold text-dark">Dr. {{ selectedDoctor.name }}</span>
      </p>
      
      <div class="mb-3">
        <label class="form-label small text-muted text-uppercase fw-bold">Date</label>
        <input
          v-model="booking.date"
          type="date"
          class="form-control"
          required
          :min="new Date().toISOString().split('T')[0]"
        >
      </div>
      <div class="mb-4">
        <label class="form-label small text-muted text-uppercase fw-bold">Time</label>
        <input
          v-model="booking.time"
          type="time"
          class="form-control"
          required
        >
      </div>
    </Modal>

    <!-- Doctor Profile Modal -->
    <Modal
      v-model="showProfileModal"
      title="Doctor Profile"
      size="large"
      :show-default-footer="false"
    >
      <div v-if="viewingDoctor">
        <div class="text-center mb-4">
          <div class="avatar-circle-lg bg-primary-subtle text-primary mx-auto mb-3">
            {{ (viewingDoctor.name && typeof viewingDoctor.name === 'string') ? viewingDoctor.name.charAt(0) : '?' }}
          </div>
          <h4 class="fw-bold mb-1">
            Dr. {{ viewingDoctor.name || 'Unknown Doctor' }}
          </h4>
          <p class="text-primary fw-medium mb-0">
            {{ viewingDoctor.specialization || 'Specialization not specified' }}
          </p>
        </div>

        <div class="row g-4 mb-4">
          <div class="col-6">
            <div class="p-3 bg-light rounded text-center">
              <small class="text-muted text-uppercase fw-bold d-block mb-1">Experience</small>
              <span class="fw-bold fs-5">{{ viewingDoctor.experience }} Years</span>
            </div>
          </div>
          <div class="col-6">
            <div class="p-3 bg-light rounded text-center">
              <small class="text-muted text-uppercase fw-bold d-block mb-1">Rating</small>
              <span class="fw-bold fs-5">4.8 <i class="bi bi-star-fill text-warning small" /></span>
            </div>
          </div>
        </div>

        <h6 class="fw-bold mb-3">
          Your History
        </h6>
        <div
          v-if="doctorAppointments.length > 0"
          class="list-group list-group-flush border rounded"
        >
          <div
            v-for="appt in doctorAppointments"
            :key="appt.id"
            class="list-group-item"
          >
            <div class="d-flex justify-content-between align-items-center">
              <div>
                <div class="fw-medium">
                  {{ appt.date }} at {{ appt.time }}
                </div>
                <small class="text-muted">{{ appt.diagnosis || 'No diagnosis' }}</small>
              </div>
              <span
                class="badge rounded-pill"
                :class="{
                  'bg-primary-subtle text-primary': appt.status === 'Booked',
                  'bg-success-subtle text-success': appt.status === 'Completed',
                  'bg-secondary-subtle text-secondary': appt.status === 'Cancelled'
                }"
              >
                {{ appt.status }}
              </span>
            </div>
          </div>
        </div>
        <div
          v-else
          class="text-center text-muted py-4 bg-light rounded"
        >
          <small>No previous appointments with this doctor</small>
        </div>
      </div>
    </Modal>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import { usePatientStore } from '@/stores/patient'
import { patientAPI } from '@/services/api'
import Modal from '@/components/shared/Modal.vue'

export default {
  name: 'PatientBooking',
  components: { Modal },
  emits: ['appointment-booked'],
  setup(props, { emit }) {
    const patientStore = usePatientStore()

    const searchQuery = ref('')
    const doctors = ref([])
    const showBookingModal = ref(false)
    const showProfileModal = ref(false)
    const selectedDoctor = ref(null)
    const booking = ref({ date: '', time: '' })
    const viewingDoctor = ref(null)
    const doctorAppointments = ref([])

    onMounted(() => {
      searchDoctors()
    })

    const searchDoctors = async () => {
      try {
        const response = await patientAPI.searchDoctors(searchQuery.value)
        console.log('Fetched doctors data:', response.data) // Debug log for fetched data
        doctors.value = response.data.data  // Extract the actual doctors array
      } catch (err) {
        console.error('Failed to search doctors:', err)
        console.error('Error details:', err.response?.data || err.message) // Debug log for error details
      }
    }

    const openBookingModal = (doctor) => {
      selectedDoctor.value = doctor
      booking.value = { date: '', time: '' }
      showBookingModal.value = true
    }

    const bookAppointment = async () => {
      if (!booking.value.date || !booking.value.time) {
        alert('Please select both date and time')
        return false
      }

      const result = await patientStore.bookAppointment({
        doctor_id: selectedDoctor.value.id,
        date: booking.value.date,
        time: booking.value.time
      })

      if (result.success) {
        alert('Appointment booked successfully!')
        showBookingModal.value = false
        emit('appointment-booked')
        return true
      } else {
        alert(result.error || 'Failed to book appointment')
        return false
      }
    }

    const viewDoctorProfile = async (doctor) => {
      viewingDoctor.value = doctor
      showProfileModal.value = true
      try {
        const response = await patientAPI.getHistory()
        doctorAppointments.value = response.data.filter(appt => appt.doctor_name === doctor.name)
      } catch (err) {
        doctorAppointments.value = []
      }
    }

    return {
      searchQuery,
      doctors,
      showBookingModal,
      showProfileModal,
      selectedDoctor,
      booking,
      viewingDoctor,
      doctorAppointments,
      searchDoctors,
      openBookingModal,
      bookAppointment,
      viewDoctorProfile
    }
  }
}
</script>

<style scoped>
.patient-booking {
  animation: fadeInUp 0.4s ease-out;
}

.hover-lift {
  transition: transform 0.2s, box-shadow 0.2s;
}

.hover-lift:hover {
  transform: translateY(-4px);
  box-shadow: 0 .5rem 1rem rgba(0,0,0,.08)!important;
}

.avatar-circle-lg {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 2rem;
  font-weight: 600;
}

.bg-primary-subtle { background-color: #e5f2ff; }
.bg-success-subtle { background-color: #e6f9eb; }
.bg-secondary-subtle { background-color: #f5f5f7; }
</style>
