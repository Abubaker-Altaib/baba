# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2016-2017 NCTR (<http://www.nctr.sd>).
#
##############################################################################

from osv import osv, fields
from tools.translate import _
import sys


class fleet_vehicle(osv.osv):
    """ 
    To manage operation of fleet vehicle
    """

    def get_uom_domin(self, cr, uid, ids, pro_id, context=None):
        """ 
        On change product id field value function gets the domin of Product uom.

        @param pro_id: id of current product
        @return: Dictionary of product_uom default value with product_uom domin
        """
	res = {}
	try:
		pro_cat = self.pool.get('product.product').browse(cr, uid, pro_id, context=context).uom_id
		res = {
		    'value': {
		        'product_uom': pro_cat.id,
			'product_uom': False,
		    },
		    'domain':{
		        'product_uom': [('category_id','=',pro_cat.category_id.id)],
		    }
		}
		untrusted.execute()
	except:
		e = sys.exc_info()[0]
        return res

    def reset_id(self, cr, uid, ids, context=None):
        """ 
        On change fuel type field value function rest product id value.

        @return: Dictionary of product_id new value
        """
        return {'value': {
			'product_id': False,
			'product_uom': False,
			}
		}

    def _check_negative(self, cr, uid, ids, context=None):
        """ 
        Check the value of fuel tank capacity and quantity,
        if greater than zero or not.

        @return: Boolean of True or False
        """
        count = 0
        for fuel in self.browse(cr, uid, ids, context=context):
            message = _("The Value Of ")
            if (fuel.fueltankcap <= 0):
                message += _("Tank Capacity")
                count += 1
            if fuel.monthly_plan == True:
                if (fuel.product_qty <= 0):
                    if (count > 0):
                        message += _(" And ")
                    message += _("Fuel Quantity")
                    count += 1
            message += _(" Must Be Greater Than Zero!")
        if count > 0 :
            raise osv.except_osv(_('ValidateError'), _(message)) 
        return True

    _inherit = "fleet.vehicle"

    _columns = { 
        'monthly_plan':fields.boolean('Monthly Plan',),
        'fueltankcap':fields.float('Tank Capacity', states={'confirm':[('readonly',True)]},
                                    help="The unit of measurement Of Tank Capacity depends on the measuring unit of Car fuel"),
        'product_id': fields.many2one('product.product','Fuel', states={'confirm':[('readonly',True)]}),
        'product_qty': fields.float('Fuel Quantity',),
        'product_uom': fields.many2one('product.uom', 'Unit of Measure', states={'confirm':[('readonly',True)]}),
        'fuel_plan_ids':fields.one2many('fuel.qty.line','vehicles_id', string='Fuel Plans',
                          readonly=True),
    }

    _constraints = [
        (_check_negative, '', ['fueltankcap','product_qty','monthly_plan']),
    ]

