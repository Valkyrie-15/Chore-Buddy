<template>
  <div class="users-management-container">
    <div class="card shadow-sm animate-card">
      <div class="card-header d-flex justify-content-between align-items-center">
        <h2 class="mb-0">
          <i class="fas fa-users me-2 text-primary"></i>User Management
        </h2>
        <div class="search-filter d-flex align-items-center">
          <div class="search-wrapper me-3 position-relative">
            <i class="fas fa-search search-icon position-absolute"></i>
            <input 
              v-model="searchQuery" 
              class="form-control ps-4" 
              type="search" 
              placeholder="Search users..."
            >
          </div>
          <div class="filter-buttons">
            <button 
              class="btn btn-filter" 
              :class="{ 'active': activeFilter === 'all' }"
              @click="filterUsers('all')"
            >
              All
            </button>
            <button 
              class="btn btn-filter" 
              :class="{ 'active': activeFilter === 'professionals' }"
              @click="filterUsers('professionals')"
            >
              Professionals
            </button>
            <button 
              class="btn btn-filter" 
              :class="{ 'active': activeFilter === 'customers' }"
              @click="filterUsers('customers')"
            >
              Customers
            </button>
          </div>
        </div>
      </div>
    </div>
    
    <div class="table-responsive animate-card mt-3">
      <table class="table table-hover mb-0">
        <thead>
          
  <tr>
    <th>Username</th>
    <th>Email</th>
    
    <th>Role</th>
    <th>Status</th>
    <th>Full Name</th>
    <th v-if="showProfessionals">Service</th>
    <th>Actions</th>
  </tr>


        </thead>
        <tbody>
          <tr 
            v-for="user in filteredUsers" 
            :key="user.id" 
            class="user-row"
          >
            <td>
              <span class="fw-bold">{{ user.username }}</span>
            </td>
            <td>{{ user.email }}</td>
            <td>
              <span 
                class="badge"
                :class="{
                  'badge-professional': user.role === 'professional',
                  'badge-customer': user.role === 'customer'
                }"
              >
                {{ user.role }}
              </span>
            </td>
            <td>
              <span 
                class="badge"
                :class="{
                  'badge-approved': user.approved,
                  'badge-pending': !user.approved,
                  'badge-flagged': user.flagged
                }"
              >
                {{ user.flagged ? "Flagged" : user.approved ? "Approved" : "Pending" }}
              </span>
            </td>
            <td v-if="showProfessionals">{{ user.fullname ?? "N/A" }}</td>

            <td v-if="showProfessionals">{{ user.service ?? "N/A" }}</td>
            <td>
              <div class="action-buttons">
                <button 
                  v-if="!user.approved && !user.flagged" 
                  class="btn btn-action btn-approve" 
                  @click="approveProfessional(user.id)"
                  title="Approve Professional"
                >
                  <i class="fas fa-check"></i>
                </button>
                <button 
                  v-if="!user.flagged" 
                  class="btn btn-action btn-flag" 
                  @click="flagUser(user.id)"
                  title="Flag User"
                >
                  <i class="fas fa-flag"></i>
                </button>
                <button 
                  class="btn btn-action btn-view" 
                  @click="viewUserDetails(user)"
                  title="View Details"
                >
                  <i class="fas fa-eye"></i>
                </button>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
      
      <div 
        v-if="filteredUsers.length === 0" 
        class="empty-state"
      >
        <i class="fas fa-users-slash fa-3x mb-3"></i>
        <p>No users found matching your search or filter.</p>
      </div>
    </div>

    <!-- Professional Review Modal for Admin -->
    <div v-if="selectedUser" class="modal-overlay animate-in">
      <div class="modal-content">
        <div class="modal-header">
          <h3>{{ selectedUser.role === 'professional' ? 'Professional' : 'User' }} Details</h3>
          <button class="btn-close" @click="closeModal">
            <i class="fas fa-times"></i>
          </button>
        </div>
        
        <div class="modal-body">
          <!-- User Basic Information -->
          <div class="user-info mb-4">
            <h4 class="text-primary">{{ selectedUser.fullname || selectedUser.username }}</h4>
            <div class="row">
              <div class="col-md-6">
                <p><strong>Username:</strong> {{ selectedUser.username }}</p>
                <p><strong>Email:</strong> {{ selectedUser.email }}</p>
                <p><strong>Role:</strong> {{ selectedUser.role }}</p>
              </div>
              <div class="col-md-6">
                <p><strong>Status:</strong> 
                  <span 
                    class="badge"
                    :class="{
                      'badge-approved': selectedUser.approved,
                      'badge-pending': !selectedUser.approved,
                      'badge-flagged': selectedUser.flagged
                    }"
                  >
                    {{ selectedUser.flagged ? "Flagged" : selectedUser.approved ? "Approved" : "Pending" }}
                  </span>
                </p>
                <p v-if="selectedUser.service"><strong>Service:</strong> {{ selectedUser.service }}</p>
              </div>
            </div>
          </div>

          <!-- Professional Reviews Section -->
          <div v-if="selectedUser.role === 'professional'" class="professional-reviews">
            <h4 class="reviews-heading">
              <i class="fas fa-star me-2 text-warning"></i>Professional Reviews
            </h4>

            <div v-if="isLoadingReviews" class="loading-spinner">
              <i class="fas fa-spinner fa-spin"></i> Loading reviews...
            </div>
            
            <div v-else-if="professionalReviews.length === 0" class="empty-state">
              <i class="fas fa-comment-slash fa-3x mb-3"></i>
              <p>No reviews found for this professional.</p>
            </div>
            
            <div v-else class="reviews-container">
              <div class="reviews-summary mb-4">
                <div class="d-flex justify-content-between align-items-center">
                  <div>
                    <h5 class="mb-2">
                      Average Rating: 
                      <span :class="averageRating < lowRatingThreshold ? 'text-danger' : 'text-success'">
                        {{ averageRating.toFixed(1) }} / 5
                      </span>
                    </h5>
                    <div class="rating-stars">
                      <i 
                        v-for="n in 5" 
                        :key="n" 
                        class="fas fa-star"
                        :class="n <= Math.round(averageRating) ? 'text-warning' : 'text-muted'"
                      ></i>
                    </div>
                    <p class="text-muted">Total Reviews: {{ totalReviews }}</p>
                  </div>
                  <div v-if="averageRating < lowRatingThreshold" class="alert alert-warning">
                    <i class="fas fa-exclamation-triangle me-2"></i>Low Rating Alert
                  </div>
                </div>
              </div>

              <div v-for="review in professionalReviews" :key="review.id" class="review-card mb-3">
                <div class="d-flex justify-content-between align-items-center">
                  <div>
                    <strong>{{ review.customer_name }}</strong>
                    <div class="rating-stars small">
                      <i 
                        v-for="n in 5" 
                        :key="n" 
                        class="fas fa-star"
                        :class="n <= review.rating ? 'text-warning' : 'text-muted'"
                      ></i>
                    </div>
                  </div>
                  <small class="text-muted">{{ formatDate(review.review_date) }}</small>
                </div>
                <p class="mt-2">{{ review.review_text }}</p>
                <small class="text-muted">Service: {{ review.service_name }}</small>
              </div>

              <!-- Pagination -->
              <div v-if="totalPages > 1" class="pagination-controls mt-3">
                <button 
                  @click="loadPreviousPage" 
                  :disabled="currentPage === 1" 
                  class="btn btn-pagination"
                >
                  <i class="fas fa-chevron-left me-1"></i> Previous
                </button>
                <span class="pagination-info">Page {{ currentPage }} of {{ totalPages }}</span>
                <button 
                  @click="loadNextPage" 
                  :disabled="currentPage === totalPages" 
                  class="btn btn-pagination"
                >
                  Next <i class="fas fa-chevron-right ms-1"></i>
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
import axios from "axios";

