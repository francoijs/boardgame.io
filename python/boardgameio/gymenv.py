#
# Copyright 2019 The boardgame.io Authors
#
# Use of this source code is governed by a MIT-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/MIT.
#
# pylint: disable=invalid-name,import-error,no-self-use

from collections import namedtuple
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
    Base class for OpenAI Gym environment.
    """

    @staticmethod
    def make(fname, cname=None):
        """
        Return a GymEnv running an instance of Game object {cname} defined in {fname}
        - a ES6 file (extension .js)
        - or a Python3 file (extension .py)
        By default, cname = fname without the extension.
        """
        if fname.endswith('.js'):
            return GymEnvJs(fname[:-3], cname)
        elif fname.endswith('.py'):
            return GymEnvPy(fname[:-3], cname)
        return gym.make(fname)

    def __init__(self):
        # stats
        self._counters = (0, 0)
        self.set_opponent_policy(self._default_opponent_policy)
        self._G = self._ctx = None
        self.reset()

    def __del__(self):
        if not self._counters[0]:
            tps = 0
        else:
            tps = self._counters[1] / self._counters[0]
        self.log.debug('avg time per step: %.3fs', tps)

    @property
    def name(self):
        """ Name of game. """
        return self._game.name

    def _default_opponent_policy(self, G):
        return random.choice(self._game.enumerate(G))

    def set_opponent_policy(self, pol):
        """ Set policy of player '1'. """
        self._think = pol

    @property
    def action_dim(self):
        """ Number of dimensions of action-space. """
        return self.action_space.n

    @property
    def action_space(self):
        """ Boundaries of action-space. """
        space = self._action_space_impl
        rv = spaces.Discrete(max(space)-min(space)+1)
        rv.low = min(space)
        rv.high = max(space)
        return rv

    @property
    def observation_dim(self):
        """ Number of dimensions of observation-space. """
        return self.observation_space.shape[0]

    @property
    def observation_space(self):
        """ Boundaries of observation-space. """
        dims = self._observation_space_impl
        assert len(dims) == 2
        return spaces.Box(low=0, high=dims[1]-1, shape=(dims[0],), dtype=int)

    def reset(self):
        """ Reset environment to initial state. """
        self._ctx = self._game.flow.ctx(2)
        self._G = self._game.setup()
        return np.asarray(self._observation(self._G))

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
                self.log.debug('action not possible in current state: %d', action)
                done = True
                reward = -10
            obs = np.asarray(self._observation(self._G))
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


class GymEnvPy(GymEnv):
    """
    Provide an OpenAI Gym environment around a Python3 Boardgame.io 'Game' object.
    """
    log = logging.getLogger('boardgameio.gymenvpy')

    def __init__(self, fname, cname=None):
        cname = cname or fname
        module = __import__(fname, globals(), locals(), [])
        self._game = getattr(module, cname)
        GymEnv.__init__(self)

    def reset(self):
        """ Reset environment to initial state. """
        self._G = self._game.setup()
        self._ctx = namedtuple('Context', ['gameover'])(False)
        return np.asarray(self._game.observation(self._G))

    @property
    def _action_space_impl(self):
        return self._game.action_space

    @property
    def _observation_space_impl(self):
        return self._game.observation_space

    def _observation(self, G):
        return self._game.observation(G)

    def _action(self, A):
        return self._game.action(A)


class GymEnvJs(GymEnv):
    """
    Provide an OpenAI Gym environment around a ES6 Boardgame.io 'Game' object.
    """
    log = logging.getLogger('boardgameio.gymenvjs')

    def __init__(self, fname, cname=None):
        cname = cname or fname
        if not os.path.isfile(cname+'.py') or os.path.getmtime(cname+'.py') < os.path.getmtime(fname+'.js'):
            js2py.translate_file(fname+'.js', cname+'.py')
        module = __import__(cname, globals(), locals(), [None])
        self._game = module.var.get(cname).get('default').to_python()
        GymEnv.__init__(self)

    @property
    def _action_space_impl(self):
        return self._game.action_space.to_list()

    @property
    def _observation_space_impl(self):
        return self._game.observation_space.to_list()

    def _observation(self, G):
        return self._game.observation(G).to_list()
