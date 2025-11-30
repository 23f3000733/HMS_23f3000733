<template>
  <Transition name="modal">
    <div
      v-if="modelValue"
      class="modal-overlay"
      @click="handleOverlayClick"
    >
      <div
        class="modal-container"
        :class="modalSize"
        role="dialog"
        aria-modal="true"
        :aria-labelledby="titleId"
      >
        <!-- Header -->
        <div class="modal-header">
          <h5
            :id="titleId"
            class="modal-title"
          >
            <slot name="header">
              {{ title }}
            </slot>
          </h5>
          <button 
            type="button" 
            class="btn-close" 
            aria-label="Close"
            @click="close"
          />
        </div>

        <!-- Body -->
        <div class="modal-body">
          <slot />
        </div>

        <!-- Footer -->
        <div
          v-if="$slots.footer || showDefaultFooter"
          class="modal-footer"
        >
          <slot name="footer">
            <button
              type="button"
              class="btn btn-secondary"
              @click="close"
            >
              Cancel
            </button>
            <button
              type="button"
              class="btn btn-primary"
              @click="confirm"
            >
              {{ confirmText }}
            </button>
          </slot>
        </div>
      </div>
    </div>
  </Transition>
</template>

<script>
export default {
  name: 'Modal',
  props: {
    modelValue: {
      type: Boolean,
      required: true
    },
    title: {
      type: String,
      default: ''
    },
    size: {
      type: String,
      default: 'medium',
      validator: (value) => ['small', 'medium', 'large', 'xl'].includes(value)
    },
    showDefaultFooter: {
      type: Boolean,
      default: true
    },
    confirmText: {
      type: String,
      default: 'Confirm'
    },
    closeOnOverlay: {
      type: Boolean,
      default: true
    }
  },
  data(){
    return {
      uniqueId: Math.random().toString(36).substr(2, 9)

    }
  },

  computed: {
    modalSize() {
      return `modal-${this.size}`
    },
    titleId() {
      return `modal-title-${this.uniqueId}`
    }
  },
  watch: {
    modelValue(newVal) {
      if (newVal) {
        this.trapFocus()
        document.body.style.overflow = 'hidden'
        document.addEventListener('keydown', this.handleEscape)
      } else {
        document.body.style.overflow = ''
        document.removeEventListener('keydown', this.handleEscape)
      }
    }
  },
  beforeUnmount() {
    document.body.style.overflow = ''
    document.removeEventListener('keydown', this.handleEscape)
  },
  methods: {
    close() {
      this.$emit('update:modelValue', false)
      this.$emit('close')
    },
    confirm() {
      this.$emit('confirm')
    },
    handleOverlayClick(event) {
      if (this.closeOnOverlay && event.target.classList.contains('modal-overlay')) {
        this.close()
      }
    },
    handleEscape(event) {
      if (event.key === 'Escape') {
        this.close()
      }
    },
    trapFocus() {
      this.$nextTick(() => {
        const focusableElements = this.$el.querySelectorAll(
          'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
        )
        if (focusableElements.length > 0) {
          focusableElements[0].focus()
        }
      })
    }
  }
}
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1050;
}

.modal-container {
  background: white;
  border-radius: 0.5rem;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.2);
  max-height: 90vh;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
}

.modal-small { width: 400px; max-width: 90vw; }
.modal-medium { width: 600px; max-width: 90vw; }
.modal-large { width: 800px; max-width: 90vw; }
.modal-xl { width: 1200px; max-width: 95vw; }

.modal-header {
  padding: 1rem 1.5rem;
  border-bottom: 1px solid #dee2e6;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.modal-title {
  margin: 0;
  font-size: 1.25rem;
  font-weight: 600;
}

.modal-body {
  padding: 1.5rem;
  flex: 1;
}

.modal-footer {
  padding: 1rem 1.5rem;
  border-top: 1px solid #dee2e6;
  display: flex;
  justify-content: flex-end;
  gap: 0.5rem;
}

/* Transition */
.modal-enter-active,
.modal-leave-active {
  transition: opacity 0.3s ease;
}

.modal-enter-from,
.modal-leave-to {
  opacity: 0;
}

.modal-enter-active .modal-container,
.modal-leave-active .modal-container {
  transition: transform 0.3s ease;
}

.modal-enter-from .modal-container,
.modal-leave-to .modal-container {
  transform: scale(0.9);
}
</style>
