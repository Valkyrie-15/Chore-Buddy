<template>
  <div class="earnings-container">
    <div class="dashboard-card">
      <div class="card-header">
        <h2 class="section-title">Earnings Dashboard</h2>
        <div class="date-filter">
          <div class="filter-item">
            <i class="fas fa-calendar-alt filter-icon"></i>
            <input 
              type="date" 
              v-model="startDate" 
              class="date-input"
              placeholder="Start Date"
            >
          </div>
          <div class="filter-item">
            <i class="fas fa-calendar-alt filter-icon"></i>
            <input 
              type="date" 
              v-model="endDate" 
              class="date-input"
              placeholder="End Date"
            >
          </div>
          <button 
            @click="fetchEarnings" 
            class="btn action-btn"
          >
            <i class="fas fa-filter me-2"></i> Filter
          </button>
        </div>
      </div>

      <div class="card-body p-0">
        <div v-if="loading" class="loading-container">
          <div class="spinner-border text-primary" role="status">
            <span class="visually-hidden">Loading...</span>
          </div>
        </div>

        <div v-else-if="error" class="alert-message">
          <i class="fas fa-exclamation-triangle me-2"></i>
          {{ error }}
        </div>

        <div v-else>
          <!-- Stats Cards Row -->
          <div class="row g-0">
            <div class="col-12 col-md-4 border-end border-light">
              <div class="p-4">
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
            </div>

            <div class="col-12 col-md-4 border-end border-light">
              <div class="p-4">
                <div class="stat-card gradient-info text-white">
                  <div class="d-flex align-items-center">
                    <div class="flex-grow-1">
                      <h6 class="text-white-50 mb-2">Completed Requests</h6>
                      <h3 class="mb-0 font-weight-bold">
                        {{ summary.total_completed_requests }}
                      </h3>
                    </div>
                    <div class="stat-icon">
                      <i class="fas fa-clipboard-check fa-2x opacity-75"></i>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <div class="col-12 col-md-4">
              <div class="p-4">
                <div class="stat-card gradient-success text-white">
                  <div class="d-flex align-items-center">
                    <div class="flex-grow-1">
                      <h6 class="text-white-50 mb-2">Avg. Earnings per Request</h6>
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

          <!-- Earnings by Service & Monthly Earnings Row -->
          <div class="row g-0">
            <div class="col-12 col-md-6 border-end border-light">
              <div class="p-4">
                <h6 class="section-subtitle mb-3">Earnings by Service</h6>
                <div class="earnings-list">
                  <div 
                    v-for="(amount, service) in summary.earnings_by_service" 
                    :key="service"
                    class="earnings-item"
                  >
                    <span class="service-name">{{ service }}</span>
                    <span class="service-amount">${{ amount.toFixed(2) }}</span>
                  </div>
                </div>
              </div>
            </div>
            
            <div class="col-12 col-md-6">
              <div class="p-4">
                <h6 class="section-subtitle mb-3">Monthly Earnings</h6>
                <div class="earnings-list">
                  <div 
                    v-for="(amount, month) in earningsByMonth" 
                    :key="month"
                    class="earnings-item"
                  >
                    <span class="month-name">{{ month }}</span>
                    <span class="month-amount">${{ amount.toFixed(2) }}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Earnings Breakdown Table -->
          <div class="p-4">
            <h6 class="section-subtitle mb-3">Earnings Breakdown</h6>
            <div class="table-responsive">
              <table class="earnings-table">
                <thead>
                  <tr>
                    <th>Request ID</th>
                    <th>Service</th>
                    <th>Amount</th>
                    <th>Payment Date</th>
                    <th>Payment Method</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="item in earningsBreakdown" :key="item.request_id">
                    <td>{{ item.request_id }}</td>
                    <td>{{ item.service_name }}</td>
                    <td>${{ item.amount.toFixed(2) }}</td>
                    <td>{{ formatDate(item.payment_date) }}</td>
                    <td>
                      <span :class="getPaymentMethodClass(item.payment_method)">
                        {{ item.payment_method }}
                      </span>
                    </td>
                  </tr>
                </tbody>
              </table>
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
  name: 'ProfessionalEarningsComponent',
  data() {
    return {
      earningsBreakdown: [],
      summary: {
        total_earnings: 0,
        total_completed_requests: 0,
        earnings_by_service: {},
        average_earnings_per_request: 0
      },
      earningsByMonth: {},
      loading: true,
      error: null,
      startDate: null,
      endDate: null
    };
  },
  mounted() {
    this.fetchEarnings();
  },
  methods: {
    async fetchEarnings() {
      this.loading = true;
      this.error = null;

      const params = {};
      if (this.startDate) params.start_date = this.startDate;
      if (this.endDate) params.end_date = this.endDate;

      try {
        const token = localStorage.getItem('token');
        const response = await axios.get('/api/professional/earnings', {
          params,
          headers: {
            'Authorization': `Bearer ${token}`
          }
        });

        const data = response.data;
        this.earningsBreakdown = data.earnings_breakdown;
        this.summary = data.summary;
        this.earningsByMonth = data.earnings_by_month;
      } catch (error) {
        console.error('Error fetching earnings:', error);
        this.error = error.response?.data?.error || 'An error occurred';
      } finally {
        this.loading = false;
      }
    },
    formatDate(dateString) {
      return format(parseISO(dateString), 'MMM dd, yyyy');
    },
    getPaymentMethodClass(method) {
      const methodClasses = {
        'credit_card': 'payment-primary',
        'paypal': 'payment-info',
        'bank_transfer': 'payment-success',
        'cash': 'payment-warning'
      };
      return methodClasses[method.toLowerCase()] || 'payment-secondary';
    }
  }
};
</script>

