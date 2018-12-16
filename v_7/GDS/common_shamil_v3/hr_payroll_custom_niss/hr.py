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
from openerp import netsvc
from openerp.tools.translate import _
import re
import mx


class hr_department(osv.Model):
    _inherit = 'hr.department'
    _columns = {
       'payroll_employee_id':fields.many2one('hr.department.payroll' , string="Group"),
    }

class hr_salary_scale(osv.Model):
    _inherit ='hr.salary.scale'
    _columns = {
        'sequence' : fields.integer('Sequence') , 
    }

#----------------------------------------
#hr_department_payroll(inherit) 
#----------------------------------------
class hr_department_payroll(osv.Model):

    _name = "hr.department.payroll"

    _columns = {
        'name': fields.char('Department Of Payroll',size=256, required=True ),
        'department_payroll_ids':fields.one2many('hr.employee', 'payroll_employee_id', 'Employees', readonly=True, domain=[('state', '=', 'approved')]),
        #'department_payroll_ids':fields.many2many('hr.employee', 'payroll_employee_id_rel' ,'payroll_employee_id' , 'employee' ), 
        'state_id':fields.selection([('khartoum', 'khartoum'), ('states', 'States')], "States or Khartoum"),
        'sector_id' : fields.many2one('hr.department.payroll' , string="Sector"),
        'type' : fields.selection([('sector' , 'Sector') , ('group' , 'Group')] , string="Type") ,
        'department_id' : fields.many2one('hr.department' , string='Department') ,
    }
    
#----------------------------------------
# Employee (Inherit) 
# Adding new fields 
#----------------------------------------
class hr_employee(osv.Model):

    _inherit = "hr.employee"

    _order = "sequence"

    _columns = {
        'sector_id' : fields.many2one('hr.department.payroll', 'Sector',ondelete="restrict"),
        'payroll_employee_id':fields.many2one('hr.department.payroll', 'Group',ondelete="restrict" ,readonly=True, required = True , states={'draft':[('readonly', False)]}),
        'payroll_state':fields.selection([('khartoum', 'khartoum'), ('states', 'States')], "States or Khartoum", required=True),
    }

    _defaults = {
       
    }

   

    _constraints = [
        
    ]
    _sql_constraints = [
       
    ]

    def onchange_department_id(self, cr, uid, ids, department_id, context=None):
        value = {'parent_id': False}
        if department_id:
            department = self.pool.get('hr.department').browse(cr, uid, department_id)
            value['parent_id'] = department.manager_id.id
            value['payroll_employee_id'] = department.payroll_employee_id and department.payroll_employee_id.id or False
        return {'value': value}

class hr_payroll_main_archive(osv.Model):
    _inherit = 'hr.payroll.main.archive'
    _columns = {
        'payroll_employee_id' : fields.many2one('hr.department.payroll', 'Group'),
    }

    def create(self, cr, uid, vals, context=None):
        emp_obj = self.pool.get('hr.employee').browse(cr , uid , [vals['employee_id']] , context)[0]
        if emp_obj.payroll_employee_id :
            group_id = payroll_employee_id.id
            vals['payroll_employee_id'] = group_id
        return super(hr_payroll_main_archive, self).create(cr , uid , vals , context)


