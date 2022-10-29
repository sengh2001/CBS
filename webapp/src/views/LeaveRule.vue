<!--
Component for leave rule editing.

@author Balwinder Sodhi
-->
<template>
  <div class="container-fluid">
    <div class="card">
      <div class="card-header">
        <div class="fs-5 float-start">Leave Rules</div>
        <span class="float-end">
          <a class="btn btn-sm btn-success me-2" href="#/rule">Add Another</a>
          <button type="button" class="btn btn-sm btn-primary" @click="makeCopy">Make Copy</button>
        </span>
      </div>
      <div class="card-body">
        <leave-rule-comp :rule="rule" @rule-saved="save" @rule-cleared="clear"/>
      </div>
    </div>
  </div>
</template>

<script>
import _ from "lodash";
import LeaveRuleComp from "./LeaveRuleComp.vue"
export default {
  name: "LeaveRule",
  components: {
    LeaveRuleComp
  },
  data: function () {
    return {
      rule: { },
    };
  },
  computed: {
    isEdit() {
      console.log("isEdit() called");
      return this.$route.params.id > 0;
    }
  },
  async created() {
    console.log("Creating Leave Rule Details");
    let vm = this;
    if (vm.isEdit) {
      await vm.load(vm.$route.params.id);
    } else {
      vm.reset();
    }
    if (vm.$route.query["nr"] == 1) {
      vm.setStatusMessage("Saved the rule details!");
      vm.$route.query={};
    }
    if (vm.$route.query["cid"] > 0) {
      await vm.load(vm.$route.query["cid"]);
      vm.rule.id = undefined
      vm.rule.sub_role = ""
      vm.$route.query={};
    }
  },
  methods: {
    makeCopy() {
      let vm = this;
      vm.$router.push({ path: "/rule", query: { cid: vm.rule.id } });
    },
    async load(rid) {
      let vm = this;
      console.log("Loading rule details. id=" + rid);
      // Fetch data from an API
      await vm.doGet(`rule/${rid}`, (b)=>{vm.rule = b;}, 
        vm.setStatusMessage)
    },
    isValid() {
      return true
      // return !(_.isEmpty(this.rule.email) || _.isEmpty(this.rule.first_name)
      //   || _.isEmpty(this.rule.last_name));
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
      console.log("Saving rule details.");
      await vm.doPost("rule_save", vm.rule, 
        (b) => {
          vm.rule = b;
          vm.setStatusMessage("Saved successfully!");
          if (!vm.isEdit) {
            vm.$router.push({path: "/rule/"+vm.rule.id, query: {nr:1}});
          }
        }, vm.setStatusMessage);
    },
    reset() {
      this.rule = { };
      console.log("Clearing rule details.");
    },
  },
};
</script>
