# -*- coding: utf-8 -*-
##############################################################################
#
# NCTR, Nile Center for Technology Research
# Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################
from openerp.osv import osv,fields
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp


class product_product(osv.osv):
    _inherit = "product.product"
    _columns = {
        'product_qty' : fields.integer('Product Qty',),
        'installment' : fields.integer('Instalment', help="Determine the maximum allowed month for the sale loan payment"),
        'installment_value' : fields.integer('Instalment Value',),
        'installment_upfront' : fields.integer('Instalment Upfront',),
    }







