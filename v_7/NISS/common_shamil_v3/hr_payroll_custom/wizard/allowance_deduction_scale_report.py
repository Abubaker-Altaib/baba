# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################
import time
from datetime import datetime
from openerp.osv import fields, osv
from openerp.tools.translate import _
#----------------------------------------
#hr_allowance_deduction_report
#----------------------------------------
class hr_allowance_deduction_report(osv.osv_memory):
    _name ='hr.allowance.deduction.scale.report'

    def _get_months(self, cr, uid, context):
        months=[(n,n) for n in range(1,13)]
        return months

    _columns = {
        #'company_id': fields.many2many('res.company','hr_report_company_rel','report_id','company_id','Company',required=True),
        'payroll_ids': fields.many2one('hr.salary.scale','Salary Scale',required= True),
        #'allow_deduct_ids': fields.many2many('hr.allowance.deduction','allow_deduct_rel','report_id','allow_deduct_id', 'Allowances/Deductions'),
        #'employee_ids': fields.many2many('hr.employee','report_employee_rel','report_id','employ_id',"Employees"),
        #'month' :fields.selection(_get_months,"Month", required= True),
	#    'year' :fields.integer("Year", required= True),
        'type':fields.selection([('allow','Allowance'),('deduct','Deductions')],"Type"),
        #'by':fields.selection([('allow','Allowances/Deductions'),('employee','Employee')],"By",required=True),
        #'pay_sheet':fields.selection([('first', 'First Pay Sheet'), 
        #                              ('second', 'Second Pay Sheet')],'Pay Sheet'),
        'in_salary_sheet' : fields.boolean('In Salary Sheet'),
        #'display':fields.selection([('detail','Detail'),('total','Total')],"Display" ,required=True),
        #'landscape' : fields.boolean('Landscape'),
        #'department_cat_id' : fields.many2one('hr.department.cat','Department Category') ,
        #'department_ids' : fields.many2many('hr.department' , 'hr_report_deps_rel') ,
        #'order_by' : fields.selection([('degree' , 'Degree') , ('code' , 'Emploee Code') , ('name' , 'Name')],string='Order By')
    }
    def _get_companies(self, cr, uid, context=None): 
   
        return [self.pool.get('res.users').browse(cr,uid,uid).company_id.id]

    _defaults = {
        #'year': int(time.strftime('%Y')),
        #'month': int(time.strftime('%m')),
        #'display':'detail',
        #'company_id': _get_companies,
        'in_salary_sheet' :1,
        'type':'allow',
        #'order_by' : 'degree' ,
    }

    def print_report(self, cr, uid, ids, context=None):
        datas = {}
        if context is None:
            context = {}
        data = self.read(cr, uid, ids)[0]
        for rec in self.browse(cr, uid, ids):
            data['payroll_ids']=rec.payroll_ids.id
            company_name = rec.payroll_ids.name
        data['company_name']  = company_name
        print ">>>>>>>>>>>>>>>>>>",data['payroll_ids']
        data['type_name'] = 'الإستحقاقات\الخصومات'
        if data['type'] == 'allow':
            data['type_name'] = 'اﻹستحقاقات'
        if data['type'] == 'deduct':
            data['type_name'] = 'الإستقطاعات'

        datas = {
             'ids': context.get('active_ids', []),
             'model': 'hr.allowance.deduction.archive',
             'form': data
        }
        return {
		        'type': 'ir.actions.report.xml',
		        'report_name': 'allowance.deduction.scale.landscape',
		        'datas': datas,
		    }
     
