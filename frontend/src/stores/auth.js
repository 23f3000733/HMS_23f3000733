import { defineStore } from 'pinia'
import { authAPI, setTokens, clearTokens, getAccessToken } from '@/services/api'

export const useAuthStore = defineStore('auth', {
    state: () => ({
        user: null,
        token: null,
        refreshToken: null,
        role: null,
        isAuthenticated: false,
        loading: false,
        error: null
    }),

    getters: {
        isAdmin: (state) => state.role === 'admin',
        isDoctor: (state) => state.role === 'doctor',
        isPatient: (state) => state.role === 'patient',
        userId: (state) => state.user?.id,
        userEmail: (state) => state.user?.email
    },

    actions: {
        async login(email, password) {
            this.loading = true
            this.error = null

            try {
                const response = await authAPI.login({ email, password })

                if (response.data.success) {
                    const data = response.data.data

                    // Set tokens in localStorage via api helper
                    setTokens(data.access_token, data.refresh_token)

                    // Persist user data to localStorage
                    localStorage.setItem('role', data.role)
                    localStorage.setItem('user_id', data.user_id)
                    localStorage.setItem('email', data.email)

                    // Update store state
                    this.token = data.access_token
                    this.refreshToken = data.refresh_token
                    this.role = data.role
                    this.user = {
                        id: data.user_id,
                        email: data.email
                    }
                    this.isAuthenticated = true

                    return { success: true, role: data.role }
                }
            } catch (err) {
                this.error = err.response?.data?.message || 'Login failed'
                return { success: false, error: this.error }
            } finally {
                this.loading = false
            }
        },

        async register(userData) {
            this.loading = true
            this.error = null

            try {
                const response = await authAPI.register(userData)

                if (response.data.success) {
                    const data = response.data.data

                    setTokens(data.access_token, data.refresh_token)

                    // Persist user data to localStorage
                    localStorage.setItem('role', 'patient')
                    localStorage.setItem('user_id', data.user_id)
                    localStorage.setItem('email', userData.email)

                    this.token = data.access_token
                    this.refreshToken = data.refresh_token
                    this.role = 'patient' // Registration creates patient accounts
                    this.user = {
                        id: data.user_id,
                        email: userData.email
                    }
                    this.isAuthenticated = true

                    return { success: true }
                }
            } catch (err) {
                this.error = err.response?.data?.message || 'Registration failed'
                return { success: false, error: this.error }
            } finally {
                this.loading = false
            }
        },

        async logout() {
            try {
                await authAPI.logout()
            } catch (err) {
                console.error('Logout failed:', err)
            } finally {
                // Clear state
                this.token = null
                this.refreshToken = null
                this.user = null
                this.role = null
                this.isAuthenticated = false
                this.error = null

                // Clear localStorage
                clearTokens()
                localStorage.removeItem('role')
                localStorage.removeItem('user_id')
                localStorage.removeItem('email')
            }
        },

        // Initialize auth state from localStorage on app load
        initializeAuth() {
            const token = getAccessToken()
            const role = localStorage.getItem('role')
            const userId = localStorage.getItem('user_id')
            const email = localStorage.getItem('email')

            if (token && role) {
                this.token = token
                this.role = role
                this.user = { id: userId, email }
                this.isAuthenticated = true
            }
        },

        // Update user profile data
        updateUser(userData) {
            this.user = { ...this.user, ...userData }
        }
    }
})



