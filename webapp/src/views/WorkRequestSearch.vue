<!--
Component for searching work requests.

@author Balwinder Sodhi
-->
<template>
  <div class="container-fluid">
    <h5>Find Work Requests</h5>
    <form @submit.prevent="find(false)">
      <div class="row mb-2">
        <div class="col-md-3">
          <label for="status">Status</label>
          <select class="form-select" id="status" v-model="crit.status">
            <option v-for="x in SD.WfStatuses" v-bind:value="x.id" :key="x.id">
              {{ x.value }}
            </option>
          </select>
        </div>
        <div class="col-md-4">
          <label for="emp">Employee</label>
          <user-lookup-comp @userSelected="onUserSelect"/>
        </div>
        <div class="col-md-4">
          <label for="dtrange">Dates</label>
          <div class="input-group">
            <input type="date" class="form-control" placeholder="Start date" aria-label="Start date" v-model="crit.start_dt">
            <span class="input-group-text"> To </span>
            <input type="date" class="form-control" placeholder="End date" aria-label="End date" v-model="crit.end_dt">
          </div>
        </div>
        <div class="col">
          <div class="mt-4">
            <button class="btn btn-outline-success me-2" type="submit">
              <i class="bi bi-search"></i>
            </button>
            <button class="btn btn-outline-danger" @click="reset" type="reset">
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
          <div class="col-md-6">Request Details</div>
        </div>
        <p v-if="results.items == undefined || results.items.length == 0">Nothing to show yet!</p>
        <div class="row row-striped mt-4" v-for="(r, i) in results.items" :key="r.id">
          <div class="col-md-1">{{ (results.pg_no - 1) * results.pg_size + i + 1 }}</div>
          <div class="col-md-4">
            <a :href="'#/leaves.status/' + r.user.id">
              <span class="me-2">{{r.user.first_name +" "+ r.user.last_name}}</span>
            </a>
            <span class="me-2">({{ labelFor(SD.UserRoles, r.user.role) }})</span>
            <span class="me-2">Joined: {{r.user.profile.doj}}</span>
            <span class="me">Area: {{ labelFor(SD.WorkAreas, r.user.profile.area) }}</span>
          </div>
          <div class="col">
            <span :class="['badge bg-primary me-2', {'bg-success': r.status=='APP'}, {'bg-danger': r.status=='REJ'}]">{{ labelFor(SD.WfStatuses, r.status) }}</span>
            Period: {{r.start_dt}} to {{r.end_dt}}
            <span class="ms-2">Reasons: {{r.reasons}}</span>
            <span class="ms-2">Approver notes: {{r.approver_notes}}</span>
            <a class="ms-2 btn btn-outline-primary" :href="'#/wreq/' + r.id"><i class="bi bi-pencil"></i></a>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import UserLookupComp from "./UserLookupComp.vue";
import _ from "lodash";

export default {
  name: "WorkRequestSearch",
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
    console.log("Creating WorkRequestSearch");
  },
  mounted: function () {
    if (sessionStorage.wreqSrch) {
      this.crit = JSON.parse(sessionStorage.wreqSrch);
    }
    if (sessionStorage.wrSrchRes) {
      this.results = JSON.parse(sessionStorage.wrSrchRes);
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
      sessionStorage.wreqSrch = JSON.stringify(vm.crit);
      vm.results.items = [];
      await vm.doPost("wreq_find", vm.crit,
        (b) => {
          vm.results = b;
          sessionStorage.wrSrchRes = JSON.stringify(vm.results);
        }, vm.setStatusMessage);
    },
    reset() {
      this.results = { items: [], has_next: false };
      this.crit = { pg_no: 1 };
      this.selUser = {}
      sessionStorage.wrSrchRes = undefined;
      sessionStorage.wreqSrch = undefined;
    }
  }
};
</script>
