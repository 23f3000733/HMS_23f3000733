<template>
  <div class="card-skeleton">
    <div class="card border-0 shadow-sm h-100">
      <div class="card-body p-4">
        <div class="d-flex justify-content-between align-items-center">
          <div style="flex: 1;">
            <div
              class="skeleton-box mb-2"
              style="height: 12px; width: 60%;"
            />
            <div
              class="skeleton-box"
              style="height: 32px; width: 40%;"
            />
          </div>
          <div class="skeleton-circle" />
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'CardSkeleton'
}
</script>

<style scoped>
.card-skeleton .skeleton-box,
.card-skeleton .skeleton-circle {
  background: linear-gradient(
    90deg,
    #f0f0f0 0%,
    #e0e0e0 50%,
    #f0f0f0 100%
  );
  background-size: 200% 100%;
  animation: shimmer 1.5s infinite;
  border-radius: 4px;
}

.skeleton-circle {
  width: 56px;
  height: 56px;
  border-radius: 50%;
  flex-shrink: 0;
}

@keyframes shimmer {
  0% {
    background-position: -200% 0;
  }
  100% {
    background-position: 200% 0;
  }
}
</style>
