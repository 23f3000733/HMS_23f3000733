<template>
  <div id="app">
    <Navbar v-if="showNavbar" />
    <router-view v-slot="{ Component }">
      <transition
        name="fade"
        mode="out-in"
      >
        <component :is="Component" />
      </transition>
    </router-view>
  </div>
</template>

<script>
import Navbar from './components/Navbar.vue'

export default {
  name: 'App',
  components: {
    Navbar
  },
  computed: {
    showNavbar() {
      // Hide navbar on login and register pages
      const hideOn = ['/login', '/register', '/']
      return !hideOn.includes(this.$route.path)
    }
  }
}
</script>

<style>
/* Page transition animations are handled by global-theme.css */
</style>
