<template>
  <div class="app-wrapper position-relative overflow-hidden">
    <!-- Background Geometric Shapes -->
    <div class="bg-shapes">
      <div class="shape shape-1"></div>
      <div class="shape shape-2"></div>
      <div class="shape shape-3"></div>
    </div>

    <nav class="navbar navbar-expand-lg navbar-light sticky-top">
      <div class="container-fluid">
        <a class="navbar-brand" href="#">
          <img :src="require('@/assets/logo.png')" alt="Logo" height="30" class="me-2 logo-animation">
        </a>

        <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
          <span class="navbar-toggler-icon"></span>
        </button>

        <div class="collapse navbar-collapse" id="navbarNav">
          <!-- Customer Navbar -->
          <ul v-if="userRole === 'customer'" class="navbar-nav me-auto">
            <li class="nav-item">
              <router-link class="nav-link" to="/cust-dashboard" active-class="active">
                <i class="fas fa-home me-2"></i>Dashboard
              </router-link>
            </li>
            
            <li class="nav-item">
              <router-link class="nav-link" to="/book-service" active-class="active">
                <i class="fas fa-calendar-plus me-2"></i>Book Service
              </router-link>
            </li>
            <li class="nav-item">
              <router-link class="nav-link" to="/my-bookings" active-class="active">
                <i class="fas fa-calendar-check me-2"></i>My Bookings
              </router-link>
            </li>
          </ul>

          <!-- Professional Navbar -->
          <ul v-if="userRole === 'professional'" class="navbar-nav me-auto">
            <li class="nav-item">
              <router-link class="nav-link" to="/pro-dashboard" active-class="active">
                <i class="fas fa-tachometer-alt me-2"></i>Dashboard
              </router-link>
            </li>
            <li class="nav-item">
              <router-link class="nav-link" to="/my-jobs" active-class="active">
                <i class="fas fa-briefcase me-2"></i>My Jobs
              </router-link>
            </li>
            <li class="nav-item">
              <router-link class="nav-link" :to="`/professional/${user.id}/reviews`" active-class="active">
                <i class="fas fa-star me-2"></i>Reviews
              </router-link>
            </li>
            <li class="nav-item">
              <router-link class="nav-link" to="/earnings" active-class="active">
                <i class="fas fa-dollar-sign me-2"></i>Earnings
              </router-link>
            </li>
          </ul>

          <!-- Admin Navbar -->
          <ul v-if="userRole === 'admin'" class="navbar-nav me-auto">
            <li class="nav-item">
              <router-link class="nav-link" to="/admin-dashboard" active-class="active">
                <i class="fas fa-chart-line me-2"></i>Dashboard
              </router-link>
            </li>
            <li class="nav-item">
              <router-link class="nav-link" to="/admin-users" active-class="active">
                <i class="fas fa-users me-2"></i>Users
              </router-link>
            </li>
            <li class="nav-item">
              <router-link class="nav-link" to="/services" active-class="active">
                <i class="fas fa-concierge-bell me-2"></i>Services
              </router-link>
            </li>
          </ul>

          <!-- Unauthenticated Navbar -->
          <ul v-if="!isAuthenticated" class="navbar-nav me-auto">
            <li class="nav-item">
              <router-link class="nav-link" to="/" active-class="active">
                <i class="fas fa-home me-2"></i>Home
              </router-link>
            </li>
            <li class="nav-item">
              <router-link class="nav-link" to="/" active-class="active">
                <i class="fas fa-sign-in-alt me-2"></i>Learn More
              </router-link>
            </li>
            <li class="nav-item">
              <router-link class="nav-link" to="/" active-class="active">
                <i class="fas fa-user-plus me-2"></i>Contact
              </router-link>
            </li>
          </ul>

          <!-- User Dropdown (replacing the previous logout button) -->
          <ul v-if="isAuthenticated" class="navbar-nav ms-auto">
            <li class="nav-item dropdown">
              <a class="nav-link dropdown-toggle user-dropdown" href="#" id="userDropdown" role="button" 
                 data-bs-toggle="dropdown" aria-expanded="false">
                <i class="fas fa-user-circle me-1"></i>User
              </a>
              <ul class="dropdown-menu dropdown-menu-end" aria-labelledby="userDropdown">
                <li>
                  <router-link class="dropdown-item" :to="getUserProfilePath">
                    <i class="fas fa-user me-2"></i>Profile
                  </router-link>
                </li>
                <li><hr class="dropdown-divider"></li>
                <li>
                  <a class="dropdown-item logout-link" @click="handleLogout">
                    <i class="fas fa-sign-out-alt me-2"></i>Logout
                  </a>
                </li>
              </ul>
            </li>
          </ul>
        </div>
      </div>
    </nav>

    <!-- Main Content -->
    <main class="container-fluid py-4 position-relative z-1">
      <slot></slot>
    </main>
  </div>
