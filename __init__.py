# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
from trytond.pool import Pool
from . import request


def register():
    Pool.register(
        request.SupplyRequest,
        module='farm_nutrition_program_supply_request', type_='model')
