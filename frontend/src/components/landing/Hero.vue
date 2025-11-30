<template>
  <section class="hero-wrapper position-relative overflow-hidden">
    <!-- Animated Background -->
    <div class="hero-background position-absolute w-100 h-100">
      <div class="gradient-orb orb-1"></div>
      <div class="gradient-orb orb-2"></div>
      <div class="gradient-orb orb-3"></div>
      <div class="grid-overlay"></div>
    </div>

    <div class="container position-relative">
      <div class="row align-items-center min-vh-75 py-5">
        <!-- Content Column -->
        <div 
          class="col-lg-6 text-center text-lg-start mb-5 mb-lg-0"
          v-motion
          :initial="{ opacity: 0, y: 30 }"
          :enter="{ opacity: 1, y: 0, transition: { duration: 900, delay: 100 } }"
        >
          <!-- Badge -->
          <div class="status-badge d-inline-flex align-items-center gap-2 mb-4">
            <span class="pulse-dot">
              <span class="pulse-ring"></span>
              <span class="pulse-core"></span>
            </span>
            <span class="badge-text">v2.0 Now Live</span>
          </div>
          
          <!-- Headline -->
          <h1 class="hero-headline mb-4">
            Modern Healthcare<br class="d-none d-lg-block" />
            <span class="gradient-text">Simplified.</span>
          </h1>
          
          <!-- Subheadline -->
          <p class="hero-subheadline text-muted mb-5">
            Experience the future of hospital management. Seamlessly connect doctors, patients, and administrators in one elegant platform.
          </p>
          
          <!-- CTA Buttons -->
          <div class="cta-group d-flex flex-column flex-sm-row justify-content-center justify-content-lg-start gap-3 mb-5">
            <router-link to="/register" class="btn-hero-primary">
              <span class="btn-content">Start Free Trial</span>
              <span class="btn-glow"></span>
            </router-link>
            <router-link to="/login" class="btn-hero-secondary">
              <span class="btn-content">View Demo</span>
            </router-link>
          </div>
          
          <!-- Trust Indicators -->
          <div class="trust-badges d-flex flex-wrap align-items-center justify-content-center justify-content-lg-start gap-4">
            <div class="trust-item d-flex align-items-center gap-2">
              <CheckCircle class="trust-icon" />
              <span class="trust-text">No credit card required</span>
            </div>
            <div class="trust-item d-flex align-items-center gap-2">
              <CheckCircle class="trust-icon" />
              <span class="trust-text">14-day free trial</span>
            </div>
          </div>
        </div>

        <!-- Visual Column -->
        <div 
          class="col-lg-6"
          v-motion
          :initial="{ opacity: 0, x: 30 }"
          :enter="{ opacity: 1, x: 0, transition: { duration: 900, delay: 300 } }"
        >
          <div class="dashboard-mockup position-relative">
            <!-- Main Dashboard Card -->
            <div class="mockup-card">
              <!-- Browser Bar -->
              <div class="browser-bar d-flex align-items-center gap-2 px-4 py-3">
                <span class="dot dot-red"></span>
                <span class="dot dot-yellow"></span>
                <span class="dot dot-green"></span>
              </div>
              
              <!-- Dashboard Content -->
              <div class="mockup-content p-4">
                <div class="row g-3">
                  <!-- Sidebar -->
                  <div class="col-4">
                    <div class="sidebar-item active mb-2"></div>
                    <div class="sidebar-item mb-2"></div>
                    <div class="sidebar-item mb-2"></div>
                    <div class="sidebar-item mb-2"></div>
                    <div class="metric-card mt-4">
                      <div class="metric-icon"></div>
                      <div class="metric-bar"></div>
                    </div>
                  </div>
                  
                  <!-- Main Area -->
                  <div class="col-8">
                    <!-- Stats Cards -->
                    <div class="row g-2 mb-3">
                      <div class="col-6">
                        <div class="stat-card stat-primary">
                          <div class="stat-icon"></div>
                          <div class="stat-value"></div>
                        </div>
                      </div>
                      <div class="col-6">
                        <div class="stat-card stat-success">
                          <div class="stat-icon"></div>
                          <div class="stat-value"></div>
                        </div>
                      </div>
                    </div>
                    
                    <!-- Chart -->
                    <div class="chart-container">
                      <div class="chart-bars d-flex align-items-end justify-content-between h-100 px-3 pb-2">
                        <div class="bar" style="height: 45%"></div>
                        <div class="bar" style="height: 75%"></div>
                        <div class="bar" style="height: 55%"></div>
                        <div class="bar" style="height: 90%"></div>
                        <div class="bar" style="height: 65%"></div>
                        <div class="bar" style="height: 80%"></div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <!-- Floating Stat Cards -->
            <div class="floating-stat stat-1 animate-float">
              <div class="d-flex align-items-center gap-3">
                <div class="float-icon bg-success-subtle">
                  <Activity class="icon" />
                </div>
                <div class="flex-grow-1">
                  <div class="float-label">Daily Patients</div>
                  <div class="float-value">+128</div>
                </div>
              </div>
            </div>

            <div class="floating-stat stat-2 animate-float">
              <div class="d-flex align-items-center gap-3">
                <div class="float-icon bg-primary-subtle">
                  <Users class="icon" />
                </div>
                <div class="flex-grow-1">
                  <div class="float-label">Active Doctors</div>
                  <div class="float-value">48</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup>
