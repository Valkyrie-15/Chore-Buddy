<template>
  <div class="bookings-container">
    <h2 class="title">Service Requests</h2>

    <!-- Status Filters -->
    <div class="filters">
      <button
        v-for="filter in statusFilters"
        :key="filter.value"
        @click="currentFilter = filter.value"
        :class="{ active: currentFilter === filter.value }"
      >
        {{ filter.label }}
      </button>
    </div>

    <!-- Bookings List -->
    <div v-if="loading" class="loading">Loading bookings...</div>
    <div v-else-if="error" class="error">{{ error }}</div>
    <div v-else>
      <div v-for="booking in filteredBookings" :key="booking.id" class="booking-card">
        <div class="booking-header">
          <h3 class="service-name">
            {{ booking.service_name || 'Not Specified' }}
          </h3>
          <span class="status-badge" :class="getStatusClass(booking.status)">
            {{ booking.status }}
          </span>
        </div>

        <div class="booking-details">
          <p><strong>📅 Date:</strong> {{ formatDate(booking.request_date) }}</p>
          <p><strong>👤 Professional:</strong> 
            {{ booking.professional?.name || 'Not Assigned' }}
          </p>
          <p><strong>💰 Price:</strong> {{ booking.price ? `$${booking.price}` : 'Not Available' }}</p>
          <p><strong>⏳ Duration:</strong> {{ booking.duration ? `${booking.duration} mins` : 'Not Available' }}</p>
        </div>

        <!-- Booking Actions -->
        <div class="booking-actions">
          <button @click="openEditModal(booking)" class="btn edit" 
            :disabled="!['pending'].includes(booking.status.toLowerCase())">
            Edit
          </button>
          <button @click="cancelBooking(booking.id)" class="btn cancel"
            :disabled="!['pending', 'accepted'].includes(booking.status.toLowerCase())">
            Cancel
          </button>
          <button @click="markCompleted(booking.id)" class="btn complete"
            :disabled="booking.status.toLowerCase() !== 'accepted'">
            Complete
          </button>
          <button 
            @click="payForService(booking)" 
            class="btn pay"
            :disabled="booking.status !== 'Completed'"
          >
            Pay
          </button>
          <button 
            @click="openReviewModal(booking)" 
            class="btn review"
            :disabled="!['paid', 'accepted', 'completed'].includes(booking.status.toLowerCase())"
          >
            Leave a Review
          </button>
        </div>
      </div>
    </div>

    <!-- Edit Modal -->
    <div v-if="isEditModalOpen" class="modal">
      <div class="modal-content">
        <h2>Edit Service Request</h2>
        
        <p><strong>Service:</strong> {{ editBooking?.service_name }}</p>
        
        <div class="form-group">
          <label for="editDate">Date and Time:</label>
          <input 
            type="datetime-local" 
            id="editDate" 
            v-model="editedDate"
            class="input-field"
          />
        </div>
        
        <div class="form-group">
          <label for="editDuration">Duration (minutes):</label>
          <input 
            type="number" 
            id="editDuration" 
            v-model="editedDuration"
            class="input-field"
            min="15"
            step="15"
          />
        </div>
        
        <div class="form-group">
          <label for="editNotes">Special Instructions:</label>
          <textarea 
            id="editNotes" 
            v-model="editedNotes"
            class="input-field"
            placeholder="Add any special instructions here..."
            rows="3"
          ></textarea>
        </div>
        
        <div v-if="editError" class="error-message">
          {{ editError }}
        </div>
        
        <div class="modal-actions">
          <button @click="closeEditModal" class="btn cancel-btn">Cancel</button>
          <button @click="saveEditChanges" class="btn save-btn">Save Changes</button>
        </div>
      </div>
    </div>
    
    <!-- Simplified Payment Modal -->
    <div v-if="isPaymentModalOpen" class="modal">
      <div class="modal-content">
        <h2>Payment for {{ paymentBooking?.service_name }}</h2>
        
        <div class="payment-details">
          <p><strong>Service:</strong> {{ paymentBooking?.service_name }}</p>
          <p><strong>Professional:</strong> {{ paymentBooking?.professional?.name || 'Not Assigned' }}</p>
          <p><strong>Amount:</strong> {{ paymentAmount }}</p>
          <p><strong>Date:</strong> {{ formatDate(paymentBooking?.request_date) }}</p>
        </div>
        
        <div class="form-group">
          <label for="paymentMethod">Payment Method:</label>
          <select 
            id="paymentMethod" 
            v-model="paymentMethod"
            class="input-field"
          >
            <option 
              v-for="method in paymentMethods" 
              :key="method.value" 
              :value="method.value"
            >
              {{ method.label }}
            </option>
          </select>
        </div>
        
        <!-- PayPal Instructions -->
        <div v-if="paymentMethod === 'paypal'" class="payment-info">
          <p>You will be redirected to PayPal to complete your payment after clicking Process Payment.</p>
        </div>
        
        <!-- Bank Transfer Instructions -->
        <div v-if="paymentMethod === 'bank_transfer'" class="payment-info">
          <p>Please use the following details for bank transfer:</p>
          <p><strong>Account Name:</strong> Service Provider Company</p>
          <p><strong>Account Number:</strong> 1234567890</p>
          <p><strong>Routing Number:</strong> 987654321</p>
          <p><strong>Reference:</strong> Booking #{{ paymentBooking?.id }}</p>
        </div>
        
        <div v-if="paymentError" class="error-message">
          {{ paymentError }}
        </div>
        
        <div class="modal-actions">
          <button @click="closePaymentModal" class="btn cancel-btn">Cancel</button>
          <button 
            @click="processPayment" 
            class="btn save-btn"
            :disabled="paymentLoading"
          >
            {{ paymentLoading ? 'Processing...' : 'Process Payment' }}
          </button>
        </div>
      </div>
    </div>

    <!-- Review Modal -->
    <div v-if="isReviewModalOpen" class="modal">
      <div class="modal-content">
        <h2>Leave a Review</h2>
        
        <p><strong>Service:</strong> {{ selectedBooking?.service_name }}</p>
        <p><strong>Professional:</strong> {{ selectedBooking?.professional?.name || 'Not Assigned' }}</p>

        <!-- Star rating component -->
        <StarRating v-model="rating" />

        <!-- Review text -->
        <textarea v-model="reviewText" placeholder="Write your review..." class="input-field"></textarea>

        <div class="modal-actions">
          <button @click="submitReview" class="btn save-btn">Submit</button>
          <button @click="closeReviewModal" class="btn cancel-btn">Close</button>
        </div>
      </div>
    </div>
  </div>
