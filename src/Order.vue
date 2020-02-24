<template>
  <el-container>
    <el-header>
      <el-menu :default-active="currentTab" mode="horizontal" @select="switchTab">
        <el-menu-item index="1">订单列表</el-menu-item>
        <el-menu-item index="2">创建订单</el-menu-item>
      </el-menu>
    </el-header>
    <el-main>
      <el-table v-show="currentTab=='1'" :data="tableData" style="width: 100%">
        <el-table-column
            prop="time"
            label="日期">
        </el-table-column>
        <el-table-column
            prop="name"
            label="姓名">
        </el-table-column>
        <el-table-column
            prop="telephone"
            label="电话">
        </el-table-column>
        <el-table-column
            prop="address"
            label="地址">
        </el-table-column>
      </el-table>
      <el-form v-show="currentTab=='2'" :model="order" status-icon :rules="rulesOrder" ref="order"
               label-width="100px" class="demo-ruleForm" style="width: 100%">
        <el-form-item label="收货人" prop="name">
          <el-input type="text" v-model="order.name" auto-complete="off"></el-input>
        </el-form-item>
        <el-form-item label="地址" prop="address">
          <el-input type="text" v-model="order.address" auto-complete="off"></el-input>
          <el-button type="info" size="mini" icon="el-icon-location" @click="openMap" style="float: right;">
            定位
          </el-button>
        </el-form-item>
        <el-form-item label="电话" prop="telephone">
          <el-input type="tel" v-model.number="order.telephone"></el-input>
        </el-form-item>
        <el-form-item label="商品" prop="items">
          <el-input type="textarea" v-model.number="order.items"></el-input>
        </el-form-item>
        <el-form-item label="备注" prop="note">
          <el-input type="text" v-model.number="order.note"></el-input>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="submitForm('order')">提交</el-button>
          <el-button @click="resetForm('order')">重置</el-button>
        </el-form-item>
      </el-form>
      <baidu-map v-show="currentTab=='0'" class="bm-view" :center="center" :zoom="zoom"
                 @ready="mapHandler" @click="showLocation">
        <bm-geolocation anchor="BMAP_ANCHOR_TOP_LEFT" :showAddressBar="true" :autoLocation="true"
                        @locationSuccess="locationSuccess"></bm-geolocation>
        <bm-scale anchor="BMAP_ANCHOR_TOP_RIGHT"></bm-scale>
        <bm-navigation anchor="BMAP_ANCHOR_BOTTOM_RIGHT"></bm-navigation>
        <bm-info-window :position="{lng: infoWindow.lng, lat: infoWindow.lat}" :title="infoWindow.name"
                        :show="infoWindow.show" @close="infoWindowClose" @open="infoWindowOpen">
          <el-button type="primary" size="mini" icon="el-icon-success" @click="selectLocation">
            选定
          </el-button>
        </bm-info-window>
      </baidu-map>
    </el-main>
    <el-footer>武汉加油！中国加油！
      <el-button v-show="currentTab=='1'" type="info" icon="el-icon-refresh-right" @click="fetchList"></el-button>
    </el-footer>
  </el-container>
</template>

