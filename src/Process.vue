<template>
  <el-container>
    <el-header>
      <p>查看地址信息时可打开百度地图app导航</p>
      <p>
        <el-switch v-model="showAll"
                   active-text="所有订单"
                   inactive-text="忽略过期订单">
        </el-switch>
        <el-badge :value="newOrder" v-show="newOrder>0" style="margin-left:1em;">
          <el-button size="small" @click="fetchList">新订单</el-button>
        </el-badge>
      </p>
    </el-header>
    <el-main>
      <el-table v-show="!showMap" :data="tableData" style="width: 100%">
        <el-table-column prop="time" label="日期"></el-table-column>
        <el-table-column prop="name" label="姓名"></el-table-column>
        <el-table-column prop="telephone" label="电话"></el-table-column>
        <el-table-column label="地址">
          <template slot-scope="scope">
            <span>{{scope.row.address}}</span>
            <el-button @click="popupMap(scope.row)" type="info" plain size="mini">查看</el-button>
          </template>
        </el-table-column>
        <el-table-column prop="items" label="商品"></el-table-column>
        <el-table-column prop="note" label="备注"></el-table-column>
        <el-table-column label="状态">
          <template slot-scope="scope">
            <div v-show="scope.row.stat==0">
              <span>待确认</span>
              <el-button @click="accept(scope.row)" type="primary" plain size="mini">接单</el-button>
              <el-button @click="deny(scope.row)" type="danger" plain size="mini">弃单</el-button>
            </div>
            <div v-show="scope.row.stat==1">
              <span>已接单</span>
              <el-button @click="finish(scope.row)" type="primary" plain size="mini">送达</el-button>
            </div>
            <div v-show="scope.row.stat==2">
              <span>已完成</span>
              <el-button @click="hide(scope.row)" type="primary" plain size="mini">隐藏</el-button>
            </div>
            <div v-show="scope.row.stat==-1">
              <span>已弃单</span>
            </div>
            <div v-show="scope.row.stat==3">
              <span>已隐藏</span>
            </div>
          </template>
        </el-table-column>
      </el-table>
      <baidu-map v-show="showMap" class="bm-view" :center="center" :zoom="zoom"
                 @ready="mapHandler">
        <bm-scale anchor="BMAP_ANCHOR_TOP_RIGHT"></bm-scale>
        <bm-navigation anchor="BMAP_ANCHOR_BOTTOM_RIGHT"></bm-navigation>
        <bm-info-window :position="{lng: infoWindow.lng, lat: infoWindow.lat}" :title="infoWindow.addr"
                        :show="infoWindow.show" @close="infoWindowClose" @open="infoWindowOpen"
                        style="min-height:4rem;">
          <p><span class="left">收货人：</span><span class="right">{{infoWindow.name}}</span></p>
          <p><span class="left">电话：</span><span class="right">{{infoWindow.tel}}</span></p>
          <p><span class="left">商品：</span><span class="right">{{infoWindow.items}}</span></p>
          <p><span class="left">备注：</span><span class="right">{{infoWindow.note}}</span></p>
        </bm-info-window>
      </baidu-map>
    </el-main>
    <el-footer>武汉加油！中国加油！</el-footer>
  </el-container>
</template>

