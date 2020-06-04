var path = require('path');
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
      path: path.resolve('./wagalytics/static/wagalytics/'),
      filename: "[name].bundle.js"
  },

  module: {
    rules: [{
      test: /\.jsx?$/,
      exclude: /node_modules/,
      use: [{
        loader: 'babel-loader',
        options: {
          presets: [],
        },
      },
      ]
    }]
  },

  mode: 'production',

  plugins: [
    new webpack.DefinePlugin({
      'process.env': {
        NODE_ENV: JSON.stringify('production')
      }
    }),
    new webpack.SourceMapDevToolPlugin({
      filename: '[name].js.map',
      append: '\n//# sourceMappingURL=http://127.0.0.1:3001/dist/js/[url]'
    }),
    new webpack.IgnorePlugin(/^\.\/locale$/, /moment$/)
  ]
}
