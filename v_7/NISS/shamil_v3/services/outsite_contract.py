# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################
from openerp.osv import osv, fields
import netsvc
import time
from datetime import datetime,date,timedelta
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp
from admin_affairs.copy_attachments import copy_attachments as copy_attachments
from tools.amount_to_text_en import amount_to_text
from base_custom import amount_to_text_ar

#
# Model definition
#
#----------------------------------------
marital_status = [
           ('1', 'Married'),
           ('2', 'Single'),
       ('3', 'Divorced'),
       ('4', 'Widower'),
        ]
education_level  = [
           ('1', 'Nook'),
           ('2','Secondary' ),
       ('3', 'University'),
       ('4', 'Other'),
        ]
class output_contract(osv.Model):
    _name = "outsite.contract"
    _description = "Outsite Contract"
    _columns = { 
                'name':fields.char("Name contract",size=128),
                'address_home_id':fields.char('Home Address', size=32, readonly=False),
                 'mobile_phone': fields.char('Work Mobile', size=32, readonly=False),
                'phone_relat': fields.char('Phone Relation', size=32, readonly=False),
                 'birthday_date': fields.date("Date of Birth", required=True, readonly=False),# states={'draft':[('readonly', False)]}
                 'department_id':fields.many2one('hr.department', 'Department', required=True, readonly=False, domain="[('company_id','=',company_id)]" ),#states={'draft':[('readonly', False)]}
                
                 'sequence' :fields.char("Sequence",size=100, readonly=True),
                 'contract_date' : fields.date('Employment Date',  readonly=False),#, states={'draft':[('readonly', False)]}
                'company_id' : fields.many2one('res.company', 'Company',required= True),
                 'service_terminated' : fields.boolean('Service Terminated'),
                 'education_level': fields.selection(education_level, 'Education Level'),
                'classfication':fields.char("Classfication",size=128),
                'car_licence_type':fields.char("Car Licence Type",size=128),
                'note':fields.text("Note"),
                'place_work':fields.char("Place Work",size=128),
                'job_id' :fields.many2one('outsite.job.config', "Job" , required=True),
                'car_model' :fields.many2one('fleet.vehicle.model', "Car model" ),
                'marital_status': fields.selection(marital_status, 'Marital Status'),
                'allows_mount':fields.one2many('contract.payroll.amount','employee', "Allows Mount", readonly=True),
                'family_no':fields.char("Relations",size=8),
                'partner_id':fields.many2one('res.partner',"Partner name",required= True),
    }

    #_constraints = [
     #            ('name_unique', 'unique(name)', 'The name of the training should be unique!')
      #           ]

    _defaults = {
    'sequence': lambda obj, cr, uid, context: obj.pool.get('ir.sequence').get(cr, uid,'outsite.contract'),
                 }
    
    _order = "sequence"
    


class allows_detuct_contract(osv.Model):
    _name = "outsite.allow.detuct"
    _description = "Outside Contractor Allowances And Deductions"

    _columns = { 
                'name':fields.char("Name Allows ",size=128),
                'allow_mount' :fields.float("allow mount" ,digits=(18,2),  readonly=False,required= True),
                'overtime_holi' :fields.float("Overtime Holiday " ,digits=(18,2),  readonly=False),
      
               }

    def compute_allowance_deduction_contract(self, cr, uid,emp_obj,allow_deduct): 
       """ 
	Method computes allowances and deductions amount for missions , overtime.
	@param browse record emp_obj: outsite.contract.employee record
	@param allow_deduct: Id of allowance/deduction 
	@return: Dictionary of allowance/deduction values
       """
       return {'amount':self.browse(cr,uid,allow_deduct).allow_mount,'amount_hol':self.browse(cr,uid,allow_deduct).overtime_holi}

class job_contract(osv.Model):
    _name = "outsite.job.config"
    _description = "Outside Contractor Job"
    _columns = { 
                'name':fields.char("Name Job",size=128),
                'code':fields.char('Code', size=32, readonly=False),
                'basic_salary' :fields.float("Basic Salary", digits=(18,2),required= True ,  readonly=False),
                'total_amount' :fields.float("Total amount" ,digits=(18,2),  readonly=False,required= True),
      
    }
    


 
class overtime_contract_archive(osv.Model):

    def _get_months(self, cr, uid, context):
       """
	Method that returns months of year as numbers.
	@return: List Of tuple
       """
       months=[(str(n),str(n)) for n in range(1,13)]
       return months

    _name = "overtime.contract"
    _description = "Outside Contractor Overtime Archive"

    _columns = {  
            'company_id' : fields.many2one('res.company', 'Company' , required= True , readonly=False,),
            'month': fields.selection(_get_months,'Month', select=True),
            'year' :fields.integer("Year", required= True ,  readonly=False),
            'overtime_name' :fields.many2one('outsite.allow.detuct', 'Allow name' , required= True , readonly=False,),
            'employees': fields.many2one('outsite.contract',"Employee"),
            'amount':fields.one2many('contract.payroll.amount','amount',"amount"),

                }
    _defaults = {
        'company_id': lambda s,cr,uid,c: s.pool.get('res.company')._company_default_get(cr, uid, 'account.account', context=c), 
        'year' : int(time.strftime('%Y')),
                 }
    


