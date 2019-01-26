/*
 * 2019 The boardgame.io Authors
 *
 * Use of this source code is governed by a MIT-style
 * license that can be found in the LICENSE file or at
 * https://opensource.org/licenses/MIT.
 */

import { GameEnv } from './game-env';
import { default as GTicTacToe } from './game';

const TicTacToe = GameEnv({
  game: GTicTacToe,
  action_space: [0, 8],
  observation_space: [...new Array(9)].map(() => [0, 2]),

  enumerate: G => {
    let r = [];
    for (let i = 0; i < 9; i++) {
      if (G.cells[i] === null) {
        r.push(i);
      }
    }
    return r;
  },
  make_observation: G => {
    return G.cells.map(c => {
      if (c === null) return 0;
      return parseInt(c) + 1;
    });
  },
  make_action: action => {
    return {
      type: 'clickCell',
      args: [action],
    };
  },
});

export default TicTacToe;
