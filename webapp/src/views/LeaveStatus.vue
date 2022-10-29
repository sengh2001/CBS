<!--
Component for searching leave quota status.

@author Balwinder Sodhi
-->
<template>
  <div class="container-fluid">
    <span class="fs-5">Status of Leaves for {{user.first_name}} {{user.last_name}}</span>
    <span class="ms-2 fs-6 fw-light">
      {{labelFor(SD.UserRoles, user.role)}} Joined on {{user.profile.doj}}
    </span>
    <div class="row fw-bold border-info border-bottom border-2">
      <div class="col-md-2">S#</div>
      <div class="col-md-4">Leave Type</div>
      <div class="col-md-2">Eligible</div>
      <div class="col-md-2">Availed</div>
      <div class="col-md-2">Available</div>
    </div>
    <div class="row row-striped mt-4" v-for="(r, i) in leaves" :key="r.id">
      <div class="col-md-2">
        {{ i + 1 }}
      </div>
      <div class="col-md-4">{{labelFor(SD.LeaveTypes, r[0])}}</div>
      <div class="col-md-2">{{r[1]}}</div>
      <div class="col-md-2">{{r[2]}}</div>
      <div class="col-md-2">{{r[3]}}</div>
    </div>
  </div>
</template>

<script>
export default {
  name: "LeaveStatus",
  components: {
  },
  data: function () {
    return {
      user: {},
      leaves: []
    };
  },
  computed: {
    isEdit() {
      console.log("isEdit() called");
      return this.$route.params.id > 0;
    }
  },
  async mounted() {
    const uid = this.isEdit ? this.$route.params.id : this.currentUser.id
    await this.load(uid)
  },
  methods: {
    async load(user_id) {
      console.log("Loading leaves status for user_id="+user_id)
      let vm = this;
      vm.leaves = [];
      await vm.doGet(
        `leave_status/${user_id}`,
        (b) => {
          vm.leaves = b.data
          vm.user = b.user
        },
        vm.setStatusMessage
      );
    },
    reset() {
      this.user = {}
      this.leaves = []
    },
  },
};
</script>
