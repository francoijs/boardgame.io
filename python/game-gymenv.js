/*
 * 2019 The boardgame.io Authors
 *
 * Use of this source code is governed by a MIT-style
 * license that can be found in the LICENSE file or at
 * https://opensource.org/licenses/MIT.
 */

import { makeMove, gameEvent } from '../src/core/action-creators';
import { CreateGameReducer } from '../src/core/reducer';
import { default as TicTacToe } from './game';

TicTacToe.action_space = [0, 8];
TicTacToe.observation_space = [...new Array(9)].map(() => [0, 2]);

/* FIXME: shall be based on state as returned by Game.playerView('0') */
TicTacToe.observation = G => {
  return G.cells.map(c => {
    if (c === null) return 0;
    return parseInt(c) + 1;
  });
};

TicTacToe.action = (action, playerID) => {
  return {
    type: 'clickCell',
    playerID: playerID,
    args: [action],
  };
};

TicTacToe.step = (G, ctx, action, playerID) => {
  const reducer = CreateGameReducer({ game: TicTacToe, numPlayers: 2 });
  let state = { G: G, ctx: ctx };
  state = reducer(state, makeMove('clickCell', [action], playerID));
  state = reducer(state, gameEvent('endTurn'));
  return state;
};

export default TicTacToe;