class overtime_amount(osv.Model):

    _name = "contract.payroll.amount"
    _description = "Outside Contractor overtime "

    _columns = {
          'amount': fields.many2one('overtime.contract',"amount", size=4, required= False),
          'employee' : fields.many2one('outsite.contract',"Employee", required= True,readonly=False,domain="[('service_terminated','=',False)]"),
          'salary_emp': fields.float("Salary", digits=(18,2) , required= False),
          'amounts_hours': fields.float("Amount/Hours", digits=(18,2)  , required= False,readonly=True),
          'no_hours': fields.float("Number of Hours", digits=(18,2) , required= False,),
          'amounts_value': fields.float("hoday_Amount", digits=(18,2)  , required= False,readonly=True),
          'no_hours_holi': fields.float("Number of Hours Holiday", digits=(18,2) , required= False,),
          'gross_amount': fields.float("Gross Amount",digits=(18,2)  , required= False,readonly=True),
         'amounts_holiday': fields.float("Amount/Hours", digits=(18,2)  , required= False,readonly=True),
         'amounts_custom': fields.float("Amount/Hours", digits=(18,2)  , required= False,readonly=True),
         'month':fields.char("Month",size=128),
        'year':fields.char("Year",size=128),
        'overtime_name':fields.many2one('outsite.allow.detuct',"Overtime and Mission name"),
       'no_day':fields.integer('No of Apsent Day',digits_compute= dp.get_precision('Account'),),
       'appsent_amount': fields.float("Apsent_Amount", digits=(18,2)  , required= False,readonly=True),


        }

    _sql_constraints = [

       ('employee_uniqe', 'unique (amount,employee)', 'you can not duplicate employee !')
                      ]
 
    def create(self, cr, uid,vals,context={}):
        """
	Mehtod overwrites creates method to calculate and create overtime amount for contractor .
	@param vals: Dictionary contains the entered data
	@return: Id of the created record
        """
        holiday=0.0
        custom=0.0
        overtime_obj = self.pool.get('overtime.contract')
        employee_obj = self.pool.get('outsite.contract')
        payroll_obj = self.pool.get('outsite.allow.detuct')
        emp_overtime_id=super(osv.Model,self).create(cr, uid, vals)
        for emp_overtime in self.browse(cr,uid,[emp_overtime_id]):
           for overtime in overtime_obj.browse(cr,uid,[emp_overtime.amount.id]):
              for emp in employee_obj.browse(cr,uid,[emp_overtime.employee.id]):
                   allow_dict=payroll_obj.compute_allowance_deduction_contract(cr,uid,emp,overtime.overtime_name.id)
                   holiday=float(allow_dict['amount_hol']*emp_overtime.no_hours_holi)
                   custom=float(allow_dict['amount']*emp_overtime.no_hours)
                   apsent=float(employee_obj.browse(cr,uid,emp.id).job_id.total_amount/30)*emp_overtime.no_day
                   emp_overtime = {           
                                     'amount':overtime.id,
                                     'employee': emp.id,
                                     'amounts_hours':allow_dict['amount'],
                                     'amounts_value':allow_dict['amount_hol'],
                                     'amounts_holiday':holiday,                                 
                                     'amounts_custom':custom,
                                     'gross_amount':float(holiday+custom+apsent),
                                     'month':str(overtime.month),
                                     'year':str(overtime.year),
                                     'overtime_name':overtime.overtime_name.id,
                                     'appsent_amount':apsent,

                       }
                   update = self.write(cr, uid,[emp_overtime_id],emp_overtime)
        emp_record=employee_obj.write(cr, uid,emp_overtime['employee'],emp_overtime)
        return emp_overtime_id

    

#----------------------------------------
#outsite contract payroll main archive
#----------------------------------------
class contract_main_archive(osv.Model):

    def _get_amount(self, cr, uid, context=None):
        """
	Mehtod returns the gross amount of contractor's payroll.
	@param vals: Dictionary contains the entered data
	@return: Id of the created record
        """
        if context is None:
            context= {}
        return context.get('gross', 0.0)

    _name ="outsite.contract.main.archive"
    _description ="Outsite Contract Main Archive"
    _columns ={
         'employee_id' : fields.many2one('outsite.contract',"Employee", readonly=True),
         'month' :fields.integer("Month", size=8 , required= True),
         'year' :fields.integer("Year", size=8 , required= True),
         'company_id' : fields.many2one('res.company', 'Company',readonly=True,required= True),
         'job_id' : fields.many2one('outsite.job.config',"Job",readonly=True),
         'dep_name':fields.many2one('hr.department','Department' , readonly=True),
         'total_allowance' :fields.float("Total Allowances",digits=(18,2) , readonly=True),
        'total_mission' :fields.float("Total mission",digits=(18,2) , readonly=True),
        'appsent_amount' :fields.float("Total Apsent",digits=(18,2) , readonly=True),
         'department_id' : fields.many2one('hr.department','Department' ,readonly=True),
        'net' :fields.float("Net",digits=(18,2) , readonly=True),
        'gross' :fields.float("Gross",digits=(18,2) ,readonly=True),
        'appsent_amount':fields.float("Total Mount for Appsent Day",digits=(18,2) , readonly=True),
        'partner_id':fields.many2one('res.partner',"Partner name",readonly=True),

               }
    _defaults = {
             'gross': _get_amount,
                 }

