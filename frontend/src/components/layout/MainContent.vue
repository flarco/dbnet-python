<template>
  <section class="main-content">
    
    <div class="tile is-ancestor animated fadeInLeftBig" style="margin: -5px">
      <b-loading :is-full-page="true" :active.sync="$store.vars.app_loading" :can-cancel="true"></b-loading>
      <div id="side-menu" class="tile is-parent is-2" style="padding-right: 0px" :style="{'max-width': $store.style.sidebar_width}" v-if="$store.settings.sidebar_shown">
        <article class="tile is-child box">
          <side-menu></side-menu>
        </article>
      </div>
      <div id="query-pane" class="tile is-parent" style="padding-right: 1px" :style="{'height': $store.style.pane_height}" :class="{'is-2':$store.settings.pane_width=='2','is-3':$store.settings.pane_width=='3','is-4':$store.settings.pane_width=='4', 'is-5':$store.settings.pane_width=='5'}"
      v-if="$route.name == 'Query' && $store.query.db_name != null">
        <article class="tile is-child box">
          <query class="animated"></query>
        </article>
      </div>
      <div class="tile is-parent" style="padding-left: 0px">
        <article class="tile is-child box" style="padding-top: 4px; padding-left: 7px" v-if="$route.name == 'Settings' || ($route.name != 'Home' && $store.query.db_name != null)">

          <transition
              mode="out-in"
              enter-active-class="fadeIn"
              leave-active-class="fadeOut"
              appear>
              <router-view class="animated"></router-view>
          </transition>

        </article>
      </div>
    </div>
  </section>
</template>

<script>
import SideMenu from "./SideMenu.vue";
import QueryPane from "../../views/QueryPane.vue";
export default {
  name: "main-content",
  components: {
    "side-menu": SideMenu,
    query: QueryPane
  }
};
</script>

<style lang="scss" scoped>
.main-content {
  min-height: 400px;
}
article.tile {
  padding: 15px;
}
</style>
