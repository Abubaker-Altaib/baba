# -*- coding: utf-8 -*-
##############################################################################
#
# NCTR, Nile Center for Technology Research
# Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################
from openerp.osv import osv,fields

# ----------------------------------------------------
# Product Product inherit
# ----------------------------------------------------
class product_product(osv.osv):
    _inherit = "product.product"

    _sql_constraints = [
       	    ('code_uniq', 'unique(default_code)', 'Product Code "Vocab" must be unique !'),
    ]

#----------------------------------------------------------
# Products template (inherit)
#----------------------------------------------------------
class product_template(osv.osv):
    _inherit = "product.template"

    _defaults={
            'standard_price': 1
              }

    _sql_constraints = [
       	    ('name_uniq', 'unique(name)', 'Product name must be unique !'),
       	    ('price_positive', 'check(standard_price>0)', 'Product cost must be bigger than zero!'),
    ]

#----------------------------------------------------------
# Products Uom (inherit)
#----------------------------------------------------------
class product_uom(osv.osv):
    _inherit = "product.uom"

    _sql_constraints = [
       	    ('name_uniq', 'unique(name)', 'Product UOM name must be unique !'),
    ]

#----------------------------------------------------------
# Products Uom Category (inherit)
#----------------------------------------------------------
class product_uom_categ(osv.osv):
    _inherit = "product.uom.categ"

    _sql_constraints = [
       	    ('name_uniq', 'unique(name)', 'Unit of Measure Category name must be unique !'),
    ]

#----------------------------------------------------------
# Products Category (inherit)
#----------------------------------------------------------
class product_category(osv.osv):
    _inherit = "product.category"

    _sql_constraints = [
       	    ('name_uniq', 'unique(name)', 'Product Category name must be unique !'),
    ]



