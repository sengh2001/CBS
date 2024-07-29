<template>
    <div class="container mt-4">
      <h2>Add Classroom</h2>
      <form @submit.prevent="submitForm">
        <div class="mb-3">
          <label for="class_name" class="form-label">Classroom Name</label>
          <input
            type="text"
            id="class_name"
            v-model="classroom.class_name"
            class="form-control"
            required
          />
        </div>
        <div class="mb-3">
          <label for="capacity" class="form-label">Capacity</label>
          <input
            type="number"
            id="capacity"
            v-model="classroom.capacity"
            class="form-control"
            required
          />
        </div>
        <div class="mb-3">
          <label for="class_name" class="form-label">Department Name</label>
          <input
            type="text"
            id="class_name"
            v-model="classroom.Location"
            class="form-control"
            required
          />
        </div>
        <div class="mb-3">
          <label for="description" class="form-label">Description</label>
          <textarea
            id="description"
            v-model="classroom.description"
            class="form-control"
          ></textarea>
        </div>
        <div class="form-check mb-3">
          <input
            type="checkbox"
            id="is_booked"
            v-model="classroom.is_booked"
            class="form-check-input"
          />
          <label for="is_booked" class="form-check-label">Is Booked</label>
        </div>
        <div class="form-check mb-3">
          <input
            type="checkbox"
            id="is_available"
            v-model="classroom.is_available"
            class="form-check-input"
          />
          <label for="is_available" class="form-check-label">Is Available</label>
        </div>
        <button type="submit" class="btn btn-primary">Add Classroom</button>
      </form>
      <div v-if="responseMessage" class="mt-3 alert alert-info">
        {{ responseMessage }}
      </div>
      <div v-if="errorMessage" class="mt-3 alert alert-danger">
        {{ errorMessage }}
      </div>
    </div>
  </template>
  
  <script>
  import axios from 'axios';
  
  export default {
    data() {
      return {
        classroom: {
          class_name: '',
          capacity: '',
          Location: '',
          description: '',
          is_booked: false,
          is_available: true,
        },
        responseMessage: '',
        errorMessage: '',
      };
    },
    methods: {
      async submitForm() {
        try {
          const response = await axios.post('add_classroom', this.classroom);
          this.responseMessage = `Classroom added successfully! ID: ${response.data.classroom_id}`;
          this.errorMessage = '';
          // Reset form after successful submission
          this.classroom = {
            class_name: '',
            capacity: '',
            Location: '',
            description: '',
            is_booked: false,
            is_available: true,
          };
        } catch (error) {
          this.errorMessage = error.response.data.error || 'An error occurred';
          this.responseMessage = '';
        }
      },
    },
  };
  </script>
  
  <style scoped>
  .container {
    max-width: 600px;
  }
  </style>
  