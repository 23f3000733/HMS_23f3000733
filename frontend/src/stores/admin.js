import { defineStore } from 'pinia'
import { adminAPI } from '@/services/api'

export const useAdminStore = defineStore('admin', {
    state: () => ({
        stats: null,
        doctors: [],
        patients: [],
        appointments: [],
        analytics: null,
        loading: {
            stats: false,
            doctors: false,
            patients: false,
            appointments: false,
            analytics: false
        },
        error: null
    }),

    getters: {
        totalDoctors: (state) => state.stats?.doctors || 0,
        totalPatients: (state) => state.stats?.patients || 0,
        totalAppointments: (state) => state.stats?.appointments || 0,
        revenue: (state) => state.stats?.revenue || 0,

        // Getters for filtered lists could go here
        activeDoctors: (state) => state.doctors.filter(d => d.active),
        flaggedDoctors: (state) => state.doctors.filter(d => d.flagged)
    },

    actions: {
        async fetchStats() {
            this.loading.stats = true
            try {
                const response = await adminAPI.getStats()
                if (response.data.success) {
                    this.stats = response.data.data
                }
            } catch (err) {
                this.error = 'Failed to fetch stats'
                console.error(err)
            } finally {
                this.loading.stats = false
            }
        },

        async fetchDoctors() {
            this.loading.doctors = true
            try {
                const response = await adminAPI.getDoctors()
                if (response.data.success) {
                    this.doctors = response.data.data.doctors || response.data.data
                }
            } catch (err) {
                this.error = 'Failed to fetch doctors'
                console.error(err)
            } finally {
                this.loading.doctors = false
            }
        },

        async addDoctor(doctorData) {
            try {
                const response = await adminAPI.addDoctor(doctorData)
                if (response.data.success) {
                    await this.fetchDoctors() // Refresh list
                    return { success: true }
                }
            } catch (_err) {
                const errorMessage = _err.response?.data?.errors
                    ? Object.values(_err.response.data.errors).join(', ')
                    : _err.response?.data?.message || 'Failed to add doctor'

                return {
                    success: false,
                    error: errorMessage
                }
            }
        },

        async updateDoctor(id, data) {
            try {
                const response = await adminAPI.updateDoctor(id, data)
                if (response.data.success) {
                    await this.fetchDoctors()
                    return { success: true }
                }
            } catch (_err) {
                return {
                    success: false,
                    error: _err.response?.data?.message || 'Failed to update doctor'
                }
            }
        },

        async deleteDoctor(id) {
            try {
                const response = await adminAPI.deleteDoctor(id)
                if (response.data.success) {
                    this.doctors = this.doctors.filter(d => d.id !== id)
                    return { success: true }
                }
            } catch (_err) {
                return {
                    success: false,
                    error: _err.response?.data?.message || 'Failed to delete doctor'
                }
            }
        },

        async flagDoctor(id) {
            try {
                const response = await adminAPI.flagDoctor(id)
                if (response.data.success) {
                    const doctor = this.doctors.find(d => d.id === id)
                    if (doctor) {
                        doctor.flagged = !doctor.flagged
                    }
                    return response  // Return full response for task ID
                }
            } catch (_err) {
                return { success: false, error: 'Failed to flag doctor' }
            }
        },

        async reactivateDoctor(id) {
            try {
                const response = await adminAPI.reactivateDoctor(id)
                if (response.data.success) {
                    const doctor = this.doctors.find(d => d.id === id)
                    if (doctor) {
                        doctor.active = true
                    }
                    return { success: true }
                }
            } catch (_err) {
                return {
                    success: false,
                    error: _err.response?.data?.message || 'Failed to reactivate doctor'
                }
            }
        },

        async fetchPatients() {
            this.loading.patients = true
            try {
                const response = await adminAPI.getPatients()
                if (response.data.success) {
                    this.patients = response.data.data.patients || response.data.data
                }
            } catch (err) {
                this.error = 'Failed to fetch patients'
                console.error(err)
            } finally {
                this.loading.patients = false
            }
        },

        async addPatient(patientData) {
            try {
                const response = await adminAPI.addPatient(patientData)
                if (response.data.success) {
                    await this.fetchPatients()
                    return { success: true }
                }
            } catch (_err) {
                return {
                    success: false,
                    error: _err.response?.data?.message || 'Failed to add patient'
                }
            }
        },

        async updatePatient(id, data) {
            try {
                const response = await adminAPI.updatePatient(id, data)
                if (response.data.success) {
                    await this.fetchPatients()
                    return { success: true }
                }
            } catch (_err) {
                return {
                    success: false,
                    error: _err.response?.data?.message || 'Failed to update patient'
                }
            }
        },

        async deletePatient(id) {
            try {
                const response = await adminAPI.deletePatient(id)
                if (response.data.success) {
                    this.patients = this.patients.filter(p => p.id !== id)
                    return { success: true }
                }
            } catch (_err) {
                return {
                    success: false,
                    error: _err.response?.data?.message || 'Failed to delete patient'
                }
            }
        },

        async flagPatient(id) {
            try {
                const response = await adminAPI.flagPatient(id)
                if (response.data.success) {
                    const patient = this.patients.find(p => p.id === id)
                    if (patient) {
                        patient.flagged = !patient.flagged
                    }
                    return response  // Return full response for task ID
                }
            } catch (_err) {
                return { success: false, error: 'Failed to flag patient' }
            }
        },

        async reactivatePatient(id) {
            try {
                const response = await adminAPI.reactivatePatient(id)
                if (response.data.success) {
                    const patient = this.patients.find(p => p.id === id)
                    if (patient) {
                        patient.active = true
                    }
                    return { success: true }
                }
            } catch (_err) {
                return {
                    success: false,
                    error: _err.response?.data?.message || 'Failed to reactivate patient'
                }
            }
        },

        async fetchAppointments() {
            this.loading.appointments = true
            try {
                const response = await adminAPI.getAppointments()
                if (response.data.success) {
                    this.appointments = response.data.data.appointments || response.data.data
                }
            } catch (err) {
                this.error = 'Failed to fetch appointments'
                console.error(err)
            } finally {
                this.loading.appointments = false
            }
        },

        async deleteAppointment(id) {
            try {
                const response = await adminAPI.deleteAppointment(id)
                if (response.data.success) {
                    this.appointments = this.appointments.filter(a => a.id !== id)
                    return { success: true }
                }
            } catch (_err) {
                return {
                    success: false,
                    error: _err.response?.data?.message || 'Failed to delete appointment'
                }
            }
        },

        async fetchAnalytics() {
            this.loading.analytics = true
            try {
                const response = await adminAPI.getAnalytics()
                if (response.data.success) {
                    this.analytics = response.data.data
                }
            } catch (err) {
                this.error = 'Failed to fetch analytics'
                console.error(err)
            } finally {
                this.loading.analytics = false
            }
        }
    }
})



