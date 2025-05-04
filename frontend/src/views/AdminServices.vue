<template>
  <div class="dashboard-container">
    <!-- Main Card Container -->
    <div class="dashboard-card">
      <!-- Card Header -->
      <div class="card-header">
        <h2 class="section-title">Service Management</h2>
      </div>
      
      <!-- Card Body -->
      <div class="card-body p-0">
        <div class="p-4">
          <!-- Search Section -->
          <div class="row mb-4">
            <div class="col-md-6">
              <div class="search-wrapper">
                <i class="fas fa-search search-icon"></i>
                <input 
                  type="text"
                  class="search-input"
                  v-model="searchQuery"
                  placeholder="Search services"
                  @input="filterServices"
                />
              </div>
            </div>
          </div>
    
          <!-- Add Service Form -->
          <form @submit.prevent="addService" class="mb-4">
            <div class="row g-3">
              <!-- Service Name Input -->
              <div class="col-md-3">
                <label for="serviceName" class="form-label">Service Name</label>
                <input 
                  id="serviceName" 
                  type="text" 
                  class="form-control" 
                  v-model="newService.name" 
                  placeholder="Enter Service Name" 
                  required
                >
              </div>
              
              <!-- Base Price Input -->
              <div class="col-md-3">
                <label for="basePrice" class="form-label">Base Price</label>
                <input 
                  id="basePrice" 
                  type="number" 
                  class="form-control" 
                  v-model="newService.basePrice" 
                  placeholder="Enter Base Price" 
                  required
                >
              </div>
              
              <!-- Timing Input -->
              <div class="col-md-3">
                <label for="timing" class="form-label">Timing</label>
                <input 
                  id="timing" 
                  type="text" 
                  class="form-control" 
                  v-model="newService.timing" 
                  placeholder="Enter Timing(min)"
                >
              </div>
              
              <!-- Location Input -->
              <div class="col-md-3">
                <label for="location" class="form-label">Location</label>
                <input 
                  id="location" 
                  type="text" 
                  class="form-control" 
                  v-model="newService.location" 
                  placeholder="Enter Location (optional)"
                >
              </div>
              
              <!-- Closed Service Checkbox -->
              <div class="col-md-3">
                <div class="form-check mt-4">
                  <input 
                    id="isClosed" 
                    type="checkbox" 
                    class="form-check-input" 
                    v-model="newService.isClosed"
                  >
                  <label class="form-check-label" for="isClosed">
                    Is Closed
                  </label>
                </div>
              </div>
              
              <!-- Add Service Button -->
              <div class="col-md-9 d-flex align-items-center justify-content-end mt-4">
                <button type="submit" class="action-btn">
                  <i class="fas fa-plus-circle me-2"></i>Add Service
                </button>
              </div>
            </div>
          </form>
        </div>
  
        <!-- Services Table -->
        <div v-if="filteredServices.length > 0" class="table-responsive">
          <table class="table">
            <thead>
              <tr>
                <th>Id</th>
                <th>Name</th>
                <th>Base Price</th>
                <th>Timing(min)</th>
                <th>Location</th>
                <th>Status</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="service in filteredServices" :key="service.id">
                <td>{{ service.id }}</td>
                <td>
                  <input 
                    type="text" 
                    class="form-control" 
                    v-model="service.name" 
                    :disabled="service.id !== editingServiceId"
                  >
                </td>
                <td>
                  <input 
                    type="number" 
                    class="form-control" 
                    v-model="service.basePrice" 
                    :disabled="service.id !== editingServiceId"
                  >
                </td>
                <td>
                  <input 
                    type="text" 
                    class="form-control" 
                    v-model="service.timing" 
                    :disabled="service.id !== editingServiceId"
                  >
                </td>
                <td>
                  <input 
                    type="text" 
                    class="form-control" 
                    v-model="service.location" 
                    :disabled="service.id !== editingServiceId"
                  >
                </td>
                <td>
                  <div class="status-toggle">
                    <input 
                      type="checkbox" 
                      class="toggle-input" 
                      v-model="service.isClosed" 
                      :disabled="service.id !== editingServiceId"
                    >
                    <span class="status-tag" 
                      :class="service.isClosed ? 'status-warning' : 'status-success'">
                      {{ service.isClosed ? 'Closed' : 'Open' }}
                    </span>
                  </div>
                </td>
                <td>
                  <!-- Action Buttons -->
                  <div class="action-buttons">
                    <!-- Edit Button -->
                    <button 
                      v-if="service.id !== editingServiceId" 
                      @click="startEditing(service)" 
                      class="btn-edit"
                    >
                      <i class="fas fa-pencil-alt me-1"></i>Edit
                    </button>
                    
                    <!-- Save Button -->
                    <button 
                      v-if="service.id === editingServiceId" 
                      @click="saveService(service)" 
                      class="btn-save"
                    >
                      <i class="fas fa-check-circle me-1"></i>Save
                    </button>
                    
                    <!-- Cancel Button -->
                    <button 
                      v-if="service.id === editingServiceId" 
                      @click="cancelEditing()" 
                      class="btn-cancel"
                    >
                      <i class="fas fa-times-circle me-1"></i>Cancel
                    </button>
                    
                    <!-- Delete Button -->
                    <button 
                      v-if="service.id !== editingServiceId" 
                      @click="deleteService(service)" 
                      class="btn-delete"
                    >
                      <i class="fas fa-trash-alt me-1"></i>Delete
                    </button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
  
        <!-- No Services Message -->
        <div v-else class="no-results">
          <i class="fas fa-inbox fa-3x"></i>
          <p>No services found.</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  // Component Logic and Data Management
  data() {
    return {
      services: [],               // Full list of services
      newService: {               // Object for adding new service
        name: '',
        basePrice: '',
        timing: '',
        location: '',
        isClosed: false
      },
      editingServiceId: null,     // Track which service is being edited
      originalService: null,      // Store original service data for cancellation
      filteredServices: [],       // Services shown after search filtering
      searchQuery: '',            // Search input value
    };
  },

  // Load services when component is mounted
  mounted() {
    this.loadServices();
  },

  methods: {
    // Fetch services from backend
    async loadServices() {
      try {
        const response = await axios.get('http://127.0.0.1:5000/services');
        // Transform backend data to frontend format
        this.services = response.data.map(service => ({
          id: service.id,
          name: service.service_name,
          basePrice: service.base_price,
          timing: service.timing,
          location: service.location,
          isClosed: service.is_closed
        }));
        this.filteredServices = this.services;
        console.log('Transformed services:', this.services);
      } catch(error) {
        console.error('Error loading services', error);
      }
    },

    // Add a new service
    async addService() {
      try {
        const response = await axios.post('http://127.0.0.1:5000/api/services', {
          name: this.newService.name,
          basePrice: this.newService.basePrice,
          timing: this.newService.timing,
          location: this.newService.location,
          isClosed: this.newService.isClosed
        });
        
        console.log('Service added', response.data);
        
        // Reset new service form
        this.newService = {
          name: '',
          basePrice: '',
          timing: '',
          location: '',
          isClosed: false
        };
        
        // Refresh services list
        this.loadServices();
      } catch(err) {
        console.error('Error adding service', err);
      }
    },

    // Delete a service
    async deleteService(service) {
      try {
        await axios.delete(`http://127.0.0.1:5000/api/services/${service.id}`);
        
        // Refresh services list
        this.loadServices();
      } catch(err) {
        console.error('Error deleting service', err);
      }
    },

    // Start editing a service
    startEditing(service) {
      this.editingServiceId = service.id;
      // Store original values for potential cancellation
      this.originalService = {...service};
    },

    // Save edited service
    async saveService(service) {
      try {
        await axios.put(`http://127.0.0.1:5000/api/services/${service.id}`, {
          name: service.name,
          basePrice: service.basePrice,
          timing: service.timing,
          location: service.location,
          isClosed: service.isClosed
        });
        
        // Reset editing state
        this.editingServiceId = null;
        this.originalService = null;
        
        // Refresh services list
        this.loadServices();
      } catch(err) {
        console.error('Error updating service', err);
      }
    },

    // Cancel editing and restore original values
    cancelEditing() {
      if (this.originalService) {
        const index = this.services.findIndex(s => s.id === this.editingServiceId);
        if (index !== -1) {
          this.services[index] = {...this.originalService};
          this.filteredServices = [...this.services];
        }
      }
      this.editingServiceId = null;
      this.originalService = null;
    },

    // Filter services based on search query
    filterServices() {
      const query = this.searchQuery.toLowerCase();
      this.filteredServices = this.services.filter(service => 
        service.name.toLowerCase().includes(query)
      );
    }
  }
}
</script>

