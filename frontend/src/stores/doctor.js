import { defineStore } from 'pinia'
import { doctorAPI } from '@/services/api'

export const useDoctorStore = defineStore('doctor', {
    state: () => ({
        stats: null,
        appointments: [],
        patients: [],
        prescriptions: [],
        profile: null,
        analytics: null,
        loading: {
            stats: false,
            appointments: false,
            patients: false,
            prescriptions: false,
            profile: false,
            analytics: false
        },
        error: null
    }),

    getters: {
        todayAppointments: (state) => {
            const today = new Date().toISOString().split('T')[0]
            return state.appointments.filter(a => a.date === today)
        },
        pendingAppointments: (state) => state.appointments.filter(a => a.status === 'Booked'),
        completedAppointments: (state) => state.appointments.filter(a => a.status === 'Completed')
    },

    actions: {
        async fetchDashboard() {
            this.loading.stats = true
            try {
                const response = await doctorAPI.getDashboard()
                if (response.data.success) {
                    this.stats = response.data.data
                }
            } catch {
                this.error = 'Failed to fetch dashboard stats'
            } finally {
                this.loading.stats = false
            }
        },

        async fetchAppointments() {
            this.loading.appointments = true
            try {
                const response = await doctorAPI.getAppointments()
                if (response.data.success) {
                    this.appointments = response.data.data
                }
            } catch {
                this.error = 'Failed to fetch appointments'
            } finally {
                this.loading.appointments = false
            }
        },

        async completeAppointment(id, data) {
            try {
                const response = await doctorAPI.completeAppointment(id, data)
                if (response.data.success) {
                    await this.fetchAppointments()
                    return { success: true }
                }
            } catch (_err) {
                return { success: false, error: _err.response?.data?.message }
            }
        },

        async cancelAppointment(id) {
            try {
                const response = await doctorAPI.cancelAppointment(id)
                if (response.data.success) {
                    await this.fetchAppointments()
                    return { success: true }
                }
            } catch (_err) {
                return { success: false, error: _err.response?.data?.message }
            }
        },

        async fetchPatients() {
            this.loading.patients = true
            try {
                const response = await doctorAPI.getPatients()
                if (response.data.success) {
                    this.patients = response.data.data
                }
            } catch {
                this.error = 'Failed to fetch patients'
            } finally {
                this.loading.patients = false
            }
        },

        async fetchPrescriptions() {
            this.loading.prescriptions = true
            try {
                const response = await doctorAPI.getPrescriptions()
                if (response.data.success) {
                    this.prescriptions = response.data.data
                }
            } catch {
                this.error = 'Failed to fetch prescriptions'
            } finally {
                this.loading.prescriptions = false
            }
        },

        async fetchProfile() {
            this.loading.profile = true
            try {
                const response = await doctorAPI.getProfile()
                if (response.data.success) {
                    this.profile = response.data.data
                }
            } catch {
                this.error = 'Failed to fetch profile'
            } finally {
                this.loading.profile = false
            }
        },

        async updateProfile(data) {
            try {
                const response = await doctorAPI.updateProfile(data)
                if (response.data.success) {
                    this.profile = response.data.data
                    return { success: true }
                }
            } catch (_err) {
                return { success: false, error: _err.response?.data?.message }
            }
        },

        async fetchAnalytics() {
            this.loading.analytics = true
            try {
                const response = await doctorAPI.getAnalytics()
                if (response.data.success) {
                    this.analytics = response.data.data
                }
            } catch {
                this.error = 'Failed to fetch analytics'
            } finally {
                this.loading.analytics = false
            }
        }
    }
})