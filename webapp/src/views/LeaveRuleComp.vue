<!--
Component for leave rules.

@author Balwinder Sodhi
-->
<template>
  <form @submit.prevent="save">
    <div class="row mb-2">
      <div class="col-md-3">
        <label for="sub_role">Employee Role</label>
        <select required class="form-select" id="sub_role" v-model="rule.sub_role" :disabled="viewOnly">
          <option v-for="x in SD.UserRoles" v-bind:value="x.id" :key="x.id">
            {{ x.value }}
          </option>
        </select>
      </div>
      <div class="col-md-3">
        <label for="leave_type">Leave Type</label>
        <select required class="form-select" id="leave_type" v-model="rule.leave_type" :disabled="viewOnly">
          <option v-for="x in SD.LeaveTypes" v-bind:value="x.id" :key="x.id">
            {{ x.value }}
          </option>
        </select>
      </div>
      <div class="col-md-3">
        <label for="yearly">Yearly No.</label>
        <input type="number" step="1" min="0" required class="form-control" id="yearly" v-model="rule.yearly_quota"
          :disabled="viewOnly" />
      </div>
      <div class="col-md-3">
        <label for="max_pi">Max. Per Instance</label>
        <input type="number" step="1" min="0" required class="form-control" id="max_pi"
          v-model="rule.max_per_instance" :disabled="viewOnly" />
      </div>
    </div>
    <div class="row mb-2">
      <div class="col-md-3">
        <label for="max_ac">Max. Accrual</label>
        <input type="number" step="1" min="0" required class="form-control" id="max_ac" v-model="rule.max_accrual"
          :disabled="viewOnly" />
      </div>
      <div class="col-md-3">
        <label for="min_sy">Min. Service Years</label>
        <input type="number" step="1" min="0" required class="form-control" id="min_sy"
          v-model="rule.min_service_years" :disabled="viewOnly" />
      </div>
      <div class="col-md-3">
        <div class="form-check mt-4">
          <input class="form-check-input" type="checkbox" id="cb1" v-model="rule.rolls_over" :disabled="viewOnly" />
          <label class="form-check-label" for="cb1">
            Rolls Over
          </label>
        </div>
      </div>
      <div class="col-md-3">
        <div class="form-check mt-4">
          <input class="form-check-input" type="checkbox" id="cb2" v-model="rule.encashable" :disabled="viewOnly" />
          <label class="form-check-label" for="cb2">
            Encashable
          </label>
        </div>
      </div>
    </div>
    <div class="row mb-2">
      <div class="col-md-3">
        <div class="form-check mt-4">
          <input class="form-check-input" type="checkbox" id="cb3" v-model="rule.fraction_allowed"
            :disabled="viewOnly" />
          <label class="form-check-label" for="cb3">
            Fraction Allowed
          </label>
        </div>
      </div>
      <div class="col-md-3">
        <label for="elconv">Conversion to EL</label>
        <input type="number" required class="form-control" id="elconv" v-model="rule.conversion_to_el"
          :disabled="viewOnly" />
      </div>
      <div class="col-md-3">
        <label for="valid_fr">Valid From</label>
        <input type="date" required class="form-control" id="valid_fr" v-model="rule.valid_from" 
        :disabled="viewOnly" />
      </div>
      <div class="col-md-3">
        <label for="valid_till">Valid Till</label>
        <input type="date" class="form-control" id="valid_till" v-model="rule.valid_till"
        :disabled="viewOnly" />
      </div>
    </div>
    <div class="row mb-2">
      <div class="col-md-4">
        <label for="approle">Approver</label>
        <select id="aprrole" class="form-select" v-model="rule.apr_role" :disabled="viewOnly">
          <option v-for="x in SD.UserRoles" v-bind:value="x.id" :key="x.id">
            {{ x.value }}
          </option>
        </select>
      </div>
      <div class="col-md-4">
        <label for="recrole">Recommender</label>
        <select id="recrole" class="form-select" v-model="rule.rec_role" :disabled="viewOnly" >
          <option v-for="x in SD.UserRoles" v-bind:value="x.id" :key="x.id">
            {{ x.value }}
          </option>
        </select>
      </div>
      <div class="col-md-4">
        <div class="form-check mt-4">
          <input class="form-check-input" type="checkbox" id="matchar" v-model="rule.match_area"
            :disabled="viewOnly" />
          <label class="form-check-label" for="matchar">
            Match area
          </label>
        </div>
      </div>
    </div>
    <div v-if="!viewOnly" class="row">
      <div class="col-md-2">
        <button type="submit" class="btn btn-sm btn-outline-primary" @click="$emit('ruleSaved')">Save</button>
      </div>
      <div class="col-md-2">
        <button type="reset" class="btn btn-sm btn-outline-danger" @click="$emit('ruleCleared')">Clear</button>
      </div>
    </div>
  </form>
</template>

<script>
export default {
  name: "LeaveRuleComp",
  components: {},
  props: { rule: Object },
  emits: ['ruleSaved', 'ruleCleared'],
  data: function () {
    return { }
  },
  async created() {
    console.log("Creating LeaveRuleComp");
  },
  methods: {
  },
};
</script>
