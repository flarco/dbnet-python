<template>
  <div style="font-size:0.9rem">
    <b-field horizontal label="Schema">
      <b-autocomplete
          v-model="$store.query.sessions[$store.query.session_name].schema"
          :data="get_schema_list()"
          :open-on-focus="true"
          :loading="loading"
          placeholder="Schema"
          @input="get_async_schema_list"
          @select="option => change_schema(option)">
      </b-autocomplete>
    </b-field>
    <b-field horizontal label="Type">
        <b-select expanded v-model="$store.query.sessions[$store.query.session_name].schema_obj_type" placeholder="Object type" @change="change_schema()">
          <option value="tables">Table</option>
          <option value="views">View</option>
        </b-select>
    </b-field>
    <b-field horizontal label="Name">
      <b-autocomplete
          v-model="$store.query.sessions[$store.query.session_name].schema_object"
          :data="get_schema_object_list()"
          :open-on-focus="true"
          :loading="loading"
          placeholder="Table / View Name"
          @input="get_async_schema_object_list"
          @select="option => log(option)">
      </b-autocomplete>
    </b-field>
  </div>
</template>

<script>
export default {
  computed: {},
  methods: {
    get_schema_list() {
      return Object.keys(this.$store.query.meta.schema);
    },
    get_schema_object_list() {
      return Object.keys(this.$store.query.meta.schema_objects);
    },
    change_schema(new_schema = null) {
      new_schema = new_schema == null ? this.sess_schema : new_schema;
      if (this.sess_schema_obj_type == "tables") this.get_tables(new_schema);
      else if (this.sess_schema_obj_type == "views") this.get_views(new_schema);
    },

    get_async_schema_list() {
      self = this;
      self.loading = true;
      self.schema_list = [];
      for (let key of self.get_schema_list()) {
        self.schema_list.push(key);
      }
      self.loading = false;
      // this.debounce(function() {
      //   self.schema_list = [];
      //   for (let key of self.get_schema_list()) {
      //     self.schema_list.push(key);
      //   }
      //   self.loading = false;
      // }, 500);
    },
    get_async_schema_object_list() {
      this.get_schema_object_list();
    }
  },
  data() {
    return {
      loading: false,
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
