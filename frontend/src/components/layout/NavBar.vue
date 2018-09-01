<template>
    <div>
      <header class="navbar is-bold" >
        <a class="navbar-item" @click="$store.settings.sidebar_shown=!$store.settings.sidebar_shown">
          <b-icon pack="fa" icon="bars" ></b-icon>
        </a>
        <div class="navbar-item has-dropdown is-hoverable">
          <a class="navbar-link" href="#">
            <b-icon pack="fa" icon="bolt" ></b-icon>
          </a>
          <!-- Favorite connections on top -->
          <div class="navbar-dropdown is-boxed">
            <a class="navbar-item is-active" href="#">
              SPARK
            </a>
            <a class="navbar-item" href="#">
              HIVE
            </a>
            <hr class="navbar-divider">
            <a class="navbar-item" href="#">
              DW1
            </a>
            <a class="navbar-item" href="#">
              EDW2
            </a>
          </div>
        </div>
        <div class="container">

          <div id="navbarDropdown" class="navbar-menu" style="heigth: 100px">
            <div class="navbar-start">
              <div class="navbar-brand">
                <a class="navbar-item">
                  <img src="../../assets/logo-brand2.png" alt=""/>
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
        <b-tooltip :label="$store.app.socket_connected?  'Connected': 'Disconnected'" position="is-bottom" type="is-dark">
          <a class="navbar-item">
            <b-icon pack="fa" icon="circle" :style="{'color': $store.app.socket_connected? '#83FF33': 'red'}"></b-icon>
          </a>
        </b-tooltip>
        <a class="navbar-item" @click="reset">
          <b-icon pack="fa" icon="trash-o" ></b-icon>
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
export default {};

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

