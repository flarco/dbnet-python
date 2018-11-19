/* eslint-disable */
import classes from "./classes";
import Vue from "vue";

var LZString = require("lz-string");
var debounce = require("debounce");

function toObject(arr, key = null) {
  var rv = {};
  for (var i = 0; i < arr.length; ++i) rv[key == null ? arr[i] : key] = arr[i];
  return rv;
}

var methods = {
  test() {
    this.log("test");
  },

  handleKey(e) {
    this.log("keyCode -> " + e.keyCode);
    if ((e.metaKey || e.ctrlKey) && e.keyCode == 72) {
      this.log("bingo");
    }
  },

  set(key, value) {
    localStorage.setItem(key, LZString.compress(JSON.stringify(value)));
  },

  get(key) {
    let val = localStorage.getItem(key);
    val = val ?
      JSON.parse(LZString.decompress(localStorage.getItem(key))) :
      null;
    return val;
  },

  debounce: debounce,

  reset() {
    this.$store.app.resetting = true;
    localStorage.clear();

    let on_resp = data => location.reload();
    let data1 = new classes.ReqData({
      req_type: "reset-db"
    });

    this.submit_req(data1, on_resp);
  },

  save_state(path = null) {
    // lodash _.get and _.has
    let store = {
      app: this.$store.app,
      query: this.$store.query,
      settings: this.$store.settings,
      style: this.$store.style
    };
    this.set("store", store);
  },

  commit() {
    // save to backend
    this.log("NEEDS to SAVE to BACKEND");
  },

  load_state() {
    let self = this;
    let store = this.get("store");
    if (this._.isEmpty(store)) return;
    Object.keys(store).forEach(function (key) {
      self.$store[key] = store[key];
    }, this);
  },

  resize_panes() {
    let side_menu_width =
      document.getElementById("side-menu") == null ?
      0 :
      document.getElementById("side-menu").offsetWidth;
    let side_menu_sections_heigth =
      document.getElementById("menu-sections") == null ?
      0 :
      document.getElementById("menu-sections").scrollHeight;
    let query_pane_width =
      document.getElementById("query-pane") == null ?
      0 :
      document.getElementById("query-pane").offsetWidth;
    let query_tab_headers_height =
      document.getElementById("query_tab_headers") == null ?
      0 :
      document.getElementById("query_tab_headers").scrollHeight;
    let query_tab_names_height =
      document.getElementById("tab-names") == null ?
      0 :
      document.getElementById("tab-names").scrollHeight;
    let query_meta_tab_headers_heigth =
      document.getElementById("query_meta_tab_headers_heigth") == null ?
      0 :
      document.getElementById("query_meta_tab_headers_heigth").scrollHeight;
    let query_row_view_pane = document.getElementById("row-view-pane") ?
      document.getElementById("row-view-pane").offsetWidth :
      0;
    this.$store.style.app_height = `${window.innerHeight}px`;
    this.$store.style.menu_height = `${window.innerHeight - 97}px`;
    this.$store.style.menu_connections_height = `${window.innerHeight -
      190 -
      side_menu_sections_heigth}px`;
    this.$store.style.pane_height = `${window.innerHeight - 30}px`;
    this.$store.style.editor_height = `${window.innerHeight - 165}px`;
    this.$store.style.schema_object_height = `${window.innerHeight - 430}px`;
    this.$store.style.query_hot_height = `${window.innerHeight -
      100 -
      query_tab_names_height -
      query_tab_headers_height}px`;
    this.$store.style.query_meta_hot_height = `${window.innerHeight -
      110 -
      query_tab_names_height -
      query_meta_tab_headers_heigth}px`;
    // this.$store.style.query_hot_width = `${window.innerWidth - 620}px`;
    this.$store.style.query_hot_width = `${window.innerWidth -
      query_pane_width -
      side_menu_width -
      query_row_view_pane -
      20}px`;
    this.$store.style.schema_object_lines = parseInt(
      window.innerHeight / 33,
      10
    );
    this.$forceUpdate();
  },

  sio_message(data1) {
    this.$socket.emit("message", data1, function (data2) {
      // console.log(data2);
    });
  },

  log(text) {
    console.log(text);
  },

  logo(obj_name, obj) {
    this.log(obj_name + " -> " + JSON.stringify(obj));
  },

  handle_messages(timeout = null) {
    // TODO: not working when multiple messages arrive.
    let self = this;
    let handle = function () {
      if (
        !self._.isEmpty(self.$store.queue.messages) &&
        !self.$store.settings.message.show
      ) {
        let message = self.$store.queue.messages.shift(); // take first
        self.$store.settings.message.title = message.title;
        self.$store.settings.message.type = message.type;
        self.$store.settings.message.text = message.text;
        self.$store.settings.message.show = true;
        if (timeout != null)
          setTimeout(
            () => (self.$store.settings.message.show = false),
            timeout
          );
      }
    };

    setTimeout(handle, 400);
  },

  notify(data, timeout = null) {
    this.log(data);
    let msg = null;
    if ("error" in data) {
      msg = {
        title: `Error for Req #${data.id}`,
        type: "is-danger",
        text: data.error
      };
    } else if ("completed" in data) {
      msg = {
        title: `Completed Req #${data.id}`,
        type: "is-primary",
        text: data.notify || JSON.stringify(data)
      };
    }
    if (msg != null) {
      msg.width = "370px";
      msg.size = "is-medium";
      this.$store.queue.messages.push(msg);
      this.handle_messages(timeout);
    }
  },

  save_dbquery_state(on_save = (data, self) => {}) {
    this.sync_session_copy();

    let data1a = new classes.ReqData({
      store_func: "set_dbquery_state",
      kwargs: {
        data: this.$store.query
      }
    });

    let self = this;
    this.$socket.emit("store", data1a, function (data2) {
      self.log(`Session saved @ '${data2.payload.sql_fpath}'`);
      on_save(data2, self);
    });
  },

  load_dbquery_state(db_name, self = null) {
    let data1b = new classes.ReqData({
      store_func: "get_dbquery_state",
      kwargs: {
        db_name: db_name
      }
    });

    self = self == null ? this : self;
    self.$store.vars.db_query_loaded = false;
    this.$socket.emit("store", data1b, function (data3) {
      self.log(data3);
      self.$store.app.active_section = "Query";
      self.$store.query = new classes.StoreQuery(data3.payload);
      self.$store.query.pane_tab_index = 0;
      if (!self._.isEmpty(self.sess_tabs)) self.activate_tab(null);
      self.$store.vars.app_loading = false;
      self.$store.vars.db_query_loaded = true;
      self.resize_panes();

      // Process queue
      let ll = self.$store.queue.rcv_query_data.length; // start length
      for (let ii = 0; ii < ll; ii++) {
        // cycle through all items once
        self.rcv_query_data(self.$store.queue.rcv_query_data.shift()); // process 1st positioned item
      }
    });
  },

  sync_session_copy() {
    let self = this;
    if (
      this.sess_active_tab_id != null &&
      this.$store.query._session._tab != null
    ) {
      if (
        this.sess_active_child_tab != null &&
        this.sess_active_tab.parent_id == null
      ) {
        let keys = ["limit", "filter_text", "query_records"];
        for (let key of keys)
          this.$store.query._session._tab[key] = this.sess_active_child_tab[
            key
          ];
      }

      Object.keys(self.$store.query._session._tab).forEach(function (key) {
        let val = self.$store.query._session._tab[key];
        if (key != "_child_tab") {
          self.$store.query._session.tabs[this.sess_active_tab_id][key] = val;
        } else {
          Object.keys(self.$store.query._session._tab[key]).forEach(function (
              key2
            ) {
              let val2 = self.$store.query._session._tab[key][key2];
              self.$store.query._session.tabs[this.sess_active_tab_id][key][
                key2
              ] = val2;
            },
            this);
        }
      }, this);
    }
    this.$store.query._session.editor_text = this.$store.query.editor_text;
    this.$store.query.sessions[this.sess_name] = this._.cloneDeep(
      this.$store.query._session
    );
  },

  activate_meta_tab() {
    // this loads the tab HOT table. when clicked in QueryData view
    // use this.$store.query.data_tab_index as clicked tab
    // let tab = this.sess_tabs[Object.keys(this.sess_tabs)[this.sess_active_tab_index]]
    // use tab.rows and tab.headers to lot HOT
    // this.$store.query._session.active_tab_id = tab_id
  },

  refresh_tab() {},

  activate_tab(tab_id = null) {
    // this loads the tab HOT table. when clicked in QueryData view
    // use this.$store.query.data_tab_index as clicked tab
    // let tab = this.sess_tabs[Object.keys(this.sess_tabs)[this.sess_active_tab_index]]
    let self = this;
    this.$store.vars.show_tab_row_view = false;
    this.$store.vars.tab_row_view_filter = "";
    this.$store.vars.tabs_active = !this._.isEmpty(this.get_sess_tabs());

    if (tab_id == null && !this._.isEmpty(this.$store.query._session._tab))
      tab_id = this.$store.query._session._tab.id;

    let tab = this.$store.query._session.tabs[tab_id];
    if (this.$store.query._session._tab.id == tab_id) {
      tab = this.$store.query._session._tab;
    } else {
      tab = this.$store.query._session.tabs[tab_id];
      this.$store.query._session._tab = tab;
    }

    if (tab != null && !this._.isEmpty(tab.child_tab_ids)) {
      let child_tab_id = tab.child_tab_ids[tab.child_active_tab];
      tab = this.$store.query._session.tabs[child_tab_id];
      this.$store.query._session._tab._child_tab = tab;
      if (tab.query == null) {
        if (tab.name == "Data")
          this.get_object_data(tab.long_name, child_tab_id);
        if (tab.name == "Properties") this.get_ddl(tab.long_name, child_tab_id);
      }
    } else if (tab == null) {
      tab = {
        id: null
      };
    } else if (tab._child_tab == null) {
      // Work around to have child_tab be the main binded object to front-end tab
      tab._child_tab = this._.cloneDeep(tab);
    }

    // use tab.rows and tab.headers to lot HOT
    this.sync_session_copy();
    this.$store.hotSettings.data =
      tab == null ? [] : this.filter_rows(tab.rows, tab.filter_text);
    this.$store.hotSettings.colHeaders = tab == null ? [] : tab.headers;
    this.$store.hotSettings.columns =
      tab == null ? [] :
      tab.headers.map(val => {
        readOnly: true;
      });
    Vue.set(
      this.$store.hotSettings,
      "afterSelection",
      self.store_last_hot_selection
    );
    Vue.set(this.$store.hotSettings, "afterDocumentKeyDown", self.hot_keydown);
    this.$store.vars.hot_selection_values = [];
    this.$store.vars.hot_selection_rows = [];
    this.$store.vars.query_progress_prct = null;

    // live query time
    if (tab.loading) {
      this.$store.vars.query_time_interval = setInterval(
        this.set_tab_live_progress,
        200
      );
    }

    setTimeout(self.resize_panes, 50);
  },

  filter_rows(rows, filter_text = null) {
    // use $store.query._session._tab.filter_text to filter rows
    if (filter_text == null) return rows;

    return rows.filter(row => {
      let new_row = row.filter(val => {
        if (
          val != null &&
          val
          .toString()
          .toLowerCase()
          .indexOf(filter_text.toLowerCase()) >= 0
        )
          return val;
      });
      if (new_row.length > 0) return row;
    });
  },

  set_clipboard(data) {
    let self = this;
    self.$clipboard(data);

    this.$toast.open({
      message: `Copied to clipboard...`,
      type: "is-success"
    });
  },

  copy_hot_headers() {
    // Ctrl + h: copy headers
    let headers = [];
    let self = this;
    if (self.$store.vars.hot_selection) {
      for (let selection of self.$store.vars.hot_selections) {
        for (let c = selection.c_start; c <= selection.c_end; c++) {
          headers.push(self.$store.hotSettings.colHeaders[c]);
        }
      }
    } else {
      headers = self.$store.hotSettings.colHeaders;
    }
    self.set_clipboard(headers.join("\n"));
  },

  copy_tab_row_view_data() {
    let tsv_rows = [];
    let self = this;
    tsv_rows.push('"' + ["N", "Field", "Value"].join('"\t"') + '"');
    for (let obj of self.$store.vars.tab_row_data) {
      let row = [obj.n, obj.field, obj.value];
      tsv_rows.push('"' + row.join('"\t"') + '"');
    }
    this.set_clipboard(tsv_rows.join("\n"));
  },
  copy_hot_data() {
    let headers = [];
    let tsv_rows = [];

    let self = this;

    // get headers
    if (self.$store.vars.hot_selection) {
      for (
        var c = self.$store.vars.hot_selection.c_start; c <= self.$store.vars.hot_selection.c_end; c++
      ) {
        headers.push(self.$store.hotSettings.colHeaders[c]);
      }
    } else {
      headers = self.$store.hotSettings.colHeaders;
    }

    tsv_rows.push('"' + headers.join('"\t"') + '"');

    // get rows
    if (self.$store.vars.hot_selection) {
      for (
        var r = self.$store.vars.hot_selection.r_start; r <= self.$store.vars.hot_selection.r_end; r++
      ) {
        let row = [];
        for (
          var c = self.$store.vars.hot_selection.c_start; c <= self.$store.vars.hot_selection.c_end; c++
        ) {
          row.push(self.$store.hotSettings.data[r][c]);
        }
        tsv_rows.push('"' + row.join('"\t"') + '"');
      }
    } else {
      self.$store.hotSettings.data.forEach(function (row) {
        tsv_rows.push('"' + row.join('"\t"') + '"');
      }, this);
    }

    self.set_clipboard(tsv_rows.join("\n"));
  },

  hot_keydown(e) {
    let self = this;
    if ((e.metaKey || e.ctrlKey) && e.keyCode == 72) {
      // Ctrl + H: Copy headers + cells
      self.copy_hot_data();
    }
  },

  render_tab_row_view_data() {
    let self = this;
    let cols = [{
        field: "n",
        label: "N"
        // width: "40"
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
    ];
    let i = 0;
    self.$store.vars.tab_row_data = [];
    let filter_text = this.$store.vars.tab_row_view_filter;
    if (self.$store.vars.hot_selection_rows_full.length == 0) return;
    for (let val of self.$store.vars.hot_selection_rows_full[0]) {
      if (
        filter_text == "" ||
        (val &&
          val
          .toString()
          .toLowerCase()
          .indexOf(filter_text.toLowerCase()) >= 0) ||
        self.$store.hotSettings.colHeaders[i]
        .toString()
        .toLowerCase()
        .indexOf(filter_text.toLowerCase()) >= 0
      )
        self.$store.vars.tab_row_data.push({
          n: i + 1,
          field: self.$store.hotSettings.colHeaders[i],
          value: val
        });
      i++;
    }
    self.resize_panes();
  },

  store_last_hot_selection(r_start, c_start, r_end, c_end) {
    let self = this;
    let hot_selection = {
      r_start: r_start,
      c_start: c_start,
      r_end: r_end,
      c_end: c_end
    };
    let selection_array = null;
    try {
      selection_array = this.$store.vars.hot.table.getSelected(); // array of [[startRow, startCol, endRow, endCol],[],..]
    } catch (error) {
      this.log(error);
      return;
    }

    self.$store.vars.hot_selections = [];
    self.$store.vars.hot_selection_values = [];
    self.$store.vars.hot_selection_rows = [];
    self.$store.vars.hot_selection_rows_full = [];

    for (let selection_item of selection_array) {
      let selection = {
        r_start: selection_item[0],
        c_start: selection_item[1],
        r_end: selection_item[2],
        c_end: selection_item[3]
      };

      self.$store.vars.hot_selection = selection;
      self.$store.vars.hot_selections.push(selection)
      for (var r = selection.r_start; r <= selection.r_end; r++) {
        let row = [];
        for (var c = selection.c_start; c <= selection.c_end; c++) {
          row.push(this.$store.hotSettings.data[r][c]);
          self.$store.vars.hot_selection_values.push(
            this.$store.hotSettings.data[r][c]
          );
        }
        self.$store.vars.hot_selection_rows.push(row);
        self.$store.vars.hot_selection_rows_full.push(
          this.$store.hotSettings.data[r]
        );
      }
    }

    this.render_tab_row_view_data();
    // this.log(self.$store.vars.hot_selection_values)
  },

  filter_tab_data() {
    let tab = this.sess_active_tab;
    if (tab != null && !this._.isEmpty(tab.child_tab_ids)) {
      tab = this.sess_active_child_tab;
    }
    this.$store.hotSettings.data =
      tab == null ? [] : this.filter_rows(tab.rows, tab.filter_text);
  },

  filter_tab_row_view_data() {
    let tab = this.sess_active_tab;
    if (tab != null && !this._.isEmpty(tab.child_tab_ids)) {
      tab = this.sess_active_child_tab;
    }
    this.$store.hotSettings.data =
      tab == null ? [] : this.filter_rows(tab.rows, tab.filter_text);
  },

  delete_tab(tab_id = null) {
    let sess_parent_tabs = this.get_sess_tabs();
    if (this._.isEmpty(tab_id) || tab_id instanceof Event)
      tab_id = this.sess_active_tab_id;
    if (tab_id == "META") return;

    let index = Object.keys(sess_parent_tabs).indexOf(tab_id);

    this.$store.hotSettings.data = [];
    this.$store.hotSettings.colHeaders = [];

    if (Object.keys(sess_parent_tabs).length > 1) {
      let new_tab =
        sess_parent_tabs[
          Object.keys(sess_parent_tabs)[index == 0 ? 1 : index - 1]
        ];
      this.$store.query._session._tab = new_tab;
      this.activate_tab(new_tab.id);
    } else {
      this.$store.vars.tabs_active = false;
    }

    // Delete children
    Object.keys(this.sess_tabs[tab_id].child_tab_ids).forEach(function (key) {
      let child_tab_id = this.sess_tabs[tab_id].child_tab_ids[key];
      delete this.$store.query._session.tabs[child_tab_id];
    }, this);

    delete this.$store.query._session.tabs[tab_id];
    if (this.sess_active_tab_id == tab_id)
      delete this.$store.query._session._tab;

    // Seems when we attempt to delete the last key, it doesnt delete it (only deletes the value)
    let tab_keys = Object.keys(this.$store.query._session.tabs);
    if (
      tab_keys.length == 1 &&
      this.$store.query._session.tabs[tab_keys[0]] == null
    ) {
      this.$store.query._session.tabs = {};
    }
    this.sync_session_copy();
  },

  get_ace_selection(ace_editor = null, word = false) {
    if (!ace_editor) ace_editor = this.$store.vars.ace_editor;
    let selection = ace_editor.editor.getCopyText();

    if (selection == "" && word) {
      // need to select cursor word

      let done = false;
      let ace_editor_ = _.cloneDeep(ace_edito);

      let cur_pos = {
        col: ace_editor_.editor.selection.lead.column,
        row: ace_editor_.editor.selection.lead.row
      };
      let value = ace_editor_.editor.selection.doc.$lines[cur_pos.row];
      let textLength = value.length;
      let i = _.cloneDeep(cur_pos).col;

      this.logo("value", value);

      let start, end;

      // from cursor to end of name
      while (!done && i <= textLength) {
        i++;
        let c = value.substring(i - 1, i);
        if (c == " " || c == "\t" || c == "\n" || i == textLength) {
          end =
            i == textLength && c != " " && c != "\t" && c != "\n" && c != ";" ?
            i :
            i - 1;
          done = true;
        }
      }

      // from cursor to beginning of name
      i = _.cloneDeep(cur_pos).col;
      done = false;
      while (!done && i > 0) {
        i--;
        let c = value.substring(i, i + 1);
        if (c == " " || c == "\t" || c == "\n" || i == 0) {
          start =
            i == 0 && c != " " && c != "\t" && c != "\n" && c != ";" ?
            i :
            i + 1;
          done = true;
        }
      }

      let new_cursor = {
        from: {
          row: cur_pos.row,
          col: start
        },
        to: {
          row: cur_pos.row,
          col: end
        }
      };

      ace_editor.editor.selection.setSelectionAnchor(
        new_cursor.from.row,
        new_cursor.from.col
      );
      ace_editor.editor.selection.selectTo(
        new_cursor.to.row,
        new_cursor.to.col
      );
      // selection = ace_editor.editor.getCopyText()
      this.logo("selection", selection);
    }

    return selection;
  },

  get_ace_selection2(ace_editor = null) {
    if (!ace_editor) ace_editor = this.$store.vars.ace_editor;
    let start, end, c1, c2;
    c1 = {
      col: ace_editor.editor.selection.lead.column,
      row: ace_editor.editor.selection.lead.row
    };
    c2 = {
      col: ace_editor.editor.selection.anchor.column,
      row: ace_editor.editor.selection.anchor.row
    };
    if (c1.row < c2.row) {
      start = c1;
      end = c2;
    } else if (c1.row == c2.row && c1.col < c2.col) {
      start = c1;
      end = c2;
    } else {
      start = c2;
      end = c1;
    }

    let lines = ace_editor.editor.selection.doc.$lines;
    let text = "";
    let passed = false;
    for (let r = 0; r < lines.length; r++) {
      const line = lines[r];
      for (let c = 0; c < line.length; c++) {
        const ch = line[c];
        text = text + ch;
        if (r == end.row && c > end.col) passed = true;
        if (passed && ch == ";") break;
        else if (ch == ";") text = "";
      }
      if (r == start.row) {
        for (let c = 0; c < line.length; c++) {
          const ch = line[c];
          if (c >= start.col) text = text + ch;
        }
        if (end.row > start.row) text = text + "\n";
      } else if (r > start.row && r < end.row) {
        for (let c = 0; c < line.length; c++) {
          const ch = line[c];
          text = text + ch;
        }
        text = text + "\n";
      } else if (r == end.row) {
        for (let c = 0; c < line.length; c++) {
          const ch = line[c];
          if (c < end.col) text = text + ch;
        }
      }
    }
    console.log(text);
  },

  get_ace_cursor_query(ace_editor = null) {
    if (!ace_editor) ace_editor = this.$store.vars.ace_editor;
    let selection = this.get_ace_selection(ace_editor);
    if (selection != "") return selection;

    let start, end;

    start = {
      col: 0,
      row: 0
    };

    end = {
      col: ace_editor.editor.selection.lead.column,
      row: ace_editor.editor.selection.lead.row
    };

    let lines = ace_editor.editor.selection.doc.$lines;
    let ch;
    let passed = false;

    for (let r = 0; r < lines.length; r++) {
      const line = lines[r];

      for (let c = 0; c < line.length; c++) {
        if (ch == ";") {
          start.row = r;
          start.col = c;
          selection = "";
        }
        ch = line[c];
        selection = selection + ch;
        if (r == end.row && c + 1 >= end.col) passed = true;

        if (
          (passed && ch == ";") ||
          (r == lines.length - 1 && c == line.length - 1)
        ) {
          end.row = r;
          end.col = c;
          break;
        }
      }
      if ((passed && ch == ";") || r == lines.length - 1) break;
      selection = selection + "\n";
    }

    // this.log(start)
    // this.log(end)

    ace_editor.editor.selection.setSelectionAnchor(start.row, start.col);
    ace_editor.editor.selection.selectTo(end.row, end.col);
    console.log(selection);
  },

  get_editor_selection(cm_editor, word = false) {
    let selection = cm_editor.getSelection();

    if (selection == "" && word) {
      // need to select cursor word
      let cur_pos = cm_editor.getDoc().getCursor();
      this.log("cur_pos=" + JSON.stringify(cur_pos));

      let done = false;
      let value = cm_editor.getLine(cur_pos.line);
      let textLength = value.length;
      let i = cur_pos.ch;

      let start,
        end = cur_pos;

      // from cursor to end of name
      while (!done && i <= textLength) {
        i++;
        let c = value.substring(i - 1, i);
        if (c == " " || c == "\t" || c == "\n" || i == textLength) {
          end =
            i == textLength && c != " " && c != "\t" && c != "\n" && c != ";" ?
            i :
            i - 1;
          done = true;
        }
      }

      // from cursor to beginning of name
      i = cur_pos.ch;
      done = false;
      while (!done && i > 0) {
        i--;
        let c = value.substring(i, i + 1);
        if (c == " " || c == "\t" || c == "\n" || i == 0) {
          start =
            i == 0 && c != " " && c != "\t" && c != "\n" && c != ";" ?
            i :
            i + 1;
          done = true;
        }
      }
      selection = {
        from: {
          line: cur_pos.line,
          ch: start
        },
        to: {
          line: cur_pos.line,
          ch: end
        }
      };

      cm_editor.getDoc().setSelection(selection.from, selection.to);
      selection = cm_editor.getSelection();
    }
    return selection;
  },

  get_cursor_query(cm_editor) {
    // Select the query in between semi colons
    let self = this;
    let selection = self.get_editor_selection(cm_editor);
    if (selection != "") return selection;

    let s_cur = cm_editor.getSearchCursor(";");
    let cur_pos = cm_editor.getDoc().getCursor();

    let start_cur = s_cur.pos.to;
    let end_cur;
    let found = false;

    while (end_cur == undefined && s_cur.findNext()) {
      found = true;
      if (
        s_cur.pos.to.line > cur_pos.line ||
        (s_cur.pos.to.line == cur_pos.line && s_cur.pos.to.ch >= cur_pos.ch)
      ) {
        end_cur = s_cur.pos.to;
      } else {
        start_cur = s_cur.pos.to;
      }
    }
    if (end_cur == undefined) {
      let ll = cm_editor.lastLine();
      end_cur = {
        line: ll,
        ch: cm_editor.getLine(ll).length
      };
    }
    selection = {
      from: start_cur,
      to: end_cur
    };

    cm_editor.getDoc().setSelection(selection.from, selection.to);
    return self.get_editor_selection(cm_editor);
  },

  kill_query(tab_id = null) {
    if (tab_id == null) tab_id = this.sess_active_child_tab_id;
    this.log("kill_query");
    let data1 = new classes.ReqData({
      req_type: "stop-worker",
      database: this.$store.query.db_name,
      worker_name: this.$store.query._session.tabs[tab_id].query.worker_name
    });

    this.submit_req(data1);
    this.set_tab_prop(tab_id, "loading", false, this.sess_name);
    this.set_tab_query_prop(tab_id, "error", "Killed!", this.sess_name);
    if (this.$store.query._session.tabs[tab_id].parent_id != null)
      this.set_tab_prop(
        this.$store.query._session.tabs[tab_id].parent_id,
        "loading",
        false
      );
  },

  email_exec_sql(sql, email_options, tab_id = null) {
    if (tab_id == null) {
      tab_id = this.$store.query._session._tab.id;
    }

    if (!(email_options.name && email_options.email_address && email_options.limit)) {
      this.$snackbar.open({
        duration: 5000,
        message: `Must input all fields (name, to_address, limit).`
      });
      return;
    }

    this.$store.query._session._tab._child_tab.form_data.email._show = false

    this.activate_tab(tab_id);
    let child_tab = this.sess_active_child_tab;
    this.submit_sql(sql, child_tab.id, email_options);
  },

  execute_sql(sql, tab_id = null) {
    // get or create tab
    // use active unpinned tab or get unpinned tabs
    if (
      tab_id == null &&
      !this._.isEmpty(this.$store.query._session._tab) &&
      !this.$store.query._session._tab.pinned &&
      this.$store.query._session._tab.type == "data"
    ) {
      // use active unpinned tab
      tab_id = this.$store.query._session._tab.id;
    } else if (tab_id == null) {
      // get unpinned tabs
      let tabs = this.get_sess_tabs();

      let unpinned_tabs = Object.keys(tabs).filter(tab_id => {
        if (
          tab_id != "META" &&
          !tabs[tab_id].pinned &&
          tabs[tab_id].type == "data"
        )
          return true;
        else return false;
      });
      this.log(JSON.stringify(unpinned_tabs));

      if (unpinned_tabs.length == 0) {
        tab_id = this.create_data_tab();
      } else {
        tab_id = unpinned_tabs.pop();
      }
    }

    this.activate_tab(tab_id);
    let child_tab = this.sess_active_child_tab;
    this.submit_sql(sql, child_tab.id);
  },

  create_data_tab(sql = "") {
    let tab_name = `Q${Object.keys(this.get_sess_tabs())
      .length.toString()
      .padStart(2, "0")}`;

    let query = new classes.SqlQuery({
      database: this.$store.query.db_name,
      sql: sql,
      limit: this.$store.settings.default_query_limit
    });

    let tab = new classes.Tab({
      name: tab_name,
      long_name: tab_name,
      limit: this.$store.settings.default_query_limit,
      child_active_tab: 0,
      type: "data"
    });

    let child_tab = new classes.Tab({
      name: tab_name,
      long_name: tab_name,
      parent_id: tab.id,
      query: query,
      limit: this.$store.settings.default_query_limit,
      type: "data"
    });

    tab.child_tab_ids[0] = child_tab.id;
    this.$store.query._session.tabs[tab.id] = tab;
    this.$store.query._session.tabs[child_tab.id] = child_tab;
    this.$store.query._session._tab = tab;
    this.sync_session_copy();

    this.set_tab_prop(child_tab.id, "sql", sql);
    this.set_tab_prop(child_tab.id, "query", query);

    this.activate_tab(tab.id);
    return tab.id;
  },

  create_object_tab(object_full_name) {
    // let object_full_name = this.sess_schema + '.' + this.sess_schema_objects_selected[0]

    // Create the Tab
    let parent_tab = new classes.Tab({
      name: `S${Object.keys(this.sess_tabs)
        .length.toString()
        .padStart(2, "0")}`,
      long_name: object_full_name.split(".")[1],
      child_active_tab: 0,
      type: "object"
    });

    let child_tab_columns = new classes.Tab({
      name: `Columns`,
      long_name: object_full_name,
      parent_id: parent_tab.id,
      type: "object"
    });

    let child_tab_data = new classes.Tab({
      name: `Data`,
      long_name: object_full_name,
      parent_id: parent_tab.id,
      limit: this.$store.settings.default_query_limit,
      type: "object"
    });

    let child_tab_properties = new classes.Tab({
      name: `Properties`,
      long_name: object_full_name,
      parent_id: parent_tab.id,
      type: "object"
    });

    parent_tab.child_tab_ids[0] = child_tab_columns.id;
    parent_tab.child_tab_ids[1] = child_tab_data.id;
    parent_tab.child_tab_ids[2] = child_tab_properties.id;

    this.$store.query._session.tabs[parent_tab.id] = parent_tab;
    this.$store.query._session.tabs[child_tab_columns.id] = child_tab_columns;
    this.$store.query._session.tabs[child_tab_data.id] = child_tab_data;
    this.$store.query._session.tabs[
      child_tab_properties.id
    ] = child_tab_properties;
    this.$store.query._session._tab = parent_tab;
    this.sync_session_copy();
    this.activate_tab(parent_tab.id);

    this.get_object_columns(object_full_name, child_tab_columns.id);
  },

  activate_query_db(db_name) {
    this.$store.vars.app_loading = true;
    this.save_state();

    if (this._.isEmpty(this.$store.query.db_name)) {
      this.load_dbquery_state(db_name);
      return;
    }

    let self = this;

    let on_save = (data2, self) => {
      if (data2.completed) {
        self.load_dbquery_state(db_name, self);
      } else {
        self.notify(data2);
      }
    };

    this.save_dbquery_state(on_save);
  },

  analyze_fields(
    analysis_name,
    table_name = null,
    fields = [],
    mandatory_fields = false,
    kwargs = {},
    tab_id = null
  ) {
    if (mandatory_fields && this._.isEmpty(fields)) {
      this.$snackbar.open({
        duration: 5000,
        message: `Must select fields to run analysis '${analysis_name}'.`
      });
      return;
    }
    if (tab_id == null) {
      // need to create new tab
      let parent_tab_id = this.create_data_tab(
        `-- Waiting for Template SQL for ${analysis_name}.`
      );
      tab_id = this.$store.query._session.tabs[parent_tab_id]._child_tab.id;
      this.set_tab_prop(tab_id, "loading", true);
    }
    if (table_name == null)
      table_name = this.$store.query._session._tab._child_tab.long_name;

    let data1 = new classes.ReqData({
      tab_id: tab_id,
      req_type: "get-analysis-sql",
      database: this.$store.query.db_name,
      analysis: analysis_name,
      table_name: table_name,
      fields: fields,
      as_sql: true,
      kwargs: kwargs
    });
    this.submit_req(data1);
  },

  analyze_tables(analysis_name, tables = [], tab_id = null) {
    if (this._.isEmpty(tables)) {
      this.$snackbar.open({
        duration: 5000,
        message: `Must select tables to run analysis '${analysis_name}'.`
      });
      return;
    }

    if (tab_id == null) {
      // need to create new tab
      let parent_tab_id = this.create_data_tab(
        `-- Waiting for Template SQL for ${analysis_name}.`
      );
      tab_id = this.$store.query._session.tabs[parent_tab_id]._child_tab.id;
      this.set_tab_prop(tab_id, "loading", true);
    }

    let data1 = new classes.ReqData({
      tab_id: tab_id,
      req_type: "get-analysis-sql",
      database: this.$store.query.db_name,
      analysis: analysis_name,
      tables: tables,
      as_sql: true
    });
    this.submit_req(data1);
  },

  analyze_join_match(t1, t2, t1_field, t2_field, t1_filter = '1=1', t2_filter = '1=1', tab_id = null) {
    if (!(t1 && t2 && t1_field && t2_field)) {
      this.$snackbar.open({
        duration: 5000,
        message: `Must input all fields (t1, t2, t1_field, t2_field).`
      });
      return;
    }

    if (tab_id == null) {
      this.sess_active_child_tab.form_data.jm._show = false
      // need to create new tab
      let parent_tab_id = this.create_data_tab(
        `-- Waiting for Template SQL for 'join-match'`
      );
      tab_id = this.$store.query._session.tabs[parent_tab_id]._child_tab.id;
      this.set_tab_prop(tab_id, "loading", true);
    }

    let data1 = new classes.ReqData({
      tab_id: tab_id,
      req_type: "get-analysis-sql",
      database: this.$store.query.db_name,
      analysis: 'join-match',
      as_sql: true,
      kwargs: {
        t1,
        t2,
        t1_field,
        t2_field,
        t1_filter,
        t2_filter
      }
    });
    this.submit_req(data1);
  },

  // get_object_data(object_full_name, tab_id) {
  get_ddl(object_full_name, tab_id) {
    let query = new classes.SqlQuery({
      database: this.$store.query.db_name,
      limit: 1000,
      options: {
        meta: "get_ddl",
        kwargs: {
          table_name: object_full_name
        }
      }
    });

    let sql_req = new classes.ReqData({
      req_type: "submit-sql",
      database: query.database,
      sql: "",
      limit: query.limit,
      tab_id: tab_id,
      session_name: this.$store.query.session_name,
      options: query.options
    });

    this.$store.vars.query_time_interval = setInterval(
      self.update_query_time,
      200
    );

    this.$store.vars.query_time = setInterval(self.update_query_time, 200);
    this.set_tab_prop(tab_id, "query", query);
    this.set_tab_prop(tab_id, "loading", true);
    this.$store.vars.query_time = 0;
    if (this.$store.query._session.tabs[tab_id].parent_id != null)
      this.set_tab_prop(
        this.$store.query._session.tabs[tab_id].parent_id,
        "loading",
        true
      );
    this.submit_req(sql_req);
  },

  submit_meta(options) {
    options.kwargs = options.kwargs || {}; // default empty

    let data1 = new classes.ReqData({
      req_type: "submit-sql",
      database: this.$store.query.db_name,
      sql: "",
      options: options
    });

    this.submit_req(data1);
  },

  submit_req(data1, on_resp = data => {}) {
    this.$socket.emit("client-request", data1, function (data2) {
      on_resp(data2);
    });
  },

  get_queries(filter = "", limit = null) {
    let sql_req = new classes.ReqData({
      req_type: "get-queries",
      database: this.curr_database,
      filter: filter,
      limit: limit ? limit : 100
    });
    this.submit_req(sql_req);
  },

  rcv_queries(data) {
    this.log("rcv_queries");
    this.log(data);
    this.$store.queue.rcv_queries = data.data;
  },

  submit_sql(sql, tab_id = null, options = {}) {
    if (tab_id == null) {
      // need to create new tab
      tab_id =
        this.sess_active_child_tab_id == null ?
        this.sess_active_tab_id :
        this.sess_active_child_tab_id;
    }

    sql = sql.trim();

    let query = new classes.SqlQuery({
      database: this.$store.query.db_name,
      sql: sql,
      limit: options.limit ? options.limit : this.$store.query._session.tabs[tab_id].limit
    });

    let sql_req = new classes.ReqData({
      req_type: "submit-sql",
      database: query.database,
      sql: query.sql,
      tab_id: tab_id,
      limit: query.limit,
      options: options,
      session_name: this.$store.query.session_name
    });

    this.set_tab_prop(tab_id, "sql", sql_req.sql);
    this.set_tab_prop(tab_id, "query", query);
    this.set_tab_prop(tab_id, "loading", true);
    this.set_tab_prop(tab_id, "cache_used", false);
    this.$store.vars.query_time = 0;
    if (this.$store.query._session.tabs[tab_id].parent_id != null)
      this.set_tab_prop(
        this.$store.query._session.tabs[tab_id].parent_id,
        "loading",
        true
      );

    if (tab_id == this.sess_active_child_tab_id) {
      this.activate_tab(this.sess_active_child_tab.parent_id); // to enable loading timer
    }

    this.submit_req(sql_req);

    if (this.sess_active_child_tab_id == tab_id) {
      this.$store.hotSettings.data = [];
      this.$store.hotSettings.colHeaders = [];
    }
  },

  change_meta_level() {
    this.log(this.$store.app.meta_level);
  },

  export_to_csv() {
    let options = {
      csv: true,
      name: "export"
    };
    this.submit_sql(
      this.$store.query._session._tab._child_tab.sql,
      this.$store.query._session._tab.id,
      options
    );
  },

  //////////////// META

  get_databases() {
    let data1 = new classes.ReqData({
      req_type: "get-databases"
    });

    let self = this;
    this.submit_req(data1);
  },

  rcv_databases(data) {
    let self = this;
    let orig_setting = this.$store.settings.sidebar_shown;
    this.$store.settings.sidebar_shown = this.$store.settings.sidebar_shown ?
      false :
      this.$store.settings.sidebar_shown;
    Object.keys(data.data).forEach(function (name) {
      let favorite =
        self.$store.app.databases[name] == null ?
        false :
        self.$store.app.databases[name].favorite;
      self.$store.app.databases[name] = data.data[name];
      self.$store.app.databases[name].favorite = favorite;
    }, this);
    setTimeout(() => {
      self.$store.settings.sidebar_shown = orig_setting;
    }, 100);
  },

  get_schemas() {
    this.$store.query._session.schema_loading = true;
    this.submit_meta({
      meta: "get_schemas"
    });
  },

  get_object_columns(object_full_name, tab_id) {
    let query = new classes.SqlQuery({
      database: this.$store.query.db_name,
      limit: 1000,
      options: {
        meta: "get_columns",
        kwargs: {
          table_name: object_full_name,
          include_schema_table: false
        }
      }
    });

    let sql_req = new classes.ReqData({
      req_type: "submit-sql",
      database: query.database,
      sql: "",
      limit: query.limit,
      tab_id: tab_id,
      session_name: this.$store.query.session_name,
      options: query.options
    });

    this.$store.vars.query_time_interval = setInterval(
      self.update_query_time,
      200
    );
    this.$store.vars.query_time = setInterval(self.update_query_time, 200);
    this.set_tab_prop(tab_id, "query", query);
    this.set_tab_prop(tab_id, "loading", true);
    this.$store.vars.query_time = 0;
    if (this.$store.query._session.tabs[tab_id].parent_id != null)
      this.set_tab_prop(
        this.$store.query._session.tabs[tab_id].parent_id,
        "loading",
        true
      );
    this.submit_req(sql_req);
  },

  set_tab_prop(tab_id, key, val, sess_name = null) {
    if (sess_name == null) sess_name = this.sess_name;

    if (this.sess_name == sess_name) {
      this.$store.query._session.tabs[tab_id][key] = val;
      if (this.sess_active_tab_id == tab_id)
        this.$store.query._session._tab[key] = val;
      if (this.sess_active_child_tab_id == tab_id)
        this.$store.query._session._tab._child_tab[key] = val;
    }
    this.$store.query.sessions[sess_name].tabs[tab_id][key] = val;
  },

  set_tab_query_prop(tab_id, key, val, sess_name = null) {
    if (sess_name == null) sess_name = this.sess_name;

    if (this.sess_name == sess_name) {
      this.$store.query._session.tabs[tab_id].query[key] = val;
      if (this.sess_active_tab_id == tab_id)
        this.$store.query._session._tab.query[key] = val;
      if (this.sess_active_child_tab_id == tab_id)
        this.$store.query._session._tab._child_tab.query[key] = val;
    }
    this.$store.query.sessions[sess_name].tabs[tab_id].query[key] = val;
  },

  calc_query_time(tab) {
    let lapsed = 0;

    if (tab.query != null) {
      let ts_end =
        tab.query.ts_end == null ? new Date().getTime() : tab.query.ts_end;
      lapsed = ts_end - tab.query.ts_start;
      lapsed = Math.ceil(lapsed / 100) / 10;
      lapsed = lapsed.toFixed(1);
    }

    return lapsed;
  },

  get_mon_perf() {
    let self = this;
    self.$socket.emit("get-perf", {}, function (data2) {
      if (data2.tot_cpu_prct > 100) {
        data2.tot_cpu_prct = `${(data2.tot_cpu_prct / 100.0).toFixed(1)}X`;
      } else {
        data2.tot_cpu_prct = `${data2.tot_cpu_prct}%`;
      }
      self.$store.vars.perf_summary.cpu = data2.tot_cpu_prct;
      self.$store.vars.perf_summary.ram = data2.tot_ram_prct;
    });
  },

  set_tab_live_progress() {
    let self = this;
    let tab = this.sess_active_tab;
    if (tab != null && !this._.isEmpty(tab.child_tab_ids)) {
      tab = this.sess_active_child_tab;
    }

    this.$store.vars.query_time = this.calc_query_time(tab);

    // if database is spark, get progress percent
    if (
      self.$store.settings.query_progress_enabled &&
      self.$store.app.databases[this.curr_database].type.toLowerCase() ==
      "spark"
    ) {
      let last_got = self.$store.app.databases[this.curr_database].last_got;
      if (
        last_got != null &&
        new Date().getTime() - last_got <
        parseInt(self.$store.settings.progress_interval)
      )
        return;
      if (!self.$store.query._session._tab._child_tab.loading) return;
      let url = self.$store.app.databases[this.curr_database].url;
      if (url == null) return;

      let data1 = {
        url: url
      };
      self.$socket.emit("spark-progress", data1, function (data2) {
        self.$store.vars.query_progress_prct = data2["query_progress_prct"];
      });

      self.$store.app.databases[
        this.curr_database
      ].last_got = new Date().getTime();
    }
  },

  get_object_data(object_full_name, tab_id) {
    let query = new classes.SqlQuery({
      database: this.$store.query.db_name,
      sql: "select * from " + object_full_name,
      limit: this.$store.query._session.tabs[tab_id].limit
    });

    let sql_req = new classes.ReqData({
      req_type: "submit-sql",
      database: query.database,
      sql: query.sql,
      tab_id: tab_id,
      limit: query.limit,
      session_name: this.$store.query.session_name
    });

    this.set_tab_prop(tab_id, "sql", sql_req.sql);
    this.set_tab_prop(tab_id, "query", query);
    this.set_tab_prop(tab_id, "loading", true);
    this.$store.vars.query_time = 0;
    if (this.$store.query._session.tabs[tab_id].parent_id != null)
      this.set_tab_prop(
        this.$store.query._session.tabs[tab_id].parent_id,
        "loading",
        true
      );
    this.submit_req(sql_req);
  },

  rcv_schemas(data) {
    this.log("receive_schemas");
    if (data.database == this.curr_database) {
      let schemas = data.rows.map(row => row[0]);
      let schemas_obj = toObject(schemas);

      // remove not present in latest
      for (let schema of this.schemas) {
        delete this.$store.query.meta.schema[schema];
      }

      // add new missing
      for (let schema of schemas) {
        if (!(schema in this.schemas)) {
          this.$store.query.meta.schema[schema] = {
            tables: [],
            tables_obj: {},
            views: []
          };
        }
      }
      if (this._.isEmpty(this.sess_schema)) {
        this.$store.query._session.schema = [this.schemas[0]];
        this.schema_objects;
      }
      this.$store.query._session.schema_loading = false;
      this.$forceUpdate();
    }
  },

  get_sess_tabs() {
    let self = this;
    let sess_tabs = {};
    Object.keys(self.sess_tabs).forEach(function (key) {
      let tab = self.sess_tabs[key];
      if (tab != null && self._.isEmpty(tab.parent_id))
        sess_tabs[key] = self.sess_tabs[key];
    }, this);
    return sess_tabs;
  },

  get_schema_list() {
    return Object.keys(this.$store.query.meta.schema);
    let filter_word = this.$store.query._session.schema;
    return Object.keys(this.$store.query.meta.schema).filter(name => {
      return filter_word ?
        name
        .toString()
        .toLowerCase()
        .indexOf(filter_word.toLowerCase()) >= 0 :
        name;
    });
  },

  get_db_list() {
    this.$forceUpdate();
    return Object.keys(this.$store.app.databases);
  },

  get_schema_objects() {
    return this.$store.query.meta.schema_objects[this.sess_schema_obj_type];
  },

  get_tables(schema) {
    if (this._.isEmpty(schema)) return;
    this.$store.query._session.schema_loading = true;
    this.submit_meta({
      meta: "get_tables",
      kwargs: {
        schema: schema
      }
    });
  },

  get_meta_tables() {
    let req = new classes.ReqData({
      req_type: "get-meta-tables",
      database: this.curr_database,
      session_name: this.sess_name,
      limit: 1000,
      tab_id: "META",
      filter_schema: this.sess_active_tab.filter_schema,
      filter_table: this.sess_active_tab.filter_table
    });
    this.set_tab_prop("META", "loading", true);
    this.submit_req(req);
  },

  get_meta_columns() {
    let req = new classes.ReqData({
      req_type: "get-meta-columns",
      database: this.curr_database,
      session_name: this.sess_name,
      limit: 1000,
      tab_id: "META",
      filter_schema: this.sess_active_tab.filter_schema,
      filter_table: this.sess_active_tab.filter_table,
      filter_column: this.sess_active_tab.filter_column
    });
    this.set_tab_prop("META", "loading", true);
    this.submit_req(req);
  },

  rcv_tables(data) {
    this.log("receive_tables");
    this.$store.query._session.schema_loading = false;
    let schema = data.orig_req.options.kwargs.schema;
    if (data.database == this.curr_database) {
      let tables = data.rows.map(row => row[1]);
      this.$store.query.meta.schema[schema].tables = tables;
      if (schema == this.sess_schema)
        this.$store.query.meta.schema_objects.tables = tables;
      this.save_state();
    }
  },

  get_views(schema) {
    if (this._.isEmpty(schema)) return;
    this.$store.query._session.schema_loading = true;
    this.submit_meta({
      meta: "get_views",
      kwargs: {
        schema: schema
      }
    });
  },

  rcv_views(data) {
    this.log("receive_views");
    this.$store.query._session.schema_loading = false;
    let schema = data.orig_req.options.kwargs.schema;
    if (data.database == this.curr_database) {
      let views = data.rows.map(row => row[1]);
      this.$store.query.meta.schema[schema].views = views;
      if (schema == this.sess_schema)
        this.$store.query.meta.schema_objects.views = views;
      this.save_state();
    }
  },

  rcv_properties(data) {
    // Table propteries, such as DDL, PK, indexes, etc
  },

  rcv_query_data(data) {
    // all other SQL query data
    this.log("rcv_query_data");
    if (
      data.orig_req.database == this.curr_database &&
      data.orig_req.tab_id != null
    ) {
      let tab_id = data.orig_req.tab_id;
      let sess_name = data.orig_req.session_name;

      // TODO: not going to work when viewing another database...

      this.set_tab_prop(tab_id, "query_records", data.rows.length, sess_name);
      this.set_tab_prop(tab_id, "cache_used", data.cache_used, sess_name);
      this.set_tab_prop(tab_id, "rows", data.rows, sess_name);
      this.set_tab_prop(tab_id, "loading", false, sess_name);
      this.set_tab_prop(tab_id, "headers", data.headers, sess_name);
      if (data.options.meta == "get_ddl") {
        let text_data = data.rows.length == 1 ? data.rows[0][0] : "(null)";
        this.set_tab_prop(tab_id, "text_data", text_data, sess_name);
      }

      this.set_tab_query_prop(
        tab_id,
        "ts_end",
        new Date().getTime(),
        sess_name
      );
      this.set_tab_query_prop(tab_id, "error", data.error, sess_name);
      if (this.$store.query._session.tabs[tab_id].parent_id != null)
        this.set_tab_prop(
          this.$store.query._session.tabs[tab_id].parent_id,
          "loading",
          false
        );

      if (this.sess_active_tab_id == data.orig_req.tab_id)
        this.activate_tab(this.sess_active_tab_id);
      if (this.sess_active_child_tab_id == data.orig_req.tab_id)
        this.activate_tab(this.sess_active_tab_id);
      if (
        this.sess_active_child_tab_id == data.orig_req.tab_id &&
        this.$store.vars.query_time_interval != null
      ) {
        clearInterval(this.$store.vars.query_time_interval);
        this.$store.vars.query_progress_prct = null;
      }

      if (
        !data.completed &&
        this.sess_active_child_tab_id != data.orig_req.tab_id
      )
        this.notify(data, 3000);

      if (data.options && data.options.csv && data.options.url) {
        document.getElementById("file-iframe").src = data.options.url;
      }

      this.$forceUpdate();
    } else if (data.orig_req.tab_id != null) {
      // add to queue so that when switched back to database it can be processes
      this.log("queued to $store.queue.rcv_query_data");
      this.$store.queue.rcv_query_data.push(data);
    }
  }
};

export default Object.assign(classes, methods);