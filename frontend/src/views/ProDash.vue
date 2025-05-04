<template>
  <div class="dashboard-container">
    <div class="row g-4">
      <div class="col-12">
        <div class="dashboard-card">
          <div class="card-body p-0">
            <div class="row g-0">
              <!-- Stats Cards -->
              <div class="col-12 col-md-4 border-end border-light">
                <div class="p-4">
                  <div class="row g-3">
                    <!-- Total Earnings Card -->
                    <div class="col-12">
                      <div class="stat-card gradient-primary text-white">
                        <div class="d-flex align-items-center">
                          <div class="flex-grow-1">
                            <h6 class="text-white-50 mb-2">Total Earnings</h6>
                            <h3 class="mb-0 font-weight-bold">
                              ${{ summary.total_earnings.toFixed(2) }}
                            </h3>
                          </div>
                          <div class="stat-icon">
                            <i class="fas fa-dollar-sign fa-2x opacity-75"></i>
                          </div>
                        </div>
                      </div>
                    </div>

                    <!-- Average Earnings Card -->
                    <div class="col-12">
                      <div class="stat-card gradient-success text-white">
                        <div class="d-flex align-items-center">
                          <div class="flex-grow-1">
                            <h6 class="text-white-50 mb-2">Avg. Earnings</h6>
                            <h3 class="mb-0 font-weight-bold">
                              ${{ summary.average_earnings_per_request.toFixed(2) }}
                            </h3>
                          </div>
                          <div class="stat-icon">
                            <i class="fas fa-chart-line fa-2x opacity-75"></i>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              <!-- Reviews and Filter Column -->
              <div class="col-12 col-md-4 border-end border-light">
                <div class="p-4">
                  <div class="stat-card bg-soft-light">
                    <div class="d-flex align-items-center">
                      <!-- Rating stars using direct FontAwesome icons instead of component -->
                      <div class="rating-stars me-3">
                        <i 
                          v-for="n in 5" 
                          :key="n" 
                          class="fas fa-star"
                          :class="n <= Math.round(averageRating) ? 'text-warning' : 'text-muted'"
                        ></i>
                      </div>
                      <div>
                        <h6 class="mb-0">{{ averageRating.toFixed(1) }} / 5</h6>
                        <small class="text-muted">
                          Total Reviews: {{ totalReviews }}
                        </small>
                      </div>
                    </div>
                  </div>

                  <div class="stat-card bg-soft-light mt-3">
                    <h6 class="section-subtitle mb-2">Status Filter</h6>
                    <div class="filter-wrapper">
                      <i class="fas fa-filter filter-icon"></i>
                      <select 
                        v-model="selectedStatus" 
                        @change="fetchRequests"
                        class="filter-select"
                      >
                        <option value="">All Statuses</option>
                        <option value="pending">Pending</option>
                        <option value="confirmed">Confirmed</option>
                        <option value="in_progress">In Progress</option>
                        <option value="completed">Completed</option>
                      </select>
                    </div>
                  </div>
                </div>
              </div>

              <!-- Quick Stats -->
              <div class="col-12 col-md-4">
                <div class="p-4">
                  <div class="stat-card gradient-info text-white">
                    <div class="d-flex align-items-center">
                      <div class="flex-grow-1">
                        <h6 class="text-white-50 mb-2">Total Requests</h6>
                        <h3 class="mb-0 font-weight-bold">
                          {{ requests.length }}
                        </h3>
                      </div>
                      <div class="stat-icon">
                        <i class="fas fa-clipboard-list fa-2x opacity-75"></i>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Upcoming Jobs Section -->
      <div class="col-12">
        <div class="dashboard-card">
          <div class="card-header">
            <h2 class="section-title">Upcoming Jobs</h2>
          </div>
          <div class="card-body p-0">
            <div v-if="error" class="alert-message">
              <i class="fas fa-exclamation-triangle me-2"></i>
              {{ error }}
            </div>

            <div v-if="loading" class="loading-container">
              <div class="spinner-border text-primary" role="status">
                <span class="visually-hidden">Loading...</span>
              </div>
            </div>

            <div v-else-if="requests.length === 0" class="no-results">
              <i class="fas fa-inbox fa-3x"></i>
              <p>No service requests found.</p>
            </div>

            <div v-else class="requests-grid">
              <div 
                v-for="request in requests" 
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
                    <i class="fas fa-calendar-alt icon"></i>
                    <span><strong>Date:</strong> {{ formatDate(request.request_date) }}</span>
                  </div>
                  <div class="service-detail">
                    <i class="fas fa-clock icon"></i>
                    <span><strong>Duration:</strong> {{ request.duration }} mins</span>
                  </div>
                  <div class="service-detail" v-if="request.service_price">
                    <i class="fas fa-dollar-sign icon"></i>
                    <span><strong>Price:</strong> ${{ request.service_price.toFixed(2) }}</span>
                  </div>
                </div>
                
                <button class="btn action-btn">
                  <i class="fas fa-check-circle me-2"></i> Update Status
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';
import { format, parseISO } from 'date-fns';

