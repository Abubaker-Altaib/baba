# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################
import time
from datetime import datetime
import mx

from openerp.osv import fields, osv
from openerp.tools.translate import _
#----------------------------------------------------------
# Payroll Calculation Functions
#----------------------------------------------------------
class payroll(osv.osv):

    _name = "payroll"

    _description = "Payroll Calculation"
    
    def family_relation_calculation(self, cr, uid, emp_id, date):
        """
        Method calculates amounts of family realtions.
        @param emp_id: Id of employee
        @param date: Current date
        @return: Dictionary of values , children amount , rel amount and number of children
        """
        rel_amount = 0.0
        child_no = 0
        relation_pool = self.pool.get('hr.family.relation')
        family_pool = self.pool.get('hr.employee.family')
        family = family_pool.read_group(cr, uid, [
                 ('employee_id', '=', emp_id), ('start_date', '<=', date),
                 ('state', '=', 'approved')
        ], ['relation_id'], ['relation_id'])

        for m in family:
            relation=relation_pool.browse(cr, uid,[m['relation_id'][0]] )[0]
            if m['relation_id_count'] > relation.max_number:
                m['relation_id_count']= relation.max_number 
            if relation.children:
                child_no +=  m['relation_id_count']
            rel_amount += m['relation_id_count']*relation.amount
        return {'rel_amount':rel_amount, 'child_no':child_no}


    def qualification_calculation(self, cr, uid, emp_id):
        """
        Method that calculates the amount of qualification.
        @param emp_id: Id of employee
        @return: qualification amount 
        """
        qual_amount = 0.0
        qual_obj= self.pool.get('hr.qualification')
        emp_qual_obj= self.pool.get('hr.employee.qualification')
        #If the employee has approved qualifications
        qual_ids = emp_qual_obj.search(cr, uid, [
                                ('employee_id', '=', emp_id),('state', '=', 'approved'),('emp_qual_id', '!=', False)])
                                
        qual_list = [q.emp_qual_id.id for q in emp_qual_obj.browse(cr, uid, qual_ids) if qual_ids]
        if qual_list:
            # qualification of the employee with the maximum order  
            cr.execute("select q.amount from hr_qualification q where q.order=(select max(q.order) from hr_qualification q where q.id in %s)" , (tuple(qual_list),))
            res = cr.fetchone()
            if res:
                qual_amount = res[0]
        return qual_amount
        
    def allowances_linked_absence_calculation(self, cr, uid, emp_dict,amount):
        """
        Method that calculates the amount of qualification.
        @param emp_id: Id of employee
        @return: qualification amount 
        """
        emp_holiday_obj = self.pool.get('hr.holidays')
        main_arch_obj = self.pool.get('hr.payroll.main.archive')
        allow_deduct_arch_obj = self.pool.get('hr.allowance.deduction.archive')
        holiday_amount = 0.0
        remain_amount = 0.0
        deduct = 0.0
        exempted = emp_dict['allow_deduct'].allow_deduct_id.exempted_amount
        allow_deduct= emp_dict['allow_deduct'].allow_deduct_id
        
        curr_date = datetime.strptime(emp_dict['date'], '%Y-%m-%d')
        
        if emp_dict['allow_deduct'].allow_deduct_id.in_salary_sheet:
           in_salary_sheet = True
        else:
           in_salary_sheet = False
        calc_allowance_id = emp_dict['allow_deduct'].allow_deduct_id.id
        '''cr.execute("select id from hr_payroll_main_archive where month=(select max(month) from hr_payroll_main_archive where year =(select max(year) from hr_payroll_main_archive where in_salary_sheet =%s and employee_id=%s) and in_salary_sheet =%s and employee_id=%s) and year=(select max(year) from hr_payroll_main_archive where in_salary_sheet =%s and employee_id=%s) and in_salary_sheet =%s and employee_id=%s" , (in_salary_sheet,emp_dict['emp_id'],in_salary_sheet,emp_dict['emp_id'],in_salary_sheet,emp_dict['emp_id'],in_salary_sheet,emp_dict['emp_id'],))'''
        if in_salary_sheet == True:
          cr.execute('select m.id from hr_payroll_main_archive m \
                                where \
                                  m.month=(select max(m2.month) from hr_payroll_main_archive m2\
                                    where m2.year =(select max(m1.year) from hr_payroll_main_archive m1 \
                                        where m1.in_salary_sheet =%s and m1.employee_id=%s) \
                                    and m2.in_salary_sheet =%s and m2.employee_id=%s) \
                                and \
                                    m.year=(select max(m3.year) from hr_payroll_main_archive m3 \
                                        where m3.in_salary_sheet =%s and m3.employee_id=%s) \
                                and \
                                    m.in_salary_sheet =%s and m.employee_id=%s',(in_salary_sheet,emp_dict['emp_id'],
                                          in_salary_sheet,emp_dict['emp_id'],in_salary_sheet,emp_dict['emp_id'],
                                          in_salary_sheet,emp_dict['emp_id'],))
        else:
          cr.execute('select m.id from hr_payroll_main_archive m \
                                  where \
                                    m.month=(select max(m2.month) from hr_payroll_main_archive m2\
                                      join hr_allowance_deduction_archive v2 on (v2.main_arch_id =  m2.id and v2.allow_deduct_id=%s)\
                                      where m2.year =(select max(m1.year) from hr_payroll_main_archive m1 \
                                          join hr_allowance_deduction_archive v1 on (v1.main_arch_id =  m1.id and v1.allow_deduct_id=%s)\
                                          where m1.in_salary_sheet =%s and m1.employee_id=%s) \
                                      and m2.in_salary_sheet =%s and m2.employee_id=%s) \
                                  and \
                                      m.year=(select max(m3.year) from hr_payroll_main_archive m3 \
                                          join hr_allowance_deduction_archive v3 on (v3.main_arch_id =  m3.id and v3.allow_deduct_id=%s)\
                                          where m3.in_salary_sheet =%s and m3.employee_id=%s) \
                                  and \
                                      m.in_salary_sheet =%s and m.employee_id=%s',(calc_allowance_id,calc_allowance_id,in_salary_sheet,emp_dict['emp_id'],
                                            in_salary_sheet,emp_dict['emp_id'],calc_allowance_id,in_salary_sheet,emp_dict['emp_id'],
                                            in_salary_sheet,emp_dict['emp_id'],))
        res = cr.fetchone()
        if res:
           prev_salary_date=main_arch_obj.browse(cr,uid,res[0])
           domain=[]
           domain += ['|','|', ('date_to','<=',emp_dict['date']),('date_to','>=',emp_dict['date']),('date_to','>',prev_salary_date.salary_date)]
           domain += ['|','|',('date_from','>=',prev_salary_date.salary_date), ('date_from','<=',prev_salary_date.salary_date),('date_from','<=',emp_dict['date'])]
           domain+= [('employee_id','=',emp_dict['emp_id']),('state','in',('validate','done_cut'))]
           #domain+= [('employee_id','=',emp_dict['emp_id']),('state','not in',('draft','cancel','refuse'))]
           if emp_dict['allow_deduct'].allow_deduct_id.holiday_ids:
              domain+= [('holiday_status_id','in',[holiday.id for holiday in emp_dict['allow_deduct'].allow_deduct_id.holiday_ids])]
           emp_holidays_ids= emp_holiday_obj.search(cr,uid,domain)
           days=0
           if emp_holidays_ids: 
              for holiday in emp_holiday_obj.browse(cr,uid,emp_holidays_ids):
                       prev_dt = time.mktime(time.strptime(prev_salary_date.salary_date,'%Y-%m-%d'))
                       date_t = mx.DateTime.Parser.DateTimeFromString(holiday.date_to)
                       date_f = mx.DateTime.Parser.DateTimeFromString(holiday.date_from)
                       if date_t.month == curr_date.month and date_t.year == curr_date.year:
                          if date_f.month == curr_date.month:
                             days+= holiday.number_of_days_temp
                          elif (date_f.month < curr_date.month and date_t.year == curr_date.year) or (date_f.month > curr_date.month and date_f.year == curr_date.year-1):
                             if holiday.create_date > prev_salary_date.salary_date:
                                days+= holiday.number_of_days_temp
                             else:
                                days+=date_t.day
                                if date_f.day==31:
                                   days-=1

                       elif (date_t.month > curr_date.month and date_t.year == curr_date.year) or (date_t.month < curr_date.month and date_t.year > curr_date.year):
                          if date_f.month == curr_date.month:
                             days+=(30-date_f.day+1)
                          elif (date_f.month < curr_date.month and date_t.year == curr_date.year) or (date_f.month > curr_date.month and date_f.year == curr_date.year-1): 
                             if holiday.create_date < prev_salary_date.salary_date :
                                days+=30
                             else :
                                if not date_f.month == 2:
                                   prev_month=30-date_f.day+1
                                else :
                                   prev_month=30-date_f.day
                                days+=30+ prev_month
                       elif ((date_t.month < curr_date.month and date_t.year== curr_date.year) or (date_t.month > curr_date.month and date_t.year == curr_date.year-1)) and holiday.create_date > prev_salary_date.salary_date :
                          days+=holiday.number_of_days_temp
           amount_per_day=amount/30
           deduct=amount_per_day * days
           emp_prev_allow = allow_deduct_arch_obj.search(cr,uid,[('allow_deduct_id','=',emp_dict['allow_deduct'].allow_deduct_id.id),('main_arch_id','=',prev_salary_date.id)])
           if emp_prev_allow:
              deduct+= allow_deduct_arch_obj.browse(cr,uid,emp_prev_allow[0]).remain_amount
           if deduct >= amount:
              remain_amount= deduct - amount
              deduct=amount
              amount= 0.0
              exempted=emp_dict['allow_deduct'].allow_deduct_id.exempted_amount-((emp_dict['allow_deduct'].allow_deduct_id.exempted_amount/30)*30)
                        
           else:
              exempted=emp_dict['allow_deduct'].allow_deduct_id.exempted_amount-((emp_dict['allow_deduct'].allow_deduct_id.exempted_amount/30)*days)
              holiday_amount=amount-deduct
        holiday_amount = deduct
        return  holiday_amount , remain_amount

    def allowances_deductions_calculation(self, cr, uid, date, employee_obj, emp_dict, allow_deduct, substitution=False, allow_list=[]):
        """
        Retrieve all employees's salary scale allowances and deductions, based on employee's salary scale and degree.
        @param date: Current date
        @param employee_obj: hr.employee record
        @param emp_dict: Dictionary of values
        @param allow_deduct: List of allowances and deductions ids 
        @param substitution: Boolean
        @param allow_list: List of employee allowances and deductions ids
        @return: Dictionary of data 
        """
        salary_scale_obj = self.pool.get('hr.salary.scale')
        salary_allow_deduct_obj = self.pool.get('hr.salary.allowance.deduction')
        employee_substitution_obj = self.pool.get('hr.employee.substitution')
        allow_amount = 0.0
        deduct_amount = 0.0
        result = []
        if not substitution:
            # if substitution False the emp_dict is empty and will be updated with employee's info , 
            #if its True it  contains employee's substitution info 
            if (not emp_dict) or (emp_dict and 'no_sp_rec' not in emp_dict.keys()) :
                emp_dict.update({'no_sp_rec': False})
            emp_dict .update({
                'emp_id':employee_obj.id,
                'company':employee_obj.company_id.id,
                'department':employee_obj.department_id.id,
                'job_id':employee_obj.job_id.id,
                'gender':employee_obj.gender,
                'category':employee_obj.category_ids,
                'payroll':employee_obj.payroll_id.id,
                'degree':employee_obj.degree_id.id,
                'taxable': employee_obj.degree_id.taxable,
                'bonus':employee_obj.bonus_id.id,
                'basic_salary':employee_obj.bonus_id.basic_salary,
                'old_basic_salary':employee_obj.bonus_id.old_basic_salary,
                'started_section':employee_obj.degree_id.basis,
                'marital_status':employee_obj.marital,
                'exemp_tax':employee_obj.tax_exempted,
                'date':date,
                'substitution':substitution,
                'special': False })
            # check if employee has substitution
            substitue_ids = employee_substitution_obj.search(cr, uid, ['|', ('end_date', '>=', date), ('end_date', '=', False), 
                            ('employee_id', '=', emp_dict['emp_id']), ('start_date', '<=', date)])
            if substitue_ids:
                for sub_record in employee_substitution_obj.browse(cr, uid, substitue_ids):
                    scale = salary_scale_obj.read(cr, uid, [emp_dict['payroll']], ['sub_salary'])[0]
                    emp_dict.update({'substitution_obj': sub_record,
                                     'substitution_setting':scale['sub_salary']})
                    if scale['sub_salary'] == 'sustitut_degree':
                        #update emp_dict with employee's substitution degree if substitution setting=sustitut_degree
                        emp_dict.update({
                            'payroll':sub_record.payroll_id.id,
                            'degree':sub_record.degree_id.id,
                            'started_section':sub_record.degree_id.basis,
                            'bonus':sub_record.bonus_id.id,
                            'basic_salary':sub_record.bonus_id.basic_salary,
                            'old_basic_salary':sub_record.bonus_id.old_basic_salary})
        domain = [('payroll_id', '=', emp_dict['payroll']), ('degree_id', '=', emp_dict['degree'])]
        if allow_deduct:
            # if allow_deuct list is empty retrieve all allowances and deductions or 
            #retrieve only allowances and deductions specified on allow_deduct list
            domain += [('allow_deduct_id', 'in', tuple(allow_deduct))]
        allow_deduct_ids = salary_allow_deduct_obj.search(cr, uid, domain)
        if allow_deduct_ids:
            if not allow_list:
                allow_list = [a.allow_deduct_id.id for a in salary_allow_deduct_obj.browse(cr, uid, allow_deduct_ids)]
         
        sub_setting = salary_scale_obj.read(cr, uid, [emp_dict['payroll']], ['sub_setting'])[0]
        for record in salary_allow_deduct_obj.browse(cr, uid, allow_deduct_ids):
            # if substitution True check  pay_sheet settings (frist sheet only or first and second sheet)
            if (substitution and (sub_setting['sub_setting'] and (sub_setting['sub_setting'] == 'first' and \
                   record.allow_deduct_id.pay_sheet == 'first') or sub_setting['sub_setting'] == 'first_and_second') and \
                   record.allow_deduct_id.name_type == 'allow') or not substitution:
                if (not allow_deduct and record.allow_deduct_id.in_salary_sheet) or allow_deduct:
                    #if not record.allow_deduct_id.special:
                    emp_dict.update({'allow_deduct': record, })
                    allow_deduct_dict = self.allowances_deductions_amount(cr, uid, emp_dict, allow_list)
                    if record.allow_deduct_id.name_type == 'allow':
                        allow_amount += allow_deduct_dict['amount']
                    else:
                        deduct_amount += allow_deduct_dict['amount']
                    if not substitution:
                        # add allowance or deduction list to the result list if not retreiving allowances and deductions for substitution
                        allow_deduct_dict.update({'allow_deduct': record, })
                    result.append(allow_deduct_dict)
        return {'total_allow':allow_amount, 'total_deduct':deduct_amount, 'result':result}

    def allowances_deductions_amount(self, cr, uid, emp_dict, allow_list):
        """
        calculate amount of allowances / deductions.
        @param emp_dict: Dictionary of values
        @param allow_list: List of employee allowances and deductions ids
        @return: Dictionary of values 
        """
        salary_allow_deduct_obj = self.pool.get('hr.salary.allowance.deduction')
        allow_deduct_exception_obj = self.pool.get('hr.allowance.deduction.exception')
        marital_status_obj = self.pool.get('hr.allow.marital.status')
        amount = tax_amount = imprint = 0.0
        holiday_amount = 0.0
        remain_amount = 0.0
        percent = 1
        exempted = emp_dict['allow_deduct'].allow_deduct_id.exempted_amount
        check = False
        allow_deduct= emp_dict['allow_deduct'].allow_deduct_id
        # check if allowance or deduction is special and special flag is false then call special function
        if allow_deduct.special and not emp_dict['special']:
            special_dict = self.allowances_deductions_sp_calculation(cr, uid, emp_dict, allow_list)
            amount += special_dict['amount']
            tax_amount += special_dict['tax']
        else:
            # check employee allowance/deduction exclusion
            exclusion = allow_deduct_exception_obj.search(cr, uid, ['|', ('end_date', '>', emp_dict['date']), ('end_date', '=', False),
                           ('employee_id', '=', emp_dict['emp_id']), ('start_date', '<', emp_dict['date']), 
                           ('allow_deduct_id', '=', allow_deduct.id), ('action', '=', 'exclusion')])
            if not exclusion:
                # check start date , end date,company,departments, jobs and categories for specific allowance/deduction 
                if allow_deduct.start_date <= emp_dict['date'] and (not allow_deduct.end_date or (allow_deduct.end_date and \
                    allow_deduct.end_date >= emp_dict['date'])):
                    if not allow_deduct.company_id or (allow_deduct.company_id and \
                        allow_deduct.company_id.id == emp_dict['company']):
                        dept_list = []
                        cr.execute("select department_id from allow_deduct_department_rel where allow_deduct_id=%s" ,\
                                            (allow_deduct.id,))
                        res = cr.fetchall()
                        dept_list = [r[0] for r in res if res]
                        if not dept_list or (dept_list and emp_dict['department'] in dept_list):
                            allow_gender = allow_deduct.allow_gender_ids
                            if not allow_deduct.related_gender_type or (allow_gender and emp_dict['gender'] in [i.gender for i in  allow_gender]):
                              check = True
                if check :
                  if not allow_deduct.allow_cat_ids and not allow_deduct.allow_job_ids :
                    check = True
                  else :
                    emp_cat_ids = [i.id for i in emp_dict['category']]
                    allow_cat_obj = self.pool.get('hr.allowance.cat')
                    allow_cat_ids = allow_cat_obj.search(cr , uid , [('cat_id' , 'in' , emp_cat_ids) , ('allow_deduct_id' , '=' , allow_deduct.id)])
                    if allow_cat_ids :
                      values = allow_cat_obj.read(cr , uid , allow_cat_ids , ['value'])
                      percent = percent * values[0]['value'] / 100
                    else :
                      allow_job_obj = self.pool.get('hr.allowance.job')
                      allow_job_ids = allow_job_obj.search(cr , uid , [('job_id' , '=' , emp_dict['job_id']) , ('allow_deduct_id' , '=' , allow_deduct.id)])
                      if allow_job_ids :
                        values = allow_job_obj.read(cr , uid , allow_job_ids , ['value'])
                        percent = percent * values[0]['value']  / 100
                      else :
                        check = False
                if check:
                    if allow_deduct.salary_included:
                        amount += emp_dict['basic_salary']
                    if allow_deduct.old_salary_included:
                        amount += emp_dict['old_basic_salary']
                    if allow_deduct.started_section_included:
                        amount += emp_dict['started_section']
                    if allow_deduct.allowance_type=='qualification':
                        amount += self.qualification_calculation(cr, uid, emp_dict['emp_id'])
                    if allow_deduct.allowance_type=='family_relation':
                        family_relation= self.family_relation_calculation(cr, uid, emp_dict['emp_id'], emp_dict['date'])
                        amount += family_relation['rel_amount']
                    if allow_deduct.allowance_type=='substitution':
                        if not emp_dict['substitution']:
                            if 'substitution_obj' in emp_dict:
                                if emp_dict['substitution_setting'] == 'diff':
                                    # calculate substitution amount by subtract total allowances
                                    # of current degree from total allowance of substitution degree 
                                    # if substitution setting = diff (Compute Difference Between The 2 Degree)
                                    emp_curr_dict = emp_dict.copy()
                                    emp_curr_dict.update({'substitution':True})
                                    # total allowances amount for current degree
                                    curr_allow_dict = self.allowances_deductions_calculation(cr, uid, emp_curr_dict['date'],
                                                            [], emp_curr_dict, [], emp_curr_dict['substitution'], [])
                                    curr_allow_dict['total_allow'] += emp_curr_dict['basic_salary']
                                    emp_sub_dict = emp_dict.copy()
                                    substitution_obj=emp_sub_dict['substitution_obj']
                                    emp_sub_dict.update({
                                        'payroll':substitution_obj.payroll_id.id,
                                        'degree':substitution_obj.degree_id.id,
                                        'bonus':substitution_obj.bonus_id.id,
                                        'basic_salary':substitution_obj.bonus_id.basic_salary,
                                        'old_basic_salary':substitution_obj.bonus_id.old_basic_salary,
                                        'started_section':substitution_obj.degree_id.basis,
                                        'substitution':True})
                                    # total allowances amount for substitution degree
                                    sub_allow_dict = self.allowances_deductions_calculation(cr, uid, emp_sub_dict['date'],
                                          [], emp_sub_dict, [], emp_sub_dict['substitution'], [])
                                    sub_allow_dict['total_allow'] += emp_sub_dict['basic_salary']
                                    substitution_amount = sub_allow_dict['total_allow'] - curr_allow_dict['total_allow']
                                    # substitution percentge
                                    sub_config=self.pool.get('hr.salary.scale').browse(cr, uid, [emp_dict['payroll']])[0]
                                    if sub_config.sub_prcnt_selection and sub_config.sub_percentage:
                                        emp_slry_prcnt=curr_allow_dict['total_allow']*sub_config.sub_percentage/100
                                        if  sub_config.sub_prcnt_selection == 'percentge':
                                            substitution_amount=emp_slry_prcnt
                                        elif  sub_config.sub_prcnt_selection == 'bigest':
                                            substitution_amount = emp_slry_prcnt > substitution_amount and emp_slry_prcnt or substitution_amount
                                        elif  sub_config.sub_prcnt_selection == 'smalest':
                                            substitution_amount = emp_slry_prcnt < substitution_amount and emp_slry_prcnt or substitution_amount
                                    amount += substitution_amount
                                    emp_dict.update({'substitution':False})
                    if allow_deduct.type == 'amount':
                        #if type is amount add the amount of allowance/deduction
                        if allow_deduct.allowance_type=='family_relation':
                            if family_relation['rel_amount'] > 0:
                                amount += emp_dict['allow_deduct'].amount
                        else:
                            amount += emp_dict['allow_deduct'].amount
                    else:
                        #if type is complex compute the amounts of allowances that compose allowance/deduction 
                        #then take the percentage
                        complex_allow_ids = [allow.id for allow in allow_deduct.allowances_ids]
                        allow_complex = 0.0
                        complex_salary_ids = salary_allow_deduct_obj.search(cr, uid, [
                                                    ('allow_deduct_id', 'in', tuple(complex_allow_ids)),
                                                    ('payroll_id', '=', emp_dict['payroll']), ('degree_id', '=', emp_dict['degree'])])
                        if complex_salary_ids :
                            emp_comp_dict = emp_dict.copy()
                            for comp in salary_allow_deduct_obj.browse(cr, uid, complex_salary_ids):
                                #if comp.allow_deduct_id.id in allow_list:
                                emp_comp_dict.update({'allow_deduct':comp})
                                comp_allow_dict = self.allowances_deductions_amount(cr, uid, emp_comp_dict, allow_list)

                                if comp.allow_deduct_id.name_type == 'allow':
                                    allow_complex += comp_allow_dict['amount']
                                else:
                                    allow_complex -= comp_allow_dict['amount']
                        amount += allow_complex
                        amount = (amount * emp_dict['allow_deduct'].amount) / 100
                    # Linked Absence
                    if allow_deduct.linked_absence:
                        holiday_amount , remain_amount = self.allowances_linked_absence_calculation(cr, uid, emp_dict,amount)
                    if allow_deduct.distributed:
                        amount = amount / allow_deduct.distributed
                        if holiday_amount :
                            holiday_amount = holiday_amount / allow_deduct.distributed

                    # compute allowance/deduction amount based on marital status and number of children
                    if allow_deduct.related_marital_status:
                        family_relation=self.family_relation_calculation(cr, uid, emp_dict['emp_id'], emp_dict['date'])
                        married=False
                        if emp_dict['marital_status'] == 'married': married=True
                        children=family_relation['child_no']
                        if children > 1: children=1
                        status_ids = marital_status_obj.search(cr, uid, [
                                        ('allow_deduct_id', '=', allow_deduct.id),
                                        ('married', '=', married),('children_no', '=', children)])
                        if status_ids:
                            for record in marital_status_obj.browse(cr, uid, status_ids):
                                amount = (amount * record.percentage) / 100
                                tax_factor = record.taxable
                                perc = record.percentage / 100
                                if emp_dict['taxable'] and allow_deduct.name_type == 'allow' and allow_deduct.bonus_percent and not emp_dict['exemp_tax']:
                                    taxable = (amount / perc) * tax_factor
                                    tax_amount = (taxable * allow_deduct.bonus_percent) / 100
                    else:
                        # compute taxes for specific allowance for employees not exempted from taxes( exemp_tax is False)
                        if emp_dict['taxable'] and allow_deduct.name_type == 'allow' and allow_deduct.bonus_percent and not emp_dict['exemp_tax']:
                            if holiday_amount :
                                tax_amount = ((holiday_amount-exempted) * allow_deduct.bonus_percent) / 100
                            else:
                                tax_amount = ((amount-exempted) * allow_deduct.bonus_percent) / 100
                    if allow_deduct.stamp:
                        imprint = allow_deduct.stamp                             
        
        amount = amount * percent
        if check and allow_deduct.related_gender_type and allow_deduct.related_gender_type :
                        allow_gender = self.pool.get('hr.allowance.gender')
                        allow_gender_ids = allow_gender.search(cr , uid , [('gender' , '=' , emp_dict['gender']) , ('allow_deduct_id' , '=' , allow_deduct.id)])
                        values = allow_gender.read(cr , uid , [allow_gender_ids[0]] , ['value'])
                        value = values[0]['value']
                        amount = (amount * value) / 100

        return {'amount':amount, 'tax':tax_amount ,'holiday_amount':holiday_amount , 'remain_amount' : remain_amount,'imprint': imprint}

    def allowances_deductions_sp_calculation(self, cr, uid, emp_dict, allow_list):
        """
        Retrieve employee's special allowances and deductions.
        @param emp_dict: Dictionary of values
        @param allow_list: List of employee allowances and deductions ids
        @return: Dictionary of values 
        """
        allow_deduct_exception_obj = self.pool.get('hr.allowance.deduction.exception')
        amount= 0.0
        tax_amount = 0.0
        special_ids = allow_deduct_exception_obj.search(cr, uid, ['|', ('end_date', '>', emp_dict['date']), 
                         ('end_date', '=', False),('allow_deduct_id', '=', emp_dict['allow_deduct'].allow_deduct_id.id), 
                         ('employee_id', '=', emp_dict['emp_id']),('start_date', '<=', emp_dict['date']), ('action', '=', 'special')])
        if special_ids and not emp_dict['no_sp_rec']:
            for special in allow_deduct_exception_obj.browse(cr, uid, special_ids):
                if special.allow_deduct_id.in_salary_sheet:
                    if special.amount:
                        # If there is amount then take the amount directly 
                        amount += special.amount
                    else:
                        # If there is no amount then compute the amount from salary allowance deduction 
                        emp_dict.update({'special':True, })
                        allow_deduct_dict = self.allowances_deductions_amount(cr, uid, emp_dict, allow_list)
                        amount += allow_deduct_dict['amount']
                        tax_amount = allow_deduct_dict['tax']
                        emp_dict.update({'special':False, })
        if not special_ids  and emp_dict['no_sp_rec']:
            emp_dict.update({'special':True, })
            allow_deduct_dict = self.allowances_deductions_amount(cr, uid, emp_dict, allow_list)
            amount += allow_deduct_dict['amount']
            tax_amount = allow_deduct_dict['tax']
            emp_dict.update({'special':False, })
        return {'amount':amount, 'tax':tax_amount}

    def write_allow_deduct(self, cr, uid, emp_id, result_dict , emp_obj=False ):
        """
        write allowance/deduction amount for specific employee in employee salary model.
        @param emp_id: Id of employee 
        @param result_dict: List of dictionaries contains employee's allowance/deduction values
        @return: Boolean True
        """

        employee_salary_obj = self.pool.get('hr.employee.salary')
        unlink_ids = []
        if len(result_dict) >1 or emp_obj:
            check_allow_deduct = employee_salary_obj.search(cr, uid, [('employee_id', '=', emp_id)])
            allow_deduct_ids = []
            types = []
            if check_allow_deduct:
                for res in result_dict:
                    allow_deduct_ids.append(res['allow_deduct'].allow_deduct_id.id)
                    types.append(res['allow_deduct'].allow_deduct_id.name_type)
                for salary in employee_salary_obj.browse(cr, uid, check_allow_deduct):
                    if salary.allow_deduct_id.id not in allow_deduct_ids and salary.allow_deduct_id.name_type in types:
                        unlink_ids.append(salary.id)
        for res in result_dict:
            allow_deduct_dict = {
               'employee_id': emp_id,
               'allow_deduct_id': res['allow_deduct'].allow_deduct_id.id ,
               'type': res['allow_deduct'].allow_deduct_id.name_type,
               'amount': res['amount'] ,
               'holiday_amount': res['holiday_amount'] ,
               'remain_amount': res['remain_amount'] ,
               'tax_deducted': res['tax'],
               }
            check_allow = employee_salary_obj.search(cr, uid, [('employee_id', '=', emp_id), 
                                                               ('allow_deduct_id', '=', res['allow_deduct'].allow_deduct_id.id)])
            # check allowance/deduction in employee salary if it is already exist
            # and new amount > 0 make write on record with the new amount else unlink the record,
            # if it is not exist create record with the new amount
            if check_allow:
                if res['amount'] > 0:
                    employee_salary_obj.write(cr, uid, check_allow, allow_deduct_dict)
                else:
                    employee_salary_obj.unlink(cr, uid, check_allow)
            else:
                if res['amount'] > 0:
                    employee_salary_obj.create(cr, uid, allow_deduct_dict)
        employee_salary_obj.unlink(cr, uid, unlink_ids)
        return True

    def change_allow_deduct(self, cr, uid, allow_deduct_ids, scale_allow_deduct_ids ,emp_obj=False):
        """
        Recalculate allowances and deductions amount if the configuration changed .
        @param allow_deduct_ids: List of allownces/deductions ids 
        @param scale_allow_deduct_ids: List of salary scale allowances deductions ids 
        @return: True
        """
        salary_allow_deduct_obj = self.pool.get('hr.salary.allowance.deduction')
        allow_deduct_obj = self.pool.get('hr.allowance.deduction')
        employee_obj = self.pool.get('hr.employee')
        com_allow_deduct = []
        new_allow_deduct_ids = []
        emp_ids = []
        if scale_allow_deduct_ids:
            for rec in salary_allow_deduct_obj.browse(cr, uid, scale_allow_deduct_ids):
                if rec.allow_deduct_id.id not in new_allow_deduct_ids:
                    new_allow_deduct_ids.append(rec.allow_deduct_id.id)
        if allow_deduct_ids:
            for x in allow_deduct_ids:
                if x not in new_allow_deduct_ids:
                    new_allow_deduct_ids.append(x)
        for allow_deduct_rec in allow_deduct_obj.browse(cr,uid,new_allow_deduct_ids):
            date = time.strftime('%Y-%m-%d')
            emp_ids = []
            com_allow_deduct = []
            if allow_deduct_rec.in_salary_sheet:
                cr.execute('SELECT com_allow_deduct_id ' \
                           'FROM com_allow_deduct_rel c ' \
                           'JOIN hr_allowance_deduction a on (a.id=c.allowance_id) ' \
                           'WHERE a.in_salary_sheet = True AND a.special = False ' \
                           'AND allowance_id =%s',(allow_deduct_rec.id,))
                res = cr.fetchall()
                com_allow_deduct = [r[0] for r in res if res]
                scale_allow_deduct_ids = salary_allow_deduct_obj.search(cr, uid, [('allow_deduct_id', '=', allow_deduct_rec.id)])    
                if scale_allow_deduct_ids:
                    for allow_deduct in salary_allow_deduct_obj.browse(cr, uid, scale_allow_deduct_ids):
                            emp_ids1 = employee_obj.search(cr, uid, [('state', 'not in', ('draft', 'refuse')),
                                        ('payroll_id', '=', allow_deduct.payroll_id.id), ('degree_id', '=', allow_deduct.degree_id.id)])
                            for x in emp_ids1:
                                if x not in emp_ids:
                                    emp_ids.append(x)
                if emp_ids:
                    for emp in employee_obj.browse(cr, uid, emp_ids):
                        allow_deduct_dict = self.allowances_deductions_calculation(cr, uid, date, emp, {}, [allow_deduct_rec.id])
                        self.write_allow_deduct(cr, uid, emp.id, allow_deduct_dict['result'],emp_obj)
                if com_allow_deduct:
                    self.change_allow_deduct(cr, uid, com_allow_deduct, [])
        return True

    def create_payment(self, cr, uid, ids, vals = {}, context = None):
        """Method that transfers allowance/deduction to voucher.
           @para vals emp_obj: Dictionary of values
           @return: Id of created voucher
        """
        allow_deduct_obj = self.pool.get('hr.allowance.deduction')
        model_pool = self.pool.get(vals.get('model', 'account.voucher'))
        user = self.pool.get('res.users').browse(cr, uid, uid, context = context)
        reference = vals.get('reference')
        lines = vals.get('lines')
        tax_amount = vals.get('tax_amount', 0.0)
        ttype = vals.get('ttype', 'purchase')
        stamp_amount = vals.get('stamp_amount', 0.0)
        narration = vals.get('narration', '')
        journal_id = vals.get('journal_id')
        partner_id = vals.get('partner_id')
        in_salary_sheet= vals.get('in_salary_sheet',True)
        line_ids = []
        number = False
        for line in lines:
            keys = [key for key in line.keys()]
            account_analytic_id = False
            #account_analytic_id=user.department_id and user.department_id.account_analytic_id and user.department_id.account_analytic_id.id or False
            name = ''
            amount = line['amount']
            if 'account_analytic_id' in keys:
                account_analytic_id = line['account_analytic_id']
            if 'allow_deduct_id' in keys:
                allow_deduct = allow_deduct_obj.browse(cr, uid, line['allow_deduct_id'], context = context)
                account_id = allow_deduct.account_id and allow_deduct.account_id.id
                #custom_to_ntc
                account_analytic_id = allow_deduct.analytic_id and allow_deduct.analytic_id.id
                name = allow_deduct.name
                if allow_deduct.name_type == 'deduct':
                    amount = -line['amount']
            if 'account_id' in keys:
                account_id = line['account_id']
            if not account_id:
                raise osv.except_osv(_('ERROR'), _('Please enter account  for Allowances/deductions for %s')%(allow_deduct.name))
            if 'name' in keys:
                name = line['name'] or name
            
            line = {
                'name':name ,
                'account_id':account_id,
                'account_analytic_id':amount > 0 and account_analytic_id ,
                'amount':amount,
                'type':ttype=='purchase'and 'dr' or 'cr',
            }
            line_ids.append(line)

        if tax_amount:
            if not user.company_id.tax_account_id or not user.company_id.bon_tax_account_id:
                raise osv.except_osv(_('ERROR'), _('Please enter tax account for Your Company'))
            account_id= in_salary_sheet and user.company_id.tax_account_id.id or user.company_id.bon_tax_account_id.id
            tax_line = {
                'name': 'Taxes',
                'account_id':account_id,
                'account_analytic_id':False ,
                'amount':-tax_amount,
                'type':'dr',
            }
            line_ids.append(tax_line)

        if stamp_amount:
            if not user.company_id.stamp_account_id:
                raise osv.except_osv(_('ERROR'), _('Please enter imprint account for Your Company'))
            stamp_line = {
                'name':'Imprint',
                'account_id':user.company_id.stamp_account_id.id,
                'amount':-stamp_amount,
                'account_analytic_id':False ,
                'type':'dr',
            }
            line_ids.append(stamp_line)

        if line_ids:
            journal = journal_id or (ttype=='purchase' and user.company_id.hr_journal_id and user.company_id.hr_journal_id.id) or (ttype=='sale' and user.company_id.hr_rev_journal_id and user.company_id.hr_rev_journal_id.id) or False
            if not journal:
                raise osv.except_osv(_('ERROR'), _('Please Enter HR Journal for Your Company'))
            group_lines = self.group_lines(cr, uid, line_ids)
            currency_id = vals.get('currency_id') or (user.company_id.hr_journal_id.currency and user.company_id.hr_journal_id.currency.id) or user.company_id.currency_id.id
            rec_id = model_pool.create(cr, uid , {
                'company_id': user.company_id.id,
                'journal_id': journal,
                'account_id': account_id, # Doesn't exist in payment permanent 
                'type': ttype, # Doesn't exist in payment permanent
                'reference': reference,
                'narration': narration,
                'line_ids': group_lines['grouped'],
                'amount': group_lines['total'],
                'currency_id': currency_id,
                'partner_id': partner_id,
            }, context = context)

            if vals.get('model', 'account.voucher')=='account.voucher':
                number=rec_id
        return number

    def group_lines(self, cr, uid, lines):
        """Merge voucher lines  
           Lines will only be merged if:
             * Lines belong to the same account
             * Lines belong to the same analytic account
          @param lines: List of line dictionaries
          @return: Dictionary of values
        """
        line_grouped = {}
        total = 0.0
        for line in lines:
            key = (line['account_id'], line['account_analytic_id'])
            if not key in line_grouped:
                line_grouped[key] = line
            else:
                line_grouped[key]['amount'] += line['amount']
                line_grouped[key]['name'] = line_grouped[key]['name'] + "/" + line['name']
        grouped = []
        for key, val in line_grouped.items():
            grouped.append((0, 0, val))
            total += val['amount']
        return {'grouped': grouped, 'total':total}

    def current_salary_status(self, cr, uid,ids, emp_obj, date):
        """Retrieve employees's current salary amount.
           @param date: date
           @return: Current salary amount
        """
        tax=0
        sal_allow_deduct = self.allowances_deductions_calculation(cr, uid, date,emp_obj, {'no_sp_rec': False} ,[],False,[])
        total_allow = sal_allow_deduct.get('total_allow') + emp_obj.bonus_id.basic_salary
        if not emp_obj.tax_exempted:
            cr.execute('''select id from hr_payroll_main_archive where month=(select max(month) from hr_payroll_main_archive where year =(select max(year) from hr_payroll_main_archive where in_salary_sheet =%s and employee_id=%s) and in_salary_sheet =%s and employee_id=%s) and year=(select max(year) from hr_payroll_main_archive where in_salary_sheet =%s and employee_id=%s) and in_salary_sheet =%s and employee_id=%s''' , (True,emp_obj.id,True,emp_obj.id,True,emp_obj.id,True,emp_obj.id,))
            res = cr.fetchone()
            if res:
                tax = self.pool.get('hr.payroll.main.archive').browse(cr, uid, res[0]).tax
        total_deduct = sal_allow_deduct.get('total_deduct') + tax
        return  {'total_allow': total_allow, 'total_deduct':total_deduct, 'balance':total_allow - total_deduct,}

#vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
