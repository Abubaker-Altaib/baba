# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################
import time
from openerp.osv import fields, osv
from openerp.tools.translate import _

class employees_salary_report(osv.osv_memory):
    _name = "employees.salary.report"

    def _get_months(sel, cr, uid, context):
       months=[(n,n) for n in range(1,13)]
       return months

    _columns = {
	    'month': fields.selection(_get_months,'Month', required=True),
	    'year': fields.integer('year',required=True ),
		}

    _defaults = {
        'year': int(time.strftime('%Y')),
        'month': int(time.strftime('%m')),
		}


    def print_report(self, cr, uid, ids, context=None):
        datas = {}
        if context is None:
            context = {}
        data = self.read(cr, uid, ids)[0]
        main_archive_obj=self.pool.get('hr.payroll.main.archive')
        addendum_archive_obj=self.pool.get('hr.employee.salary.addendum')
        main_arch_ids= main_archive_obj.search(cr, uid,[('employee_id', '=',context['employee_id']),
                                                                  ('month', '=', data['month']),
                                                                  ('year', '=', data['year']),('in_salary_sheet', '=',True)])
        
        rec = main_arch_ids and main_archive_obj.browse(cr,uid,main_arch_ids[len(main_arch_ids)-1]).arch_id or False
        
        '''if not main_arch_ids or (main_arch_ids and rec.state != 'transferred') :
            raise osv.except_osv(_('Error'), _('No Data Found For This Month...'))'''
	if not main_arch_ids:
            raise osv.except_osv(_('Error'), _('No Data Found For This Month...'))
        datas = {
             'ids': context.get('active_ids', []),
             'model': 'hr.employee',
             'form': data
                }
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'employees.salary',
            'datas': datas,
            }
 
