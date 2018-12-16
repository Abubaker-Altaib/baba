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
#   Brief Secret Report Wizard
#-----------------------------------------

class brief_secret_report_wizard(osv.osv_memory):
    _name = "brief.secret.report.wizard"

    def _selection_year(self, cr, uid, context=None):
        """
        Select year between 1970 and Current year.

        @return: list of years 
        """
        return [(str(years), years) for years in range(int(datetime.now().year) + 1, 1970, -1)]

    _columns = {
        'year': fields.selection(_selection_year, 'From Years'),
        'employee_ids': fields.many2many('hr.employee', 'employee_brief_secret_report_rel', 'employee_id', 'report_id', 'employees'),
    }

    def print_report(self, cr, uid, ids, context={}):

        data = {'form': self.read(cr, uid, ids, [])[0]}
        
        return {'type': 'ir.actions.report.xml', 'report_name': 'brief_secret_report', 'datas': data}
