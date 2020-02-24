# order-lbs
借力百度地图的简易订单系统

场景
====
一个简易订单记账系统，客户下单并输入收货地址。商家查单用地址导航送货。

组成
====
BS架构，前端 vue.js+elementui  后端 tornado+redis

文件
====
后端文件包括backend文件夹和requirements.txt，其他为前端文件（vue-cli3搭建）包括
* src前端源码
* public模板文件（有tornado模板语法）
* mock测试数据
另外有设计文件design.uml用star uml打开

安装
====
把自己申请的百度开发者app对应的AK填写在src/main.js中

前端：安装node环境
* npm i
* npm build
前端打包生成在backend/vuedist中

后端：安装python3和redis，运行redis提供6379端口
* pip3 install -r requirements.txt

测试
====
* python3 webserver.py
* 在python交互环境用webserver.py中Shop.NewShop生成店铺
* 在python交互环境用webserver.py中Shop.GenShopKey查看客户和商家对应码
* 客户: http://127.0.0.1:9000/load?shop=客户对应码&role=customer
* 商家: http://127.0.0.1:9000/load?shop=商家对应码&role=saler
