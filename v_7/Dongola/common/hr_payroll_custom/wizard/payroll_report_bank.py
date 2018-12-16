# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2016-2017 NCTR (<http://www.nctr.sd>).
#
##############################################################################

import pooler
import time
from datetime import datetime
from dateutil import relativedelta
from openerp.osv import fields, osv

from openerp.osv import fields, osv, orm



class payroll_report_bank(osv.osv_memory):
    
    _name ='payroll.report.bank'


    _columns = {
        #'company_id': fields.many2one('res.company', string='Company', required=True),
        'company_id': fields.many2many('res.company','hr_report_company_rel_report','report_id','company_id','Company',required=True),
        'bank_id': fields.many2many('res.bank','hr_report_bank_rel_report','report_id','bank_id' ,string='Bank'),
        'payroll_ids': fields.many2many('hr.salary.scale', 'hr_report_payroll_rel_bank','pay_bonus','pay_id','Salary Scale'),
        'month' :fields.selection([(1, '1'), (2, ' 2'), (3, '3'), (4, '4'), (5, '5'), (6, '6'),
                                   (7, '7'), (8, '8'), (9, '9'), (10, '10'), (11, '11'), (12, '12')],
                                    'Month', required=True),
        'year' :fields.integer('Year', required=True),
        'type' :fields.selection([('1', 'Payroll'), ('2', 'Bouns')],
                                    'Type', required=True),
        'bonus_date' :fields.date("Bonus Date"),
        'allow': fields.many2one('hr.allowance.deduction','allowance'),
        'no_bank' : fields.boolean('Include Employees without Bank Accounts')
        #'allow_deduct_ids': fields.many2many('hr.allowance.deduction','allow_deduct_rel_bank','report_id','allow_deduct_id', 'Allowances/Deductions'),
        #'bonus_date' :fields.date('Bouns Date'),
        #'in_salary_sheet' : fields.boolean('In Salary Sheet'),
        #'allow_deduct_ids': fields.many2many('hr.allowance.deduction','allow_deduct_rel','report_id','allow_deduct_id', 'Allowances/Deductions'),
    }

    def _get_companies(self, cr, uid, context=None): 
        print "--------------------------------------_get_companies", self.pool.get('res.users').browse(cr,uid,uid).company_id.id
        return [self.pool.get('res.users').browse(cr,uid,uid).company_id.id]

    _defaults ={
        'year': int(time.strftime('%Y')),
        'type': '1',
        'company_id': _get_companies,
        'month': int(time.strftime('%m')),
    }

    def onchange_data(self,cr,uid,ids,company_id,payroll_ids,ttype,in_salary_sheet,pay_sheet):
        domain=value={}
        '''emp_domain= [('company_id','in',company_id[0][2]),('state','not in',('draft','refuse'))]
        if payroll_ids and payroll_ids[0][2]:
            emp_domain.append(('payroll_id','in',payroll_ids[0][2]))
            value['employee_ids']=[]
        domain['employee_ids']= emp_domain'''
        
        '''allow_domain= [('company_id','in',company_id[0][2]+[False]),('in_salary_sheet','=',in_salary_sheet)]
        if ttype:
            allow_domain.append(('name_type','=',ttype))'''
        '''if pay_sheet:
           allow_domain.append(('pay_sheet','=',pay_sheet))'''
        '''if not in_salary_sheet:
            allow_domain += [('allowance_type','=','general'),('allowance_type','!=','in_cycle'),('special','=', False)]
        domain['allow_deduct_ids']=allow_domain'''
        return {'domain':domain}

    def xls_export(self, cr, uid, ids, context=None):
        return self.print_report(cr, uid, ids, context=context)

    def print_report(self, cr, uid, ids, context={}):
        
        datas = {}
        if context is None:
            context = {}
        data = self.read(cr, uid, ids)[0]
        if not data['bank_id']:
           raise osv.except_osv(('ERROR'), ('Please Choose Bank'))
        datas = {
             'ids': context.get('active_ids', []),
             'model': 'hr.payroll.main.archive',
             'form': data
             }
        if context.get('xls_export'):
                return {'type': 'ir.actions.report.xml',
                        'report_name': 'payroll.report.bank.xls',
                        'datas': data}
        else:
            return{
                'type': 'ir.actions.report.xml',
                'report_name': 'payroll.report.bank',
                'datas': datas,
                        }
         
