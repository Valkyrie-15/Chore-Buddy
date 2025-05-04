<template>
  <div class="dashboard-container">
    <div class="dashboard-card">
      <div class="card-header">
        <h2 class="section-title">Service Requests</h2>
        
        <!-- Quick stats -->
        <div class="d-flex gap-3">
          <div class="stat-card bg-soft-light py-2 px-3">
            <i class="fas fa-clock me-2"></i>
            <span>Pending: {{pendingCount}}</span>
          </div>
          <div class="stat-card gradient-success text-white py-2 px-3">
            <i class="fas fa-check-circle me-2"></i>
            <span>Completed: {{completedCount}}</span>
          </div>
          <div class="stat-card bg-soft-secondary py-2 px-3">
            <i class="fas fa-ban me-2"></i>
            <span>Cancelled: {{cancelledCount}}</span>
          </div>
        </div>
      </div>

      <div class="card-body p-0">
        <!-- Notification -->
        <div v-if="notification.show" class="p-4">
          <div :class="[
            'alert-message',
            notification.type === 'success' ? 'alert-success' :
            notification.type === 'error' ? 'alert-error' :
            'alert-info'
          ]">
            <i :class="[
              'me-2',
              notification.type === 'success' ? 'fas fa-check-circle' :
              notification.type === 'error' ? 'fas fa-exclamation-circle' :
              'fas fa-info-circle'
            ]"></i>
            <div>
              <div class="fw-bold">{{ notification.title }}</div>
              <div>{{ notification.text }}</div>
            </div>
          </div>
        </div>
        
        <!-- Filters -->
        <div class="p-4 border-bottom border-light">
          <div class="row g-0">
            <div class="col-12 col-md-4">
              <h6 class="section-subtitle mb-2">Status Filter</h6>
              <div class="filter-wrapper">
                <i class="fas fa-filter filter-icon"></i>
                <select 
                  v-model="currentFilter" 
                  class="filter-select"
                >
                  <option 
                    v-for="filter in statusFilters" 
                    :key="filter.value"
                    :value="filter.value"
                  >
                    {{ filter.label }}
                  </option>
                </select>
              </div>
            </div>
          </div>
        </div>
        
        <!-- Loading state -->
        <div v-if="loading" class="loading-container">
          <div class="spinner-border text-primary" role="status">
            <span class="visually-hidden">Loading...</span>
          </div>
        </div>
        
        <!-- No requests message -->
        <div v-else-if="filteredRequests.length === 0" class="no-results">
          <i class="fas fa-inbox fa-3x"></i>
          <p>No service requests found</p>
          <p v-if="currentFilter !== 'all'" class="text-muted">
            Try changing your filter to see other requests
          </p>
        </div>
        
        <!-- Requests list -->
        <div v-else class="requests-grid">
          <div 
            v-for="request in filteredRequests" 
            :key="request.id"
            class="request-card"
          >
            <div class="card-header">
              <h3 class="service-title">{{ request.service_name }}</h3>
              <span 
                :class="getStatusClass(request.status)"
                class="status-tag"
              >
                {{ formatStatus(request.status) }}
              </span>
            </div>
            <div class="card-body">
              <div class="service-detail">
                <i class="fas fa-user icon"></i>
                <span><strong>Customer:</strong> {{ request.customer_name }}</span>
              </div>
              <div class="service-detail">
                <i class="fas fa-phone-alt icon"></i>
                <span><strong>Contact:</strong> {{ request.customer_contact }}</span>
              </div>
              <div class="service-detail">
                <i class="fas fa-phone-alt icon"></i>
                <span><strong>Address:</strong> {{ request.customer_address }}</span>
              </div>
              <div class="service-detail">
                <i class="fas fa-calendar-alt icon"></i>
                <span><strong>Date:</strong> {{ formatDate(request.request_date) }}</span>
              </div>
              <div class="service-detail">
                <i class="fas fa-map-marker-alt icon"></i>
                <span><strong>Location:</strong> {{ request.location }}</span>
              </div>
              <div class="service-detail">
                <i class="fas fa-hourglass-half icon"></i>
                <span><strong>Duration:</strong> {{ request.duration }} mins</span>
              </div>
              <div class="service-detail">
                <i class="fas fa-dollar-sign icon"></i>
                <span><strong>Price:</strong> ${{ request.price }}</span>
              </div>
            </div>
            
            <!-- Action buttons -->
            <div class="action-buttons">
              <!-- Accept/Reject for pending status -->
              <button 
                v-if="request.status === 'pending'" 
                @click="updateRequestStatus(request.id, 'accepted')"
                class="btn action-btn accept-btn"
              >
                <i class="fas fa-check me-2"></i> Accept
              </button>
              <button 
                v-if="request.status === 'pending'" 
                @click="updateRequestStatus(request.id, 'rejected')"
                class="btn action-btn reject-btn"
              >
                <i class="fas fa-times me-2"></i> Reject
              </button>
              
              <!-- Cancel button - available for pending and accepted statuses -->
              <button 
                v-if="['pending', 'accepted'].includes(request.status)" 
                @click="updateRequestStatus(request.id, 'Cancelled')"
                class="btn action-btn cancel-btn"
              >
                <i class="fas fa-ban me-2"></i> Cancel
              </button>
              
              <!-- Mark Complete button - available for accepted status -->
              <button 
                v-if="request.status === 'accepted'" 
                @click="updateRequestStatus(request.id, 'completed')"
                class="btn action-btn complete-btn"
              >
                <i class="fas fa-flag-checkered me-2"></i> Complete
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  name: 'ProfessionalRequestsDashboard',
  data() {
    return {
      requests: [],
      loading: true,
      error: null,
      currentFilter: 'all',
      notification: {
        show: false,
        title: '',
        text: '',
        type: 'info', // success, error, info
        timeout: null
      },
      statusFilters: [
        { label: 'All Requests', value: 'all' },
        { label: 'Pending', value: 'pending' },
        { label: 'Accepted', value: 'accepted' },
        { label: 'Completed', value: 'completed' },
        { label: 'Paid', value: 'Paid' },
        { label: 'Rejected', value: 'rejected' },
        { label: 'Cancelled', value: 'Cancelled' }
      ]
    };
  },
  
  computed: {
    pendingCount() {
      return this.requests.filter(req => req.status === 'pending').length;
    },
    completedCount() {
      return this.requests.filter(req => req.status === 'completed').length;
    },
    cancelledCount() {
      return this.requests.filter(req => req.status === 'Cancelled').length;
    },
    // Filter requests client-side
    filteredRequests() {
      if (this.currentFilter === 'all') {
        return this.requests;
      }
      return this.requests.filter(req => req.status === this.currentFilter);
    }
  },
  
  mounted() {
    this.fetchRequests();
    // Add debugging
    console.log('Component mounted');
  },
  
  methods: {
    getAuthToken() {
      return localStorage.getItem('token');
    },
    
    getAuthHeaders() {
      const token = this.getAuthToken();
      if (!token) {
        console.error('No authentication token found in local storage');
        return {};
      }
      return {
        'Authorization': `Bearer ${token}`
      };
    },
    
    showNotification(title, text, type = 'info') {
      // Clear any existing timeout
      if (this.notification.timeout) {
        clearTimeout(this.notification.timeout);
      }
      
      // Set notification
      this.notification = {
        show: true,
        title,
        text,
        type,
        timeout: null
      };
      
      // Hide after 3 seconds
      this.notification.timeout = setTimeout(() => {
        this.notification.show = false;
      }, 3000);
    },
    
    async fetchRequests() {
      this.loading = true;
      try {
        // Always fetch all requests - we'll filter client-side for better UX
        const url = '/api/professional/requests';
        
        const response = await axios.get(url, { 
          headers: this.getAuthHeaders() 
        });
        
        if (response.data.success) {
          this.requests = response.data.requests;
          // Debug output
          console.log('All requests:', this.requests);
          console.log('Cancelled requests:', this.requests.filter(r => r.status === 'Cancelled'));
        } else {
          this.error = 'Failed to load requests';
        }
      } catch (err) {
        console.error('Error fetching requests:', err);
        this.error = err.response?.data?.error || 'An error occurred while fetching requests';
        
        // Handle authentication errors
        if (err.response?.status === 401) {
          // Redirect to login page or refresh token as needed
          this.$router.push('/login');
        }
      } finally {
        this.loading = false;
      }
    },
    
    async updateRequestStatus(requestId, newStatus) {
      try {
        const response = await axios.patch(`/api/requests/${requestId}/status`, {
          status: newStatus
        }, {
          headers: this.getAuthHeaders()
        });
        
        if (response.data.success) {
          // Update local state to reflect the change
          const index = this.requests.findIndex(req => req.id === requestId);
          if (index !== -1) {
            this.requests[index].status = newStatus;
            console.log(`Request ${requestId} status updated to ${newStatus}`);
          }
          
          // Show success notification
          this.showNotification(
            'Success', 
            `Request successfully ${this.formatActionText(newStatus)}`, 
            'success'
          );
          
          // Refresh the list to ensure we have the latest data
          this.fetchRequests();
        }
      } catch (err) {
        console.error('Error updating request status:', err);
        this.showNotification(
          'Error',
          err.response?.data?.error || 'Failed to update request status',
          'error'
        );
        
        // Handle authentication errors
        if (err.response?.status === 401) {
          this.$router.push('/login');
        }
      }
    },
    
    formatActionText(status) {
      switch(status) {
        case 'accepted': return 'accepted';
        case 'rejected': return 'rejected';
        case 'Cancelled': return 'cancelled';
        case 'Paid': return 'paid';
        case 'completed': return 'marked as completed';
        default: return 'updated';
      }
    },
    
    formatDate(dateString) {
      const date = new Date(dateString);
      return date.toLocaleString('en-US', {
        month: 'short',
        day: 'numeric',
        hour: 'numeric',
        minute: '2-digit'
      });
    },
    
    formatStatus(status) {
      return status.charAt(0).toUpperCase() + status.slice(1);
    },
    
    getStatusClass(status) {
      const statusClasses = {
        pending: 'status-warning',
        accepted: 'status-primary',
        completed: 'status-success',
        paid: 'status-success',
        rejected: 'status-danger',
        Cancelled: 'status-secondary'
      };
      
      return statusClasses[status] || 'status-secondary';
    }
  }
};
</script>

