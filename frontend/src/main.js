import { createApp } from 'vue'
import { createPinia } from 'pinia'
import { MotionPlugin } from '@vueuse/motion'

import App from './App.vue'
import router from './router'
import { useAuthStore } from './stores/auth' // Keep this import as it's used later

import 'bootstrap/dist/css/bootstrap.min.css'
import 'bootstrap' // Changed from 'bootstrap/dist/js/bootstrap.bundle.min.js'
import 'bootstrap-icons/font/bootstrap-icons.css'
import './assets/main.css'

const app = createApp(App)

app.use(createPinia()) // Changed from separate pinia constant
app.use(router)
app.use(MotionPlugin) // Added MotionPlugin

app.mount('#app')

// Initialize auth state from localStorage (moved after app.mount)
const authStore = useAuthStore()
authStore.initializeAuth()
