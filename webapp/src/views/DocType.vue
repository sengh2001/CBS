<!--
Component for leave rules.

@author Balwinder Sodhi
-->
<template>
  <div class="card">
    <div class="card-header">
      <span>Doc Type</span>
      <span class="float-end" v-if="!viewOnly">
        <button type="button" class="btn btn-sm btn-outline-primary me-2" @click="saveDocType">Save</button>
        <button type="button" class="btn btn-sm btn-outline-danger" @click="reset">Clear</button>
      </span>
    </div>
    <div class="card-body">
      <div class="row mb-2">
        <div class="col-md-3">
          <label for="doc_name">Name</label>
          <input type="text" required class="form-control" id="doc_name"
          v-model="doc_type.name" :disabled="viewOnly" />
        </div>
        <div class="col-md-3">
          <label for="docdesc">Description</label>
          <input type="text" required class="form-control" id="docdesc"
          v-model="doc_type.description" :disabled="viewOnly" />
        </div>
      </div>
    </div>
    <div class="card-header">
      <span>Doc Fields</span>
      <span class="float-end" v-if="!viewOnly">
        <button type="button" class="btn btn-sm btn-outline-primary me-2" @click="addDocField">Add</button>
      </span>
    </div>
    <div class="card-body">
      <p v-if="doc_fields.length == 0">Nothing to show yet!</p>
      <div v-else>
        <div class="row fw-bold">
          <div class="col-md-3">S#. Field Name</div>
          <div class="col-md-2">Field Type</div>
          <div class="col-md-2">Optional</div>
          <div class="col">Description</div>
        </div>
        <div class="row mb-2" :class="{'border border-success': !pb.id}" v-for="(pb, i) in doc_fields" :key="pb.id">
          <div class="col-md-3">
            <div class="input-group">
              <span class="fw-bold me-2">{{i+1}}. </span>
              <input class="form-control" type="text" v-model="pb.name" />
            </div>
          </div>
          <div class="col-md-2">
            <select class="form-select" v-model="pb.field_type ">
              <option v-for="x in SD.DocFieldTypes" v-bind:value="x.id" :key="x.id">
                {{ x.value }}
              </option>
            </select>
          </div>
          <div class="col-md-2">
            <div class="form-check form-check-inline">
              <input class="form-check-input" type="checkbox" v-model="pb.optional">
            </div>
          </div>
          <div class="col">
            <input class="form-control" type="text" v-model="pb.description" />
            <button title="Save this item" class="btn btn-sm btn-outline-primary me-2" @click="saveItem(pb)"><i class="bi bi-save" role="button"></i></button>
            <button title="Copy this item as new row" class="btn btn-sm btn-outline-success me-2" @click="copyItem(pb)"><i class="bi bi-clipboard-plus" role="button"></i></button>
            <button title="Delete this item" class="btn btn-sm btn-outline-danger" @click="removeItem(pb)"><i class="bi bi-trash-fill"></i></button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: "DocType",
  components: {},
  data: function () {
    return { doc_type: { doc_fields: []} }
  },
  async created() {
    console.log("Creating DocType");
  },
  methods: {
  },
};
</script>