class hr_employee_salary_addendum(osv.Model):
    _inherit = 'hr.employee.salary.addendum'
    def compute(self, cr, uid, ids, context = {}):

        """Compute salary/addendum for all employees or specific employees in specific month.
           @return: Dictionary 
        """
        print "**************************************************START>>>>"
	all_num=0
        main_arch_obj = self.pool.get('hr.payroll.main.archive')
        status_obj = self.pool.get('hr.holidays.status')
        delegation_obj = self.pool.get('hr.employee.delegation')
        holidays_obj = self.pool.get('hr.holidays')

        payroll_obj = self.pool.get('payroll')
        employee_obj = self.pool.get('hr.employee')
        archive_obj = self.pool.get('hr.allowance.deduction')
        promotion_obj = self.pool.get('hr.movements.degree')
        emp_process_list=[]

        data= self.get_data(cr, uid, ids, context=context)
        salary_date = mx.DateTime.Parser.DateTimeFromString(data['date'])
        first_date=datetime(salary_date.year, salary_date.month, 1)
        last_date=datetime(salary_date.year, salary_date.month, 30)
        process_ids=promotion_obj.search(cr, uid, [('approve_date', '>', first_date.strftime('%Y-%m-%d')),
                                                      ('approve_date', '<', last_date.strftime('%Y-%m-%d')),
                                                      ('employee_id', 'in', tuple(data['employee_ids']))])
        process_archive_data=promotion_obj.browse(cr, uid, process_ids, context=context)

        for emp in process_archive_data:
            emp_process_list.append(emp.employee_id.id)
        print "************************", emp_process_list
        if data['archive_ids']:
            employee=main_arch_obj.browse(cr,uid,data['archive_ids'])
            emp_list=[]
            for emp in employee:
                emp_list.append(emp.employee_id.emp_code)
            raise osv.except_osv(_('Error'), _('The  %s In The %sth Month Year Of %s It is  Already Computed With Code %s')
                                    % (data['type'], data['month'], data['year'],str(emp_list)))
        if not data['employee_ids']:
            raise osv.except_osv(_('Error'), _('No employee found.'))
        if  context.get('salary_batch_id'):
            self.pool.get('hr.salary.batch').write(cr,uid,[context.get('salary_batch_id')],{'batch_total':len(data['employee_ids']),} )
        main_arch_obj.create_main_archive(cr, uid, \
                        {'employee_ids':data['employee_ids'],'year':data['year'], 'month': data['month']})
        start_salary = time.time()
              
        '''cr.execute("""select a.id as main_id, employee_id, working_days, holiday_days, delegation_days,\
                            emp_code, e.department_id, company_id, e.job_id, e.degree_id, e.bonus_id, e.bank_account_id
                             from hr_payroll_main_archive  a  
                             left join hr_employee e on (a.employee_id=e.id)
                              where a.id=291""") '''    
        cr.execute("""select a.id as main_id, e.payroll_employee_id as pay_emp_id , employee_id, working_days,\
                            emp_code, e.department_id, company_id, e.job_id, e.payroll_id,
                             e.degree_id, e.bonus_id, e.bank_account_id
                             from hr_payroll_main_archive  a  
                             left join hr_employee e on (a.employee_id=e.id)
                              where employee_id in %s and a.year=%s and a.month=%s""",\
                              (tuple(data['employee_ids']),data['year'],data['month'] ))
        #TODO: and type=insalary_sheey
        result_dic = cr.dictfetchall()
        '''cr.execute("""update  hr_payroll_main_archive set arch_id=%s, salary_date=%s where id in %s  """ ,\
                              ( ids[0],data['date'], tuple([r['main_id'] for r in result_dic]) )  )  '''
        #TODO: *** do upper update inside the for loop and use res dictionary in write_allow_deduct
        if data['type'] == 'salary':
            for res in result_dic:
		all_num =all_num+1
                cr.execute("""select * from hr_payroll_holidays
                                      where employee_id = %s """,\
                                      (res['employee_id'],))
                holiday_dic = cr.dictfetchall()
                holidays = []
                startt1 = time.time()
                for r in holiday_dic:
                    key = (r['employee_id'], r['type'], r['status_id'])
                    if not key in holidays:
                        allow_deduct_ids = []
                        holidays[key] = r
                        if r['type'] == 'customized':
                            allow_deduct_ids = [r.id for r in status_obj.browse(cr, uid, r['status_id']).allow_deduct_ids ]
                        holidays[key].update({'allow_deduct_ids':allow_deduct_ids})
                    else:
                        holidays[key]['days'] += r['days']
                holidays.append({'days':res['working_days'] ,'allow_deduct_ids':[]})
                #print "****************************************************************" 
                #print "PYTHON GET Allow Deduct_ids   ..........", time.time()-startt1  

                start2 = time.time()
                
                if res['employee_id'] in emp_process_list:
                    filtered=filter(lambda arch : arch['employee_id'].id == res['employee_id'], process_archive_data)
                    print "************************************>>",filtered
                    allow_deduct_dict,total_basic=self.different_compute(cr, uid, ids,filtered[0],str(last_date),context)
                    cr.execute("""update hr_payroll_main_archive set basic_salary=%s where id=%s  """ ,(total_basic, res['main_id'] ))
                    
                else:
                    allow_deduct_dict = self.write_allow_deduct(cr, uid, res['employee_id'], holidays)
                #print "Function: write Allow Deduct_ids   ..........", time.time()-start2      
                for d in allow_deduct_dict:
                    d['main_arch_id'] = res['main_id']
                    d['active']=True
                    #d['employee_id']=res['employee_id']
                   # print d.values()
                    #TODO: dict order
                    cr.execute("insert into  hr_allowance_deduction_archive (allow_deduct_id,\
                             amount, tax_deducted, main_arch_id,active, remain_amount, type) values %s" , (tuple(d.values()),))
                s_obj = self.browse(cr, uid, ids[0])

                start3 = time.time()
                result = main_arch_obj.total_allow_deduct(cr, uid, [res['main_id']], \
                            data={'salary_date':data['date'], 'type':s_obj.type , 'addendum_ids':s_obj.addendum_ids})
                #print "total_allow_deduct   ..........", time.time()-start3      
                #print result
                #TODO: Company_id should be???
                cr.execute("""update hr_payroll_main_archive set tax=%s,total_allowance=%s, \
                                    allowances_tax=%s,total_deduction=%s,net=%s,total_loans=%s,\
                                    code=%s, department_id=%s, company_id=%s, job_id=%s, \
                                    scale_id=%s, degree_id=%s, bonus_id=%s, bank_account_id=%s,\
                                    arch_id=%s, salary_date=%s  , payroll_employee_id=%s where id=%s  """ ,\
                              (result[res['main_id']]['tax'], result[res['main_id']]['total_allowance'], result[res['main_id']]['allowances_tax'],\
                               result[res['main_id']]['total_deduction'], result[res['main_id']]['net'],result[res['main_id']]['total_loans'], \
                               res['emp_code'],res['department_id'],\
                               1, res['job_id'], res['payroll_id'], res['degree_id'],\
                               res['bonus_id'],res['bank_account_id'],ids[0],data['date'], res['pay_emp_id'], res['main_id'] ))
                
        print "All Employee salary...........( ",all_num," )", time.time()-start_salary


