import { reactive } from 'vue'

const state = reactive({
    toasts: []
})

let idCounter = 0

function addToast(message, type = 'info', duration = 4000) {
    const id = ++idCounter
    state.toasts.push({ id, message, type, visible: true })
    setTimeout(() => {
        removeToast(id)
    }, duration)
}

function removeToast(id) {
    const index = state.toasts.findIndex(t => t.id === id)
    if (index !== -1) {
        state.toasts.splice(index, 1)
    }
}

export function useToast() {
    return {
        toasts: state.toasts,
        showSuccess: (msg) => addToast(msg, 'success'),
        showError: (msg) => addToast(msg, 'danger', 6000),
        showInfo: (msg) => addToast(msg, 'info'),
        showWarning: (msg) => addToast(msg, 'warning'),
        removeToast
    }
}
