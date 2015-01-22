# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
import unittest

import trytond.tests.test_tryton
from trytond.tests.test_tryton import test_view, test_depends


class TestCase(unittest.TestCase):
    '''
    Test module.
    '''

    def setUp(self):
        trytond.tests.test_tryton.install_module(
            'farm_nutrition_program_supply_request')

    def test0005views(self):
        '''
        Test views.
        '''
        test_view('farm_nutrition_program_supply_request')

    def test0006depends(self):
        '''
        Test depends.
        '''
        test_depends()


def suite():
    suite = trytond.tests.test_tryton.suite()
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestCase))
    return suite
