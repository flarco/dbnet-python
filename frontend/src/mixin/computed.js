export default {
  curr_database() {
    return this.$store.query.db_name;
  },
  sess_schema() {
    return this.$store.query.sessions[this.$store.query.session_name].schema;
  },
  sess_schema_obj_type() {
    return this.$store.query.sessions[this.$store.query.session_name]
      .schema_obj_type;
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
