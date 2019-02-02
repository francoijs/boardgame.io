#
# Copyright 2019 The boardgame.io Authors
#
# Use of this source code is governed by a MIT-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/MIT.
#
# pylint: disable=invalid-name,import-error,no-self-use,missing-docstring

import unittest
import numpy as np
from boardgameio import GymEnv


class TestGymEnv(unittest.TestCase):

    def setUp(self):
        self.sut = GymEnv.make('bundle-tic-tac-toe', 'TicTacToe')

    def test_name_shall_return_name_of_game(self):
        self.assertEqual(self.sut.name, 'tic-tac-toe')

    # action_space

    def test_action_dim_shall_return_num_of_dimensions_of_action_space(self):
        self.assertEqual(self.sut.action_dim, 9)

    def test_action_space_shall_return_action_space_boundaries(self):
        self.assertEqual(self.sut.action_space.low, 0)
        self.assertEqual(self.sut.action_space.high, 8)

    # observation_space

    def test_observation_dim_shall_return_num_of_dimensions_of_observation_space(self):
        self.assertEqual(self.sut.observation_dim, 9)

    def test_observation_space_shall_return_observation_space_boundaries(self):
        np.testing.assert_array_equal(self.sut.observation_space.low, [0]*9)
        np.testing.assert_array_equal(self.sut.observation_space.high, [2]*9)

    # reset

    def test_reset_shall_return_initial_observation(self):
        np.testing.assert_array_equal(self.sut.reset(), [0]*9)
    
    def test_reset_shall_reset_internal_state(self):
        self.sut.step(0)
        self.sut.step(3)
        np.testing.assert_array_equal(self.sut.reset(), [0]*9)

    # step

    def test_step_shall_return_new_observation_and_reward(self):
        self.sut.set_opponent_policy(lambda G: 8)
        state, reward, done, _ = self.sut.step(0)
        np.testing.assert_array_equal(state, [1, 0, 0,
                                              0, 0, 0,
                                              0, 0, 2])
        self.assertEqual(reward, 0.)
        self.assertEqual(done, False)

    @staticmethod
    def make_policy(actions):
        _idx = -1
        def policy(_G):
            nonlocal _idx
            _idx += 1
            return actions[_idx]
        return policy

    def test_step_shall_set_reward_and_done_if_episode_has_ended(self):
        self.sut.set_opponent_policy(TestGymEnv.make_policy([1,4]))
        _, reward, done, _ = self.sut.step(0)
        self.assertEqual(reward, 0.)
        self.assertEqual(done, False)
        _, reward, done, _ = self.sut.step(3)
        self.assertEqual(reward, 0.)
        self.assertEqual(done, False)
        state, reward, done, _ = self.sut.step(6)
        np.testing.assert_array_equal(state, [1, 2, 0,
                                              1, 2, 0,
                                              1, 0, 0])
        self.assertEqual(reward, 1)
        self.assertEqual(done, True)

    def test_step_shall_return_negative_reward_if_game_was_lost(self):
        self.sut.set_opponent_policy(TestGymEnv.make_policy([1,4,7]))
        self.sut.step(0)
        self.sut.step(3)
        state, reward, done, _ = self.sut.step(5)
        np.testing.assert_array_equal(state, [1, 2, 0,
                                              1, 2, 1,
                                              0, 2, 0])
        self.assertEqual(reward, -1)
        self.assertEqual(done, True)

    def test_step_shall_return_negative_reward_if_game_was_draw(self):
        self.sut.set_opponent_policy(TestGymEnv.make_policy([1,4,6,8]))
        self.sut.step(0)
        self.sut.step(2)
        self.sut.step(3)
        self.sut.step(5)
        state, reward, done, _ = self.sut.step(7)
        np.testing.assert_array_equal(state, [1, 2, 1,
                                              1, 2, 1,
                                              2, 1, 2])
        self.assertEqual(reward, -1)
        self.assertEqual(done, True)