export default {
  name: 'UserManagement',
  data() {
    return {
      users: [],
      showProfessionals: false,
      searchQuery: '',
      activeFilter: 'all',
      selectedUser: null,
      
      // Reviews data
      professionalReviews: [],
      isLoadingReviews: false,
      averageRating: 0,
      totalReviews: 0,
      currentPage: 1,
      totalPages: 1,
      lowRatingThreshold: 2
    };
  },
  computed: {
    filteredUsers() {
      return this.users.filter(user => {
        const matchesSearch = user.username.toLowerCase().includes(this.searchQuery.toLowerCase()) ||
                               user.email.toLowerCase().includes(this.searchQuery.toLowerCase());
        
        const matchesFilter = 
          this.activeFilter === 'all' || 
          (this.activeFilter === 'professionals' && user.role === 'professional') ||
          (this.activeFilter === 'customers' && user.role === 'customer');
        
        return matchesSearch && matchesFilter && user.role !== 'admin';  // Hide admins
      });
    }
  },
  created() {
    // Set up axios interceptor to include JWT token
    const token = localStorage.getItem('token');
    if (token) {
      axios.interceptors.request.use(
        config => {
          config.headers['Authorization'] = `Bearer ${token}`;
          return config;
        },
        error => {
          return Promise.reject(error);
        }
      );
    }
    
    this.fetchUsers();
  },
  methods: {
    fetchUsers() {
      axios.get("/all_users")
      .then(response => {
          this.users = response.data.map(user => ({
            ...user,
            flagged: !user.approved && user.flagged_status  // If flagged, mark it
          }));
          this.showProfessionals = this.users.some(user => user.fullname); 
      })
      .catch(error => {
          console.error("Error fetching users:", error);
        });
    },
    filterUsers(filter) {
      this.activeFilter = filter;
    },
    viewUserDetails(user) {
      this.selectedUser = user;
      
      // If professional, fetch reviews
      if (user.role === 'professional') {
        this.fetchProfessionalReviews(user.id);
      }
    },
    async fetchProfessionalReviews(professionalId) {
      this.isLoadingReviews = true;
      this.professionalReviews = [];

      try {
        const response = await axios.get(`/admin/professional/${professionalId}/reviews`, {
          params: {
            page: this.currentPage,
            per_page: 5
          }
        });

        this.professionalReviews = response.data.reviews;
        this.averageRating = response.data.average_rating;
        this.totalReviews = response.data.total_reviews;
        this.totalPages = response.data.total_pages;
        this.lowRatingThreshold = response.data.low_rating_threshold;
      } catch (error) {
        console.error("Error fetching professional reviews:", error);
      } finally {
        this.isLoadingReviews = false;
      }
    },
    loadPreviousPage() {
      if (this.currentPage > 1) {
        this.currentPage--;
        this.fetchProfessionalReviews(this.selectedUser.id);
      }
    },
    loadNextPage() {
      if (this.currentPage < this.totalPages) {
        this.currentPage++;
        this.fetchProfessionalReviews(this.selectedUser.id);
      }
    },
    formatDate(dateString) {
      return dateString ? new Date(dateString).toLocaleDateString() : 'N/A';
    },
    closeModal() {
      this.selectedUser = null;
      this.professionalReviews = [];
      this.currentPage = 1;
    },
    approveProfessional(id) {
      axios.post(`/approve_professional/${id}`)
        .then(() => {
          this.fetchUsers();
        })
        .catch(error => {
          console.error("Error approving professional:", error);
      });
    },
    flagUser(id) {
      axios.post(`/flag_user/${id}`)
        .then(() => {
          this.fetchUsers();
        })
        .catch(error => {
          console.error("Error flagging user:", error);
        });
    }
  }
};
</script>

