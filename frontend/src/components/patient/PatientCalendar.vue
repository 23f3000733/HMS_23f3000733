<template>
  <div class="calendar-view">
    <!-- Calendar Header -->
    <div class="d-flex justify-content-between align-items-center mb-4 px-2">
      <h4 class="mb-0 fw-bold text-dark">
        {{ currentMonthYear }}
      </h4>
      <div
        class="btn-group shadow-sm rounded-pill"
        role="group"
      >
        <button
          class="btn btn-light border-0 px-3"
          @click="previousMonth"
        >
          <i class="bi bi-chevron-left text-primary" />
        </button>
        <button
          class="btn btn-light border-0 px-3"
          @click="goToToday"
        >
          Today
        </button>
        <button
          class="btn btn-light border-0 px-3"
          @click="nextMonth"
        >
          <i class="bi bi-chevron-right text-primary" />
        </button>
      </div>
    </div>

    <!-- Calendar Grid -->
    <div class="card border-0 shadow-sm overflow-hidden rounded-4">
      <div class="card-body p-0">
        <!-- Day Headers -->
        <div class="calendar-header-row border-bottom">
          <div
            v-for="day in dayHeaders"
            :key="day"
            class="calendar-header-cell"
          >
            {{ day }}
          </div>
        </div>
        
        <!-- Days -->
        <div class="calendar-grid">
          <div 
            v-for="(day, index) in calendarDays" 
            :key="index"
            class="calendar-day"
            :class="{
              'other-month': !day.isCurrentMonth,
              'today': day.isToday,
              'selected': selectedDate && selectedDate.toDateString() === day.fullDate.toDateString()
            }"
            @click="selectDate(day)"
          >
            <div class="day-content">
              <div
                class="day-number"
                :class="{ 'text-white bg-danger rounded-circle': day.isToday }"
              >
                {{ day.date }}
              </div>
              
              <!-- Event Dots -->
              <div
                v-if="day.appointments.length > 0"
                class="event-dots"
              >
                <div 
                  v-for="appt in day.appointments.slice(0, 3)" 
                  :key="appt.id"
                  class="event-dot"
                  :class="'bg-' + getStatusColor(appt.status)"
                  :title="appt.time + ' - ' + appt.doctor_name"
                />
                <span
                  v-if="day.appointments.length > 3"
                  class="more-events text-muted"
                >+</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Selected Date Events (Split View Style) -->
    <transition name="slide-up">
      <div
        v-if="selectedDateEvents.length > 0 || selectedDate"
        class="mt-4"
      >
        <h6 class="text-muted text-uppercase fw-bold mb-3 px-2">
          {{ selectedDate ? formatDateFull(selectedDate) : 'Select a date' }}
        </h6>
        
        <div
          v-if="selectedDateEvents.length > 0"
          class="list-group list-group-flush border-0 bg-transparent"
        >
          <div 
            v-for="appt in selectedDateEvents" 
            :key="appt.id" 
            class="card border-0 shadow-sm mb-3 hover-lift"
            @click="showAppointmentDetails(appt)"
          >
            <div class="card-body p-3 d-flex align-items-center">
              <div
                class="me-3 text-center"
                style="min-width: 60px;"
              >
                <div class="fw-bold text-dark">
                  {{ formatTime(appt.time) }}
                </div>
                <small class="text-muted">{{ getDuration(appt.time) }}</small>
              </div>
              <div class="vr me-3 opacity-25" />
              <div class="flex-grow-1">
                <h6 class="mb-1 fw-bold text-primary">
                  Dr. {{ appt.doctor_name }}
                </h6>
                <p class="mb-0 small text-muted text-truncate">
                  {{ appt.diagnosis || 'Regular Checkup' }}
                </p>
              </div>
              <span
                class="badge rounded-pill"
                :class="'bg-' + getStatusColor(appt.status) + '-subtle text-' + getStatusColor(appt.status)"
              >
                {{ appt.status }}
              </span>
            </div>
          </div>
        </div>
        <div
          v-else-if="selectedDate"
          class="text-center py-5 text-muted opacity-50"
        >
          <i class="bi bi-calendar-plus fs-1 mb-2" />
          <p>No events for this day</p>
        </div>
      </div>
    </transition>

    <!-- Appointment Details Modal -->
    <transition name="fade">
      <div
        v-if="selectedAppointment"
        class="modal fade show d-block"
        style="background: rgba(0,0,0,0.5)"
        tabindex="-1"
        @click.self="selectedAppointment = null"
      >
        <div class="modal-dialog modal-dialog-centered">
          <div class="modal-content">
            <div class="modal-header border-0 pb-0">
              <h5 class="modal-title fw-bold">
                Event Details
              </h5>
              <button
                type="button"
                class="btn-close"
                @click="selectedAppointment = null"
              />
            </div>
            <div class="modal-body">
              <div class="d-flex align-items-center mb-4">
                <div class="avatar-circle bg-primary-subtle text-primary me-3">
                  {{ selectedAppointment.doctor_name.charAt(0) }}
                </div>
                <div>
                  <h5 class="fw-bold mb-0">
                    Dr. {{ selectedAppointment.doctor_name }}
                  </h5>
                  <p class="text-muted mb-0">
                    {{ formatDateFull(new Date(selectedAppointment.date)) }}
                  </p>
                </div>
              </div>

              <div class="p-3 bg-light rounded mb-3">
                <div class="d-flex justify-content-between mb-2">
                  <span class="text-muted">Time</span>
                  <span class="fw-medium">{{ formatTime(selectedAppointment.time) }}</span>
                </div>
                <div class="d-flex justify-content-between">
                  <span class="text-muted">Status</span>
                  <span
                    class="badge"
                    :class="'bg-' + getStatusColor(selectedAppointment.status)"
                  >{{ selectedAppointment.status }}</span>
                </div>
              </div>

              <div
                v-if="selectedAppointment.diagnosis"
                class="mb-3"
              >
                <small class="text-muted text-uppercase fw-bold">Diagnosis</small>
                <p class="mb-0">
                  {{ selectedAppointment.diagnosis }}
                </p>
              </div>

              <div class="d-grid gap-2 mt-4">
                <button 
                  v-if="selectedAppointment.status === 'Booked'" 
                  class="btn btn-outline-primary"
                  @click="rescheduleFromCalendar(selectedAppointment)"
                >
                  Reschedule
                </button>
                <button 
                  v-if="selectedAppointment.status === 'Booked'" 
                  class="btn btn-outline-danger"
                  @click="cancelFromCalendar(selectedAppointment.id)"
                >
                  Cancel Appointment
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </transition>
  </div>
