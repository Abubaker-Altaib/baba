# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2016-2017 NCTR (<http://www.nctr.sd>).
#
##############################################################################

from osv import fields, osv
from tools.translate import _

class fuel_qty_line_wizard(osv.osv_memory):
    """ Fuel qty line wizard """

    _name = "fuel.qty.line.wizard"
    _description = "Fuel qty line wizard"

    _columns = {
        'qty': fields.integer('Quantity', size=32, required=True),
        'process': fields.selection([('delivery','Delivery'),('return', 'Return'),('transfer', 'Transfer')],'Process', required=True),
        'transfer_id': fields.many2one('fuel.qty.line', 'Fuel Quantity Line'),
    }

    def _check_quantitiy(self, cr, uid, ids, context=None):
        """
        Check the value of quantitiy and rise warning message.

        @return: Boolean True
        """
        for line in self.browse(cr, uid, ids, context=context):
            if line.qty <= 0 and line.process != 'transfer':
            	raise osv.except_osv(_('ValidateError'), _("Quantitiy Value Must Be Greater Than Zero!"))
        return True

    _constraints = [
        (_check_quantitiy, '', ['qty']),
    ]
    _defaults = {
	'process': 'delivery',
    }


    def Done(self, cr, uid, ids, context=None ):
        """
        To complete the process.

        @return: True
        """
	process = self.browse(cr, uid, ids[0], context=context).process

        log_obj = self.pool.get('fleet.vehicle.log.fuel')
        line_obj = self.pool.get('fuel.qty.line')
	line_ids = context.get('active_ids')
	sumQty = 0
	for line in line_obj.browse(cr, uid, line_ids, context=context):
		quantity = self.browse(cr, uid, ids[0], context=context).qty
		remaining_quantity = line.product_qty - line.spent_qty
		if process != "transfer" and quantity > line.product_qty:
			raise osv.except_osv(_('ValidateError'), _("Quantitiy Value Must Be Less Than Line Quantitiy!"))
		if quantity > remaining_quantity:
			raise osv.except_osv(_('ValidateError'), _("Quantitiy Value Must Be Less Than Remaining Quantitiy!"))
		if process == "return":
			quantity = quantity * -1
		if process == "transfer":
			transfer_pro_id = self.browse(cr, uid, ids[0], context=context).transfer_id.product_id or False
			transfer_id = self.browse(cr, uid, ids[0], context=context).transfer_id
			if transfer_pro_id != False and line.product_id.id == transfer_pro_id.id and remaining_quantity > 0:
				sumQty = sumQty + remaining_quantity
				quantity = remaining_quantity
			if remaining_quantity <= 0:
				raise osv.except_osv(_('ValidateError'), _("There Is Nothing To Transfer!"))
			else: quantity = 0
		if quantity !=0:
			data = {
				"liter": quantity,
				"amount": line.price_unit * quantity,
				"price_per_liter": line.price_unit,
				"vehicle_id": line.vehicles_id.id or False,
				"product_uom": line.product_uom.id,
				"plan_type": line.qty_id.plan_type,
				"payment_method": 'plan',
				"state": 'done',
				'qty_line_id':line.id ,
			}
			log_obj.create(cr, uid, data, context=context)
	if process == "transfer" and sumQty != 0:
		sumQty = sumQty * -1
		data = {
			"liter": sumQty,
			"amount": transfer_id.price_unit * sumQty,
			"price_per_liter": transfer_id.price_unit,
			"vehicle_id": transfer_id.vehicles_id.id or False,
			"product_uom": transfer_id.product_uom.id,
			"plan_type": transfer_id.qty_id.plan_type,
			"payment_method": 'plan',
			"state": 'done',
			'qty_line_id':line.id ,
		}
		log_obj.create(cr, uid, data, context=context)

	return True

