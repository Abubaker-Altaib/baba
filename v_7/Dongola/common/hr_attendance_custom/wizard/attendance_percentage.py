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


class attendance_percentage(osv.osv_memory):
    _name = "hr.attendance.percentage"

    _description = "Attendance Percentage"

    _columns = {
        'start_date':fields.date('Start Date'),
        'end_date': fields.date('End Date'),
        'department_ids':fields.many2many('hr.department',string='Departments'),
        'w_prob': fields.boolean('with problems'),
    }

    def _check_date(self, cr, uid, ids, context=None):
        """
        Check the value of start_date if greater than end_date or not.

        @return: Boolean of True or False
        """
        for act in self.browse(cr, uid, ids, context):
            if ((act.start_date > act.end_date) and act.end_date):
                raise osv.except_osv(_('ValidateError'), _("Start Date Must Be Less Than End Date"))
        return True
    
    _constraints = [
        (_check_date, _(''), ['start_date','end_date']),
    ]

    def print_report(self, cr, uid, ids, context=None):
        data = self.read(cr, uid, ids, [], context=context)[0]
        data['emp_ids'] = []
        datas = {
             'ids': [],
             'model': 'hr.attendance.percentage',
             'form': data
            }
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'attendance_percentage.report',
            'datas': datas,
            }
    
    def print_report_emp(self, cr, uid, ids, context=None):
        '''
        when select form employees view
        '''
        data = self.read(cr, uid, ids, [], context=context)[0]
        data['emp_ids'] = context.get('active_ids', [])
        datas = {
             'ids': [],
             'model': 'hr.attendance.percentage',
             'form': data
            }
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'attendance_percentage.report',
            'datas': datas,
            }

    def print_report_emp_details(self, cr, uid, ids, context=None):
        '''
        when select form employees view
        '''
        data = self.read(cr, uid, ids, [], context=context)[0]
        data['emp_ids'] = context.get('active_ids', [])
        datas = {
             'ids': [],
             'model': 'hr.attendance.percentage',
             'form': data
            }
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'attendance_details.report',
            'datas': datas,
            }
        
    def print_report_emp_details_all(self, cr, uid, ids, context=None):
        data = self.read(cr, uid, ids, [], context=context)[0]
        datas = {
             'ids': [],
             'model': 'hr.attendance.percentage',
             'form': data
            }
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'attendance_details_all.report',
            'datas': datas,
            }



class resource_calendar(osv.Model):
    _inherit = 'resource.calendar'

    _columns = {
        'min_hours':fields.float('Minimum Number of Hours'),
        'max_hours': fields.float('Maximum Number of Hours'),
        'factor': fields.float('Factor'),
        'employees_ids':fields.many2many('hr.employee', string='Employees', required=True),
        'working_hours':fields.float(string='Working Hours', required=True),
    }