<!--
Component for application record view.

@author Balwinder Sodhi
-->
<template>
  <div>
    <span class="fw-semibold me-2" v-if="sno">{{sno}}. </span>
    <span class="badge text-bg-info me-2">{{fmtDate(item.upd_ts)}}</span>
    <span class="badge text-bg-success me-2">
      {{labelFor(SD.LeaveTypes, item.leave_type)}} leave
      ({{labelFor(SD.WfStatuses, item.status)}})
    </span>
    <span class="me-2"> From {{item.start_dt}} to {{item.end_dt}}.</span>
    <span class="me-2" v-if="item.fn_an != 'NA'">({{item.fn_an}})</span>
    <span class="me-2" v-if="item.leaving_stn">Leaving Station.</span>
    <span>
      <b>Contact during leave: </b>
      <span class="me-2" v-if="item.leave_phone">Ph. {{item.leave_phone}}. </span>
      <span class="me-2" v-if="item.leave_addr">
        Address: {{item.leave_addr}}
      </span>
    </span>
    <span class="me-2" v-if="item.applicant_notes"><b>Reason:</b> {{item.applicant_notes}}</span>
    <span class="me-2" v-if="item.reco_notes"><b>Reco. notes:</b> {{item.reco_notes}}</span>
    <span class="me-2" v-if="item.approver_notes"><b>Appr. notes:</b> {{item.approver_notes}}</span>
    <span v-if="item.upd_by||item.ins_by"><b>By user:</b> {{item.upd_by||item.ins_by}}</span>
  </div>
</template>

<script>
export default {
  name: "LeaveApplicationRecord",
  components: {},
  props: { item: Object, sno: Number },
  emits: [],
  data: function () {
    return {};
  },
  async created() {
    console.log("Creating LeaveApplicationRecord");
  },
  methods: {
  },
};
</script>
