<template>
  <div class="register-page">
    <div class="container">
      <div class="row justify-content-center align-items-center min-vh-100 py-5">
        <div class="col-md-6 col-lg-5">
          <!-- Logo & Title -->
          <div class="text-center mb-5">
            <div class="logo-container mb-3">
              <i class="bi bi-hospital-fill" />
            </div>
            <h1 class="fw-bold mb-1">
              HMS
            </h1>
            <p class="text-muted">
              Create Your Account
            </p>
          </div>
          
          <!-- Register Card -->
          <div class="card register-card shadow-sm">
            <div class="card-body p-4">
              <h4 class="text-center mb-4 fw-semibold">
                Patient Registration
              </h4>
              
              <form @submit.prevent="register">
                <!-- Name and Age Row -->
                <div class="row g-3">
                  <div class="col-md-6">
                    <label class="form-label">Full Name</label>
                    <input 
                      v-model="name" 
                      type="text" 
                      class="form-control" 
                      placeholder="Enter your name" 
                      required
                      autocomplete="name"
                    >
                  </div>
                  <div class="col-md-6">
                    <label class="form-label">Age</label>
                    <input 
                      v-model="age" 
                      type="number" 
                      class="form-control" 
                      placeholder="Your age" 
                      min="1" 
                      max="120" 
                      required
                    >
                  </div>
                </div>
                
                <!-- Email Field -->
                <div class="mb-3">
                  <label class="form-label">Email</label>
                  <input 
                    v-model="email" 
                    type="email" 
                    class="form-control" 
                    placeholder="Enter your email" 
                    required
                    autocomplete="email"
                  >
                </div>
                
                <!-- Password Field -->
                <div class="mb-3">
                  <label class="form-label">Password</label>
                  <input 
                    v-model="password" 
                    type="password" 
                    class="form-control" 
                    placeholder="Create a password" 
                    required
                    autocomplete="new-password"
                  >
                </div>
                
                <!-- Contact Field -->
                <div class="mb-4">
                  <label class="form-label">Contact Number</label>
                  <input 
                    v-model="contact" 
                    type="tel" 
                    class="form-control" 
                    placeholder="Enter your contact number" 
                    required
                    autocomplete="tel"
                  >
                </div>
                
                <!-- Submit Button -->
                <button 
                  type="submit" 
                  class="btn btn-secondary w-100 mb-3" 
                  :disabled="loading"
                >
                  <span
                    v-if="loading"
                    class="spinner-border spinner-border-sm me-2"
                  />
                  {{ loading ? 'Creating Account...' : 'Register' }}
                </button>
                
                <!-- Success/Error Alert -->
                <div
                  v-if="message"
                  class="alert"
                  :class="messageType"
                  role="alert"
                >
                  {{ message }}
                </div>
              </form>
              
              <!-- Login Link -->
              <div class="text-center mt-4">
                <p class="mb-0 text-muted small">
                  Already have an account? 
                  <router-link
                    to="/login"
                    class="text-decoration-none fw-semibold"
                  >
                    Sign In
                  </router-link>
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { authAPI } from '../services/api'

export default {
  name: 'Register',
  data() {
    return {
      name: '',
      email: '',
      password: '',
      age: '',
      contact: '',
      message: '',
      messageType: '',
      loading: false,
      redirectTimer: null
    }
  },
  methods: {
    async register() {
      this.loading = true
      this.message = ''
      
      try {
        await authAPI.register({
          name: this.name,
          email: this.email,
          password: this.password,
          age: this.age,
          contact: this.contact
        })
        this.message = 'Registration successful! Redirecting to login...'
        this.messageType = 'alert-success'
        
        // Clear any existing timer
        if (this.redirectTimer) {
          clearTimeout(this.redirectTimer)
        }
        this.redirectTimer = setTimeout(() => {
          this.$router.push('/login')
        }, 2000)
      } catch (err) {
        this.message = err.response?.data?.message || 'Registration failed. Please try again.'
        this.messageType = 'alert-danger'
      } finally {
        this.loading = false
      }
    }
  },
  
  beforeUnmount() {
    // Clean up timer when component is destroyed
    if (this.redirectTimer) {
      clearTimeout(this.redirectTimer)
    }
  }
}
</script>

<style scoped>
.register-page {
  background-color: var(--color-light);
  min-height: 100vh;
}

.logo-container {
  font-size: 4rem;
  color: var(--color-secondary);
}

.register-card {
  border: 1px solid var(--color-gray-200);
  border-radius: var(--radius-xl);
}

.min-vh-100 {
  min-height: 100vh;
}
</style>
