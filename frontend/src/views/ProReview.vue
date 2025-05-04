<template>
  <div class="reviews-container">
    <!-- Error Message for Invalid ID -->
    <div v-if="!isValidProfessionalId" class="alert-message">
      <i class="fas fa-exclamation-triangle me-2"></i>
      {{ errorMessage }}
    </div>

    <!-- Reviews Header -->
    <div v-else class="dashboard-card mb-4">
      <div class="card-header">
        <h2 class="section-title">Professional Reviews</h2>
        <div class="average-rating d-flex align-items-center">
          <div class="rating-stars me-2">
            <i 
              v-for="n in 5" 
              :key="n" 
              class="fas fa-star"
              :class="n <= Math.round(averageRating) ? 'text-warning' : 'text-muted'"
            ></i>
          </div>
          <span class="status-tag status-primary">
            {{ averageRating.toFixed(1) }} / 5
          </span>
        </div>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="isLoadingReviews" class="loading-container">
      <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">Loading...</span>
      </div>
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="alert-message">
      <i class="fas fa-exclamation-triangle me-2"></i>
      {{ error }}
    </div>

    <!-- Reviews List -->
    <div v-else-if="professionalReviews.length" class="reviews-grid">
      <div v-for="review in professionalReviews" :key="review.id" class="review-card">
        <div class="review-card-header">
          <h3 class="customer-name">{{ review.customer_name }}</h3>
          <div class="rating d-flex align-items-center">
            <div class="rating-stars me-2">
              <i 
                v-for="n in 5" 
                :key="n" 
                class="fas fa-star"
                :class="n <= review.rating ? 'text-warning' : 'text-muted'"
              ></i>
            </div>
            <span class="review-rating">({{ review.rating }}/5)</span>
          </div>
        </div>
        <div class="review-card-body">
          <div class="review-service">
            <i class="fas fa-tag icon"></i>
            <span>{{ review.service_name }}</span>
          </div>
          <div class="review-date">
            <i class="fas fa-calendar-alt icon"></i>
            <span>{{ formatDate(review.review_date) }}</span>
          </div>
          <p class="review-text">{{ review.review_text }}</p>
        </div>
      </div>
    </div>

    <!-- No Reviews State -->
    <div v-else class="no-results">
      <i class="fas fa-comments fa-3x"></i>
      <p>No reviews available for this professional.</p>
    </div>

    <!-- Pagination -->
    <nav v-if="totalPages > 1" class="pagination-container">
      <ul class="pagination">
        <li 
          v-for="page in totalPages" 
          :key="page" 
          :class="['page-item', { 'active': page === currentPage }]"
        >
          <button 
            class="page-btn" 
            :class="{ 'active-page': page === currentPage }"
            @click="fetchProfessionalReviews(professionalId, page)"
          >
            {{ page }}
          </button>
        </li>
      </ul>
    </nav>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  name: 'ProReview',
  data() {
    return {
      userId: null,
      professionalId: null,
      professionalReviews: [],
      isLoadingReviews: true,
      error: null,
      errorMessage: 'No professional information found.',
      currentPage: 1,
      totalPages: 0,
      averageRating: 0,
      totalReviews: 0
    };
  },
  computed: {
    isValidProfessionalId() {
      return this.professionalId && this.professionalId > 0;
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
    
    this.initializeProfessionalId();
  },
  methods: {
    initializeProfessionalId() {
      try {
        const storedUser = localStorage.getItem('user');
        const userData = JSON.parse(storedUser);

        if (userData && userData.id) {
          this.userId = userData.id;
          this.fetchProfessionalId();
        } else {
          this.errorMessage = 'Could not find user ID';
          this.isLoadingReviews = false;
        }
      } catch (error) {
        console.error('Error parsing user data:', error);
        this.errorMessage = 'Error processing user information';
        this.isLoadingReviews = false;
      }
    },
    async fetchProfessionalId() {
      try {
        const response = await axios.get(`/api/user/${this.userId}/professional`);

        if (response.data && response.data.professional_id) {
          this.professionalId = response.data.professional_id;
          this.fetchProfessionalReviews(this.professionalId);
        } else {
          this.errorMessage = 'No professional account found for this user';
          this.isLoadingReviews = false;
        }
      } catch (error) {
        console.error('Error fetching professional ID:', error);
        this.errorMessage = 'Failed to retrieve professional information';
        this.isLoadingReviews = false;
      }
    },
    async fetchProfessionalReviews(professionalId, page = 1) {
      if (!this.isValidProfessionalId) {
        this.isLoadingReviews = false;
        this.error = 'Invalid professional ID';
        return;
      }

      this.isLoadingReviews = true;
      this.error = null;
      this.professionalReviews = [];

      try {
        const response = await axios.get(`/api/professional/${professionalId}/reviews`, {
          params: {
            page: page,
            per_page: 10
          }
        });

        this.professionalReviews = response.data.reviews;
        this.currentPage = response.data.current_page || page;
        this.totalPages = response.data.total_pages;
        this.averageRating = response.data.average_rating;
        this.totalReviews = response.data.total_reviews;
      } catch (error) {
        this.error = 'Failed to load reviews. Please try again later.';
        console.error('Review fetch error:', error);
      } finally {
        this.isLoadingReviews = false;
      }
    },
    formatDate(dateString) {
      return new Date(dateString).toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
      });
    }
  }
}
</script>
<style scoped>
.reviews-container {
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

.loading-container {
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 3rem;
}

.alert-message {
  background-color: #fdf2f2;
  color: #e53e3e;
  padding: 12px 20px;
  margin: 15px 0;
  border-radius: 10px;
  border-left: 4px solid #e53e3e;
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

.reviews-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 20px;
}

.review-card {
  background-color: rgba(255, 255, 255, 0.85);
  backdrop-filter: blur(10px);
  border-radius: 15px;
  overflow: hidden;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.05);
  transition: transform 0.3s ease, box-shadow 0.3s ease;
  border: 1px solid rgba(0, 0, 0, 0.05);
  display: flex;
  flex-direction: column;
  height: 100%;
}

