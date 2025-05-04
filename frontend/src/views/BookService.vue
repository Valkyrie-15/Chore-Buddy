<template>
  <div class="services-container">
    <div class="services-header">
      <h2 class="section-title">Available Services</h2>
      
      <!-- Search and filters -->
      <div class="search-container">
        <div class="search-input-wrapper">
          <i class="fas fa-search search-icon"></i>
          <input 
            type="text" 
            class="search-input" 
            placeholder="Search services..." 
            v-model="searchQuery" 
            @input="filterServices"
          >
        </div>
        
        <div class="filter-options">
          <select class="filter-select" v-model="locationFilter" @change="filterServices">
            <option value="">All Locations</option>
            <option v-for="location in uniqueLocations" :key="location" :value="location">
              {{ location }}
            </option>
          </select>
          
          <div class="price-filter">
            <span>Price: ${{ priceFilter }}</span>
            <input 
              type="range" 
              class="price-slider" 
              min="0" 
              :max="maxPrice" 
              v-model.number="priceFilter" 
              @input="filterServices"
            >
          </div>
        </div>
      </div>
    </div>
    
    <!-- Loading indicator -->
    <div v-if="loading" class="loading-container">
      <div class="spinner"></div>
      <p>Loading services...</p>
    </div>
    
    <!-- Error message -->
    <div v-else-if="error" class="error-message">
      <i class="fas fa-exclamation-circle"></i>
      <p>{{ error }}</p>
    </div>
    
    <!-- No services found -->
    <div v-else-if="filteredServices.length === 0" class="no-results">
      <i class="fas fa-search fa-3x"></i>
      <p>No services found matching your criteria.</p>
    </div>
    
    <!-- Services grid -->
    <div v-else class="services-grid">
      <div v-for="service in filteredServices" :key="service.id" class="service-card">
        <div class="card-header">
          <h3 class="service-title">{{ service.name }}</h3>
          <span class="status-tag" :class="service.isClosed ? 'status-closed' : 'status-available'">
            {{ service.isClosed ? 'Unavailable' : 'Available' }}
          </span>
        </div>
        
        <div class="card-body">
          <div class="service-detail">
            <i class="fas fa-dollar-sign icon"></i>
            <span><strong>Price:</strong> ${{ service.basePrice }}</span>
          </div>
          
          <div class="service-detail">
            <i class="fas fa-clock icon"></i>
            <span><strong>Duration:</strong> {{ service.timing }} {{ parseInt(service.timing) === 1 ? 'hour' : 'hours' }}</span>
          </div>
          
          <div class="service-detail">
            <i class="fas fa-map-marker-alt icon"></i>
            <span><strong>Location:</strong> {{ service.location }}</span>
          </div>
        </div>
        
        <button 
          @click="bookService(service)" 
          class="btn book-btn"
          :disabled="service.isClosed"
          :class="{'disabled-btn': service.isClosed}"
        >
          <i class="fas fa-calendar-check me-2"></i> Book Service
        </button>
      </div>
    </div>
    
    <!-- Booking Modal -->
    <transition name="modal-fade">
      <div v-if="showBookingModal" class="modal-overlay" @click.self="closeModal">
        <div class="booking-modal">
          <div class="modal-header">
            <h3>Book {{ selectedService?.name }}</h3>
            <button class="close-btn" @click="closeModal">&times;</button>
          </div>
          <div class="modal-body">
            <div class="service-summary">
              <div class="summary-item">
                <i class="fas fa-concierge-bell icon"></i>
                <div>
                  <span class="label">Service:</span>
                  <span class="value">{{ selectedService?.name }}</span>
                </div>
              </div>
              <div class="summary-item">
                <i class="fas fa-dollar-sign icon"></i>
                <div>
                  <span class="label">Price:</span>
                  <span class="value">${{ selectedService?.basePrice }}</span>
                </div>
              </div>
              <div class="summary-item">
                <i class="fas fa-clock icon"></i>
                <div>
                  <span class="label">Duration:</span>
                  <span class="value">{{ selectedService?.timing }} {{ parseInt(selectedService?.timing) === 1 ? 'hour' : 'hours' }}</span>
                </div>
              </div>
              <div class="summary-item">
                <i class="fas fa-map-marker-alt icon"></i>
                <div>
                  <span class="label">Location:</span>
                  <span class="value">{{ selectedService?.location }}</span>
                </div>
              </div>
            </div>
            
            <div class="form-group">
              <label for="bookingDate">Select Date:</label>
              <div class="booking-time-wrapper">
                <i class="fas fa-calendar-alt icon"></i>
                <input 
                  type="date" 
                  id="bookingDate" 
                  class="booking-time-input" 
                  v-model="bookingDate"
                >
              </div>
            </div>
            
            <div class="form-group">
              <label for="bookingTime">Select Time:</label>
              <div class="booking-time-wrapper">
                <i class="fas fa-clock icon"></i>
                <input 
                  type="time" 
                  id="bookingTime" 
                  class="booking-time-input" 
                  v-model="bookingTime"
                >
              </div>
            </div>
          </div>
          <div class="modal-footer">
            <button class="btn cancel-btn" @click="closeModal">
              <i class="fas fa-times me-2"></i>Cancel
            </button>
            <button class="btn confirm-btn" @click="confirmBooking">
              <i class="fas fa-check me-2"></i>Confirm Booking
            </button>
          </div>
        </div>
      </div>
    </transition>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  name: 'CustomerServices',
  data() {
    return {
      services: [],
      filteredServices: [],
      searchQuery: '',
      locationFilter: '',
      priceFilter: 5000, // Default maximum price filter
      loading: true,
      error: null,
      maxPrice: 5000, // Initial maximum price
      
      // Booking modal data
      showBookingModal: false,
      selectedService: null,
      bookingDate: '',
      bookingTime: '',
    };
  },
  computed: {
    uniqueLocations() {
      // Get unique locations from services
      return [...new Set(this.services.map(service => service.location))];
    }
  },
  mounted() {
    this.loadServices();
  },
  methods: {
    async loadServices() {
      this.loading = true;
      this.error = null;
      
      try {
        const response = await axios.get('http://127.0.0.1:5000/services');
        
        // Transform data to match expected property names
        this.services = response.data.map(service => ({
          id: service.id,
          name: service.service_name,
          basePrice: service.base_price,
          timing: service.timing,
          location: service.location,
          isClosed: service.is_closed
        }));
        
        // Set initial filtered services
        this.filteredServices = [...this.services];
        
        // Update max price based on available services
        if (this.services.length > 0) {
          this.maxPrice = Math.max(...this.services.map(s => s.basePrice));
          this.priceFilter = this.maxPrice; // Set initial price filter to maximum
        }
        
      } catch (error) {
        console.error('Error loading services:', error);
        this.error = 'Failed to load services. Please try again later.';
      } finally {
        this.loading = false;
      }
    },
    
    filterServices() {
      const query = this.searchQuery.toLowerCase();
      
      this.filteredServices = this.services.filter(service => {
        // Name search
        const nameMatch = service.name.toLowerCase().includes(query);
        
        // Location filter
        const locationMatch = !this.locationFilter || service.location === this.locationFilter;
        
        // Price filter
        const priceMatch = service.basePrice <= this.priceFilter;
        
        return nameMatch && locationMatch && priceMatch;
      });
    },
    
    bookService(service) {
      // Instead of navigating to a new route, show the booking modal
      this.selectedService = service;
      this.showBookingModal = true;
      
      // Set default date to tomorrow
      const tomorrow = new Date();
      tomorrow.setDate(tomorrow.getDate() + 1);
      this.bookingDate = tomorrow.toISOString().split('T')[0];
      
      // Set default time
      this.bookingTime = '10:00';
    },
    
    closeModal() {
      this.showBookingModal = false;
      this.selectedService = null;
      this.bookingDate = '';
      this.bookingTime = '';
    },
    
    async confirmBooking() {
      if (!this.bookingDate || !this.bookingTime) {
        alert('Please select both date and time for your booking.');
        return;
      }
      
      try {
        // Get JWT token from local storage or wherever you store it
        const token = localStorage.getItem('token'); // adjust based on your auth implementation
        
        if (!token) {
          alert('You need to be logged in to book a service.');
          // Optionally redirect to login page
          // this.$router.push('/login');
          return;
        }
        
        // Format the date and time for the API
        const bookingDateTime = `${this.bookingDate}T${this.bookingTime}:00`;
        
        // Make the API call to create the booking with auth token
        await axios({
          method: 'post',
          url: 'http://127.0.0.1:5000/bookings',
          data: {
            service_id: this.selectedService.id,
            booking_time: bookingDateTime,
          },
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`  // Include JWT token
          }
        });
        
        // Show success message
        alert('Your booking has been confirmed!');
        
        // Close the modal
        this.closeModal();
        
      } catch (error) {
        console.error('Error creating booking:', error);
        if (error.response) {
          // The request was made and the server responded with a status code
          // that falls out of the range of 2xx
          console.error('Response data:', error.response.data);
          console.error('Response status:', error.response.status);
          
          if (error.response.status === 401 || error.response.status === 403) {
            alert('Authentication error: Please log in again.');
            // Optionally redirect to login
            // this.$router.push('/login');
          } else {
            alert(`Booking failed: ${error.response.data.error || 'An unknown error occurred'}`);
          }
        } else if (error.request) {
          // The request was made but no response was received
          alert('No response from server. Please check if the server is running.');
        } else {
          alert('Failed to create booking. Please try again later.');
        }
      }
    }
  }
};
</script>

<style scoped>
.services-container {
  padding: 2rem;
  max-width: 1200px;
  margin: 0 auto;
}

.services-header {
  margin-bottom: 2rem;
}

.section-title {
  font-weight: 700;
  margin-bottom: 1.5rem;
  color: #8a4fff; /* Matching primary color from layout */
  position: relative;
  display: inline-block;
  padding-bottom: 8px;
}

.section-title::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 0;
  height: 3px;
  width: 70%;
  background: linear-gradient(90deg, #c3adee, transparent);
  border-radius: 2px;
}

.search-container {
  display: flex;
  gap: 15px;
  align-items: center;
  margin-bottom: 1.5rem;
  flex-wrap: wrap;
}

.search-input-wrapper {
  position: relative;
  flex-grow: 1;
  min-width: 250px;
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
  box-shadow: 0 2px 15px rgba(0, 0, 0, 0.05);
  transition: all 0.3s ease;
  background-color: rgba(255, 255, 255, 0.8);
  backdrop-filter: blur(5px);
}

.search-input:focus {
  outline: none;
  box-shadow: 0 2px 20px rgba(138, 79, 255, 0.15);
  border-color: #a98ade;
}

.filter-options {
  display: flex;
  gap: 15px;
  align-items: center;
  flex-wrap: wrap;
}

.filter-select {
  min-width: 160px;
  padding: 12px 15px;
  border: 1px solid rgba(0, 0, 0, 0.05);
  border-radius: 10px;
  font-size: 16px;
  background-color: rgba(255, 255, 255, 0.8);
  backdrop-filter: blur(5px);
  box-shadow: 0 2px 15px rgba(0, 0, 0, 0.05);
  appearance: none;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='16' height='16' fill='%238a4fff' class='bi bi-chevron-down' viewBox='0 0 16 16'%3E%3Cpath fill-rule='evenodd' d='M1.646 4.646a.5.5 0 0 1 .708 0L8 10.293l5.646-5.647a.5.5 0 0 1 .708.708l-6 6a.5.5 0 0 1-.708 0l-6-6a.5.5 0 0 1 0-.708z'/%3E%3C/svg%3E");
  background-repeat: no-repeat;
  background-position: right 15px center;
  transition: all 0.3s ease;
}

.filter-select:focus {
  outline: none;
  box-shadow: 0 2px 20px rgba(138, 79, 255, 0.15);
  border-color: #a98ade;
}

.price-filter {
  display: flex;
  flex-direction: column;
  gap: 8px;
  min-width: 150px;
  color: #4a4a4a;
}

.price-slider {
  appearance: none;
  width: 100%;
  height: 6px;
  border-radius: 5px;
  background: linear-gradient(to right, #c3adee, #8a4fff);
  outline: none;
}

.price-slider::-webkit-slider-thumb {
  appearance: none;
  width: 20px;
  height: 20px;
  border-radius: 50%;
  background: #8a4fff;
  cursor: pointer;
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.2);
}

.services-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(340px, 1fr));
  gap: 20px;
}

.service-card {
  background-color: rgba(255, 255, 255, 0.85);
  backdrop-filter: blur(10px);
  border-radius: 15px;
  overflow: hidden;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.05);
  transition: transform 0.3s ease, box-shadow 0.3s ease;
  border: 1px solid rgba(0, 0, 0, 0.05);
  display: flex;
  flex-direction: column;
}

.service-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 15px 35px rgba(138, 79, 255, 0.1);
}

.card-header {
  padding: 20px;
  background: linear-gradient(135deg, #c3adee 0%, #a98ade 100%);
  color: white;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.service-title {
  margin: 0;
  font-size: 1.25rem;
  font-weight: 600;
  flex-grow: 1;
}

.status-tag {
  padding: 5px 10px;
  border-radius: 20px;
  font-weight: bold;
  backdrop-filter: blur(5px);
}

.status-available {
  background-color: rgba(78, 205, 196, 0.2);
  color: #4ecdc4;
}

.status-closed {
  background-color: rgba(255, 107, 158, 0.2);
  color: #ff6b9e;
}

.card-body {
  padding: 20px;
  flex-grow: 1;
}

.service-detail {
  margin-bottom: 12px;
  display: flex;
  align-items: center;
}

.service-detail .icon {
  width: 24px;
  margin-right: 10px;
  color: #8a4fff;
}

.btn {
  padding: 12px 20px;
  border-radius: 10px;
  border: none;
  cursor: pointer;
  font-weight: 600;
  font-size: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease;
}

.book-btn {
  background-color: #ffccdf; /* Pastel pink */
  color: #ff6b9e; /* Secondary color from layout */
  margin: 15px 20px 20px;
}

.book-btn:hover {
  background-color: #ff6b9e;
  color: white;
  transform: translateY(-2px);
}

.disabled-btn {
  opacity: 0.5;
  cursor: not-allowed;
  background-color: #e2e8f0;
  color: #6a6a6a;
}

.disabled-btn:hover {
  transform: none;
  background-color: #e2e8f0;
  color: #6a6a6a;
}

.loading-container {
  text-align: center;
  padding: 60px 20px;
  color: #a98ade;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 15px;
}

.spinner {
  width: 50px;
  height: 50px;
  border: 5px solid rgba(169, 138, 222, 0.3);
  border-radius: 50%;
  border-top-color: #8a4fff;
  animation: spin 1s ease-in-out infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.error-message {
  background-color: #fdf2f2;
  color: #e74c3c;
  padding: 20px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  gap: 10px;
  border-left: 4px solid #e74c3c;
}

.no-results {
  text-align: center;
  padding: 60px 20px;
  color: #a98ade;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 15px;
  background-color: rgba(255, 255, 255, 0.7);
  border-radius: 15px;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.05);
  backdrop-filter: blur(10px);
}

/* Modal Styles */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  backdrop-filter: blur(5px);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.booking-modal {
  background-color: white;
  width: 90%;
  max-width: 500px;
  border-radius: 15px;
  overflow: hidden;
  box-shadow: 0 20px 50px rgba(0, 0, 0, 0.25);
  max-height: 85vh;
  display: flex;
  flex-direction: column;
}

.modal-header {
  padding: 20px 25px;
  background: linear-gradient(135deg, #c3adee 0%, #a98ade 100%);
  display: flex;
  justify-content: space-between;
  align-items: center;
  color: white;
}

.modal-header h3 {
  margin: 0;
  font-size: 1.25rem;
  font-weight: 600;
}

.close-btn {
  background: rgba(255, 255, 255, 0.2);
  border: none;
  border-radius: 50%;
  width: 30px;
  height: 30px;
  font-size: 1.25rem;
  cursor: pointer;
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background 0.3s ease;
}

.close-btn:hover {
  background: rgba(255, 255, 255, 0.3);
}

.modal-body {
  padding: 25px;
  overflow-y: auto;
  flex-grow: 1;
}

.service-summary {
  margin-bottom: 25px;
  padding-bottom: 15px;
  border-bottom: 1px solid rgba(0, 0, 0, 0.05);
}

.summary-item {
  margin-bottom: 15px;
  display: flex;
  align-items: center;
}

.summary-item .icon {
  width: 24px;
  margin-right: 15px;
  color: #8a4fff;
}

.summary-item div {
  display: flex;
  flex-direction: column;
}

.summary-item .label {
  font-size: 14px;
  color: #6a6a6a;
  margin-bottom: 2px;
}

.summary-item .value {
  font-weight: 600;
  color: #4a4a4a;
}

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  margin-bottom: 10px;
  font-weight: 600;
  color: #4a4a4a;
}

.booking-time-wrapper {
  position: relative;
}

.booking-time-wrapper .icon {
  position: absolute;
  left: 15px;
  top: 50%;
  transform: translateY(-50%);
  color: #a98ade;
}

.booking-time-input {
  width: 100%;
  padding: 12px 15px 12px 40px;
  border: 1px solid rgba(0, 0, 0, 0.05);
  border-radius: 10px;
  font-size: 16px;
  background-color: #f8f9fa;
  transition: all 0.3s ease;
}

.booking-time-input:focus {
  outline: none;
  box-shadow: 0 2px 20px rgba(138, 79, 255, 0.15);
  border-color: #a98ade;
}

.modal-footer {
  padding: 20px 25px;
  display: flex;
  justify-content: flex-end;
  gap: 15px;
  border-top: 1px solid rgba(0, 0, 0, 0.05);
}

.cancel-btn {
  background-color: #e2e8f0; /* Pastel gray */
  color: #6a6a6a;
}

.cancel-btn:hover {
  background-color: #cbd5e1;
}

.confirm-btn {
  background-color: #d1f7e0; /* Pastel green */
  color: #4ecdc4; /* Accent color from layout */
}

.confirm-btn:hover {
  background-color: #4ecdc4;
  color: white;
}

/* Modal transition */
.modal-fade-enter-active, .modal-fade-leave-active {
  transition: opacity 0.3s;
}

.modal-fade-enter-from, .modal-fade-leave-to {
  opacity: 0;
}

/* Responsive adjustments */
@media (max-width: 768px) {
  .services-container {
    padding: 1rem;
  }
  
  .services-grid {
    grid-template-columns: 1fr;
  }
  
  .search-container {
    flex-direction: column;
    align-items: stretch;
  }
  
  .filter-options {
    flex-direction: column;
    width: 100%;
  }
  
  .booking-modal {
    width: 95%;
    max-height: 90vh;
  }
}
</style>