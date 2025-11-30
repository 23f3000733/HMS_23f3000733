<template>
  <nav
    class="navbar-custom fixed-top"
    :class="{ 'scrolled': isScrolled }"
  >
    <div class="container">
      <div class="navbar-content d-flex align-items-center justify-content-between">
        <!-- Logo -->
        <a href="#" class="logo-link">
          <span class="logo-text">HMS</span>
        </a>

        <!-- Desktop Navigation -->
        <div class="nav-menu d-none d-lg-flex align-items-center gap-4">
          <a 
            v-for="link in links" 
            :key="link.name" 
            :href="link.href" 
            class="nav-item"
          >
            {{ link.name }}
          </a>
        </div>

        <!-- Auth Buttons Desktop -->
        <div class="auth-buttons d-none d-lg-flex align-items-center gap-3">
          <router-link to="/login" class="btn-link">
            Log In
          </router-link>
          <router-link to="/register" class="btn-primary-custom">
            Get Started
            <span class="btn-shine"></span>
          </router-link>
        </div>

        <!-- Mobile Menu Toggle -->
        <button 
          @click="toggleMenu" 
          class="mobile-toggle d-lg-none"
          :class="{ 'active': isOpen }"
        >
          <span class="hamburger-line"></span>
          <span class="hamburger-line"></span>
          <span class="hamburger-line"></span>
        </button>
      </div>

      <!-- Mobile Menu -->
      <transition name="mobile-menu">
        <div v-if="isOpen" class="mobile-menu d-lg-none">
          <div class="mobile-menu-content">
            <a
              v-for="link in links"
              :key="link.name"
              :href="link.href"
              class="mobile-nav-item"
              @click="closeMenu"
            >
              {{ link.name }}
            </a>
            <div class="mobile-divider"></div>
            <router-link to="/login" class="mobile-nav-item" @click="closeMenu">
              Log In
            </router-link>
            <router-link to="/register" class="btn-primary-mobile" @click="closeMenu">
              Get Started
            </router-link>
          </div>
        </div>
      </transition>
    </div>
  </nav>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'

const isOpen = ref(false)
const isScrolled = ref(false)

const links = [
  { name: 'Features', href: '#features' },
  { name: 'Testimonials', href: '#testimonials' },
  { name: 'FAQ', href: '#faq' },
  { name: 'Contact', href: '#contact' }
]

const toggleMenu = () => {
  isOpen.value = !isOpen.value
  if (isOpen.value) {
    document.body.style.overflow = 'hidden'
  } else {
    document.body.style.overflow = ''
  }
}

const closeMenu = () => {
  isOpen.value = false
  document.body.style.overflow = ''
}

const handleScroll = () => {
  isScrolled.value = window.scrollY > 20
}

onMounted(() => {
  window.addEventListener('scroll', handleScroll)
})

onUnmounted(() => {
  window.removeEventListener('scroll', handleScroll)
  document.body.style.overflow = ''
})
</script>

<style scoped>
/* Navbar Base */
.navbar-custom {
  padding: 1.25rem 0;
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
  z-index: 1000;
  background: transparent;
}

.navbar-custom.scrolled {
  padding: 0.875rem 0;
  background: rgba(255, 255, 255, 0.92);
  backdrop-filter: blur(20px) saturate(180%);
  -webkit-backdrop-filter: blur(20px) saturate(180%);
  border-bottom: 1px solid rgba(0, 0, 0, 0.04);
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.02);
}

/* Logo */
.logo-link {
  text-decoration: none;
  position: relative;
}

.logo-text {
  font-size: 1.75rem;
  font-weight: 800;
  letter-spacing: -0.5px;
  background: linear-gradient(135deg, #0d6efd 0%, #0dcaf0 100%);
  -webkit-background-clip: text;
  background-clip: text;
  -webkit-text-fill-color: transparent;
  transition: all 0.3s ease;
}

.logo-link:hover .logo-text {
  transform: scale(1.05);
}

/* Navigation Items */
.nav-item {
  position: relative;
  font-size: 0.9375rem;
  font-weight: 500;
  color: #495057;
  text-decoration: none;
  transition: color 0.3s ease;
  padding: 0.5rem 0;
}

.nav-item::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 0;
  width: 0;
  height: 2px;
  background: linear-gradient(90deg, #0d6efd, #0dcaf0);
  transition: width 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.nav-item:hover {
  color: #0d6efd;
}

.nav-item:hover::after {
  width: 100%;
}

/* Buttons */
.btn-link {
  font-size: 0.9375rem;
  font-weight: 500;
  color: #495057;
  text-decoration: none;
  transition: color 0.3s ease;
  padding: 0.5rem 1rem;
}

.btn-link:hover {
  color: #0d6efd;
}

.btn-primary-custom {
  position: relative;
  display: inline-flex;
  align-items: center;
  padding: 0.625rem 1.5rem;
  font-size: 0.9375rem;
  font-weight: 600;
  color: white;
  background: linear-gradient(135deg, #0d6efd 0%, #0b5ed7 100%);
  border-radius: 50rem;
  text-decoration: none;
  overflow: hidden;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 0 4px 12px rgba(13, 110, 253, 0.2);
}

.btn-primary-custom:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(13, 110, 253, 0.35);
  color: white;
}

.btn-shine {
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.3), transparent);
}

.btn-primary-custom:hover .btn-shine {
  animation: shine 0.8s ease;
}

@keyframes shine {
  to { left: 100%; }
}

/* Mobile Toggle */
.mobile-toggle {
  width: 32px;
  height: 32px;
  background: none;
  border: none;
  padding: 0;
  display: flex;
  flex-direction: column;
  justify-content: center;
  gap: 5px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.hamburger-line {
  width: 100%;
  height: 2px;
  background: #495057;
  border-radius: 2px;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.mobile-toggle.active .hamburger-line:nth-child(1) {
  transform: translateY(7px) rotate(45deg);
}

.mobile-toggle.active .hamburger-line:nth-child(2) {
  opacity: 0;
}

.mobile-toggle.active .hamburger-line:nth-child(3) {
  transform: translateY(-7px) rotate(-45deg);
}

/* Mobile Menu */
.mobile-menu {
  position: absolute;
  top: 100%;
  left: 0;
  right: 0;
  background: white;
  border-bottom: 1px solid rgba(0, 0, 0, 0.04);
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.1);
}

.mobile-menu-content {
  padding: 1.5rem;
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.mobile-nav-item {
  font-size: 1rem;
  font-weight: 500;
  color: #495057;
  text-decoration: none;
  padding: 0.75rem 0;
  transition: color 0.3s ease;
}

.mobile-nav-item:hover {
  color: #0d6efd;
}

.mobile-divider {
  height: 1px;
  background: #e9ecef;
  margin: 0.5rem 0;
}

.btn-primary-mobile {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 0.875rem 1.5rem;
  font-size: 0.9375rem;
  font-weight: 600;
  color: white;
  background: linear-gradient(135deg, #0d6efd 0%, #0b5ed7 100%);
  border-radius: 50rem;
  text-decoration: none;
  margin-top: 0.5rem;
  box-shadow: 0 4px 12px rgba(13, 110, 253, 0.2);
}

/* Transitions */
.mobile-menu-enter-active,
.mobile-menu-leave-active {
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.mobile-menu-enter-from {
  opacity: 0;
  transform: translateY(-20px);
}

.mobile-menu-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}
</style>
