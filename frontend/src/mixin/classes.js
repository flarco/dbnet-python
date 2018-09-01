const nanoid = require('nanoid')

let StoreQuerySession = class {
  constructor(data = {}) {
    this.db_name = data.db_name || null
    this.session_name = data.session_name || null
    this.editor_text = data.editor_text || null
    this.active_tab_name = data.active_tab_name || null
    this.schema = data.schema || null
    this.schema_object = data.schema_object || null
    this.schema_obj_type = data.schema_obj_type || 'tables'
    this.tabs = data.tabs || {}
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

  Tab: class {
    constructor(data = {}) {
      this.name = data.name || ''
      this.long_name = data.long_name || ''
      this.sql = data.sql || ''
      this.status = data.status || ''
      this.rows = data.rows || []
      this.headers = data.headers || []
      this.filter_text = data.filter_text || ''
      this.pid = data.pid || null
      this.query_id = data.query_id || undefined
      this.query_time_start = data.query_time_start || 0
      this.query_time = data.query_time || 0
      this.database = data.database || null
      this.query_records = data.query_records || 0
      this.query_error = data.query_error || ''
      this.is_loading = data.is_loading || false
      this.pinned = data.pinned || false
      this.show_tab_functions = data.show_tab_functions || false
      this.type = data.type || 'data'
      this.id = data.id || null
      this.limit = data.limit || 200
    }
  },

  ReqData: class {
    constructor(data = {}) {
      self = this
      // self.id = new Date().getTime()
      self.id = nanoid(11)
      Object.keys(data).forEach(function (key) {
        self[key] = data[key];
      }, this);
    }
  },
  StoreQuerySession: StoreQuerySession,
  StoreQuery: class {
    constructor(data = {}) {
      self = this
      this.db_name = data.db_name || null
      this.favorite = data.favorite || false
      this.pane_tab_index = data.pane_tab_index || 0
      this.data_tab_index = data.data_tab_index || 0
      this.session_name = data.session_name || 'default'
      this.editor_text = data.editor_text || ''
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