<style scoped>
.dashboard-container {
  padding: 2rem;
  max-width: 1200px;
  margin: 0 auto;
}

/* Dashboard Card */
.dashboard-card {
  background-color: rgba(255, 255, 255, 0.85);
  backdrop-filter: blur(10px);
  border-radius: 15px;
  overflow: hidden;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.05);
  transition: transform 0.3s ease, box-shadow 0.3s ease;
  border: 1px solid rgba(0, 0, 0, 0.05);
  margin-bottom: 1.5rem;
}

.dashboard-card:hover {
  box-shadow: 0 15px 35px rgba(138, 79, 255, 0.1);
}

/* Card Header */
.card-header {
  padding: 20px;
  background: linear-gradient(135deg, #c3adee 0%, #a98ade 100%);
  color: white;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.section-title {
  font-weight: 700;
  margin-bottom: 0;
  color: white;
  position: relative;
  display: inline-block;
}

/* Form Controls */
.form-label {
  font-weight: 600;
  color: #8a4fff;
  margin-bottom: 0.5rem;
}

.form-control {
  background-color: rgba(255, 255, 255, 0.8);
  border-radius: 10px;
  border: 1px solid rgba(0, 0, 0, 0.05);
  padding: 12px 15px;
  box-shadow: 0 2px 15px rgba(0, 0, 0, 0.05);
  transition: all 0.3s ease;
}

.form-control:focus {
  outline: none;
  box-shadow: 0 2px 20px rgba(138, 79, 255, 0.15);
  border-color: #a98ade;
}

.form-control:disabled {
  background-color: rgba(255, 255, 255, 0.5);
  color: #4a4a4a;
  border: 1px solid rgba(0, 0, 0, 0.03);
}

/* Search */
.search-wrapper {
  position: relative;
}

.search-icon {
  position: absolute;
  left: 15px;
  top: 50%;
  transform: translateY(-50%);
  color: #a98ade;
}

.search-input {
  width: 100%;
  padding: 12px 15px 12px 40px;
  border: 1px solid rgba(0, 0, 0, 0.05);
  border-radius: 10px;
  font-size: 16px;
  background-color: rgba(255, 255, 255, 0.8);
  backdrop-filter: blur(5px);
  box-shadow: 0 2px 15px rgba(0, 0, 0, 0.05);
  transition: all 0.3s ease;
}

.search-input:focus {
  outline: none;
  box-shadow: 0 2px 20px rgba(138, 79, 255, 0.15);
  border-color: #a98ade;
}

/* Checkbox */
.form-check-input {
  width: 1.2em;
  height: 1.2em;
  margin-top: 0.15em;
  cursor: pointer;
  border-radius: 5px;
  border: 1px solid #a98ade;
}

.form-check-input:checked {
  background-color: #8a4fff;
  border-color: #8a4fff;
}

.form-check-label {
  color: #4a4a4a;
  font-weight: 500;
}

/* Table */
.table-responsive {
  padding: 0 20px 20px;
}

.table {
  width: 100%;
  border-collapse: separate;
  border-spacing: 0;
}

.table thead {
  background-color: rgba(138, 79, 255, 0.05);
}

.table th {
  padding: 15px;
  font-weight: 600;
  color: #8a4fff;
  border-bottom: 2px solid rgba(138, 79, 255, 0.1);
  text-align: left;
}

.table td {
  padding: 15px;
  vertical-align: middle;
  border-bottom: 1px solid rgba(0, 0, 0, 0.03);
}

/* Status Tag */
.status-toggle {
  display: flex;
  align-items: center;
}

.toggle-input {
  margin-right: 10px;
  width: 1.2em;
  height: 1.2em;
}

.status-tag {
  padding: 5px 10px;
  border-radius: 20px;
  font-weight: bold;
  font-size: 0.8rem;
  backdrop-filter: blur(5px);
  background-color: rgba(255, 255, 255, 0.2);
}

.status-primary {
  background-color: #8a4fff;
  color: white;
}

.status-success {
  background-color: #4ecdc4;
  color: white;
}

.status-warning {
  background-color: #ffb347;
  color: white;
}

.status-info {
  background-color: #2575fc;
  color: white;
}

/* Buttons */
.action-btn {
  background-color: #8a4fff;
  color: white;
  border: none;
  padding: 12px 20px;
  border-radius: 10px;
  font-weight: 600;
  font-size: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.3s ease;
}

.action-btn:hover {
  background-color: #a98ade;
  transform: translateY(-2px);
  box-shadow: 0 6px 15px rgba(138, 79, 255, 0.2);
}

.action-buttons {
  display: flex;
  gap: 8px;
}

.btn-edit, .btn-save, .btn-cancel, .btn-delete {
  border: none;
  padding: 8px 12px;
  border-radius: 8px;
  font-weight: 600;
  font-size: 14px;
  display: flex;
  align-items: center;
  cursor: pointer;
  transition: all 0.3s ease;
}

.btn-edit {
  background-color: rgba(138, 79, 255, 0.1);
  color: #8a4fff;
}

.btn-edit:hover {
  background-color: #8a4fff;
  color: white;
}

.btn-save {
  background-color: #4ecdc4;
  color: white;
}

.btn-save:hover {
  background-color: #3db9b1;
}

.btn-cancel {
  background-color: #6c757d;
  color: white;
}

.btn-cancel:hover {
  background-color: #5a6268;
}

.btn-delete {
  background-color: rgba(255, 107, 107, 0.1);
  color: #ff6b6b;
}

.btn-delete:hover {
  background-color: #ff6b6b;
  color: white;
}

/* No Results */
.no-results {
  text-align: center;
  padding: 60px 20px;
  color: #a98ade;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 15px;
}

/* Responsive adjustments */
@media (max-width: 768px) {
  .dashboard-container {
    padding: 1rem;
  }
  
  .action-buttons {
    flex-direction: column;
    gap: 5px;
  }
  
  .form-control {
    padding: 10px;
  }
}
</style>