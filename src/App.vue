<template>
  <div id="app">
    <router-view />
  </div>
</template>

<script>
  export default {
    name: 'app',
    created () {
      let shop = document.querySelector("#shop")
      let role = document.querySelector("#role")
      if (shop && role) {
        if (role.textContent === 'customer') {
          this.$router.push({
            path:'/order',
            query:{
              shop: shop.textContent,
              role: 'customer'
            }
          })
        } else if (role.textContent === 'saler') {
          this.$router.push({
            path:'/process',
            query:{
              shop: shop.textContent,
              role: 'saler'
            }
          })
        } else {
          this.$router.push('/error')
        }
      } else {
        this.$router.push('/error')
      }
    }
  }
</script>

<style scoped>
  #app {
    font-family: 'Avenir', Helvetica, Arial, sans-serif;
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
    text-align: center;
    color: #2c3e50;
    /*margin-top: 60px;*/
  }
</style>
