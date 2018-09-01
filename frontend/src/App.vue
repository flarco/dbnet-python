<template>
  <div id="app" :style="{'height': this.$store.style.app_height}">
    <nav-bar></nav-bar>
    <main-content></main-content>
    <!-- <info-bar></info-bar>
    <footer-bar></footer-bar> -->
  </div>
</template>

<script>
import { NavBar, MainContent, InfoBar, FooterBar } from "components/layout/";

export default {
  components: {
    "nav-bar": NavBar,
    "main-content": MainContent,
    "info-bar": InfoBar,
    "footer-bar": FooterBar
  },
  sockets: {
    connect: function() {
      console.log("socket connected");
      this.$store.app.socket_connected = true;

      // get profile databases from backend
      this.get_databases();
    },
    disconnect: function() {
      console.log("socket disconnected");
      this.$store.app.socket_connected = false;
    },
    customEmit: function(val) {
      console.log(
        'this method was fired by the socket server. eg: io.emit("customEmit", data)'
      );
    },
    "client-response": function(data) {
      self = this;

      if (!data.completed && !data.queued) {
        this.notify(data);
      } else {
        switch (data.orig_req.req_type) {
          case "get-databases":
            self.rcv_databases(data);
            break;
          case "get-query-state":
            self.activate_query_db(data);
            break;
          default:
            data;
        }
      }
    },
    "query-data": function(data) {
      self = this;

      if (!data.completed) {
        this.notify(data);
      } else if (!this._.isEmpty(data.options.meta)) {
        switch (data.options.meta) {
          case "get_schemas":
            self.rcv_schemas(data);
            break;
          case "get_tables":
            self.rcv_tables(data);
            break;
          case "get_views":
            self.rcv_views(data);
            break;
          default:
            self.notify(data);
        }
      }
    },
    "task-error": function(data2) {
      this.notify(data2);
    }
  },
  methods: {},
  beforeCreate() {},
  created() {
    let self = this;
    window.addEventListener("resize", self.resize_panes);
    setTimeout(self.resize_panes, 50);

    // Load State from localStorage
    this.load_state();

    window.onbeforeunload = function(event) {
      if (!self.$store.app.resetting) self.save_state();
    };
  },
  mounted() {
    this.resize_panes();
  }
};
</script>

<style lang="scss">
@import "~animate.css";
.animated {
  animation-duration: 0.377s;
}

// Import Bulma's core
@import "~bulma/sass/utilities/_all";

// Set your colors
$primary: #67ef9b;
$primary-invert: findColorInvert($primary);

$navbar-height: 2.5rem;
$navbar-padding-horizontal: 1rem;

// Setup $colors to use as bulma classes (e.g. 'is-twitter')
$colors: (
  "white": ($white, $black),
  "black": ($black, $white),
  "light": ($light, $light-invert),
  "dark": ($dark, $dark-invert),
  "primary": ($primary, $primary-invert),
  "info": ($info, $info-invert),
  "success": ($success, $success-invert),
  "warning": ($warning, $warning-invert),
  "danger": ($danger, $danger-invert)
);

// Links
$link: $primary;
$link-invert: $primary-invert;
$link-focus-border: $primary;

// Import Bulma and Buefy styles
@import "~bulma";
@import "~buefy/src/scss/buefy";

$fa-font-path: "~font-awesome/fonts/";
@import "~font-awesome/scss/font-awesome";

// global custom style
.has-shadow {
  box-shadow: 0 2px 3px hsla(0, 0%, 4%, 0.1);
}

#app {
  background-color: lightgrey;
  height: 100%;
}

.CodeMirror {
  border: 1px solid #eee;
  height: 100%;
  font-size: 0.8rem;
}

.separator {
  margin-left: 0.4em;
  padding-right: 0.4em;
  border-left: 1px solid lightgray;
}

nav.tabs > ul > li > a {
  padding-top: 3px;
  padding-bottom: 3px;
  padding-left: 11px;
  padding-right: 11px;
}

.schema_select {
  height: 300px;
}
</style>
