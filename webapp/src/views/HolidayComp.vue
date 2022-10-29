<!--
Component for a holiday item.

@author Balwinder Sodhi
-->
<template>
  <div>
    <div v-if="!editMode">
      {{labelFor(SD.DurationTypes, item.period_type)}}. 
      During {{item.start_dt}} to {{item.end_dt}}.
      (<span class="fw-light">{{item.description}}.</span>)
    </div>
    <div v-else>
      <input type="text" class="form-control mb-2" v-model="item.description" 
        placeholder="Description of the item."/>
      <div class="input-group">
        <span class="input-group-text">From:</span>
        <input type="date" class="form-control" v-model="item.start_dt" />
        <span class="input-group-text">To:</span>
        <input type="date" class="form-control" v-model="item.end_dt" />
        <span class="input-group-text ms-2">Type:</span>
        <select class="form-select" v-model="item.period_type">
          <option v-for="x in SD.DurationTypes" v-bind:value="x.id" :key="x.id">
            {{ x.value }}
          </option>
        </select>
        <button class="btn btn-outline-success ms-2" type="button" @click="$emit('itemSaved', item)">
          <i class="bi bi-save"></i></button>
        <button class="btn btn-outline-danger" type="button" @click="$emit('itemRemoved', item)">
          <i class="bi bi-trash"></i></button>
      </div>
    </div>
  </div>
</template>

<script>

export default {
  name: "HolidayComp",
  components: { },
  props: { 
          "initialValue": Object, 
          "editMode": { type: Boolean, default: true} 
        },
  emits: ["itemSaved", "itemRemoved"],
  data: function () {
    return { 
      item: {}
    };
  },
  async mounted() {
    console.log("Mounting HolidayComp. Initial value=" + JSON.stringify(this.initialValue));
    this.item = this.initialValue
  },
  methods: { },
};
</script>
