import Vue from 'vue'
import Router from 'vue-router'
import Order from '@/Order'
import Process from '@/Process'
import Error from '@/Error'

Vue.use(Router)
export default new Router({
  mode: 'history',
  routes: [
    {
      path: '/order',
      name: 'order',
      component: Order,
      props: (route) => ({
        shop: route.query.shop,
        role: route.query.role
      })
    },
    {
      path: '/process',
      name: 'process',
      component: Process,
      props: (route) => ({
        shop: route.query.shop,
        role: route.query.role
      })
    },
    {
      path: '/error',
      name: 'error',
      component: Error
    }
  ]
})