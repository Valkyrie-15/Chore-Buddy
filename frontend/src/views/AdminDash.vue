<template>
  <div class="admin-dashboard">
    <div class="dashboard-container">
      <div class="row g-4">
        <div class="col-12">
          <div class="dashboard-card">
            <div class="card-body p-0">
              <div class="header-container p-4">
                <div class="d-flex justify-content-between align-items-center">
                  <h1 class="dashboard-title">
                    <i class="fas fa-chart-line me-3 text-primary"></i>Administration Dashboard
                  </h1>
                  <div class="action-buttons">
                    <button 
                      class="btn action-btn me-3" 
                      @click="refreshStats"
                      :disabled="isLoading"
                    >
                      <i class="fas fa-sync-alt me-2"></i>
                      {{ isLoading ? 'Refreshing...' : 'Refresh Data' }}
                    </button>
                    <button 
                      class="btn action-btn" 
                      @click="exportReport"
                      :disabled="isLoading"
                    >
                      <i class="fas fa-file-export me-2"></i>
                      {{ isLoading ? 'Exporting...' : 'Export Report' }}
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <!-- Main dashboard content -->
      <div class="row g-4">
        <!-- Full width top rectangle for User Distribution -->
        <div class="col-12">
          <div class="dashboard-card">
            <div class="card-header">
              <h2 class="section-title">
                <i class="fas fa-users me-2"></i>User Distribution
              </h2>
              <span class="section-subtitle">Customers vs Professionals</span>
            </div>
            <div class="card-body">
              <canvas ref="userChart" class="chart"></canvas>
            </div>
          </div>
        </div>
        
        <!-- Two equal width cards side by side below -->
        <div class="col-12 col-md-6">
          <div class="dashboard-card h-100">
            <div class="card-header">
              <h2 class="section-title">
                <i class="fas fa-calendar-check me-2"></i>Service Bookings
              </h2>
              <span class="section-subtitle">Distribution by service type</span>
            </div>
            <div class="card-body">
              <canvas ref="serviceChart" class="chart-medium"></canvas>
            </div>
          </div>
        </div>
        
        <div class="col-12 col-md-6">
          <div class="dashboard-card h-100">
            <div class="card-header">
              <h2 class="section-title">
                <i class="fas fa-chart-pie me-2"></i>Service Requests
              </h2>
              <span class="section-subtitle">Current status overview</span>
            </div>
            <div class="card-body">
              <canvas ref="statusChart" class="chart-medium"></canvas>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';
import { Chart } from 'chart.js/auto';

