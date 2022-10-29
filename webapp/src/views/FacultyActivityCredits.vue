<!--
Component for faculty activity.

@author Balwinder Sodhi
-->
<template>
  <div class="container-fluid">
    <h5>Faculty Activity Credits Setup</h5>
    <div class="card">
      <div class="card-header text-bg-secondary">
        <div class="float-start">Admin Duties Credits</div>
        <div class="float-end">
          <button class="btn btn-sm btn-outline-primary" @click="addAdminDuty">Add</button>
        </div>
      </div>
      <div class="card-body">
        <admin-work-comp :items="adminWork" @item-copied="addAdminDuty"/>
      </div>
    </div>
    <div class="card mt-2">
      <div class="card-header">
        <div class="float-start">Research Credits</div>
        <div class="float-end">
          <button class="btn btn-sm btn-outline-primary" @click="addPublication">Add</button>
        </div>
      </div>
      <div class="card-body">
        <p v-if="researchWork.length == 0">Nothing to show yet!</p>
        <div v-else>
          <div class="row g-1">
            <div class="col-md-1">S#</div>
            <div class="col-md-3">Classification</div>
            <div class="col-md-2">Pub. Type</div>
            <div class="col-md-1">Credits</div>
            <div class="col-md-3">Validity Period</div>
            <div class="col-md-2">Status</div>
          </div>
          <div class="row mb-2 g-1" v-for="(pb, i) in researchWork" :key="pb.id">
            <div class="col-md-1">{{ i + 1 }}.</div>
            <div class="col-md-3">
              <input type="text" class="form-control" v-model="pb.classif" :disabled="viewOnly" />
            </div>
            <div class="col-md-2">
              <select class="form-select" id="work_type" v-model="pb.pub_type" :disabled="viewOnly">
                <option v-for="x in SD.PubTypes" v-bind:value="x.id" :key="x.id">
                  {{ x.value }}
                </option>
              </select>
            </div>
            <div class="col-md-1">
              <input type="number" min="0" class="form-control" v-model="pb.credits" :disabled="viewOnly" />
            </div>
            <div class="col-md-3">
              <div class="input-group">
                <input type="date" class="form-control p-1" v-model="pb.valid_from">
                <span class="input-group-text">To</span>
                <input type="date" class="form-control p-1" v-model="pb.valid_till">
              </div>
            </div>
            <div class="col-md-2">
              <div class="input-group">
                <select class="form-select" id="status" v-model="pb.status" :disabled="viewOnly">
                  <option v-for="x in SD.WfStatuses" v-bind:value="x.id" :key="x.id">
                    {{ x.value }}
                  </option>
                </select>
                <button class="btn btn-sm btn-outline-primary ms-2 me-1" @click="saveResItem(pb)" title="Save row data"><i class="bi bi-save" role="button"></i></button>
                <button class="btn btn-sm btn-outline-info me-1" title="Copy this row" @click="addPublication(pb)"><i class="bi bi-clipboard-plus" role="button"></i></button>
                <button class="btn btn-sm btn-outline-danger" @click="removeResItem(pb)" title="Delete this row"><i
                    class="bi bi-trash-fill"></i></button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import _ from "lodash";
import AdminWorkComp from "./AdminWorkComp.vue";

export default {
  name: "FacultyActivityCredits",
  components: {
    AdminWorkComp
  },
  data: function () {
    return {
      adminWork: [],
      researchWork: [],
      roleActions: {
        "SUP": [
          { label: "Save Draft", arg: "DRA" },
          { label: "Submit", arg: "SUB" },
          { label: "Approve", arg: "APP" },
          { label: "Reject", arg: "REJ" },
          { label: "Withdraw", arg: "WIT" }
        ],
        "DEA": [
          { label: "Approve", arg: "APP" },
          { label: "Reject", arg: "REJ" },
        ],
        "FAC": [
          { label: "Save Draft", arg: "DRA" },
          { label: "Submit", arg: "SUB" },
          { label: "Withdraw", arg: "WIT" }
        ],
        "STA": [
          { label: "Save Draft", arg: "DRA" },
          { label: "Submit", arg: "SUB" },
          { label: "Withdraw", arg: "WIT" }
        ]
      }
    };
  },
  computed: {
    isEdit() {
      console.log("isEdit() called");
      return this.$route.params.id > 0;
    },
    actions() {
      return this.roleActions[this.userRole]
    }
  },
  async created() {
    console.log("Creating FacultyActivityCredits");
    await this.loadCredits()
  },
  methods: {
    addItemToList(list, item) {
      let obj = {}
      if (item !== undefined) {
        Object.assign(obj, item)
        obj.id = undefined
      }
      list.push(obj)
    },
    addAdminDuty(obj) {
      this.addItemToList(this.adminWork, obj)
    },
    addPublication(obj) {
      this.addItemToList(this.researchWork, obj)
    },
    async loadCredits() {
      const vm = this;
      await vm.doGet("get_credits/AD/N", b => { vm.adminWork = b },
        vm.setStatusMessage)
      await vm.doGet("get_credits/RES/N", b => { vm.researchWork = b },
        vm.setStatusMessage)
    },
    async saveResItem(obj) {
      let vm = this;
      if (!confirm("Confirm save?")) {
        vm.setStatusMessage("User canceled save!");
        return;
      }
      console.log("Saving research credit details.");
      await vm.doPost("res_credit_save", obj,
        (b) => {
          obj.id = b.id;
          vm.setStatusMessage("Saved successfully!");
        }, vm.setStatusMessage);
    },
    async removeResItem(obj) {
      let vm = this;
      if (!confirm("Confirm delete?")) {
        vm.setStatusMessage("User canceled delete!");
        return;
      }
      console.log("Deleting research credit details.");
      await vm.doGet(`res_credit_del/${obj.id}`,
        (b) => { this.$emit("itemDeleted", obj) }, vm.setStatusMessage)
    }
  },
};
</script>
