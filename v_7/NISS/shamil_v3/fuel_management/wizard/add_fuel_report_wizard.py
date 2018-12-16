# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2016-2017 NCTR (<http://www.nctr.sd>).
#
##############################################################################

from osv import osv, fields
from openerp.tools.translate import _
from lxml import etree
from openerp.osv.orm import setup_modifiers
import openerp.addons.decimal_precision as dp
import time
from datetime import datetime

#-----------------------------------------
#   Additional Fuel Report Wizard
#-----------------------------------------

class add_fuel_report_wizard(osv.osv_memory):
    _name = "add.fuel.report.wizard"

    _columns = {
        'type': fields.selection([('other','Other'),('permanent','Permanent'),('temporary','Temporary'),('moving','Moving'),('additional','Additional')],"Additional fuel Type",required=True),
        'start_date': fields.date(string="Start Date" ),
        'end_date': fields.date(string="End Date"),  
        'purpose_id': fields.many2one('additional.fuel.purpose', 'Fuel Purpose'),
        'state': fields.selection([('draft', 'Draft'), ('done', 'Done'),('approve','Approve'),('reapprove','Re-Approve'),('confirm','Confirm'),('cancel','Cancel')], 'State'),
    }

    def print_report(self, cr, uid, ids, context={}):

        data = {'form': self.read(cr, uid, ids, [])[0]}
        
        return {'type': 'ir.actions.report.xml', 'report_name': 'add_fuel_report', 'datas': data}
