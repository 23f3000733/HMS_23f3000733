<template>
  <section class="testimonials-section">
    <div class="container">
      <div class="text-center mx-auto mb-5" style="max-width: 700px;">
        <h2 class="display-5 fw-bold text-dark mb-3">
          Trusted by healthcare professionals
        </h2>
        <p class="lead text-muted">
          See what doctors, administrators, and patients are saying about HMS.
        </p>
      </div>

      <div class="row g-4">
        <div
          v-for="(testimonial, index) in testimonials"
          :key="index"
          class="col-md-6 col-lg-4"
          :class="{ 'testimonial-offset': index === 1 }"
        >
          <div class="testimonial-card card border-0 shadow-sm h-100 position-relative">
            <!-- Background Quote Icon -->
            <Quote class="quote-bg position-absolute" />
            
            <div class="card-body p-4 position-relative">
              <div class="d-flex gap-1 mb-4">
                <Star v-for="i in 5" :key="i" class="star-icon text-warning" />
              </div>
              
              <p class="text-dark mb-4 lh-base">
                "{{ testimonial.content }}"
              </p>
              
              <div class="d-flex align-items-center gap-3 mt-auto">
                <div class="avatar rounded-circle overflow-hidden">
                  <img :src="testimonial.avatar" :alt="testimonial.author" class="w-100 h-100 object-fit-cover" />
                </div>
                <div>
                  <div class="fw-bold text-dark">{{ testimonial.author }}</div>
                  <div class="small text-muted">{{ testimonial.role }}</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup>
import { Star, Quote } from 'lucide-vue-next'

const testimonials = [
  {
    content: "HMS has completely transformed how we manage our clinic. The patient flow is smoother, and the administrative burden has been reduced significantly.",
    author: "Dr. Sarah Chen",
    role: "Chief of Medicine",
    avatar: "https://i.pravatar.cc/150?u=a042581f4e29026024d"
  },
  {
    content: "The best hospital management software we've used. The interface is clean, intuitive, and the support team is incredibly responsive.",
    author: "James Wilson",
    role: "Hospital Administrator",
    avatar: "https://i.pravatar.cc/150?u=a042581f4e29026704d"
  },
  {
    content: "As a patient, I love how easy it is to book appointments and access my medical records. It gives me peace of mind knowing my data is secure.",
    author: "Emily Rodriguez",
    role: "Patient",
    avatar: "https://i.pravatar.cc/150?u=a04258114e29026302d"
  }
]
</script>

<style scoped>
.testimonials-section {
  padding: 6rem 0;
  background: #f8f9fa;
}

.testimonial-offset {
  margin-top: 2rem;
}

.testimonial-card {
  transition: all 0.3s ease;
}

.testimonial-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 1rem 2rem rgba(0, 0, 0, 0.1) !important;
}

.quote-bg {
  top: 1.5rem;
  right: 1.5rem;
  width: 48px;
  height: 48px;
  color: #f1f3f5;
  z-index: 0;
}

.card-body {
  z-index: 1;
}

.star-icon {
  width: 16px;
  height: 16px;
  fill: currentColor;
}

.avatar {
  width: 48px;
  height: 48px;
  background: #e9ecef;
}

@media (min-width: 768px) {
  .testimonial-offset {
    margin-top: 3rem;
  }
}

@media (max-width: 767.98px) {
  .testimonial-offset {
    margin-top: 0;
  }
}
</style>
