<template>
  <span>
    <b-tooltip label="Sessions" position="is-bottom" type="is-dark">

      <b-dropdown position="is-bottom-left">
          <a class="is-info" slot="trigger">
            <b-icon pack="fa" icon="bandcamp" size="is-small"></b-icon>
          </a>

        <b-dropdown-item custom paddingless>
          <div class="modal-card" style="width:270px;">
            <section class="modal-card-body" style="padding-top:10px;">
                <p style="padding-bottom:10px;">Active: <span style="color: blue">{{ $store.query.session.session_name }}</span></p>

                <p style="padding-bottom:10px;">
                  <a class="button is-small is-primary" @click="form.show_field_new_session=true">New</a>
                  <a class="button is-small is-info" @click="form.show_field_rename_session=true">Rename</a>
                  <a class="button is-small is-danger">Delete</a>
                  <a class="button is-small is-danger" @click="save_session()">Save</a>
                </p>

                <b-field v-if="form.show_field_new_session">
                    <b-input
                      name="session_name"
                      v-model="new_session_name"
                      size="is-small"
                      placeholder="Enter new session name..." expanded
                    ></b-input>
                    <p class="control">
                    <button
                      class="button is-primary is-small" @click="create_session"
                    >OK</button>
                    </p>
                </b-field>


                <b-field v-if="form.show_field_rename_session">
                  <b-input name="session_name" size="is-small" placeholder="Enter new session name..." expanded v-model="session_name"></b-input>
                  <p class="control">
                    <button
                      class="button is-primary is-small" @click="rename_session"
                    >OK</button>
                  </p>
                </b-field>

              <b-field>
                <b-autocomplete
                  size="is-small"
                  rounded
                  v-model="session_name"
                  :data="$store.query.session_names"
                  :open-on-focus="true"
                  placeholder="Find & Load Session.."
                  @select="load_session">
                  <template slot="empty">No results found</template>
                </b-autocomplete>
              </b-field>

              <a class="button is-small is-fullwidth is-warning">Export Active Session</a>

              <br/>
              <br/>
              <br/>
              <br/>
              <br/>
              <br/>
              <br/>
            </section>
          </div>
        </b-dropdown-item>
      </b-dropdown>
    </b-tooltip>
  </span>
</template>

<script>
export default {
  data() {
    return {
      new_session_name: null,
      session_name: null,
      form: {
        show_field_new_session: false,
        show_field_rename_session: false,
        show_option_delete_session: false
      }
    };
  },
  methods: {
    select_session(option) {
      self = this;
      if (option == null) return;
      this.$store.query.sessions_name = option;
      setTimeout(function() {
        self.session_name = null;
      }, 10);
    },
    rename_session() {
      this.$store.query.session.session_name = session_name;
      this.form.show_field_rename_session = false;
      this.save_session();
    },

    create_session() {
      self = this;

      // Call only if save is successful
      let on_save = function() {
        self.$store.query.session = {
          db_name: self.$store.query.db_name,
          session_name: self.new_session_name,
          editor_text: null,
          active_tab_name: null,
          tabs: {}
        };
        self.save_session(() => {
          self.new_session_name = null;
          self.form.show_field_new_session = false;
          self.get_sessions();
        });
      };
      self.save_session(on_save);
    },

    save_session(on_save = () => {}) {
      /* Save session to backend */
      self = this;
      this.$store.query.session.editor_text = this.$store.main_editor.text;

      let data1 = {
        store_func: "save_session",
        kwargs: self.$store.query.session
      };

      this.$socket.emit("store", data1, function(data2) {
        if (data2.completed) {
          console.log(
            `Saved session ${self.$store.query.session.session_name}`
          );
          on_save();
        } else {
          // Error handling
          self.notifiy(data2);
        }
      });
    },
    load_session() {
      /* Load session from backend */
      self = this;
      let data1 = {
        store_func: "load_session",
        kwargs: {
          db_name: self.$store.query.db_name,
          session_name: self.session_name
        }
      };

      self.$socket.emit("store", data1, function(data2) {
        if (data2.completed) {
          console.log(`Loading session ${self.session_name}`);
          // self.$store.query.session = {
          //   db_name: data2.payload.db_name,
          //   session_name: data2.payload.session_name,
          //   editor_text: data2.payload.editor_text,
          //   active_tab_name: data2.payload.active_tab_name,
          //   tabs: data2.payload.tabs
          // };
          self.$store.query.session = new self.obj_session(
            data2.payload.db_name,
            data2.payload.session_name,
            data2.payload.editor_text,
            data2.payload.active_tab_name,
            data2.payload.tabs
          );

          self.session_name = null;

          // TODO: create all tabs once payload is received
        } else {
          // Error handling
          self.notifiy(data2);
        }
      });
    },
    delete_session() {
      /* TODO: Delete session from backend */
    },
    get_sessions() {
      // Get list of sessions for Database
      self = this;
      let data1 = {
        store_func: "get_sessions",
        kwargs: {
          db_name: self.$store.query.db_name
        }
      };

      self.$socket.emit("store", data1, function(data2) {
        if (data2.completed) {
          if (self._.isEmpty(data2.payload)) {
            self.$store.query.session_names = data2.payload.map(
              rec => rec.session_name
            );
          }
          // TODO: create all tabs once payload is received
        } else {
          // Error handling
          self.notifiy(data2);
        }
      });
    }
  },
  mounted() {
    // this.main_editor.setSize(600, 300);
    // TODO: load up last session
    /*
      FIRST TIME
      check `databases`
      create `databases` entry with 'default' session_name
      create `sessions` entry of 'default'

      SECOND TIME
      get session_name from `databases`
      get session records from `sessions` with session_name

     */
    self = this;

    if (self.session_name === null) {
      // Initial load, get session name for DB from backend
      let data1 = {
        store_func: "load_database",
        kwargs: {
          db_name: self.$store.query.db_name
        }
      };

      self.$socket.emit("store", data1, function(data2) {
        console.log(data2.payload);
        if (data2.completed) {
          if (self._.isEmpty(data2.payload)) {
            // Create a new session default
            self.$store.query.session = {
              db_name: self.$store.query.db_name,
              session_name: "default",
              editor_text: "",
              active_tab_name: null,
              tabs: {}
            };
            self.save_session();
          } else {
            self.session_name = data2.payload.session_name;
            self.load_session();
          }

          // TODO: create all tabs once payload is received
        } else {
          // Error handling
          self.notifiy(data2);
        }
      });
    }
    setTimeout(function() {
      self.get_sessions();
    }, 1000);
  }
};
</script>

<style lang="scss" scoped>
</style>
