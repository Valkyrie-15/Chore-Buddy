<template>
    <div class="csv-export-container">
      <button 
        @click="exportCSV" 
        :disabled="isLoading"
        class="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded"
      >
        {{ isLoading ? 'Exporting...' : 'Export CSV' }}
      </button>
    </div>
  </template>
  
  <script>
  import axios from 'axios';
  
  export default {
    data() {
      return {
        isLoading: false
      }
    },
    methods: {
      async exportCSV() {
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
          link.setAttribute('download', 'export.csv');
          document.body.appendChild(link);
          link.click();
  
          // Clean up
          document.body.removeChild(link);
          URL.revokeObjectURL(href);
        } catch (error) {
          console.error('CSV Export Error:', error);
          
          if (error.response) {
            alert(`Export failed: ${error.response.data.message || 'Server error'}`);
          } else if (error.request) {
            alert('No response received from server. Please check your connection.');
          } else {
            alert('Error setting up export request');
          }
        } finally {
          this.isLoading = false;
        }
      }
    }
  }
  </script>
  
  <style scoped>
  .csv-export-container {
    display: flex;
    justify-content: center;
    margin: 20px 0;
    color:black
  }
  </style>