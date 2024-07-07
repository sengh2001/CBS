
<template>
  <div>
    <label :for="elmId">{{ docField.label }}</label>
    <input v-if="!isDocref" :id="elmId" :class="fieldClass" :type="fieldType" v-model="value" />
    <select class="form-select" v-else :id="elmId" :class="fieldClass" v-model="value">
      <option v-for="(item, index) in localDocItems" :key="index" :value="item.id">
        {{ formatDropdownLabel(item) }}
      </option>
    </select>
  </div>
</template>

<!--Coming to docrefernce , when the already filled form are selected in the dropdown , the id of the that form present in the docitem table is filled in the docfieldvalue table ,
 whatever the name of the that dropdown field the user has given while creating the form-->

<script>
import axios from 'axios';

export default {
  name: "DocFieldComp",
  props: {
    modelValue: null,
    docField: Object,
    dropdownOptions: Array  // Ensure dropdownOptions is properly defined
  },
  emits: ['update:modelValue'],
  data() {
    return {
      fieldClass: "form-control",
      localDocItems: []  // Array to store fetched docitems
    };
  },
  mounted() {
    this.fetchCurrentUser();
  },
  methods: {
    fetchCurrentUser() {
      axios.get('current_user')
        .then(response => {
          const userEmail = response.data.body.user.email;
          this.fetchDocItemsByUser(userEmail);
        })
        .catch(error => {
          console.error('Error fetching current user:', error);
        });
    },
    fetchDocItemsByUser(userEmail) {
      axios.get(`ebs/docitems_by_user/${userEmail}`)
        .then(response => {
          this.localDocItems = response.data.docitems;
        })
        .catch(error => {
          console.error('Error fetching docitems by user:', error);
        });
    },
    formatDropdownLabel(item) {
    // Example format: status (DRA) / form1 / Thu, 06 Jun 2024 10:46:25 GMT / updated by: (null) / Thu, 06 Jun 2024 10:46:25 GMT / testing forms / Identifier: (xxxxxxxxxxxx)
    let identifierSection = item.fields.find(field => field.field_name === 'Identifier');
    let identifierValue = identifierSection ? `Identifier: (${identifierSection.field_value})` : '';
    
    return `${item.id} / ${item.status} / ${identifierValue} / ${item.ins_ts} / updated by: (${item.upd_by}) / ${item.upd_ts}`;
},

  },
  computed: {
    elmId() {
      const f = this.docField;
      return `d_${f.doc_type}_${f.id}_${f.field_type}`;
    },
    isCheckbox() {
      return this.docField.field_type === "boolean";
    },
    isDocref() {
      return this.docField.field_type === "docref";
    },
    value: {
      get() {
        return this.isCheckbox ? this.modelValue === "on" : this.modelValue;
      },
      set(value) {
        this.$emit('update:modelValue', value);
      }
    },
    fieldType() {
      let myType = "text";
      if (this.isCheckbox) {
        myType = "checkbox";
        this.fieldClass = "form-check-input ms-2";
      } else if (this.docField.field_type === "integer") {
        myType = "number";
      } else if (this.docField.field_type === "date") {
        myType = "date";
      }
      return myType;
    }
  }
};
</script>
