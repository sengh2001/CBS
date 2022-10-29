<!--
Component for searching leave rules.

@author Balwinder Sodhi
-->
<template>
  <div class="container-fluid">
    <h5>Find Leave Rules</h5>
    <form @submit.prevent="find(false)">
      <div class="row mb-2">
        <div class="col-md-2">
          <label for="sub_role">Employee Role</label>
          <select class="form-select" id="sub_role" v-model="rule.sub_role">
            <option v-for="x in SD.UserRoles" v-bind:value="x.id" :key="x.id">
              {{ x.value }}
            </option>
          </select>
        </div>
        <div class="col-md-2">
          <label for="leave_type">Leave Type</label>
          <select class="form-select" id="leave_type" v-model="rule.leave_type">
            <option v-for="x in SD.LeaveTypes" v-bind:value="x.id" :key="x.id">
              {{ x.value }}
            </option>
          </select>
        </div>
        <div class="col-md-2">
          <label for="vfrm">Valid From</label>
          <input class="form-control" type="date" id="vfrm" v-model="rule.valid_from" />
        </div>
        <div class="col-md-2">
          <div class="form-check mt-4">
            <input class="form-check-input" type="checkbox" id="cb2" v-model="rule.encashable" />
            <label class="form-check-label" for="cb2">
              Encashable
            </label>
          </div>
        </div>
        <div class="col">
          <div class="mt-4">
            <button class="btn btn-outline-success me-2" type="submit">
              <i class="bi bi-search"></i>
            </button>
            <button class="btn btn-outline-danger me-2" @click="reset" type="reset">
              <i class="bi bi-eraser"></i>
            </button>
            <a class="btn btn-sm btn-primary float-end" href="#/rule">Create New</a>
          </div>
        </div>
      </div>
    </form>
    <div class="card">
      <div class="card-header">
        <span class="fs-5">Results</span>
        <span class="float-end">
          <button class="btn btn-outline-info btn-sm me-4" v-if="rule.pg_no > 1" @click="prev_pg">Prev</button>
          <button class="btn btn-outline-info btn-sm me-4" v-if="results.has_next" @click="next_pg">Next</button>
        </span>
      </div>
      <div class="card-body">
        <div class="row fw-bold border-info border-bottom border-2">
          <div class="col-md-1">S#</div>
          <div class="col-md-2">Emp. Role</div>
          <div class="col-md-2">Leave Type</div>
          <div class="col-md">Details</div>
        </div>
        <p v-if="results.ruleList == undefined || results.ruleList.length == 0">Nothing to show yet!</p>
        <div class="row row-striped mt-4" v-for="(r, i) in results.ruleList" :key="r.id">
          <div class="col-md-1">{{ (results.pg_no - 1) * results.pg_size + i + 1 }}</div>
          <div class="col-md-2">
            <a :href="'#/rule/' + r.id">
              {{ labelFor(SD.UserRoles, r.sub_role) }}
            </a>
          </div>
          <div class="col-md-2">
            {{ labelFor(SD.LeaveTypes, r.leave_type) }}
          </div>
          <div class="col-md">{{ leaveDetails(r) }}</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: "LeaveRuleSearch",
  data: function () {
    return {
      rule: { pg_no: 1 },
      results: { ruleList: [], has_next: false }
    };
  },
  computed: {
  },
  created: function () {
    console.log("Creating LeaveRuleSearch");
  },
  mounted: function () {
    if (sessionStorage.ruleSrch) {
      this.rule = JSON.parse(sessionStorage.ruleSrch);
    }
    if (sessionStorage.myUserS) {
      this.results = JSON.parse(sessionStorage.myUserS);
    } else {
      this.results = { ruleList: [], has_next: false };
    }
  },
  methods: {
    leaveDetails(d) {
      // TODO:
      const enc = d.encashable ? "Encashable" : "Non-encashable"
      const rolls = d.rolls_over ? "Rolls over" : "Doesn't Roll over"
      const frac = d.fraction_allowed ? "Fraction allowed" : "Fraction not allowed"
      return `Yearly quota: ${d.yearly_quota}. Max. accrual: ${d.max_accrual}.
      ${enc}. ${rolls}. ${frac}. Min. service: ${d.min_service_years}yrs.
      Max. per instance: ${d.max_per_instance}. Validity period: ${d.valid_from} to 
      ${d.valid_till==null?'present':d.valid_till}.`
    },
    async next_pg() {
      this.rule.pg_no += 1;
      await this.find(true);
    },
    async prev_pg() {
      this.rule.pg_no -= 1;
      await this.find(true);
    },
    async find(is_paging) {
      let vm = this;
      if (!is_paging) vm.rule.pg_no = 1;
      sessionStorage.ruleSrch = JSON.stringify(vm.rule);
      vm.results.ruleList = [];
      await vm.doPost("rule_find", vm.rule,
        (b) => {
          vm.results = b;
          sessionStorage.myUserS = JSON.stringify(vm.results);
        }, vm.setStatusMessage);
    },
    reset() {
      this.results = { ruleList: [], has_next: false };
      this.rule = { pg_no: 1 };
      sessionStorage.myUserS = undefined;
      sessionStorage.ruleSrch = undefined;
    }
  }
};
</script>
