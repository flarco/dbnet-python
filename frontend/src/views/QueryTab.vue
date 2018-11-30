<template>
  <div>
    <div id="query_tab_div">
      <div id="query_tab_headers">
        <h4 class="title is-5" style="margin-bottom: 6px; margin-top: 4px" v-if="sess_active_tab.type == 'object'"
        >{{sess_active_child_long_name}}<span>
            <b-tooltip label="Copy object name to Clipboard" position="is-bottom" type="is-light" style="margin-left:7px">
              <a v-clipboard="() => sess_active_child_long_name">
                <i class="fa fa-clipboard" style="font-size: 12px; color:green" aria-hidden="true"></i>
              </a>
            </b-tooltip>
            <span id="analysis-buttons" v-if="$store.query._session._tab.child_active_tab == 0">
              <b-tooltip label="Analyze selected fields" position="is-bottom" type="is-light" style="margin-left:7px">
                <a @click="analyze_fields('field_stat', sess_active_child_long_name, hot_selection_values, true)">
                  <i class="fa fa-life-ring" style="font-size: 12px; color:black"></i>
                </a>
              </b-tooltip>

              <b-tooltip label="Analyze selected fields (deep)" position="is-bottom" type="is-light" style="margin-left:7px">
                <a @click="analyze_fields('field_stat_deep', sess_active_child_long_name, hot_selection_values, true)">
                  <i class="fa fa-life-ring" style="font-size: 12px;color:blue"></i>
                </a>
              </b-tooltip>

              <b-tooltip label="Group selected field (fill count)" position="is-bottom" type="is-light" style="margin-left:7px">
                <a @click="analyze_fields('fill_cnt_group_field', sess_active_child_long_name, hot_selection_values, true, {union:false, expr_func_map: {fill_cnt_fields_sql: 'fill_cnt_field'}})">
                  <i class="fa fa-life-ring" style="font-size: 12px;color:blue"></i>
                </a>
              </b-tooltip>

              <b-tooltip label="Group selected field (fill rate)" position="is-bottom" type="is-light" style="margin-left:7px">
                <a @click="analyze_fields('fill_rate_group_field', sess_active_child_long_name, hot_selection_values, true, {union:false, expr_func_map: {fill_rate_fields_sql: 'fill_rate_field'}})">
                  <i class="fa fa-life-ring" style="font-size: 12px;color:blue"></i>
                </a>
              </b-tooltip>

              <b-tooltip label="Analyze selected char fields" position="is-bottom" type="is-light" style="margin-left:7px">
                <a @click="analyze_fields('field_chars', sess_active_child_long_name, hot_selection_values, true)">
                  <i class="fa fa-life-ring" style="font-size: 12px;color:orange"></i>
                </a>
              </b-tooltip>

              <b-tooltip label="Analyze Field Distro" position="is-bottom" type="is-light" style="margin-left:7px">
                <a @click="analyze_fields('distro_field', sess_active_child_long_name, hot_selection_values, true, {union:false})">
                  <i class="fa fa-life-ring" style="font-size: 12px;color:pink"></i>
                </a>
              </b-tooltip>

              <b-tooltip label="Analyze Date Distro" position="is-bottom" type="is-light" style="margin-left:7px">
                <a @click="analyze_fields('distro_field_date', sess_active_child_long_name, hot_selection_values, true, {union:false})">
                  <i class="fa fa-life-ring" style="font-size: 12px;color:red"></i>
                </a>
              </b-tooltip>
            </span>
          </span>
        </h4>

        <!-- Schema Object Pane -->
        <b-tabs expanded type="is-toggle" style="margin-bottom: -25px"
                v-model="$store.query._session._tab.child_active_tab"
                v-if="sess_active_tab != null && sess_active_tab.type == 'object'"
                @input="activate_tab(sess_active_tab_id)">
          <b-tab-item label="Columns"></b-tab-item>
          <b-tab-item label="Data"></b-tab-item>
          <b-tab-item label="Definition"></b-tab-item>
        </b-tabs>

        <!-- Button Tab -->
        <nav id="tab-nav" class="level tab-top" v-if="sess_active_tab != null" style="margin-bottom: 5px;">
          <!-- Left side -->
          <div class="level-left">
            <div class="level-item">
              <div class="buttons has-addons">
                
                <b-dropdown style="z-index: 10000; font-size: 10px" v-if="sess_active_tab.type == 'object' && $store.query._session._tab.child_active_tab == 0">
                  <span class="button is-small" style="color: blue"
                      slot="trigger">
                      <b-tooltip label="Functions" position="is-top" type="is-light">
                        <b-icon pack="fa" icon="snowflake-o" size="is-small"></b-icon>
                      </b-tooltip>
                  </span>

                  <b-dropdown-item @click="analyze_fields('field_stat', sess_active_child_long_name, hot_selection_values, true)">Analyze Field(s)</b-dropdown-item>

                  <b-dropdown-item @click="analyze_fields('test_pk', sess_active_child_long_name, [''], true, { fields_exp: hot_selection_values.join(is_hive_type? ', ' : ' || '), where_clause: '' })">Test PK Field(s)</b-dropdown-item>

                  <b-dropdown-item @click="$store.query._session._tab._child_tab.form_data.jm._show = true">JOIN-MATCH</b-dropdown-item>

                  <b-dropdown-item @click="execute_sql(`select '${sess_active_child_long_name}' as table_nm, count(*) as cnt from ${sess_active_child_long_name}`)">SELECT COUNT(*)</b-dropdown-item>

                  <b-dropdown-item v-if="is_hive_type" @click="execute_sql(`describe formatted ${sess_active_child_long_name}`)">DESCRIBE HIVE TABLE</b-dropdown-item>

                  <b-dropdown-item v-if="is_hive_type" @click="execute_sql(`refresh table ${sess_active_child_long_name}`)">REFRESH TABLE</b-dropdown-item>

                  <b-dropdown-item @click="set_clipboard(`drop table ${sess_active_child_long_name};`)">DROP TABLE</b-dropdown-item>

                </b-dropdown>


                <span class="button is-small"
                      @click="$store.query._session._tab.pinned = !$store.query._session._tab.pinned"
                      :style="{ color: $store.query._session._tab.pinned? 'red' : 'black'}">
                  <b-tooltip label="Pin Tab" position="is-top" type="is-light">
                    <b-icon pack="fa" icon="font-awesome" size="is-small"></b-icon>
                  </b-tooltip>
                </span>

                <span class="button is-small"
                      :class="{'is-info':$store.query._session._tab.show_sql}"
                      @click="toggle_tab_sql">
                  <b-tooltip label="Show SQL Tab Editor" position="is-top" type="is-light">
                    SQL
                  </b-tooltip>
                </span>

                <span class="button is-small" title="Refresh Tab Data"
                      @click="execute_sql($store.query._session._tab._child_tab.query.sql, $store.query._session._tab.id)">
                    <b-icon pack="fa" icon="refresh" size="is-small"></b-icon>
                </span>

                <span class="button is-small" @click="toggle_tab_row_view"
                      :class="{'is-info':$store.vars.show_tab_row_view}">
                  <b-tooltip label="View Row" position="is-top" type="is-light">
                    <b-icon pack="fa" icon="search-plus" size="is-small"></b-icon>
                  </b-tooltip>
                </span>


                <p id="tab-limit" class="button is-small">
                  <select title="Limit" class="select is-small"
                          v-model="$store.query._session._tab._child_tab.limit"
                  >
                    <option selected>200</option>
                    <option>500</option>
                    <option>1000</option>
                    <option>2500</option>
                    <option>5000</option>
                    <option>10000</option>
                  </select>
                </p>

              </div>
            </div>


            <div class="level-item" style="font-size: 0.8rem">

              <span style="font-family: monospace"
                    v-if="$store.query._session._tab._child_tab.loading">Running:
                <strong>{{ $store.vars.query_time }}</strong> sec
              </span>

              <span style="font-family: monospace; min-width:100px" v-else>
                <strong>{{ sess_active_child_tab.query_records }}</strong> rows / <strong>{{ calc_query_time(sess_active_child_tab) }}</strong> sec
              </span>              
            </div>



            <div class="level-item">
              <div class="buttons has-addons">

                <a title="Copy Selected Headers to Clipboard" class="button is-small" style="color: black;"
                  @click="copy_hot_headers">
                  <b-icon pack="fa" icon="header" size="is-small"></b-icon>
                </a>

                <a title="Copy Tab Data to Clipboard (TSV)"
                  class="button is-small" style="color: black;" @click="copy_hot_data">
                  <b-icon pack="fa" icon="files-o" size="is-small"></b-icon>
                </a>

                <a title="Download Tab Data (CSV)" class="button is-small" @click="export_to_csv">
                  <b-icon pack="fa" icon="file-excel-o" size="is-small"></b-icon>
                </a>
                <a title="Email Results (CSV)" class="button is-small"
                  @click="$store.query._session._tab._child_tab.form_data.email._show = true; $store.query._session._tab._child_tab.form_data.email.name = sess_active_child_long_name">
                  <b-icon pack="fa" icon="envelope" size="is-small"></b-icon>
                </a>
                <a v-if="$store.query._session._tab.loading" title="Kill Current Query and Restart Worker."
                  class="button is-small" @click="kill_query(null)" style="color:red" >
                  Kill
                </a>

              </div>
            </div>

            <div class="level-item">
              <div class="field has-addons">
                <p class="control">
                  <input class="input is-small"
                        placeholder="Filter..." type="text"
                        @input="filter_tab_data()"
                        v-model="$store.query._session._tab._child_tab.filter_text"
                        @keyup.27="$store.query._session._tab._child_tab.filter_text = null; filter_tab_data()"
                        size="12">
                </p>
                <p class="control">
                  <span class="button is-small" @click="$store.query._session._tab._child_tab.filter_text = null; filter_tab_data()">
                    <b-icon pack="fa" icon="remove" size="is-small"></b-icon>
                  </span>
                  <span class="button is-small" style="font-size: 0.75rem" v-if="sess_active_child_tab.cache_used">
                    <strong style="color: green">cache</strong>
                  </span>  
                </p>
              </div>
            </div>

            <div class="level-item" style="font-size: 0.8rem" v-if="$store.vars.query_progress_prct != null">
              <progress class="progress is-primary" 
              style="min-width:100px" :value="$store.vars.query_progress_prct" max="100"
              >{{$store.vars.query_progress_prct}}%</progress>
            </div>
            <div class="level-item" style="font-size: 0.8rem" v-if="$store.vars.query_progress_prct != null">
              <a>{{$store.vars.query_progress_prct}}%</a>
            </div>

          </div>
        </nav>
        <div id="tab-sql">

          <!-- Join Match Rate Analysis -->
          <section>
            <b-message style="font-size: 0.8rem" title="Join Match Rate Analysis" :active.sync="$store.query._session._tab._child_tab.form_data.jm._show">
              <b-field grouped>
                  <b-field expanded>
                      <b-input size="is-small" placeholder="Src Fields" v-model="$store.query._session._tab._child_tab.form_data.jm.t1_field"></b-input>
                  </b-field>
                  <b-field expanded>
                      <b-input size="is-small" placeholder="Tgt Table" v-model="$store.query._session._tab._child_tab.form_data.jm.t2"></b-input>
                  </b-field>
                  <b-field expanded>
                      <b-input size="is-small" placeholder="Tgt Fields" v-model="$store.query._session._tab._child_tab.form_data.jm.t2_field"></b-input>
                  </b-field>
                  <p class="control ">
                    <button class="button is-primary is-small" @click="analyze_join_match(sess_active_child_long_name, sess_active_child_tab.form_data.jm.t2, sess_active_child_tab.form_data.jm.t1_field, sess_active_child_tab.form_data.jm.t2_field)">Submit</button>
                  </p>
              </b-field>
            </b-message>
          </section>

          <!-- Email Form -->
          <section>
            <b-message  title="Email CSV Results" :active.sync="$store.query._session._tab._child_tab.form_data.email._show">
              <b-field grouped>
                  <b-field horizontal expanded label="Name:">
                      <b-input expanded size="is-small" placeholder="File Name Alias" v-model="$store.query._session._tab._child_tab.form_data.email.name"></b-input>
                  </b-field>
                  <b-field horizontal expanded label="Email:">
                      <b-input size="is-small" placeholder="To Addresses (;)" v-model="$store.settings.email_address"></b-input>
                  </b-field>
                  <b-field  horizontal label="Limit:">
                      <b-input size="is-small" placeholder="Limit" v-model="$store.query._session._tab._child_tab.form_data.email.limit"></b-input>
                  </b-field>
                  <p class="control">
                    <button class="button is-primary is-small" @click="email_exec_sql($store.query._session._tab._child_tab.query.sql, {email_address: $store.settings.email_address, name:$store.query._session._tab._child_tab.form_data.email.name, limit:$store.query._session._tab._child_tab.form_data.email.limit}, $store.query._session._tab.id)">Submit</button>
                  </p>
              </b-field>
            </b-message>
          </section>

          <!-- <editor v-if="$store.query._session._tab.show_sql"></editor> -->
          <!-- <editor ref="ace_editor" v-model="$store.query._session._tab._child_tab.query.sql"
              @init="editorInit" v-if="$store.query._session._tab.show_sql"
              @keyup.120="execute_sql($store.query._session._tab._child_tab.query.sql, $store.query._session._tab.id)"
              lang="pgsql" theme="chrome" width="100%" height="100"
              title="F9 to Submit"></editor> -->
          <textarea id="tab-sql-textarea" class="textarea codelike" v-if="$store.query._session._tab.show_sql"
            v-model="$store.query._session._tab._child_tab.query.sql" rows="8"
            @keyup.120="execute_sql($store.query._session._tab._child_tab.query.sql, $store.query._session._tab.id)"
            :style="{'font-size': $store.settings.editor_font_size}"
            title="F9 to Submit" autocomplete="off" autocorrect="off" autocapitalize="off" spellcheck="false"></textarea>
        </div>
      </div>
      <div class="columns">
        <div id="row-view-pane" class="column is-4" v-if="$store.vars.show_tab_row_view"
          style="overflow:scroll; font-size: 0.7rem; width: 370px"
          :style="{'height': $store.style.query_hot_height}"
          >
          <div class="level-item">
            <div class="field has-addons">
              <p class="control">
                <input class="input is-small"
                      placeholder="Filter Values..." type="text"
                      @input="render_tab_row_view_data()"
                      v-model="$store.vars.tab_row_view_filter"
                      @keyup.27="$store.vars.tab_row_view_filter = ''; render_tab_row_view_data()"
                      size="19">
              </p>
              <p class="control">
                <span class="button is-small" @click="$store.vars.tab_row_view_filter = ''; render_tab_row_view_data()">
                  <b-icon pack="fa" icon="remove" size="is-small"></b-icon>
              </span>
              </p>

              <a title="Copy Row Data to Clipboard" class="button is-small" style="color: black;"
                @click="copy_tab_row_view_data">
                <b-icon pack="fa" icon="files-o" size="is-small"></b-icon>
              </a>
            </div>
          </div>
          <b-table :data="$store.vars.tab_row_data" :columns="columns" hoverable narrowed :default-sort="null"></b-table>
        </div>
        <div class="column">
          <div class="hot_div" :style="{'height': $store.style.query_hot_height, 'width': $store.style.query_hot_width}">
            <textarea readonly class="textarea codelike" v-if="$store.query._session._tab._child_tab.query != null && $store.query._session._tab._child_tab.query.error!=null"
                v-model="$store.query._session._tab._child_tab.query.error"
                style="color:red"
                :style="{'font-size': $store.settings.editor_font_size, 'height': $store.style.query_hot_height, 'width': $store.style.query_hot_width}"
                title="Query Error" autocomplete="off" autocorrect="off" autocapitalize="off" spellcheck="false"></textarea>
            <HotTable v-else-if="$store.query._session._tab._child_tab.query != null && $store.query._session._tab._child_tab.text_data==''"></HotTable>
            <textarea v-else readonly class="textarea codelike"
                v-model="$store.query._session._tab._child_tab.text_data"
                style="color:blue"
                :style="{'font-size': $store.settings.editor_font_size, 'height': $store.style.query_hot_height, 'width': $store.style.query_hot_width}"
                title="Text Data" autocomplete="off" autocorrect="off" autocapitalize="off" spellcheck="false"></textarea>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import HotTable from "./HotTable.vue";