#######################################################################3
        for employee in employee_obj.browse(cr, uid, data['employee_ids'], context = context):
            basic_salary = 0.0
            days = 30
            in_salary_sheet = False
            allow_deduct_dict = []
            if data['type'] == 'addendum':
                for addendum in data['addendum_ids']:

                    check_employment=archive_obj.browse(cr,uid,addendum).based_employment
                    amount_dict = payroll_obj.allowances_deductions_calculation(cr,uid,data['date'],employee,{}, [addendum], False,[])
                    if check_employment == 'based':
                        
                        # Check employment date & end_date during addendum computation
                        emp_date = mx.DateTime.Parser.DateTimeFromString(employee.employment_date)
                        year_emp_date = mx.DateTime.Parser.DateTimeFromString(employee.employment_date).year
                        #days = 0
                        if int(year_emp_date) != int(data['year']):
                            days = int(365)
                        else :
                            if employee.end_date:
                                end = (datetime.date (int(data['year']),  int(12), 31)).strftime('%Y-%m-%d')
                                end = mx.DateTime.Parser.DateTimeFromString(end)
                                end_date = mx.DateTime.Parser.DateTimeFromString(employee.end_date) 
                                emp_end_date_days = (end - end_date).days
                            else :
                                emp_end_date_days=0
                            first_date = (datetime.date (int(data['year']),  int(1), 1)).strftime('%Y-%m-%d')
                            first_date = mx.DateTime.Parser.DateTimeFromString(first_date) 
                            emp_no_days = (emp_date - first_date).days
                            days = int(365) - emp_no_days - emp_end_date_days
                            #print">>>>>>>>>>>>>>>>>>>>>>>>>>>>>" ,emp_end_date_days ,end_date ,days
                            #print">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>days" ,first_date ,emp_no_days ,days ,year_emp_date
                            #print "**************************************************" ,amount_dict['amount']/365 ,(amount_dict['amount']/365) * days
                            if days <= 0:
                                continue
                    else: days = int(365)
                    if amount_dict['result']:
                       addendum_dict = {
                        'allow_deduct_id': addendum,
                        'amount':amount_dict['result'][0]['holiday_amount'] and amount_dict['result'][0]['holiday_amount'] or (amount_dict['result'][0]['amount']/365* days) ,
                        'tax_deducted':amount_dict['result'][0]['tax'],
                        'imprint':amount_dict['result'][0]['imprint'],
                        'remain_amount':amount_dict['result'][0]['remain_amount'],
                    }
                       allow_deduct_dict.append(addendum_dict)
                       #print">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>allow_deduct_dict" ,allow_deduct_dict

        if not context.get('salary_batch_id'):
            self.write(cr, uid, ids, { 'state': 'compute'}, context=context)
        else :
            state = len([btch.id for btch in self.browse(cr,uid,ids)[0].batch_ids if btch.state!='compute'])-1 > 0 and 'draft' or 'compute'
            self.write(cr, uid, ids, { 'state': state}, context=context)
	#print "All Employee salary2...........( ",all_num," )", time.time()-start_salary
        return {}

    def different_compute(self, cr, uid, ids,prom_obj,date,context={}):
        """Method that changes the state to 'approve' and reflects the substitution to hr_employee object
        @return: Boolean True
        """
        salary_day = mx.DateTime.Parser.DateTimeFromString(prom_obj.approve_date)
        print "prom in diff>>>>>>>>>>>>>>>>>>",salary_day.day
        pref_factor=salary_day.day
        new_factor=30-salary_day.day
        current_basic=0
        pref_basic=0
        emp_curr_dict = {}
        emp_pref_dict = {}
        salary_dict={}
        salary_list=[]
        allow_deduct_obj = self.pool.get('hr.allowance.deduction')
        salary_allow_deduct_obj = self.pool.get('hr.salary.allowance.deduction')
        allow_deduct_ids=allow_deduct_obj.search(cr , uid , [], context = {'rules':True})
        # print "Allowance1>>>>>",len(diff_allow_deduct_ids)
        emp_curr_dict.update({
            'emp_id': prom_obj.employee_id.id,
            'company': prom_obj.employee_id.company_id.id,
            'department': prom_obj.employee_id.department_id.id,
            'job_id': prom_obj.employee_id.job_id.id,
            'group':prom_obj.employee_id.payroll_employee_id.id,
            'gender': prom_obj.employee_id.gender,
            'category': prom_obj.employee_id.category_ids,
            'payroll': prom_obj.employee_id.payroll_id.id,
            'degree': prom_obj.employee_id.degree_id.id,
            'taxable': prom_obj.employee_id.degree_id.taxable,
            'bonus': prom_obj.employee_id.bonus_id.id,
            'basic_salary': prom_obj.employee_id.bonus_id.basic_salary,
            'old_basic_salary': prom_obj.employee_id.bonus_id.old_basic_salary,
            'started_section': prom_obj.employee_id.degree_id.basis,
            'marital_status': prom_obj.employee_id.marital,
            'exemp_tax': prom_obj.employee_id.tax_exempted,
            'date': date,
            'substitution':prom_obj.employee_id.substitution,
            'special': False,
            'no_sp_rec': False, })
        emp_pref_dict.update({
            'emp_id': prom_obj.employee_id.id,
            'company': prom_obj.employee_id.company_id.id,
            'department': prom_obj.employee_id.department_id.id,
            'group':prom_obj.employee_id.payroll_employee_id.id,
            'job_id': prom_obj.employee_id.job_id.id,
            'gender': prom_obj.employee_id.gender,
            'category': prom_obj.employee_id.category_ids,
            'payroll': prom_obj.employee_salary_scale.id,
            'degree': prom_obj.last_degree_id.id,
            'taxable': prom_obj.last_degree_id.taxable,
            'bonus': prom_obj.last_bonus_id.id,
            'basic_salary': prom_obj.last_bonus_id.basic_salary,
            'old_basic_salary': prom_obj.last_bonus_id.old_basic_salary,
            'started_section': prom_obj.last_degree_id.basis,
            'marital_status': prom_obj.employee_id.marital,
            'exemp_tax': prom_obj.employee_id.tax_exempted,
            'date': date,
            'substitution': 1,
            'special': False,
            'no_sp_rec': False, })
        total_allow = 0
        total_deduct = 0

        for row in allow_deduct_obj.browse(cr, uid, allow_deduct_ids):
            
            emp_curr_dict.update({'allow_deduct': False, })
            emp_pref_dict.update({'allow_deduct': False, })

            curr_amount = 0
            curr_tax=0
            curr_imprint=0
            curr_remain_amount=0
            curr_holiday_amount=0

            diff_amount = 0
            diff_tax=0
            diff_imprint=0
            diff_remain_amount=0
            diff_holiday_amount=0

            gross_amount = 0
            curr_allow_dict = {}
            diff_allow_dict = {}
            # print "###",row
            domain = [('payroll_id', '=', emp_curr_dict['payroll']), ('degree_id', '=', emp_curr_dict['degree']),
                      ('allow_deduct_id', '=', row.id)]
            allow_deduct_ids = salary_allow_deduct_obj.search(cr, uid, domain, context={'rules': True})
            for rec in salary_allow_deduct_obj.browse(cr, uid, allow_deduct_ids):
                emp_curr_dict.update({'allow_deduct': rec, })

            domain = [('payroll_id', '=', emp_pref_dict['payroll']), ('degree_id', '=', emp_pref_dict['degree']),
                      ('allow_deduct_id', '=', row.id)]
            allow_deduct_ids = salary_allow_deduct_obj.search(cr, uid, domain, context={'rules': True})
            for rec in salary_allow_deduct_obj.browse(cr, uid, allow_deduct_ids):
                emp_pref_dict.update({'allow_deduct': rec, })

            if emp_curr_dict['allow_deduct']:
                curr_allow_dict = self.pool.get('payroll').allowances_deductions_amount(cr, uid, emp_curr_dict, row)

                curr_amount = round(curr_allow_dict['amount'] / 30 * new_factor, 2)
                curr_tax=round(curr_allow_dict['tax'] / 30 * new_factor, 2)
                curr_imprint=round(curr_allow_dict['imprint'] / 30 * new_factor, 2)
                curr_remain_amount=round(curr_allow_dict['remain_amount'] / 30 * new_factor, 2)
                #curr_holiday_amount=round(curr_allow_dict['amount'] / 30 * new_factor, 2)


            if emp_pref_dict['allow_deduct']:
                diff_allow_dict = self.pool.get('payroll').allowances_deductions_amount(cr, uid, emp_pref_dict, row)

                diff_amount = round(diff_allow_dict['amount'] / 30 * pref_factor, 2)
                diff_tax=round(diff_allow_dict['tax'] / 30 * pref_factor, 2)
                diff_imprint=round(diff_allow_dict['imprint'] / 30 * pref_factor, 2)
                diff_remain_amount=round(diff_allow_dict['remain_amount'] / 30 * pref_factor, 2)
                #diff_holiday_amount=round(diff_allow_dict['amount'] / 30 * pref_factor, 2)


            #if not curr_allow_dict['tax'] or not diff_allow_dict['tax']:
            #       raise osv.except_osv(_('Error'), _('%s The %s before if emp dict %s')
            #		                            % (prom_obj.employee_id.id,curr_allow_dict,diff_allow_dict))
            gross_amount = curr_amount + diff_amount
            if gross_amount != 0:
                salary_dict[row.id]= {
                              'allow_deduct_id': row.id,
                              'amount': gross_amount,
                              'tax_deducted':curr_tax+diff_tax,
                              'remain_amount':curr_remain_amount+diff_remain_amount,
                              'type': row.name_type,
                              }


            #if row.name_type == 'allow':
            #    total_allow += gross_amount
            #else:
                #total_deduct += gross_amount
                # print "id>>",row
                # print "curr>>",curr_allow_dict
                # print "diff>>",diff_allow_dict
        current_basic=(emp_curr_dict['basic_salary']/30)*new_factor
        pref_basic=(emp_pref_dict['basic_salary']/30)*pref_factor
        total_basic = current_basic+pref_basic
        return salary_dict.values(),total_basic

