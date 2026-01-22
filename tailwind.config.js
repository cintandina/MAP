module.exports = {
  content: [
    './templates/**/*.html',
    './modulo_gestion_qr/templates/**/*.html',
    './static/src/**/*.js',
    './node_modules/flowbite/**/*.js',
],
  theme: {
    extend: {},
  },
  plugins: [
    require('flowbite/plugin')
  ],
}


