/*
 * Copyright 2019 The boardgame.io Authors
 *
 * Use of this source code is governed by a MIT-style
 * license that can be found in the LICENSE file or at
 * https://opensource.org/licenses/MIT.
 */

const path = require('path');

module.exports = {
  entry: ['babel-polyfill', path.resolve(__dirname, 'tic-tac-toe.js')],

  output: {
    publicPath: '/',
    filename: 'bundle-tic-tac-toe.js',
    library: 'TicTacToe',
    libraryTarget: 'umd',
    path: path.resolve(__dirname, './'),
  },

  module: {
    loaders: [
      {
        exclude: /node_modules/,
        loader: 'babel-loader',
        query: {
          presets: ['@babel/preset-env', '@babel/react'],
          plugins: [
            [
              'module-resolver',
              {
                alias: {
                  'boardgame.io': '../packages',
                },
              },
            ],
          ],
        },
      },
    ],
  },
};
