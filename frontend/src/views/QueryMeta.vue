<template>
  <div>
    <div id="query_meta_tab_headers_heigth">
      <h4 class="title is-4" style="margin-left: 10px; margin-top: 10px; margin-bottom: 0px"
        >Metadata Browser</h4>

      <section>
          <div class="has-text-centered columns" style="padding-right:10rem; padding-left:10rem; padding-top:10px; padding-bottom:15px; min-width: 200px">

            <div class="column">
              <b-radio v-model="$store.app.meta_level" @input="change_meta_level"
                  type="is-warning"
                  native-value="Tables">
                  Tables / Views
              </b-radio>
            </div>
            <div class="column">
              <b-radio v-model="$store.app.meta_level" @input="change_meta_level"
                  type="is-danger"
                  native-value="Columns">
                  Columns
              </b-radio>
            </div>
            <div class="column">
              <a class="button" @click="get_meta()">Get</a>
            </div>
          </div>
      
      <!--
      For Objects
        schema_name, object_name, object_type, column_cnt, num_rows, last_analyzed_date
      For Columns
        schema_name, object_name, object_type, column_name, data_type,, num_distinct, num_nulls, num_rows, prct_distinct, prct_nulls 
        
      -->
      </section>
      <section style="margin-bottom:10px">
        <b-field position="is-centered"  @keyup.native.esc="clear_meta_fields()" @keyup.native.enter="get_meta()">
            <b-input :placeholder="`Filter Schemas...`" size="is-small" rounded expanded style="max-width:220px" v-model="filter_schema"></b-input>
            <b-input :placeholder="`Filter Table / Views...`" size="is-small" rounded v-if="$store.app.meta_level == 'Tables' || $store.app.meta_level == 'Columns'" expanded style="max-width:220px" v-model="filter_table"></b-input>
            <b-input :placeholder="`Filter Columns...`" size="is-small" rounded v-if="$store.app.meta_level == 'Columns'" expanded style="max-width:220px" v-model="filter_column"></b-input>
        </b-field>
      </section>
    </div>
      <div class="hot_div" :style="{'height': $store.style.query_meta_hot_height, 'width': $store.style.query_hot_width}" v-if="$store.vars.show_meta_hot">
        <HotTable :settings="$store.hotSettings" ></HotTable>
      </div>
  </div>
</template>

<script>
import "handsontable/dist/handsontable.full.css";
import HotTable from "@handsontable/vue";
export default {
  components: {
    HotTable: HotTable
  },
  methods: {
    get_meta() {
      this.$store.query._session._tab.filter_schema = this.filter_schema;
      this.$store.query._session._tab.filter_table = this.filter_table;
      this.$store.query._session._tab.filter_column = this.filter_column;

      if (this.$store.app.meta_level == "Tables") this.get_meta_tables();
      if (this.$store.app.meta_level == "Columns") this.get_meta_columns();
    },
    clear_meta_fields() {
      this.filter_schema = "";
      this.filter_table = "";
      this.filter_column = "";
    },
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
      filter_schema: "",
      filter_table: "",
      filter_column: "",
      radio: "Jack",
      loading: false,
      object_filter: null,
      schema_list: []
    };
  },
  mounted() {
    let self = this;
    this.filter_schema = this.$store.query.sessions[this.sess_name].tabs[
      "META"
    ].filter_schema;
    this.filter_table = this.$store.query.sessions[this.sess_name].tabs[
      "META"
    ].filter_table;
    this.filter_column = this.$store.query.sessions[this.sess_name].tabs[
      "META"
    ].filter_column;
    self.$store.vars.show_meta_hot = false;
    setTimeout(() => {
      self.resize_panes();
      self.$store.vars.show_meta_hot = true;
    }, 100);
  }
};
</script>

<style lang="scss" scoped>
</style>
