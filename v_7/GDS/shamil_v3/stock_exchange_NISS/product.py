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
class product_template(osv.Model):
    _inherit = 'product.template'

    _columns = {
        'need_visit': fields.boolean('Need Visit', help="If this box is checked then the exchange order for this product must passes by committee before delivered."),
        'product_manager': fields.many2many('res.users', 'product_template_user','product_id','user_id', 'Product Manager'),
    }

    _defaults={
           'need_visit':0,
              }
