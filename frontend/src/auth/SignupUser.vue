<template>
  <div class="signup-wrapper">
    <div class="container">
      <div class="row justify-content-center align-items-center vh-100">
        <div class="col-12 col-md-8 col-lg-6">
          <div class="signup-card">
            <div class="signup-header">
              <img 
                :src="require('@/assets/logo.png')" 
                alt="Logo" 
                class="signup-logo"
              />
              <h2>Create Your Account</h2>
              <p>Join our platform and get started</p>
            </div>
            
            <form @submit.prevent="submitForm" class="signup-form">
              <div class="row">
                <div class="col-md-6 mb-3">
                  <div class="form-floating">
                    <input 
                      v-model="form.username" 
                      type="text" 
                      class="form-control" 
                      id="username" 
                      placeholder="Username" 
                      required 
                    />
                    <label for="username">
                      <i class="fas fa-user me-2"></i>Username
                    </label>
                  </div>
                </div>
                
                <div class="col-md-6 mb-3">
                  <div class="form-floating">
                    <input 
                      v-model="form.email" 
                      type="email" 
                      class="form-control" 
                      id="email" 
                      placeholder="Email" 
                      required 
                    />
                    <label for="email">
                      <i class="fas fa-envelope me-2"></i>Email
                    </label>
                  </div>
                </div>
              </div>
              
              <div class="row">
                <div class="col-md-6 mb-3">
                  <div class="form-floating">
                    <input 
                      v-model="form.password" 
                      type="password" 
                      class="form-control" 
                      id="password" 
                      placeholder="Password" 
                      required 
                    />
                    <label for="password">
                      <i class="fas fa-lock me-2"></i>Password
                    </label>
                  </div>
                </div>
                
                <div class="col-md-6 mb-3">
                  <div class="form-floating">
                    <select 
                      v-model="form.role" 
                      @change="handleRoleChange" 
                      class="form-select" 
                      id="role" 
                      required
                    >
                      <option value="">Select Role</option>
                      <option value="professional">Professional</option>
                      <option value="customer">Customer</option>
                    </select>
                    <label for="role">
                      <i class="fas fa-user-tag me-2"></i>Role
                    </label>
                  </div>
                </div>
              </div>
              
              <!-- Professional Specific Fields -->
              <template v-if="form.role === 'professional'">
                <div class="row">
                  <div class="col-md-6 mb-3">
                    <div class="form-floating">
                      <input 
                        v-model="form.fullname" 
                        type="text" 
                        class="form-control" 
                        id="pro-fullname" 
                        placeholder="Full Name" 
                        required 
                      />
                      <label for="pro-fullname">
                        <i class="fas fa-id-card me-2"></i>Full Name
                      </label>
                    </div>
                  </div>
                  
                  <div class="col-md-6 mb-3">
                    <div class="form-floating">
                      <select 
                        v-model="form.service_id" 
                        class="form-select" 
                        id="service" 
                        required
                      >
                        <option value="">Select Service</option>
                        <option 
                          v-for="service in services" 
                          :key="service.id" 
                          :value="service.id"
                          :disabled="service.is_closed"
                        >
                          {{ service.service_name }} - ${{ service.base_price }}
                        </option>
                      </select>
                      <label for="service">
                        <i class="fas fa-briefcase me-2"></i>Service
                      </label>
                    </div>
                  </div>
                </div>
                
                <div class="row">
                  <div class="col-md-6 mb-3">
                    <div class="form-floating">
                      <input 
                        v-model="form.experience" 
                        type="number" 
                        class="form-control" 
                        id="experience" 
                        placeholder="Experience" 
                        required 
                      />
                      <label for="experience">
                        <i class="fas fa-graduation-cap me-2"></i>Experience (Years)
                      </label>
                    </div>
                  </div>
                </div>
              </template>
              
              <!-- Customer Specific Fields -->
              <template v-if="form.role === 'customer'">
                <div class="row">
                  <div class="col-md-6 mb-3">
                    <div class="form-floating">
                      <input 
                        v-model="form.fullname" 
                        type="text" 
                        class="form-control" 
                        id="cust-fullname" 
                        placeholder="Full Name" 
                        required 
                      />
                      <label for="cust-fullname">
                        <i class="fas fa-id-card me-2"></i>Full Name
                      </label>
                    </div>
                  </div>
                </div>
              </template>
              
              <div class="row">
                <div class="col-md-6 mb-3">
                  <div class="form-floating">
                    <input 
                      v-model="form.contact" 
                      type="tel" 
                      class="form-control" 
                      id="contact" 
                      placeholder="Contact" 
                      required 
                    />
                    <label for="contact">
                      <i class="fas fa-phone me-2"></i>Contact
                    </label>
                  </div>
                </div>
                
                <div class="col-md-6 mb-3">
                  <div class="form-floating">
                    <input 
                      v-model="form.pin_code" 
                      type="text" 
                      class="form-control" 
                      id="pincode" 
                      placeholder="PIN Code" 
                      required 
                    />
                    <label for="pincode">
                      <i class="fas fa-map-pin me-2"></i>PIN Code
                    </label>
                  </div>
                </div>
              </div>
              
              <div class="form-floating mb-3">
                <textarea 
                  v-model="form.address" 
                  class="form-control" 
                  id="address" 
                  placeholder="Address" 
                  style="height: 100px"
                  required
                ></textarea>
                <label for="address">
                  <i class="fas fa-map-marker-alt me-2"></i>Address
                </label>
              </div>
              
              <div class="d-grid">
                <button 
                  type="submit" 
                  class="btn btn-primary btn-lg"
                  :disabled="isLoading"
                  @click="submitForm"
                >
                  <span v-if="isLoading" class="spinner-border spinner-border-sm me-2"></span>
                  {{ isLoading ? 'Signing Up...' : 'Create Account' }}
                </button>
              </div>
              
              <!-- Add alert for error messages -->
              <div v-if="errorMessage" class="alert alert-danger mt-3" role="alert">
                {{ errorMessage }}
              </div>
              <div v-if="successMessage" class="alert alert-success mt-3" role="alert">
                {{ successMessage }}
              </div>
            </form>
            
            <div class="signup-footer">
              <div class="text-center">
                Already have an account? 
                <router-link to="/login" class="text-primary">
                  Sign In
                </router-link>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from "axios";

