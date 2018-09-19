<template>
  <div>
    <!--<span><b-icon pack="fa" icon="times"></b-icon></span>-->
      <!--<b-tabs animated type="is-boxed" style="margin-bottom: -20px; margin-top: 0px"-->
              <!--v-model="$store.query._session.active_tab_index"  @input="delete_tab">-->
          <!--<span><b-icon pack="fa" icon="times"></b-icon></span>-->
          <!--<b-tab-item label="T02"></b-tab-item>-->
          <!--<b-tab-item label="T03"></b-tab-item>-->
          <!--<b-tab-item label="T04"></b-tab-item>-->
          <!--<b-tab-item label="T05"></b-tab-item>-->
      <!--</b-tabs>-->
    <div id="tab-names" class="tabs is-boxed" style="overflow: scroll; margin-bottom: 0px;">
      <ul>
        <li @click="delete_tab">
            <!--<span class="icon is-small"><i class="fas fa-image" aria-hidden="true"></i></span>-->
          <a style="padding-left: 5px; padding-right: 1px"><span><b-icon pack="fa" icon="times" size="is-small"></b-icon></span></a>
        </li>

        <li v-for="(tab, tab_id) in $store.query._session.tabs"
            v-if="tab != null && tab.parent_id == null"
            :class="{'is-active': $store.query._session._tab.id == tab_id}">
            <a @click="activate_tab(tab_id)" @auxclick="delete_tab(tab.id)">

              <span v-if="tab.long_name != 'META' && tab.type=='data'">
                <b-tooltip :label="trim_text(tab._child_tab.sql)" position="is-right" type="is-white" size="is-small">
                  <i class="fa fa-spinner fa-fw" v-if="$store.query._session.tabs[tab_id].loading" style="color:blue"></i>
                  <span style="font-size: 0.8rem">{{tab.long_name}}</span>
                </b-tooltip>
              </span>

              <span v-else-if="tab.long_name != 'META' && tab.type=='object'">
                <i class="fa fa-spinner fa-fw" v-if="$store.query._session.tabs[tab_id].loading" style="color:blue"></i>
                <span style="font-size: 0.8rem">{{tab.long_name}}</span>
              </span>

              <span v-else>
                <i class="fa fa-spinner fa-fw" v-if="$store.query._session.tabs[tab_id].loading"></i>
                <b-icon pack="fa" icon="database" size="is-small"></b-icon>
              </span>
            </a>
        </li>
      </ul>
    </div>
    <query-tab v-if="sess_active_tab_id != null && sess_active_tab.long_name != 'META'" ></query-tab>
    <query-meta v-if="sess_active_tab.long_name == 'META' && $store.vars.db_query_loaded"></query-meta>
  </div>
</template>

<script>
import QueryTab from "./QueryTab.vue";
import QueryMeta from "./QueryMeta.vue";

export default {
  name: "Home",
  components: {
    "query-tab": QueryTab,
    "query-meta": QueryMeta
  },
  computed: {},
  methods: {
    trim_text(text, n = 30) {
      if (text == null) return "";
      return text.substring(0, n) + (text.length > n ? "..." : "");
    }
  },
  data() {
    return {
      settings: {
        data: [
          ["", "Ford", "Volvo", "Toyota", "Honda"],
          ["2016", 10, 11, 12, 13],
          ["2017", 20, 11, 14, 13],
          ["2018", 30, 15, 12, 13]
        ],
        colHeaders: true,
        rowHeaders: true
      }
    };
  },
  mounted() {
    this.activate_tab(null);
  }
};
</script>

<style lang="scss" scoped>
.additional-bar {
  padding: 15px;
}

.gh-btn {
  background-color: #eee;
  background-repeat: no-repeat;
  border: 1px solid #d5d5d5;
  border-radius: 4px;
  color: #333;
  text-decoration: none;
  text-shadow: 0 1px 0 #fff;
  white-space: nowrap;
  cursor: pointer;
}
</style>

