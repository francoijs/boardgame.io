/*
 * 2019 The boardgame.io Authors
 *
 * Use of this source code is governed by a MIT-style
 * license that can be found in the LICENSE file or at
 * https://opensource.org/licenses/MIT.
 */

import { Game } from 'boardgame.io/core';
import { makeMove, gameEvent } from '../src/core/action-creators';
import { CreateGameReducer } from '../src/core/reducer';

function IsVictory(cells) {
  const positions = [
    [0, 1, 2],
    [3, 4, 5],
    [6, 7, 8],
    [0, 3, 6],
    [1, 4, 7],
    [2, 5, 8],
    [0, 4, 8],
    [2, 4, 6],
  ];

  for (let pos of positions) {
    const symbol = cells[pos[0]];
    let winner = symbol;
    for (let i of pos) {
      if (cells[i] != symbol) {
        winner = null;
        break;
      }
    }
    if (winner != null) return true;
  }

  return false;
}

const TicTacToe = Game({
  name: 'tic-tac-toe',

  setup: () => ({
    cells: new Array(9).fill(null),
  }),

  moves: {
    clickCell(G, ctx, id) {
      const cells = [...G.cells];

      if (cells[id] === null) {
        cells[id] = ctx.currentPlayer;
        return { ...G, cells };
      }
    },
  },

  flow: {
    movesPerTurn: 1,

    endGameIf: (G, ctx) => {
      if (IsVictory(G.cells)) {
        return { winner: ctx.currentPlayer };
      }
      if (G.cells.filter(c => c === null).length == 0) {
        return { draw: true };
      }
    },
  },
});

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
  // let end = state.ctx.gameover && state.ctx.gameover.winner;
  // let won = false;
  // if (end && state.ctx.gameover.winner === state.ctx.currentPlayer) won = true;
  // return {
  //   G: state.G,
  //   ctx: state.ctx,
  //   done: end ? true : false,
  //   reward: end ? (won ? 1 : -1) : 0,
  // };
};

export default TicTacToe;