</template>

<script>
import { patientAPI } from '../../services/api'

export default {
  name: 'PatientCalendar',
  data() {
    return {
      currentDate: new Date(),
      appointments: [],
      selectedAppointment: null,
      selectedDate: new Date(),
      dayHeaders: ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']
    }
  },
  computed: {
    currentMonthYear() {
      return this.currentDate.toLocaleDateString('en-US', { month: 'long', year: 'numeric' })
    },
    calendarDays() {
      const year = this.currentDate.getFullYear()
      const month = this.currentDate.getMonth()
      const firstDay = new Date(year, month, 1)
      const firstDayOfWeek = firstDay.getDay()
      const lastDay = new Date(year, month + 1, 0)
      const lastDate = lastDay.getDate()
      const prevMonthLastDay = new Date(year, month, 0).getDate()
      
      const days = []
      
      // Previous month
      for (let i = firstDayOfWeek - 1; i >= 0; i--) {
        days.push({
          date: prevMonthLastDay - i,
          isCurrentMonth: false,
          isToday: false,
          fullDate: new Date(year, month - 1, prevMonthLastDay - i),
          appointments: []
        })
      }
      
      // Current month
      const today = new Date()
      for (let date = 1; date <= lastDate; date++) {
        const currentDay = new Date(year, month, date)
        const dateStr = currentDay.toISOString().split('T')[0]
        // Ensure appointments is an array before filtering
        const dayAppointments = Array.isArray(this.appointments) 
          ? this.appointments.filter(appt => appt.date === dateStr)
          : []
        
        days.push({
          date,
          isCurrentMonth: true,
          isToday: today.toDateString() === currentDay.toDateString(),
          fullDate: currentDay,
          appointments: dayAppointments
        })
      }
      
      // Next month
      const remainingDays = 42 - days.length
      for (let date = 1; date <= remainingDays; date++) {
        days.push({
          date,
          isCurrentMonth: false,
          isToday: false,
          fullDate: new Date(year, month + 1, date),
          appointments: []
        })
      }
      
      return days
    },
    selectedDateEvents() {
      if (!this.selectedDate) return []
      const dateStr = this.selectedDate.toISOString().split('T')[0]
      // Ensure appointments is an array before filtering
      return Array.isArray(this.appointments) 
        ? this.appointments.filter(appt => appt.date === dateStr)
        : []
    }
  },
  created() {
    this.fetchAppointments()
  },
  methods: {
    async fetchAppointments() {
      try {
        const response = await patientAPI.getHistory()
        // Handle various response structures and ensure it's an array
        if (response.data) {
          if (Array.isArray(response.data)) {
            this.appointments = response.data
          } else if (response.data.data && Array.isArray(response.data.data)) {
            this.appointments = response.data.data
          } else if (response.data.appointments && Array.isArray(response.data.appointments)) {
            this.appointments = response.data.appointments
          } else {
            this.appointments = []
          }
        } else {
          this.appointments = []
        }
      } catch (err) { 
        console.error('Error fetching appointments:', err)
        this.appointments = [] // Ensure it's always an array
      }
    },
    previousMonth() {
      this.currentDate = new Date(this.currentDate.getFullYear(), this.currentDate.getMonth() - 1, 1)
    },
    nextMonth() {
      this.currentDate = new Date(this.currentDate.getFullYear(), this.currentDate.getMonth() + 1, 1)
    },
    showAppointmentDetails(appt) {
      this.selectedAppointment = appt
    },
    getStatusColor(status) {
      const map = { 'Booked': 'primary', 'Completed': 'success', 'Cancelled': 'secondary' }
      return map[status] || 'secondary'
    },
    rescheduleFromCalendar(appt) {
      this.$emit('reschedule', appt)
      this.selectedAppointment = null
    },
    async cancelFromCalendar(id) {
      if (!confirm('Cancel this appointment?')) return
      try {
        await patientAPI.cancelAppointment(id)
        alert('Cancelled successfully')
        this.selectedAppointment = null
        this.fetchAppointments()
      } catch (err) { alert('Failed to cancel') }
    },
    formatDateFull(date) {
      return date.toLocaleDateString('en-US', { weekday: 'long', month: 'long', day: 'numeric' })
    },
    formatTime(time) {
      const [hours, minutes] = time.split(':')
      const h = parseInt(hours)
      const ampm = h >= 12 ? 'PM' : 'AM'
      const h12 = h % 12 || 12
      return `${h12}:${minutes} ${ampm}`
    },
    getDuration(time) {
      return '30 min' // Placeholder
    },
    selectDate(day) {
      this.selectedDate = day.fullDate
    }
  }
}
</script>

