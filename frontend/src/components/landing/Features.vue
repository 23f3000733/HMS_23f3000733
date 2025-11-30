<template>
  <section id="features" class="features-section">
    <div class="container">
      <div class="text-center mx-auto mb-5" style="max-width: 700px;">
        <h2 class="display-5 fw-bold text-dark mb-3">
          Everything you need to run a modern hospital
        </h2>
        <p class="lead text-muted">
          Powerful features tailored for every role in your healthcare ecosystem.
        </p>
      </div>

      <div class="row g-4">
        <div
          v-for="feature in features"
          :key="feature.title"
          class="col-md-6 col-lg-4"
        >
          <div class="feature-card card border-0 shadow-sm h-100">
            <div class="card-body p-4">
              <div
                class="icon-wrapper rounded-3 d-flex align-items-center justify-content-center mb-4"
                :class="feature.bgClass"
              >
                <component :is="feature.icon" class="icon" :class="feature.textClass" />
              </div>
              
              <h3 class="h5 fw-bold text-dark mb-3">
                {{ feature.title }}
              </h3>
              
              <p class="text-muted mb-0">
                {{ feature.description }}
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup>
import { Stethoscope, Users, ShieldCheck, Brain, Calendar, Activity } from 'lucide-vue-next'

const features = [
  {
    title: 'For Doctors',
    description: 'Manage appointments, view patient history, and prescribe medication with an intuitive interface designed for efficiency.',
    icon: Stethoscope,
    bgClass: 'bg-primary-subtle',
    textClass: 'text-primary'
  },
  {
    title: 'For Patients',
    description: 'Book appointments, access medical records, and communicate with your healthcare providers seamlessly.',
    icon: Users,
    bgClass: 'bg-success-subtle',
    textClass: 'text-success'
  },
  {
    title: 'For Admins',
    description: 'Oversee hospital operations, manage staff, and analyze performance metrics from a centralized dashboard.',
    icon: ShieldCheck,
    bgClass: 'bg-purple-subtle',
    textClass: 'text-purple'
  },
  {
    title: 'AI Insights',
    description: 'Leverage machine learning to predict patient trends and optimize resource allocation.',
    icon: Brain,
    bgClass: 'bg-warning-subtle',
    textClass: 'text-warning'
  },
  {
    title: 'Smart Scheduling',
    description: 'Automated appointment management reduces no-shows and optimizes doctor availability.',
    icon: Calendar,
    bgClass: 'bg-danger-subtle',
    textClass: 'text-danger'
  },
  {
    title: 'Real-time Analytics',
    description: 'Track key performance indicators and generate detailed reports instantly.',
    icon: Activity,
    bgClass: 'bg-info-subtle',
    textClass: 'text-info'
  }
]
</script>

<style scoped>
.features-section {
  padding: 6rem 0;
  background: white;
}

.feature-card {
  transition: all 0.3s ease;
}

.feature-card:hover {
  transform: translateY(-8px);
  box-shadow: 0 1rem 3rem rgba(0, 0, 0, 0.1) !important;
}

.feature-card:hover h3 {
  color: #0d6efd !important;
}

.icon-wrapper {
  width: 56px;
  height: 56px;
  transition: all 0.3s ease;
}

.feature-card:hover .icon-wrapper {
  transform: scale(1.1);
}

.icon {
  width: 28px;
  height: 28px;
}

.bg-purple-subtle {
  background-color: rgba(111, 66, 193, 0.1);
}

.text-purple {
  color: #6f42c1;
}
</style>
