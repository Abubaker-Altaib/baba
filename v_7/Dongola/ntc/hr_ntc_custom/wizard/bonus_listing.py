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
from tools.translate import _
from openerp.osv import fields, osv, orm



class payroll_report_bank(osv.osv_memory):
    
    _name ='bonus.listing'


    _columns = {
        'company_id': fields.many2one('res.company','Company',required=True),
        'month' :fields.selection([(1, '1'), (2, ' 2'), (3, '3'), (4, '4'), (5, '5'), (6, '6'),
                                   (7, '7'), (8, '8'), (9, '9'), (10, '10'), (11, '11'), (12, '12')],
                                    'Month', required=True),
        'year' :fields.integer('Year', required=True),
        'bonus_date' :fields.date("Bonus Date", required=True),
        'allow': fields.many2one('hr.allowance.deduction','allowance',required=True),
       
    }
    

    def _get_companies(self, cr, uid, context=None): 
        return [self.pool.get('res.users').browse(cr,uid,uid).company_id.id]

    _defaults ={
        'year': int(time.strftime('%Y')),
        'company_id': _get_companies,
        'month': int(time.strftime('%m')),
    }


    def print_report(self, cr, uid, ids, context={}):
        
        datas = {}
        if context is None:
            context = {}
        data = self.read(cr, uid, ids)[0]
        datas = {
             'ids': context.get('active_ids', []),
             'model': 'hr.payroll.main.archive',
             'form': data
             }
        salary_obj = self.pool.get('hr.salary.scale')
        
        
        company= data['company_id'][0]

        payroll_ids= salary_obj.search(cr, uid, [],context=context)
        cr.execute(
            'SELECT emp.id, emp.name_related AS name, '\
            'pay.total_allowance AS total_allowance,pay.total_deduction AS total_deduction,pay.total_loans AS total_loans,'\
            'pay.allowances_tax AS allowances_tax,pay.tax AS tax,pay.zakat AS zakat,'\
            'pay.net AS net, adr.imprint AS imprint ,pay.id AS pay_id '\
            'FROM hr_payroll_main_archive  pay '\
            'LEFT JOIN hr_employee  emp ON (pay.employee_id = emp.id) '\
            'LEFT JOIN hr_salary_degree deg on (deg.id= emp.degree_id)'\
            'LEFT JOIN hr_allowance_deduction_archive adr ON (adr.main_arch_id=pay.id)' \
            'WHERE pay.month  =%s'\
            'AND pay.year=%s ' \
            'AND adr.allow_deduct_id = %s '\
            'AND pay.salary_date=%s ' \
            'AND pay.company_id = %s '\
            'AND pay.scale_id in %s '\
            'AND adr.type = %s '\
            'AND pay.in_salary_sheet = False '\
	        'group by emp.id,pay.total_allowance ,pay.total_deduction,pay.allowances_tax,pay.tax,pay.zakat,pay.net,deg.sequence,pay.total_loans,adr.imprint,pay.id '
            'ORDER BY  deg.sequence,emp.name_related' , (data['month'],data['year'],data['allow'][0],data['bonus_date'],company,tuple(payroll_ids),'allow'))    
        res = cr.dictfetchall()
        pays_ids = [i['pay_id'] for i in res]
        pays_ids += pays_ids


        if not pays_ids:
            raise osv.except_osv(_('Error'), _('There is no Archive!'))
        
        #related to attendace
        allow = data['allow'][0]
        related_att = self.pool.get('hr.allowance.deduction').read(cr, uid, allow, ['related_attendance'],{})
        related_att = related_att['related_attendance']

        if related_att:
            return{
            'type': 'ir.actions.report.xml',
            'report_name': 'bonus_listing_related_att.report',
            'datas': datas,
                    }

        return{
            'type': 'ir.actions.report.xml',
            'report_name': 'bonus_listing.report',
            'datas': datas,
                    }
         


class employees_salary_report(osv.osv_memory):
    _name = "employee.bonus.report"

    def _get_employee(self, cr, uid, context=None):
        result = False
        user_obj = self.pool.get('res.users')
        archive_obj = self.pool.get('hr.process.archive')
        archive_rec = archive_obj.browse(cr,uid,context['active_id'])
        employee_id = archive_rec.employee_id.id
     
        return employee_id

    _columns = {
        'employee_id' : fields.many2one('hr.employee', "Employee", required=True),
        }

    _defaults ={
        'employee_id': _get_employee,
        
    }

   


    def print_report(self, cr, uid, ids, context=None):
        datas = {}

        if context is None:
            context = {}
        data = self.read(cr, uid, ids)[0]
        archive_obj = self.pool.get('hr.process.archive')
        archive_rec = archive_obj.browse(cr,uid,context['active_id'])

        #ref = archive_rec.reference.split(',')
        name = archive_rec.reference._name
        if archive_rec.state != 'approved':
            raise osv.except_osv(_('Warning!'),_('The process is not approved yet'))
        if name != 'hr.salary.bonuses':
            raise osv.except_osv(_('Warning!'),_('This is not Annoual Bonus'))
       
        datas = {
             'ids': context.get('active_ids', []),
             'model': 'hr.process.archive',
             'form': data
                }
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'employee.bonus',
            'datas': datas,
            }


class employees_salary_report(osv.osv_memory):
    _name = "employee.additional.form.report"

    def _get_period(self, cr, uid, context=None):
        result = False
        user_obj = self.pool.get('res.users')
        additional_obj = self.pool.get('hr.additional.allowance')
        additional_rec = additional_obj.browse(cr,uid,context['active_id'])
        period_id = additional_rec.period_id.id
     
        return period_id

    def _get_month(self, cr, uid, context=None):
        result = False
        user_obj = self.pool.get('res.users')
        additional_obj = self.pool.get('hr.additional.allowance')
        additional_rec = additional_obj.browse(cr,uid,context['active_id'])
        month = additional_rec.month
     
        return month

    _columns = {
        'period_id': fields.many2one('account.period', 'Period', domain=[('special', '=', False)]),
        'month' :fields.selection([(1, '1'), (2, ' 2'), (3, '3'), (4, '4'), (5, '5'), (6, '6'),
                                           (7, '7'), (8, '8'), (9, '9'), (10, '10'), (11, '11'), (12, '12')],
                                            'Month'),
        }

    _defaults ={
        'month': _get_month,
        'period_id': _get_period,
        
    }


    def print_report(self, cr, uid, ids, context=None):
        datas = {}

        if context is None:
            context = {}
        data = self.read(cr, uid, ids)[0]
        additional_obj = self.pool.get('hr.additional.allowance')
        additional_rec = additional_obj.browse(cr,uid,context['active_id'])
        #data['record'] = additional_rec
        line_ids = []
        data['active_id'] = context['active_id']
        print "---------------data", data, context

        datas = {
             'ids': context.get('active_ids', []),
             'model': 'hr.additional.allowance',
             'form': data
                }
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'additional_form',
            'datas': datas,
            }