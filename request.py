#The COPYRIGHT file at the top level of this repository contains the full
#copyright notices and license terms.
from trytond.model import ModelView, fields
from trytond.pool import Pool, PoolMeta
from trytond.transaction import Transaction
from trytond.pyson import Eval, Not, Equal
from trytond.modules.stock_supply_request.supply_request import _STATES, \
    _DEPENDS

__all__ = ['SupplyRequest']

__metaclass__ = PoolMeta


class SupplyRequest:
    __name__ = 'stock.supply_request'

    days = fields.Integer('Days', states=_STATES, depends=_DEPENDS)

    @classmethod
    def __setup__(cls):
        super(SupplyRequest, cls).__setup__()
        cls._error_messages.update({
                'from_location': 'A default from location must be defined',
                'no_silo': 'No silo defined for location "%s"',
                'no_days': 'Request "%s" has no days defined. Days are needed'
                ' to fill request automatically',
                'no_products_found': 'No feed products had been found for '
                    'location "%s"',
                })
        cls._buttons.update({
                'fill_request': {
                    'readonly': Not(Equal(Eval('state'), 'draft'))
                }
            })

    @classmethod
    @ModelView.button
    def fill_request(cls, requests):
        pool = Pool()
        Location = pool.get('stock.location')
        Lot = pool.get('stock.lot')
        Uom = pool.get('product.uom')
        RequestLine = pool.get('stock.supply_request.line')

        for request in requests:
            location = request.to_warehouse
            days = request.days

            if not days:
                cls.raise_user_error('no_days', request.rec_name)

            locations = Location.search([('parent', 'child_of', location.id)])
            locations = [l.id for l in locations]
            try:
                silo, = Location.search([
                        ('locations_to_fed', 'in', locations),
                        ('silo', '=', True),
                    ], limit=1)
            except ValueError:
                cls.raise_user_error('no_silo', location.rec_name)

            products_quantity = {}
            with Transaction().set_context(locations=locations):
                lots_in_warehouse = Lot.search([('quantity', '>', 0)])
                for lot in lots_in_warehouse:
                    if not lot.nutrition_program or \
                            not lot.nutrition_program.bom:
                        continue
                    for bom_line in lot.nutrition_program.bom.inputs:
                        product = bom_line.product
                        quantity = Uom.compute_qty(bom_line.uom,
                            bom_line.quantity, product.default_uom)
                        if product in products_quantity:
                            products_quantity[product] += quantity
                        else:
                            products_quantity[product] = quantity
            if len(products_quantity) == 0:
                cls.raise_user_error('no_products_found', location.rec_name)

            RequestLine.delete(RequestLine.search([('request', '=', request)]))
            request.lines = []
            for product, quantity in products_quantity.iteritems():
                line = RequestLine()
                request.lines.append(line)
                line.product = product
                line.quantity = Uom.round(quantity * days,
                    product.default_uom.rounding)
                line.to_location = silo
            request.save()
