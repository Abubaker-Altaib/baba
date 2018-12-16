# -*- coding: utf-8 -*-
##############################################################################
#
# NCTR, Nile Center for Technology Research
# Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################
import time
from openerp.osv import osv,fields
from openerp import netsvc
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp


class product_category(osv.osv):
    _inherit = "product.category"
    _columns = {

        'co_operative' : fields.boolean('Cooperative?' , help="This Field determinate whether this category is a Cooperative or not"),
    }
    _sql_constraints = [

       ('product_category_name_uniq', 'unique(name)', 'Category name must be unique !'),


          ]



class stock_location(osv.osv):
    _inherit = "stock.location"
    _columns = {

        'co_operative' : fields.boolean('Cooperative?' , help="This Field determinate whether this location is a Cooperative or not"),
    }

    
    
    
