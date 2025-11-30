<template>
  <section class="cta-section position-relative overflow-hidden">
    <!-- Animated Background Blobs -->
    <div class="bg-blobs position-absolute w-100 h-100 top-0 start-0">
      <div class="cta-blob blob-1"></div>
      <div class="cta-blob blob-2"></div>
    </div>

    <div class="container position-relative text-center" style="z-index: 1;">
      <h2 class="display-4 fw-bold text-white mb-4">
        Ready to transform your hospital?
      </h2>
      <p class="lead text-white-50 mb-5 mx-auto" style="max-width: 600px;">
        Join thousands of healthcare providers who trust HMS to deliver better patient care.
      </p>
      
      <div class="d-flex flex-column flex-sm-row justify-content-center gap-3">
        <router-link to="/register" class="btn btn-light btn-lg rounded-pill px-5 shadow-lg">
          Get Started for Free
        </router-link>
        <button class="btn btn-outline-light btn-lg rounded-pill px-5">
          Talk to Sales
        </button>
      </div>
    </div>
  </section>
</template>

<style scoped>
.cta-section {
  padding: 7rem 0;
  background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
}

.cta-blob {
  position: absolute;
  border-radius: 50%;
  filter: blur(80px);
  mix-blend-mode: screen;
  animation: blob-bounce 7s infinite;
}

.blob-1 {
  top: 50%;
  left: 25%;
  width: 400px;
  height: 400px;
  background: rgba(13, 110, 253, 0.3);
}

.blob-2 {
  top: 50%;
  right: 25%;
  width: 400px;
  height: 400px;
  background: rgba(111, 66, 193, 0.3);
  animation-delay: 2s;
}

@keyframes blob-bounce {
  0% { transform: translate(0, 0) scale(1); }
  33% { transform: translate(30px, -50px) scale(1.1); }
  66% { transform: translate(-20px, 20px) scale(0.9); }
  100% { transform: translate(0, 0) scale(1); }
}

.btn-light:hover {
  transform: translateY(-2px);
  box-shadow: 0 0.5rem 1.5rem rgba(255, 255, 255, 0.3) !important;
}

.btn-outline-light {
  background: rgba(255, 255, 255, 0.1);
  border-color: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
}

.btn-outline-light:hover {
  background: rgba(255, 255, 255, 0.2);
  border-color: rgba(255, 255, 255, 0.2);
  transform: translateY(-2px);
}
</style>
