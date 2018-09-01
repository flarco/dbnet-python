// The Vue build version to load with the `import` command
// (runtime-only or standalone) has been set in webpack.base.conf with an alias.
import Vue from 'vue'
import App from './App'
import router from './router'
import Buefy from 'buefy'
import 'buefy/lib/buefy.css'
import VueStash from 'vue-stash';
import store from './store';
import methods from './mixin/methods';
import computed from './mixin/computed';
import VueLodash from 'vue-lodash'
import VueSocketio from 'vue-socket.io';

Vue.use(Buefy, {
  defaultIconPack: 'fa'
})
let sio_url = `http://${document.domain}:5566`

// https://github.com/cklmercer/vue-stash
Vue.use(VueStash)

// https://github.com/Ewocker/vue-lodash
Vue.use(VueLodash)

// https://github.com/MetinSeylan/Vue-Socket.io
Vue.config.productionTip = false

// if (Vue.config.productionTip || process.env.NOVE_ENV != 'development') {
//   sio_url = `http://${document.domain}:${location.port}`
// }
Vue.use(VueSocketio, sio_url);

Vue.mixin({
  computed: computed,
  methods: methods
})

/* eslint-disable no-new */
new Vue({
  el: '#app',
  router,
  template: '<App/>',
  data: {
    store
  },
  components: {
    App
  }
})
