# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from osv import osv, fields
from tools.translate import _
import time
class hr_expenses(osv.osv_memory):

    _name = 'hr.expenses'

    _columns = {
        'start_date': fields.date('Start Date',required=True),
        'end_date': fields.date('End Date ',required=True),
        'selection': fields.selection([('1', 'Additional Allowances'), ('2', 'Hierarchical Allowances'),('3', 'subsidization Allowances')], 'Selection',required=True),
        'company_ids': fields.many2many('res.company','expenses_comp_rel','expenses_id','company_id','Companies',required=True), 
        'payroll_ids': fields.many2many('hr.salary.scale','expenses_scale_rel','expenses_id','scale_id','Companies',required=True), 
        'department_ids': fields.many2many('hr.department','expenses_dept_rel','expenses_id','department_id','Departments',required=True), 
        #'allowance_id': fields.many2one('hr.allowance.deduction', 'Allowance', required=True ),  
        'allowance': fields.many2one('hr.allowance.deduction', 'Allowance', required=True ,domain="[('name_type','=','allow')]"), 
    }

    def _check_dates(self, cr, uid, ids, context=None):
        for missions in self.read(cr, uid, ids, ['start_date', 'end_date'], context=context):
             if missions['start_date'] and missions['end_date'] and missions['start_date'] > missions['end_date']:
                 return False
        return True

    _constraints = [ (_check_dates, 'Warning! Sorry  start-date must be lower then end-date.', ['start_date', 'end_date'])]

    def print_report(self, cr, uid, ids, data, context=None):
        wiz_data =self.read(cr, uid, ids[0], context={})
        datas = {
            'ids': [],
            'model':'hr.payroll.main.archive',
            'form':wiz_data
                }

        return {
                    'type': 'ir.actions.report.xml',
                    'report_name':'hr.expenses',
                    'datas':datas
                     }
 

hr_expenses()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
