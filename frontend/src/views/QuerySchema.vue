<template>
  <div style="font-size:0.9rem">
    <b-field horizontal label="Schema">
      <!-- <b-autocomplete
            @keyup.native.esc="$store.query._session.schema=null"
            v-model="$store.query._session.schema"
            :data="get_schema_list()"
            :open-on-focus="true"
            :keep-first="true"
            :loading="loading"
            placeholder="Schema"
            @select="option => change_schema(option)">
      </b-autocomplete>-->
      <b-input
        expanded
        v-model="$store.query._session.schema_filter"
        @keyup.native.esc="$store.query._session.schema_filter = null"
        placeholder="Filter Schemas..."
        type="search"
      ></b-input>
      <p class="control">
        <b-tooltip label="Add Schema to Favorites" position="is-bottom" type="is-dark">
          <a class="button is-outlined is-info">
            <b-icon pack="fa" icon="heart-o" size="is-small"></b-icon>
          </a>
        </b-tooltip>
      </p>
    </b-field>

    <div class="schema_div">
      <select
        multiple
        v-model="$store.query._session.schema"
        class="schema_select item_select"
        style="font-size: 1.1em; width:100%; height: 150px"
      >
        <option
          v-for="schema in filertered_schemas()"
          @click="change_schema(schema)"
          v-bind:key="schema"
          :value="schema"
        >{{schema}}</option>
      </select>
    </div>
    <!-- <b-field horizontal label="Type">
      <b-select expanded v-model="$store.query._session.schema_obj_type" placeholder="Object type" @input="change_schema()">
        <option value="tables">Table</option>
        <option value="views">View</option>
      </b-select>
    </b-field>-->
    <b-field style="margin-top: 10px">
      <b-select
        expanded
        v-model="$store.query._session.schema_obj_type"
        placeholder="Object type"
        @input="change_schema()"
      >
        <option value="tables">Tables</option>
        <option value="views">Views</option>
      </b-select>
      <b-input
        v-model="$store.query._session.schema_obj_filter"
        @keyup.native.esc="$store.query._session.schema_obj_filter=null"
        placeholder="Filter..."
        type="search"
      ></b-input>
      <p class="control">
        <button
          title="Refresh Schemas / Objects"
          class="button is-warning"
          @click="() => {get_schemas(); change_schema()}"
        >
          <b-icon
            pack="fa"
            :icon="$store.query._session.schema_loading? 'refresh fa-spin' : 'refresh'"
          ></b-icon>
        </button>
      </p>

      <b-dropdown style="z-index: 10000; font-size: 10px">
        <button
          title="Functions"
          id="schema-obj-funcs"
          class="button is-primary is-outlined"
          slot="trigger"
          style="color: blue"
        >
          <b-icon pack="fa" icon="snowflake-o"></b-icon>
        </button>

        <b-dropdown-item
          @click="sess_schema_objects_selected.map(tbl => create_object_tab(`${sess_schema}.${tbl}`))"
        >Open</b-dropdown-item>

        <b-dropdown-item
          @click="get_tables_columns()"
        >Columns</b-dropdown-item>

        <b-dropdown-item
          @click="set_clipboard(sess_schema_objects_selected.map(tbl => `${sess_schema}.${tbl}`).join('\n'))"
        >Copy Name</b-dropdown-item>

        <b-dropdown-item
          @click="set_clipboard(sess_schema_objects_selected.map(tbl => `select * from ${sess_schema}.${tbl}`).join(';\n')+';')"
        >Copy SELECT *</b-dropdown-item>

        <b-dropdown-item
          @click="set_clipboard(sess_schema_objects_selected.map(tbl => `drop table ${sess_schema}.${tbl}`).join(';\n')+';')"
        >Copy DROP TABLE</b-dropdown-item>

        <b-dropdown-item
          @click="execute_sql(sess_schema_objects_selected.map(tbl => `select '${sess_schema}.${tbl}' as table_nm, count(*) as cnt from ${sess_schema}.${tbl}`).join(' union all\n'))"
        >Exec SELECT COUNT(*)</b-dropdown-item>

        <b-dropdown-item
          v-if="is_hive_type"
          @click="execute_sql(sess_schema_objects_selected.map(tbl => `refresh table ${sess_schema}.${tbl}`).join(';\n'))"
        >Exec REFRESH TABLE</b-dropdown-item>

        <b-dropdown-item
          v-if="is_hive_type"
          @click="sess_schema_objects_selected.map(tbl => execute_sql(`describe formatted ${sess_schema}.${tbl}`))"
        >Exec DESCRIBE TABLE</b-dropdown-item>

        <b-dropdown-item
          @click="sess_schema_objects_selected.map(tbl => analyze_fields('field_stat', `${sess_schema}.${tbl}`, [], false))"
        >Analyze Fields</b-dropdown-item>
      </b-dropdown>
    </b-field>
    <div class="schema_div">
      <select
        multiple
        v-model="$store.query._session.schema_objects_selected"
        class="schema_select item_select"
        style="font-size: 1.1em; width:100%"
        :style="{'height': $store.style.schema_object_height}"
      >
        <option
          v-for="object in filertered_tables()"
          @dblclick="create_object_tab(sess_schema_objects_selected.map(o => sess_schema + '.' + o)[0])"
          @contextmenu.prevent="click_id('schema-obj-funcs')"
          v-bind:key="object"
          :value="object"
        >{{object}}</option>
      </select>
    </div>
    <context-menu id="context-menu" ref="ctxMenu">
      <li>option 1</li>
      <li>option 1b</li>
      <li class="disabled">option 2</li>
      <li>option 3</li>
    </context-menu>
  </div>
