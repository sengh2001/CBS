<!--
@author Balwinder Sodhi
-->
<template>
  <div>
    <label :for="elmId">{{docField.label}}</label>
    <input :id="elmId"
      :class="fieldClass" :type="fieldType" :value="modelValue"
      @input="$emit('update:modelValue', $event.target.value)"
    />
  </div>
</template>

<script>

export default {
  name: "DocFieldComp",
  props: {'modelValue': null, "docField": Object},
  emits: ['update:modelValue'],
  data: function () {
    return { fieldClass: "form-control" };
  },
  async mounted() {
    console.log("Mounting DocFieldComp. Initial value="+
    this.modelValue+". docField="+JSON.stringify(this.docField));
  },
  computed: {
    elmId() {
      const f = this.docField
      return `d_${f.doc_type}_${f.id}_${f.field_type}`
    },
    fieldType() {
      let myType = "text"
      if (this.docField.field_type == "boolean") {
        myType = "checkbox"
        this.fieldClass = "form-check-input ms-2"
      } else if (this.docField.field_type == "integer") {
        myType = "number"
      } else if (this.docField.field_type == "date") {
        myType = "date"
      } else {
        myType = "text"
      }
      return myType
    }
  },
  methods: { },
};
</script>
