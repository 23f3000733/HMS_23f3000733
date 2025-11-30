<template>
  <div class="doctor-profile">
    <div class="row justify-content-center">
      <div class="col-md-6">
        <div class="card border-0 shadow-sm">
          <div class="card-body p-5 text-center">
            <div class="avatar-circle-lg bg-primary text-white mx-auto mb-4">
              <i class="bi bi-person-fill" />
            </div>
            <h4 class="fw-bold mb-1">
              {{ form.name || 'Doctor Profile' }}
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
                <label class="form-label small text-muted text-uppercase fw-bold">Specialization</label>
                <input 
                  v-model="form.specialization" 
                  type="text" 
                  class="form-control" 
                  required
                >
              </div>
              
              <div class="mb-4">
                <label class="form-label small text-muted text-uppercase fw-bold">Experience (Years)</label>
                <input 
                  v-model="form.experience" 
                  type="number" 
                  class="form-control" 
                  required
                  min="0"
                >
              </div>
              
              <div class="d-grid">
                <button
                  type="submit"
                  class="btn btn-primary py-2"
                  :disabled="loading.profile"
                >
                  {{ loading.profile ? 'Saving Changes...' : 'Save Profile' }}
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
import { ref, onMounted, watch } from 'vue'
import { useDoctorStore } from '@/stores/doctor'
import { storeToRefs } from 'pinia'

export default {
  name: 'DoctorProfile',
  setup() {
    const doctorStore = useDoctorStore()
    const { profile, loading } = storeToRefs(doctorStore)
    
    const form = ref({ name: '', specialization: '', experience: 0 })

    onMounted(async () => {
      await doctorStore.fetchProfile()
      if (profile.value) {
        form.value = {
          name: profile.value.name,
          specialization: profile.value.specialization,
          experience: profile.value.experience
        }
      }
    })

    // Watch for profile changes in case it's loaded later
    watch(profile, (newProfile) => {
      if (newProfile) {
        form.value = {
          name: newProfile.name,
          specialization: newProfile.specialization,
          experience: newProfile.experience
        }
      }
    })

    const saveProfile = async () => {
      const result = await doctorStore.updateProfile(form.value)
      if (result.success) {
        alert('Profile updated successfully')
      } else {
        alert(result.error)
      }
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
.doctor-profile {
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