<style scoped>
.earnings-container {
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

.date-filter {
  display: flex;
  gap: 10px;
  align-items: center;
}

.filter-item {
  position: relative;
}

.filter-icon {
  position: absolute;
  left: 15px;
  top: 50%;
  transform: translateY(-50%);
  color: white;
  z-index: 2;
}

.date-input {
  padding: 10px 15px 10px 40px;
  border-radius: 10px;
  border: 1px solid rgba(255, 255, 255, 0.2);
  background-color: rgba(255, 255, 255, 0.2);
  color: white;
  font-size: 14px;
  backdrop-filter: blur(5px);
  transition: all 0.3s ease;
}

.date-input:focus {
  outline: none;
  border-color: white;
  background-color: rgba(255, 255, 255, 0.3);
}

.date-input::placeholder {
  color: rgba(255, 255, 255, 0.7);
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

.stat-icon {
  width: 50px;
  height: 50px;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: rgba(255, 255, 255, 0.2);
  border-radius: 10px;
  margin-left: 15px;
}

.earnings-list {
  background-color: rgba(255, 255, 255, 0.7);
  border-radius: 15px;
  overflow: hidden;
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.05);
}

.earnings-item {
  display: flex;
  justify-content: space-between;
  padding: 15px 20px;
  border-bottom: 1px solid rgba(0, 0, 0, 0.05);
  transition: background-color 0.3s ease;
}

.earnings-item:last-child {
  border-bottom: none;
}

.earnings-item:hover {
  background-color: rgba(255, 255, 255, 0.9);
}

.service-name, .month-name {
  font-weight: 500;
  color: #4a4a4a;
}

.service-amount, .month-amount {
  font-weight: 600;
  color: #8a4fff;
  background-color: rgba(138, 79, 255, 0.1);
  border-radius: 20px;
  padding: 3px 12px;
}

.earnings-table {
  width: 100%;
  border-collapse: separate;
  border-spacing: 0;
  background-color: rgba(255, 255, 255, 0.7);
  border-radius: 15px;
  overflow: hidden;
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.05);
}

.earnings-table th, 
.earnings-table td {
  padding: 15px 20px;
  text-align: left;
}

.earnings-table th {
  background-color: rgba(138, 79, 255, 0.1);
  color: #8a4fff;
  font-weight: 600;
  position: sticky;
  top: 0;
}

.earnings-table tr {
  transition: background-color 0.3s ease;
}

.earnings-table tbody tr:hover {
  background-color: rgba(255, 255, 255, 0.9);
}

.earnings-table tbody tr:not(:last-child) {
  border-bottom: 1px solid rgba(0, 0, 0, 0.05);
}

.payment-primary, .payment-info, .payment-success, .payment-warning, .payment-secondary {
  padding: 5px 10px;
  border-radius: 20px;
  font-weight: bold;
  font-size: 0.8rem;
  backdrop-filter: blur(5px);
  display: inline-block;
}

.payment-primary {
  background-color: #8a4fff;
  color: white;
}

.payment-info {
  background-color: #2575fc;
  color: white;
}

.payment-success {
  background-color: #4ecdc4;
  color: white;
}

.payment-warning {
  background-color: #ffb347;
  color: white;
}

.payment-secondary {
  background-color: #6c757d;
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
  margin: 15px;
  border-radius: 10px;
  border-left: 4px solid #e53e3e;
}

.btn {
  padding: 10px 20px;
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
  background-color: rgba(255, 255, 255, 0.25);
  color: white;
  backdrop-filter: blur(5px);
}

.action-btn:hover {
  background-color: white;
  color: #8a4fff;
  transform: translateY(-2px);
}

@media (max-width: 768px) {
  .earnings-container {
    padding: 1rem;
  }
  
  .card-header {
    flex-direction: column;
    gap: 15px;
    align-items: flex-start;
  }
  
  .date-filter {
    width: 100%;
    flex-wrap: wrap;
  }
  
  .filter-item {
    width: 100%;
  }
}
</style>