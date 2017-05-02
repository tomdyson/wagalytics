var path = require("path");
var webpack = require('webpack');

module.exports = {
  context: __dirname,
  entry: {
    wagalytics: './src/wagalytics.js',
    vendors: [
      'moment',
    ]
  },
  output: {
      path: path.resolve('../wagalytics/static/wagalytics/'),
      filename: "[name].bundle.js"
  },

  module: {
    loaders: [{
      test: /\.jsx?$/,
      exclude: /node_modules/,
      loaders: [
        'babel?presets[]=stage-0'
      ]
    }]
  },
  debug: false,

  plugins: [
    new webpack.optimize.DedupePlugin(),
    new webpack.DefinePlugin({
      'process.env': {
        NODE_ENV: JSON.stringify('production')
      }
    }),
    new webpack.SourceMapDevToolPlugin(
      'bundle.js.map',
      '\n//# sourceMappingURL=http://127.0.0.1:3001/dist/js/[url]'
    ),
    new webpack.IgnorePlugin(/^\.\/locale$/, /moment$/)
  ]
}