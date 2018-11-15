module.exports = {
  configureWebpack: {
    devServer: {
      clientLogLevel: 'info',
      watchOptions: {
        poll: true
      }
    }
  }
}