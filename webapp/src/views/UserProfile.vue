<!--
Component for user profile.

@author Balwinder Sodhi
-->
<template>
  <form @submit.prevent="save">
    <div class="row mb-2">
      <div class="col-md-4">
        <label for="area">Work Area</label>
          <select class="form-select" id="area" v-model="profile.area">
            <option v-for="x in SD.WorkAreas" v-bind:value="x.id" :key="x.id" :disabled="x.disabled">
              {{ x.value }}
            </option>
          </select>
      </div>
      <div class="col-md-4">
        <label for="doj">Joining Dt.</label>
        <input type="date" required class="form-control" id="doj" v-model="profile.doj" :disabled="viewOnly" />
      </div>
      <div class="col-md-4">
        <label for="dob">Birth Dt.</label>
        <input type="date" required class="form-control" id="dob" v-model="profile.dob" :disabled="viewOnly" />
      </div>
    </div>
    <div class="row mb-2">
      <div class="col-md-4">
        <label for="valid_fr">Valid From</label>
        <input type="date" required class="form-control" id="valid_fr" v-model="profile.valid_from" :disabled="viewOnly" />
      </div>
      <div class="col-md-4">
        <label for="valid_till">Valid Till</label>
        <input type="date" class="form-control" id="valid_till" v-model="profile.valid_till" :disabled="viewOnly" />
      </div>
      <div class="col-md-2">
        <label for="gend">Gender</label>
        <select required class="form-select" id="gend" v-model="profile.gender" :disabled="viewOnly">
          <option value="">Choose...</option>
          <option value="M">Male</option>
          <option value="F">Female</option>
          <option value="T">Transgender</option>
          <option value="U">Unspecified</option>
        </select>
      </div>
      <div class="col-md-2">
        <div class="form-check mt-4">
          <input class="form-check-input" type="checkbox" id="coall"
          v-model="profile.allowed_compoff" :disabled="viewOnly">
          <label class="form-check-label" for="coall">
            Comp-Off Allowed
          </label>
        </div>
      </div>
    </div>
    <div class="row mb-2">
      <div class="col-md-4">
        <label for="cpc">CPC Level</label>
        <input type="text" min="0" class="form-control" id="cpc" v-model="profile.cpc_level" :disabled="viewOnly" />
      </div>
      <div class="col-md-4">
        <label for="basic_pay">Basic Pay</label>
        <input type="number" min="0" class="form-control" id="basic_pay" v-model="profile.basic_pay" :disabled="viewOnly" />
      </div>
      <div class="col-md-4">
        <label for="cat">Category</label>
          <select class="form-select" id="cat" v-model="profile.category">
            <option v-for="x in SD.UserCategories" v-bind:value="x.id" :key="x.id">
              {{ x.value }}
            </option>
          </select>
      </div>
    </div>
    <div class="row">
      <div class="col" v-if="!viewOnly">
        <div class="mt-4">
          <button class="btn btn-outline-success me-2" type="submit">
            Save
            <i class="bi bi-save-fill"></i>
          </button>
          <button class="btn btn-outline-danger" @click="reset" type="reset">
            Clear
            <i class="bi bi-eraser-fill"></i>
          </button>
        </div>
      </div>
    </div>
  </form>
</template>

<script>
import _ from "lodash";
export default {
  name: "UserProfile",
  props: { userId: Number },
  emits: [],
  components: {
  },
  data: function () {
    return {
      profile: {}
    };
  },
  computed: {
  },
  async created() {
    console.log("Creating User Profile");
    await this.load();
    this.profile.user_id = this.userId
  },
  methods: {
    async load() {
      // Alias 'this' for accessing in promises
      let vm = this;
      await vm.doGet(`user_profile/${vm.userId}`, (b) => { vm.profile = b; },
        vm.setStatusMessage)
    },
    isValid() {
      // TODO:
      return true
      // return !(_.isEmpty(this.profile.email) || _.isEmpty(this.profile.first_name)
      //   || _.isEmpty(this.profile.last_name));
    },
    async save() {
      let vm = this;
      if (!this.isValid()) {
        vm.setStatusMessage("Please supply all required fields!");
        return;
      }
      if (!confirm("Confirm save?")) {
        vm.setStatusMessage("User canceled save!");
        return;
      }
      console.log("Saving user profile.");
      await vm.doPost("user_profile_save", vm.profile,
        (b) => {
          vm.profile = b;
          vm.setStatusMessage("Saved successfully!");
        }, vm.setStatusMessage);
    },
    reset() {
      this.profile = {user_id: this.userId};
      console.log("Clearing user profile.");
    },
  },
};
</script>
