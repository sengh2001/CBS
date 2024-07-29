<template>
  <div class="card">
    <div class="card-header">
      <span>Doc Type</span>
      <a class="btn btn-outline-success float-end" href="#/doc_type">Add Another</a>
    </div>
    <div class="card-body">
      <div class="row mb-2">
        <div class="col-md-3">
          <label for="doc_name">Name</label>
          <input type="text" required class="form-control" id="doc_name" v-model="doc_type.name" :disabled="viewOnly" />
        </div>
        <div class="col-md-3">
          <label for="grp">Group Name</label>
          <input type="text" required class="form-control" id="grp" v-model="doc_type.group" :disabled="viewOnly" />
        </div>
        <div class="col">
          <label for="docdesc">Description</label>
          <input type="text" required class="form-control" id="docdesc" v-model="doc_type.description"
            :disabled="viewOnly" />
        </div>
        <div class="col-md-2">
          <span class="float-end mt-4" v-if="!viewOnly">
            <button type="button" class="btn btn-sm btn-outline-primary me-2" @click="saveDocType">Save</button>
            <button type="button" class="btn btn-sm btn-outline-danger" @click="reset">Clear</button>
          </span>
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
      <p v-if="!hasFields">Nothing to show yet!</p>
      <div v-else>
        <div class="row fw-bold">
          <div class="col-md-1">S#.</div>
          <div class="col-md-2">Field Name</div>
          <div class="col-md-2">Field Type</div>
          <div class="col-md-1">Optional</div>
          <div class="col-md-1">Finder</div>
          <div class="col-md-1">Display Seq.</div>
          <div class="col">Label</div>
        </div>
        <div class="row mb-2" :class="{ 'border border-success': !pb.id }" v-for="(pb, i) in doc_type.doc_fields"
          :key="pb.id">
          <div class="col-md-1">
            <span class="fw-bold me-2">{{ i + 1 }}.</span>
          </div>
          <div class="col-md-2">
            <div class="input-group">
              <input class="form-control" type="text" v-model="pb.name" />
            </div>
          </div>
          <div class="col-md-2">
            <select class="form-select" style="width: 100%;" v-model="pb.field_type">
              <option v-for="x in SD.DocFieldTypes" v-bind:value="x.id" :key="x.id">
                {{ x.value }}
              </option>
            </select>

            <div class="col-md-2" v-if="pb.field_type === 'docref'">
              <select class="form-select" style="width: 280px;" v-model="pb.doc_group_type">
                <option v-for="(groupType, index) in groupTypes" :key="index" :value="groupType">
                  {{ groupType.group }} / {{ groupType.name }}
                </option>
              </select>
            </div>
          </div>

          <div class="col-md-1">
            <div class="form-check form-check-inline">
              <input class="form-check-input" type="checkbox" v-model="pb.optional">
            </div>
          </div>
          <div class="col-md-1">
            <div class="form-check form-check-inline">
              <input class="form-check-input" type="checkbox" v-model="pb.finder">
            </div>
          </div>
          <div class="col-md-1">
            <input class="form-control" type="number" min="0" v-model="pb.display_seq" />
          </div>
          <div class="col">
            <div class="input-group">
              <input class="form-control" type="text" v-model="pb.label" />
              <button title="Save this item" class="btn btn-sm btn-outline-primary me-2" @click="saveItem(pb)"><i
                  class="bi bi-save" role="button"></i></button>
              <button title="Copy this item as new row" class="btn btn-sm btn-outline-success me-2"
                @click="copyItem(pb)"><i class="bi bi-clipboard-plus" role="button"></i></button>
              <button title="Delete this item" class="btn btn-sm btn-outline-danger" @click="removeItem(pb)"><i
                  class="bi bi-trash-fill"></i></button>
            </div>
          </div>
        </div>
      </div>
    </div>

  </div>
</template>

<script>
import _ from "lodash";
import axios from "axios";

export default {
  name: "DocType",
  data() {
    return {
      doc_type: { doc_fields: [] },
      selectedGroupType: null,
      groupTypes: []
    };
  },
  async mounted() {
    this.fetchGroupTypes();
    if (this.isEdit) {
      await this.load();
    } else {
      this.reset();
    }
    if (this.$route.query["nr"] == 1) {
      this.setStatusMessage("Saved the doc type!");
      this.$route.query = {};
    }
  },
  computed: {
    isEdit() {
      return this.$route.params.id > 0;
    },
    hasFields() {
      return (
        this.doc_type !== undefined &&
        this.doc_type.doc_fields !== undefined &&
        this.doc_type.doc_fields.length > 0
      );
    },
  },
  methods: {
    async reset() {
      this.doc_type = { doc_fields: [] };
    },
    async load() {
      let uid = this.$route.params.id;
      await this.doGet(`doc_type/${uid}`, (b) => {
        this.doc_type = b;
      });
    },
    isValid() {
      return !_.isEmpty(this.doc_type.name);
    },
    async saveDocType() {
      if (!this.isValid()) {
        this.setStatusMessage("Please supply all required fields!");
        return;
      }
      if (!confirm("Confirm save?")) {
        return;
      }
      await this.doPost("doc_type_save", this.doc_type, (b) => {
        this.doc_type = b;
        this.setStatusMessage("Saved successfully!");
        if (!this.isEdit) {
          this.$router.push({ path: "/doc_type/" + this.doc_type.id, query: { nr: 1 } });
        }
      }, this.setStatusMessage);
    },
    async addDocField() {
      let dt = this.doc_type;
      if (!this.hasFields) dt.doc_fields = [];
      dt.doc_fields.push({ "doc_type_id": dt.id, "doc_group_type": null }); // Ensure doc_type_id and doc_group_type are included
    },
    async saveItem(obj) {
      if (!confirm("Confirm save?")) {
        return;
      }
      await this.doPost("dtf_save", obj, (b) => {
        Object.assign(obj, b);
        this.setStatusMessage("Saved successfully!");
      }, this.setStatusMessage);
    },
    async copyItem(obj) {
      let cp = {};
      Object.assign(cp, obj);
      cp.id = undefined;
      this.doc_type.doc_fields.push(cp);
    },
    async removeItem(obj) {
      if (!confirm("Confirm delete?")) return;
      this.doc_type.doc_fields = this.doc_type.doc_fields.filter((item) => item.id !== obj.id);
      if (obj.id !== undefined) {
        await this.doGet("dtf_delete/" + obj.id, (b) => {
          this.setStatusMessage(b);
        }, this.setStatusMessage);
      }
    },
    async fetchGroupTypes() {
      try {
        const response = await axios.get('get_group_type');
        console.log('Group Types Response:', response.data); // Log the response data
        this.groupTypes = response.data; // Set groupTypes to the response data
      } catch (error) {
        console.error('Error fetching group types:', error);
      }
    },
  }
};
</script>
