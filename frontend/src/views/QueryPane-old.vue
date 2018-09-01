<template>
  <div>
    <h3 class="title is-4" style="margin-bottom:10px"> {{ $store.query.db_name }}<span>
        <span class="separator"/>

        <b-tooltip label="Help" position="is-bottom" type="is-dark">
          <a>
            <b-icon pack="fa" icon="question-circle" size="is-small"></b-icon>
          </a>
        </b-tooltip>

        <span style="padding-left:10px"></span>
        <b-tooltip :label="$store.query.favorite?'Un-Favorite':'Favorite'" position="is-bottom" type="is-dark">
          <a @click="$store.query.favorite=!$store.query.favorite">
            <b-icon pack="fa" :icon="$store.query.favorite?'star':'star-o'" size="is-small"></b-icon>
          </a>
        </b-tooltip>

        <span style="padding-left:10px"></span>
        <b-tooltip label="Resize Editor" position="is-bottom" type="is-dark">
          <a @click="toggle_editor_size">
            <b-icon pack="fa" icon="columns" size="is-small"></b-icon>
          </a>
        </b-tooltip>

        <span style="padding-left:10px"></span>
        <query-session></query-session>

      </span>
    </h3>
    <b-tabs expanded type="is-toggle" style="margin-bottom: -20px" v-model="$store.query.pane_tab_index">
        <b-tab-item label="Editor"></b-tab-item>
        <b-tab-item label="Schema"></b-tab-item>
        <b-tab-item label="History"></b-tab-item>
    </b-tabs>

    <!-- <div id="editor_div" v-if="isLeftPaneActive('editor')" class="editor_div" style="font-size: 0.9em" @keyup.120="submit_sql" @keyup.115="get_object_data(get_editor_selection())" :style="{'height': settings.heights.editor_div}"> -->
    <div class="editor_div" style="font-size: 0.9em" :style="{'height': $store.style.editor_height}" v-if="$store.query.pane_tab_index == 0">
      <codemirror ref="main_editor" v-model="$store.main_editor.text" :options="$store.main_editor.options"
        @ready="onEditorReady" @focus="onEditorFocus" @change="onEditorCodeChange" :style="{'height': $store.style.editor_height}"></codemirror>
    </div>
    <div v-if="$store.query.pane_tab_index == 1">
      <query-schema></query-schema>
    </div>
    <div v-if="$store.query.pane_tab_index == 2">
      <query-history></query-history>
    </div>
    

  </div>
</template>

<script>
import QuerySchema from "./QuerySchema.vue";
import QuerySession from "./QuerySession.vue";
import QueryHistory from "./QueryHistory.vue";
import { codemirror, CodeMirror } from "vue-codemirror";
import "codemirror/lib/codemirror.css";
require("codemirror/addon/scroll/annotatescrollbar");
require("codemirror/addon/search/matchesonscrollbar");
require("codemirror/addon/search/searchcursor");
require("codemirror/addon/search/match-highlighter");
require("codemirror/mode/sql/sql");

export default {
  components: {
    codemirror: codemirror,
    "query-session": QuerySession,
    "query-schema": QuerySchema,
    "query-history": QueryHistory
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
    },
    toggle_editor_size() {
      if (this.$store.settings.pane_width == "5") {
        this.$store.settings.pane_width = "3";
      } else if (this.$store.settings.pane_width == "4") {
        this.$store.settings.pane_width = "5";
      } else if (this.$store.settings.pane_width == "3") {
        this.$store.settings.pane_width = "4";
      } else {
        this.$store.settings.pane_width = "3";
      }
      // this.$forceUpdate();
    }
  },
  data() {
    return {
      st: "star-o"
    };
  },
  mounted() {}
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

.editor_div {
  border: 1px solid #eee;
  height: 800px;
}
</style>

