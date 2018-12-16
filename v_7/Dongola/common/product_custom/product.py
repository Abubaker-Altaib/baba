# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
############################################################################
from openerp.osv import osv

class product_template(osv.Model):

    _inherit = 'product.template'

    _defaults = {
        'sale_ok': 0,
    }
    _sql_constraints = [
        
        ('standard_price_positive', 'CHECK (standard_price >= 0)', 'Cost price of the product should positive value !')
    ]
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
