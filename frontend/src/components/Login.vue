<template>
  <div class="login-page">
    <div class="container">
      <div class="row justify-content-center align-items-center min-vh-100">
        <div class="col-md-5 col-lg-4">
          <!-- Logo & Title -->
          <div class="text-center mb-5">
            <div class="logo-container mb-3">
              <i class="bi bi-hospital-fill" />
            </div>
            <h1 class="fw-bold mb-1">
              HMS
            </h1>
            <p class="text-muted">
              Hospital Management System
            </p>
          </div>
          
          <!-- Login Card -->
          <div class="card login-card shadow-sm">
            <div class="card-body p-4">
              <h4 class="text-center mb-4 fw-semibold">
                Sign In
              </h4>
              
              <form @submit.prevent="login">
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
                <div class="mb-4">
                  <label class="form-label">Password</label>
                  <input 
                    v-model="password" 
                    type="password" 
                    class="form-control" 
                    placeholder="Enter your password" 
                    required
                    autocomplete="current-password"
                  >
                </div>
                
                <!-- Submit Button -->
                <button 
                  type="submit" 
                  class="btn btn-primary w-100 mb-3" 
                  :disabled="loading"
                >
                  <span
                    v-if="loading"
                    class="spinner-border spinner-border-sm me-2"
                  />
                  {{ loading ? 'Signing in...' : 'Sign In' }}
                </button>
                
                <!-- Error Alert -->
                <div
                  v-if="error"
                  class="alert alert-danger"
                  role="alert"
                >
                  {{ error }}
                </div>
              </form>
              
              <!-- Register Link -->
              <div class="text-center mt-4">
                <p class="mb-0 text-muted small">
                  Don't have an account? 
                  <router-link
                    to="/register"
                    class="text-decoration-none fw-semibold"
                  >
                    Register
                  </router-link>
                </p>
              </div>
            </div>
          </div>
          
          <!-- Default Credentials -->
          <div class="text-center mt-3">
            <small class="text-muted">
              Default: admin@hms.com / password
            </small>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { useAuthStore } from '@/stores/auth'

export default {
  name: 'Login',
  data() {
    return {
      email: '',
      password: '',
      error: '',
      loading: false
    }
  },
  methods: {
    async login() {
      this.loading = true
      this.error = ''
      
      const authStore = useAuthStore()
      const result = await authStore.login(this.email, this.password)
      
      this.loading = false
      
      if (result.success) {
        // Navigate based on role
        if (result.role === 'admin') {
          this.$router.push('/admin')
        } else if (result.role === 'doctor') {
          this.$router.push('/doctor')
        } else {
          this.$router.push('/patient')
        }
      } else {
        this.error = result.error || 'Login failed. Please check your credentials.'
      }
    }
  }
}
</script>

<style scoped>
.login-page {
  background-color: var(--color-light);
  min-height: 100vh;
}

.logo-container {
  font-size: 4rem;
  color: var(--color-primary);
}

.login-card {
  border: 1px solid var(--color-gray-200);
  border-radius: var(--radius-xl);
}

.min-vh-100 {
  min-height: 100vh;
}
</style>