import { CheckCircle, Activity, Users } from 'lucide-vue-next'
</script>

<style scoped>
/* Hero Section */
.hero-wrapper {
  min-height: 100vh;
  display: flex;
  align-items: center;
  padding-top: 6rem;
  padding-bottom: 4rem;
}

.min-vh-75 {
  min-height: 75vh;
}

/* Background */
.hero-background {
  top: 0;
  left: 0;
  pointer-events: none;
}

.gradient-orb {
  position: absolute;
  border-radius: 50%;
  filter: blur(100px);
  opacity: 0.5;
  animation: float-slow 20s infinite ease-in-out;
}

.orb-1 {
  width: 500px;
  height: 500px;
  background: linear-gradient(135deg, rgba(13, 110, 253, 0.3), rgba(13, 202, 240, 0.2));
  top: -10%;
  left: -5%;
  animation-delay: 0s;
}

.orb-2 {
  width: 400px;
  height: 400px;
  background: linear-gradient(135deg, rgba(111, 66, 193, 0.25), rgba(220, 53, 69, 0.15));
  top: 20%;
  right: -5%;
  animation-delay: 5s;
}

.orb-3 {
  width: 350px;
  height: 350px;
  background: linear-gradient(135deg, rgba(13, 202, 240, 0.2), rgba(32, 201, 151, 0.2));
  bottom: 10%;
  left: 30%;
  animation-delay: 10s;
}

@keyframes float-slow {
  0%, 100% { transform: translate(0, 0) scale(1); }
  33% { transform: translate(20px, -30px) scale(1.05); }
  66% { transform: translate(-15px, 20px) scale(0.95); }
}

.grid-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-image: 
    linear-gradient(rgba(13, 110, 253, 0.02) 1px, transparent 1px),
    linear-gradient(90deg, rgba(13, 110, 253, 0.02) 1px, transparent 1px);
  background-size: 50px 50px;
  opacity: 0.5;
}

/* Status Badge */
.status-badge {
  padding: 0.5rem 1rem;
  background: linear-gradient(135deg, rgba(13, 110, 253, 0.08), rgba(13, 202, 240, 0.08));
  border: 1px solid rgba(13, 110, 253, 0.15);
  border-radius: 50rem;
  backdrop-filter: blur(10px);
}

.pulse-dot {
  position: relative;
  width: 8px;
  height: 8px;
}

