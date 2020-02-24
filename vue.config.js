// vue.config.js
module.exports = {
  assetsDir: 'static',
  chainWebpack (config) {
    config.plugins.delete('preload')
    config.plugins.delete('prefetch')
  },
  productionSourceMap: false,
  parallel: require('os').cpus().length > 1,
  pages: {
    index: {
      entry: 'src/main.js',
      template: 'public/index.html',
      filename: 'index.html'
    }
  },
  css: {
    extract: false
  },
  devServer: {
    port: 8080,
    before (mockRoute) {
      // mockRoute.all('*', function (req, res, next) {
      //   res.header('Access-Control-Allow-Origin', '*')
      //   res.header('Access-Control-Allow-Headers', '*')
      //   res.header('Access-Control-Allow-Methods', '*')
      //   next()
      // })

      mockRoute.get('/list', (req, resp) => {
        if (req.query.role === 'customer') {
          let menulist = require('./mock/customerlist.json')
          resp.json(menulist)
        } else if (req.query.role === 'saler') {
          let menulist = require('./mock/salerlist.json')
          resp.json(menulist)
        }
      })

      mockRoute.get('/new', (req, resp) => {
          resp.json({state: 'ok', msg: ''})
      })

      mockRoute.get('/update', (req, resp) => {
          resp.json({state: 'ok', msg: ''})
      })

      mockRoute.get('/count', (req, resp) => {
          resp.json({state: 'ok', msg: '2'})
      })
    }
  }
}
