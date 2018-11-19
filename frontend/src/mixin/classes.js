const nanoid = require('nanoid')
// const _ = require('lodash');

let Tab = class {
  constructor(data = {}) {
    let prefix = data.parent_id == null ? 'TAB-' : 'CHILD-'
    this.id = data.id || prefix + nanoid(11)
    this.name = data.name || ''
    this.long_name = data.long_name || 'null'
    this.rows = data.rows || []
    this.text_data = data.text_data || ''
    this.headers = data.headers || []
    this.filter_text = data.filter_text || ''
    this.pid = data.pid || null
    this.query = data.query || null
    this.query_records = data.query_records || 0
    this.loading = data.loading || false
    this.pinned = data.pinned || false
    this.cache_used = data.cache_used || false
    this.show_tab_functions = data.show_tab_functions || false
    this.type = data.type || 'data'
    this.limit = data.limit || 200
    this._child_tab = data._child_tab || {} // Active child tab
    this.child_tab_ids = data.child_tab_ids || {}
    this.child_active_tab = data.child_active_tab || 0
    this.parent_id = data.parent_id || null
    this.form_data = data.form_data || {
      jm: { // join-match
        _show: false
      },
      email: {
        _show: false
      },
    }
  }
}

let StoreQuerySession = class {
  constructor(data = {}) {
    let self = this
    let meta_tab = new Tab({
      id: 'META',
      name: 'META',
      long_name: 'META',
      pinned: true,
      limit: 1000,
      query: {}
    })
    meta_tab.filter_schema = null
    meta_tab.filter_table = null
    meta_tab.filter_column = null

    this.db_name = data.db_name || null
    this.name = data.name || null
    this.editor_text = data.editor_text || null
    this.active_tab_index = data.active_tab_index || 0
    this.active_tab_id = data.active_tab_id || null
    this.schema = data.schema || []
    this.schema_loading = data.schema_loading || false
    this.schema_object = data.schema_object || []
    this.schema_filter = data.schema_filter || ''
    this.schema_obj_filter = data.schema_obj_filter || ''
    this.schema_obj_type = data.schema_obj_type || 'tables'
    this.schema_objects_selected = data.schema_objects_selected || []
    // this.tabs = data.tabs || {'META': new Tab({id: 'META', name:'META', type:'meta'}), 22:{name:'S04'}, 33:{name:'T04'}}
    this._tab = new Tab(data._tab || meta_tab)

    // All Tables
    if (data.tabs != null) {
      Object.keys(data.tabs).forEach(function (tab_id) {
        let tab = data.tabs[tab_id];
        self.tabs[tab_id] = new Tab(tab)
      }, this);
    } else {
      this.tabs = data.tabs || {
        'META': meta_tab
      }
    }
  }
}

let SqlQuery = class {
  constructor(data = {}) {
    let self = this
    self.id = 'QUERY-' + nanoid(11)
    self.ts_start = new Date().getTime()
    self.ts_end = null
    self.database = data.database
    self.sql = data.sql || ''
    self.limit = data.limit || 200
    self.error = data.error || null
    self.worker_name = data.worker_name || null
    self.options = data.options || {}
    self.tab_id = data.tab_id
  }
}

export default {
  Session: class {
    constructor(db_name, session_name, editor_text, active_tab_name, tabs) {
      this.db_name = db_name;
      this.session_name = session_name;
      this.editor_text = editor_text;
      this.active_tab_name = active_tab_name;
      this.tabs = tabs;
    }
  },

  Tab: Tab,

  ReqData: class {
    constructor(data = {}) {
      let self = this
      self.ts_start = new Date().getTime()
      // self.id = 'REQ-' + nanoid(11)
      self.id = `${self.ts_start}.${nanoid(3)}`
      Object.keys(data).forEach(function (key) {
        self[key] = data[key];
      }, this);
    }
  },
  SqlQuery: SqlQuery,
  StoreQuerySession: StoreQuerySession,
  StoreQuery: class {
    constructor(data = {}) {
      let self = this
      this.db_name = data.db_name || null
      this.favorite = data.favorite || false
      this.pane_tab_index = data.pane_tab_index || 0
      this.session_name = data.session_name || 'default'
      this.editor_text = data.editor_text || ''
      self._session = new StoreQuerySession(data._session || {
        name: 'default'
      }) // Active session

      self.sessions = {
        'default': new StoreQuerySession()
      }

      if (data.sessions != null) {
        Object.keys(data.sessions).forEach(function (name) {
          let session = data.sessions[name];
          self.sessions[name] = new StoreQuerySession(session)
        }, this);
      }

      this.meta = data.meta || {
        schema: {},
        schema_objects: {
          tables: [],
          views: [],
        },
      }
    }
  }
}