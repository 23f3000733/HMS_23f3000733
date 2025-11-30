<template>
  <section class="stats-section border-top border-bottom">
    <div class="container">
      <div class="row g-4">
        <div v-for="stat in stats" :key="stat.label" class="col-6 col-md-3 text-center">
          <div class="stat-value text-gradient fw-bold mb-2">
            {{ stat.value }}
          </div>
          <div class="stat-label text-muted text-uppercase small fw-semibold">
            {{ stat.label }}
          </div>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup>
const stats = [
  { label: 'Patients Served', value: '10k+' },
  { label: 'Doctors', value: '500+' },
  { label: 'Hospitals', value: '50+' },
  { label: 'Uptime', value: '99.9%' }
]
</script>

<style scoped>
.stats-section {
  padding: 3rem 0;
  background: #f8f9fa;
  border-color: #e9ecef !important;
}

.stat-value {
  font-size: 2.5rem;
  line-height: 1;
}

.text-gradient {
  background: linear-gradient(135deg, #0d6efd, #0dcaf0);
  -webkit-background-clip: text;
  background-clip: text;
  -webkit-text-fill-color: transparent;
}

.stat-label {
  letter-spacing: 0.05em;
}
</style>
