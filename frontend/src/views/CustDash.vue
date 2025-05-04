<template>
  <div class="recommendations-container">
    <div class="recommendations-header">
      <h2 class="section-title">Services For You</h2>
      
      <!-- Search Bar -->
      <div class="search-container">
        <div class="search-input-wrapper">
          <i class="fas fa-search search-icon"></i>
          <input 
            type="text" 
            v-model="searchQuery" 
            placeholder="Search services..."
            class="search-input"
            @input="filterRecommendations"
          />
        </div>
        <div class="filter-options">
          <select v-model="filterCriteria" @change="filterRecommendations" class="filter-select">
            <option value="all">All Criteria</option>
            <option value="service_name">Service Name</option>
            <option value="professional_name">Professional</option>
            <option value="location">Location</option>
            <option value="price">Price Range</option>
          </select>
        </div>
      </div>
    </div>
    
    <div v-if="filteredRecommendations.length" class="recommendations-grid">
      <div v-for="(rec, index) in filteredRecommendations" :key="index" class="recommendation-card">
        <div class="card-header">
          <h3 class="service-title">{{ rec.service_name }}</h3>
          <span class="price-tag">${{ rec.price }}</span>
        </div>
        
        <div class="card-body">
          <div class="service-detail">
            <i class="fas fa-user-tie icon"></i>
            <span><strong>Professional:</strong> {{ rec.professional_name || "Available Professionals" }}</span>
          </div>
          <div class="service-detail">
            <i class="fas fa-star icon"></i>
            <span><strong>Experience:</strong> {{ rec.experience }} years</span>
          </div>
          <div class="service-detail">
            <i class="fas fa-phone-alt icon"></i>
            <span><strong>Contact:</strong> {{ rec.contact }}</span>
          </div>
          <div class="service-detail">
            <i class="fas fa-map-marker-alt icon"></i>
            <span><strong>Location:</strong> {{ rec.location }}</span>
          </div>
          <div class="service-detail">
            <i class="fas fa-clock icon"></i>
            <span><strong>Duration:</strong> {{ rec.duration }} mins</span>
          </div>
        </div>
        
        <button @click="openBookingModal(rec)" class="btn book-btn">
          <i class="fas fa-calendar-check me-2"></i> Book Service
        </button>
      </div>
    </div>
    <div v-else class="no-results">
      <i class="fas fa-search fa-3x"></i>
      <p>No recommendations found for your search criteria.</p>
    </div>
    
    <!-- Booking Modal -->
    <transition name="modal-fade">
      <div v-if="showBookingModal" class="modal-overlay" @click.self="closeModal">
        <div class="booking-modal">
          <div class="modal-header">
            <h3>Book {{ selectedService?.service_name }}</h3>
            <button class="close-btn" @click="closeModal">&times;</button>
          </div>
          <div class="modal-body">
            <div class="service-summary">
              <div class="summary-item">
                <i class="fas fa-concierge-bell icon"></i>
                <div>
                  <span class="label">Service:</span>
                  <span class="value">{{ selectedService?.service_name }}</span>
                </div>
              </div>
              <div class="summary-item">
                <i class="fas fa-user-tie icon"></i>
                <div>
                  <span class="label">Professional:</span>
                  <span class="value">{{ selectedService?.professional_name || "Available Professionals" }}</span>
                </div>
              </div>
              <div class="summary-item">
                <i class="fas fa-dollar-sign icon"></i>
                <div>
                  <span class="label">Price:</span>
                  <span class="value">${{ selectedService?.price }}</span>
                </div>
              </div>
              <div class="summary-item">
                <i class="fas fa-clock icon"></i>
                <div>
                  <span class="label">Duration:</span>
                  <span class="value">{{ selectedService?.duration }} mins</span>
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
              <label for="bookingDateTime">Select Date and Time:</label>
              <div class="booking-time-wrapper">
                <i class="fas fa-calendar-alt icon"></i>
                <input 
                  type="datetime-local" 
                  id="bookingDateTime" 
                  class="booking-time-input" 
                  v-model="bookingTime"
                >
              </div>
            </div>
            
            <div v-if="bookingError" class="error-message">
              <i class="fas fa-exclamation-circle me-2"></i>
              {{ bookingError }}
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
export default {
  data() {
    return {
      recommendations: [],
      filteredRecommendations: [],
      searchQuery: '',
      filterCriteria: 'all',
      showBookingModal: false,
      selectedService: null,
      bookingTime: '',
      bookingError: ''
    };
  },
  mounted() {
    this.fetchRecommendations();
    // Set default booking time to tomorrow at 10:00 AM
    const tomorrow = new Date();
    tomorrow.setDate(tomorrow.getDate() + 1);
    tomorrow.setHours(10, 0, 0);
    this.setDefaultBookingTime(tomorrow);
  },
  methods: {
    setDefaultBookingTime(date) {
      // Format date for datetime-local input
      const year = date.getFullYear();
      const month = String(date.getMonth() + 1).padStart(2, '0');
      const day = String(date.getDate()).padStart(2, '0');
      const hours = String(date.getHours()).padStart(2, '0');
      const minutes = String(date.getMinutes()).padStart(2, '0');
      
      this.bookingTime = `${year}-${month}-${day}T${hours}:${minutes}`;
    },
    
    async fetchRecommendations() {
      try {
        const token = localStorage.getItem("token");

        if (!token) {
          console.error("No token found, user might not be logged in");
          return;
        }

        let response = await fetch("http://127.0.0.1:5000/recommendations", {
          method: "GET",
          headers: {
            "Authorization": `Bearer ${token}`,
            "Content-Type": "application/json",
          },
        });

        if (!response.ok) {
          let errorResponse = await response.json();
          console.error("Error from server:", errorResponse);
          throw new Error("Failed to fetch recommendations");
        }

        let data = await response.json();
        this.recommendations = data.recommendations;
        this.filteredRecommendations = [...this.recommendations];
      } catch (error) {
        console.error("Error fetching recommendations:", error);
      }
    },
    
    filterRecommendations() {
      if (!this.searchQuery.trim()) {
        this.filteredRecommendations = [...this.recommendations];
        return;
      }
      
      const query = this.searchQuery.toLowerCase().trim();
      
      this.filteredRecommendations = this.recommendations.filter(rec => {
        if (this.filterCriteria === 'all') {
          return (
            (rec.service_name && rec.service_name.toLowerCase().includes(query)) ||
            (rec.professional_name && rec.professional_name.toLowerCase().includes(query)) ||
            (rec.location && rec.location.toLowerCase().includes(query)) ||
            (rec.price && rec.price.toString().includes(query))
          );
        } else if (this.filterCriteria === 'price') {
          // Handle price as a special case for range searches
          try {
            const price = parseFloat(rec.price);
            
            if (query.includes('-')) {
              const [min, max] = query.split('-').map(num => parseFloat(num.trim()));
              return price >= min && price <= max;
            } else if (query.includes('<')) {
              const max = parseFloat(query.replace('<', '').trim());
              return price <= max;
            } else if (query.includes('>')) {
              const min = parseFloat(query.replace('>', '').trim());
              return price >= min;
            } else {
              // Direct comparison
              return rec.price.toString().includes(query);
            }
          } catch (e) {
            return false;
          }
        } else {
          // Filter by specific criteria
          return rec[this.filterCriteria] && 
                 rec[this.filterCriteria].toString().toLowerCase().includes(query);
        }
      });
    },

    openBookingModal(service) {
  console.log("Selected service object:", service);
  console.log("Available properties:", Object.keys(service));
  
  this.selectedService = service;
  this.showBookingModal = true;
  this.bookingError = '';
  
  // Set default time to tomorrow at 10 AM
  const tomorrow = new Date();
  tomorrow.setDate(tomorrow.getDate() + 1);
  tomorrow.setHours(10, 0, 0);
  this.setDefaultBookingTime(tomorrow);
},
    
    closeModal() {
      this.showBookingModal = false;
      this.selectedService = null;
      this.bookingError = '';
    },
    
    async confirmBooking() {
  this.bookingError = '';
  
  try {
    const token = localStorage.getItem("token");

    if (!token) {
      this.bookingError = "You must be logged in to book a service.";
      return;
    }

    if (!this.bookingTime) {
      this.bookingError = "Please select a booking time.";
      return;
    }

    // Debug the service object structure
    console.log("Selected service for booking:", this.selectedService);
    
    // Check what property might contain the service ID
    // Common alternatives: id, _id, serviceId, etc.
    let serviceId = this.selectedService.service_id;
    
    if (!serviceId && this.selectedService.id) {
      serviceId = this.selectedService.id;
    } else if (!serviceId && this.selectedService._id) {
      serviceId = this.selectedService._id;
    } else if (!serviceId && this.selectedService.serviceId) {
      serviceId = this.selectedService.serviceId;
    }
    
    if (!serviceId) {
      this.bookingError = "Service ID is missing. Please contact support.";
      console.error("Service object is missing ID. Available properties:", 
                    Object.keys(this.selectedService));
      return;
    }

    const bookingData = {
      service_id: serviceId,
      booking_time: new Date(this.bookingTime).toISOString()
    };

    console.log("Sending booking data:", bookingData);

    let response = await fetch("http://127.0.0.1:5000/bookings", {
      method: "POST",
      headers: {
        "Authorization": `Bearer ${token}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify(bookingData),
    });

    if (!response.ok) {
      let errorResponse = await response.json();
      console.error("Booking error:", errorResponse);
      this.bookingError = errorResponse.error || "Failed to book service";
      return;
    }

    let data = await response.json();
    alert(data.message || "Service booked successfully!");
    this.closeModal();
  } catch (error) {
    console.error("Error booking service:", error);
    this.bookingError = "An error occurred while booking the service.";
  }
}
  }
};
</script>

<style scoped>
.recommendations-container {
  padding: 2rem;
  max-width: 1200px;
  margin: 0 auto;
}

.recommendations-header {
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
}

.search-input-wrapper {
  position: relative;
  flex-grow: 1;
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
  min-width: 160px;
}

.filter-select {
  width: 100%;
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

.recommendations-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(340px, 1fr));
  gap: 20px;
}

.recommendation-card {
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

.recommendation-card:hover {
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

.price-tag {
  background-color: rgba(255, 255, 255, 0.2);
  padding: 5px 10px;
  border-radius: 20px;
  font-weight: bold;
  backdrop-filter: blur(5px);
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

.error-message {
  color: #e74c3c;
  margin-top: 15px;
  padding: 12px 15px;
  background-color: #fdf2f2;
  border-radius: 10px;
  border-left: 4px solid #e74c3c;
  display: flex;
  align-items: center;
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
  .recommendations-container {
    padding: 1rem;
  }
  
  .recommendations-grid {
    grid-template-columns: 1fr;
  }
  
  .search-container {
    flex-direction: column;
    align-items: stretch;
  }
  
  .filter-options {
    width: 100%;
  }
  
  .booking-modal {
    width: 95%;
    max-height: 90vh;
  }
  
  .modal-body {
    padding: 15px;
  }
  
  .modal-footer {
    padding: 15px;
    flex-direction: column;
  }
  
  .btn {
    width: 100%;
  }
}
</style>