export default {
  name: 'ProfessionalRequestsComponent',
  data() {
    return {
      requests: [],
      loading: true,
      error: null,
      selectedStatus: '',
      summary: {
        total_earnings: 0,
        total_completed_requests: 0,
        average_earnings_per_request: 0
      },
      averageRating: 0,
      totalReviews: 0,
      professionalId: null,
      currentPage: 1,
      isLoadingReviews: false
    };
  },
  mounted() {
    this.fetchProfessionalId();
  },
  methods: {
    async fetchProfessionalId() {
      try {
        const storedUser = localStorage.getItem('user');
        const userData = JSON.parse(storedUser);

        if (userData && userData.id) {
          const response = await axios.get(`/api/user/${userData.id}/professional`);
          
          if (response.data && response.data.professional_id) {
            this.professionalId = response.data.professional_id;
            
            // Parallel calls
            Promise.all([
              this.fetchRequests(),
              this.fetchEarnings(),
              this.fetchProfessionalReviews(this.professionalId)
            ]);
          }
        }
      } catch (error) {
        console.error('Error fetching professional ID:', error);
      }
    },
    async fetchRequests() {
      this.loading = true;
      this.error = null;

      const token = localStorage.getItem('token');
      
      if (!token) {
        this.error = 'No authentication token found';
        this.loading = false;
        return;
      }

      try {
        const response = await axios.get('/api/professional/requests', {
          params: { 
            status: this.selectedStatus 
          },
          headers: {
            'Authorization': `Bearer ${token}`
          }
        });

        this.requests = response.data.requests;
      } catch (error) {
        this.handleErrorResponse(error);
      } finally {
        this.loading = false;
      }
    },
    async fetchEarnings() {
      const token = localStorage.getItem('token');
      
      if (!token) {
        return;
      }

      try {
        const response = await axios.get('/api/professional/earnings', {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        });

        this.summary = response.data.summary || {
          total_earnings: 0,
          total_completed_requests: 0,
          average_earnings_per_request: 0
        };
      } catch (error) {
        console.error('Error fetching earnings:', error);
      }
    },
    async fetchProfessionalReviews(professionalId) {
      if (!professionalId) return;
      
      this.isLoadingReviews = true;
      const token = localStorage.getItem('token');
      
      if (!token) {
        console.error('No authentication token found for reviews');
        this.isLoadingReviews = false;
        return;
      }

      try {
        const response = await axios.get(`/admin/professional/${professionalId}/reviews`, {
          params: {
            page: this.currentPage,
            per_page: 5
          },
          headers: {
            'Authorization': `Bearer ${token}`
          }
        });

        // Update review statistics from the response
        this.averageRating = response.data.average_rating || 0;
        this.totalReviews = response.data.total_reviews || 0;
      } catch (error) {
        console.error('Error fetching professional reviews:', error);
        // If admin endpoint fails, fall back to public endpoint
        this.fetchPublicReviews(professionalId);
      } finally {
        this.isLoadingReviews = false;
      }
    },
    async fetchPublicReviews(professionalId) {
      try {
        const response = await axios.get(`/api/professional/${professionalId}/reviews`, {
          params: {
            page: 1,
            per_page: 1
          }
        });

        this.averageRating = response.data.average_rating || 0;
        this.totalReviews = response.data.total_reviews || 0;
      } catch (error) {
        console.error('Error fetching public reviews:', error);
      }
    },
    handleErrorResponse(error) {
      console.error('Error fetching requests:', error);
      
      if (error.response) {
        this.error = error.response.data.msg || 'An error occurred';
        console.log('Error Response:', error.response.data);
      } else if (error.request) {
        this.error = 'No response received from server';
      } else {
        this.error = 'Error setting up the request';
      }
    },
    formatDate(dateString) {
      return format(parseISO(dateString), 'MMM dd, yyyy - hh:mm a');
    },
    formatStatus(status) {
      const statusMap = {
        'pending': 'Pending',
        'confirmed': 'Confirmed',
        'in_progress': 'In Progress',
        'completed': 'Completed'
      };
      return statusMap[status] || status;
    },
    getStatusClass(status) {
      const statusClasses = {
        'pending': 'status-warning',
        'confirmed': 'status-primary',
        'in_progress': 'status-info',
        'completed': 'status-success'
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

.star-rating .star {
  fill: #ffc107 !important;
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
  padding: 20px;
  margin-bottom: 15px;
  border: 1px solid rgba(0, 0, 0, 0.05);
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
  border-left: 4px solid #e53e3e;
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

.action-btn {
  background-color: #ffccdf;
  color: #ff6b9e;
  margin: 15px 20px 20px;
}

.action-btn:hover {
  background-color: #ff6b9e;
  color: white;
  transform: translateY(-2px);
}

@media (max-width: 768px) {
  .dashboard-container {
    padding: 1rem;
  }
  
  .requests-grid {
    grid-template-columns: 1fr;
  }
}
</style>