# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

from osv import fields, osv
import time
from tools.translate import _


class mission_state_wizard_report(osv.osv_memory):
    _name = "mission_state_wizard.report"

    _columns = {
        'start_date' :fields.date("Start Date", required=True),
        'end_date' :fields.date("End Date", required=True),
        'state': fields.selection( [('open', 'Opened'),('close', 'Closed'),('pending', 'Pending'),('illness','Illness Details')], 'State',required=True),
    }

    def print_report(self, cr, uid, ids, context={}):

        datas = {}
        if context is None:
            context = {}
        data = self.read(cr, uid, ids)[0]
        datas = {
             'ids': [],
             'model': 'hr.employee.mission',
             'form': data
                }
        print">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>"
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'mission_state_wizard.report',
            'datas': datas,
            }