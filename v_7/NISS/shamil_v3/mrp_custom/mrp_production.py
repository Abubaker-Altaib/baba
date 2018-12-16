# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

from openerp.osv import fields, osv, orm
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp
import time
import netsvc


class mrp_workcenter(osv.osv):
    """
    To manage mrp Workcenter inherit """

    _inherit = "mrp.workcenter"
    _columns={
           'product_id_move': fields.many2one('product.product', 'Move product', required=True),
            }
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
