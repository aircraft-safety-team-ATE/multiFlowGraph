import Vue from 'vue'
import Router from 'vue-router'
import MultiProcess from '@/components/MultiProcess'
import ElementUI from 'element-ui';
import 'element-ui/lib/theme-chalk/index.css';
Vue.use(ElementUI);
Vue.use(Router)

export default new Router({
  routes: [
    {
      path: '/',
      name: 'MultiProcess',
      component: MultiProcess
    }
  ]
})
