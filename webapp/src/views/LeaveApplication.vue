<!--
Component for leave application.

@author Balwinder Sodhi
-->
<template>
  <div class="container-fluid">
    <form>
      <div class="card">
        <div class="card-header">
          <div class="fs-5 float-start">Leave Application</div>
          <span class="badge text-bg-info ms-2" v-if="appl.user">
            {{appl.user.first_name}} {{appl.user.last_name}}, 
            {{labelFor(SD.UserRoles, appl.user.role)}}
          </span>
          <span class="text-danger ms-2" v-if="inBlackout">
            Selected dates overlap blacked out period!</span>
          <span class="float-end">
            <a class="btn btn-outline-success me-2" href="#/leave">Apply Afresh</a>
            <workflow-actions :button-label="Actions" :role-actions="actions" @action-selected="onAction" />
          </span>
        </div>
        <div class="card-body">
          <p class="text-center text-primary">!! All fields are required !!</p>
          <div class="row mb-2">
            <div class="col-md-3">
              <label for="status">Status
                <span class="fw-light ms-2" v-if="appl.upd_ts">@{{fmtDate(appl.upd_ts)}}</span>
              </label>
              <select disabled="disabled" class="form-select" id="status" v-model="appl.status">
                <option v-for="x in SD.WfStatuses" v-bind:value="x.id" :key="x.id">
                  {{ x.value }}
                </option>
              </select>
            </div>
            <div class="col-md-3">
              <label for="leave_type">Leave Type</label>
              <select class="form-select" id="leave_type" required v-model="appl.leave_type" :disabled="viewOnly">
                <option v-for="x in SD.LeaveTypes" v-bind:value="x.id" :key="x.id">
                  {{ x.value }}
                </option>
              </select>
            </div>
            <div class="col-md-6">
              <label for="dtrange">Dates <span class="text-danger">{{dateRangeValid ? "": "Invalid!"}}</span></label>
              <div class="input-group">
                <input type="date" class="form-control" placeholder="Start date" aria-label="Start date"
                  required v-model="appl.start_dt" :disabled="viewOnly">
                <span class="input-group-text"> To </span>
                <input type="date" class="form-control" placeholder="End date" aria-label="End date"
                  required v-model="appl.end_dt" :disabled="viewOnly">
              </div>
            </div>
          </div>
          <div class="row">
            <div class="col-md-2">
              <div class="form-check mt-4">
                <input class="form-check-input" type="checkbox" value="" id="lvStn"
                v-model="appl.leaving_stn" :disabled="viewOnly">
                <label class="form-check-label" for="lvStn">
                  Leaving Station?
                </label>
              </div>
            </div>
            <div class="col-md-2">
              <label for="fnan">FN/AN</label>
              <select class="form-select" id="fnan" required 
                v-model="appl.fn_an" :disabled="viewOnly">
                <option value="NA">N/A</option>
                <option value="FN">Forenoon</option>
                <option value="AN">Afternoon</option>
              </select>
            </div>
            <div class="col-md-2">
              <label for="lvPh">Phone No. During Leave</label>
              <input type="tel" class="form-control" id="lvPh" v-model="appl.leave_phone"
              required :disabled="viewOnly"/>
            </div>
            <div class="col-md-6">
              <label for="adrStn">Address During Leave</label>
              <input type="text" class="form-control" id="adrStn" v-model="appl.leave_addr"
              required :disabled="viewOnly"/>
            </div>
          </div>
          <div class="row mb-2">
            <div class="col-md-4">
              <label for="notes1">Reasons for Leave</label>
              <textarea id="notes1" class="form-control" rows="3" v-model="appl.applicant_notes"
              required :disabled="viewOnly"></textarea>
            </div>
            <div class="col-md-4">
              <label for="notes3">Recommender Notes</label>
              <textarea id="notes3" class="form-control" rows="3"
              :disabled="!canEditRecoNotes"
              v-model="appl.reco_notes"></textarea>
            </div>
            <div class="col-md-4">
              <label for="notes2">Approver Notes</label>
              <textarea id="notes2" class="form-control" rows="3" :disabled="!canEditApproverNotes"
                v-model="appl.approver_notes"></textarea>
            </div>
          </div>
          <div>
            <div class="card" v-if="appl.status_history && appl.status_history.length > 0">
              <div class="card-header">Record History
                <span role="button" class="float-end" @click="showHistory=!showHistory">
                  <i v-if="showHistory" class="bi bi-dash-square"></i>
                  <i v-else class="bi bi-plus-square"></i>
                </span>
              </div>
              <div v-if="showHistory" class="card-body">
                <ol class="list-group list-group-flush">
                  <li class="list-group-item" v-for="(s, i) in appl.status_history" :key="s">
                    <leave-application-record :sno="i+1" :item="s.old_row_data"/>
                  </li>
                </ol>
              </div>
            </div>
            <p v-else>No history available yet!</p>
          </div>
        </div>
      </div>
    </form>
  </div>