#----------------------------------------
#----------------------------------------
#salary suspend archive
#----------------------------------------

suspend_type = [
           ('suspend', 'Suspend'),
           ('resume', 'Resume'),
	    ]
class salary_suspend_archive(osv.osv):
    _name = "hr2.basic.salary.suspend.archive"
    _columns = {
		 'employee_id':fields.many2one('hr.employee', "Employee", required=True),
		 'suspend_date' :fields.date("Suspend/Resume Date", size=8 , required=True),
		 'comments': fields.text("Comments"),
		 'suspend_type':fields.selection(suspend_type, "Suspend Type" , readonly=True),
		}
    
salary_suspend_archive()

# Employee (Inherit) 
# Adding new fields 
#----------------------------------------
class hr_allowance_deduction_report(osv.osv_memory):
    _name ='hr.allowance.deduction.report'
    _inherit = 'hr.allowance.deduction.report'


    _columns = {
        'department_ids' : fields.many2many('hr.department.payroll' , 'hr_report_custom_deps_pay2_rel', 'report_id','dep_id', string="groups") ,
    }

   
class hr_allowance_deduction(osv.osv):
    _inherit = "hr.allowance.deduction"
    _description = "Allowance and Deduction"
    _columns = { 
                'payroll_department_ids' : fields.many2many('hr.department.payroll' , 'hr_payroll_dept_allowance_deduction', 'allow_deduct_id','dept_id', string="groups") ,
                }


