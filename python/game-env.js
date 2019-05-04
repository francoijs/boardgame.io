/*
 * 2019 The boardgame.io Authors
 *
 * Use of this source code is governed by a MIT-style
 * license that can be found in the LICENSE file or at
 * https://opensource.org/licenses/MIT.
 */

import { makeMove, gameEvent } from '../src/core/action-creators';
import { CreateGameReducer } from '../src/core/reducer';

/**
 * Build extended Game object for use in the python OpenAI Gym environment.
 *
 * @param {...object} game - The original game object.
 * @param {...object} action_space - Discrete range of valid actions (format: [min, max]).
 * @param {...object} observation_space - Dimensions and range of valid observations
 *                                        (e.g: [[0, 1], [-2.4, 2.4]]).
 * @param {...function} enumerate - Provides the list of valid actions for a given state
 *                                  (format: G => [actions from action_space]).
 * @param {...function} make_action - Converts from action_space to game action
 *                                    (format: A => {type: string, args: array}).
 * @param {...function} make_observation - Converts state to observation
 *                                         (format: G => obs from observation_space).
 */
export function GameEnv({
  game,
  action_space,
  observation_space,
  enumerate,
  make_action,
  make_observation,
}) {
  /* patch that prevents 'moveNames' to be seen empty when using js2py+python3 */
  game.moveNames = Object.keys(game.moves);
  const reducer = CreateGameReducer({ game, numPlayers: 2 });
  return Object.assign(
    {
      action_space,
      observation_space,
      enumerate,

      observation: G => {
        return make_observation(game.playerView(G));
      },
      action: A => {
        return make_action(A);
      },

      step: (G, ctx, A, playerID) => {
        let state = { G: G, ctx: ctx };
        let action = make_action(A);
        state = reducer(state, makeMove(action.type, action.args, playerID));
        state = reducer(state, gameEvent('endTurn'));
        return state;
      },
    },
    game
  );
}
