# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

from osv import fields,osv
import datetime


class internal_requestion(osv.osv):
    """
    Inherit purchase custom module to add fields related to requisition"""

    _inherit = "ireq.m"
    _columns = {
                'product_specialization': fields.selection([('admin', 'Administrative'),('technical','Technical')],'Specialization'),
}