<style scoped>
.calendar-view {
  animation: fadeInUp 0.4s ease-out;
}

.calendar-header-row {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  background-color: #f8f9fa;
}

.calendar-header-cell {
  padding: 10px;
  text-align: center;
  font-size: 0.85rem;
  font-weight: 600;
  color: #8e8e93;
  text-transform: uppercase;
}

.calendar-grid {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  background-color: white;
}

.calendar-day {
  min-height: 100px;
  border-right: 1px solid #f0f0f0;
  border-bottom: 1px solid #f0f0f0;
  padding: 8px;
  cursor: pointer;
  transition: background-color 0.2s;
}

.calendar-day:nth-child(7n) {
  border-right: none;
}

.calendar-day:hover {
  background-color: #f8f9fa;
}

.calendar-day.selected {
  background-color: #f0f8ff;
}

.calendar-day.other-month {
  background-color: #fafafa;
}

.calendar-day.other-month .day-number {
  color: #d1d1d6;
}

.day-content {
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.day-number {
  width: 28px;
  height: 28px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 500;
  font-size: 0.9rem;
  margin-bottom: 6px;
}

.day-number.bg-danger {
  background-color: #ff3b30 !important; /* Apple Red */
  font-weight: 600;
}

.event-dots {
  display: flex;
  gap: 3px;
  flex-wrap: wrap;
  justify-content: center;
}

.event-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
}

.more-events {
  font-size: 10px;
  line-height: 6px;
}

.hover-lift {
  transition: transform 0.2s, box-shadow 0.2s;
}

.hover-lift:hover {
  transform: translateY(-2px);
  box-shadow: 0 .5rem 1rem rgba(0,0,0,.08)!important;
}

.avatar-circle {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.2rem;
  font-weight: 600;
}

.bg-primary-subtle { background-color: #e5f2ff; }
.bg-success-subtle { background-color: #e6f9eb; }
.bg-secondary-subtle { background-color: #f5f5f7; }
</style>
