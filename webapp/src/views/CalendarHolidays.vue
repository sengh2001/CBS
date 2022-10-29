<!--
Component for calendar holidays.

@author Balwinder Sodhi
-->
<template>
  <div class="container-fluid">
    <div class="card">
      <div class="card-header">
        <b>Select an Action: </b>
        <div class="form-check form-check-inline">
          <input class="form-check-input" type="radio" name="actionOpt" id="act1" value="show" v-model="action">
          <label class="form-check-label" for="act1">Show Holiday Info</label>
        </div>
        <div class="form-check form-check-inline">
          <input class="form-check-input" type="radio" name="actionOpt" id="act2" value="add"  v-model="action">
          <label class="form-check-label" for="act2">Add Item</label>
        </div>
        <div class="form-check form-check-inline">
          <input class="form-check-input" type="radio" name="actionOpt" id="act3" value="upload" v-model="action">
          <label class="form-check-label" for="act3">Upload Items in Bulk</label>
        </div>
      </div>
      <div class="card-body" v-if="action=='show'">
        <div class="input-group mb-3">
          <span class="input-group-text">Type:</span>
          <select class="form-select" v-model="holidayType">
            <option value="ALL">Show Everything</option>
            <option v-for="x in SD.DurationTypes" v-bind:value="x.id" :key="x.id">
              {{ x.value }}
            </option>
          </select>
          <span class="input-group-text">Calendar year:</span>
          <input type="text" class="form-control" placeholder="YYYY (e.g. 2018)"
            aria-label="Year to load" aria-describedby="loadBtn" v-model="yearToLoad">
          <button id="loadBtn" class="btn btn-outline-success" type="button" @click="load">
            Load</button>
          <button class="btn btn-outline-danger" type="button" @click="reset">
            Clear</button>
        </div>
        <div class="form-check form-switch">
          <input class="form-check-input" type="checkbox" role="switch" id="swt" v-model="editMode">
          <label class="form-check-label" for="swt">Editable Results</label>
        </div>
        <p v-if="calHols.length == 0">No data to show yet!</p>
        <div v-else class="row row-cols-md-2 g-2">
          <div class="col p-2 border" v-for="x in calHols" :key="x">
            <HolidayComp :editMode="editMode" :initial-value="x" @item-saved="saveItem" @item-removed="removeItem"/>
          </div>
        </div>
      </div>
      <div class="card-body" v-if="action=='add'">
        <HolidayComp :initial-value="{}" @item-saved="saveItem" @item-removed="removeItem"/>
      </div>
      <div class="card-body" v-if="action=='upload'">
        Action not implemented yet: {{action}}
      </div>
    </div>
  </div>
</template>

<script>
import HolidayComp from "./HolidayComp.vue"
export default {
  name: "CalendarHolidays",
  components: {
    HolidayComp
  },
  data: function () {
    return {
      yearToLoad: "",
      holidayType: "ALL",
      calHols: [],
      action: "show",
      editMode: false
    };
  },
  computed: {},
  async mounted() {
    console.log("Mounted CalendarHolidays");
  },
  methods: {
    reset() {
      this.calHols = []
      this.yearToLoad = ""
      this.holidayType = "ALL"
    },
    async saveItem(obj) {
      if (!confirm("Confirm save?")) return
      const vm = this;
      await vm.doPost("hol_save", obj,
        (b) => {
          vm.setStatusMessage("Saved the record!")
        }, vm.setStatusMessage)
    },
    async removeItem(obj) {
      if (!confirm("Confirm delete?")) return
      const vm = this;
      vm.calHols = vm.calHols.filter(function (item) {
        return item.id !== obj.id
      })
      if (obj.id !== undefined) {
        await vm.doGet(`hol_delete/${obj.id}`,
          vm.setStatusMessage, vm.setStatusMessage)
      }
    },
    async load() {
      const vm = this;
      if (vm.yearToLoad) {
        await vm.doGet(`list_holidays/${vm.yearToLoad}/${vm.holidayType}`,
          (b)=>{vm.calHols = b}, vm.setStatusMessage)
      }
    },
    copyItem(obj) {
      let cp = {}
      Object.assign(cp, obj)
      cp.id = undefined
      this.calHols.push(cp)
    }
  },
};
</script>
