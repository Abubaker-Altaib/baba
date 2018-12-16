# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#

############################################################################
import time
from openerp.osv import fields, osv, orm
from openerp import netsvc
from openerp.tools.translate import _
import datetime


class hr_employee(osv.Model):

    _inherit = ["hr.employee",'mail.thread', 'ir.needaction_mixin']
    _name = "hr.employee"
    _columns = {
        'state':fields.selection([('draft', 'Draft'), ('experiment', 'In Experiment'), 
                             ('approved', 'In Service'), ('suspend', 'suspend'), 
                             ('refuse', 'Out of Service')] , "State", track_visibility='onchange', readonly=True), 
    }