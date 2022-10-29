<!--
Component for admin work.

@author Balwinder Sodhi
-->
<template>
  <p v-if="items == undefined || items.length==0">
    Nothing to show yet!
  </p>
  <div v-else>
    <div class="row mb-2 g-1">
      <div class="col-md-1">S#</div>
      <div class="col-md-3">Type of work</div>
      <div class="col-md-2">Credits</div>
      <div class="col-md-4">Validity Period</div>
      <div class="col">Status</div>
    </div>
    <div class="row mt-2 g-1" v-for="(aw, i) in items" :key="aw.id">
      <div class="col-md-1">{{i+1}}.</div>
      <div class="col-md-3">
        <input
          type="text"
          class="form-control"
          id="work_type"
          v-model="aw.work_type"
          :disabled="viewOnly"
        />
      </div>
      <div class="col-md-2">
        <input
          type="number"
          step="1"
          min="0"
          class="form-control"
          id="credits"
          v-model="aw.credits"
          :disabled="viewOnly"
        />
      </div>
      <div class="col-md-4">
        <div class="input-group">
          <input
            type="date"
            class="form-control p-1"
            id="valid_from"
            v-model="aw.valid_from"
            :disabled="viewOnly"
          />
          <span class="input-group-text">To</span>
          <input
            type="date"
            class="form-control p-1"
            id="valid_till"
            v-model="aw.valid_till"
            :disabled="viewOnly"
          />
        </div>
      </div>
      <div class="col">
        <div class="input-group">
          <select
            class="form-select"
            id="status"
            v-model="aw.status"
            :disabled="viewOnly"
          >
            <option v-for="x in SD.WfStatuses" v-bind:value="x.id" :key="x.id">
              {{ x.value }}
            </option>
          </select>
          <button class="btn btn-sm btn-outline-primary ms-2 me-1" @click="save(aw)" title="Save row data"><i class="bi bi-save" role="button"></i></button>
          <button class="btn btn-sm btn-outline-info me-1" @click="copyRow(aw)" title="Copy this row"><i class="bi bi-clipboard-plus"></i></button>
          <button class="btn btn-sm btn-outline-danger" @click="remove(aw)" title="Delete this row"><i class="bi bi-trash-fill"></i></button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: "AdminWorkComp",
  components: {},
  props: { items: Array },
  emits: ["itemDeleted", "itemCopied"],
  data: function () {
    return {};
  },
  async created() {
    console.log("Creating AdminWorkComp");
  },
  methods: {
    async save(obj) {
      let vm = this;
      if (!confirm("Confirm save?")) {
        vm.setStatusMessage("User canceled save!");
        return;
      }
      console.log("Saving admin credit details.");
      await vm.doPost("ad_credit_save", obj, 
        (b) => {
          obj.id = b.id;
          vm.setStatusMessage("Saved successfully!");
        }, vm.setStatusMessage);
    },
    async remove(obj) {
      let vm = this;
      if (!confirm("Confirm delete?")) {
        vm.setStatusMessage("User canceled delete!");
        return;
      }
      console.log("Deleting admin credit details.");
      await vm.doGet(`ad_credit_del/${obj.id}`,
        (b)=>{this.$emit("itemDeleted", obj)}, vm.setStatusMessage)
    },
    copyRow(obj) {
      this.$emit("itemCopied", obj)
    }
  },
};
</script>
