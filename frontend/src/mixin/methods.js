import classes from './classes'

var LZString = require('lz-string')
var debounce = require('debounce');

function toObject(arr, key = null) {
  var rv = {};
  for (var i = 0; i < arr.length; ++i)
    rv[key == null ? arr[i] : key] = arr[i];
  return rv;
}

var methods = {

  set(key, value) {
    localStorage.setItem(
      key,
      LZString.compress(
        JSON.stringify(value)
      )
    );
  },

  get(key) {
    let val = localStorage.getItem(key)
    val = val ? JSON.parse(
      LZString.decompress(
        localStorage.getItem(key)
      )
    ) : null;
    return val
  },

  debounce: debounce,

  reset() {
    this.$store.app.resetting = true
    localStorage.clear();
    location.reload();
  },

  save_state(path = null) {
    // lodash _.get and _.has
    let store = {
      app: this.$store.app,
      query: this.$store.query,
      settings: this.$store.settings,
      style: this.$store.style,
    }
    this.set('store', store)
  },

  commit() {
    // save to backend
    this.log('NEEDS to SAVE to BACKEND')
  },

  load_state() {
    self = this
    let store = this.get('store')
    if (this._.isEmpty(store)) return
    Object.keys(store).forEach(function (key) {
      self.$store[key] = store[key]
    }, this);
  },

  resize_panes() {
    this.$store.style.app_height = `${window.innerHeight}px`;
    this.$store.style.menu_height = `${window.innerHeight - 97}px`;
    this.$store.style.pane_height = `${window.innerHeight - 30}px`;
    this.$store.style.editor_height = `${window.innerHeight - 165}px`;
    this.$store.style.schema_object_height = `${window.innerHeight - 310}px`;
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

  handle_messages() {
    // TODO: not working when multiple messages arrive.
    self = this
    let handle = function () {
      if (!self._.isEmpty(self.$store.queue.messages) && !self.$store.settings.message.show) {
        let message = self.$store.queue.messages.shift() // take first
        self.$store.settings.message.title = message.title
        self.$store.settings.message.type = message.type
        self.$store.settings.message.text = message.text
        self.$store.settings.message.show = true
      }
    }

    setTimeout(handle, 400);
  },

  notify(data) {
    this.log(data);
    let msg = null
    if ("error" in data) {
      msg = {
        title: `Error for Req #${data.id}`,
        type: 'is-danger',
        text: data.error,
      }
    } else if ("completed" in data) {
      msg = {
        title: `Completed Req #${data.id}`,
        type: 'is-primary',
        text: data.notify || JSON.stringify(data),
      }
    }
    if (msg != null) {
      msg.width = '370px'
      msg.size = 'is-medium'
      this.$store.queue.messages.push(msg)
      this.handle_messages()
    }
  },

  load_dbquery_state(db_name) {
    let data1b = new classes.ReqData({
      store_func: 'get_dbquery_state',
      kwargs: {
        db_name: db_name
      }
    })

    self = this
    this.$socket.emit("store", data1b, function (data3) {
      self.log(data3)
      self.$store.app.active_section = 'Query'
      self.$store.query = new classes.StoreQuery(data3.payload)
    });
  },

  activate_query_db(db_name) {
    this.save_state()

    if (this._.isEmpty(this.$store.query.db_name)) {
      this.load_dbquery_state(db_name)
      return
    }

    let data1a = new classes.ReqData({
      store_func: 'set_dbquery_state',
      kwargs: {
        data: this.$store.query
      }
    })

    self = this
    self.$socket.emit("store", data1a, function (data2) {
      self.log(data2);
      if (data2.completed) {
        self.load_dbquery_state(db_name)
      } else {
        self.notify(data2)
      }
    });
  },

  submit_meta(options) {
    options.kwargs = options.kwargs || {} // default empty

    let data1 = new classes.ReqData({
      req_type: 'submit-sql',
      database: this.$store.query.db_name,
      sql: '',
      options: options
    })

    self = this
    this.$socket.emit("client-request", data1, function (data2) {
      self.log(data2);
    });
  },

  //////////////// META

  get_databases() {
    let data1 = new classes.ReqData({
      req_type: 'get-databases'
    })

    self = this
    this.$store.settings.sidebar_shown = false
    this.$socket.emit("client-request", data1, function (data2) {
      self.log(data2);
    });

  },

  rcv_databases(data) {
    self = this
    Object.keys(data.data).forEach(function (name) {
      self.$store.app.databases[name] = data.data[name];
    }, this);
    this.$store.settings.sidebar_shown = true
  },

  get_schemas() {
    this.submit_meta({
      meta: "get_schemas"
    })
  },

  rcv_schemas(data) {
    this.log('receive_schemas')
    if (data.database == this.curr_database) {
      let schemas = data.rows.map((row) => row[0])
      let schemas_obj = toObject(schemas)

      // remove not present in latest
      for (let schema of this.schemas) {
        delete this.$store.query.meta.schema[schema]
      }

      // add new missing
      for (let schema of schemas) {
        if (!(schema in this.schemas)) {
          this.$store.query.meta.schema[schema] = {
            tables: [],
            tables_obj: {},
            views: [],
          }
        }
      }
      if (this._.isEmpty(this.sess_schema)) {
        this.$store.query.sessions[this.$store.query.session_name].schema = this.schemas[0]
        this.schema_objects
      }
      this.$forceUpdate()
    }
  },
  get_schema_list() {
    // return Object.keys(this.$store.query.meta.schema);
    let filter_word = this.$store.query.sessions[this.$store.query.session_name].schema
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
    return Object.keys(this.$store.app.databases)
  },

  get_schema_objects() {
    return this.$store.query.meta.schema_objects[this.sess_schema_obj_type];
  },

  get_tables(schema) {
    if (this._.isEmpty(schema)) return
    this.submit_meta({
      meta: "get_tables",
      kwargs: {
        schema: schema
      }
    })
  },

  rcv_tables(data) {
    this.log('receive_tables')
    if (data.database == this.curr_database && !this._.isEmpty(data.rows)) {
      let schema = data.rows.map((row) => row[0])[0]
      let tables = data.rows.map((row) => row[1])
      this.$store.query.meta.schema[schema].tables = tables
      if (schema == this.sess_schema)
        this.$store.query.meta.schema_objects.tables = tables
      this.save_state()
    }
  },

  get_views(schema) {
    if (this._.isEmpty(schema)) return
    this.submit_meta({
      meta: "get_views",
      kwargs: {
        schema: schema
      }
    })
  },

  rcv_views(data) {
    this.log('receive_views')
    this.log(data)
    if (data.database == this.curr_database && !this._.isEmpty(data.rows)) {
      let schema = data.rows.map((row) => row[0])[0]
      let views = data.rows.map((row) => row[1])
      this.$store.query.meta.schema[schema].views = views
      if (schema == this.sess_schema)
        this.$store.query.meta.schema_objects.views = views
      this.save_state()
    }
  },


}

export default Object.assign(classes, methods);
