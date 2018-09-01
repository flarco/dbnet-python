<template>
  <div>
    <b-tabs type="is-boxed" style="margin-bottom: -20px; margin-top: 0px" v-model="$store.query.data_tab_index">
        <b-tab-item label="T01"></b-tab-item>
        <b-tab-item label="T02"></b-tab-item>
        <b-tab-item label="T03"></b-tab-item>
    </b-tabs>
    <HotTable :settings="settings" ></HotTable>
  </div>
</template>

<script>
import { codemirror, CodeMirror } from "vue-codemirror";
import "codemirror/lib/codemirror.css";
import "handsontable/dist/handsontable.full.css";
require("codemirror/addon/scroll/annotatescrollbar");
require("codemirror/addon/search/matchesonscrollbar");
require("codemirror/addon/search/searchcursor");
require("codemirror/addon/search/match-highlighter");

import HotTable from "@handsontable/vue";

export default {
  name: "Home",
  components: {
    codemirror: codemirror,
    HotTable: HotTable
  },
  computed: {
    main_editor() {
      return this.$refs.main_editor.editor;
    },
    main_editor_cursor() {
      return this.$refs.main_editor.editor.getDoc().getCursor();
    }
  },
  methods: {
    onEditorReady() {
      // this.main_editor_text = this.database.editor_sql;
    },
    onEditorFocus() {
      // localStorage.setItem('sql_text', this.main_editor_text);
    },
    onEditorCodeChange() {
      // localStorage.setItem('sql_text', this.main_editor_text);
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

