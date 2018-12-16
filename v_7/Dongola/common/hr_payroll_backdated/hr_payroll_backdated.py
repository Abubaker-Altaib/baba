# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################
import time
import datetime
from openerp.osv import fields, osv, orm
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp
import mx
from dateutil.relativedelta import relativedelta

#----------------------------------------
#Payroll Main Archive
#---------------------------------------- 
class hr_employee_salary_addendum(osv.Model):

    _inherit = 'hr.employee.salary.addendum'

    _columns = {
       
        'to_month' :fields.selection([(1, '1'), (2, ' 2'), (3, '3'), (4, '4'), (5, '5'), (6, '6'),
                                   (7, '7'), (8, '8'), (9, '9'), (10, '10'), (11, '11'), (12, '12')], "Month"),
        'to_year' :fields.integer("Year"),
      
        'basic_salary' : fields.boolean('Basic Salary'),

        'type':fields.selection([('salary', 'Salary'), ('addendum', 'Addendum'),('backdated_salary', 'Backdated salary'),('backdated_addendum', 'Backdated addendum')], "Type", required = True),
        
    }
    
    def get_data(self, cr, uid, ids, context = {}):

        main_archive_obj = self.pool.get('hr.payroll.main.archive')
        archive_obj = self.pool.get('hr.allowance.deduction.archive')
        res = super(hr_employee_salary_addendum, self).get_data(cr, uid, ids, context=context)
       
        
        for record in self.browse(cr, uid, ids, context = context):
            if record.type in ( 'backdated_salary','backdated_addendum'):
                domain = [('type', '=', record.type),('month', '=', record.month), ('year', '=', record.year), ('scale_id', 'in', res['payroll_ids']),
                                            ('employee_id', 'in', res['employee_ids']), ('company_id', 'in', res['company_id'])]
                if record.type == 'backdated_salary':
                    domain.append(('in_salary_sheet', '=', True))
                else:
                    domain.append(('in_salary_sheet', '=', False))
           
                archive_ids = main_archive_obj.search(cr, uid, domain, context=context)
                addendums_arch_ids = []
                if archive_ids:
                    if record.type == 'backdated_addendum':
                        addendums_arch_ids = archive_obj.search(cr, uid, [('main_arch_id', 'in', archive_ids),
                                                                      ('allow_deduct_id', 'in', res['addendum_ids'])], context=context)
                        if not addendums_arch_ids:
                            archive_ids = []
                res.update({'archive_ids':archive_ids,
                            'addendums_arch_ids':addendums_arch_ids,
                            'basic_salary':record.basic_salary,
                            'to_year':record.to_year,
                            'to_month':record.to_month})
            
        return res
        
    def compute(self, cr, uid, ids, context = {}):
        """Compute salary/addendum for all employees or specific employees in specific month.
           @return: Dictionary 
        """
        payroll_obj = self.pool.get('payroll')
        employee_obj = self.pool.get('hr.employee')
        main_arch_obj = self.pool.get('hr.payroll.main.archive')
        status_obj = self.pool.get('hr.holidays.status')
        delegation_obj = self.pool.get('hr.employee.delegation')
        allow_deduct_obj = self.pool.get('hr.allowance.deduction')
        data = self.get_data(cr, uid, ids, context=context)
        if data['archive_ids']:
            raise osv.except_osv(_('Error'), _('The  %s In The %sth Month Year Of %s It is  Already Computed')
                                    % (data['type'], data['month'], data['year']))
        if  context.get('salary_batch_id'):
            self.pool.get('hr.salary.batch').write(cr,uid,[context.get('salary_batch_id')],{'batch_total':len(data['employee_ids']),} )
        paroll_date = (datetime.date (int(data['year']), int(data['month']), 1) + relativedelta(day=1, months= +1, days= -1)).strftime('%Y-%m-%d')
        paroll_date = mx.DateTime.Parser.DateTimeFromString(paroll_date) 
        unpaied = status_obj.search(cr, uid, [('payroll_type', '=', 'unpaied')])
        customized = status_obj.search(cr, uid, [('payroll_type', '=', 'customized')])
        hol = self._get_leave_status(cr, uid, ids, data['employee_ids'] , data['month'], data['year'], paroll_date)
        unpaied_del = delegation_obj.search(cr, uid, [('payroll_type', '=', 'unpaied')])
        customized_del = delegation_obj.search(cr, uid, [('payroll_type', '=', 'customized')])
        deligation = self._get_delgation(cr, uid , ids, data['employee_ids'], data['month'], data['year'],paroll_date)
        if data['type'] =='backdated_salary':
            allow_deduct = self._get_allowance_deduction(cr, uid, ids,  data)
        for employee in employee_obj.browse(cr, uid, data['employee_ids'], context=context):
            basic_salary = 0.0
            days = 30
            in_salary_sheet = False
            allow_deduct_dict = []
            if data['type'] == 'salary':
                in_salary_sheet = True
                basic_salary = employee.bonus_id.basic_salary
                # Check employment date & end_date during salary computation
                # FIXME:  February has 28/29 days with always less than 30 
                emp_date = mx.DateTime.Parser.DateTimeFromString(employee.employment_date)
                end_date = employee.end_date and mx.DateTime.Parser.DateTimeFromString(employee.end_date) or paroll_date
                emp_no_days = (paroll_date - emp_date).days + 1
                end_no_days = (paroll_date - end_date).days
                days = (emp_no_days < 30 and emp_no_days or 30) - (0 <= end_no_days <= 30 and end_no_days or 0)
                if days <= 0:
                    continue
                # TEST: if same month has holiday & delegation
                # unpaied and  customized holidays
                for un in unpaied:
                    dict1 = hol.get((employee.id, 'unpaied', un), {})
                    if dict1:
                        days -= dict1['days']
                if days >= 0 :
                    basic_salary = (basic_salary / 30) * days
                customized_allow_deduct = []
                for cus in customized:
                    dict2 = hol.get((employee.id, 'customized', cus), {})
                    if dict2:
                        days -= dict2['days']
                        customized_allow_deduct += self.write_allow_deduct(cr, uid, ids, employee.id, dict2['days'], dict2['allow_deduct_ids'])
                # unpaied and  customized delegation
                for un in unpaied_del:
                    dict1 = deligation.get((employee.id, 'unpaied', un), {})
                    if dict1:
                        days -= dict1['days']
                        if days >= 0 :
                            basic_salary = (basic_salary / 30) * days
                            customized_allow_deduct = []
                for cus in customized_del:
                    dict2 = deligation.get((employee.id, 'customized', cus), {})
                    if dict2:
                        days -= dict2.get('days', 0)
                        customized_allow_deduct += self.write_allow_deduct(cr, uid, ids, employee.id, dict2['days'], dict2['allow_deduct_ids'])
                allow_deduct_dict = self.write_allow_deduct(cr, uid, ids, employee.id, days)
                if customized_allow_deduct:
                    grouped = {}
                    res = allow_deduct_dict + customized_allow_deduct
                    for r in res:
                        key = r['allow_deduct_id']
                        if not key in grouped:
                            grouped[key] = r
                        else:
                            grouped[key]['amount'] += r['amount']
                            grouped[key]['tax_deducted'] += r['tax_deducted']
                    allow_deduct_dict = [val for key, val in grouped.items()]
            elif data['type'] =='backdated_salary':
                in_salary_sheet = True
                if  data['basic_salary']:
                    basic_salary = employee.bonus_id.basic_salary
                allow_deduct_dict = allow_deduct.get(employee.id,[])
            else:
                for addendum in data['addendum_ids']:
                    check_employment=allow_deduct_obj.browse(cr,uid,addendum).based_employment
                    if check_employment == 'based':
                        amount_dict = payroll_obj.allowances_deductions_calculation(cr,uid,data['date'],employee,{}, [addendum])
                        # Check employment date & end_date during addendum computation
                        emp_date = mx.DateTime.Parser.DateTimeFromString(employee.employment_date)
                        year_emp_date =  emp_date.year
                        days = 365
                        if int(year_emp_date) == int(data['year']):
                            emp_end_date_days = 0
                            if employee.end_date:
                                end = (datetime.date (int(data['year']),  int(12), 31)).strftime('%Y-%m-%d')
                                end = mx.DateTime.Parser.DateTimeFromString(end)
                                end_date = mx.DateTime.Parser.DateTimeFromString(employee.end_date) 
                                emp_end_date_days = (end - end_date).days

                            first_date = (datetime.date (int(data['year']),  int(1), 1)).strftime('%Y-%m-%d')
                            first_date = mx.DateTime.Parser.DateTimeFromString(first_date) 
                            emp_no_days = (emp_date - first_date).days
                            days -= (emp_no_days + emp_end_date_days)
                            if days <= 0:
                                continue
                    if amount_dict['result']:
                        amount = amount_dict['result'][0]['holiday_amount'] and amount_dict['result'][0]['holiday_amount'] or amount_dict['result'][0]['amount']
                        if data['type'] =='backdated_addendum':
                            addendum_data = self._get_addendum(cr, uid, data ,employee.id ,addendum, amount)
                            allow_deduct_dict +=addendum_data[employee.id]
                        else:
                            addendum_dict = {
                            'allow_deduct_id': addendum,
                            'amount':amount and amount/365 * days ,
                            'tax_deducted':amount_dict['result'][0]['tax'],
                            'imprint':amount_dict['result'][0]['imprint'],
                            'remain_amount':amount_dict['result'][0]['remain_amount'],
                        }
                            allow_deduct_dict.append(addendum_dict)
            main_arch_obj.create(cr, uid, {
                'code':employee.emp_code,
                'employee_id':employee.id,
                'month' :data['month'],
                'year' :data['year'],
                'department_id' :employee.department_id and employee.department_id.id or False,
                'salary_date' :data['date'],
                'basic_salary':basic_salary,
                'company_id':employee.company_id.id,
                'job_id': employee.job_id and employee.job_id.id or False,
                'scale_id' : employee.payroll_id.id,
                'degree_id' : employee.degree_id.id,
                'bonus_id' :employee.bonus_id.id,
                'allow_deduct_ids': [(0, 0, x) for x in allow_deduct_dict],
                'in_salary_sheet':in_salary_sheet,
                'arch_id':data['record_id'],
                'bank_account_id': employee.bank_account_id and employee.bank_account_id.id or False,
                'type':data['type'],
            }, context = context)
        if not context.get('salary_batch_id'):
            self.write(cr, uid, ids, { 'state': 'compute'}, context=context)
        else :
            state = len([btch.id for btch in self.browse(cr,uid,ids)[0].batch_ids if btch.state!='compute'])-1 > 0 and 'draft' or 'compute'
            self.write(cr, uid, ids, { 'state': state}, context=context)
        return {}
        

    def _get_allowance_deduction(self, cr, uid, ids, data):
       
        allow_deduct_dict = {}

        if data['employee_ids']:
            cr.execute("""SELECT 
                          arc.employee_id, 
                          
                          adarch.allow_deduct_id, 
                          emp.type,                         
                          SUM(emp.amount - adarch.amount) as diff

                        FROM 
                          hr_allowance_deduction_archive adarch LEFT JOIN  
                          hr_payroll_main_archive arc  ON 
                          adarch.main_arch_id = arc.id 
                          INNER JOIN  hr_employee_salary emp   
                          ON  emp.allow_deduct_id = adarch.allow_deduct_id AND
                          emp.employee_id = arc.employee_id 
                        WHERE arc.employee_id IN %s AND  adarch.allow_deduct_id IN %s 
                            AND TO_DATE(arc.month  || '01' || arc.year, 'MMDDYY')  between
                            TO_DATE(%s  || '01' || %s, 'MMDDYY') AND
                            TO_DATE(%s  || '01' || %s, 'MMDDYY')
                        GROUP BY arc.employee_id, emp.type,adarch.allow_deduct_id
                          """ , (tuple(data['employee_ids']),tuple( data['addendum_ids']) ,data['month'],data['year'], data['to_month'], data['to_year']))
            res = cr.dictfetchall()
            for r in res:
                key = r['employee_id']
                data= {
                        'allow_deduct_id': r['allow_deduct_id'],
                        'type' : r['type'],
                        'amount': r['diff'] ,
                        'tax_deducted':0.0}
                if not key in allow_deduct_dict :
                    allow_deduct_dict[key] = []
                allow_deduct_dict[key].append(data)
        return allow_deduct_dict 


    def _get_addendum(self, cr, uid,  data ,employee ,addendum, amount):
       
        addendum_dict = {}

        cr.execute("""SELECT 
                      arc.employee_id, 
                      adarch.allow_deduct_id, 
                      adarch.type,                         
                      SUM( %s - adarch.amount) as diff
                    FROM 
                      hr_allowance_deduction_archive adarch LEFT JOIN  
                      hr_payroll_main_archive arc  ON 
                      adarch.main_arch_id = arc.id 
                    WHERE arc.employee_id = %s AND  adarch.allow_deduct_id = %s 
                        AND TO_DATE(arc.month  || '01' || arc.year, 'MMDDYY')  between
                        TO_DATE(%s  || '01' || %s, 'MMDDYY') AND
                        TO_DATE(%s  || '01' || %s, 'MMDDYY')
                    GROUP BY arc.employee_id, adarch.type,adarch.allow_deduct_id
                      """ , (amount, employee,addendum ,data['month'],data['year'], data['to_month'], data['to_year']))
        res = cr.dictfetchall()
        for r in res:
            key = r['employee_id']
            data= {
                    'allow_deduct_id': r['allow_deduct_id'],
                    'type' : r['type'],
                    'amount': r['diff'] ,
                    'tax_deducted':0.0}
            if not key in addendum_dict :
                addendum_dict[key] = []
            addendum_dict[key].append(data)
        return addendum_dict
        
        
class hr_payroll_main_archive(osv.Model):

    _inherit = 'hr.payroll.main.archive'
    _columns = {
        'type':fields.selection([('salary', 'Salary'), ('addendum', 'Addendum'),('backdated_salary', 'Backdated salary'),('backdated_addendum', 'Backdated addendum')], "Type", required = True),

        
        #'unpaied_hol_days' :fields.integer("Unpaied holidays days"),
        #'customized_hol_days' :fields.integer("Customized holidays days"),       
    }
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