</template>


<script>
import StarRating from 'vue3-star-ratings';
import axios from "axios";

export default {
  components: {
    StarRating, // Register the component
  },
  name: "CustomerBookings",
  data() {
    return {
      bookings: [],
      loading: true,
      error: null,
      currentFilter: "all",
      statusFilters: [
        { label: "All Requests", value: "all" },
        { label: "Pending", value: "Pending" },
        { label: "Completed", value: "Completed" },
        { label: "Paid", value: "Paid" },
        { label: "Cancelled", value: "Cancelled" },
      ],
      isReviewModalOpen: false,
      selectedBooking: null,
      rating: 0,
      reviewText: "",
      apiBaseUrl: "http://127.0.0.1:5000/api",
      
      // Edit modal data
      isEditModalOpen: false,
      editBooking: null,
      editedDate: "",
      editedDuration: 0,
      editedNotes: "",
      editError: "",
      
      // Simplified payment modal data
      isPaymentModalOpen: false,
      paymentBooking: null,
      paymentMethod: "credit_card", // Default payment method
      paymentMethods: [
        { value: "credit_card", label: "Credit Card" },
        { value: "debit_card", label: "Debit Card" },
        { value: "paypal", label: "PayPal" },
        { value: "bank_transfer", label: "Bank Transfer" }
      ],
      paymentLoading: false,
      paymentError: ""
    };
  },
  computed: {
    filteredBookings() {
      if (this.currentFilter === "all") {
        return this.bookings;
      }
      return this.bookings.filter(
        (booking) => booking.status.toLowerCase() === this.currentFilter.toLowerCase()
      );
    },
    paymentAmount() {
      if (!this.paymentBooking || !this.paymentBooking.price) {
        return "N/A";
      }
      return `$${this.paymentBooking.price}`;
    }
  },
  created() {
    this.setupAxiosInterceptors();
    this.fetchBookings();
  },
  methods: {
    setRating(star) {
      this.rating = star;
    },
    
    setupAxiosInterceptors() {
      axios.interceptors.request.use((config) => {
        const token = localStorage.getItem("token");
        if (token) {
          config.headers['Authorization'] = `Bearer ${token}`;
        }
        return config;
      }, (error) => {
        return Promise.reject(error);
      });
    },
    
    async fetchBookings() {
      this.loading = true;
      try {
        const token = localStorage.getItem("token");
        if (!token) {
          this.error = "Authentication token missing. Please log in.";
          this.loading = false;
          return;
        }
        const response = await axios.get("/my-bookings");
        
        // Directly use the bookings array from the response
        this.bookings = response.data.bookings;
        
        console.log("Processed bookings:", this.bookings);
        this.loading = false;
      } catch (err) {
        console.error("Fetch bookings error:", err.response ? err.response.data : err.message);
        this.error = "Failed to fetch bookings. Try again later.";
        this.loading = false;
      }
    },
    
    async updateBookingStatus(id, status) {
      try {
        const token = localStorage.getItem("token");
        if (!token) {
          this.error = "Authentication token missing. Please log in.";
          return false;
        }

        const response = await axios.put(`/update-booking-status/${id}`, 
          { status }
        );

        // Update the local bookings list to reflect the status change
        const bookingIndex = this.bookings.findIndex(booking => booking.id === id);
        if (bookingIndex !== -1) {
          this.bookings[bookingIndex].status = status;
        }

        // Optional: Show success message
        alert(response.data.message);
        return true;
      } catch (err) {
        console.error("Failed to update booking status:", err.response ? err.response.data : err.message);
        
        // Show error message
        const errorMsg = err.response?.data?.error || "Failed to update booking status";
        alert(errorMsg);
        return false;
      }
    },
    
    async cancelBooking(id) {
      const confirmed = confirm("Are you sure you want to cancel this booking?");
      if (confirmed) {
        const success = await this.updateBookingStatus(id, "Cancelled");
        if (success) {
          console.log(`Booking ${id} cancelled successfully`);
        }
      }
    },
    
    async markCompleted(id) {
      const confirmed = confirm("Mark this booking as completed?");
      if (confirmed) {
        const success = await this.updateBookingStatus(id, "Completed");
        if (success) {
          console.log(`Booking ${id} marked as completed`);
        }
      }
    },
    
    formatDate(dateString) {
      if (!dateString) return 'N/A';
      const date = new Date(dateString);
      return date.toLocaleString("en-US", { 
        year: 'numeric', 
        month: "short", 
        day: "numeric", 
        hour: "numeric", 
        minute: "2-digit" 
      });
    },
    
    getStatusClass(status) {
      return {
        Pending: "status-pending",
        Accepted: "status-accepted",
        Completed: "status-completed",
        Cancelled: "status-cancelled",
        Paid: "status-paid"
      }[status] || "status-default";
    },
    
    openReviewModal(booking) {
      console.log("Opening review modal for:", booking); // Debugging log
      if (['paid', 'accepted', 'completed'].includes(booking.status.toLowerCase())) {
        this.selectedBooking = booking;
        this.isReviewModalOpen = true;
        this.rating = 0;
        this.reviewText = "";
        console.log("Modal state:", this.isReviewModalOpen); // Debugging log
      } else {
        console.log("Cannot review this booking, status:", booking.status);
      }
    },
    
    closeReviewModal() {
      this.isReviewModalOpen = false;
      this.selectedBooking = null;
      this.rating = 0;
      this.reviewText = "";
    },
    
    async submitReview() {
      const token = localStorage.getItem("token") || sessionStorage.getItem("token");

      if (!token) {
        alert("You must be logged in to submit a review.");
        return;
      }

      if (!this.rating || !this.reviewText.trim()) {
        alert("Please provide a rating and a review before submitting.");
        return;
      }

      try {
        const response = await axios.post(
          `${this.apiBaseUrl}/service-requests/${this.selectedBooking.id}/review`,
          {
            rating: this.rating,
            review_text: this.reviewText,
          },
          {
            headers: {
              Authorization: `Bearer ${token}`,
              "Content-Type": "application/json",
            },
          }
        );

        alert(response.data.message);
        this.closeReviewModal();
      } catch (error) {
        console.error("Error submitting review:", error);
        alert(error.response?.data?.error || "Failed to submit review.");
      }
    },
    
    // Edit booking methods
    openEditModal(booking) {
      // Only allow editing for pending bookings
      if (booking.status.toLowerCase() !== 'pending') {
        alert("Only pending bookings can be edited.");
        return;
      }
      
      this.editBooking = booking;
      
      // Set initial values from booking
      // Convert the date string to a format compatible with datetime-local input
      const requestDate = new Date(booking.request_date);
      const year = requestDate.getFullYear();
      const month = String(requestDate.getMonth() + 1).padStart(2, '0');
      const day = String(requestDate.getDate()).padStart(2, '0');
      const hours = String(requestDate.getHours()).padStart(2, '0');
      const minutes = String(requestDate.getMinutes()).padStart(2, '0');
      
      this.editedDate = `${year}-${month}-${day}T${hours}:${minutes}`;
      this.editedDuration = booking.duration || 60; // Default to 60 minutes if not available
      
      this.isEditModalOpen = true;
      this.editError = "";
    },
    
    closeEditModal() {
      this.isEditModalOpen = false;
      this.editBooking = null;
      this.editError = "";
    },
    
    async saveEditChanges() {
      this.editError = "";
      
      // Validate inputs
      if (!this.editedDate) {
        this.editError = "Please select a date and time";
        return;
      }
      
      if (!this.editedDuration || this.editedDuration < 15) {
        this.editError = "Duration must be at least 15 minutes";
        return;
      }
      
      try {
        const token = localStorage.getItem("token");
        if (!token) {
          this.editError = "Authentication token missing. Please log in.";
          return;
        }
        
        const bookingData = {
          request_date: new Date(this.editedDate).toISOString(),
          duration: parseInt(this.editedDuration),
          notes: this.editedNotes
        };
        
        // Make API call to update the booking
        const response = await axios.put(
          `${this.apiBaseUrl}/update-booking/${this.editBooking.id}`,
          bookingData
        );
        
        // Update local data
        const bookingIndex = this.bookings.findIndex(b => b.id === this.editBooking.id);
        if (bookingIndex !== -1) {
          // Update the booking with new values
          this.bookings[bookingIndex].request_date = bookingData.request_date;
          this.bookings[bookingIndex].duration = bookingData.duration;
          this.bookings[bookingIndex].notes = bookingData.notes;
        }
        
        alert(response.data.message || "Booking updated successfully!");
        this.closeEditModal();
      } catch (error) {
        console.error("Error updating booking:", error);
        this.editError = error.response?.data?.error || "Failed to update booking";
      }
    },
    
    // Simplified payment methods
    payForService(booking) {
      // Fix: Check for exact status match (case-sensitive)
      if (booking.status !== 'Completed') {
        alert("Only completed services can be paid for.");
        return;
      }
      
      this.paymentBooking = booking;
      this.isPaymentModalOpen = true;
      this.paymentError = "";
      this.paymentLoading = false;
      
      // Reset payment form
      this.paymentMethod = "credit_card";
    },
    
    closePaymentModal() {
      this.isPaymentModalOpen = false;
      this.paymentBooking = null;
      this.paymentError = "";
      this.paymentLoading = false;
    },
    
    // Simplified payment processing (no card validation needed)
    async processPayment() {
      this.paymentError = "";
      this.paymentLoading = true;
      
      try {
        const token = localStorage.getItem("token");
        if (!token) {
          this.paymentError = "Authentication token missing. Please log in.";
          this.paymentLoading = false;
          return;
        }
        
        // Prepare payment data - just send the method
        const paymentData = {
          payment_method: this.paymentMethod
        };
        
        // Make API call to process payment
        const response = await axios.post(
          `${this.apiBaseUrl}/bookings/${this.paymentBooking.id}/pay`,
          paymentData
        );
        
        // Update local booking status
        const bookingIndex = this.bookings.findIndex(b => b.id === this.paymentBooking.id);
        if (bookingIndex !== -1) {
          this.bookings[bookingIndex].status = "Paid";
        }
        
        // Show success message and close modal
        alert(response.data.message || "Payment processed successfully!");
        this.closePaymentModal();
        
      } catch (error) {
        console.error("Payment error:", error);
        this.paymentError = error.response?.data?.error || "Failed to process payment. Please try again.";
      } finally {
        this.paymentLoading = false;
      }
    }
  }
};
</script>

