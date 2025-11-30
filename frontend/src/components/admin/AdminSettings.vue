<template>
  <div class="admin-profile">
    <div class="row justify-content-center">
      <div class="col-md-6">
        <div class="card border-0 shadow-sm">
          <div class="card-body p-5 text-center">
            <div class="avatar-circle-lg bg-primary text-white mx-auto mb-4">
              <i class="bi bi-person-fill" />
            </div>
            <h4 class="fw-bold mb-1">
              {{ form.name || 'Admin Profile' }}
            </h4>
            <p class="text-muted mb-4">
              {{ profile?.email }}
            </p>

            <form
              class="text-start"
              @submit.prevent="saveProfile"
            >
              <div class="mb-3">
                <label class="form-label small text-muted text-uppercase fw-bold">Full Name</label>
                <input 
                  v-model="form.name" 
                  type="text" 
                  class="form-control" 
                  required
                >
              </div>
              
              <div class="mb-3">
                <label class="form-label small text-muted text-uppercase fw-bold">Email</label>
                <input 
                  v-model="form.email" 
                  type="email" 
                  class="form-control" 
                  required
                  disabled
                >
              </div>
              
              <div class="mb-4">
                <label class="form-label small text-muted text-uppercase fw-bold">Role</label>
                <input 
                  v-model="form.role" 
                  type="text" 
                  class="form-control" 
                  disabled
                >
              </div>
              
              <div class="d-grid">
                <button
                  type="submit"
                  class="btn btn-primary py-2"
                  :disabled="loading"
                >
                  {{ loading ? 'Saving Changes...' : 'Save Profile' }}
                </button>
              </div>
            </form>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'

export default {
  name: 'AdminProfile',
  setup() {
    const authStore = useAuthStore()
    const loading = ref(false)
    
    const form = ref({
      name: '',
      email: '',
      role: 'Administrator'
    })

    const profile = ref({
      email: ''
    })

    onMounted(() => {
      // In a real app, this would fetch admin profile data from an API
      // For now, we'll use mock data or data from auth store
      form.value.name = 'Admin User'
      form.value.email = authStore.user?.email || 'admin@hospital.com'
      profile.value.email = authStore.user?.email || 'admin@hospital.com'
    })

    const saveProfile = async () => {
      loading.value = true
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 1000))
      alert('Profile updated successfully')
      loading.value = false
    }

    return {
      profile,
      form,
      loading,
      saveProfile
    }
  }
}
</script>

<style scoped>
.admin-profile {
  animation: fadeInUp 0.4s ease-out;
}

.avatar-circle-lg {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 2.5rem;
}
</style>