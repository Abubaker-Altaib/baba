# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2016-2017 NCTR (<http://www.nctr.sd>).
#
##############################################################################

from osv import fields,osv
from tools.translate import _

#----------------------------------------
# Class product inherit
#----------------------------------------

class product_product(osv.osv):
    """
    To manage fuel products
    """
    def _check_unique_insesitive(self, cr, uid, ids, context=None):
        """ 
        Check uniqueness of product name.

        @return: Boolean of True or False
        """
        name = self.browse(cr, uid, ids[0], context=context).name
        if len(self.search(cr, uid, [('name','=ilike',name)],  context=context)) > 1:
            raise osv.except_osv(_('Constraint Error'), _("The Name Must Be Unique!"))
        return True

    def _check_cost(self, cr, uid, ids, context=None):
        """ 
        Check the value of product standard price,
        if greater than zero or not.

        @return: Boolean of True or False
        """
        count = 0
        for product in self.browse(cr, uid, ids, context=context):
            if (product.standard_price <= 0):
                message = _("The Cost Must Be Greater Than Zero!")
                count += 1
        if count > 0 :
            raise osv.except_osv(_('ValidateError'), _(message))
        return True

    _inherit = "product.product"

    _columns = {
        'fuel_ok': fields.boolean('Fuel Product', help="Determine This Product Is Fuel"),
        'fuel_type': fields.selection([('gasoline','Gasoline'),('diesel', 'Diesel'),('electric', 'Electric'), ('hybrid', 'Hybrid')],'Fuel type') ,       
    }

    _constraints = [
        (_check_cost, '', ['']),
        (_check_unique_insesitive, '', [''])
    ]

