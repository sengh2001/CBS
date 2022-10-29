<!--
Component for searching Faculty Activity.

@author Balwinder Sodhi
-->
<template>
  <div class="container-fluid">
    <h5>Find Faculty Activity</h5>
    <div class="row mb-2">
      <div class="col-md-6">
        <label for="emp">Show activity for employee</label>
        <user-lookup-comp @userSelected="onUserSelect"/>
      </div>
      <div class="col-md-6">
        <label for="status">List employees having activity in status</label>
        <select class="form-select" id="status" v-model="status" @change="findForStatus">
          <option v-for="x in SD.WfStatuses" v-bind:value="x.id" :key="x.id">
            {{ x.value }}
          </option>
        </select>
      </div>
    </div>
    <div class="card">
      <div class="card-header">
        <span class="fs-5">Results</span>
      </div>
      <div class="card-body">
        <div class="row fw-bold border-info border-bottom border-2">
          <div class="col-md-2">S#</div>
          <div class="col">Employee</div>
        </div>
        <p v-if="results == undefined || results.length == 0">Nothing to show yet!</p>
        <div class="row row-striped mt-4" v-for="(r, i) in results" :key="r.id">
          <div class="col-md-2">{{ i + 1 }}</div>
          <div class="col">
            <a :href="'#/fa/' + r.id">
              <span class="me-2">{{r.first_name +" "+ r.last_name}}</span>
            </a>
            <span class="me-2">({{ labelFor(SD.UserRoles, r.role) }})</span>
            <span class="me-2">Joined: {{r.doj}}</span>
            <span>Area: {{labelFor(SD.WorkAreas, r.area)}}</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import UserLookupComp from "./UserLookupComp.vue";
export default {
  name: "FacultyActivitySearch",
  components: {
    UserLookupComp
  },
  data: function () {
    return {
      selUser: {},
      status: "",
      results: []
    };
  },
  computed: {
  },
  created: function () {
    console.log("Creating FacultyActivitySearch");
  },
  mounted: function () {
  },
  methods: {
    onUserSelect(c) {
      this.selUser = c;
      this.$router.push("/fa/"+c.id)
    },
    async findForStatus() {
      let vm = this;
      vm.results.items = [];
      await vm.doGet("activity_find/"+vm.status,
        (b) => {
          vm.results = b;
        }, vm.setStatusMessage);
    },
    reset() {
      this.results = []
      this.status = ""
      this.selUser = {}
    }
  }
};
</script>
