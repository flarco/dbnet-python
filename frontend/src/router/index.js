import Vue from 'vue'
import Router from 'vue-router'
import QueryData from '../views/QueryData'
import Settings from '../views/Settings'
import Transfer from '../views/Transfer'
import Home from '../views/Home'

Vue.use(Router)

export default new Router({
  mode: 'hash',
  linkActiveClass: 'is-active', // for router-link
  scrollBehavior: () => ({
    y: 0
  }),
  routes: [{
      path: '/',
      name: 'Home',
      component: Home
    },
    {
      path: '/query',
      name: 'Query',
      component: QueryData
    },
    {
      path: '/settings',
      name: 'Settings',
      component: Settings
    },
    {
      path: '/transfer',
      name: 'Transfer',
      component: Transfer
    },
  ]
})