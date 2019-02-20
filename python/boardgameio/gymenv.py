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
import time
import random
import logging
import numpy as np
import js2py
import gym
from gym import spaces


class GymEnv(gym.Env):
    """
    Provide an OpenAI Gym environment around a Boardgame.io 'Game' object.
    """
    log = logging.getLogger('boardgameio.gymenv')

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
        module = __import__(cname, globals(), locals(), [None])
        self._game = module.var.get(cname).get('default').to_python()
        self.set_opponent_policy(self._default_opponent_policy)
        # game context
        self._ctx = self._G = None
        self.reset()
        # stats
        self._counters = (0, 0)
        # default policy = random
        self._think = self._default_opponent_policy

    def __del__(self):
        if not self._counters[0]:
            tps = 0
        else:
            tps = self._counters[1] / self._counters[0]
        self.log.debug('avg time per step: %.3fs', tps)

    def _default_opponent_policy(self, G):
        return random.choice(self._game.enumerate(G))

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
        dims = self._game.observation_space.to_list()
        assert len(dims) == 2
        return dims[0]

    @property
    def observation_space(self):
        """ Boundaries of observation-space. """
        dims = self._game.observation_space.to_list()
        assert len(dims) == 2
        return spaces.Box(low=0, high=dims[1]-1, shape=(dims[0],), dtype=int)

    def reset(self):
        """ Reset environment to initial state. """
        self._ctx = self._game.flow.ctx(2)
        self._G = self._game.setup()
        return np.asarray(self._game.observation(self._G).to_list())

    def step(self, action):
        """ Perform step. """
        time0 = time.time()
        done = False
        reward = 0

        # fix numpy types (fail with js2py)
        if type(action).__module__ == np.__name__:
            action = action.item()
        try:
            if action in self._game.enumerate(self._G):
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
                self.log.warning('action not possible in current state: %d', action)
                done = True
                reward = -1
            obs = np.asarray(self._game.observation(self._G).to_list())
        except Exception as e:
            self.log.error("""internal exception in JS Game object:
            G=%s
            action=%s
            ctx=%s""", self._G, action, self._ctx)
            raise e

        # update stats
        c = self._counters
        self._counters = (c[0] + 1, c[1] + time.time() - time0)
        return obs, float(reward), done, dict()
