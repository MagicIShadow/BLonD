# coding: utf8
# Copyright 2014-2017 CERN. This software is distributed under the
# terms of the GNU General Public Licence version 3 (GPL Version 3),
# copied verbatim in the file LICENCE.md.
# In applying this licence, CERN does not waive the privileges and immunities
# granted to it by virtue of its status as an Intergovernmental Organization or
# submit itself to any jurisdiction.
# Project website: http://blond.web.cern.ch/

"""
Unit-test for general_parameters.py
:Authors: **Markus Schwarz**, **Alexandre Lasheen**
"""


import sys
import math
import unittest
import numpy as np

from input_parameters.ring import Ring
from beam.beam import Electron


class TestGeneralParameters(unittest.TestCase):

    # Initialization ----------------------------------------------------------

    def setUp(self):

        self.n_turns = 10
        self.C = [13000, 13659]
        self.num_sections = 2
        self.alpha_0 = [[3.21e-4], [2.89e-4]]
        self.alpha_1 = [[2.e-5], [1.e-5]]
        self.alpha_2 = [[5.e-7], [5.e-7]]
        self.alpha_order = 2
        self.momentum = [450e9*(np.ones(self.n_turns+1)),
                         450e9*(np.ones(self.n_turns+1))]
        self.particle = Electron()

        if int(sys.version[0]) == 2:
            self.assertRaisesRegex = self.assertRaisesRegexp

    def assertIsNaN(self, value, msg=None):
        """
        Fail if provided value is not NaN
        """

        standardMsg = "%s is not NaN" % str(value)

        if not np.isnan(value):
            self.fail(self._formatMessage(msg, standardMsg))

    # Exception raising test --------------------------------------------------

    def test_ring_length_exception(self):
        # Test if 'ring length size' RuntimeError gets thrown for wrong number
        # of rf sections
        num_sections = 1    # only one rf-section!

        with self.assertRaisesRegex(
                RuntimeError, 'ERROR in Ring: Number of sections and ring ' +
                'length size do not match!',
                msg='No RuntimeError for wrong n_sections!'):

            Ring(self.n_turns, self.C, self.alpha_0, self.momentum,
                 self.particle, n_sections=num_sections,
                 alpha_order=self.alpha_order, alpha_1=self.alpha_1,
                 alpha_2=self.alpha_2)

    def test_alpha_shape_exception(self):
        # Test if 'momentum compaction' RuntimeError gets thrown for wrong
        # shape of alpha
        alpha = [[3.21e-4, 2.e-5, 5.e-7]]   # only one array!

        with self.assertRaisesRegex(
                RuntimeError, 'ERROR in Ring: Number of sections and size ' +
                'of momentum compaction do not match!',
                msg='No RuntimeError for wrong shape of alpha!'):

            Ring(self.n_turns, self.C, alpha, self.momentum, self.particle,
                 n_sections=self.num_sections)

    def test_synchronous_data_exception(self):
        # What to do when user wants momentum programme for multiple sections?
        # One array of cycle_time? One array per section?
        # Currently, __init__ checks only if the number of cycle_time arrays is
        # the same as the number of momentum_arrays, but not if the array
        # have the correct length.

        cycle_time = np.linspace(0, 1, self.n_turns)  # wrong length

        with self.assertRaisesRegex(
                RuntimeError, "ERROR in Ring: synchronous data does " +
                "not match the time data",
                msg='No RuntimeError for wrong synchronous_data!'):

            Ring(self.n_turns, self.C, self.alpha_0,
                 ([cycle_time, cycle_time], self.momentum),
                 self.particle, n_sections=self.num_sections)

    def test_momentum_shape_exception(self):
        # Test if RuntimeError gets thrown for wrong shape of momentum

        cycle_time = np.linspace(0, 1, self.n_turns)
        momentum = 450e9  # only one momentum!

        with self.assertRaisesRegex(
                RuntimeError, "ERROR in Ring: synchronous data does " +
                "not match the time data",
                msg='No RuntimeError for wrong shape of momentum!'):

            Ring(self.n_turns, self.C, self.alpha_0, (cycle_time, momentum),
                 self.particle, n_sections=self.num_sections)

    def test_momentum_length_exception(self):
        # Test if RuntimeError gets thrown for wrong length of momentum
        # Only n_turns elements per section!

        momentum = np.linspace(450e9, 450e9, self.n_turns)

        with self.assertRaisesRegex(
                RuntimeError, 'ERROR in Ring: The momentum program does ' +
                'not match the proper length \(n_turns\+1\)',
                msg='No RuntimeError for wrong length of momentum array!'):

            Ring(self.n_turns, self.C, self.alpha_0, momentum,
                 self.particle, n_sections=self.num_sections)

    # Other tests -------------------------------------------------------------

    def test_kinetic_energy_positive(self):
        # Kinetic energy must be greater or equal 0 for all turns
        general_parameters = Ring(self.n_turns, self.C,
                                  self.alpha_0, self.momentum, self.particle,
                                  n_sections=self.num_sections)

        self.assertTrue((general_parameters.kin_energy >= 0.0).all(),
                        msg='In TestGeneralParameters kinetic energy is ' +
                        'negative!')

    def test_cycle_time_turn1(self):
        # Cycle_time[0] must be equal to t_rev[0]
        general_parameters = Ring(self.n_turns, self.C,
                                  self.alpha_0, self.momentum, self.particle,
                                  n_sections=self.num_sections)

        self.assertEqual(general_parameters.cycle_time[0],
                         general_parameters.t_rev[0],
                         msg='In TestGeneralParameters cycle_time at first ' +
                         'turn not equal to revolution time at first turn!')

    def test_convert_data_exception(self):
        with self.assertRaisesRegex(
                RuntimeError,
                'ERROR in Ring: Synchronous data type not recognized!',
                msg='No RuntimeError for wrong synchronous data type!'):

            general_parameters = Ring(self.n_turns, self.C,
                                      self.alpha_0, self.momentum,
                                      self.particle,
                                      n_sections=self.num_sections)

            general_parameters.convert_data(
                25e9,
                synchronous_data_type='somethingCompletelyDifferent')

    def test_convert_data_value_rest_mass(self):

        general_parameters = Ring(self.n_turns, self.C,
                                  self.alpha_0, self.momentum, self.particle,
                                  n_sections=self.num_sections)

        self.assertEqual(general_parameters.convert_data(
                            Electron().mass,
                            synchronous_data_type='total energy'),
                         0.0,
                         msg='Momentum not zero for total engery equal rest ' +
                         'mass!')

    def test_convert_data_wrong_total_energy(self):
        # use energy 25 instead of 25e9

        general_parameters = Ring(self.n_turns, self.C,
                                  self.alpha_0, self.momentum, self.particle,
                                  n_sections=self.num_sections)

        self.assertIsNaN(general_parameters.convert_data(
                            25,
                            synchronous_data_type='total energy'),
                         msg='No NaN for total energy less than rest mass!')

    def test_convert_data_wrong_kinetic_energy(self):
        # use negative kinetic energy

        general_parameters = Ring(self.n_turns, self.C,
                                  self.alpha_0, self.momentum, self.particle,
                                  n_sections=self.num_sections)

        self.assertIsNaN(general_parameters.convert_data(
                            -25,
                            synchronous_data_type='kinetic energy'),
                         msg='No NaN for total energy less than rest mass!')


if __name__ == '__main__':

    unittest.main()
