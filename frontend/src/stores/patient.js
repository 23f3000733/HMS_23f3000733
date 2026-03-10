import { defineStore } from 'pinia'
import { patientAPI } from '@/services/api'

export const usePatientStore = defineStore('patient', {
    state: () => ({
        stats: null,
        appointments: [],
        history: [],
        documents: [],
        profile: null,
        analytics: null,
        loading: {
            stats: false,
            appointments: false,
            history: false,
            documents: false,
            profile: false,
            analytics: false
        },
        error: null
    }),

    getters: {
        upcomingAppointments: (state) => state.appointments.filter(a => a.status === 'Booked'),
        pastAppointments: (state) => state.appointments.filter(a => ['Completed', 'Cancelled'].includes(a.status))
    },

    actions: {
        async fetchDashboard() {
            this.loading.stats = true
            try {
                const response = await patientAPI.getDashboard()
                if (response.data.success) {
                    this.stats = response.data.data
                    // Dashboard often returns recent appointments too
                    if (response.data.data.upcoming_appointments) {
                        this.appointments = response.data.data.upcoming_appointments
                    }
                }
            } catch {
                this.error = 'Failed to fetch dashboard'
            } finally {
                this.loading.stats = false
            }
        },

        async fetchHistory() {
            this.loading.history = true
            try {
                const response = await patientAPI.getHistory()
                if (response.data.success) {
                    this.history = response.data.data
                }
            } catch {
                this.error = 'Failed to fetch medical history'
            } finally {
                this.loading.history = false
            }
        },

        async bookAppointment(data) {
            try {
                const response = await patientAPI.bookAppointment(data)
                if (response.data.success) {
                    await this.fetchDashboard() // Refresh appointments
                    return { success: true }
                }
            } catch (_err) {
                return { success: false, error: _err.response?.data?.message }
            }
        },

        async cancelAppointment(id) {
            try {
                const response = await patientAPI.cancelAppointment(id)
                if (response.data.success) {
                    await this.fetchDashboard()
                    await this.fetchHistory()
                    return { success: true }
                }
            } catch (_err) {
                return { success: false, error: _err.response?.data?.message }
            }
        },

        async fetchDocuments() {
            this.loading.documents = true
            try {
                const response = await patientAPI.getDocuments()
                if (response.data.success) {
                    this.documents = response.data.data
                }
            } catch {
                this.error = 'Failed to fetch documents'
            } finally {
                this.loading.documents = false
            }
        },

        async uploadDocument(formData) {
            try {
                const response = await patientAPI.uploadDocument(formData)
                if (response.data.success) {
                    await this.fetchDocuments()
                    return { success: true }
                }
            } catch (_err) {
                return { success: false, error: _err.response?.data?.message }
            }
        },

        async fetchProfile() {
            this.loading.profile = true
            try {
                const response = await patientAPI.getProfile()
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
                const response = await patientAPI.updateProfile(data)
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
                const response = await patientAPI.getAnalytics()
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



