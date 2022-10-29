<!--
Component for searching leave applications.

@author Balwinder Sodhi
-->
<template>
  <div class="container-fluid">
    <h5>Find Leave Applications</h5>
    <form @submit.prevent="find(false)">
      <div class="row mb-2">
        <div class="col-md-2">
          <label for="emp">Employee</label>
          <user-lookup-comp @userSelected="onUserSelect"/>
        </div>
        <div class="col-md-2">
          <label for="lstatus">Status</label>
          <select class="form-select" id="lstatus" v-model="crit.status">
            <option v-for="x in SD.WfStatuses" v-bind:value="x.id" :key="x.id">
              {{ x.value }}
            </option>
          </select>
        </div>
        <div class="col-md-2">
          <label for="leave_type">Leave Type</label>
          <select class="form-select" id="leave_type" v-model="crit.leave_type">
            <option v-for="x in SD.LeaveTypes" v-bind:value="x.id" :key="x.id">
              {{ x.value }}
            </option>
          </select>
        </div>
        <div class="col-md-2">
          <label for="work_area">Area</label>
          <select class="form-select" id="work_area" v-model="crit.area">
            <option v-for="x in SD.WorkAreas" v-bind:value="x.id" :key="x.id" :disabled="x.disabled">
              {{ x.value }}
            </option>
          </select>
        </div>
        <div class="col-md-3">
          <label for="dtrange">Dates</label>
          <div class="input-group">
            <input type="date" class="form-control" placeholder="Start date" aria-label="Start date" v-model="crit.start_dt">
            <span class="input-group-text"> To </span>
            <input type="date" class="form-control" placeholder="End date" aria-label="End date" v-model="crit.end_dt">
          </div>
        </div>
        
        <div class="col-md-1">
          <div class="mt-4">
            <button class="btn btn-outline-success me-2" type="submit">
              <i class="bi bi-search"></i>
            </button>
            <button class="btn btn-outline-danger me-2" @click="reset" type="reset">
              <i class="bi bi-eraser"></i>
            </button>
          </div>
        </div>
      </div>
    </form>
    <div class="card">
      <div class="card-header">
        <span class="fs-5">Results</span>
        <span class="float-end">
          <button class="btn btn-outline-info btn-sm me-4" v-if="crit.pg_no > 1" @click="prev_pg">Prev</button>
          <button class="btn btn-outline-info btn-sm me-4" v-if="results.has_next" @click="next_pg">Next</button>
        </span>
      </div>
      <div class="card-body">
        <div class="row fw-bold border-info border-bottom border-2">
          <div class="col-md-1">S#</div>
          <div class="col-md-5">Employee</div>
          <div class="col-md-6">Leave Details</div>
        </div>
        <p v-if="results.items == undefined || results.items.length == 0">Nothing to show yet!</p>
        <div class="row row-striped mt-4" v-for="(r, i) in results.items" :key="r.id">
          <div class="col-md-1">{{ (results.pg_no - 1) * results.pg_size + i + 1 }}</div>
          <div class="col-md-5">
            <a :href="'#/leaves.status/' + r.user">
              <span class="me-2">{{r.first_name +" "+ r.last_name}}</span>
            </a>
            <span class="me-2">({{ labelFor(SD.UserRoles, r.role) }})</span>
            <span class="me-2">Joined: {{r.doj}}</span>
            <span>Area: {{labelFor(SD.WorkAreas, r.area)}}</span>
          </div>
          <div class="col-md-6">
            <span :class="['badge bg-primary me-2', {'bg-success': r.status=='APP'}, {'bg-danger': r.status=='REJ'}]">{{ labelFor(SD.WfStatuses, r.status) }}</span>
            <span class="me-2">
            Type: {{ labelFor(SD.LeaveTypes, r.leave_type) }}. 
            From {{r.start_dt}} to {{r.end_dt}}
            </span>
            <a class="btn btn-outline-primary" :href="'#/leave/' + r.id"><i class="bi bi-pencil"></i></a>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import UserLookupComp from "./UserLookupComp.vue";

export default {
  name: "LeaveApplicationSearch",
  components: {
    UserLookupComp
  },
  data: function () {
    return {
      selUser: {},
      crit: { pg_no: 1 },
      results: { items: [], has_next: false }
    };
  },
  computed: {
  },
  created: function () {
    console.log("Creating LeaveApplicationSearch");
  },
  mounted: function () {
    if (sessionStorage.lappSrch) {
      this.crit = JSON.parse(sessionStorage.lappSrch);
    }
    if (sessionStorage.laSrchRes) {
      this.results = JSON.parse(sessionStorage.laSrchRes);
    } else {
      this.results = { items: [], has_next: false };
    }
  },
  methods: {
    onUserSelect(c) {
      this.selUser = c;
      this.crit.user_id = c.id;
    },
    async next_pg() {
      this.crit.pg_no += 1;
      await this.find(true);
    },
    async prev_pg() {
      this.crit.pg_no -= 1;
      await this.find(true);
    },
    async find(is_paging) {
      let vm = this;
      if (!is_paging) vm.crit.pg_no = 1;
      sessionStorage.lappSrch = JSON.stringify(vm.crit);
      vm.results.items = [];
      await vm.doPost("leave_appl_find", vm.crit,
        (b) => {
          vm.results = b;
          sessionStorage.laSrchRes = JSON.stringify(vm.results);
        }, vm.setStatusMessage);
    },
    reset() {
      this.results = { items: [], has_next: false };
      this.crit = { pg_no: 1 };
      this.selUser = {}
      sessionStorage.laSrchRes = undefined;
      sessionStorage.lappSrch = undefined;
    }
  }
};
</script>
