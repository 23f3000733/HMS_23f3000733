<template>
  <div class="toast-container position-fixed top-0 end-0 p-3" style="z-index: 9999;">
    <transition-group name="toast-slide">
      <div
        v-for="toast in toasts"
        :key="toast.id"
        class="toast show align-items-center border-0 mb-2"
        :class="`text-bg-${toast.type}`"
        role="alert"
        aria-live="assertive"
        aria-atomic="true"
      >
        <div class="d-flex">
          <div class="toast-body d-flex align-items-center">
            <i
              class="bi me-2"
              :class="{
                'bi-check-circle-fill': toast.type === 'success',
                'bi-x-circle-fill': toast.type === 'danger',
                'bi-info-circle-fill': toast.type === 'info',
                'bi-exclamation-triangle-fill': toast.type === 'warning'
              }"
            ></i>
            {{ toast.message }}
          </div>
          <button
            type="button"
            class="btn-close btn-close-white me-2 m-auto"
            @click="removeToast(toast.id)"
          ></button>
        </div>
      </div>
    </transition-group>
  </div>
</template>

<script>
import { useToast } from '@/composables/useToast'

export default {
  name: 'ToastContainer',
  setup() {
    const { toasts, removeToast } = useToast()
    return { toasts, removeToast }
  }
}
</script>

<style scoped>
.toast {
  min-width: 280px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  border-radius: 8px;
}

.toast-slide-enter-active {
  transition: all 0.3s ease-out;
}
.toast-slide-leave-active {
  transition: all 0.2s ease-in;
}
.toast-slide-enter-from {
  transform: translateX(100%);
  opacity: 0;
}
.toast-slide-leave-to {
  transform: translateX(100%);
  opacity: 0;
}
</style>
