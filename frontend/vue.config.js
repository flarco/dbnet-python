module.exports = {
  configureWebpack: {
    devServer: {
      disableHostCheck: true,
      clientLogLevel: 'info',
      watchOptions: {
        poll: true
      }
    }
  }
}