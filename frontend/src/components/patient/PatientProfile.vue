<template>
  <div class="patient-profile">
    <div class="row g-4">
      <!-- Profile Details -->
      <div class="col-lg-8">
        <div class="card border-0 shadow-sm mb-4">
          <div class="card-header bg-white border-bottom py-3 d-flex justify-content-between align-items-center">
            <h5 class="mb-0 fw-semibold">
              <i class="bi bi-person-circle me-2 text-primary" />My Profile
            </h5>
            <button
              class="btn btn-sm btn-outline-primary"
              @click="toggleEdit"
            >
              <i
                class="bi"
                :class="editMode ? 'bi-x-lg' : 'bi-pencil'"
              />
              {{ editMode ? 'Cancel' : 'Edit' }}
            </button>
          </div>
          <div class="card-body p-4">
            <form @submit.prevent="saveProfile">
              <div class="row g-3">
                <div class="col-md-6">
                  <label class="form-label small text-muted text-uppercase fw-bold">Full Name</label>
                  <input 
                    v-model="form.name" 
                    type="text" 
                    class="form-control" 
                    :disabled="!editMode"
                    required
                  >
                </div>
                <div class="col-md-6">
                  <label class="form-label small text-muted text-uppercase fw-bold">Email</label>
                  <input 
                    v-model="form.email" 
                    type="email" 
                    class="form-control bg-light" 
                    disabled
                  >
                </div>
                <div class="col-md-6">
                  <label class="form-label small text-muted text-uppercase fw-bold">Age</label>
                  <input 
                    v-model="form.age" 
                    type="number" 
                    class="form-control" 
                    :disabled="!editMode"
                    required
                  >
                </div>
                <div class="col-md-6">
                  <label class="form-label small text-muted text-uppercase fw-bold">Contact Number</label>
                  <input 
                    v-model="form.contact" 
                    type="text" 
                    class="form-control" 
                    :disabled="!editMode"
                    required
                  >
                </div>
                <div class="col-12">
                  <label class="form-label small text-muted text-uppercase fw-bold">Medical History</label>
                  <textarea 
                    v-model="form.medical_history" 
                    class="form-control" 
                    rows="4" 
                    :disabled="!editMode"
                    placeholder="Allergies, past surgeries, chronic conditions..."
                  />
                </div>
              </div>
              
              <transition name="fade">
                <div
                  v-if="editMode"
                  class="mt-4 text-end"
                >
                  <button
                    type="submit"
                    class="btn btn-primary px-4"
                    :disabled="loading.profile"
                  >
                    {{ loading.profile ? 'Saving...' : 'Save Changes' }}
                  </button>
                </div>
              </transition>
            </form>
          </div>
        </div>
      </div>

      <!-- Documents Section -->
      <div class="col-lg-4">
        <div class="card border-0 shadow-sm h-100">
          <div class="card-header bg-white border-bottom py-3">
            <h5 class="mb-0 fw-semibold">
              <i class="bi bi-file-earmark-medical me-2 text-primary" />Documents
            </h5>
          </div>
          <div class="card-body p-0">
            <!-- Upload Area -->
            <div class="p-3 border-bottom bg-light">
              <label class="form-label small text-muted fw-bold mb-2">Upload New Document</label>
              <div class="input-group input-group-sm">
                <input
                  ref="fileInput"
                  type="file"
                  class="form-control"
                  accept=".pdf,.jpg,.jpeg,.png"
                  @change="handleFileSelect"
                >
                <button
                  class="btn btn-primary"
                  :disabled="!selectedFile || loading.documents"
                  @click="uploadDocument"
                >
                  <i class="bi bi-cloud-upload" />
                </button>
              </div>
              <small
                class="text-muted d-block mt-1"
                style="font-size: 0.75rem;"
              >PDF, JPG, PNG (Max 5MB)</small>
            </div>

            <!-- Documents List -->
            <div class="list-group list-group-flush">
              <div
                v-for="doc in documents"
                :key="doc.id"
                class="list-group-item p-3"
              >
                <div class="d-flex justify-content-between align-items-center">
                  <div class="d-flex align-items-center overflow-hidden">
                    <div class="icon-box-sm bg-light text-primary rounded me-3 flex-shrink-0">
                      <i
                        class="bi"
                        :class="getFileIcon(doc.file_type)"
                      />
                    </div>
                    <div class="text-truncate">
                      <p class="mb-0 fw-medium text-truncate">
                        {{ doc.filename }}
                      </p>
                      <small class="text-muted">{{ formatTimestamp(doc.uploaded_at) }}</small>
                    </div>
                  </div>
                  <div class="btn-group btn-group-sm ms-2" role="group">
                    <button
                      v-if="doc.file_type && doc.file_type.includes('pdf')"
                      class="btn btn-outline-primary"
                      @click="viewDocument(doc.id)"
                    >
                      <i class="bi bi-eye" />
                    </button>
                    <button
                      class="btn btn-outline-secondary"
                      @click="downloadDocument(doc.id, doc.filename)"
                    >
                      <i class="bi bi-download" />
                    </button>
                  </div>
                </div>
              </div>
              <div
                v-if="documents.length === 0"
                class="text-center py-5 text-muted"
              >
                <i class="bi bi-folder2-open fs-1 opacity-25" />
                <p class="mt-2 mb-0 small">
                  No documents yet
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
import { ref, onMounted, watch } from 'vue'
import { usePatientStore } from '@/stores/patient'
import { storeToRefs } from 'pinia'
import { patientAPI } from '@/services/api'
import { useToast } from '@/composables/useToast'