<style scoped>
.users-management-container {
  padding: 2rem;
  max-width: 1200px;
  margin: 0 auto;
}

.card {
  background-color: rgba(255, 255, 255, 0.85);
  backdrop-filter: blur(10px);
  border-radius: 15px;
  overflow: hidden;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.05);
  transition: transform 0.3s ease, box-shadow 0.3s ease;
  border: 1px solid rgba(0, 0, 0, 0.05);
  margin-bottom: 1.5rem;
}

.card:hover {
  box-shadow: 0 15px 35px rgba(138, 79, 255, 0.1);
}

.card-header {
  padding: 20px;
  background: linear-gradient(135deg, #c3adee 0%, #a98ade 100%);
  color: white;
}

.search-wrapper {
  position: relative;
}

.search-icon {
  color: #8a4fff;
  left: 15px;
  top: 50%;
  transform: translateY(-50%);
}

.form-control {
  border-radius: 10px;
  padding: 12px 15px 12px 40px;
  border: 1px solid rgba(0, 0, 0, 0.05);
  background-color: rgba(255, 255, 255, 0.8);
  backdrop-filter: blur(5px);
  box-shadow: 0 2px 15px rgba(0, 0, 0, 0.05);
  transition: all 0.3s ease;
}

.form-control:focus {
  outline: none;
  box-shadow: 0 2px 20px rgba(138, 79, 255, 0.15);
  border-color: #a98ade;
}

.btn-filter {
  padding: 10px 15px;
  border-radius: 10px;
  border: none;
  background-color: rgba(255, 255, 255, 0.3);
  color: white;
  font-weight: 600;
  margin-left: 10px;
  transition: all 0.3s ease;
}

.btn-filter:hover {
  background-color: rgba(255, 255, 255, 0.5);
  transform: translateY(-2px);
}

.btn-filter.active {
  background-color: rgba(255, 255, 255, 0.8);
  color: #8a4fff;
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
}

.animate-card {
  animation: fadeInUp 0.5s ease-out;
}

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
}
}

.table-responsive {
  background-color: rgba(255, 255, 255, 0.85);
  backdrop-filter: blur(10px);
  border-radius: 15px;
  overflow: hidden;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.05);
  border: 1px solid rgba(0, 0, 0, 0.05);
}

.table {
  margin-bottom: 0;
}

.table thead {
  background-color: rgba(138, 79, 255, 0.1);
}

.table thead th {
  padding: 15px;
  color: #8a4fff;
  font-weight: 600;
  border: none;
}