export default {
  data() {
    return {
      form: {
        username: "",
        email: "",
        password: "",
        role: "",
        fullname: "",
        service_id: "",
        experience: "",
        contact: "",
        address: "",
        pin_code: "",
      },
      services: [],
      isLoading: false,
      errorMessage: "",
      successMessage: ""
    };
  },
  async created() {
    try {
      const response = await axios.get("http://localhost:5000/services");
      this.services = response.data;
    } catch (error) {
      console.error("Error fetching services:", error);
      this.errorMessage = "Failed to load services. Please refresh the page.";
    }
  },
  methods: {
    handleRoleChange() {
      // Reset professional-specific fields when role changes
      if (this.form.role !== 'professional') {
        this.form.service_id = "";
        this.form.experience = "";
      }
    },
    async submitForm() {
      console.log("Submit form triggered"); // Debug log
      
      // Clear previous messages
      this.errorMessage = "";
      this.successMessage = "";
      
      // Minimal validation - just check if a role is selected
      if (!this.form.role) {
        this.errorMessage = "Please select a role";
        console.log("Role validation failed"); // Debug log
        return;
      }
      
      // If professional, check if service is selected
      if (this.form.role === 'professional' && !this.form.service_id) {
        this.errorMessage = "Please select a service";
        console.log("Service validation failed for professional"); // Debug log
        return;
      }

      this.isLoading = true;
      console.log("Submitting form data:", this.form); // Debug log

      try {
        const response = await axios.post(
          "http://localhost:5000/signup",
          this.form
        );
        
        console.log("Signup successful:", response.data); // Debug log
        this.successMessage = response.data.message || "Account created successfully!";
        
        // Reset form after successful submission
        this.resetForm();
        
        setTimeout(() => {
          try {
            this.$router.push({ name: "login" });
          } catch (routerError) {
            console.error("Router navigation error:", routerError);
            // Fallback navigation if the named route doesn't exist
            window.location.href = "/login";
          }
        }, 1500);
      } catch (error) {
        console.error("Signup error:", error);
        if (error.response) {
          // The request was made and the server responded with a status code
          // that falls out of the range of 2xx
          this.errorMessage = error.response.data?.error || 
                             `Signup failed (${error.response.status}). Please try again.`;
        } else if (error.request) {
          // The request was made but no response was received
          this.errorMessage = "No response from server. Please check your connection.";
        } else {
          // Something happened in setting up the request that triggered an Error
          this.errorMessage = "Error: " + error.message;
        }
        
        // Optional: Add haptic feedback if supported
        if (navigator.vibrate) {
          navigator.vibrate(200);
        }
      } finally {
        this.isLoading = false;
      }
    },
    resetForm() {
      // Reset form data
      this.form = {
        username: "",
        email: "",
        password: "",
        role: "",
        fullname: "",
        service_id: "",
        experience: "",
        contact: "",
        address: "",
        pin_code: "",
      };
    }
  },
};
</script>

<style scoped>
.signup-wrapper {
  background-color: var(--bg-secondary);
  min-height: 100vh;
}

.signup-card {
  background-color: var(--card-bg);
  border-radius: 12px;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1);
  padding: 2rem;
  border: 1px solid var(--border-color);
  animation: fadeIn 0.5s ease;
}

.signup-header {
  text-align: center;
  margin-bottom: 2rem;
}

.signup-logo {
  max-width: 100px;
  margin-bottom: 1rem;
  border-radius: 10px;
}

.signup-header h2 {
  color: var(--text-primary);
  margin-bottom: 0.5rem;
}

.signup-header p {
  color: var(--text-secondary);
}

.signup-form .form-control,
.signup-form .form-select {
  background-color: rgba(255,255,255,0.1);
  border-color: var(--border-color);
  color: var(--text-primary);
}

.signup-form .form-control:focus,
.signup-form .form-select:focus {
  background-color: rgba(255,255,255,0.2);
  border-color: var(--primary-color);
  box-shadow: none;
}

.signup-footer {
  margin-top: 1rem;
  border-top: 1px solid var(--border-color);
  padding-top: 1rem;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}
</style>