# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

from osv import osv , fields
import time
from tools.translate import _
from datetime import datetime
import mx

#----------------------------------------------------------
# Payroll , contains all payroll functions
#----------------------------------------------------------
class payroll(osv.osv):

    _name = "payroll"
    _description = "Payroll"

    def family_relation_calculation(self, cr, uid, emp_id, date):
       """Method calculates amounts of family realtions.
          @param emp_id: Id of employee
          @param date: Current date
          @return: Dictionary of values , children amount , wife amount and number of children
       """
       context = {'rules':True}
       family_relation_obj = self.pool.get('hr.employee.family')
       rel_ids = family_relation_obj.search(cr, uid, [('employee_id', '=', emp_id), ('start_date', '<=', date), ('state', '=', 'approved')],context=context)
       rel_amount = 0.0
       wife_amount = 0.0
       ch_no = 0
       if rel_ids:
          for rel in family_relation_obj.browse(cr, uid, rel_ids,context=context):
             if not rel.end_date or rel.end_date > date :
                if rel.relation_id.max_age >= 0 and rel.relation_id.relation_type=='2':
                   # relation with max age is son relation
                   if rel.birth_date:
                      today_dt = time.mktime(time.strptime(date, '%Y-%m-%d'))
                      birth_dt = time.mktime(time.strptime(rel.birth_date, '%Y-%m-%d'))
                      diff_day = (today_dt - birth_dt) / (3600 * 24)
                      age = round(diff_day / 365) - 1
                      if age <= rel.relation_id.max_age:
                         ch_no += 1
                         if ch_no > rel.relation_id.max_number:
                            ch_no= rel.relation_id.max_number 
                         rel_amount = ch_no*rel.relation_id.amount
                     
                if rel.relation_id.max_age >= 0 and rel.relation_id.relation_type=='1':
                   # relation without max age is wife relation
                   wife_amount = rel.relation_id.amount
       return {'child_amount':rel_amount , 'wife_amount':wife_amount , 'child_no':ch_no}

    def qualification_calculation(self, cr, uid, emp_id):
       """Method that alculates the amount of qualification.
          @param emp_id: Id of employee
          @return: qualification amount 
       """
       emp_qual_obj = self.pool.get('hr.employee.qualification')
       qual_ids = emp_qual_obj.search(cr, uid, [('employee_id', '=', emp_id)])
       qual_amount = 0.0
       if qual_ids:
          # if the employee has approved qualifications
          qual_list = [q.emp_qual_id.id for q in emp_qual_obj.browse(cr, uid, qual_ids) if q.state == 'approved' and q.emp_qual_id]
          if qual_list:
             # get the qualification of the employee with the maximum order  
             cr.execute("select q.amount from hr_qualification q where q.order=(select max(q.order) from hr_qualification q where q.id in %s)" , (tuple(qual_list),))
             res = cr.fetchone()
             if res:
                qual_amount = res[0]
       return qual_amount

    def allowances_deductions_calculation(self, cr, uid, date, employee_obj, emp_dict, allow_deduct, substitution, allow_list):
       """Retrieve all employees's salary scale allowances and deductions, based on employee's salary scale and degree.
          @param date: Current date
          @param employee_obj: hr.employee record
          @param emp_dict: Dictionary of values
          @param allow_deduct: List of allowances and deductions ids 
          @param substitution: Bolean
          @param allow_list: List of employee allowances and deductions ids
          @return: Dictionary of data 
       """
       salary_scale_obj = self.pool.get('hr.salary.scale')
       salary_allow_deduct_obj = self.pool.get('hr.salary.allowance.deduction')
       employee_substitution_obj = self.pool.get('hr.employee.substitution')
       if not employee_obj:
           emp_id = emp_dict['emp_id']
       else:
          emp_id = employee_obj.id
       # calling qualification , family_relation and punishment functions
       qualification = self.qualification_calculation(cr, uid, emp_id)
       family_relation = self.family_relation_calculation(cr, uid, emp_id, date)
       family_chaild = self.family_relation_calculation(cr, uid, emp_id, date)
       substitution_setting = ''
       allow_amount = 0.0
       deduct_amount = 0.0
       result = []
       if not substitution:
          # if substitution False the emp_dict is empty and will be updated with employee's info , if its True it  contains employee's substitution info 
          if (not emp_dict) or (emp_dict and 'no_sp_rec' not in emp_dict.keys()) :
             emp_dict.update({'no_sp_rec': False})
          emp_dict .update({
                    'emp_id':employee_obj.id,
                    'company':employee_obj.company_id.id,
                    'department':employee_obj.department_id.id,
                    'job_id':employee_obj.job_id.id,
                    'category':employee_obj.category_ids,
                    'payroll':employee_obj.payroll_id.id,
                    'degree':employee_obj.degree_id.id,
                    'bonus':employee_obj.bonus_id.id,
                    'basic_salary':employee_obj.bonus_id.basic_salary,
                    'old_basic_salary':employee_obj.bonus_id.old_basic_salary,
                    'started_section':employee_obj.degree_id.basis,
                    'marital_status':employee_obj.marital,
                    'exemp_tax':employee_obj.tax_exempted,
                    'qualification': qualification,
                    'family_relation':family_relation,
                    'family_chaild':family_chaild,
                    'date':date,
                    'substitution':substitution,
                    'special': False ,
                    'degree':employee_obj.degree_id.id,
                    })
          # check if employee has sustitution
          domain = []
          domain += ['|', ('end_date', '>=', date), ('end_date', '=', False), ('employee_id', '=', emp_dict['emp_id']), ('start_date', '<=', date)]
          substitue_ids = employee_substitution_obj.search(cr, uid, domain, context = {'rules':True})
          if substitue_ids:
             for sub_record in employee_substitution_obj.browse(cr, uid, substitue_ids):
                scale = salary_scale_obj.read(cr, uid, [emp_dict['payroll']], ['sub_salary'])[0]
                emp_dict.update({'substitution_obj': sub_record,
                                 'substitution_setting':scale['sub_salary']})
                if scale['sub_salary'] == 'sustitut_degree':
                   # update emp_dict with employee's substitution degree if substitution setting=3 (Compute Allowances of Sustitution Degree) 
                   emp_dict.update({
                                    'payroll':sub_record.payroll_id.id,
                                    'degree':sub_record.degree_id.id,
                                    'started_section':sub_record.degree_id.basis,
                                    'bonus':sub_record.bonus_id.id,
                                    'basic_salary':sub_record.bonus_id.basic_salary,
                                    'old_basic_salary':sub_record.bonus_id.old_basic_salary})
       domain = [('payroll_id', '=', emp_dict['payroll']), ('degree_id', '=', emp_dict['degree'])]
       if allow_deduct:
          # if allow_deuct list is empty retrieve all allowances and deductions or retrieve only allowances and deductions specified on allow_deduct list
          domain += [('allow_deduct_id', 'in', tuple(allow_deduct))]
       allow_deduct_ids = salary_allow_deduct_obj.search(cr, uid, domain, context = {'rules':True})
       if allow_deduct_ids:
         if not allow_list:
            allow_list = [a.allow_deduct_id.id for a in salary_allow_deduct_obj.browse(cr, uid, allow_deduct_ids)]
         if allow_deduct:
          # if allow_deuct list is empty retrieve all allowances and deductions or retrieve only allowances and deductions specified on allow_deduct list
            domain += [('allow_deduct_id', 'in', tuple(allow_deduct))]
            allow_deduct_ids = salary_allow_deduct_obj.search(cr, uid, domain)
         sub_setting = salary_scale_obj.read(cr, uid, [emp_dict['payroll']], ['sub_setting'])[0]
         for record in salary_allow_deduct_obj.browse(cr, uid, allow_deduct_ids):
            tax_amount = 0.0
            # if substitution True check  pay_sheet settings (frist sheet only or first and second sheet)
            if (substitution and (sub_setting['sub_setting'] and (sub_setting['sub_setting'] == 'first' and record.allow_deduct_id.pay_sheet == 'first') or sub_setting['sub_setting'] == 'first_and_second') and record.allow_deduct_id.name_type == 'allow') or not substitution:
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
       """calculatethe amount of allowances and deductions.
          @param emp_dict: Dictionary of values
          @param allow_list: List of employee allowances and deductions ids
          @return: Dictionary of values 
       """
       salary_allow_deduct_obj = self.pool.get('hr.salary.allowance.deduction')
       allow_deduct_exception_obj = self.pool.get('hr.allowance.deduction.exception')
       marital_status_obj = self.pool.get('hr.allow.marital.status')
       allow_degree_obj = self.pool.get('hr.allowance.degree')
       emp_holiday_obj = self.pool.get('hr.holidays')
       main_arch_obj = self.pool.get('hr.payroll.main.archive')
       allow_deduct_arch_obj = self.pool.get('hr.allowance.deduction.archive')
       amount = 0.0
       holiday_amount = 0.0
       remain_amount = 0.0
       tax_amount = 0.0
       exempted = emp_dict['allow_deduct'].allow_deduct_id.exempted_amount
       check_categ = False
       check_job = False
       # check if allowance or deduction is special and special flag is false then call special function
       if emp_dict['allow_deduct'].allow_deduct_id.special and not emp_dict['special']:
          sp_dict = self.allowances_deductions_sp_calculation(cr, uid, emp_dict, allow_list)
          amount += sp_dict['amount']
          tax_amount += sp_dict['tax']
       else:
          # check employee allowance/deduction exclusion
          check = allow_deduct_exception_obj.search(cr, uid, ['|', ('end_date', '>', emp_dict['date']), ('end_date', '=', False), ('employee_id', '=', emp_dict['emp_id']), ('start_date', '<', emp_dict['date']), ('allow_deduct_id', '=', emp_dict['allow_deduct'].allow_deduct_id.id), ('action', '=', 'exclusion')],context = {'rules':True})
          if not check:
             # check start date , end date,company,departments and categories for specific allowance/deduction 
             if emp_dict['allow_deduct'].allow_deduct_id.start_date <= emp_dict['date'] and (not emp_dict['allow_deduct'].allow_deduct_id.end_date or (emp_dict['allow_deduct'].allow_deduct_id.end_date and emp_dict['allow_deduct'].allow_deduct_id.end_date >= emp_dict['date'])):
                if (emp_dict['allow_deduct'].allow_deduct_id.company_id and emp_dict['allow_deduct'].allow_deduct_id.company_id.id == emp_dict['company']) or not emp_dict['allow_deduct'].allow_deduct_id.company_id:
                   dept_list = []
                   cr.execute("select department_id from allow_deduct_department_rel where allow_deduct_id=%s" , (emp_dict['allow_deduct'].allow_deduct_id.id,))
                   res = cr.fetchall()
                   if res:
                      dept_list = [r[0] for r in res]
                   if not dept_list or (dept_list and emp_dict['department'] in dept_list):
                      #Check job
                      emp_job_id = emp_dict['job_id']
                      job_list = [job.id for job in emp_dict['allow_deduct'].allow_deduct_id.job_ids ]
                      if not job_list or emp_job_id in job_list:
                          check_job = True
                      allow_categs = emp_dict['allow_deduct'].allow_deduct_id.category_ids
                      if not allow_categs:
                         check_categ = True
                      else:
                         if emp_dict['category'] and [emp_categ.id for emp_categ in emp_dict['category'] if emp_categ in allow_categs]:
                            check_categ = True
                      
                      if check_job and check_categ:
                         if emp_dict['allow_deduct'].allow_deduct_id.salary_included:
                            amount += emp_dict['basic_salary']
                         if emp_dict['allow_deduct'].allow_deduct_id.old_salary_included :
                            amount += emp_dict['old_basic_salary']
                         if emp_dict['allow_deduct'].allow_deduct_id.started_section_included:
                            amount += emp_dict['started_section']                        
                         if emp_dict['allow_deduct'].allow_deduct_id.allowance_type=='qualification':
                            #if emp_dict['qualification']:
                            amount += emp_dict['qualification']
                         if emp_dict['allow_deduct'].allow_deduct_id.allowance_type=='family_relation':
                            #if emp_dict['family_relation']:
                            amount +=  emp_dict['family_relation']['wife_amount']
                         if emp_dict['allow_deduct'].allow_deduct_id.allowance_type=='family_chaild':
                            #if emp_dict['family_chaild']:
                            amount += emp_dict['family_chaild']['child_amount'] 
                         if emp_dict['allow_deduct'].allow_deduct_id.allowance_type=='substitution':
                            if not emp_dict['substitution']:
                               if 'substitution_obj' in emp_dict:
                                  if emp_dict['substitution_setting'] == 'diff':
                                     #print"ttttttttttttttttttttttttttttttttttttttttttttttttttttttttt amount ",amount
                                  # calculate substitution amount by subtract total allowances of current degree from total allowance of substiution degree if substitution setting = 2 (Compute Difference Between The 2 Degree)
                                     emp_curr_dict = emp_dict.copy()
                                     emp_curr_dict.update({'substitution':True})
                                     # calling allowances_deductions_calculation function to retrieve total of allowances amount of current degree
                                     curr_allow_dict = self.allowances_deductions_calculation(cr, uid, emp_curr_dict['date'], [], emp_curr_dict, [], emp_curr_dict['substitution'], [])
                                     curr_allow_dict['total_allow'] += emp_curr_dict['basic_salary']
                                     #print"33333333333333333333333333333333333333333333333333333 amount ",amount
                                     #print"++++++++++++++++++++++++++++++++++++++org salary",curr_allow_dict['total_allow']
                                     emp_sub_dict = emp_dict.copy()
                                     emp_sub_dict.update({
                                                    'payroll':emp_sub_dict['substitution_obj'].payroll_id.id,
                                                    'degree':emp_sub_dict['substitution_obj'].degree_id.id,
                                                    'bonus':emp_sub_dict['substitution_obj'].bonus_id.id,
                                                    'basic_salary':emp_sub_dict['substitution_obj'].bonus_id.basic_salary,
                                                    'old_basic_salary':emp_sub_dict['substitution_obj'].bonus_id.old_basic_salary,
                                                    'started_section':emp_sub_dict['substitution_obj'].degree_id.basis,
                                                    'substitution':True,
                                                    })
                                     # calling allowances_deductions_calculation function to retrieve total of allowances amount of substitution degree
                                     sub_allow_dict = self.allowances_deductions_calculation(cr, uid, emp_sub_dict['date'], [], emp_sub_dict, [], emp_sub_dict['substitution'], [])
                                     sub_allow_dict['total_allow'] += emp_sub_dict['basic_salary']
                                     #print"++++++++++++++++++++++++++++++++++++++new salary",sub_allow_dict['total_allow']
                                     substitution_amount = sub_allow_dict['total_allow'] - curr_allow_dict['total_allow']
                                     sub_config=self.pool.get('hr.salary.scale').browse(cr, uid, [emp_dict['payroll']])[0]
                                     #print"*************************orginal***************substitution_amount ",sub_config
                                     if sub_config and sub_config.sub_prcnt_selection and sub_config.sub_percentage >0:
                                         #print"------------------------------sub_config",sub_config.sub_prcnt_selection, sub_config.sub_percentage
                                         #print"----------------------normal way---------substitution_amount",substitution_amount
                                         emp_slry_prcnt=curr_allow_dict['total_allow']*sub_config.sub_percentage/100
                                         #print"-------------------------------emp_slry_prcnt",emp_slry_prcnt
                                         if  sub_config.sub_prcnt_selection=='percentge':
                                             #print"55555555 55555 5555 555 55 5,percentge"
                                             substitution_amount=emp_slry_prcnt
                                         elif  sub_config.sub_prcnt_selection=='bigest':
                                             #print"55555555 55555 5555 555 55 5,bigest"
                                             substitution_amount=emp_slry_prcnt > substitution_amount and emp_slry_prcnt or substitution_amount
                                         elif  sub_config.sub_prcnt_selection=='smalest':
                                             #print"55555555 55555 5555 555 55 5,smalest"
                                             substitution_amount=emp_slry_prcnt < substitution_amount and emp_slry_prcnt or substitution_amount
                                     #print"**************************************** substitution_amount",substitution_amount
                                     amount += substitution_amount
                                     emp_dict.update({'substitution':False})
                         if emp_dict['allow_deduct'].allow_deduct_id.type == 'amount':
                            # if type is price add the amount of allowance/deduction
                            amount += emp_dict['allow_deduct'].amount
                         else:
                            # if type is complex compute the amounts of allowances that compose allowance/deduction then take the percentage
                            ids_list = [allow.id for allow in emp_dict['allow_deduct'].allow_deduct_id.allowances_ids]
                            domain = [('allow_deduct_id', 'in', tuple(ids_list)), ('payroll_id', '=', emp_dict['payroll']), ('degree_id', '=', emp_dict['degree'])]
                            allow_com = 0.0
                            #print">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>comxxxx",amount
                            other_allow_ids = salary_allow_deduct_obj.search(cr, uid, domain, context = {'rules':True})
                            if other_allow_ids:
                               emp_com_dict = emp_dict.copy()
                               for o in salary_allow_deduct_obj.browse(cr, uid, other_allow_ids, context = {'rules':True}):
                                  #if o.allow_deduct_id.id in allow_list:
                                     emp_com_dict.update({'allow_deduct':o},)
                                     com_allow_dict = self.allowances_deductions_amount(cr, uid, emp_com_dict, allow_list)
                                     if o.allow_deduct_id.name_type == 'allow':
                                        allow_com += com_allow_dict['amount']
                                     else:
                                        allow_com -= com_allow_dict['amount']
                                        #print">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>comxxxx amount allow_com",amount ,allow_com 
                            amount += allow_com
                            allow_per = (amount * emp_dict['allow_deduct'].amount) / 100
                            amount = allow_per
                            #print">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>comxxxx",amount
                         if emp_dict['allow_deduct'].allow_deduct_id.linked_absence:
                            curr_date = datetime.strptime(emp_dict['date'], '%Y-%m-%d')
                            if emp_dict['allow_deduct'].allow_deduct_id.in_salary_sheet:
                               in_salary_sheet = True
                            else:
                               in_salary_sheet = False
                            cr.execute("select id from hr_payroll_main_archive where month=(select max(month) from hr_payroll_main_archive where year =(select max(year) from hr_payroll_main_archive where in_salary_sheet =%s and employee_id=%s) and in_salary_sheet =%s and employee_id=%s) and year=(select max(year) from hr_payroll_main_archive where in_salary_sheet =%s and employee_id=%s) and in_salary_sheet =%s and employee_id=%s" , (in_salary_sheet,emp_dict['emp_id'],in_salary_sheet,emp_dict['emp_id'],in_salary_sheet,emp_dict['emp_id'],in_salary_sheet,emp_dict['emp_id'],))
                            res = cr.fetchone()
                            if res:
                               prev_salary_date=main_arch_obj.browse(cr,uid,res[0])
                               domain=[]
                               domain += ['|','|', ('date_to','<=',emp_dict['date']),('date_to','>=',emp_dict['date']),('date_to','>',prev_salary_date.salary_date)]
                               domain += ['|','|',('date_from','>=',prev_salary_date.salary_date), ('date_from','<=',prev_salary_date.salary_date),('date_from','<=',emp_dict['date'])]
                               domain+= [('employee_id','=',emp_dict['emp_id']),('state','in',('validate','done_cut'))]
                               if emp_dict['allow_deduct'].allow_deduct_id.holiday_ids:
                                  domain+= [('holiday_status_id','in',[holiday.id for holiday in emp_dict['allow_deduct'].allow_deduct_id.holiday_ids])]
                               emp_holidays_ids= emp_holiday_obj.search(cr,uid,domain, context = {'rules':True})
                               days=0
                               if emp_holidays_ids:
                                  #emp_abs_ids= emp_holiday_obj.browse(cr,uid,emp_holidays_ids)
                                  #print "abs serch" , emp_abs_ids  
                                  for holiday in emp_holiday_obj.browse(cr,uid,emp_holidays_ids):
                                           from_dt = time.mktime(time.strptime(holiday.date_from,'%Y-%m-%d %H:%M:%S'))
                                           to_dt = time.mktime(time.strptime(holiday.date_to,'%Y-%m-%d %H:%M:%S'))
                                           prev_dt = time.mktime(time.strptime(prev_salary_date.salary_date,'%Y-%m-%d'))
                                           bonus_dt = time.mktime(time.strptime(emp_dict['date'],'%Y-%m-%d'))   
                                           date_t = mx.DateTime.Parser.DateTimeFromString(holiday.date_to)
                                           date_f = mx.DateTime.Parser.DateTimeFromString(holiday.date_from)
                                           if date_t.month == curr_date.month and date_t.year == curr_date.year:
                                              if date_f.month == curr_date.month:
                                                 days+= holiday.number_of_days_temp
                                              elif (date_f.month < curr_date.month and date_t.year == curr_date.year) or (date_f.month > curr_date.month and date_f.year == curr_date.year-1):
                                                 if  holiday.create_date > prev_salary_date.salary_date:
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
                               emp_prev_allow = allow_deduct_arch_obj.search(cr,uid,[('allow_deduct_id','=',emp_dict['allow_deduct'].allow_deduct_id.id),('main_arch_id','=',prev_salary_date.id)], context = {'rules':True})
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
                         if emp_dict['allow_deduct'].allow_deduct_id.related_marital_status == 'yes':
                            # compute allowance/deduction amount based on marital status and number of children if alternative_cash is True
                            status_ids = marital_status_obj.search(cr, uid, [('allow_deduct_id', '=', emp_dict['allow_deduct'].allow_deduct_id.id)], context = {'rules':True})
                            if status_ids:
