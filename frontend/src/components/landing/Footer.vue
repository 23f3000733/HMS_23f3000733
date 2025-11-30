<template>
  <footer class="footer border-top">
    <div class="container py-5">
      <div class="row g-4">
        <!-- Brand -->
        <div class="col-lg-4 col-md-6">
          <a href="#" class="d-inline-block text-gradient fw-bold h4 mb-3">
            HMS
          </a>
          <p class="text-muted mb-4" style="max-width: 300px;">
            The most advanced hospital management system for modern healthcare facilities. Built with ❤️ for doctors, patients, and admins.
          </p>
          <div class="d-flex gap-3">
            <a href="#" class="social-icon text-muted">
              <Twitter class="icon" />
            </a>
            <a href="#" class="social-icon text-muted">
              <Github class="icon" />
            </a>
            <a href="#" class="social-icon text-muted">
              <Linkedin class="icon" />
            </a>
          </div>
        </div>

        <!-- Links -->
        <div class="col-lg-2 col-md-3 col-6">
          <h6 class="fw-semibold text-dark mb-3">Product</h6>
          <ul class="list-unstyled footer-links">
            <li><a href="#" class="text-muted text-decoration-none">Features</a></li>
            <li><a href="#" class="text-muted text-decoration-none">Pricing</a></li>
            <li><a href="#" class="text-muted text-decoration-none">Security</a></li>
            <li><a href="#" class="text-muted text-decoration-none">Roadmap</a></li>
          </ul>
        </div>

        <div class="col-lg-2 col-md-3 col-6">
          <h6 class="fw-semibold text-dark mb-3">Company</h6>
          <ul class="list-unstyled footer-links">
            <li><a href="#" class="text-muted text-decoration-none">About</a></li>
            <li><a href="#" class="text-muted text-decoration-none">Careers</a></li>
            <li><a href="#" class="text-muted text-decoration-none">Blog</a></li>
            <li><a href="#" class="text-muted text-decoration-none">Contact</a></li>
          </ul>
        </div>

        <div class="col-lg-2 col-md-3 col-6">
          <h6 class="fw-semibold text-dark mb-3">Legal</h6>
          <ul class="list-unstyled footer-links">
            <li><a href="#" class="text-muted text-decoration-none">Privacy</a></li>
            <li><a href="#" class="text-muted text-decoration-none">Terms</a></li>
            <li><a href="#" class="text-muted text-decoration-none">Cookie Policy</a></li>
            <li><a href="#" class="text-muted text-decoration-none">HIPAA</a></li>
          </ul>
        </div>
      </div>

      <hr class="my-4 border-top" />

      <div class="d-flex flex-column flex-md-row align-items-center justify-content-between gap-3">
        <div class="text-muted small">
          &copy; 2025 Hospital Management System. All rights reserved.
        </div>
        <div class="d-flex gap-4 small">
          <a href="#" class="text-muted text-decoration-none">Privacy Policy</a>
          <a href="#" class="text-muted text-decoration-none">Terms of Service</a>
        </div>
      </div>
    </div>
  </footer>
</template>

<script setup>
import { Twitter, Github, Linkedin } from 'lucide-vue-next'
</script>

<style scoped>
.footer {
  background: white;
  border-color: #e9ecef !important;
}

.text-gradient {
  background: linear-gradient(135deg, #0d6efd, #0dcaf0);
  -webkit-background-clip: text;
  background-clip: text;
  -webkit-text-fill-color: transparent;
}

.social-icon {
  transition: color 0.2s ease;
}

.social-icon:hover {
  color: #0d6efd !important;
}

.icon {
  width: 20px;
  height: 20px;
}

.footer-links li {
  margin-bottom: 0.5rem;
}

.footer-links a:hover {
  color: #0d6efd !important;
}
</style>
