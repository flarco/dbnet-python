/* eslint-disable */
<template>
  <div id="app" :style="{'height': this.$store.style.app_height}">
    <nav-bar></nav-bar>
    <main-content></main-content>
    <iframe id="file-iframe" hidden/>
    <!-- <info-bar></info-bar>
    <footer-bar></footer-bar> -->
  </div>
</template>

<script>
import { NavBar, MainContent, InfoBar, FooterBar } from "./components/layout/";

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

      this.$store.vars.mon_interval = setInterval(this.get_mon_perf, 1000);
    },
    disconnect: function() {
      console.log("socket disconnected");
      this.$store.app.socket_connected = false;
      clearInterval(this.$store.vars.mon_interval);
    },
    customEmit: function(val) {
      console.log(
        'this method was fired by the socket server. eg: io.emit("customEmit", data)'
      );
    },
    "client-response": function(data) {
      let self = this;

      data.ts_end = new Date().getTime();

      if (!data.completed && !data.queued) {
        this.notify(data);
      } else if (data.queued && data.orig_req.tab_id != null) {
        switch (data.orig_req.req_type) {
          case "submit-sql":
            // set the worker name
            self.set_tab_query_prop(
              data.orig_req.tab_id,
              "worker_name",
              data.worker_name,
              data.orig_req.session_name
            );
            break;
          default:
            data;
        }
      } else {
        switch (data.orig_req.req_type) {
          case "get-databases":
            self.rcv_databases(data);
            break;
          case "get-query-state":
            self.activate_query_db(data);
            break;
          case "get-meta-columns":
            self.rcv_query_data(data);
            break;
          case "get-queries":
            self.rcv_queries(data);
            break;
          case "get-meta-tables":
            if (data.rows != null) self.rcv_query_data(data);
            break;
          default:
            data;
        }
      }
    },
    "meta-updated": function(data) {
      if (!data.completed) {
        this.notify(data);
      } else {
        // Meta has been updated, re-submit orig-req
        this.submit_req(data.orig_req);
      }
    },
    monitor: function(data) {
      this.$store.vars.perf_summary.cpu = data.tot_cpu_prct;
      this.$store.vars.perf_summary.ram = data.tot_ram_prct;
    },
    "spark-url": function(data) {
      this.$store.app.databases[data.database].url = data.url;
    },
    "template-sql": function(data) {
      if (!data.completed) {
        this.notify(data);
      } else {
        this.submit_sql(data.sql, data.orig_req.tab_id);
      }
    },
    "query-data": function(data) {
      let self = this;
      if (!this._.isEmpty(data.options.meta)) {
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
          case "get_columns":
            self.rcv_query_data(data);
            break;
          case "get_ddl":
            self.rcv_query_data(data);
            break;
          case "analyze_fields":
            self.rcv_query_data(data);
            break;
          case "analyze_tables":
            self.rcv_query_data(data);
            break;
          default:
            self.log(data);
        }
      } else if (data.orig_req.req_type == "submit-sql") {
        self.rcv_query_data(data);
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
    const self = this
    window.addEventListener("keydown", function(e) {
      if(e.keyCode == 113) self.show_db_name_filter()
    });
    window.addEventListener("keydown", function(e) {
      if(e.keyCode == 66 && (e.altKey || e.metaKey)) self.navigate_prev_db()
    });
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
  "white": (
    $white,
    $black
  ),
  "black": (
    $black,
    $white
  ),
  "light": (
    $light,
    $light-invert
  ),
  "dark": (
    $dark,
    $dark-invert
  ),
  "primary": (
    $primary,
    $primary-invert
  ),
  "info": (
    $info,
    $info-invert
  ),
  "success": (
    $success,
    $success-invert
  ),
  "warning": (
    $warning,
    $warning-invert
  ),
  "danger": (
    $danger,
    $danger-invert
  )
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
  // font-size: 0.8rem;
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

div.tabs > ul > li > a {
  padding-top: 3px;
  padding-bottom: 3px;
  padding-left: 11px;
  padding-right: 11px;
}

div.tabs > ul > li > span > a {
  padding-top: 3px;
  padding-bottom: 3px;
  padding-left: 11px;
  padding-right: 11px;
}

.hot_div {
  box-sizing: border-box;
  padding-top: 0px;
  width: 100%;
  overflow: hidden;
  font-size: 0.7rem;
}

.schema_select {
  height: 300px;
}

nav.tab-top {
  padding-top: 0.3em;
  padding-bottom: 0.3em;
  margin-bottom: 10px;
}

div.tab-top > ul > li > a {
  padding-left: 0.3em;
  padding-right: 0.3em;
}

div.tab-top > span {
  padding-right: 20px;
}

div.tab-top > span > a > i {
  vertical-align: baseline;
}

.codelike {
  font-family: monospace;
}

.item_select {
  border-radius: 4px;
  border: 1px solid #aaaaaa;
}
</style>
