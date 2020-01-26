module.exports = {
  configureWebpack: {
    devServer: {
      disableHostCheck: true,
      proxy: {
        '^/ws': {
          target: 'http://localhost:5566',
          ws: true,
          changeOrigin: true
        },
        '^/sockjs-node': {
          target: 'http://localhost:5566',
          ws: true,
          changeOrigin: true
        },
        '^/socket.io': {
          target: 'http://localhost:5566',
          ws: true,
          changeOrigin: true,
        },
      },
      clientLogLevel: 'info',
      watchOptions: {
        poll: true
      }
    }
  }
}