.pulse-ring {
  position: absolute;
  width: 100%;
  height: 100%;
  border-radius: 50%;
  background: #0d6efd;
  opacity: 0.75;
  animation: pulse-ring 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
}

.pulse-core {
  position: absolute;
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #0d6efd;
}

@keyframes pulse-ring {
  0% { transform: scale(1); opacity: 0.75; }
  100% { transform: scale(2); opacity: 0; }
}

.badge-text {
  font-size: 0.8125rem;
  font-weight: 600;
  color: #0d6efd;
  letter-spacing: 0.5px;
  text-transform: uppercase;
}

/* Typography */
.hero-headline {
  font-size: clamp(2.5rem, 5vw, 4.5rem);
  font-weight: 800;
  line-height: 1.1;
  letter-spacing: -0.02em;
  color: #1a1a1a;
  margin-bottom: 1.5rem;
}

.gradient-text {
  background: linear-gradient(135deg, #0d6efd 0%, #0dcaf0 100%);
  -webkit-background-clip: text;
  background-clip: text;
  -webkit-text-fill-color: transparent;
  display: inline-block;
}

.hero-subheadline {
  font-size: clamp(1.125rem, 2vw, 1.375rem);
  line-height: 1.6;
  color: #6c757d;
  max-width: 540px;
  margin-left: auto;
  margin-right: auto;
}

@media (min-width: 992px) {
  .hero-subheadline {
    margin-left: 0;
  }
}

/* CTA Buttons */
.btn-hero-primary {
  position: relative;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 1rem 2.5rem;
  font-size: 1.0625rem;
  font-weight: 600;
  color: white;
  background: linear-gradient(135deg, #0d6efd 0%, #0b5ed7 100%);
  border: none;
  border-radius: 50rem;
  text-decoration: none;
  overflow: hidden;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 0 8px 24px rgba(13, 110, 253, 0.25);
}

.btn-hero-primary:hover {
  transform: translateY(-3px);
  box-shadow: 0 12px 32px rgba(13, 110, 253, 0.4);
  color: white;
}

.btn-glow {
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.4), transparent);
}

.btn-hero-primary:hover .btn-glow {
  animation: button-glow 1s ease;
}

@keyframes button-glow {
  to { left: 100%; }
}

.btn-hero-secondary {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 1rem 2.5rem;
  font-size: 1.0625rem;
  font-weight: 600;
  color: #495057;
  background: white;
  border: 2px solid #e9ecef;
  border-radius: 50rem;
  text-decoration: none;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
}

.btn-hero-secondary:hover {
  transform: translateY(-3px);
  border-color: #0d6efd;
  color: #0d6efd;
  box-shadow: 0 8px 20px rgba(13, 110, 253, 0.15);
}

/* Trust Indicators */
.trust-item {
  font-size: 0.9375rem;
}

.trust-icon {
  width: 18px;
  height: 18px;
  color: #20c997;
}

.trust-text {
  color: #6c757d;
  font-weight: 500;
}

/* Dashboard Mockup */
.mockup-card {
  background: white;
  border-radius: 20px;
  box-shadow: 
    0 0 0 1px rgba(0, 0, 0, 0.04),
    0 20px 60px rgba(0, 0, 0, 0.12);
  overflow: hidden;
  transform: perspective(1500px) rotateY(-2deg);
  transition: transform 0.5s ease;
}

.mockup-card:hover {
  transform: perspective(1500px) rotateY(0deg);
}

.browser-bar {
  background: #f8f9fa;
  border-bottom: 1px solid #e9ecef;
}

.dot {
  width: 12px;
  height: 12px;
  border-radius: 50%;
}

