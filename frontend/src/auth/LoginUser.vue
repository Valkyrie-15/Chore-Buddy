<template>
  <div class="login-wrapper">
    <div class="login-container">
      <div class="login-form-section animate-slide-in-left">
        <div class="login-form-header">
          <h2 class="animate-fade-in">Welcome Back</h2>
          <p class="animate-fade-in delay-100">Sign in to continue to your dashboard</p>
        </div>
        
        <form @submit.prevent="loginuser" class="login-form animate-fade-in delay-200">
          <div class="form-group animate-slide-in-right">
            <input 
              type="text" 
              placeholder="Username" 
              v-model="username" 
              required
              @focus="resetError"
            />
            <i class="fas fa-user"></i>
          </div>
          
          <div class="form-group animate-slide-in-right delay-100">
            <input 
              type="password" 
              placeholder="Password" 
              v-model="password" 
              required
              @focus="resetError"
            />
            <i class="fas fa-lock"></i>
          </div>
          
          <div 
            v-if="errorMessage" 
            class="error-message animate-shake"
          >
            <i class="fas fa-exclamation-triangle me-2"></i>
            {{ errorMessage }}
          </div>
          
          <button 
            type="submit" 
            class="login-btn animate-pulse-on-hover"
            :disabled="isLoading"
          >
            <span v-if="isLoading" class="spinner"></span>
            {{ isLoading ? 'Signing In...' : 'Sign In' }}
          </button>
          
          <div class="login-footer animate-fade-in delay-300">
            <a href="#" class="forgot-password">Forgot Password?</a>
            <router-link to="/signup" class="create-account">
              Create an Account
            </router-link>
          </div>
        </form>
      </div>
      
      <div class="login-illustration-section animate-slide-in-right">
        <img 
          :src="require('@/assets/login.png')" 
          alt="Login Illustration" 
          class="login-image animate-float"
        />
      </div>
    </div>
  </div>
</template>

<script>
import axios from "axios";

export default {
  data() {
    return {
      username: "",
      password: "",
      errorMessage: "",
      isLoading: false
    };
  },
  methods: {
    resetError() {
      this.errorMessage = "";
    },
    async loginuser() {
      this.errorMessage = "";
      this.isLoading = true;

      try {
        const response = await axios.post("http://127.0.0.1:5000/api/login", {
          username: this.username,
          password: this.password,
        });

        const { access_token, user } = response.data;
        
        await this.$store.dispatch("login", {
          token: access_token,
          user: user,
        });
        localStorage.setItem("user", JSON.stringify(user));

        const routeMap = {
          admin: "/admin-dashboard",
          professional: "/pro-dashboard",
          customer: "/cust-dashboard"
        };
        
        await this.$router.push(routeMap[user.role] || "/");
      } catch (error) {
        this.errorMessage = error.response
          ? error.response.data.message
          : "Login failed. Please try again.";
        
        navigator.vibrate?.(200);
      } finally {
        this.isLoading = false;
      }
    },
  },
};
</script>

<style scoped>
:root {
  --primary-color: #3b82f6;
  --background-color: #f3f4f6;
  --text-color: #1f2937;
  --card-bg: white;
}