###########################################skn gndy###################################
                               allow_deduct= emp_dict['allow_deduct'].allow_deduct_id
                               res_all = allow_degree_obj.search(cr , uid , [('degree_id' , '=' , emp_dict['degree']) , ('allow_deduct_id' , '=' , allow_deduct.id)])
		               if res_all:
                                       values = allow_degree_obj.read(cr , uid , res_all , ['value'])
                                       amount = amount * values[0]['value']  / 100
				       #print ".........allow_degree_ids.........................",values[0]['value'] 
#######################################################################################
                               family_relation=emp_dict['family_relation']
                               for record in marital_status_obj.browse(cr, uid, status_ids):
                                  
                                  '''if (emp_dict['marital_status'] != 'married' and record.married and ((family_relation['child_amount'] == 0 and record.children_no == 0) or (family_relation['child_amount'] > 0 and record.children_no) and  (family_relation['child_no'] == record.children_no) or (family_relation['child_amount'] > 0 and record.children_no and family_relation['child_no'] > record.children_no and record.children_no != 1))) or (emp_dict['marital_status'] == 'single' and not record.married  and  family_relation['child_amount'] == 0 and record.children_no == 0) :
                                     if emp_dict['allow_deduct'].allow_deduct_id.distributed:
                                        alter_amount = alter_amount / emp_dict['allow_deduct'].allow_deduct_id.distributed
                                        amount = alter_amount
                                     if emp_dict['allow_deduct'].allow_deduct_id.name_type == 'allow' and emp_dict['allow_deduct'].allow_deduct_id.bonus_percent:
                                        if not emp_dict['exemp_tax']:
                                           taxable = ((amount-exempted) / perc) * tax_factor
                                           tax_amount = (taxable * emp_dict['allow_deduct'].allow_deduct_id.bonus_percent) / 100
                                     break'''
 				  if (emp_dict['marital_status'] == 'single' and not record.married  and  family_relation['child_amount'] >= 0 and record.children_no == 0 and not res_all) :
                                     print "...............................111..................................." 
                                     alter_amount = (amount * record.percentage) / 100
                                     tax_factor = record.taxable
                                     perc = record.percentage / 100
				     amount = alter_amount

				  if (emp_dict['marital_status'] == 'married' and record.married  and  family_relation['wife_amount'] >= 0 and record.children_no == 0 and not res_all) :
                                     print "..............................222.................................."
                                     alter_amount = (amount * record.percentage) / 100
                                     tax_factor = record.taxable
                                     perc = record.percentage / 100
				     amount = alter_amount

				  if (emp_dict['marital_status'] == 'divorced'  and record.married  and  family_relation['wife_amount'] >= 0 and record.children_no == 0 and not res_all) :
                                     print "..............................333..................................",family_relation
                                     alter_amount = (amount * record.percentage) / 100
                                     tax_factor = record.taxable
                                     perc = record.percentage / 100
				     amount = alter_amount

				  if (emp_dict['marital_status'] == 'widower' and record.married  and  family_relation['wife_amount'] >= 0 and record.children_no == 0 and not res_all) :
                                     print "..............................333..................................",family_relation
                                     alter_amount = (amount * record.percentage) / 100
                                     tax_factor = record.taxable
                                     perc = record.percentage / 100
				     amount = alter_amount

                         else:
                            if emp_dict['allow_deduct'].allow_deduct_id.distributed:
                               amount = amount / emp_dict['allow_deduct'].allow_deduct_id.distributed
                               if holiday_amount :
                                  holiday_amount = holiday_amount / emp_dict['allow_deduct'].allow_deduct_id.distributed
                            if emp_dict['allow_deduct'].allow_deduct_id.name_type == 'allow' and emp_dict['allow_deduct'].allow_deduct_id.bonus_percent > 0:
                               # compute taxes for specific allownace for employees not exempted from taxes( exemp_tax is False)
                               if not emp_dict['exemp_tax']:
                                  if holiday_amount :
                                     tax_amount = ((holiday_amount-exempted) * emp_dict['allow_deduct'].allow_deduct_id.bonus_percent) / 100
                                  else:
                                     tax_amount = ((amount-exempted) * emp_dict['allow_deduct'].allow_deduct_id.bonus_percent) / 100
       allow_deduct_dict = {'amount':amount, 'tax':tax_amount, 'holiday_amount':holiday_amount , 'remain_amount' : remain_amount,'imprint': emp_dict['allow_deduct'].allow_deduct_id.stamp}
       #if emp_dict['allow_deduct'].allow_deduct_id.allowance_type=='substitution' and emp_dict['allow_deduct'].allow_deduct_id.id==1:
          # print"fffffffffffffffffffffffffffffffffffffffffffff+++amount",amount,emp_dict['allow_deduct'].allow_deduct_id.allowance_type
       #print"***************************" ,allow_deduct_dict
       return allow_deduct_dict

    def allowances_deductions_sp_calculation(self, cr, uid, emp_dict, allow_list):
       """Retrieve employee's special allowances and deductions.
          @param emp_dict: Dictionary of values
          @param allow_list: List of employee allowances and deductions ids
          @return: Dictionary of values 
       """
       allow_deduct_exception_obj = self.pool.get('hr.allowance.deduction.exception')
       allow_deduct_amount_sp = 0.0
       tax_amount = 0.0
       allow_deduct_sp_ids = allow_deduct_exception_obj.search(cr, uid, ['|', ('end_date', '>', emp_dict['date']), ('end_date', '=', False), ('allow_deduct_id', '=', emp_dict['allow_deduct'].allow_deduct_id.id), ('employee_id', '=', emp_dict['emp_id']), ('start_date', '<=', emp_dict['date']), ('action', '=', 'special')],context = {'rules':True})
       if allow_deduct_sp_ids and not emp_dict['no_sp_rec']:
          for sp in allow_deduct_exception_obj.browse(cr, uid, allow_deduct_sp_ids):
             if sp.allow_deduct_id.in_salary_sheet:
                if sp.amount:
                   # if there is amount in hr allowance deduction exception record then take the amount directly 
                   allow_deduct_amount_sp += sp.amount
                else:
                   # if there is no amount in hr allowance deduction exception record then compute the amount from salary allowance deduction 
                         emp_dict.update({'special':True, })
                         allow_deduct_dict = self.allowances_deductions_amount(cr, uid, emp_dict, allow_list)
                         allow_deduct_amount_sp += allow_deduct_dict['amount']
                         tax_amount = allow_deduct_dict['tax']
                         emp_dict.update({'special':False, })
       if not allow_deduct_sp_ids and emp_dict['no_sp_rec']:
          emp_dict.update({'special':True, })
          allow_deduct_dict = self.allowances_deductions_amount(cr, uid, emp_dict, allow_list)
          allow_deduct_amount_sp += allow_deduct_dict['amount']
          tax_amount = allow_deduct_dict['tax']
          emp_dict.update({'special':False, })
       return {'amount':allow_deduct_amount_sp, 'tax':tax_amount}

    def write_allow_deduct(self, cr, uid, emp_id, result_dict , emp_obj=False):
       """write allownce/deduction amount for specific employee in employee salary model .
         @param emp_id: Id of employee 
         @param result_dict: List of dictionaries contains employee's allowance/deduction values
         @return: Boolean True
       """
       employee_salary_obj = self.pool.get('hr.employee.salary')
       unlink_ids = []
       if len(result_dict) > 1 or emp_obj:
          check_allow_deduct = employee_salary_obj.search(cr, uid, [('employee_id', '=', emp_id)],context = {'rules':True})
          allow_deduct_ids = []
          types = []
          if check_allow_deduct:
             for res in result_dict:
                allow_deduct_ids.append(res['allow_deduct'].allow_deduct_id.id)
                types.append(res['allow_deduct'].allow_deduct_id.name_type)
             for salary in employee_salary_obj.browse(cr, uid, check_allow_deduct,context = {'rules':True}):
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
          check_allow = employee_salary_obj.search(cr, uid, [('employee_id', '=', emp_id), ('allow_deduct_id', '=', res['allow_deduct'].allow_deduct_id.id)],context = {'rules':True})
          # check allowance/deduction in employee salary if it is already exist and new amount > 0 make write on record with the new amount else unlink the record, if it is not exist create record with the new amount
          if check_allow:
             if res['amount'] > 0:
                update = employee_salary_obj.write(cr, uid, check_allow, allow_deduct_dict,context = {'rules':True})
             else:
                delete = employee_salary_obj.unlink(cr, uid, check_allow,context = {'rules':True})
          else:
             if res['amount'] > 0:
                create = employee_salary_obj.create(cr, uid, allow_deduct_dict,context = {'rules':True})
       delete = employee_salary_obj.unlink(cr, uid, unlink_ids,context = {'rules':True})
       return True

   # def change_allow_deduct(self, cr, uid, allow_deduct_id, scale_allow_deduct_id,emp_obj=False):
    def change_allow_deduct(self, cr, uid, allow_deduct_ids, scale_allow_deduct_ids, emp_obj=False):
		"""
		Recalculate allowances and deductions amount if the configuration changed .
		@param allow_deduct_ids: List of allownces/deductions ids 
		@param scale_allow_deduct_ids: List of salary scale allowances deductions ids 
		@return: True
		"""
		
		salary_allow_deduct_obj = self.pool.get('hr.salary.allowance.deduction')
		employee_obj = self.pool.get('hr.employee')
		if allow_deduct_ids:
			scale_allow_deduct_ids = salary_allow_deduct_obj.search(cr, uid, [('allow_deduct_id', 'in', tuple(allow_deduct_ids))])
		if scale_allow_deduct_ids:
			date = time.strftime('%Y-%m-%d')	
			for allow_deduct in salary_allow_deduct_obj.browse(cr, uid, scale_allow_deduct_ids):
				if allow_deduct.allow_deduct_id.in_salary_sheet:
					cr.execute('SELECT com_allow_deduct_id ' \
							   'FROM com_allow_deduct_rel c ' \
							   'JOIN hr_allowance_deduction a on (a.id=c.allowance_id) ' \
							   'WHERE a.in_salary_sheet = True ' \
							   'AND allowance_id =%s',(allow_deduct.allow_deduct_id.id,))
					res = cr.fetchall()
					com_allow_deduct = [r[0] for r in res if res]
					update_ids = salary_allow_deduct_obj.search(cr, uid, [('allow_deduct_id', 'in', tuple(com_allow_deduct)),
																		  ('degree_id', '=', allow_deduct.degree_id.id)],context = {'rules':True})
																		  
					cr.execute("SELECT id  FROM hr_employee WHERE state not in ('draft', 'refuse') AND degree_id =%s",(allow_deduct.degree_id.id,))
					res2 = cr.fetchall()
					emp_ids = [e[0] for e in res2 ]
	                
					#emp_ids = employee_obj.search(cr, uid, [('state', 'not in', ('draft', 'refuse')),
								#('payroll_id', '=', allow_deduct.payroll_id.id), ('degree_id', '=', allow_deduct.degree_id.id)])
					if emp_ids:

						for emp in employee_obj.browse(cr, uid, emp_ids):
							allow_deduct_dict = self.allowances_deductions_calculation(cr, uid, date, emp, {}, [allow_deduct.allow_deduct_id.id], False, [])
							
							self.write_allow_deduct(cr, uid, emp.id, allow_deduct_dict['result'],emp_obj=False)
						if com_allow_deduct:
							self.change_allow_deduct(cr, uid, [], update_ids)
		return True
    def read_allowance_deduct(self, cr, uid, emp_id, allow_deduct, allow_deduct_type):
       """Read allowances and deductions amount from employee salary object .
          @param emp_id: Id of employee
          @param allow_deduct: List of allowances/deductions ids 
          @param allow_deduct_type: Type allowance or deduction
          @return: Total of amount
       """
       total_amount = 0.0
       emp_salary_obj = self.pool.get('hr.employee.salary')
       payroll_obj = self.pool.get('payroll')
       employee_obj = self.pool.get('hr.employee')
       domain = [('employee_id', '=', emp_id)]
       if allow_deduct_type:
          # if type is specified return only the amount of specified type or return all amount 
          domain += [('type', '=', allow_deduct_type)]
       if allow_deduct:
          # if list of allow_deduct is empty return amount of all allowance and deduction or return amount of allowance/deduction specified in list
          for item in allow_deduct:
             allow_domain = [('allow_deduct_id', '=', item)]
             emp_salary_ids = emp_salary_obj.search(cr, uid, domain + allow_domain)
             if emp_salary_ids:
                for emp_salary in emp_salary_obj.browse(cr, uid, emp_salary_ids) :
                   total_amount += emp_salary.amount
             else:
                employee = employee_obj.browse(cr, uid, emp_id)
                date = time.strftime('%Y-%m-%d')
                allow_deduct_dict = payroll_obj.allowances_deductions_calculation(cr, uid, date, employee, {}, [item], False, [])
                if allow_deduct_type == 'allow':
                   total_amount += allow_deduct_dict['total_allow']
                else:
                   total_amount += allow_deduct_dict['total_deduct']
       else:
          emp_salary_ids = emp_salary_obj.search(cr, uid, domain)
          if emp_salary_ids:
             for emp_salary in emp_salary_obj.browse(cr, uid, emp_salary_ids) :
                total_amount += emp_salary.amount
       return total_amount

    def compute_allowance_deduction(self, cr, uid, emp_obj, allow_deduct_id, context = None):
        """Computes allowances and deductions amount for missions , loans , extra allowances ,training and subsidy from employee salary model .
           @param emp_obj: hr.employee record
           @param allow_deduct_id: Id of allowance/deduction 
           @return: Dictionary of allowance/deduction values
        """
        allow_deduct_obj = self.pool.get('hr.salary.allowance.deduction')
        payroll_obj = self.pool.get('payroll')
        allow_total = 0.0
        tax_amount = 0.0
        imprint = 0.0
        scale_allow_duduct_ids = allow_deduct_obj.search(cr, uid, [('allow_deduct_id', '=', allow_deduct_id),
                                                                   ('payroll_id', '=', emp_obj.payroll_id.id),
                                                                   ('degree_id', '=', emp_obj.degree_id.id)],
                                                         context = context)
        if scale_allow_duduct_ids:
            for allow_deduct in allow_deduct_obj.browse(cr, uid, scale_allow_duduct_ids, context = context):
                allow_total = payroll_obj.read_allowance_deduct(cr, uid, emp_obj.id, [allow_deduct.allow_deduct_id.id], 'allow')
                if allow_deduct.allow_deduct_id.bonus_percent:
                    if not emp_obj.tax_exempted:
                        tax_amount = allow_total * allow_deduct.allow_deduct_id.bonus_percent / 100
                if allow_deduct.allow_deduct_id.stamp:
                    imprint = allow_deduct.allow_deduct_id.stamp
        return {'amount': allow_total , 'tax_amount': tax_amount , 'imprint': imprint, }

    #======================
    #voucher_create
    #======================
    def create_payment(self, cr, uid, ids, vals = {}, context = None):
        """Method that transfers allowance/deduction to voucher.
           @para vals emp_obj: Dictionary of values
           @return: Id of created voucher
        """
        salary_obj = self.pool.get('hr.employee.salary.addendum')
        allow_deduct_obj = self.pool.get('hr.allowance.deduction')
        model_pool = self.pool.get(vals.get('model', 'account.voucher'))
        tax_obj = self.pool.get('hr.tax')
        user = self.pool.get('res.users').browse(cr, uid, uid, context = context)
        reference = vals.get('reference')
        lines = vals.get('lines')
        tax_amount = vals.get('tax_amount', 0.0)
        ttype = vals.get('ttype', 'purchase')
        stamp_amount = vals.get('stamp_amount', 0.0)
        narration = vals.get('narration', '')
        journal_id = vals.get('journal_id')
        partner_id = vals.get('partner_id')
        line_ids = []
        number = False
        addendum = False
        rec_id = False
        ######## for move create #######
        payroll_journal_id = user.company_id.payroll_journal_id and user.company_id.payroll_journal_id.id or False
        if not payroll_journal_id:
            raise osv.except_osv(_('ERROR'), _('Please Enter Payroll Journal for Your Company'))

        payroll_account_id = user.company_id.payroll_account_id and user.company_id.payroll_account_id.id or False
        if not payroll_account_id:
            raise osv.except_osv(_('ERROR'), _('Please Enter Payroll Journal for Your Company'))
        ctx = dict(context, account_period_prefer_normal=True)
        periods = self.pool.get('account.period').find(cr, uid, context=ctx)
        company_currency = user.company_id.currency_id.id
        tot_line = 0.0
        move_line_ids = []
        move_id = False
        ############### line name ##################
	if 'salary_name' in vals:
	    salary_name = vals['salary_name']
	if not 'salary_name' in vals:
	    for rec in salary_obj.browse(cr, uid,ids):
		salary_name=rec.name
		#print"MMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMM",salary_name
        for line in lines:
            keys = [key for key in line.keys()]
            account_analytic_id = False
            #account_analytic_id=user.department_id and user.department_id.account_analytic_id and user.department_id.account_analytic_id.id or False
            name = ''
            amount = line['amount']
            if 'allow_deduct_id' in keys:
                allow_deduct = allow_deduct_obj.browse(cr, uid, line['allow_deduct_id'], context = context)
                account_id = allow_deduct.account_id and allow_deduct.account_id.id
                name = allow_deduct.name
                if allow_deduct.name_type == 'deduct':
                    amount = -line['amount']
                if not allow_deduct.in_salary_sheet and not allow_deduct.allowance_type == 'in_cycle' and allow_deduct.allowance_type == 'general':
                    addendum = True
            if 'account_id' in keys:
                account_id = line['account_id']
            if not account_id:
                raise osv.except_osv(_('ERROR'), _('Please enter account  for Allowances/deductions for %s')%(allow_deduct.name))
            if 'name' in keys:
                name = line['name'] or name
            if 'account_analytic_id' in keys:
                account_analytic_id = line['account_analytic_id']
            line = {
                'name':name ,
                'account_id':account_id,
                'account_analytic_id':amount > 0 and account_analytic_id ,
                'amount':amount,
                'type':ttype=='purchase'and 'dr' or 'cr',
            }
            line_ids.append(line)
            ##### for move line #####
            amount = self._convert_amount(cr, uid, amount, company_currency, context=ctx)
            if amount != 0 :
              move_type =  ttype=='purchase' and 'dr' or 'cr'
              debit = 0.0
              credit = 0.0
              if amount < 0:
                  amount = -amount
                  if move_type == 'dr':
                      move_type = 'cr'
                  else:
                      move_type = 'dr'

              if (move_type=='dr'):
                  tot_line += amount
                  debit = amount
              else:
                  tot_line -= amount
                  credit = amount

              move_line = {
                  'journal_id': payroll_journal_id,
                  'period_id': periods and periods[0] or False,
                  'name': salary_name or '/',
                  'account_id': account_id,
                  #'move_id': move_id,
                  'partner_id': False,
                  #'currency_id': company_currency or False,
                  'analytic_account_id': account_analytic_id or False,
                  'quantity': 1,
                  'credit': credit,
                  'debit': debit,
                  #'date': voucher.date
              }
              #move_line_ids.append((0,0,move_line))
              move_line_ids.append(move_line)

        if tax_amount:
            taxes_ids = tax_obj.search(cr, uid, [])
            if not taxes_ids:
                raise osv.except_osv(_('ERROR'), _('Please enter tax configuration'))
            taxes_obj = tax_obj.browse(cr, uid, taxes_ids)[0]
            if  not taxes_obj.account_id:
                raise osv.except_osv(_('ERROR'), _('Please enter account for taxes in tax configuration'))
            tax_line = {
                'name': 'Taxes',
                'account_id':taxes_obj.account_id.id,
                'account_analytic_id':False ,
                'amount':-tax_amount,
                'type':'dr',
            }
            line_ids.append(tax_line)

            ##################### move line ################
            tax_move_line = {
                  'journal_id': payroll_journal_id,
                  'period_id': periods and periods[0] or False,
                  'name': 'Taxes',
                  'account_id': taxes_obj.account_id.id,
                  #'move_id': move_id,
                  'partner_id': False,
                  #'currency_id': company_currency or False,
                  'analytic_account_id': False,
                  'quantity': 1,
                  'credit': tax_amount,
                  'debit': 0.0,
                  #'date': voucher.date
            }
            #move_line_ids.append((0,0,tax_move_line))
            move_line_ids.append(tax_move_line)
            tot_line -= tax_amount

        if stamp_amount:
            if not user.company_id.stamp_account_id:
                raise osv.except_osv(_('ERROR'), _('Please enter account for imprint in tax configuration'))
            stamp_line = {
                'name':'Imprint',
                'account_id':user.company_id.stamp_account_id.id,
                'amount':-stamp_amount,
                'account_analytic_id':False ,
                'type':'dr',
            }
            line_ids.append(stamp_line)

            ##################### move line ################
            stamp_move_line = {
                  'journal_id': payroll_journal_id,
                  'period_id': periods and periods[0] or False,
                  'name': 'Imprint',
                  'account_id': user.company_id.stamp_account_id.id,
                  #'move_id': move_id,
                  'partner_id': False,
                  #'currency_id': company_currency or False,
                  'analytic_account_id': False,
                  'quantity': 1,
                  'credit': stamp_amount,
                  'debit': 0.0,
                  #'date': voucher.date
            }
            #move_line_ids.append((0,0,stamp_move_line))
            move_line_ids.append(stamp_move_line)
            tot_line -= stamp_amount


        if 'salary_compute' in context and context['salary_compute']:
              if move_line_ids:

                  total_move_line = {
                  'name': '/',
                  'account_id': payroll_account_id,
                  #'move_id': move_id,
                  'partner_id': False,
                  #'date': voucher.date,
                  'credit': tot_line > 0 and tot_line or 0.0,
                  'debit': tot_line < 0 and -tot_line or 0.0,
                  #'amount_currency': company_currency <> current_currency and (sign * -1 * voucher.writeoff_amount) or 0.0,
                  #'currency_id': company_currency or False,
                  'analytic_account_id': False,
                  }

                  #move_line_ids.append((0,0,total_move_line))
                  move_line_ids.append(total_move_line)
                  group_move_lines = self.group_move_lines(cr, uid, move_line_ids)


                  move_id = self.pool.get('account.move').create(cr, uid, {
                      #'name': name,
                      #'journal_id': voucher.journal_id.id,
                      'journal_id': payroll_journal_id,
                      'narration': narration,
                      #'date': voucher.date,
                      'ref': reference,
                      #'period_id': voucher.period_id.id,
                      'period_id': periods and periods[0] or False,
                      'line_id': group_move_lines['grouped'] #move_line_ids,
                  }, context=context)

              return_id =  move_id

        else:

          if line_ids:
              journal = journal_id or (ttype=='purchase' and user.company_id.hr_journal_id and user.company_id.hr_journal_id.id) or (ttype=='sale' and user.company_id.hr_rev_journal_id and user.company_id.hr_rev_journal_id.id) or False
              if not journal:
                  raise osv.except_osv(_('ERROR'), _('Please Enter HR Journal for Your Company'))
              group_lines = self.group_lines(cr, uid, line_ids)
              currency_id = vals.get('currency_id') or (user.company_id.hr_journal_id.currency and user.company_id.hr_journal_id.currency.id) or user.company_id.currency_id.id

              

              rec_id = model_pool.create(cr, uid , {
                  'company_id': user.company_id.id,
                  'journal_id': journal,
                  'account_id': vals.get('account_id',False) and vals.get('account_id') or account_id, #Doesn't exist in payment permanent 
                  'type': ttype, # Doesn't exist in payment permanent
                  'reference': reference,
                  'narration': narration,
                  'line_ids': group_lines['grouped'],
                  'amount': group_lines['total'],
                  'currency_id': currency_id,
                  'partner_id': partner_id
              }, context = context)


              if vals.get('model', 'account.voucher')=='account.voucher':
  				        number=rec_id
          return_id = rec_id
        return return_id


    def _convert_amount(self, cr, uid, amount, company_currency, context=None):
        '''
        This function convert the amount given in company currency. It takes either the rate in the voucher (if the
        payment_rate_currency_id is relevant) either the rate encoded in the system.

        :param amount: float. The amount to convert
        :param voucher: id of the voucher on which we want the conversion
        :param context: to context to use for the conversion. It may contain the key 'date' set to the voucher date
            field in order to select the good rate to use.
        :return: the amount in the currency of the voucher's company
        :rtype: float
        '''
        if context is None:
            context = {}
        currency_obj = self.pool.get('res.currency')
        #voucher = self.browse(cr, uid, voucher_id, context=context)
        return currency_obj.compute(cr, uid, company_currency, company_currency, amount, context=context)

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

    def group_move_lines(self, cr, uid, lines):
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
            key = (line['account_id'], line['analytic_account_id'])
            if not key in line_grouped:
                line_grouped[key] = line
            else:
                line_grouped[key]['credit'] += line['credit']
                line_grouped[key]['debit'] += line['debit']
                line_grouped[key]['name'] = line_grouped[key]['name'] + "/" + line['name']
        grouped = []
        for key, val in line_grouped.items():
            grouped.append((0, 0, val))
            #total += val['amount']
        return {'grouped': grouped}

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
	print "////////////////////////////",total_allow,total_deduct,total_allow - total_deduct
        return  {'total_allow': total_allow, 'total_deduct':total_deduct, 'balance':total_allow - total_deduct,}

#vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
