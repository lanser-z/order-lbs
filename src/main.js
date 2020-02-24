import Vue from 'vue'
import ElementUI from 'element-ui'
import 'element-ui/lib/theme-chalk/index.css'
import BaiduMap from 'vue-baidu-map'
import App from './App.vue'
import router from './router'

Vue.use(BaiduMap, {
  ak: 'YOUR BAIDU MAP APP AK'
})
Vue.use(ElementUI)

Vue.config.productionTip = false
// Vue.config.devtools = true /* always enable dev-tools */

new Vue({
  router,
  render: h => h(App),
}).$mount('#app')