/* Animation Keyframes */
@keyframes slideInLeft {
  from {
    opacity: 0;
    transform: translateX(-50px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

@keyframes slideInRight {
  from {
    opacity: 0;
    transform: translateX(50px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

@keyframes shake {
  0%, 100% { transform: translateX(0); }
  10%, 30%, 50%, 70%, 90% { transform: translateX(-5px); }
  20%, 40%, 60%, 80% { transform: translateX(5px); }
}

@keyframes float {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-10px); }
}

@keyframes pulse {
  0% { transform: scale(1); }
  50% { transform: scale(1.05); }
  100% { transform: scale(1); }
}

/* Animation Classes */
.animate-slide-in-left {
  animation: slideInLeft 0.8s ease-out forwards;
}

.animate-slide-in-right {
  animation: slideInRight 0.8s ease-out forwards;
}

.animate-fade-in {
  animation: fadeIn 0.8s ease-out forwards;
  opacity: 0;
}

.animate-shake {
  animation: shake 0.5s ease-in-out;
}

.animate-float {
  animation: float 3s ease-in-out infinite;
}

.animate-pulse-on-hover:hover {
  animation: pulse 0.5s ease-in-out;
}

.delay-100 {
  animation-delay: 0.1s;
}

.delay-200 {
  animation-delay: 0.2s;
}

.delay-300 {
  animation-delay: 0.3s;
}

/* Rest of the previous CSS remains the same */
.login-wrapper {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background-color: var(--background-color);
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Open Sans', 'Helvetica Neue', sans-serif;
  overflow: hidden;
}

/* ... (rest of the previous CSS) ... */

:root {
  --primary-color: #3b82f6;
  --background-color: #f3f4f6;
  --text-color: #1f2937;
  --card-bg: white;
}

.login-wrapper {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background-color: var(--background-color);
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Open Sans', 'Helvetica Neue', sans-serif;
}

.login-container {
  display: flex;
  width: 100%;
  max-width: 1200px;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1);
  border-radius: 16px;
  overflow: hidden;
  background-color: var(--card-bg);
}

.login-form-section {
  flex: 1;
  padding: 4rem;
  display: flex;
  flex-direction: column;
  justify-content: center;
}

.login-illustration-section {
  flex: 1;
  background-color: var(--primary-color);
  display: flex;
  justify-content: center;
  align-items: center;
  position: relative;
  overflow: hidden;
}

.login-image {
  max-width: 80%;
  z-index: 1;
}

.login-form-header {
  margin-bottom: 2rem;
  text-align: center;
}

.login-form-header h2 {
  font-size: 2.25rem;
  margin-bottom: 0.5rem;
  color: var(--text-color);
}

.login-form-header p {
  color: #6b7280;
}



.form-group {
  margin-bottom: 1rem;
  position: relative;
}

.form-group input {
  width: 100%;
  padding: 0.75rem 1rem 0.75rem 2.5rem;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  font-size: 1rem;
  transition: all 0.3s ease;
}

.form-group input:focus {
  outline: none;
  border-color: var(--primary-color);
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.form-group i {
  position: absolute;
  left: 1rem;
  top: 50%;
  transform: translateY(-50%);
  color: #9ca3af;
  transition: color 0.3s ease;
}

.form-group input:focus + i {
  color: var(--primary-color);
}

.login-btn {
  width: 100%;
  padding: 0.75rem;
  background-color: var(--primary-color);
  color: rgb(20, 20, 20);
  border-color: var(--primary-color);
  
  border-radius: 8px;
  font-size: 1rem;
  cursor: pointer;
  transition: background-color 0.3s ease;
  display: flex;
  justify-content: center;
  align-items: center;
}

.login-btn:hover {
  background-color: #86a6eb;
}

.login-btn:disabled {
  opacity: 0.7;
  cursor: not-allowed;
  border: #1f2937;
  color: #1f2937;
}

.spinner {
  border: 2px solid rgba(255,255,255,0.3);
  border-top: 2px solid white;
  border-radius: 50%;
  width: 20px;
  height: 20px;
  animation: spin 1s linear infinite;
  margin-right: 10px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.error-message {
  background-color: #fee2e2;
  color: #7f1d1d;
  padding: 0.75rem;
  border-radius: 8px;
  margin-bottom: 1rem;
  display: flex;
  align-items: center;
}

.login-footer {
  display: flex;
  justify-content: space-between;
  margin-top: 1rem;
  font-size: 0.875rem;
}

.login-footer a {
  color: var(--primary-color);
  text-decoration: none;
}

@media (max-width: 768px) {
  .login-container {
    flex-direction: column;
  }

  .login-illustration-section {
    display: none;
  }

  .login-form-section {
    padding: 2rem;
  }
}
</style>