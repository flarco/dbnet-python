<template>
  <div style="font-size:0.9rem">
      <b-field horizontal label="Schema">
        <b-autocomplete
          @keyup.native.esc="$store.query.sessions[$store.query.session_name].schema=null"
          v-model="$store.query.sessions[$store.query.session_name].schema"
          :data="get_schema_list()"
          :open-on-focus="true"
          :keep-first="true"
          :loading="loading"
          placeholder="Schema"
          @select="option => change_schema(option)">
        </b-autocomplete>
    </b-field>
      <b-field horizontal label="Type">
        <b-select expanded v-model="$store.query.sessions[$store.query.session_name].schema_obj_type" placeholder="Object type" @input="change_schema()">
          <option value="tables">Table</option>
          <option value="views">View</option>
        </b-select>
    </b-field>
    <b-field>
        <b-input expanded 
        v-model="object_filter"
        @keyup.native.esc="object_filter=null"
        placeholder="Filter..." type="search">
        </b-input>
        <p class="control">
          <button title="Refresh Schemas / Objects"  class="button is-warning" @click="() => {get_schemas(); change_schema()}"><b-icon pack="fa" icon="refresh" ></b-icon></button>
        </p>
    </b-field>
    <div id="schema_div">
      <select multiple v-model="object_selected" class="schema_select" style="font-size: 1.1em; width:100%" :style="{'height': $store.style.schema_object_height}">
        <option v-for="object in filertered_objects()" 
          @dblclick="log(object_selected)"
          v-bind:key="object"
          :value="object"
        >{{object}}</option>
      </select>
    </div>
  </div>
</template>

<script>
export default {
  computed: {},
  methods: {
    change_schema(new_schema = null) {
      new_schema = new_schema == null ? this.sess_schema : new_schema;
      if (this.sess_schema_obj_type == "tables") this.get_tables(new_schema);
      else if (this.sess_schema_obj_type == "views") this.get_views(new_schema);
    },
    filertered_objects() {
      try {
        return this.get_schema_objects().filter(name => {
          return this.object_filter
            ? name
                .toString()
                .toLowerCase()
                .indexOf(this.object_filter.toLowerCase()) >= 0
            : name;
        });
      } catch (error) {
        this.log(error);
        return [];
      }
    }
  },
  data() {
    return {
      loading: false,
      object_filter: null,
      object_selected: [],
      schema_list: []
    };
  },
  mounted() {
    this.get_schemas();
  }
};
</script>

<style lang="scss" scoped>
.schema_field {
  max-width: 50px;
}
#schema_div > div > div > span > select {
  height: 100%;
}
</style>
