// The Vue build version to load with the `import` command
// (runtime-only or standalone) has been set in webpack.base.conf with an alias.
import Vue from 'vue'
import App from './App'
import router from './router'
import ViewUI from 'view-design'
import 'view-design/dist/styles/iview.css'
import ElementUI from 'element-ui'
import 'element-ui/lib/theme-chalk/index.css'
import Axios from './utils/setaxios'

// import axios from 'axios'
// Vue.use(axios)

Vue.use(ElementUI)
Vue.use(ViewUI)
Vue.config.productionTip = false // 阻止vue在启动时生成生产提示
Vue.prototype.$axios = Axios // 使用方法为this.$axios

new Vue({
  el: '#app',
  router,
  components: { App },
  template: '<App/>'
})