class payroll(osv.osv):

    _inherit = "payroll"
    _description = "Payroll"


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
       substitution_setting = ''
       allow_amount = 0.0
       deduct_amount = 0.0
       result = []
       if not substitution:
          # if substitution False the emp_dict is empty and will be updated with employee's info , if its True it  contains employee's substitution info 
          if (not emp_dict) or (emp_dict and 'no_sp_rec' not in emp_dict.keys()) :
             emp_dict.update({'no_sp_rec': False})
          emp_dict.update({
                    'emp_id':employee_obj.id,
                    'company':employee_obj.company_id.id,
                    'department':employee_obj.department_id.id,
                    'job_id':employee_obj.job_id.id,
                    'category':employee_obj.category_ids,
                    'group':employee_obj.payroll_employee_id.id,
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
                    'date':date,
                    'substitution':substitution,
                    'special': False ,
                    })
          # check if employee has sustitution
          domain = []
          domain += ['|', ('end_date', '>=', date), ('end_date', '=', False), ('employee_id', '=', emp_dict['emp_id']), ('start_date', '<=', date)]
          substitue_ids = employee_substitution_obj.search(cr, uid, domain)
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
       allow_deduct_ids = salary_allow_deduct_obj.search(cr, uid, domain)
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
       check_group=False
       # check if allowance or deduction is special and special flag is false then call special function
       if emp_dict['allow_deduct'].allow_deduct_id.special and not emp_dict['special']:
          #if emp_dict['allow_deduct'].allow_deduct_id.id==13:
	  #		raise osv.except_osv(_('Error'), _('The before %s ')% (emp_dict['allow_deduct'].allow_deduct_id.special))
          sp_dict = self.allowances_deductions_sp_calculation(cr, uid, emp_dict, allow_list)

          amount += sp_dict['amount']
          tax_amount += sp_dict['tax']
       else:
          #if emp_dict['allow_deduct'].allow_deduct_id.id==13:
	  #	    raise osv.except_osv(_('Error'), _('The after %s')
          # 		                            % (emp_dict['allow_deduct'].allow_deduct_id.special))
          # check employee allowance/deduction exclusion
          check = allow_deduct_exception_obj.search(cr, uid, ['|', ('end_date', '>', emp_dict['date']), ('end_date', '=', False), ('employee_id', '=', emp_dict['emp_id']), ('start_date', '<', emp_dict['date']), ('allow_deduct_id', '=', emp_dict['allow_deduct'].allow_deduct_id.id), ('action', '=', 'exclusion')])
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

                      emp_group_id = emp_dict['group']
                      group_list = [group.id for group in emp_dict['allow_deduct'].allow_deduct_id.payroll_department_ids ]
                      if not group_list or emp_group_id in group_list:
                          check_group = True

                      allow_categs = emp_dict['allow_deduct'].allow_deduct_id.category_ids
                      if not allow_categs:
                         check_categ = True
                      else:
                         if emp_dict['category'] and [emp_categ.id for emp_categ in emp_dict['category'] if emp_categ in allow_categs]:
                            check_categ = True
                      if check_job and check_categ and check_group:
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
                            amount += emp_dict['family_relation']['child_amount'] + emp_dict['family_relation']['wife_amount']
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
                            other_allow_ids = salary_allow_deduct_obj.search(cr, uid, domain)
                            if other_allow_ids:
                               emp_com_dict = emp_dict.copy()
                               for o in salary_allow_deduct_obj.browse(cr, uid, other_allow_ids):
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
                               emp_holidays_ids= emp_holiday_obj.search(cr,uid,domain)
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
                         if emp_dict['allow_deduct'].allow_deduct_id.related_marital_status == 'yes':
                            # compute allowance/deduction amount based on marital status and number of children if alternative_cash is True
                            status_ids = marital_status_obj.search(cr, uid, [('allow_deduct_id', '=', emp_dict['allow_deduct'].allow_deduct_id.id)])
                            if status_ids:
			       #print "insidddddddddddddddddddddddddd" ,status_ids
                               family_relation=emp_dict['family_relation']
                               for record in marital_status_obj.browse(cr, uid, status_ids):
                                  if (emp_dict['marital_status'] != 'married' and record.married and ((family_relation['child_amount'] == 0 and record.children_no == 0) or (family_relation['child_amount'] > 0 and record.children_no) and  (family_relation['child_no'] == record.children_no) or (family_relation['child_amount'] > 0 and record.children_no and family_relation['child_no'] > record.children_no and record.children_no != 1))) or (emp_dict['marital_status'] == 'single' and not record.married  and  family_relation['child_amount'] == 0 and record.children_no == 0) :
                                     if emp_dict['allow_deduct'].allow_deduct_id.distributed:
                                        alter_amount = alter_amount / emp_dict['allow_deduct'].allow_deduct_id.distributed
                                        amount = alter_amount
                                     if emp_dict['allow_deduct'].allow_deduct_id.name_type == 'allow' and emp_dict['allow_deduct'].allow_deduct_id.bonus_percent:
                                        if not emp_dict['exemp_tax']:
                                           taxable = ((amount-exempted) / perc) * tax_factor
                                           tax_amount = (taxable * emp_dict['allow_deduct'].allow_deduct_id.bonus_percent) / 100
                                     break
 				  if (emp_dict['marital_status'] == 'single' and not record.married  and  family_relation['child_amount'] == 0 and record.children_no == 0) :
                                     alter_amount = (amount * record.percentage) / 100
				     #print "SSSSSSSSSSSSSSSSSSSSSSSS" ,alter_amount
                                     tax_factor = record.taxable
                                     perc = record.percentage / 100
				     #print "percpercpercpercperc" ,perc
				     amount = alter_amount

				  if (emp_dict['marital_status'] == 'married' and record.married  and  family_relation['child_amount'] == 0 and record.children_no == 0) :
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

   


