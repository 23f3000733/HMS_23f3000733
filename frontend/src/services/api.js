import axios from 'axios'

const api = axios.create({
    baseURL: import.meta.env.VITE_APP_BASE_URL || 'http://localhost:5000'
})

// Token management helpers
const getAccessToken = () => localStorage.getItem('access_token')
const getRefreshToken = () => localStorage.getItem('refresh_token')
const setTokens = (accessToken, refreshToken) => {
    localStorage.setItem('access_token', accessToken)
    if (refreshToken) {
        localStorage.setItem('refresh_token', refreshToken)
    }
}
const clearTokens = () => {
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
    localStorage.removeItem('token') // Remove old token format
}

// Add JWT Bearer token to all requests
api.interceptors.request.use(config => {
    const accessToken = getAccessToken()
    if (accessToken) {
        config.headers['Authorization'] = `Bearer ${accessToken}`
    }

    // Fallback: support old token format during transition
    const oldToken = localStorage.getItem('token')
    if (!accessToken && oldToken) {
        config.headers['Authentication-Token'] = oldToken
    }

    return config
}, error => {
    return Promise.reject(error)
})

// Handle token refresh on 401 errors
let isRefreshing = false
let refreshSubscribers = []

const subscribeTokenRefresh = (cb) => {
    refreshSubscribers.push(cb)
}

const onRefreshed = (token) => {
    refreshSubscribers.map(cb => cb(token))
    refreshSubscribers = []
}

api.interceptors.response.use(
    response => response,
    async error => {
        const originalRequest = error.config

        // If error is 401 and we haven't tried refreshing yet
        if (error.response?.status === 401 && !originalRequest._retry) {
            if (isRefreshing) {
                // Wait for refresh to complete
                return new Promise((resolve) => {
                    subscribeTokenRefresh((token) => {
                        originalRequest.headers['Authorization'] = `Bearer ${token}`
                        resolve(axios(originalRequest))
                    })
                })
            }

            originalRequest._retry = true
            isRefreshing = true

            const refreshToken = getRefreshToken()

            if (!refreshToken) {
                // No refresh token, redirect to login
                clearTokens()
                window.location.href = '/login'
                return Promise.reject(error)
            }

            try {
                // Attempt to refresh token
                const response = await api.post('/auth/refresh', {
                    refresh_token: refreshToken
                }, { _retry: true })

                if (response.data.success) {
                    const newAccessToken = response.data.data.access_token
                    setTokens(newAccessToken)
                    // Update default header
                    api.defaults.headers.common['Authorization'] = `Bearer ${newAccessToken}`
                    originalRequest.headers['Authorization'] = `Bearer ${newAccessToken}`

                    isRefreshing = false
                    onRefreshed(newAccessToken)

                    // Retry original request
                    return axios(originalRequest)
                }
            } catch (refreshError) {
                // Refresh failed, redirect to login
                isRefreshing = false
                clearTokens()
                window.location.href = '/login'
                return Promise.reject(refreshError)
            }
        }

        return Promise.reject(error)
    }
)

// Admin API
export const adminAPI = {
    getStats: () => api.get('/admin/stats'),
    getAnalytics: () => api.get('/admin/analytics'),
    getDoctors: () => api.get('/admin/doctors'),
    addDoctor: (data) => api.post('/admin/doctors', data),
    updateDoctor: (id, data) => api.put(`/admin/doctors/${id}`, data),
    deleteDoctor: (id) => api.delete(`/admin/doctors/${id}`),
    getDoctorDetails: (id) => api.get(`/admin/doctors/${id}/details`),
    flagDoctor: (id) => api.post(`/admin/doctors/${id}/flag`),
    reactivateDoctor: (id) => api.post(`/admin/doctors/${id}/reactivate`),
    getAppointments: () => api.get('/admin/appointments'),
    search: (query) => api.get(`/admin/search?q=${query}`),
    getPatients: () => api.get('/admin/patients'),
    addPatient: (data) => api.post('/admin/patients', data),
    updatePatient: (id, data) => api.put(`/admin/patients/${id}`, data),
    deletePatient: (id) => api.delete(`/admin/patients/${id}`),
    getPatientDetails: (id) => api.get(`/admin/patients/${id}/details`),
    flagPatient: (id) => api.post(`/admin/patients/${id}/flag`),
    reactivatePatient: (id) => api.post(`/admin/patients/${id}/reactivate`),
    deleteAppointment: (id) => api.delete(`/admin/appointments/${id}`),
    exportDoctorsEmail: () => api.post('/admin/doctors/export/email'),
    exportPatientsEmail: () => api.post('/admin/patients/export/email'),
    exportAppointmentsEmail: () => api.post('/admin/appointments/export/email'),
    // Scheduled task triggers
    triggerDailyReminders: () => api.post('/admin/tasks/daily-reminders'),
    triggerMonthlyReports: () => api.post('/admin/tasks/monthly-reports')
}

