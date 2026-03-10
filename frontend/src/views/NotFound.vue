<template>
  <div class="not-found d-flex flex-column align-items-center justify-content-center min-vh-100 bg-light text-center px-3">
    <div class="mb-4">
      <i class="bi bi-exclamation-triangle display-1 text-warning"></i>
    </div>
    <h1 class="display-4 fw-bold text-dark mb-2">404</h1>
    <p class="lead text-muted mb-4">The page you're looking for doesn't exist.</p>
    <router-link to="/" class="btn btn-primary btn-lg px-4 shadow-sm">
      <i class="bi bi-house me-2"></i>Go Home
    </router-link>
  </div>
</template>

<script>
export default {
  name: 'NotFound'
}
</script>
