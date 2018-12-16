# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2016-2017 NCTR (<http://www.nctr.sd>).
#
##############################################################################


from datetime import date,datetime
from openerp.osv import osv, fields
from openerp.tools.translate import _


class checks_wizard(osv.osv_memory):
    _name = "checks.report"

    _description = "Checks Report"

    _columns =  {
        'journal_type': fields.selection([('bank', 'Bank'), ('cash', 'Cash')], 'Journal Type', required=True),
    }

    def print_report(self, cr, uid, ids, context=None):
        data = self.read(cr, uid, ids, [], context=context)[0]
        datas = {
             'ids': [],
             'model': 'checks.report',
             'form': data
            }
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'account.delivered.check.ntc',
            'datas': datas,
            }