export default {
  name: 'PatientProfile',
  setup() {
    const patientStore = usePatientStore()
    const { profile, documents, loading } = storeToRefs(patientStore)
    const toast = useToast()

    const editMode = ref(false)
    const form = ref({ name: '', email: '', age: '', contact: '', medical_history: '' })
    const selectedFile = ref(null)
    const fileInput = ref(null)

    onMounted(() => {
      patientStore.fetchProfile()
      patientStore.fetchDocuments()
    })

    // Watch profile changes and update form
    watch(profile, (newProfile) => {
      if (newProfile) {
        form.value = { ...newProfile }
      }
    }, { immediate: true })

    const toggleEdit = () => {
      if (editMode.value && profile.value) {
        // Reset form on cancel
        form.value = { ...profile.value }
      }
      editMode.value = !editMode.value
    }

    const saveProfile = async () => {
      const result = await patientStore.updateProfile(form.value)
      if (result.success) {
        toast.showSuccess('Profile updated successfully!')
        editMode.value = false
      } else {
        toast.showError(result.error || 'Failed to update profile')
      }
    }

    const handleFileSelect = (event) => {
      selectedFile.value = event.target.files[0]
    }

    const uploadDocument = async () => {
      if (!selectedFile.value) return

      const formData = new FormData()
      formData.append('file', selectedFile.value)

      const result = await patientStore.uploadDocument(formData)
      if (result.success) {
        toast.showSuccess('Uploaded successfully')
        selectedFile.value = null
        if (fileInput.value) fileInput.value.value = ''
      } else {
        toast.showError(result.error || 'Upload failed')
      }
    }

    const viewDocument = async (id) => {
      try {
        const response = await patientAPI.downloadDocument(id)
        // The response.data is already a Blob due to responseType: 'blob' in the API call
        const blob = response.data
        const url = window.URL.createObjectURL(blob)
        const newWindow = window.open(url, '_blank')
        // If window is open successfully we dont need to revoke the URL immedeatly
        if (!newWindow) {
          window.URL.revokeObjectURL(url)
          toast.showError('Popup blocked. Please allow popups to view documents.')
        }
      } catch (err) {
        console.error('View failed:', err)
        toast.showError('View failed. Please try again.')
      }
    }

    const downloadDocument = async (id, filename) => {
      try {
        const response = await patientAPI.downloadDocument(id)
        const url = window.URL.createObjectURL(new Blob([response.data]))
        const link = document.createElement('a')
        link.href = url
        link.setAttribute('download', filename || 'document')
        document.body.appendChild(link)
        link.click()
        link.remove()
      } catch (err) {
        toast.showError('Download failed')
      }
    }

    const formatTimestamp = (timestamp) => {
      return new Date(timestamp).toLocaleDateString()
    }

    const getFileIcon = (type) => {
    // Handle case where type might be undefined
      if (!type) return 'bi-file-earmark'
      if (type.includes('pdf')) return 'bi-file-pdf'
      if (type.includes('image')) return 'bi-file-image'
      return 'bi-file-earmark'
    }

    return {
      profile,
      documents,
      loading,
      editMode,
      form,
      selectedFile,
      fileInput,
      toggleEdit,
      saveProfile,
      handleFileSelect,
      uploadDocument,
      viewDocument,
      downloadDocument,
      formatTimestamp,
      getFileIcon
    }
  }
}
</script>

<style scoped>
.patient-profile { animation: fadeInUp 0.4s ease-out; }
.icon-box-sm { width: 32px; height: 32px; display: flex; align-items: center; justify-content: center; }
</style>
