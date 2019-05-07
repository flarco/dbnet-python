import classes from './mixin/classes'

export default {
  app: {
    name: 'DbNet',
    active_section: null,
    databases: {},
    resetting: false,
    socket_connected: false,
    meta_level: 'Tables',
  },
  query: new classes.StoreQuery(),
  style: {
    app_height: '500px',
    menu_height: '400px',
    pane_height: '700px',
    editor_height: '500px',
    sidebar_width: '180px',
    menu_connections_height: '280px',
  },
  settings: {
    perfMonitoringEnabled: true,
    sidebar_shown: true,
    show_hot_table: true,
    query_progress_enabled: false,
    pane_width: '3',
    default_query_limit: 200,
    editor_font_size: '0.7rem',
    progress_interval: 1000,
    email_address: '',
    message: {
      show: false,
      width: '370px',
      zindex: '1000', //   Decrease z-index to order put in background.
      size: 'is-small',
      title: 'Default',
      type: 'is-danger',
      text: 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Fusce id fermentum quam. Proin sagittis, nibh id hendrerit imperdiet, elit sapien laoreet elit '
    },
  },
  queue: {
    messages: [],
    rcv_queries: [],
    rcv_query_data: [],
  },
  hotSettings: {
    data: [
      ["2016", 10, 11, 12, 13],
      ["2017", 20, 11, 14, 13],
      ["2018", 30, 15, 12, 13]
    ],
    colHeaders: ["Year", "Ford", "Volvo", "Toyota", "Honda"],
    // columns: columnDefs,
    rowHeaders: true,
    // stretchH: 'all',
    // width: 806,
    // autoWrapRow: false,
    preventOverflow: 'horizontal',
    wordWrap: false,
    // height: 441,
    // maxRows: 50,,
    columnSorting: true,
    sortIndicator: true,
    autoColumnSize: {
      samplingRatio: 23
    },
    search: true,
    contextMenu: false,
    // fixedColumnsLeft: 2,
    manualColumnResize: true,
    modifyColWidth: function (width, col) {
      if (width > 250) {
        return 250
      }
    }
  },
  main_editor: {
    options: {
      // codemirror options
      tabSize: 2,
      lineWrapping: true,
      smartIndent: true,
      matchBrackets: true,
      autofocus: true,
      mode: 'text/x-sql',
      // theme: 'base16-dark',
      lineNumbers: true,
      line: true,
      viewportMargin: Infinity,
      // keyMap: "sublime",
      extraKeys: {
        "Ctrl": "autocomplete",
        // "Ctrl-Enter": function(cm, v1, v2) {console.log(v2)},
        "Tab": function (cm) {
          if (cm.somethingSelected()) {
            var sel = cm.getSelection("\n");
            // Indent only if there are multiple lines selected, or if the selection spans a full line
            if (sel.length > 0 && (sel.indexOf("\n") > -1 || sel.length === cm.getLine(cm.getCursor().line).length)) {
              cm.indentSelection("add");
              return;
            }
          }
          if (cm.options.indentWithTabs)
            cm.execCommand("insertTab");
          else
            cm.execCommand("insertSoftTab");
        },
        "Shift-Tab": function (cm) {
          cm.indentSelection("subtract");
        }
      },
      foldGutter: true,
      gutters: ["CodeMirror-linenumbers", "CodeMirror-foldgutter"],
      styleSelectedText: true,
      highlightSelectionMatches: {
        showToken: /\w/,
        annotateScrollbar: true
      }
    },
  },
  vars: {
    // Temp Variables that are needed for front end session (non-saved)
    objects_ready: false,
    show_tab_sql: false,
    show_tab_row_view: true,
    show_tab_text_view: false,
    show_tab_modal_email: false,
    tabs_active: false,
    query_progress_prct: null,
    query_time_interval: null,
    query_storage_size: null,
    query_history_selected: [],
    mon_interval: null,
    query_time: null,
    loading: false,
    query_editor_selection: null,
    tabs_loading: {},
    app_loading: false,
    db_query_loaded: true,
    show_meta_hot: true,
    hot: null,
    hot_selections: [],
    hot_selection_values: [],
    hot_selection_rows: [],
    hot_selection_rows_full: [],
    tab_row_data: [],
    db_name_filter: null,
    perf_summary: {
      cpu: 0,
      ram: 0,
      threads: 0,
    },
    tab_row_view_filter: '',
    tab_row_hotSettings: {
      data: [
        ["2016", 10, 11, 12, 13],
        ["2017", 20, 11, 14, 13],
        ["2018", 30, 15, 12, 13]
      ],
      colHeaders: ["Year", "Ford", "Volvo", "Toyota", "Honda"],
      // columns: columnDefs,
      rowHeaders: true,
      // stretchH: 'all',
      // width: 806,
      // autoWrapRow: false,
      preventOverflow: 'horizontal',
      wordWrap: true,
      // height: 441,
      // maxRows: 50,,
      columnSorting: true,
      sortIndicator: true,
      autoColumnSize: {
        samplingRatio: 23
      },
      search: true,
      contextMenu: false,
      // fixedColumnsLeft: 2,
      manualColumnResize: true,
      modifyColWidth: function (width, col) {
        if (width > 150) {
          return 150
        }
      }
    },
  },
}