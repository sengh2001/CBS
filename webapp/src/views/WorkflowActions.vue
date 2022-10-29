<template>
    <button disabled class="btn btn-primary" v-if="Object.keys(roleActions).length === 0">Actions</button>
    <div v-else class="btn-group">
        <div class="dropdown">
            <button v-if="showActions" type="button" class="btn btn-primary dropdown-toggle" data-bs-toggle="dropdown"
                aria-expanded="false">
                {{ buttonLabel }}
            </button>
            <ul class="dropdown-menu">
                <li v-for="act in roleActions" :key="act">
                    <a class="dropdown-item" @click.prevent="onAction(act)">{{
                            act.label
                    }}</a>
                </li>
            </ul>
        </div>
    </div>
</template>
<script>
export default {
    name: "WorkflowActions",
    components: {},
    props: {
        showActions: {
            type: Boolean,
            default: true
        },
        buttonLabel: {
            type: String,
            default: "Actions",
        },
        roleActions: {
            type: Object,
            default: { }
        }
    },
    emits: ["actionSelected"],
    data: function () {
        return {};
    },
    async mounted() {
        console.log("Mounting WorkflowActions");
    },
    methods: {
        async onAction(act) {
            this.$emit("actionSelected", act)
        }
    },
};
</script>
