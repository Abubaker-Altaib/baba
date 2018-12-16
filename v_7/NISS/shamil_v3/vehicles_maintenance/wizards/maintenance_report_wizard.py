# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2016-2017 NCTR (<http://www.nctr.sd>).
#
##############################################################################

from osv import fields, osv
import time
from tools.translate import _


class maintenance_report(osv.osv_memory):
    """ To manage maintenance report wizard """

    _name = "maintenance.report.wizard"

    _columns = {
        'state': fields.selection([('done', 'Done'), ('not_done', 'Not Done')], 'State'),
        'start_date': fields.datetime('Start Date'),
        'end_date': fields.datetime('End Date'),
        'departments_ids': fields.many2many('maintenance.department', 'maintenance_report_department_rel', 'maintenance_report_id', 'department_id', 'Departments'),
    }

    _defaults = {
        'start_date': time.strftime('%Y-%m-%d'),
        'end_date': time.strftime('%Y-%m-%d'),
    }

    def print_report(self, cr, uid, ids, context=None):
        """
        To print the report.

        @return: print the report
        """
        data = self.read(cr, uid, ids, [], context=context)[0]

        datas = {
            'ids': [],
            'model': 'maintenance.job',
            'form': data
        }
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'maintenance_report.report',
            'datas': datas,
        }