<script>
  import Axios from 'axios'
  import {BmGeolocation} from 'vue-baidu-map'
  import {BmNavigation} from 'vue-baidu-map'
  import {BmScale} from 'vue-baidu-map'
  import {BmInfoWindow} from 'vue-baidu-map'

  export default {
    name: "Order",
    props: ['shop', 'role'],
    components: {
      BmGeolocation,
      BmNavigation,
      BmScale,
      BmInfoWindow
    },
    data() {
      let validateEmpty = (rule, value, callback) => {
        if (value === '') {
          callback(new Error('请输入文字信息'));
        } else {
          callback();
        }
      }
      let validatePhone = (rule, value, callback) => {
        if (value === '') {
          callback(new Error('请输入电话号码'));
        } else {
          if (/^\d+$/.test(value)) {
            callback()
          } else {
            callback(new Error('请输入电话号码'));
          }
        }
      }
      return {
        currentTab: '1',

        tableData: [],

        order: {
          name: '',
          address: '',
          telephone: '',
          items: '',
          note: '',
          lng: 0,
          lat: 0
        },
        rulesOrder: {
          name: [
            {validator: validateEmpty, trigger: 'blur'}
          ],
          address: [
            {validator: validateEmpty, trigger: 'blur'}
          ],
          telephone: [
            {validator: validatePhone, trigger: 'blur'}
          ],
          items: [
            {validator: validateEmpty, trigger: 'blur'}
          ],
          note: []
        },

        center: {lng: 0, lat: 0},
        zoom: 3,

        infoWindow: {
          lat: 0,
          lng: 0,
          name: "",
          show: false
        },

        geoCoder: undefined
      }
    },
    methods: {
      mapHandler({BMap/*, map*/}) {
        // console.log(BMap, map)
        this.center = '西安钟楼'
        this.zoom = 19
        this.geoCoder = new BMap.Geocoder()
      },
      openMap() {
        if (this.order.address != '') {
          var that = this
          this.geoCoder.getPoint(this.order.address, point => {
            that.infoWindow.lat = point.lat
            that.infoWindow.lng = point.lng
            that.infoWindow.name = that.order.address
            that.infoWindowOpen()
            that.center = {lng: point.lng, lat: point.lat}
          })
        }
        this.currentTab='0'
      },
      locationSuccess(evt) {
        console.log(evt)
      },
      showLocation(evt) {
        //console.log(evt)
        this.infoWindow.lat = evt.point.lat
        this.infoWindow.lng = evt.point.lng

        this.geoCoder.getLocation(evt.point, resp => {
          this.infoWindow.name = resp.address
          // geoCoder.getPoint(resp.address, point => {
          //   console.log('getPoint return', point)
          // })
        })
        this.infoWindowOpen()
        this.center = {lng: this.infoWindow.lng, lat: this.infoWindow.lat}
      },
      selectLocation() {
        this.infoWindowClose()
        this.order.address = this.infoWindow.name
        this.order.lat = this.infoWindow.lat
        this.order.lng = this.infoWindow.lng
        this.currentTab = '2'
      },
      infoWindowClose() {
        this.infoWindow.show = false
      },
      infoWindowOpen() {
        this.infoWindow.show = true
      },
      switchTab(key) {
        this.currentTab = key
        if (key === '1') {
          this.fetchList()
        }
      },
      submitForm(formName) {
        this.$refs[formName].validate((valid) => {
          if (!valid) {
            console.log('error submit!!');
            return false;
          } else {
            Axios.get('/new', {
                params: {
                  shop: this.shop,
                  role: 'customer',
                  name: this.order.name,
                  address: this.order.address,
                  telephone: this.order.telephone,
                  items: this.order.items,
                  note: this.order.note,
                  lng: this.order.lng,
                  lat: this.order.lat
                }
              })
              .then(resp => {
                if (resp.data.state === 'ok') {
                  this.$message.success('下单成功！')
                  this.order.items = ''
                  this.order.note = ''
                  this.order.lng = 0
                  this.order.lat = 0
                  this.currentTab = '1'
                  this.fetchList()
                } else {
                  this.$message.error(resp.data.msg)
                }
              })
              .catch(error => console.log(error))
          }
        });
      },
      resetForm(formName) {
        this.$refs[formName].resetFields();
      },
      fetchList() {
        Axios.get(`/list?role=customer&shop=${this.shop}`)
          .then(resp => {
            this.tableData = resp.data
          })
          .catch(error => console.log(error))
      }
    },
    created() {
      this.fetchList()
    }
  }
</script>

<style scoped>
  .bm-view {
    width: 100%;
    height: 400px;
  }
</style>