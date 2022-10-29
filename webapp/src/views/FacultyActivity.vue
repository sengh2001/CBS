<!--
Component for faculty activity.

@author Balwinder Sodhi
-->
<template>
  <div class="container-fluid">
    <h5>Activity details for {{userName}}</h5>
    <div class="card">
      <div class="card-header text-bg-secondary">
        <div class="float-start">Admin Duties</div>
        <div class="float-end">
          <button class="btn btn-sm btn-outline-primary" @click="addAdminDuty">Add</button>
        </div>
      </div>
      <div class="card-body">
        <p v-if="adminWork.length == 0">Nothing to show yet!</p>
        <div v-else>
          <div class="row">
            <div class="col-md-1">S#</div>
            <div class="col-md-5">Type of Work</div>
            <div class="col-md-2">Status</div>
            <div class="col-md-4">Work Period</div>
          </div>
          <div class="row mb-2" v-for="(pb, i) in adminWork" :key="pb.id">
            <div class="col-md-1">{{i+1}}.</div>
            <div class="col-md-5">
              <select class="form-select" id="work_type" v-model="pb.credit" :disabled="viewOnly">
                <option v-for="x in ADCredits" v-bind:value="x.id" :key="x.id">
                  {{ x.value }}
                </option>
              </select>
            </div>
            <div class="col-md-2">
              <select class="form-select" id="status" v-model="pb.status" :disabled="viewOnly">
                <option v-for="x in SD.WfStatuses" v-bind:value="x.id" :key="x.id">
                  {{ x.value }}
                </option>
              </select>
            </div>
            <div class="col-md-4">
              <div class="input-group">
                <input type="date" class="form-control" v-model="pb.start_dt">
                <span class="input-group-text"> To </span>
                <input type="date" class="form-control" v-model="pb.end_dt">
                <button class="btn btn-sm btn-outline-primary ms-2 me-2" @click="saveAdminItem(pb)"><i class="bi bi-save" role="button"></i></button>
                <button class="btn btn-sm btn-outline-danger" @click="removeAdminItem(pb)"><i class="bi bi-trash-fill"></i></button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
    <div class="card mt-2">
      <div class="card-header text-bg-secondary">
        <div class="float-start">Research Work</div>
        <div class="float-end">
          <button class="btn btn-sm btn-outline-primary" @click="addPublication">Add</button>
        </div>
      </div>
      <div class="card-body">
        <publication-comp :items="pubs" @item-saved="savePublication" @item-deleted="deletePublication"/>
      </div>
    </div>
  </div>
</template>

<script>
import _ from "lodash";
import PublicationComp from "./PublicationComp.vue";

export default {
  name: "FacultyActivity",
  components: {
    PublicationComp
  },
  data: function () {
    return {
      userName: "",
      ADCredits: [],
      adminWork: [],
      pubs: []
    };
  },
  computed: {
    isEdit() {
      console.log("isEdit() called");
      return this.$route.params.id > 0;
    }
  },
  async created() {
    console.log("Creating FacultyActivity");
    const vm = this;
    await vm.doGet("get_credits/AD/Y", b => { vm.ADCredits = b },
      vm.setStatusMessage)
    const uid = vm.isEdit ? vm.$route.params.id : vm.currentUser.id
    await vm.doGet("user_activities/"+uid, 
      b => {
        vm.userName = b["userName"]
        vm.adminWork = b["adminWork"]
        vm.pubs = b["pubs"]
      },
      vm.setStatusMessage)
  },
  methods: {
    addAdminDuty() {
      this.adminWork.push({})
    },
    addPublication() {
      this.pubs.push({})
    },
    async saveAdminItem(obj) {
      if (!confirm("Confirm save?")) return
      const vm = this;
      await vm.doPost("ad_activity_save", obj, 
        (b) => {
          obj.id = b.id
          obj.status = b.status
          vm.setStatusMessage("Saved the admin activity record!")
        }, vm.setStatusMessage)
    },
    async removeAdminItem(obj) {
      if (!confirm("Confirm delete?")) return
      const vm = this;
      await vm.doGet("activity_del/"+obj.id+"/AD", 
        vm.setStatusMessage, vm.setStatusMessage)
    },
    async savePublication(obj) {
      const vm = this;
      await vm.doPost("pub_activity_save", obj, 
        (b) => {
          obj.id = b.id
          obj.status = b.status
          vm.setStatusMessage("Saved publication record!")
        }, vm.setStatusMessage)
    },
    async deletePublication(obj) {
      const vm = this;
      await vm.doGet("activity_del/"+obj.id+"/RES", 
        vm.setStatusMessage, vm.setStatusMessage)
    }
  },
};
</script>