<style scoped>
/* General Styles */
.bookings-container {
  padding: 2rem;
  max-width: 1200px;
  margin: 0 auto;
  color: #4a4a4a;
  background: transparent;
}

.title {
  font-weight: 700;
  margin-bottom: 1.5rem;
  color: #8a4fff;
  position: relative;
  display: inline-block;
  padding-bottom: 8px;
  font-size: 24px;
}

.title::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 0;
  height: 3px;
  width: 70%;
  background: linear-gradient(90deg, #c3adee, transparent);
  border-radius: 2px;
}

/* Filters */
.filters {
  display: flex;
  gap: 15px;
  margin-bottom: 1.5rem;
  flex-wrap: wrap;
}

.filters button {
  padding: 12px 20px;
  background: rgba(255, 255, 255, 0.8);
  border: 1px solid rgba(0, 0, 0, 0.05);
  color: #6a6a6a;
  cursor: pointer;
  border-radius: 10px;
  font-weight: 600;
  font-size: 16px;
  box-shadow: 0 2px 15px rgba(0, 0, 0, 0.05);
  transition: all 0.3s ease;
  backdrop-filter: blur(5px);
}

.filters button:hover {
  transform: translateY(-2px);
  box-shadow: 0 5px 15px rgba(138, 79, 255, 0.1);
}

