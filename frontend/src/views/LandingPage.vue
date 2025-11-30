<template>
  <div class="min-h-screen bg-white font-sans text-slate-900 selection:bg-blue-100 selection:text-blue-900">
    <Navbar />
    
    <main>
      <Hero />
      <Stats />
      <Features />
      <Testimonials />
      <FAQ />
      <CTA />
    </main>

    <Footer />
  </div>
</template>

<script setup>
import Navbar from '@/components/landing/Navbar.vue'
import Hero from '@/components/landing/Hero.vue'
import Stats from '@/components/landing/Stats.vue'
import Features from '@/components/landing/Features.vue'
import Testimonials from '@/components/landing/Testimonials.vue'
import FAQ from '@/components/landing/FAQ.vue'
import CTA from '@/components/landing/CTA.vue'
import Footer from '@/components/landing/Footer.vue'
</script>

<style>
html {
  scroll-behavior: smooth;
}
</style>
