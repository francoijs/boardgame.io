#
# Copyright 2019 The boardgame.io Authors
#
# Use of this source code is governed by a MIT-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/MIT.
#
# pylint: disable=invalid-name,import-error,no-self-use

"""
GymEnv interface.
"""

import os
import numpy as np
import js2py
import gym
from gym import spaces


class GymEnv(gym.Env):
    """
    Provide a OpenAI's gym environment around a JS 'Game' object.
    """

    @staticmethod
    def make(fname, cname=None):
        """
        Return a GymEnv running an instance of Game object {cname} defined in JS file '{fname}.js'.
        By default, cname = fname.
        """
        return GymEnv(fname, cname)

    def __init__(self, fname, cname=None):
        cname = cname or fname
        if not os.path.isfile(cname+'.py') or os.path.getmtime(cname+'.py') < os.path.getmtime(fname+'.js'):
            js2py.translate_file(fname+'.js', cname+'.py')
        module = __import__(cname, globals(), locals(), [None], -1)
        self._game = module.var.get(cname).get('default').to_python()
        self.set_opponent_policy(self._default_opponent_policy)
        # game context
        self._ctx = self._game.flow.ctx(2)
        self._G = self._game.setup()

    def _default_opponent_policy(self, _G):
        # policy of opponent (default=random)
        return self.action_space.sample()

    def set_opponent_policy(self, pol):
        """ Set policy of player '1'. """
        self._think = pol

    @property
    def name(self):
        """ Name of game. """
        return self._game.name

    @property
    def action_dim(self):
        """ Number of dimensions of action-space. """
        return self.action_space.n

    @property
    def action_space(self):
        """ Boundaries of action-space. """
        space = self._game.action_space.to_list()
        rv = spaces.Discrete(max(space)-min(space)+1)
        rv.low = min(space)
        rv.high = max(space)
        return rv

    @property
    def observation_dim(self):
        """ Number of dimensions of observation-space. """
        return self.observation_space.low.shape[0]

    @property
    def observation_space(self):
        """ Boundaries of observation-space. """
        space = self._game.observation_space.to_list()
        return spaces.Box(
            np.amin(space, axis=1),
            np.amax(space, axis=1)
        )

    def reset(self):
        """ Reset environment to initial state. """
        self._G = self._game.setup()
        return self._game.observation(self._G).to_list()

    def step(self, action):
        """ Perform step. """
        state = self._game.step(self._G, self._ctx, action, '0')
        if not state.ctx.gameover:
            # play opponent
            action = self._think(state.G)
            state = self._game.step(state.G, state.ctx, action, '1')
        self._G = state.G
        self._ctx = state.ctx
        if state.ctx.gameover:
            done = True
            reward = 1 if state.ctx.gameover.winner == '0' else -1
        else:
            done = False
            reward = 0
        return self._game.observation(self._G).to_list(), reward, done, 'nada'