.review-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 15px 35px rgba(138, 79, 255, 0.1);
}

.review-card-header {
  padding: 15px 20px;
  background: linear-gradient(135deg, #a98ade 0%, #8a4fff 100%);
  color: white;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.customer-name {
  margin: 0;
  font-size: 1.1rem;
  font-weight: 600;
}

.review-rating {
  color: rgba(255, 255, 255, 0.8);
  font-size: 0.9rem;
}

.review-card-body {
  padding: 15px 20px;
  flex-grow: 1;
  display: flex;
  flex-direction: column;
}

.review-service, .review-date {
  margin-bottom: 12px;
  display: flex;
  align-items: center;
  color: #4a4a4a;
}

.icon {
  width: 24px;
  margin-right: 10px;
  color: #8a4fff;
}

.review-text {
  margin-top: 15px;
  color: #4a4a4a;
  line-height: 1.6;
  flex-grow: 1;
}

.pagination-container {
  margin-top: 30px;
  display: flex;
  justify-content: center;
}

.pagination {
  display: flex;
  list-style: none;
  padding: 0;
  margin: 0;
  gap: 8px;
}

.page-btn {
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 10px;
  background-color: rgba(255, 255, 255, 0.8);
  color: #8a4fff;
  border: 1px solid rgba(138, 79, 255, 0.2);
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
}

.page-btn:hover {
  background-color: rgba(138, 79, 255, 0.1);
}

.active-page {
  background-color: #8a4fff;
  color: white;
}

@media (max-width: 768px) {
  .reviews-container {
    padding: 1rem;
  }
  
  .reviews-grid {
    grid-template-columns: 1fr;
  }
  
  .card-header {
    flex-direction: column;
    gap: 10px;
    align-items: flex-start;
  }
  
  .review-card-header {
    flex-direction: column;
    gap: 10px;
    align-items: flex-start;
  }
}

/* Fix for star rating component display */
::v-deep(.vue3-star-ratings__star) {
  margin-right: 2px;
}

::v-deep(.vue3-star-ratings__star svg) {
  fill: #ffc107;
}
</style>