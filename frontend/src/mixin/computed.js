export default {
  curr_database() {
    return this.$store.query.db_name;
  },
  sess_name() {
    return this.$store.query._session.name
  },
  sess_schema() {
    if (this.$store.query._session.schema.length == 0) return null
    else if (this.$store.query._session.schema.length == 1) return this.$store.query._session.schema[0]
    else return this.$store.query._session.schema;
  },
  sess_schema_obj_type() {
    return this.$store.query._session.schema_obj_type;
  },
  sess_schema_objects_selected() {
    return this.$store.query._session.schema_objects_selected;
  },
  sess_active_tab_index() {
    return this.$store.query._session.active_tab_index
  },
  sess_active_tab_id() {
    return this.sess_active_tab != null ? this.$store.query._session._tab.id : null
  },
  sess_active_tab() {
    return this.$store.query._session._tab
  },
  sess_active_child_tab_id() {
    return this.sess_active_child_tab != null ? this.sess_active_child_tab.id : null
  },
  sess_active_child_tab() {
    return this.$store.query._session._tab._child_tab
  },
  sess_tabs() {
    return this.$store.query._session.tabs
  },
  schemas() {
    return Object.keys(this.$store.query.meta.schema);
  },
  tables() {
    return this.$store.query.meta.schema[this.sess_schema].tables;
  },
  views() {
    return this.$store.query.meta.schema[this.sess_schema].views;
  },
  schema_objects() {
    return this.$store.query.meta.schema_objects[this.sess_schema_obj_type];
  },
  db_names() {
    return Object.keys(this.$store.app.databases)
  },
  get_schema_select_heigth() {
    return parseInt(window.innerHeight / 56, 10);
  }
}
