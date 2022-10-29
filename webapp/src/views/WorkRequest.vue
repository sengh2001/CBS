<!--
Component for work request.

@author Balwinder Sodhi
-->
<template>
  <div class="container-fluid">
    <div class="card">
      <div class="card-header">
        <div class="fs-5 float-start">Work Request</div>
        <span class="badge text-bg-info ms-2" v-if="appl.user">
          {{appl.user.first_name}} {{appl.user.last_name}}, 
          {{labelFor(SD.UserRoles, appl.user.role)}}
        </span>
        <span class="float-end">
          <a class="btn btn-outline-success me-2" href="#/wreq">Add Another</a>
          <workflow-actions :button-label="Actions" :role-actions="actions" @action-selected="onAction" />
        </span>
      </div>
      <div class="card-body">
        <p class="text-center text-primary">!! All fields are required !!</p>
        <div class="row mb-2">
          <div class="col-md-4">
            <label for="status">Status
              <span class="fw-light ms-2" v-if="appl.upd_ts">@{{fmtDate(appl.upd_ts)}}</span>
            </label>
            <select disabled="disabled" class="form-select" id="status" v-model="appl.status">
              <option v-for="x in SD.WfStatuses" v-bind:value="x.id" :key="x.id">
                {{ x.value }}
              </option>
            </select>
          </div>
          <div class="col">
            <label for="dtrange">Dates
              <span class="text-danger">{{dateRangeValid ? "": "Invalid!"}}</span>
            </label>
            <div class="input-group">
              <input type="date" class="form-control" placeholder="Start date" aria-label="Start date"
                v-model="appl.start_dt">
              <span class="input-group-text"> To </span>
              <input type="date" class="form-control" placeholder="End date" aria-label="End date"
                v-model="appl.end_dt">
            </div>
          </div>
        </div>
        <div class="row mb-2">
          <div class="col-md-6">
            <label for="notes1">Reasons</label>
            <textarea id="notes1" class="form-control" rows="3" v-model="appl.reasons"></textarea>
          </div>
          <div class="col-md-6">
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
            <div class="card-body" v-if="showHistory">
              <ol class="list-group list-group-flush">
                <li class="list-group-item" v-for="(item, i) in appl.status_history" :key="item">
                  <span class="fw-bold me-2">{{i+1}}. </span>
                  <span class="badge text-bg-info me-2">{{fmtDate(item.old_row_data.upd_ts)}}</span>
                  <span class="badge text-bg-success me-2">
                    {{labelFor(SD.WfStatuses, item.old_row_data.status)}}
                  </span>
                  <span class="me-2"> From {{item.old_row_data.start_dt}} to {{item.old_row_data.end_dt}}.</span>
                  <span class="me-2" v-if="item.old_row_data.reasons"><b>Reason:</b> {{item.old_row_data.reasons}}</span>
                  <span class="me-2" v-if="item.old_row_data.approver_notes"><b>Appr. notes:</b> {{item.old_row_data.approver_notes}}</span>
                  <span v-if="item.old_row_data.upd_by"><b>By user:</b> {{item.old_row_data.upd_by}}</span>
                </li>
              </ol>
            </div>
          </div>
          <p v-else>No history available yet!</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import _ from "lodash";
import WorkflowActions from "./WorkflowActions.vue";
export default {
  name: "WorkRequest",
  components: {
    WorkflowActions
  },
  data: function () {
    return {
      appl: { status: "DRA" },
      actions: [],
      showHistory: false,
    };
  },
  computed: {
    isEdit() {
      console.log("isEdit() called");
      return this.$route.params.id > 0;
    },
    canEditApproverNotes() {
      return this.appl.user !== undefined &&
        (this.isUserOrAdmin(this.appl.user.id) ||
          this.isDir || this.isDean || this.isHOD)
    },
    dateRangeValid() {
      return this.appl.start_dt <= this.appl.end_dt
    }
  },
  async mounted() {
    console.log("Mounting Work Request");
    let vm = this;
    if (vm.isEdit) {
      await vm.load();
    } else {
      vm.reset();
    }
    await vm.getFormActions("WorkRequest", 
              vm.appl.status, (b)=>{vm.actions = b;})

    if (vm.$route.query["nr"] == 1) {
      vm.setStatusMessage("Saved the work request!");
      vm.$route.query = {};
    }
    vm.viewOnly = vm.appl.status !== "DRA" &&
      vm.appl.user !== undefined &&
      !vm.isUserOrAdmin(vm.appl.user.id)

  },
  methods: {
    async load() {
      let vm = this;
      let uid = vm.$route.params.id;
      console.log("Loading work request. id=" + uid);
      // Fetch data from an API
      await vm.doGet(`wreq_get/${uid}`, (b) => { vm.appl = b; },
        vm.setStatusMessage)
    },
    isValid() {
      // TODO:
      return true
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
      if (!confirm("Confirm save?")) {
        vm.setStatusMessage("User canceled save!");
        return;
      }
      console.log("Saving work request.");
      let fail = false
      try {
        await vm.doPost("wreq_save", vm.appl,
          (b) => {
            vm.appl = b;
            vm.setStatusMessage("Saved successfully!");
          }, (b)=>{fail=b});
        if (fail) throw fail
        if (vm.isEdit) {
          await vm.load()
        } else {
          vm.$router.push({ path: "/wreq/" + vm.appl.id, query: { nr: 1 } });
        }
      } catch (error) {
        vm.setStatusMessage(error);
      }
    },
    reset() {
      this.appl = { status: "DRA" };
      console.log("Clearing work request.");
    },
  },
};
</script>
