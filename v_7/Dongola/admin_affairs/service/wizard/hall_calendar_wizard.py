# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2016-2017 NCTR (<http://www.nctr.sd>).
#
##############################################################################


from openerp.osv import osv, fields
import time
from datetime import datetime
# Service Report Class

class hall_calendar_wiz(osv.osv_memory):
    """ To manage hall calendar reports """
    _name = "hall.calendar.wiz"

    _description = "Service Report"

    _columns = {
        'date':fields.date('Date'), 
        'date_to':fields.date('Date to'), 
        'late_form':fields.boolean('Late Form'), 
        'department':fields.many2one('hr.department', 'Department'),
        'user':fields.many2one('res.users', 'user'),
        'halls_ids':fields.many2many('fleet.service.type', string='Halls')
    }

    _defaults = {
        'user': lambda self, cr, uid, context: uid,
    }

    def print_report(self, cr, uid, ids, context=None):
        """ 
        Print report.

        @return: Dictionary of print attributes
        """
        data = self.read(cr, uid, ids, [], context=context)[0]
        
        datas = {
             'ids': [],
             'model': 'service.hall_availability',
             'form': data,
            }
        if data['late_form']:
            return {
            'type': 'ir.actions.report.xml',
            'report_name': 'hall_availability_late.report',
            'datas': datas,
            }

        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'hall_availability.report',
            'datas': datas,
            }

