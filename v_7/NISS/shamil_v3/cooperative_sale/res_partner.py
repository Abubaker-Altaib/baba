# -*- coding: utf-8 -*-
##############################################################################
#
# NCTR, Nile Center for Technology Research
# Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################
from openerp.osv import osv,fields
import time
from datetime import datetime,timedelta,date
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp
import netsvc




class res_partner(osv.Model):
      _inherit = "res.partner"
      _columns = {

                #'partner_sales_ids' : fields.one2many('sales.partners.products' , 'parner_id' , 'Products' ),
               'sum_product_qty' : fields.integer('Sell Sum Qty' ,default = 0),


                 }