export default {
  name: 'AdminStatsDashboard',
  data() {
    return {
      isLoading: false,
      charts: {
        users: null,
        services: null,
        status: null
      },
      statsData: {
        users: {
          labels: ['Customers', 'Professionals'],
          datasets: [{
            label: 'Number of Users',
            backgroundColor: ['#8a4fff', '#4ecdc4'],
            borderRadius: 8,
            data: []
          }]
        },
        services: {
          labels: [],
          datasets: [{
            label: 'Service Bookings',
            backgroundColor: [
              '#8a4fff', 
              '#4ecdc4', 
              '#ff6b9e', 
              '#ffb347'
            ],
            borderWidth: 0,
            data: []
          }]
        },
        status: {
          labels: ['Open', 'Completed'],
          datasets: [{
            data: [],
            backgroundColor: [
              '#ffb347', 
              '#4ecdc4'
            ],
            borderWidth: 0
          }]
        }
      }
    };
  },
  mounted() {
    this.fetchStats();
  },
  methods: {
    // Centralized notification method
    notify(type, message) {
      // Fallback notification method if toast is not available
      if (type === 'success') {
        console.log(`Success: ${message}`);
        alert(message);
      } else if (type === 'error') {
        console.error(`Error: ${message}`);
        alert(`Error: ${message}`);
      }
    },
    async fetchStats() {
      this.isLoading = true;
      try {
        const response = await axios.get('/api/stat');
        const data = response.data;
        
        // Update users data - exclude admin users
        this.statsData.users.datasets[0].data = [
          data.users.customer || 0,
          data.users.professional || 0
        ];
        
        // Update services data
        this.statsData.services.labels = Object.keys(data.service_bookings);
        this.statsData.services.datasets[0].data = Object.values(data.service_bookings);
        
        // Update status data
        this.statsData.status.datasets[0].data = [
          data.request_status.pending || 0,
          data.request_status.Paid || 0, 
        ];

        this.renderCharts();
        this.notify('success', 'Dashboard statistics refreshed');
      } catch (error) {
        console.error('Error fetching stats:', error);
        this.notify('error', 'Failed to load dashboard statistics');
      } finally {
        this.isLoading = false;
      }
    },
    refreshStats() {
      this.fetchStats();
    },
    async exportReport() {
      this.isLoading = true;

      try {
        // Initiate export and get task ID
        const exportResponse = await axios.get('/api/export');
        const taskId = exportResponse.data.id;

        // Poll for the CSV file
        const csvResponse = await axios({
          url: `/api/csv_result/${taskId}`,
          method: 'GET',
          responseType: 'blob'
        });

        // Create a blob link to download
        const href = URL.createObjectURL(csvResponse.data);
        
        // Create a link to trigger the download
        const link = document.createElement('a');
        link.href = href;
        link.setAttribute('download', 'admin_dashboard_export.csv');
        document.body.appendChild(link);
        link.click();

        // Clean up
        document.body.removeChild(link);
        URL.revokeObjectURL(href);

        this.notify('success', 'CSV exported successfully');
      } catch (error) {
        console.error('CSV Export Error:', error);
        
        if (error.response) {
          this.notify('error', error.response.data.message || 'Server error');
        } else if (error.request) {
          this.notify('error', 'No response received from server. Please check your connection.');
        } else {
          this.notify('error', 'Error setting up export request');
        }
      } finally {
        this.isLoading = false;
      }
    },
    renderCharts() {
      const baseOptions = {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            position: 'bottom',
            labels: {
              color: '#4a4a4a',
              padding: 20,
              usePointStyle: true,
              pointStyle: 'circle',
              font: {
                family: "'Poppins', sans-serif",
                size: 12
              }
            }
          },
          tooltip: {
            backgroundColor: 'rgba(255, 255, 255, 0.95)',
            titleColor: '#333',
            bodyColor: '#666',
            borderColor: 'rgba(0, 0, 0, 0.05)',
            borderWidth: 1,
            padding: 12,
            boxPadding: 6,
            usePointStyle: true,
            callbacks: {
              label: function(context) {
                return ` ${context.label}: ${context.raw || context.formattedValue}`;
              }
            },
            bodyFont: {
              family: "'Poppins', sans-serif",
              size: 13
            },
            titleFont: {
              family: "'Poppins', sans-serif",
              size: 14,
              weight: 'bold'
            }
          }
        }
      };

      // User Distribution Chart (Horizontal Bar)
      if (this.charts.users) this.charts.users.destroy();
      this.charts.users = new Chart(this.$refs.userChart.getContext('2d'), {
        type: 'bar',
        data: this.statsData.users,
        options: {
          ...baseOptions,
          indexAxis: 'y', // Horizontal bar
          plugins: {
            ...baseOptions.plugins,
            legend: { display: false }
          },
          scales: {
            x: {
              grid: {
                display: true,
                color: 'rgba(0, 0, 0, 0.05)'
              },
              ticks: {
                color: '#666',
                font: {
                  family: "'Poppins', sans-serif",
                  size: 12
                }
              }
            },
            y: {
              grid: {
                display: false
              },
              ticks: {
                color: '#4a4a4a',
                font: {
                  family: "'Poppins', sans-serif",
                  size: 13,
                  weight: 'bold'
                }
              }
            }
          }
        }
      });

      // Service Bookings Chart (Doughnut)
      if (this.charts.services) this.charts.services.destroy();
      this.charts.services = new Chart(this.$refs.serviceChart.getContext('2d'), {
        type: 'doughnut',
        data: this.statsData.services,
        options: {
          ...baseOptions,
          cutout: '65%',
          plugins: {
            ...baseOptions.plugins,
            legend: { 
              position: 'right',
              align: 'center'
            }
          }
        }
      });

      // Status Chart (Doughnut with custom center text)
      if (this.charts.status) this.charts.status.destroy();
      this.charts.status = new Chart(this.$refs.statusChart.getContext('2d'), {
        type: 'doughnut',
        data: this.statsData.status,
        options: {
          ...baseOptions,
          cutout: '65%',
          plugins: {
            ...baseOptions.plugins,
            legend: { 
              position: 'right',
              align: 'center'
            }
          }
        }
      });
    }
  }
};
</script>

<style scoped>
.admin-dashboard {
  background-color: rgba(250, 250, 250, 0.5);
  min-height: 100vh;
}

.dashboard-container {
  padding: 2rem;
  max-width: 1200px;
  margin: 0 auto;
}

.dashboard-title {
  color: #4a4a4a;
  font-weight: 700;
  font-size: 1.5rem;
  margin-bottom: 0;
  display: flex;
  align-items: center;
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

.section-title {
  font-weight: 700;
  margin-bottom: 0;
  color: white;
  position: relative;
  display: inline-block;
  font-size: 1.2rem;
}

.section-subtitle {
  color: rgba(255, 255, 255, 0.8);
  font-weight: 400;
  font-size: 0.9rem;
  margin-left: 1rem;
}

.header-container {
  background-color: rgba(255, 255, 255, 0.9);
}

.card-body {
  padding: 1.5rem;
}

.chart {
  width: 100%;
  height: 250px;
}

.chart-medium {
  width: 100%;
  height: 220px;
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
  background-color: rgba(138, 79, 255, 0.1);
  color: #8a4fff;
}

.action-btn:hover:not([disabled]) {
  background-color: #8a4fff;
  color: white;
  transform: translateY(-2px);
}

.action-btn[disabled] {
  opacity: 0.7;
  cursor: not-allowed;
}

.action-buttons {
  display: flex;
}

.text-primary {
  color: #8a4fff !important;
}

@media (max-width: 768px) {
  .dashboard-container {
    padding: 1rem;
  }
  
  .action-buttons {
    flex-direction: column;
    gap: 10px;
    margin-top: 15px;
  }
  
  .dashboard-title {
    font-size: 1.2rem;
  }
  
  .chart, .chart-medium {
    height: 200px;
  }
}
</style>