</template>

<script>
import _ from "lodash";
import WorkflowActions from "./WorkflowActions.vue";
import LeaveApplicationRecord from "./LeaveApplicationRecord.vue"
export default {
  name: "LeaveApplication",
  components: {
    WorkflowActions,
    LeaveApplicationRecord
  },
  data: function () {
    return {
      inBlackout: false,
      appl: { status: "DRA", fn_an: "NA" },
      actions: [],
      showHistory: false
    };
  },
  watch: {
    "appl.start_dt": async function() {
      await this.checkBlackoutDays()
    },
    "appl.end_dt": async function() {
      await this.checkBlackoutDays()
    },
    "appl.leave_type": function(val, old) {
      if (val != "CL") {
        this.appl.fn_an = "NA"
      }
    }
  },
  computed: {
    isEdit() {
      console.log("isEdit() called");
      return this.$route.params.id > 0;
    },
    canEditApproverNotes() {
      if (this.isAdmin) return true;
      const ok = ["SUB", "SUBREC"].includes(this.appl.status) &&
        (this.isDir || this.isDean || this.isHOD)
      console.log("canEditApproverNotes="+ok)
      return ok;
    },
    canEditRecoNotes() {
      return this.canEditApproverNotes || this.isManager
    },
    dateRangeValid() {
      return this.appl.start_dt <= this.appl.end_dt
    }
  },
  async mounted() {
    console.log("Mounting Leave Application");
    let vm = this;
    try {
      if (vm.isEdit) {
        await vm.load();
        await vm.checkBlackoutDays()
      } else {
        vm.reset();
      }
      await vm.getFormActions("LeaveApplication", 
                vm.appl.status, (b)=>{vm.actions = b;})
      if (vm.$route.query["nr"] == 1) {
        vm.setStatusMessage("Saved the leave application!");
        vm.$route.query = {};
      }
      vm.viewOnly = vm.appl.status !== "DRA" &&
        vm.appl.user !== undefined &&
        !vm.isUserOrAdmin(vm.appl.user)
    } catch (error) {
      vm.setStatusMessage(error)
    }
  },
  methods: {
    async load() {
      let vm = this;
      let uid = vm.$route.params.id;
      let error = false
      console.log("Loading leave application. id=" + uid);
      // Fetch data from an API
      await vm.doGet(`leave/${uid}`, (b) => { vm.appl = b; },
        (b)=> {error = b})
      if (error) throw error
    },
    async checkBlackoutDays() {
      let vm = this;
      await vm.doGet(`isblackout/${vm.appl.start_dt}/${vm.appl.end_dt}`,
        (b) => { vm.inBlackout = b; }, vm.setStatusMessage)
      console.log("inBlackout = "+vm.inBlackout)
    },
    isValid() {
      return true
      // return !(_.isEmpty(this.appl.email) || _.isEmpty(this.appl.first_name)
      //   || _.isEmpty(this.appl.last_name));
    },
    async onAction(act) {
      console.log("Action: " + JSON.stringify(act));
      // Action 'arg' has the status value to be set
      this.appl.status = act.arg
      await this.save()
    },
    async save() {
      let vm = this;
      if (!this.isValid()) {
        vm.setStatusMessage("Please supply all required fields!");
        return;
      }
      if (vm.inBlackout && !confirm("Are you sure you want to apply during blackout duration?")) {
        return
      }
      if (!confirm("Confirm save?")) {
        if (vm.isEdit) await vm.load()
        return;
      }
      console.log("Saving leave application.");
      try {
        let fail = false
        await vm.doPost("leave_appl_save", vm.appl,
        (b) => {
          vm.appl = b;
          vm.setStatusMessage("Saved successfully!");
        }, (b) => {fail = b});
        if (fail) throw fail
        if (vm.isEdit) {
          await vm.load()
        } else {
          vm.$router.push({ path: "/leave/" + vm.appl.id, query: { nr: 1 } });
        }
      } catch (error) {
        vm.setStatusMessage(error)
      }
      
    },
    reset() {
      this.appl = { status: "DRA", fn_an: "NA" };
      console.log("Clearing leave application.");
    },
  },
};
</script>