.filters button.active {
  background: linear-gradient(135deg, #c3adee 0%, #a98ade 100%);
  color: white;
}

/* Booking Cards */
.booking-card {
  background-color: rgba(255, 255, 255, 0.85);
  backdrop-filter: blur(10px);
  padding: 20px;
  border-radius: 15px;
  margin-bottom: 20px;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.05);
  transition: transform 0.3s ease, box-shadow 0.3s ease;
  border: 1px solid rgba(0, 0, 0, 0.05);
}

.booking-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 15px 35px rgba(138, 79, 255, 0.1);
}

.booking-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
  padding-bottom: 15px;
  border-bottom: 1px solid rgba(0, 0, 0, 0.05);
}

.service-name {
  font-size: 1.25rem;
  font-weight: 600;
  margin: 0;
  color: #4a4a4a;
}

.status-badge {
  padding: 8px 15px;
  border-radius: 20px;
  font-weight: 600;
  text-transform: uppercase;
  font-size: 0.8em;
  letter-spacing: 0.5px;
  color: white;
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
  backdrop-filter: blur(5px);
}

.status-pending { 
  background: linear-gradient(135deg, #ff9a9e, #fad0c4) !important; 
  color: #ff6b6b ;
}

.status-accepted { 
  background: linear-gradient(135deg, #a1c4fd, #c2e9fb) !important; 
  color: #4a7fd1 !important;
}

.status-completed { 
  background: linear-gradient(135deg, #d4fc79, #96e6a1) !important; 
  color: #4ecdc4 !important;
}

.status-cancelled { 
  background: linear-gradient(135deg, #ffcfdf, #fefdca) !important; 
  color: #ff6b9e !important;
}

.booking-details {
  padding: 10px 0;
}

.booking-details p {
  margin: 8px 0;
  color: #6a6a6a;
}

.booking-details strong {
  color: #4a4a4a;
}

/* Modals */
.modal {
  display: flex;
  justify-content: center;
  align-items: center;
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.5);
  z-index: 1000;
  backdrop-filter: blur(5px);
}

.modal-content {
  background-color: white;
  padding: 25px;
  border-radius: 15px;
  width: 500px;
  max-width: 90%;
  color: #4a4a4a;
  box-shadow: 0 20px 50px rgba(0, 0, 0, 0.25);
}

.modal-content h2 {
  margin-top: 0;
  color: #8a4fff;
  margin-bottom: 20px;
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

.input-field {
  width: 100%;
  padding: 12px 15px;
  border: 1px solid rgba(0, 0, 0, 0.05);
  border-radius: 10px;
  background-color: #f8f9fa;
  color: #4a4a4a;
  font-size: 16px;
  transition: all 0.3s ease;
  box-shadow: 0 2px 15px rgba(0, 0, 0, 0.05);
}

.input-field:focus {
  outline: none;
  box-shadow: 0 2px 20px rgba(138, 79, 255, 0.15);
  border-color: #a98ade;
}

textarea.input-field {
  resize: vertical;
  min-height: 100px;
}

.error-message {
  color: #e74c3c;
  background: rgba(231, 76, 60, 0.1);
  padding: 12px 15px;
  border-radius: 10px;
  margin-bottom: 20px;
  border-left: 4px solid #e74c3c;
  display: flex;
  align-items: center;
}

/* Buttons */
.booking-actions {
  margin-top: 20px;
  display: flex;
  gap: 15px;
  flex-wrap: wrap;
}

.btn {
  padding: 12px 20px;
  border-radius: 10px;
  border: none;
  cursor: pointer;
  font-weight: 600;
  font-size: 16px;
  min-width: 100px;
  text-align: center;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease;
}

.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn.edit { 
  background-color: #f3e7ff; 
  color: #9c27b0; 
}

.btn.cancel { 
  background-color: #fff4e6; 
  color: #ff9800; 
}

.btn.complete { 
  background-color: #e8f5e9; 
  color: #4CAF50; 
}

.btn.pay { 
  background-color: #e3f2fd; 
  color: #2196F3; 
}

.btn.review { 
  background-color: #ede7f6; 
  color: #673ab7; 
}

.btn:hover:not(:disabled) {
  transform: translateY(-2px);
}

.btn.edit:hover:not(:disabled) { 
  background-color: #9c27b0; 
  color: white; 
}

.btn.cancel:hover:not(:disabled) { 
  background-color: #ff9800; 
  color: white; 
}

.btn.complete:hover:not(:disabled) { 
  background-color: #4CAF50; 
  color: white; 
}

.btn.pay:hover:not(:disabled) { 
  background-color: #2196F3; 
  color: white; 
}

.btn.review:hover:not(:disabled) { 
  background-color: #673ab7; 
  color: white; 
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 15px;
  margin-top: 25px;
}

.btn.cancel-btn {
  background-color: #e2e8f0;
  color: #6a6a6a;
}

.btn.cancel-btn:hover {
  background-color: #cbd5e1;
}

.btn.save-btn {
  background-color: #d1f7e0;
  color: #4ecdc4;
}

.btn.save-btn:hover {
  background-color: #4ecdc4;
  color: white;
}

/* Loading and error states */
.loading, .error {
  text-align: center;
  padding: 30px;
  background-color: rgba(255, 255, 255, 0.7);
  border-radius: 15px;
  color: #8a4fff;
  font-weight: 500;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.05);
  backdrop-filter: blur(10px);
}

.error {
  color: #e74c3c;
}

/* Modal and form styles */
.modal {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.modal-content {
  background-color: white;
  border-radius: 8px;
  padding: 24px;
  width: 90%;
  max-width: 500px;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
}

.form-group {
  margin-bottom: 16px;
}

.form-row {
  display: flex;
  gap: 16px;
  margin-bottom: 16px;
}

.half {
  flex: 1;
}

.input-field {
  width: 100%;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
}

textarea.input-field {
  resize: vertical;
  min-height: 80px;
}

.error-message {
  color: #e53935;
  margin: 16px 0;
  padding: 8px;
  background-color: rgba(229, 57, 53, 0.1);
  border-radius: 4px;
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  margin-top: 20px;
}

.btn {
  padding: 8px 16px;
  border-radius: 4px;
  cursor: pointer;
  font-weight: 500;
  border: none;
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.cancel-btn {
  background-color: #f5f5f5;
  color: #333;
}

.save-btn {
  background-color: #4caf50;
  color: white;
}

.payment-details {
  background-color: #f9f9f9;
  padding: 12px;
  border-radius: 6px;
  margin-bottom: 20px;
}

.payment-info {
  background-color: #e3f2fd;
  padding: 12px;
  border-radius: 6px;
  margin-top: 12px;
  margin-bottom: 12px;
}

.card-details {
  border: 1px solid #e0e0e0;
  padding: 16px;
  border-radius: 6px;
  margin-top: 12px;
  margin-bottom: 12px;
}

/* Status badge colors */
.status-badge {
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 500;
}

.status-pending {
  background-color: #ffecb3;
  color: #ff8f00;
}

.status-accepted {
  background-color: #b3e5fc;
  color: #0277bd;
}

.status-completed {
  background-color: #c8e6c9;
  color: #2e7d32;
}

.status-cancelled {
  background-color: #ffcdd2;
  color: #c62828;
}

.status-paid {
  background-color: #e8f5e9;
  color: #1b5e20;
}

.status-default {
  background-color: #eeeeee;
  color: #616161;
}

/* Responsive adjustments */
@media (max-width: 768px) {
  .bookings-container {
    padding: 1rem;
  }
  
  .filters {
    gap: 10px;
  }
  
  .filters button {
    padding: 10px 15px;
    font-size: 14px;
  }
  
  .booking-actions {
    justify-content: space-between;
  }
  
  .btn {
    min-width: 80px;
    font-size: 14px;
    padding: 10px 15px;
  }
  
  .modal-content {
    padding: 15px;
  }
}
</style>