.dot-red { background: #ff5f57; }
.dot-yellow { background: #ffbd2e; }
.dot-green { background: #28c840; }

.mockup-content {
  background: linear-gradient(135deg, #f8f9fa 0%, #ffffff 100%);
  min-height: 300px;
}

/* Sidebar Items */
.sidebar-item {
  height: 32px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.06);
  transition: all 0.3s ease;
}

.sidebar-item.active {
  background: linear-gradient(135deg, #0d6efd 0%, #0b5ed7 100%);
}

.metric-card {
  padding: 1rem;
  background: rgba(13, 110, 253, 0.05);
  border: 1px solid rgba(13, 110, 253, 0.1);
  border-radius: 12px;
}

.metric-icon {
  width: 32px;
  height: 32px;
  background: linear-gradient(135deg, #0d6efd 0%, #0dcaf0 100%);
  border-radius: 8px;
  margin-bottom: 0.5rem;
}

.metric-bar {
  height: 8px;
  background: #e9ecef;
  border-radius: 4px;
  position: relative;
  overflow: hidden;
}

.metric-bar::after {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 70%;
  height: 100%;
  background: linear-gradient(90deg, #0d6efd, #0dcaf0);
  border-radius: 4px;
}

/* Stat Cards */
.stat-card {
  padding: 1rem;
  border-radius: 12px;
  background: white;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}

.stat-icon {
  width: 32px;
  height: 32px;
  border-radius: 8px;
  margin-bottom: 0.5rem;
}

.stat-primary .stat-icon {
  background: rgba(13, 110, 253, 0.1);
}

.stat-success .stat-icon {
  background: rgba(32, 201, 151, 0.1);
}

.stat-value {
  height: 12px;
  width: 60%;
  background: #e9ecef;
  border-radius: 4px;
}

/* Chart */
.chart-container {
  background: white;
  border-radius: 12px;
  height: 140px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}

.bar {
  flex: 1;
  background: linear-gradient(180deg, #0dcaf0, #0d6efd);
  border-radius: 4px 4px 0 0;
  animation: bar-grow 1s ease-out backwards;
}

.bar:nth-child(1) { animation-delay: 0.1s; }
.bar:nth-child(2) { animation-delay: 0.2s; }
.bar:nth-child(3) { animation-delay: 0.3s; }
.bar:nth-child(4) { animation-delay: 0.4s; }
.bar:nth-child(5) { animation-delay: 0.5s; }
.bar:nth-child(6) { animation-delay: 0.6s; }

@keyframes bar-grow {
  from { transform: scaleY(0); }
  to { transform: scaleY(1); }
}

/* Floating Stats */
.floating-stat {
  position: absolute;
  background: white;
  padding: 1rem 1.25rem;
  border-radius: 16px;
  box-shadow: 0 12px 40px rgba(0, 0, 0, 0.12);
  border: 1px solid rgba(0, 0, 0, 0.04);
  z-index: 2;
  min-width: 200px;
}

.stat-1 {
  top: 10%;
  right: -10%;
  animation-delay: 1s;
}

.stat-2 {
  bottom: 15%;
  left: -10%;
  animation-delay: 2s;
}

.float-icon {
  width: 44px;
  height: 44px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.icon {
  width: 22px;
  height: 22px;
}

.bg-success-subtle {
  background: rgba(32, 201, 151, 0.12);
  color: #20c997;
}

.bg-primary-subtle {
  background: rgba(13, 110, 253, 0.12);
  color: #0d6efd;
}

.float-label {
  font-size: 0.8125rem;
  color: #6c757d;
  font-weight: 500;
  margin-bottom: 0.25rem;
}

.float-value {
  font-size: 1.25rem;
  font-weight: 700;
  color: #1a1a1a;
}

.animate-float {
  animation: gentle-float 6s ease-in-out infinite;
}

@keyframes gentle-float {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-15px); }
}

/* Responsive */
@media (max-width: 991.98px) {
  .hero-wrapper {
    padding-top: 5rem;
  }
  
  .stat-1, .stat-2 {
    position: static;
    margin-top: 1rem;
  }
  
  .mockup-card {
    transform: none;
  }
}
</style>
