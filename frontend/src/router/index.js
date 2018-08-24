import Vue from 'vue'
import Router from 'vue-router'
import Query from 'views/Query'
import Settings from 'views/Settings'

Vue.use(Router)

export default new Router({
  mode: 'hash',
  linkActiveClass: 'is-active', // for router-link
  scrollBehavior: () => ({
    y: 0
  }),
  routes: [{
      path: '/',
      name: 'Query',
      component: Query
    },
    {
      path: '/settings',
      name: 'Settings',
      component: Settings
    },
  ]
})