</template>

<script>
import contextMenu from "vue-context-menu";
export default {
  components: {
    contextMenu: contextMenu
  },
  computed: {},
  methods: {
    click_id(id_str) {
      document.getElementById(id_str).click();
    },
    change_schema(new_schema = null) {
      new_schema = new_schema == null ? this.sess_schema : new_schema;
      if (this.sess_schema_obj_type == "tables") this.get_tables(new_schema);
      else if (this.sess_schema_obj_type == "views") this.get_views(new_schema);
      this.$store.query._session.schema_obj_filter = "";
    },
    filertered_schemas() {
      // filter schema name by comma delimited keyword
      let filter_arr = this.$store.query._session.schema_filter
        ? this.$store.query._session.schema_filter.split(",")
        : [];
      try {
        return this.get_schema_list().filter(name => {
          return this.$store.query._session.schema_filter
            ? filter_arr.some(
                filter =>
                  name
                    .toString()
                    .toLowerCase()
                    .indexOf(filter.toLowerCase()) >= 0
              )
            : name;
        });
      } catch (error) {
        this.log(error);
        return [];
      }
    },
    filertered_tables() {
      // filter schema name by comma delimited keyword
      let filter_arr = this.$store.query._session.schema_obj_filter
        ? this.$store.query._session.schema_obj_filter.split(",")
        : [];
      try {
        return this.get_schema_objects().filter(name => {
          return this.$store.query._session.schema_obj_filter
            ? filter_arr.some(
                filter =>
                  name
                    .toString()
                    .toLowerCase()
                    .indexOf(filter.toLowerCase()) >= 0
              )
            : name;
        });
      } catch (error) {
        this.log(error);
        return [];
      }
    },
    get_tables_columns(){
      let self = this
      let objs = this.sess_schema_objects_selected.map(o => self.sess_schema + '.' + o)
      if(objs.length == 0) return

      let tab_id = this.create_data_tab();
      this.get_object_columns(objs, this.sess_active_child_tab_id, true)
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
.schema_div > div > div > span > select {
  height: 100%;
}

.dropdown-item {
  font-size: 11px;
  // font-weight: bold;
}
</style>
