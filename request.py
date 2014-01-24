# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
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
        Product = pool.get('product.product')
        RequestLine = pool.get('stock.supply_request.line')
        Uom = pool.get('product.uom')

        for request in requests:
            days = request.days
            if not days:
                cls.raise_user_error('no_days', request.rec_name)

            wh_locations = Location.search([
                    ('parent', 'child_of',
                        request.to_warehouse.storage_location.id),
                    ])
            wh_locations_ids = [l.id for l in wh_locations]
            silos = Location.search([
                    ('silo', '=', True),
                    ('locations_to_fed', 'in', wh_locations_ids),
                    ], limit=1)
            if not silos:
                cls.raise_user_error('no_silo', request.to_warehouse.rec_name)

            quantity_by_product_and_silo = {}
            for silo in silos:
                silo_quantities = {}

                silo_locations_ids = list(set(wh_locations_ids) &
                    set([l.id for l in silo.locations_to_fed]))
                with Transaction().set_context(locations=silo_locations_ids):
                    lots_in_silo_locations = Lot.search([
                            ('quantity', '>', 0),
                            ('animal_type', '!=', None)
                            ])
                    for lot in lots_in_silo_locations:
                        animal = (lot.animal if lot.animal_type != 'group'
                            else lot.animal_group)
                        if (not animal.nutrition_program or
                                not animal.nutrition_program.bom):
                            continue

                        feed_product = animal.nutrition_program.product
                        feed_quantity = 0.0
                        for bom_line in animal.nutrition_program.bom.outputs:
                            if bom_line.product != feed_product:
                                continue
                            feed_quantity = Uom.compute_qty(bom_line.uom,
                                bom_line.quantity, feed_product.default_uom)
                            break
                        feed_quantity *= lot.quantity * days

                        if feed_quantity and feed_product in silo_quantities:
                            silo_quantities[feed_product] += feed_quantity
                        elif feed_quantity:
                            silo_quantities[feed_product] = feed_quantity
                if silo_quantities:
                    quantity_by_product_and_silo[silo] = silo_quantities

            if not quantity_by_product_and_silo:
                cls.raise_user_error('no_products_found',
                    request.to_warehouse.rec_name)

            RequestLine.delete(RequestLine.search([('request', '=', request)]))
            request.lines = []
            for silo in quantity_by_product_and_silo:
                for feed_product, quantity in (
                        quantity_by_product_and_silo[silo].iteritems()):
                    with Transaction().set_context(locations=[silo.id]):
                        quantity -= Product(feed_product.id).quantity
                    if quantity > 0.0:
                        line = RequestLine()
                        request.lines.append(line)
                        line.product = feed_product
                        line.quantity = Uom.round(quantity,
                            feed_product.default_uom.rounding)
                        line.to_location = silo
            request.save()
