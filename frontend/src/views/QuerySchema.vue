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
        </b-autocomplete> -->

        <b-input expanded
        v-model="schema_filter"
        @keyup.native.esc="schema_filter = null"
        placeholder="Filter Schemas..." type="search">
        </b-input>
        <p class="control">
          <b-tooltip label="Add Schema to Favorites" position="is-bottom" type="is-dark">
            <a class="button is-outlined is-info">
              <b-icon pack="fa" icon="heart-o" size="is-small"></b-icon>
            </a>
        </b-tooltip>
        </p>
    </b-field>

    <div id="schema_div">
      <select multiple v-model="$store.query._session.schema"
              class="schema_select item_select" style="font-size: 1.1em; width:100%; height: 150px">
        <option v-for="schema in filertered_schemas()"
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
    </b-field> -->
    <b-field style="margin-top: 10px">
      <b-select expanded v-model="$store.query._session.schema_obj_type" placeholder="Object type" @input="change_schema()">
        <option value="tables">Tables</option>
        <option value="views">Views</option>
      </b-select>
        <b-input
        v-model="object_filter"
        @keyup.native.esc="object_filter=null"
        placeholder="Filter..." type="search">
        </b-input>
        <p class="control">
          <button title="Refresh Schemas / Objects"  class="button is-warning" @click="() => {get_schemas(); change_schema()}">
            <b-icon pack="fa" :icon="$store.query._session.schema_loading? 'refresh fa-spin' : 'refresh'" ></b-icon></button>
        </p>
    </b-field>
    <div id="schema_div">
      <select multiple v-model="$store.query._session.schema_objects_selected"
              class="schema_select item_select" style="font-size: 1.1em; width:100%" :style="{'height': $store.style.schema_object_height}">
        <option v-for="object in filertered_tables()"
          @dblclick="create_object_tab(sess_schema + '.' + sess_schema_objects_selected[0])"
          v-bind:key="object"
          :value="object"
        >{{object}}</option>
      </select>
    </div>
    <context-menu id="context-menu" ref="ctxMenu">
      <li >option 1</li>
      <li >option 1b</li>
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
    change_schema(new_schema = null) {
      new_schema = new_schema == null ? this.sess_schema : new_schema;
      if (this.sess_schema_obj_type == "tables") this.get_tables(new_schema);
      else if (this.sess_schema_obj_type == "views") this.get_views(new_schema);
    },
    filertered_schemas() {
      try {
        return this.get_schema_list().filter(name => {
          return this.schema_filter
            ? name
                .toString()
                .toLowerCase()
                .indexOf(this.schema_filter.toLowerCase()) >= 0
            : name;
        });
      } catch (error) {
        this.log(error);
        return [];
      }
    },
    filertered_tables() {
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
      schema_list: [],
      schema_filter: null
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