.table tbody tr {
  transition: all 0.3s ease;
  border-bottom: 1px solid rgba(0, 0, 0, 0.05);
}

.table tbody tr:hover {
  background-color: rgba(138, 79, 255, 0.05);
}

.table tbody td {
  padding: 15px;
  vertical-align: middle;
  border: none;
}

.badge {
  padding: 8px 12px;
  border-radius: 20px;
  font-weight: 600;
  font-size: 0.8rem;
}

.badge-professional {
  background-color: #8a4fff;
  color: white;
}

.badge-customer {
  background-color: #4ecdc4;
  color: white;
}

.badge-approved {
  background-color: #4ecdc4;
  color: white;
}

.badge-pending {
  background-color: #ffb347;
  color: white;
}

.badge-flagged {
  background-color: #ff6b6b;
  color: white;
}

.action-buttons {
  display: flex;
  gap: 10px;
}

.btn-action {
  width: 36px;
  height: 36px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  border: none;
  transition: all 0.3s ease;
  color: white;
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
}

.btn-approve {
  background-color: #4ecdc4;
}

.btn-approve:hover {
  background-color: #3db8af;
  transform: translateY(-2px);
}

.btn-flag {
  background-color: #ff6b6b;
}

.btn-flag:hover {
  background-color: #ff5252;
  transform: translateY(-2px);
}

.btn-view {
  background-color: #8a4fff;
}

.btn-view:hover {
  background-color: #7a3fe8;
  transform: translateY(-2px);
}

.empty-state {
  text-align: center;
  padding: 60px 20px;
  color: #a98ade;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 15px;
}

/* Modal styling */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  backdrop-filter: blur(5px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  background-color: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(10px);
  border-radius: 15px;
  width: 80%;
  max-width: 800px;
  max-height: 80vh;
  overflow-y: auto;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.2);
  animation: fadeIn 0.3s ease-out;
}

.modal-header {
  padding: 20px;
  background: linear-gradient(135deg, #8a4fff 0%, #a98ade 100%);
  color: white;
  display: flex;
  justify-content: space-between;
  align-items: center;
  position: sticky;
  top: 0;
  z-index: 1;
}

.btn-close {
  background: rgba(255, 255, 255, 0.3);
  border: none;
  width: 36px;
  height: 36px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  transition: all 0.3s ease;
}

.btn-close:hover {
  background: rgba(255, 255, 255, 0.5);
  transform: rotate(90deg);
}

.modal-body {
  padding: 25px;
}

.user-info {
  background-color: rgba(255, 255, 255, 0.6);
  padding: 20px;
  border-radius: 15px;
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.05);
}

.professional-reviews {
  background-color: rgba(255, 255, 255, 0.6);
  padding: 20px;
  border-radius: 15px;
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.05);
}

.reviews-heading {
  margin-bottom: 20px;
  color: #8a4fff;
}

.loading-spinner {
  text-align: center;
  padding: 30px;
  color: #8a4fff;
}

.reviews-summary {
  background: linear-gradient(135deg, #f5f7fa 0%, #e4e8ea 100%);
  padding: 15px;
  border-radius: 15px;
}

.rating-stars {
  margin-bottom: 5px;
}

.review-card {
  background-color: rgba(255, 255, 255, 0.8);
  padding: 15px;
  border-radius: 15px;
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.05);
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.review-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 10px 25px rgba(138, 79, 255, 0.1);
}

.alert-warning {
  background-color: rgba(255, 179, 71, 0.2);
  color: #ff9800;
  padding: 8px 15px;
  border-radius: 10px;
  font-weight: 600;
}

/* Pagination Controls */
.pagination-controls {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 15px;
}

.btn-pagination {
  background-color: #f1e8ff;
  color: #8a4fff;
  border: none;
  padding: 8px 15px;
  border-radius: 10px;
  font-weight: 600;
  transition: all 0.3s ease;
}

.btn-pagination:hover:not(:disabled) {
  background-color: #8a4fff;
  color: white;
  transform: translateY(-2px);
}

.btn-pagination:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.pagination-info {
  color: #8a4fff;
  font-weight: 600;
}

.animate-in {
  animation: fadeIn 0.3s ease-out;
}

@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

@media (max-width: 768px) {
  .users-management-container {
    padding: 1rem;
  }
  
  .search-filter {
    flex-direction: column;
    align-items: flex-start;
  }
  
  .search-wrapper {
    width: 100%;
    margin-bottom: 10px;
  }
  
  .filter-buttons {
    display: flex;
    width: 100%;
    margin-top: 10px;
  }
  
  .btn-filter {
    flex: 1;
    margin-left: 0;
    margin-right: 5px;
  }
  
  .modal-content {
    width: 95%;
  }
}
</style>