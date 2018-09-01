import classes from './mixin/classes'

export default {
  app: {
    name: 'DbNet',
    active_section: null,
    databases: {},
    resetting: false,
    socket_connected: false
  },
  query: new classes.StoreQuery(),
  style: {
    app_height: '500px',
    menu_height: '400px',
    pane_height: '700px',
    editor_height: '500px',
    sidebar_width: '180px',
  },
  settings: {
    perfMonitoringEnabled: true,
    sidebar_shown: true,
    pane_width: '3',
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
  },
  hotSettings: {
    data: [],
    // colHeaders: headers,
    // columns: columnDefs,
    rowHeaders: true,
    // stretchH: 'all',
    // width: 806,
    // autoWrapRow: false,
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
      },
    },
  },
  vars: {
    objects_ready: false
  },
}
