# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2016-2017 NCTR (<http://www.nctr.sd>).
#
##############################################################################


from osv import fields, osv
import time
from datetime import datetime, date, timedelta
from tools.translate import _


class solidarity_report_wiz(osv.osv_memory):
    """ To manage solidarity box requests report wizard """
    _name = "solidarity.report.wiz"

    _description = "Solidarity Box Requests Report Wizard"

    _columns = {
        'date_from': fields.date('Date From'), 
        'date_to': fields.date('Date To'),
        'employees_ids':fields.many2many('hr.employee',string='Departments'),
        'categories_ids':fields.many2many('enrich.category',string='Enrich Categories'),
    }

    _defaults = {
    }

    def print_report(self, cr, uid, ids, context=None):
        """
        To print the report.

        @return: print the report
        """
        data = self.read(cr, uid, ids, [], context=context)[0]
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'solidarity_report.report',
            'datas': {
                'ids': ids,
                'model': 'payment.enrich',
                'form': data,
                'context':context
            },
        }
