# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

from osv import fields, osv
import netsvc
import time
from datetime import datetime,date,timedelta
from tools.translate import _
import decimal_precision as dp
from admin_affairs.copy_attachments import copy_attachments as copy_attachments
from tools.amount_to_text_en import amount_to_text
from base_custom.amount_to_text_ar import amount_to_text as amount_to_text_ar
import logging

#----------------------------------------
# Class product inherit
#----------------------------------------
class product_product(osv.osv):
    _name="product.product"
    _description="product fleet enhancements"
    _inherit="product.product"
    _columns={
              'spare_ok': fields.boolean('Is a vehicle spare',change_default=False,help="Determines if the product is a vehicle spare."),
              }
    _defaults = {'spare_ok':lambda *a: False}
product_product()
