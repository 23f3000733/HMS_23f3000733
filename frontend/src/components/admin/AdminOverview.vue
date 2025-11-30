<template>
  <div class="admin-overview">
    <!-- Stats Cards -->
    <div class="row g-4 mb-4">
      <!-- Skeleton Loading State -->
      <template v-if="loading.stats">
        <div
          v-for="n in 3"
          :key="n"
          class="col-md-4"
        >
          <CardSkeleton />
        </div>
      </template>

      <!-- Actual Stats Cards -->
      <template v-else>
        <div class="col-md-4">
          <div class="card border-0 shadow-sm h-100 hover-lift">
            <div class="card-body p-4">
              <div class="d-flex justify-content-between align-items-center">
                <div>
                  <p class="text-muted text-uppercase small fw-bold mb-1">
                    Total Doctors
                  </p>
                  <h2 class="display-6 fw-bold mb-0 text-primary">
                    {{ stats?.doctors || 0 }}
                  </h2>
                </div>
                <div class="icon-box bg-primary-subtle text-primary rounded-circle p-3">
                  <i class="bi bi-person-badge fs-4" />
                </div>
              </div>
            </div>
          </div>
        </div>
      
        <div class="col-md-4">
          <div class="card border-0 shadow-sm h-100 hover-lift">
            <div class="card-body p-4">
              <div class="d-flex justify-content-between align-items-center">
                <div>
                  <p class="text-muted text-uppercase small fw-bold mb-1">
                    Total Patients
                  </p>
                  <h2 class="display-6 fw-bold mb-0 text-success">
                    {{ stats?.patients || 0 }}
                  </h2>
                </div>
                <div class="icon-box bg-success-subtle text-success rounded-circle p-3">
                  <i class="bi bi-people fs-4" />
                </div>
              </div>
            </div>
          </div>
        </div>
      
        <div class="col-md-4">
          <div class="card border-0 shadow-sm h-100 hover-lift">
            <div class="card-body p-4">
              <div class="d-flex justify-content-between align-items-center">
                <div>
                  <p class="text-muted text-uppercase small fw-bold mb-1">
                    Appointments
                  </p>
                  <h2 class="display-6 fw-bold mb-0 text-info">
                    {{ stats?.appointments || 0 }}
                  </h2>
                </div>
                <div class="icon-box bg-info-subtle text-info rounded-circle p-3">
                  <i class="bi bi-calendar-check fs-4" />
                </div>
              </div>
            </div>
          </div>
        </div>
      </template>
    </div>
    
    <!-- Quick Actions -->
    <div class="card border-0 shadow-sm">
      <div class="card-header bg-white border-bottom py-3">
        <h5 class="mb-0 fw-semibold">
          <i class="bi bi-lightning-charge me-2 text-warning" />Quick Actions
        </h5>
      </div>
      <div class="card-body p-4">
        <div class="row g-3">
          <div class="col-md-4">
            <button 
              class="btn btn-light w-100 p-3 text-start border hover-lift" 
              @click="$emit('switch-tab', 'doctors')"
            >
              <div class="d-flex align-items-center">
                <div class="bg-primary-subtle text-primary rounded p-2 me-3">
                  <i class="bi bi-person-plus fs-5" />
                </div>
                <div>
                  <div class="fw-semibold">
                    Add Doctor
                  </div>
                  <small class="text-muted">Register new staff</small>
                </div>
              </div>
            </button>
          </div>
          <div class="col-md-4">
            <button 
              class="btn btn-light w-100 p-3 text-start border hover-lift" 
              @click="$emit('switch-tab', 'patients')"
            >
              <div class="d-flex align-items-center">
                <div class="bg-success-subtle text-success rounded p-2 me-3">
                  <i class="bi bi-user-plus fs-5" />
                </div>
                <div>
                  <div class="fw-semibold">
                    Add Patient
                  </div>
                  <small class="text-muted">Register new patient</small>
                </div>
              </div>
            </button>
          </div>
          <div class="col-md-4">
            <button 
              class="btn btn-light w-100 p-3 text-start border hover-lift" 
              @click="$emit('switch-tab', 'search')"
            >
              <div class="d-flex align-items-center">
                <div class="bg-warning-subtle text-warning rounded p-2 me-3">
                  <i class="bi bi-search fs-5" />
                </div>
                <div>
                  <div class="fw-semibold">
                    Search Records
                  </div>
                  <small class="text-muted">Find anyone</small>
                </div>
              </div>
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { onMounted } from 'vue'
import { useAdminStore } from '@/stores/admin'
import { storeToRefs } from 'pinia'
import CardSkeleton from '../shared/CardSkeleton.vue'

export default {
  name: 'AdminOverview',
  components: {
    CardSkeleton
  },
  setup() {
    const adminStore = useAdminStore()
    const { stats, loading } = storeToRefs(adminStore)

    onMounted(() => {
      adminStore.fetchStats()
    })

    return {
      stats,
      loading
    }
  }
}
</script>

<style scoped>
.admin-overview {
  animation: fadeInUp 0.4s ease-out;
}

.hover-lift {
  transition: transform 0.2s, box-shadow 0.2s;
}

.hover-lift:hover {
  transform: translateY(-2px);
  box-shadow: 0 .5rem 1rem rgba(0,0,0,.05)!important;
}

.icon-box {
  width: 56px;
  height: 56px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.bg-primary-subtle { background-color: #e5f2ff; }
.bg-success-subtle { background-color: #e6f9eb; }
.bg-info-subtle { background-color: #cff4fc; }
.bg-warning-subtle { background-color: #fff3cd; }
</style>
