<template>
  <div>
    <aside class="menu" style="overflow: scroll" :style="{'height': this.$store.style.menu_height}">
      <p class="menu-label">
        Connections
        <span class="icon is-small">
          <b-icon pack="fa" icon="plus" type="is-black"></b-icon>
        </span>
      </p>
      <ul class="menu-list" style="overflow: scroll" :style="{'max-height': $store.style.menu_connections_height}">
        <li
          v-for="name in Object.keys($store.app.databases)"
          v-bind:key="name"
          @click="activate_query_db(name)"
        ><a href="/#/query" :class="{'is-active': name == curr_database}">{{ name }}</a></li>
      </ul>
      <p class="menu-label">
        Activities
      </p>
      <ul id="menu-sections" class="menu-list">
        <li><a href="/#/">Query</a></li>
        <li><a href="/#/meta">Meta Explorer</a></li>
        <li><a href="/#/transfer">Data Transfer</a></li>
        <li><a href="/#/settings">Settings</a></li>
      </ul>
    </aside>
  </div>
</template>

<script>
export default {};
</script>

<style lang="scss" scoped>
.menu {
  font-size: 0.9rem;
}
</style>