// Doctor API
export const doctorAPI = {
    getDashboard: () => api.get('/doctor/dashboard'),
    getAnalytics: () => api.get('/doctor/analytics'),
    getAppointments: () => api.get('/doctor/appointments'),
    completeAppointment: (id, data) => api.post(`/doctor/appointment/${id}/complete`, data),
    cancelAppointment: (id) => api.post(`/doctor/appointment/${id}/cancel`),
    rescheduleAppointment: (id, data) => api.post(`/doctor/appointment/${id}/reschedule`, data),
    getPatients: () => api.get('/doctor/patients'),
    getPatientHistory: (id) => api.get(`/doctor/patient/${id}/history`),
    getPrescriptions: () => api.get('/doctor/prescriptions'),
    sendPrescriptionEmail: (id) => api.post(`/doctor/prescription/${id}/send-email`),
    exportPrescriptionsCSV: () => api.get('/doctor/prescriptions/export/csv', { responseType: 'blob' }),
    exportPrescriptionsEmail: () => api.post('/doctor/prescriptions/export/email'),
    exportAppointmentsCSV: () => api.get('/doctor/appointments/export/csv', { responseType: 'blob' }),
    exportAppointmentsEmail: () => api.post('/doctor/appointments/export/email'),
    exportPatientsCSV: () => api.get('/doctor/patients/export/csv', { responseType: 'blob' }),
    exportPatientsEmail: () => api.post('/doctor/patients/export/email'),
    sendBulkPrescriptionEmails: (ids) => api.post('/doctor/prescriptions/bulk-email', { prescription_ids: ids }),

    // Profile
    getProfile: () => api.get('/doctor/profile'),
    updateProfile: (data) => api.put('/doctor/profile', data)
}

// Patient API
export const patientAPI = {
    searchDoctors: (specialization = '') => api.get(`/patient/doctors?specialization=${specialization}`),
    bookAppointment: (data) => api.post('/patient/book', data),
    cancelAppointment: (id) => api.post(`/patient/appointments/${id}/cancel`),
    getHistory: () => api.get('/patient/history'),
    getProfile: () => api.get('/patient/profile'),
    updateProfile: (data) => api.put('/patient/profile', data),
    exportHistory: () => api.post('/patient/export'),
    getDashboard: () => api.get('/patient/dashboard'),
    getAnalytics: () => api.get('/patient/analytics'),
    rescheduleAppointment: (id, data) => api.post(`/patient/appointments/${id}/reschedule`, data),
    uploadDocument: (formData) => api.post('/patient/documents', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
    }),
    getDocuments: () => api.get('/patient/documents'),
    downloadDocument: (id) => api.get(`/patient/documents/${id}/download`, { responseType: 'blob' })
}

// Auth API
export const authAPI = {
    login: (data) => api.post('/auth/login', data),
    register: (data) => api.post('/auth/register', data),
    logout: () => api.post('/auth/logout'),
    refreshToken: (refreshToken) => api.post('/auth/refresh', { refresh_token: refreshToken })
}

// Task Status API
export const taskAPI = {
    getStatus: (taskId) => api.get(`/task/status/${taskId}`)
}
// Export token helpers for use in components
export { getAccessToken, getRefreshToken, setTokens, clearTokens }

export default api