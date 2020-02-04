<template>
    <div>
      <header class="navbar is-bold" >
        <a class="navbar-item" @click="toggle_side_menu">
          <b-icon pack="fa" icon="bars" ></b-icon>
        </a>
        <div class="navbar-item has-dropdown is-hoverable">
          <a class="navbar-link" href="#">
            <b-icon pack="fa" icon="bolt" ></b-icon>
          </a>
          <!-- Favorite connections on top -->
          <div class="navbar-dropdown is-boxed" style="overflow: scroll" :style="{'max-height': $store.style.menu_connections_height}">
            <a 
              v-for="name2 in favorite_databases()"
              v-bind:key="name2"
              @click="activate_query_db(name2)"
              href="/#/query" class="navbar-item" :class="{'is-active': name2 == curr_database}">{{ name2 }}</a>
            <hr class="navbar-divider">
            <a 
              v-for="name in non_favorite_databases()"
              v-bind:key="name"
              @click="activate_query_db(name)"
              href="/#/query" class="navbar-item" :class="{'is-active': name == curr_database}">{{ name }}</a>
              
          </div>
        </div>
        <div class="navbar-item is-hoverable" @keyup.27="$store.vars.omnibox_filter=null; focus_app()">
          <a @click="show_omnibox_filter()" v-if="$store.vars.omnibox_filter == null">
            <b-icon pack="fa" icon="search" ></b-icon>
          </a>
          <b-field v-if="$store.vars.omnibox_filter != null">
              <b-autocomplete
                id="omnibox-filter"
                rounded
                v-model="$store.vars.omnibox_filter"
                :data="omnibox_filtered"
                placeholder="Omnibox..."
                icon="magnify"
                @select="option => {omnibox_action(option); $store.vars.omnibox_filter=null}"
              >
                  <template slot="empty">No results found</template>
              </b-autocomplete>
          </b-field>
        </div>
        <div class="container">

          <div id="navbarMiddle" class="navbar-menu" style="heigth: 100px">
            <div class="navbar-start">
              <div class="navbar-brand">
                <a class="navbar-item">
                  <img src="../../assets/logo-brand.png" alt="" href="https://github.com/flarco/dbnet"/>
                </a>
              </div>
            </div>

            <div class="navbar-middle">
              <h1 class="navbar-item title is-4" style="color: #074ab7">{{$route.name}}{{ $route.name == 'Query' ? ` ~ ${$store.query.db_name}  [${$store.query.session_name}]`: ''}}</h1>
            </div>

            <div class="navbar-end">
            </div>
          </div>
        </div>

          <div class="navbar-item is-hoverable" @keyup.27="$store.vars.table_view_filter=null; focus_app()">
            <b-field v-if="$store.vars.table_view_filter != null" style="width:350px">
                  <b-autocomplete
                    id="tables-views-filter"
                    rounded
                    v-model="$store.vars.table_view_filter"
                    :data="get_tables_views_filtered()"
                    placeholder="Find table / view..."
                    icon="magnify"
                    @select="option => {create_object_tab(option); $store.vars.table_view_filter=null}"
                  >
                      <template slot="empty">No results found</template>
                  </b-autocomplete>
              </b-field>
          </div>

          <a class="navbar-item" style="min-width: 55px; color: teal">
            <i class="fa fa-cog fa-spin fa-fw fa-1x" v-if="$store.vars.app_loading"></i>
          </a>
          <a class="navbar-item" style="min-width: 55px; color: teal" title="App In-Mem size for active DB">
            {{ $store.vars.query_storage_size }}
          </a>
          <b-tooltip :label="`Save DB Session (${ localstorage_size })`" position="is-bottom" type="is-dark">
            <a class="navbar-item" @click="save_dbquery_state()">
              <b-icon pack="fa" icon="hdd-o"></b-icon>
            </a>
          </b-tooltip>
          <b-tooltip :label="$store.app.socket_connected?  'Connected': 'Disconnected'" position="is-bottom" type="is-dark">
            <a class="navbar-item">
              <b-icon pack="fa" icon="circle" :style="{'color': $store.app.socket_connected? '#83FF33': 'red'}"></b-icon>
            </a>
          </b-tooltip>
          <a class="navbar-item" @click="reset">
            <b-icon pack="fa" icon="trash-o" ></b-icon>
          </a>
          <a class="navbar-item" style="width: 80px;font-size: 0.8rem" title="CPU / RAM Utilization">
            C={{$store.vars.perf_summary.cpu}}
            R={{$store.vars.perf_summary.ram}}%
          </a>
      </header>

      <!-- TODO: have for loop to display multiple messages as they arrive -->
      <div>
        <section class="modal-card animated fadeInRightBig" style="z-index: 1000; position: absolute;bottom: 10px; right: 10px;" :style="{'width': $store.settings.message.width}" v-if="$store.settings.message.show">
          <b-message
            :title="$store.settings.message.title"
            :type="$store.settings.message.type"
            :size="$store.settings.message.size"
            :close="handle_messages"
            :active.sync="$store.settings.message.show">
              {{ $store.settings.message.text }}
          </b-message>
        </section>
      </div>
    </div>
</template>

<script>
export default {
  computed: {
    localstorage_size() {
      return `${ Math.round(JSON.stringify(localStorage).length / 1024) } KB`
    }
  },
  methods: {
    toggle_side_menu() {
      let self = this;
      this.$store.settings.sidebar_shown = !this.$store.settings.sidebar_shown;
      setTimeout(() => {
        self.resize_panes();
      }, 60);
    },
    omnibox_action(option) {
      let str_filter = this.$store.vars.omnibox_filter.toLowerCase()
      console.log(str_filter)
      console.log(option)
      if(str_filter.startsWith("@")) {
        // Connections
        str_filter = str_filter.substr(1)
        this.activate_query_db(option)
      } else if(str_filter.startsWith("!")) {
        // Sessions
        str_filter = str_filter.substr(1)
        this.activate_query_db(option)
      } else {
      // Table / View Objects

      }
    }
  }
};

/* burger navigation */
document.addEventListener("DOMContentLoaded", function() {
  // Get all "navbar-burger" elements
  var $navbarBurgers = Array.prototype.slice.call(
    document.querySelectorAll(".navbar-burger"),
    0
  );
  // Check if there are any navbar burgers
  if ($navbarBurgers.length > 0) {
    // Add a click event on each of them
    $navbarBurgers.forEach(function($el) {
      $el.addEventListener("click", function() {
        // Get the target from the "data-target" attribute
        var target = $el.dataset.target;
        var $target = document.getElementById(target);
        // Toggle the class on both the "navbar-burger" and the "navbar-menu"
        $el.classList.toggle("is-active");
        $target.classList.toggle("is-active");
      });
    });
  }
});
</script>

<style lang="scss" scoped>
.navbar {
  border-bottom: 1px solid #e0e0e0;
  min-height: 1rem;
}
.navbar-item,
.navbar-menu,
.navbar-end,
.navbar-brand,
.navbar-link {
  padding-bottom: 0px;
  padding-top: 0px;
}
</style>