<script>
  import Axios from 'axios'
  import {BmNavigation} from 'vue-baidu-map'
  import {BmScale} from 'vue-baidu-map'
  import {BmInfoWindow} from 'vue-baidu-map'

  export default {
    name: "Process",
    props: ['shop', 'role'],
    components: {
      BmNavigation,
      BmScale,
      BmInfoWindow
    },
    data() {
      return {
        newOrder: 0,
        showAll: false,
        showMap: false,
        tableData: [],
        orders: [],
        center: {lng: 0, lat: 0},
        zoom: 3,
        infoWindow: {
          lat: 0,
          lng: 0,
          addr: "",
          show: false,
          name: '',
          tel: '',
          items: '',
          note: ''
        },
        geoCoder: undefined,
        refresher: undefined
      }
    },
    watch: {
      showAll() {
        this.fetchList()
      }
    },
    methods: {
      hideObsolete() {
        this.tableData = []
        for (let order of this.orders) {
          if (order.stat == 3 || order.stat == -1) {
            continue
          } else {
            this.tableData.push(order)
          }
        }
      },
      showObsolete() {
        this.tableData = this.orders
      },
      fetchList() {
        Axios.get(`/list?role=saler&shop=${this.shop}`)
          .then(resp => {
            this.orders = resp.data
            if (!this.showAll) {
              this.hideObsolete()
            } else {
              this.showObsolete()
            }
            this.newOrder = 0
          })
          .catch(error => console.log(error))
      },
      mapHandler({BMap/*, map*/}) {
        // console.log(BMap, map)
        this.center = '西安钟楼'
        this.zoom = 19
        this.geoCoder = new BMap.Geocoder()
      },
      popupMap(order) {
        var userAgentInfo = navigator.userAgent
        var agents = ['Android', 'iPhone', 'SymbianOS', 'Windows Phone', 'iPad', 'iPod']
        var isPc = true
        for (var v = 0; v < agents.length; v++) {
          if (userAgentInfo.indexOf(agents[v]) > 0) {
            isPc = false
            break
          }
        }
        if (isPc) {
          let point = order.point
          let address = order.address
          if (point !== undefined) {
            let pos = point.split(',', 2)
            let lng = parseFloat(pos[0])
            let lat = parseFloat(pos[1])

            let that = this
            this.$nextTick(() => {
              that.infoWindow.lat = lat
              that.infoWindow.lng = lng
              that.infoWindow.addr = address
              that.infoWindow.show = true
            })
            this.center = {lng: lng, lat: lat}
          } else {
            let that = this
            this.geoCoder.getPoint(address, point => {
              this.$nextTick(() => {
                that.infoWindow.lat = point.lat
                that.infoWindow.lng = point.lng
                that.infoWindow.addr = address
                that.infoWindow.show = true
              })
              that.center = {lng: point.lng, lat: point.lat}
            })
          }
          this.infoWindow.name = order.name
          this.infoWindow.tel = order.telephone
          this.infoWindow.items = order.items
          this.infoWindow.note = order.note
          this.showMap = true
        }
        else {
          var location = order.address
          if (order.point !== undefined) {
            let pos = order.point.split(',', 2)
            let lng = parseFloat(pos[0])
            let lat = parseFloat(pos[1])
            location = `${lat},${lng}`
            let href = `http://api.map.baidu.com/marker?location=${location}&title=${order.name} ${order.telephone}&content=${order.address}&output=html`
            window.location.href=encodeURI(href)
          } else {
            let href = `http://api.map.baidu.com/geocoder?address=${order.address}&output=html`
            window.location.href=encodeURI(href)
          }
        }
      },
      infoWindowClose() {
        this.infoWindow.show = false
        this.showMap = false
      },
      infoWindowOpen() {
        this.infoWindow.show = true
      },
      changeState(order, stat) {
        Axios.get(`/update?shop=${this.shop}&role=saler&id=${order.id}&stat=${stat}`)
          .then(resp => {
            if (resp.data.state == 'ok') {
              order.stat = stat
            } else {
              console.log(resp.data.msg)
            }
          })
          .catch(error => console.log(error))
      },
      accept(order) {
        this.changeState(order, 1)
      },
      deny(order) {
        this.changeState(order, -1)
      },
      finish(order) {
        this.changeState(order, 2)
      },
      hide(order) {
        this.changeState(order, 3)
      },
      fetchCount() {
        Axios.get(`/count?shop=${this.shop}&role=saler`)
          .then(resp => {
            if (resp.data.state == 'ok') {
              this.newOrder = parseInt(resp.data.msg) - this.orders.length
            } else {
              console.log(resp.data.msg)
            }
          })
          .catch(error => console.log(error))
      }
    },
    created() {
      this.fetchList()
    },
    mounted() {
      this.refresher = setInterval(this.fetchCount, 30*1000)
    },
    destroyed () {
      if (this.refresher)
        clearInterval(this.refreshLeader)
    }
  }
</script>

<style scoped>
  .bm-view {
    width: 100%;
    height: 400px;
  }

  .bm-view p {
    margin: 0px;
  }
</style>