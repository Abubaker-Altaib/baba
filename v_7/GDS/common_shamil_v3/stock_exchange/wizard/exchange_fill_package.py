from openerp.osv import fields, osv, orm
from openerp.tools.translate import _

class stock_fill_package(osv.osv_memory):
    _name = "stock.fill.package"
    _description = "Import package"
    _columns = {
        'package_id': fields.many2one('stock.pakage', 'pakage', required=True),
        'package_qty': fields.integer("Product Qty", required=True,help="If checked, products contained in child packages of selected package will be included as well."),

    }
    _defaults = {
        'package_qty':1,
    }


    def view_init(self, cr, uid, fields_list, context=None):

        if context is None:
            context = {}
        super(stock_fill_package, self).view_init(cr, uid, fields_list, context=context)

        if len(context.get('active_ids',[])) > 1:
            raise osv.except_osv(_('Error!'), _('You cannot perform this operation on more than one Stock exchange.'))

        if context.get('active_id', False):
            stock = self.pool.get('exchange.order').browse(cr, uid, context.get('active_id', False))
        return True

    def fill_package(self, cr, uid, ids, context=None):

        if context is None:
            context = {}
        order_line_obj = self.pool.get('exchange.order.line')
        package_obj = self.pool.get('stock.package')
        if ids and len(ids):
            ids = ids[0]
        else:
             return {'type': 'ir.actions.act_window_close'}
        exchange_order_line={}
        fill_package = self.browse(cr, uid, ids, context=context)
        for line in fill_package.package_id.package_line:
            exchange_order_line = { 'order_id': context['active_ids'][0],
                                    'product_id': line.product_id.id,
                                    'name': line.product_id.name,
                                    'product_qty': line.product_qty * fill_package.package_qty, }
            
            order_line_obj.create(cr, uid, exchange_order_line, context=context)
        return {'type': 'ir.actions.act_window_close'}

stock_fill_package()

