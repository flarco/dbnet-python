import Vue from 'vue'
import App from './App'
import router from './router'
import Buefy from 'buefy'
import VueStash from 'vue-stash';
import store from './store';
import methods from './mixin/methods';
import computed from './mixin/computed';
import VueLodash from 'vue-lodash'
import VueSocketio from 'vue-socket.io';
import Clipboard from 'v-clipboard'
import VueContextMenu from 'vue-context-menu'

import axios from 'axios'
import VueAxios from 'vue-axios'

Vue.use(VueAxios, axios)

Vue.use(Buefy, {
  defaultIconPack: 'fa'
})

let sio_url = `http://${document.domain}:5566`

// https://github.com/cklmercer/vue-stash
Vue.use(VueStash)

// https://github.com/Ewocker/vue-lodash
Vue.use(VueLodash)

// https://github.com/euvl/v-clipboard
Vue.use(Clipboard)

// https://github.com/MetinSeylan/Vue-Socket.io
Vue.config.productionTip = false

// https://github.com/vmaimone/vue-context-menu
Vue.use(VueContextMenu)

if (Vue.config.productionTip || process.env.NODE_ENV != 'development') {
  let prefix = document.URL.toLocaleLowerCase().includes("https:") ? 'https' : 'http'
  sio_url = `${prefix}://${document.domain}:${location.port}`
}
Vue.use(VueSocketio, sio_url);

Vue.mixin({
  computed: computed,
  methods: methods
})

/* eslint-disable */
const app = new Vue({
  el: '#app',
  router,
  template: '<App/>',
  data: {
    store
  },
  components: {
    App
  },
  render: h => h(App)
}).$mount('#app')

window.vm = app