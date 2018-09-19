<template>
  <div>
    <div id="query_tab_div">
      <div id="query_tab_headers">
        <h4 class="title is-5" style="margin-bottom: 6px; margin-top: 4px" v-if="sess_active_tab.type == 'object'"
        >{{$store.query._session._tab._child_tab.long_name}}<span>
            <b-tooltip label="Copy object name to Clipboard" position="is-bottom" type="is-light" style="margin-left:7px">
              <a v-clipboard="() => $store.query._session._tab._child_tab.long_name">
                <i class="fa fa-clipboard" style="font-size: 12px; color:green" aria-hidden="true"></i>
              </a>
            </b-tooltip>
            <span id="analysis-buttons" v-if="$store.query._session._tab.child_active_tab == 0">
              <b-tooltip label="Analyze selected fields" position="is-bottom" type="is-light" style="margin-left:7px">
                <a @click="analyze_fields('field_stat', $store.query._session._tab._child_tab.long_name, $store.vars.hot_selection_values, true)">
                  <i class="fa fa-life-ring" style="font-size: 12px; color:black"></i>
                </a>
              </b-tooltip>

              <b-tooltip label="Analyze selected fields (deep)" position="is-bottom" type="is-light" style="margin-left:7px">
                <a @click="analyze_fields('field_stat_deep', $store.query._session._tab._child_tab.long_name, $store.vars.hot_selection_values, true)">
                  <i class="fa fa-life-ring" style="font-size: 12px;color:blue"></i>
                </a>
              </b-tooltip>

              <b-tooltip label="Group selected field (fill count)" position="is-bottom" type="is-light" style="margin-left:7px">
                <a @click="analyze_fields('fill_cnt_group_field', $store.query._session._tab._child_tab.long_name, $store.vars.hot_selection_values, true, {union:false, expr_func_map: {fill_cnt_fields_sql: 'fill_cnt_field'}})">
                  <i class="fa fa-life-ring" style="font-size: 12px;color:blue"></i>
                </a>
              </b-tooltip>

              <b-tooltip label="Group selected field (fill rate)" position="is-bottom" type="is-light" style="margin-left:7px">
                <a @click="analyze_fields('fill_rate_group_field', $store.query._session._tab._child_tab.long_name, $store.vars.hot_selection_values, true, {union:false, expr_func_map: {fill_rate_fields_sql: 'fill_rate_field'}})">
                  <i class="fa fa-life-ring" style="font-size: 12px;color:blue"></i>
                </a>
              </b-tooltip>

              <b-tooltip label="Analyze selected char fields" position="is-bottom" type="is-light" style="margin-left:7px">
                <a @click="analyze_fields('field_chars', $store.query._session._tab._child_tab.long_name, $store.vars.hot_selection_values, true)">
                  <i class="fa fa-life-ring" style="font-size: 12px;color:orange"></i>
                </a>
              </b-tooltip>

              <b-tooltip label="Analyze Field Distro" position="is-bottom" type="is-light" style="margin-left:7px">
                <a @click="analyze_fields('distro_field', $store.query._session._tab._child_tab.long_name, $store.vars.hot_selection_values, true, {union:false})">
                  <i class="fa fa-life-ring" style="font-size: 12px;color:pink"></i>
                </a>
              </b-tooltip>

              <b-tooltip label="Analyze Date Distro" position="is-bottom" type="is-light" style="margin-left:7px">
                <a @click="analyze_fields('distro_field_date', $store.query._session._tab._child_tab.long_name, $store.vars.hot_selection_values, true, {union:false})">
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
                <span class="button is-small"
                      @click="$store.query._session._tab.pinned = !$store.query._session._tab.pinned"
                      :style="{ color: $store.query._session._tab.pinned? 'red' : 'black'}">
                  <b-tooltip label="Pin Tab" position="is-top" type="is-light">
                    <b-icon pack="fa" icon="font-awesome" size="is-small"></b-icon>
                  </b-tooltip>
                </span>

                <span class="button is-small"
                      :class="{'is-info':$store.vars.show_tab_sql}"
                      @click="toggle_tab_sql">
                  <b-tooltip label="Show SQL Tab Editor" position="is-top" type="is-light">
                    SQL
                  </b-tooltip>
                </span>

                <span class="button is-small" title="Refresh Tab Data"
                      @click="execute_sql($store.query._session._tab._child_tab.sql, $store.query._session._tab.id)">
                    <b-icon pack="fa" icon="refresh" size="is-small"></b-icon>
                </span>

                <span class="button is-small">
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
                  <span class="button is-small" @click="$store.query._session._tab._child_tab.filter_text = null">
                    <b-icon pack="fa" icon="remove" size="is-small"></b-icon>
                </span>
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
                  @click="$store.vars.show_tab_modal_email = !$store.vars.show_tab_modal_email">
                  <b-icon pack="fa" icon="envelope" size="is-small"></b-icon>
                </a>
                <a v-if="$store.query._session._tab.loading" title="Kill Current Query and Restart Worker."
                  class="button is-small" @click="kill_query" style="color:red" >
                  Kill
                </a>

              </div>
            </div>
            <div class="level-item" style="font-size: 0.8rem">
              <progress class="progress is-primary" v-if="$store.vars.query_progress_prct != null"
              style="min-width:100px" :value="$store.vars.query_progress_prct" max="100"
              >{{$store.vars.query_progress_prct}}%</progress>
            </div>

          </div>
        </nav>
        <div id="tab-sql">
          <textarea id="tab-sql-textarea" class="textarea codelike" v-if="$store.vars.show_tab_sql"
            v-model="$store.query._session._tab._child_tab.sql" rows="8"
            @keyup.120="execute_sql($store.query._session._tab._child_tab.sql, $store.query._session._tab.id)"
            :style="{'font-size': $store.settings.editor_font_size}"
            title="F9 to Submit"></textarea>
        </div>
      </div>
      <div class="hot_div" :style="{'height': $store.style.query_hot_height, 'width': $store.style.query_hot_width}">
        <HotTable v-if="$store.query._session._tab._child_tab.query != null && $store.query._session._tab._child_tab.query.error==null"></HotTable>
        <textarea readonly class="textarea codelike" v-if="$store.query._session._tab._child_tab.query != null && $store.query._session._tab._child_tab.query.error!=null"
            v-model="$store.query._session._tab._child_tab.query.error"
            style="color:red"
            :style="{'font-size': $store.settings.editor_font_size, 'height': $store.style.query_hot_height, 'width': $store.style.query_hot_width}"
            title="Query Error"></textarea>
      </div>
    </div>
  </div>
</template>

<script>
import { codemirror, CodeMirror } from "vue-codemirror";
import "codemirror/lib/codemirror.css";
require("codemirror/addon/scroll/annotatescrollbar");
require("codemirror/addon/search/matchesonscrollbar");
require("codemirror/addon/search/searchcursor");
require("codemirror/addon/search/match-highlighter");

import HotTable from "./HotTable.vue";
export default {
  components: {
    codemirror: codemirror,
    HotTable: HotTable
  },
  methods: {
    toggle_tab_sql() {
      self = this;
      this.$store.vars.show_tab_sql = !this.$store.vars.show_tab_sql;
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
</style>