<style scoped>
.dashboard-container {
  padding: 2rem;
  max-width: 1200px;
  margin: 0 auto;
}

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

.section-subtitle {
  color: #8a4fff;
  font-weight: 600;
}

.stat-card {
  background-color: rgba(255, 255, 255, 0.8);
  backdrop-filter: blur(5px);
  border-radius: 15px;
  overflow: hidden;
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.05);
  transition: all 0.3s ease;
  padding: 10px 15px;
  margin-bottom: 0;
  border: 1px solid rgba(0, 0, 0, 0.05);
  display: flex;
  align-items: center;
}

.stat-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 10px 20px rgba(0, 0, 0, 0.1);
}

.gradient-primary {
  background: linear-gradient(135deg, #8a4fff 0%, #a98ade 100%);
}

.gradient-success {
  background: linear-gradient(135deg, #4ecdc4 0%, #63e6be 100%);
}

.gradient-info {
  background: linear-gradient(135deg, #6a11cb 0%, #2575fc 100%);
}

.bg-soft-light {
  background-color: rgba(255, 255, 255, 0.8);
  color: #4a4a4a;
}

.filter-wrapper {
  position: relative;
}

.filter-icon {
  position: absolute;
  left: 15px;
  top: 50%;
  transform: translateY(-50%);
  color: #a98ade;
}

.filter-select {
  width: 100%;
  padding: 12px 15px 12px 40px;
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

.loading-container {
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 3rem;
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

.requests-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 20px;
  padding: 20px;
}

.request-card {
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

.request-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 15px 35px rgba(138, 79, 255, 0.1);
}

.request-card .card-header {
  padding: 15px 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.service-title {
  margin: 0;
  font-size: 1.1rem;
  font-weight: 600;
  flex-grow: 1;
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

.status-danger {
  background-color: #ff5252;
  color: white;
}

.status-secondary {
  background-color: #6c757d;
  color: white;
}

.request-card .card-body {
  padding: 15px 20px;
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

.alert-message {
  background-color: #fdf2f2;
  color: #e53e3e;
  padding: 12px 20px;
  margin: 15px;
  border-radius: 10px;
  display: flex;
  align-items: flex-start;
}

.alert-success {
  background-color: #f0fff4;
  color: #38a169;
  border-left: 4px solid #38a169;
}

.alert-error {
  background-color: #fdf2f2;
  color: #e53e3e;
  border-left: 4px solid #e53e3e;
}

.alert-info {
  background-color: #ebf8ff;
  color: #3182ce;
  border-left: 4px solid #3182ce;
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

.action-buttons {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  padding: 0 20px 20px;
}

.action-btn {
  padding: 10px 16px;
  font-size: 14px;
}

.accept-btn {
  background-color: #4ecdc4;
  color: white;
}

.accept-btn:hover {
  background-color: #63e6be;
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(78, 205, 196, 0.3);
}

.reject-btn {
  background-color: #ff5252;
  color: white;
}

.reject-btn:hover {
  background-color: #ff6b6b;
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(255, 82, 82, 0.3);
}

.cancel-btn {
  background-color: #ffb347;
  color: white;
}

.cancel-btn:hover {
  background-color: #ffcc80;
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(255, 179, 71, 0.3);
}

.complete-btn {
  background-color: #8a4fff;
  color: white;
}

.complete-btn:hover {
  background-color: #a98ade;
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(138, 79, 255, 0.3);
}

.pay-btn {
  background-color: #63e6be;
  color: white;
}

.pay-btn:hover {
  background-color: #77f9d1;
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(99, 230, 190, 0.3);
}

@media (max-width: 768px) {
  .dashboard-container {
    padding: 1rem;
  }
  
  .requests-grid {
    grid-template-columns: 1fr;
  }
  
  .card-header {
    flex-direction: column;
    gap: 10px;
    align-items: flex-start;
  }
}
</style>