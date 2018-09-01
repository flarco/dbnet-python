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
                <!-- Session Name -->
                <p style="padding-bottom:10px;">Active: <span style="color: blue">{{ $store.query.session_name }}</span></p>

                <!-- New Session Input -->
                <b-field v-if="form.show_field_new_session">
                    <b-input
                      name="session_name"
                      v-model="new_session_name"
                      size="is-small"
                      placeholder="Enter new session name..." expanded @keyup.native.esc="form.show_field_new_session=false"
                      @keyup.native.enter="create_session"
                      v-entry-focus="true"
                    ></b-input>
                    <p class="control">
                    <button
                      class="button is-primary is-small" @click="create_session"
                    >OK</button>
                    </p>
                </b-field>

                <!-- Rename Session Input -->
                <b-field v-if="form.show_field_rename_session" >
                  <b-input name="session_name" size="is-small" placeholder="Enter new session name..." expanded v-model="session_name" 
                  v-entry-focus="true"
                  @keyup.native.esc="form.show_field_rename_session=false" @keyup.native.enter="rename_session"></b-input>
                  <p class="control">
                    <button
                      class="button is-primary is-small" @click="rename_session"
                    >OK</button>
                  </p>
                </b-field>

              <!-- Find & Load Session Input -->
              <b-field @keyup.native.esc="filter_word=null" v-if="!form.show_field_new_session && !form.show_field_rename_session">
                <b-autocomplete
                  size="is-small"
                  rounded
                  v-model="filter_word"
                  :data="session_names()"
                  :open-on-focus="true"
                  placeholder="Find & Load Session.."
                  @select="select_session">
                  <template slot="empty">No results found</template>
                </b-autocomplete>
              </b-field>

                <!-- Buttons -->
                <p style="padding-bottom:7px;">
                  <a class="button is-small is-fullwidth is-primary" @click="form.show_field_new_session=true;form.show_field_rename_session=false">Create New Session</a>
                </p>
                <p style="padding-bottom:7px;">
                  <a class="button is-small is-fullwidth is-info" @click="form.show_field_rename_session=true; form.show_field_new_session=false">Rename Active Session</a>
                </p>
                <p style="padding-bottom:7px;">
                  <a class="button is-small is-fullwidth is-danger" @click="delete_session">Delete Active Session</a>
                </p>

              <!-- Save button -->
              <div style="padding-bottom:7px;">
              <a class="button is-small is-fullwidth is-dark" @click="save_session(true)">Save Active Session</a>
              </div>

              <!-- Export button -->
              <a class="button is-small is-fullwidth is-warning">Export Active Session</a>

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
      filter_word: "",
      form: {
        show_field_new_session: false,
        show_field_rename_session: false,
        show_option_delete_session: false
      }
    };
  },
  directives: {
    // https://github.com/buefy/buefy/issues/539
    "entry-focus": function(el, binding) {
      if (binding.value) {
        if (el.tagName === "INPUT") {
          el.focus();
        } else {
          el.querySelector("input").focus();
        }
      }
    }
  },
  computed: {},
  methods: {
    session_names() {
      // return Object.keys(this.$store.query.sessions);
      return Object.keys(this.$store.query.sessions).filter(sess_name => {
        return this.filter_word
          ? sess_name
              .toString()
              .toLowerCase()
              .indexOf(this.filter_word.toLowerCase()) >= 0
          : sess_name;
      });
    },
    select_session(option) {
      self = this;
      if (option == null) return;
      this.filter_word = "";
      self.new_session_name = option;
      this.load_session();
      this.$store.query.sessions_name = option;
      setTimeout(function() {
        self.filter_word = null;
      }, 100);
    },
    rename_session() {
      let old_name = this._.cloneDeep(this.$store.query.session_name);
      if (old_name == "default") {
        this.$toast.open({
          message: `Cannot rename Session 'default'. Create a new one!`,
          type: "is-danger"
        });
        self.session_name = this._.cloneDeep(this.$store.query.session_name);
        return;
      }
      this.$store.query.session_name = this.session_name;
      this.$store.query.sessions[this.session_name] = this._.cloneDeep(
        this.$store.query.sessions[old_name]
      );
      delete this.$store.query.sessions[old_name];
      this.form.show_field_rename_session = false;
      this.save_session();
    },

    create_session() {
      self = this;
      let session_data = {
        db_name: self.$store.query.db_name,
        session_name: self.new_session_name
      };

      if (self.new_session_name in self.$store.query.sessions) {
        this.$toast.open({
          message: `Session '${self.new_session_name}' already exists!`,
          type: "is-danger"
        });
      } else {
        self.$store.query.sessions[self.new_session_name] = new this.Session(
          session_data
        );
        this.load_session();

        self.new_session_name = null;
        self.form.show_field_new_session = false;
      }
    },

    save_session(toast = false) {
      this.$store.query.sessions[
        this.session_name
      ].editor_text = this.$store.query.editor_text;
      this.save_state();
      if (toast)
        this.$toast.open({
          message: `Session '${self.$store.query.session_name}' saved!`,
          type: "is-success"
        });
    },
    load_session(toast = true) {
      /* Load session from backend */
      self = this;
      this.save_session();
      if (self.new_session_name in self.$store.query.sessions) {
        this.$store.query.session_name = this.new_session_name;
        this.session_name = this.new_session_name;
        this.$store.query.editor_text = this.$store.query.sessions[
          this.session_name
        ].editor_text;
        this.$forceUpdate();
        self.filter_word = null;
        if (toast)
          this.$toast.open({
            message: `Session '${self.new_session_name}' loaded!`,
            type: "is-success"
          });
      } else {
        self.notify({
          error: `Session '${self.new_session_name}' not found!`
        });
      }
    },
    delete_session() {
      /* TODO: Delete session from backend */
      self = this;
      let old_name = this._.cloneDeep(this.$store.query.session_name);
      if (old_name == "default") {
        this.$toast.open({
          message: `Cannot delete 'default' session.`,
          type: "is-danger"
        });
        return;
      }

      let do_delete = function() {
        self.new_session_name = "default";
        self.load_session(false);
        delete self.$store.query.sessions[old_name];
        self.$toast.open({
          message: `Session '${old_name}' deleted!`,
          type: "is-warning"
        });
      };

      this.$dialog.confirm({
        title: `Deleting Session '${old_name}'`,
        size: "is-small",
        message: `Are you sure you want to <b>delete</b> your session ${old_name}? This action cannot be undone. You will lose at the SQL Code, Analysis and Query history for that session!`,
        confirmText: "Delete Session",
        type: "is-danger",
        hasIcon: true,
        onConfirm: () => do_delete()
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

    self.session_name = this._.cloneDeep(this.$store.query.session_name);
  }
};
</script>

<style lang="scss" scoped>
</style>
