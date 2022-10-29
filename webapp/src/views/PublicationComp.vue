<!--
Component for publications work item.

@author Balwinder Sodhi
-->
<template>
  <p v-if="items == undefined || items.length==0">
    Nothing to show yet!
  </p>
  <div v-else >
    <div v-for="(aw, i) in items" :key="aw.id">
      <div class="card border-primary mb-3">
        <div class="card-header">
          <span class="float-start">#{{i+1}}</span>
          <span class="float-end">
            <button class="btn btn-sm btn-outline-primary ms-2 me-2" @click="save(aw)"><i class="bi bi-save" role="button"></i></button>
            <button class="btn btn-sm btn-outline-danger" @click="remove(aw)"><i class="bi bi-trash-fill"></i></button>
          </span>
        </div>
        <div class="card-body">
          <div class="row mb-2 g-1">
            <div class="col">
              <label for="work_type">Classification</label>
              <select class="form-select" id="work_type" v-model="aw.credit" :disabled="viewOnly">
                <option v-for="x in RWCredits" v-bind:value="x.id" :key="x.id">
                  {{ x.value }}
                </option>
              </select>
            </div>
            <div class="col-md-5">
              <label for="title">Title</label>
              <input type="text" class="form-control" id="title" v-model="aw.title" :disabled="viewOnly" />
            </div>
            <div class="col-md-4">
              <label for="authors">Authors</label>
              <input type="text" class="form-control" id="authors" v-model="aw.authors" :disabled="viewOnly" />
            </div>
          </div>
          <div class="row mb-2 g-1">
            <div class="col">
              <label for="pub_name">Publication</label>
              <input type="text" class="form-control" id="pub_name" v-model="aw.pub_name" :disabled="viewOnly" />
            </div>
            <div class="col-md-2">
              <label for="pub_status">Pub. Status</label>
              <select class="form-select" id="pub_status" v-model="aw.pub_status" :disabled="viewOnly">
                <option value="A">Accepted</option>
                <option value="P">Published</option>
              </select>
            </div>
            <div class="col-md-2">
              <label for="pub_dt">Pub. Dt.</label>
              <input type="date" class="form-control" id="pub_dt" v-model="aw.pub_dt" :disabled="viewOnly" />
            </div>
            <div class="col-md-2">
              <label for="doi">DOI</label>
              <input type="text" class="form-control" id="doi" v-model="aw.doi" :disabled="viewOnly" />
            </div>
            <div class="col-md-2">
              <label for="status">Status</label>
              <select class="form-select" id="status" v-model="aw.status" :disabled="viewOnly">
                <option v-for="x in SD.WfStatuses" v-bind:value="x.id" :key="x.id">
                  {{ x.value }}
                </option>
              </select>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: "PublicationComp",
  components: {},
  props: { items: Array },
  emits: ["itemDeleted", "itemSaved"],
  data: function () {
    return {
      RWCredits: []
    };
  },
  async created() {
    console.log("Creating PublicationComp");
    const vm = this
    await vm.doGet("get_credits/RES/Y", b => { vm.RWCredits = b },
      vm.setStatusMessage)
  },
  methods: {
    async save(obj) {
      if(confirm("Sure you want to save the item?"))
        this.$emit("itemSaved", obj)
    },
    async remove(obj) {
      if(confirm("Sure you want to delete the item?"))
        this.$emit("itemDeleted", obj)
    }
  },
};
</script>
