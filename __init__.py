#The COPYRIGHT file at the top level of this repository contains the full
#copyright notices and license terms.

from trytond.pool import Pool
from request import *


def register():
    Pool.register(
        SupplyRequest,
        module='nutrition_program_fill_stock_request', type_='model')
