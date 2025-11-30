<template>
  <section class="faq-section">
    <div class="container">
      <div class="text-center mx-auto mb-5" style="max-width: 600px;">
        <h2 class="display-5 fw-bold text-dark mb-3">
          Frequently Asked Questions
        </h2>
        <p class="lead text-muted">
          Everything you need to know about getting started with HMS.
        </p>
      </div>

      <div class="accordion-container mx-auto" style="max-width: 800px;">
        <div
          v-for="(faq, index) in faqs"
          :key="index"
          class="faq-item card border rounded-4 mb-3"
        >
          <button
            @click="toggle(index)"
            class="btn btn-link text-decoration-none w-100 d-flex align-items-center justify-content-between p-4 text-start"
          >
            <span class="fw-semibold text-dark">{{ faq.question }}</span>
            <ChevronDown
              class="chevron-icon text-muted"
              :class="{ 'rotated': isOpen(index) }"
            />
          </button>
          
          <div
            v-if="isOpen(index)"
            class="faq-answer px-4 pb-4 text-muted"
          >
            {{ faq.answer }}
          </div>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup>
import { ref } from 'vue'
import { ChevronDown } from 'lucide-vue-next'

const openIndex = ref(null)

const toggle = (index) => {
  openIndex.value = openIndex.value === index ? null : index
}

const isOpen = (index) => openIndex.value === index

const faqs = [
  {
    question: "Is HMS HIPAA compliant?",
    answer: "Yes, HMS is fully HIPAA compliant. We use bank-level encryption for all data transmission and storage, ensuring your patient data remains secure and private at all times."
  },
  {
    question: "Can I migrate data from my current system?",
    answer: "Absolutely. We offer comprehensive data migration services to help you move your existing patient records, appointment history, and staff data to HMS seamlessly."
  },
  {
    question: "Is there a contract or cancellation fee?",
    answer: "No, we believe in earning your business every month. You can cancel your subscription at any time with no hidden fees or penalties."
  },
  {
    question: "Do you offer training for staff?",
    answer: "Yes, we provide extensive onboarding and training resources, including video tutorials, documentation, and live webinars to ensure your team gets up to speed quickly."
  }
]
</script>

<style scoped>
.faq-section {
  padding: 6rem 0;
  background: white;
}

.faq-item {
  overflow: hidden;
  transition: all 0.3s ease;
}

.faq-item:hover {
  box-shadow: 0 0.5rem 1rem rgba(0, 0, 0, 0.08);
}

.btn-link {
  color: inherit;
  background: white;
  border: none;
  transition: background-color 0.2s;
}

.btn-link:hover {
  background: #f8f9fa;
}

.chevron-icon {
  width: 20px;
  height: 20px;
  transition: transform 0.3s ease;
  flex-shrink: 0;
}

.chevron-icon.rotated {
  transform: rotate(180deg);
}

.faq-answer {
  line-height: 1.6;
  animation: slideDown 0.3s ease;
}

@keyframes slideDown {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
</style>
