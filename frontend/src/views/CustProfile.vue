<template>
  <div class="dashboard-container">
    <div class="row g-4">
      <div class="col-12">
        <div class="dashboard-card">
          <div class="card-header">
            <h2 class="section-title">Customer Profile</h2>
          </div>
          <div class="card-body p-4">
            <div class="profile-grid">
              <div class="profile-item">
                <div class="icon-wrapper">
                  <i class="fas fa-user"></i>
                </div>
                <div class="content">
                  <h6 class="item-label">Full Name</h6>
                  <p class="item-value">{{ customer.fullname }}</p>
                </div>
              </div>
              <div class="profile-item">
                <div class="icon-wrapper">
                  <i class="fas fa-phone"></i>
                </div>
                <div class="content">
                  <h6 class="item-label">Contact</h6>
                  <p class="item-value">{{ customer.contact }}</p>
                </div>
              </div>
              <div class="profile-item">
                <div class="icon-wrapper">
                  <i class="fas fa-map-marker-alt"></i>
                </div>
                <div class="content">
                  <h6 class="item-label">Address</h6>
                  <p class="item-value">{{ customer.address }}</p>
                </div>
              </div>
              <div class="profile-item">
                <div class="icon-wrapper">
                  <i class="fas fa-map-pin"></i>
                </div>
                <div class="content">
                  <h6 class="item-label">Pin Code</h6>
                  <p class="item-value">{{ customer.pin_code }}</p>
                </div>
              </div>
            </div>
            <button class="btn action-btn" @click="isEditing = true">
              <i class="fas fa-edit me-2"></i> Edit Profile
            </button>
          </div>
        </div>
      </div>
    </div>

    <div v-if="isEditing" class="modal-overlay">
      <div class="modal-container">
        <div class="dashboard-card modal-content">
          <div class="card-header">
            <h2 class="section-title">Edit Customer Profile</h2>
            <button class="close-btn" @click="cancelEditing">
              <i class="fas fa-times"></i>
            </button>
          </div>
          <div class="card-body p-4">
            <div class="edit-form">
              <div class="form-group" v-for="(value, key) in editableFields" :key="key">
                <label class="form-label">
                  <i :class="[iconMap[key] || 'fas fa-info-circle', 'me-2']"></i>
                  {{ formatLabel(key) }}
                </label>
                <input
                  v-model="editableCustomer[key]"
                  class="form-control"
                  :placeholder="`Enter your ${formatLabel(key).toLowerCase()}`"
                />
              </div>
            </div>
          </div>
          <div class="modal-footer">
            <button class="btn cancel-btn" @click="cancelEditing">
              <i class="fas fa-times me-2"></i> Cancel
            </button>
            <button class="btn save-btn" @click="saveChanges">
              <i class="fas fa-check me-2"></i> Save Changes
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';
import { useRoute } from 'vue-router';
import { ref, onMounted, computed } from 'vue';

export default {
  setup() {
    const route = useRoute();
    const customerId = ref(route.params.id);
    const customer = ref({ fullname: '', contact: '', address: '', pin_code: '' });
    const editableCustomer = ref({ ...customer.value });
    const isEditing = ref(false);
    let originalCustomer = ref(null);

    const fetchCustomerData = () => {
      axios.get(`/api/customer/${customerId.value}`)
        .then(response => {
          customer.value = response.data;
          editableCustomer.value = { ...response.data };
          originalCustomer.value = { ...response.data };
        })
        .catch(error => {
          console.error("Error fetching customer data", error);
        });
    };

    const saveChanges = () => {
      axios.patch(`/api/customer/${customerId.value}`, editableCustomer.value)
        .then(() => {
          customer.value = { ...editableCustomer.value };
          originalCustomer.value = { ...editableCustomer.value };
          isEditing.value = false;
        })
        .catch(error => {
          console.error("Error updating customer data", error);
        });
    };

    const cancelEditing = () => {
      editableCustomer.value = { ...originalCustomer.value };
      isEditing.value = false;
    };

    const editableFields = computed(() => {
      return Object.keys(editableCustomer.value).reduce((fields, key) => {
        fields[key] = editableCustomer.value[key];
        return fields;
      }, {});
    });

    const formatLabel = (key) => {
      return key.split('_').map(word => word.charAt(0).toUpperCase() + word.slice(1)).join(' ');
    };

    const iconMap = {
      fullname: "fas fa-user",
      contact: "fas fa-phone",
      address: "fas fa-map-marker-alt",
      pin_code: "fas fa-map-pin"
    };

    onMounted(fetchCustomerData);
    return { 
      customer, 
      editableCustomer, 
      isEditing, 
      saveChanges, 
      cancelEditing, 
      editableFields, 
      formatLabel,
      iconMap
    };
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
  transform: translateY(-5px);
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

.profile-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 20px;
  margin-bottom: 2rem;
}

.profile-item {
  background-color: rgba(255, 255, 255, 0.8);
  backdrop-filter: blur(5px);
  border-radius: 15px;
  overflow: hidden;
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.05);
  transition: all 0.3s ease;
  padding: 20px;
  display: flex;
  align-items: center;
  gap: 15px;
  border: 1px solid rgba(0, 0, 0, 0.05);
}