</template>

<script>
import { mapGetters, mapState } from 'vuex';

export default {
  name: 'AppLayout',
  computed: {
    ...mapGetters(['isAuthenticated', 'userRole']),
    ...mapState(['user']),
    getUserProfilePath() {
      if (this.userRole === 'customer') {
        return `/profile/customer/${this.user.id}`;
      } else if (this.userRole === 'professional') {
        return `/profile/professional/${this.user.id}`;
      } else if (this.userRole === 'admin') {
        return `/profile/user/${this.user.id}`;
      }
      return '/profile';
    }
  },
  methods: {
    async handleLogout() {
      try {
        await this.$axios.post("/logout");
      } catch (error) {
        console.error("Logout failed:", error);
      } finally {
        this.$store.dispatch("logout");
      }
    },
  }
}
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
  
  /* Card and Border */
  --card-bg: rgba(255, 255, 255, 0.85);
  --border-color: rgba(0, 0, 0, 0.05);
}

.app-wrapper {
  background: linear-gradient(135deg, var(--bg-primary) 0%, var(--bg-secondary) 100%);
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  position: relative;
}

.bg-shapes {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  overflow: hidden;
  z-index: 0;
}

.shape {
  position: absolute;
  border-radius: 50%;
  opacity: 0.15;
  z-index: 0;
}

.shape-1 {
  background: #8a4fff;
  width: 250px;
  height: 250px;
  top: -100px;
  right: -100px;
  animation: float-1 10s infinite alternate;
}

.shape-2 {
  background: #ff6b9e;
  width: 200px;
  height: 200px;
  bottom: -100px;
  left: -100px;
  animation: float-2 12s infinite alternate;
}

.shape-3 {
  background: #4ecdc4;
  width: 180px;
  height: 180px;
  top: 50%;
  right: 10%;
  animation: float-3 8s infinite alternate;
}

.navbar {
  background-color: rgba(255, 255, 255, 0.7);
  backdrop-filter: blur(10px);
  border-bottom: 1px solid rgba(0, 0, 0, 0.05);
}

.navbar-light .navbar-nav .nav-link {
  color: var(--text-primary);
  transition: all 0.3s ease;
}

.navbar-light .navbar-nav .nav-link:hover,
.navbar-light .navbar-nav .nav-link.active {
  color: var(--primary-color);
  transform: translateY(-2px);
}

.navbar-brand .logo-animation {
  border-radius: 10px; /* Adjust as needed */
  object-fit: contain; /* Ensures it maintains the aspect ratio */
  width: auto; /* Maintain original width */
  height: 30px; /* Ensure fixed height */
  
  transition: transform 0.3s ease;
}

.navbar-brand .logo-animation:hover {
  transform: scale(1.1) rotate(5deg);
}

main {
  flex: 1;
  z-index: 1;
}

.nav-link i {
  width: 20px;
  text-align: center;
  color: var(--text-secondary);
}

/* User Dropdown Styling */
.user-dropdown {
  font-weight: 500;
  display: flex;
  align-items: center;
}

.dropdown-menu {
  background-color: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(5px);
  border: 1px solid var(--border-color);
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
}

.dropdown-item {
  color: var(--text-primary);
  padding: 0.6rem 1.5rem;
  display: flex;
  align-items: center;
  transition: all 0.2s ease;
}

.dropdown-item:hover, 
.dropdown-item:focus {
  background-color: rgba(138, 79, 255, 0.1);
  color: var(--primary-color);
  transform: translateX(3px);
}

.dropdown-item i {
  color: var(--text-secondary);
  margin-right: 8px;
  width: 20px;
  text-align: center;
}

.logout-link {
  cursor: pointer;
}

.logout-link:hover {
  color: var(--secondary-color);
}

.dropdown-divider {
  border-top: 1px solid rgba(0, 0, 0, 0.05);
  margin: 0.3rem 0;
}

@keyframes float-1 {
  from { transform: translateY(0); }
  to { transform: translateY(40px); }
}

@keyframes float-2 {
  from { transform: translateY(40px); }
  to { transform: translateY(0); }
}

@keyframes float-3 {
  from { transform: translateX(0); }
  to { transform: translateX(40px); }
}
</style>