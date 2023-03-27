import Vue from 'vue'
import Router from 'vue-router'
import MultiProcess from '@/components/MultiProcess'

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