.profile-item:hover {
  transform: translateY(-5px);
  box-shadow: 0 10px 20px rgba(138, 79, 255, 0.1);
}

.icon-wrapper {
  width: 50px;
  height: 50px;
  border-radius: 50%;
  background: linear-gradient(135deg, #8a4fff 0%, #a98ade 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.icon-wrapper i {
  color: white;
  font-size: 1.2rem;
}

.content {
  flex-grow: 1;
}

.item-label {
  font-weight: 600;
  color: #8a4fff;
  margin-bottom: 5px;
  font-size: 0.9rem;
}

.item-value {
  font-size: A1.1rem;
  margin-bottom: 0;
  color: #4a4a4a;
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
  margin: 0 auto;
  width: fit-content;
}

.action-btn:hover {
  background-color: #ff6b9e;
  color: white;
  transform: translateY(-2px);
}

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.5);
  backdrop-filter: blur(5px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-container {
  width: 90%;
  max-width: 600px;
  margin: 0 auto;
}

.modal-content {
  margin-bottom: 0;
  animation: slideIn 0.3s ease-out;
}

.close-btn {
  background: transparent;
  border: none;
  color: white;
  font-size: 1.2rem;
  cursor: pointer;
  transition: transform 0.3s ease;
}

.close-btn:hover {
  transform: scale(1.2);
}

.edit-form {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: 20px;
}

.form-group {
  margin-bottom: 15px;
}

.form-label {
  display: block;
  margin-bottom: 8px;
  color: #8a4fff;
  font-weight: 600;
}

.form-control {
  width: 100%;
  padding: 12px 15px;
  border: 1px solid rgba(0, 0, 0, 0.1);
  border-radius: 10px;
  font-size: 16px;
  background-color: rgba(255, 255, 255, 0.8);
  backdrop-filter: blur(5px);
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
  transition: all 0.3s ease;
}

.form-control:focus {
  outline: none;
  box-shadow: 0 2px 20px rgba(138, 79, 255, 0.15);
  border-color: #a98ade;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 15px;
  padding: 20px;
  background-color: rgba(0, 0, 0, 0.02);
  border-top: 1px solid rgba(0, 0, 0, 0.05);
}

.cancel-btn {
  background-color: #f8f9fa;
  color: #6c757d;
}

.cancel-btn:hover {
  background-color: #e2e6ea;
  transform: translateY(-2px);
}

.save-btn {
  background: linear-gradient(135deg, #8a4fff 0%, #a98ade 100%);
  color: white;
}

.save-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 5px 15px rgba(138, 79, 255, 0.3);
}

@keyframes slideIn {
  from {
    transform: translateY(-30px);
    opacity: 0;
  }
  to {
    transform: translateY(0);
    opacity: 1;
  }
}

@media (max-width: 768px) {
  .dashboard-container {
    padding: 1rem;
  }
  
  .profile-grid {
    grid-template-columns: 1fr;
  }
  
  .edit-form {
    grid-template-columns: 1fr;
  }
  
  .modal-footer {
    flex-direction: column;
  }
  
  .btn {
    width: 100%;
  }
}
</style>