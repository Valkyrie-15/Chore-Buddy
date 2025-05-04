<template>
  <div class="landing-page vh-100 d-flex flex-column">
    <!-- Background Geometric Shapes -->
    <div class="bg-shapes">
      <div class="shape shape-1"></div>
      <div class="shape shape-2"></div>
      <div class="shape shape-3"></div>
    </div>
    
    <!-- Main Content -->
    <div class="container-fluid flex-grow-1 d-flex align-items-center justify-content-center">
      <div class="row w-100 align-items-center text-center text-md-start">
        <div class="col-md-6 illustration-slide">
          <div class="illustration-wrapper position-relative">
            <img 
              src="@/assets/download.png" 
              alt="Business Transformation Illustration" 
              class="img-fluid illustration-animation"
            />
          </div>
        </div>
        <div class="col-md-6 description-slide">
          <h1 class="display-4 fw-bold mb-3 text-primary">Looking for reliable home services?</h1>
          <p class="lead mb-4 text-secondary">
            Our app connects you with trusted professionals for cleaning, repairs, plumbing, electrical work, and more—right at your doorstep. Book effortlessly, track your service, and enjoy hassle-free home maintenance. Get started today!
          </p>
          <div class="button-group">
            <router-link 
              to="/login" 
              class="btn btn-gradient login-btn me-2 hover-lift"
            >
              Login
            </router-link>
            <router-link 
              to="/signup" 
              class="btn btn-gradient signup-btn hover-lift"
            >
              Sign Up
            </router-link>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
// No additional setup required
</script>

<style scoped>
:root {
  /* Primary color palette */
  --primary-color: #8a4fff;
  --secondary-color: #ff6b9e;
  --accent-color: #4ecdc4;
  
  /* Deeper lavender background colors */
  --bg-primary: #a98ade;   /* Deeper lavender */
  --bg-secondary: #c3adee; /* Slightly lighter lavender */
  
  --text-primary: #4a4a4a;
  --text-secondary: #6a6a6a;
}

.landing-page {
  background: linear-gradient(135deg, var(--bg-primary) 0%, var(--bg-secondary) 100%);
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  overflow: hidden;
}

/* Background shapes */
.bg-shapes {
  position: absolute;
  width: 100%;
  height: 100%;
  z-index: 0;
}

.shape {
  position: absolute;
  border-radius: 50%;
  opacity: 0.15;
  filter: blur(40px);
  animation-duration: 15s;
  animation-iteration-count: infinite;
  animation-timing-function: ease-in-out;
}

.shape-1 {
  background: var(--secondary-color);
  width: 300px;
  height: 300px;
  top: -100px;
  right: 10%;
  animation-name: float-1;
}

.shape-2 {
  background: var(--accent-color);
  width: 200px;
  height: 200px;
  bottom: -50px;
  left: 10%;
  animation-name: float-2;
}

.shape-3 {
  background: var(--primary-color);
  width: 350px;
  height: 350px;
  bottom: 20%;
  right: -100px;
  animation-name: float-3;
}

@keyframes float-1 {
  0%, 100% { transform: translate(0, 0); }
  50% { transform: translate(30px, 20px); }
}

@keyframes float-2 {
  0%, 100% { transform: translate(0, 0); }
  50% { transform: translate(-20px, 30px); }
}

@keyframes float-3 {
  0%, 100% { transform: translate(0, 0); }
  50% { transform: translate(-15px, -25px); }
}

/* Illustration animation */
.illustration-animation {
  animation: image-float 6s ease-in-out infinite;
}

@keyframes image-float {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-15px); }
}

/* Column animations */
.illustration-slide {
  animation: slide-in-left 1s ease-out;
}

.description-slide {
  animation: slide-in-right 1s ease-out;
}

@keyframes slide-in-left {
  from { transform: translateX(-50px); opacity: 0; }
  to { transform: translateX(0); opacity: 1; }
}

@keyframes slide-in-right {
  from { transform: translateX(50px); opacity: 0; }
  to { transform: translateX(0); opacity: 1; }
}

/* Button Styles */
.button-group {
  display: flex;
  flex-wrap: wrap;
}

.btn-gradient {
  padding: 12px 24px;
  border-radius: 30px;
  border: none;
  font-weight: 600;
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
  color: rgb(33, 31, 31) !important;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
}

.login-btn {
  background: linear-gradient(135deg, var(--primary-color) 0%, #7940e6 100%);
}

.signup-btn {
  background: linear-gradient(135deg, var(--secondary-color) 0%, #e54b81 100%);
}

.hover-lift:hover {
  transform: translateY(-5px);
  box-shadow: 0 10px 20px rgba(0, 0, 0, 0.15);
}

/* Add shimmer effect to buttons */
.btn-gradient::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.3), transparent);
  transition: left 0.7s;
}

.btn-gradient:hover::before {
  left: 100%;
}

/* Responsive adjustments */
@media (max-width: 768px) {
  .button-group {
    justify-content: center;
    gap: 10px;
  }
  
  .btn-gradient {
    margin-bottom: 10px;
  }
}
</style>