// import AceEditor from "./AceEditor.vue";
export default {
  data() {
    return {
      columns: [
        {
          field: "n",
          label: "N",
          width: "10"
          // numeric: true
        },
        {
          field: "field",
          label: "Field"
          // width: "40"
        },
        {
          field: "value",
          label: "Value"
          // width: "40"
        }
      ]
    };
  },
  components: {
    // editor: require('vue2-ace-editor'),
    // editor: AceEditor,
    HotTable: HotTable
  },
  methods: {
    editorInit() {
      require("brace/ext/language_tools"); //language extension prerequsite...
      require("brace/mode/html");
      require("brace/mode/javascript"); //language
      require("brace/mode/pgsql"); //language
      require("brace/mode/less");
      require("brace/theme/chrome");
      require("brace/snippets/javascript"); //snippet

      let self = this;
      // Add F9 command
      this.$refs.ace_editor.editor.commands.addCommand({
        name: "Execute SQL",
        exec: function() {
          // self.execute_sql(self.$store.query._session._tab._child_tab.query.sql, self.$store.query._session._tab.id)
          self.get_ace_selection(self.$refs.ace_editor);
        },
        bindKey: { mac: "f9", win: "f9" }
      });
    },
    toggle_tab_row_view() {
      let self = this;
      self.$store.vars.tab_row_data = [];
      this.$store.vars.show_tab_row_view = !this.$store.vars.show_tab_row_view;

      setTimeout(() => {
        self.resize_panes();
      }, 20);
    },
    toggle_tab_sql() {
      let self = this;
      this.$store.query._session._tab.show_sql = !this.$store.query._session
        ._tab.show_sql;
      this.log(this.$refs);
      this.log(this.$store.vars.hot.table.getSelected());

      setTimeout(() => {
        self.resize_panes();

        // handle pressing tab & f4
        // https://stackoverflow.com/a/14166052/2295355
        var textareas = document.getElementsByTagName("textarea");
        var count = textareas.length;
        for (var i = 0; i < count; i++) {
          textareas[i].onkeydown = function(e) {
            if (e.keyCode == 9 || e.which == 9) {
              e.preventDefault();
              var s = this.selectionStart;
              this.value =
                this.value.substring(0, this.selectionStart) +
                "  " +
                this.value.substring(this.selectionEnd);
              this.selectionEnd = s + 2;
            } else if (e.keyCode == 115 || e.which == 115) {
              // get object definition

              if (this.selectionStart == this.selectionEnd) {
                // need to determine the object name automatically
                let done = false;
                let i = this.selectionStart;
                let start,
                  end = this.selectionStart;
                // from cursor to end of name
                while (!done && i <= this.textLength) {
                  i++;
                  let c = this.value.substring(i - 1, i);
                  if (
                    c == " " ||
                    c == "\t" ||
                    c == "\n" ||
                    i == this.textLength
                  ) {
                    end =
                      i == this.textLength && c != " " && c != "\t" && c != "\n"
                        ? i
                        : i - 1;
                    done = true;
                  }
                }
                // from cursor to beginning of name
                i = this.selectionStart;
                done = false;
                while (!done && i > 0) {
                  i--;
                  let c = this.value.substring(i, i + 1);
                  if (c == " " || c == "\t" || c == "\n" || i == 0) {
                    start =
                      i == 0 && c != " " && c != "\t" && c != "\n" ? i : i + 1;
                    done = true;
                  }
                }

                this.selectionStart = start;
                this.selectionEnd = end;
              }

              let object_name = this.value
                .substring(this.selectionStart, this.selectionEnd)
                .trim();

              // self.log(
              //   JSON.stringify({
              //     tabIndex: this.tabIndex,
              //     textLength: this.textLength,
              //     selectionStart: this.selectionStart,
              //     selectionEnd: this.selectionEnd
              //   })
              // );
              // self.log("object_name = " + object_name);
              self.create_object_tab(object_name);
            }
          };
        }
      }, 20);
    },
    update_hot_ref() {
      this.$store.vars.hot = this.$refs.hot;
    }
  },
  mounted() {
    // this.update_hot_ref();
  }
};
</script>

<style lang="scss" scoped>
.dropdown-item {
  font-size: 11px;
  // font-weight: bold;
}
</style>
