# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
from trytond.pool import Pool
from request import *


def register():
    Pool.register(
        SupplyRequest,
        module='farm_nutrition_program_supply_request', type_='model')
