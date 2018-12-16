# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2016-2017 NCTR (<http://www.nctr.sd>).
#
##############################################################################

from __future__ import division
import datetime
from dateutil.relativedelta import relativedelta
import mx
import time
from openerp import netsvc
from openerp.osv import fields, osv, orm
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp
import math
from admin_affairs.model.email_serivce import send_mail

class hr_salary_addendum_percentage(osv.Model):

    _name = 'hr.salary.addendum.percentage'
    _rec_name = 'emp_code'

    _columns = {
                'percentage' :fields.integer("Percentage"),
                'employee_id': fields.many2one('hr.employee', "Employee"),
                'adden_id': fields.many2one('hr.employee.salary.addendum', "addendum"),
                'emp_code' :fields.related('employee_id', 'emp_code', type='char', 
                    string="Employee Code"),        
                }

    def onchange_employee(self, cr, uid, ids, percentage, employee_id, context={}):
        """
        Method returns the default percentage from hr.employee.salary.addendum
        @param emp_id: ID of the employee
        @return: Dictionary contains the value of employee percentage
        """
        emp_obj = self.pool.get('hr.employee')
        emps_code = employee_id and emp_obj.browse(cr,uid,employee_id).emp_code
        result = {}
        result['percentage'] = percentage
        if emps_code:
            result['emp_code'] = emps_code
        return {'value': result}
        

    def onchange_code(self, cr, uid, ids, code, payroll_ids,employee_ids,payroll_ids_me, context={}):
        """
        Method returns the default percentage from hr.employee.salary.addendum
        @param emp_id: ID of the employee
        @return: Dictionary contains the value of employee percentage
        """
        emp_obj = self.pool.get('hr.employee')
        emp_per_obj = self.pool.get('hr.salary.addendum.percentage')
        emp_ids = []
        emp_list = []

        for emps in employee_ids:
            if emps[0] == 0:
                emp_list.append(emps[2]['employee_id'])
            if emps[0] == 4:
                emp_list.append(emp_per_obj.browse(cr,uid,emps[1]).employee_id.id) 
        if payroll_ids_me[0][2]:
            emp_ids = emp_obj.search(cr,uid,[('emp_code','=',code),('id','not in',emp_list), 
                ('id','in',payroll_ids_me[0][2])])
        if emp_ids:
            return {'value': {'employee_id':emp_obj.browse(cr,uid,emp_ids[0]).id} }
        else :
            return {'value': {'employee_id':False} }


class hr_employee_salary_addendum(osv.Model):

    _inherit  = 'hr.employee.salary.addendum'
    _track = {
        'state': {
            'hr_ntc_custom.mt_payroll_draft': lambda self, cr, uid, obj, ctx=None: obj['state'] == 'draft',
            'hr_ntc_custom.mt_payroll_compute': lambda self, cr, uid, obj, ctx=None: obj['state'] == 'compute',
            'hr_ntc_custom.mt_payroll_confirm': lambda self, cr, uid, obj, ctx=None: obj['state'] == 'confirm',
            'hr_ntc_custom.mt_payroll_approve': lambda self, cr, uid, obj, ctx=None: obj['state'] == 'approve',
            'hr_ntc_custom.mt_payroll_validate': lambda self, cr, uid, obj, ctx=None: obj['state'] == 'validate',
            'hr_ntc_custom.mt_payroll_transferred': lambda self, cr, uid, obj, ctx=None: obj['state'] == 'transferred',
            'hr_ntc_custom.mt_payroll_cancel': lambda self, cr, uid, obj, ctx=None: obj['state'] == 'cancel',
        },
    }

    _columns = {
        'employee_ids': fields.one2many('hr.salary.addendum.percentage', 'adden_id', "Employees"),
        'percentage' :fields.integer("Percentage"),
        'compute_date' :fields.date("Computation Date"),
        'payroll_ids_me': fields.many2many('hr.employee', 'hr_employee_rel', 'pay_bonus', 'pay_id', 'temp'),
        'deduction_ids': fields.many2many('hr.allowance.deduction', 'deduction_payroll_rel3', 'payroll_addendum', 'addendum_id', 'Deduction'),
        #'state': fields.selection([('draft', 'Draft'), ('compute', 'compute'),('confirm', 'Confirm'),
        # ('approve', 'Approved'), ('validate', 'Validated'),('transferred', 'Transferred'), ('cancel', 'Rejected'),
        #], 'Status', select=True, readonly=True),
        'state': fields.selection([('draft', 'Draft'), ('compute', 'Computed'),('confirm', 'Waiting HR Manager Approval'),
         ('approve', 'Waiting Reviewer Approval'), ('validate', 'Waiting Transferring'),('transferred', 'Transferred'), ('cancel', 'Rejected'),
         ], 'Status', select=True, readonly=True),
        
    }

    def rollback(self, cr, uid, ids, context=None):
        """
        delete records from main archive when rolback a calculated salary or addendum.
        @return: boolean  
        """
        main_arch_obj = self.pool.get('hr.payroll.main.archive')
        for rec in self.browse(cr, uid, ids, context=context):
            if rec.arch_ids:
                archive_ids = [x.id for x in rec.arch_ids]
                main_arch_obj.unlink(cr, uid, archive_ids)
            
            if rec.addendum_ids:
                if len(rec.addendum_ids) == 1:
                    if rec.addendum_ids[0].related_attendance:
                        addendum_perc_obj = self.pool.get('hr.salary.addendum.percentage')
                        arch_ids=addendum_perc_obj.search(cr, uid, [('adden_id','in',ids )] , context=context)

                        addendum_perc_obj.write(cr, uid, arch_ids,{'percentage':100.0})

            
        return self.write(cr, uid, ids, { 'state': 'draft'}, context=context)
    def default_payroll(self, cr, uid, ids, context={}):
        """Method that checks if the enterd persentage is less than zero it raise .
           @return: Boolean True or False
        """
        payroll_ids = self.pool.get('hr.salary.scale').search(cr,uid,[])
        payroll_list = []
        if payroll_ids:
            payroll_list += [[6, False, [5]]]

        return payroll_list


    _defaults = {
        'percentage': 100,
        'payroll_ids': default_payroll
    }

    def check_percentagee(self, cr, uid, ids, context={}):
        """Method that checks if the enterd persentage is less than zero it raise .
           @return: Boolean True or False
        """

        for rec in self.browse(cr, uid, ids):
            for rec1 in rec.employee_ids:
                if rec.percentage < 0 or rec1.percentage < 0:
                    raise osv.except_osv(_('Error'), _('Percentage Should Be More Than OR Equal To 0'))
                if (rec.percentage > 100 or rec1.percentage > 100) and rec.type == 'salary':
                    raise osv.except_osv(_('Error'), _('Percentage Should Be Less Than OR Equal To 100'))
                if not rec1.emp_code or not rec1.employee_id:
                    raise osv.except_osv(_('Error'), _('Please Look At Employees: Missing Employee Code OR Employee Name As a Result To Insert Unexisted Employee Code OR Has Been Already Selected'))
        return True

    _constraints = [
       (check_percentagee, '', []),       
    ]

    def get_months(self, cr, uid, ids, month, context=None):
        month_list = {1:'يناير', 2:'فبراير', 3:'مارس', 4:'أبريل', 5:'مايو', 6:'يونيو', 7:'يوليو', 8:'أغسطس',
                        9:'سبتمبر', 10:'أكتوبر', 11:'نوفمبر', 12:'ديسمبر'}
        return month_list[month]

    def name_change(self, cr, uid, ids, name,month,year,compute_per,type1,addendum_ids,payroll_ids, context=None):

        return self.name_changeeeee(cr,uid,ids,name,month,year,compute_per,type1,addendum_ids,payroll_ids)

    def type_change(self, cr, uid, ids, name,month,year,compute_per,type1,addendum_ids,payroll_ids, context=None):
        emp_obj = self.pool.get('hr.employee')
        salary_scale_obj = self.pool.get('hr.salary.scale')
        termination_obj = self.pool.get('hr.employment.termination')
        salary_per_obj = self.pool.get('hr.salary.addendum.percentage')

        dict_list = self.name_changeeeee(cr,uid,ids,name,month,year,compute_per,type1,addendum_ids,payroll_ids)
        emp_list = []
        domain1 = ['|',('state', 'not in', ('draft','refuse')),('delegation', '=', True),('payroll_id','in',payroll_ids[0][2]),('salary_suspend','!=',True)]
        emp_ids = emp_obj.search(cr,uid,domain1)
        payroll_ids_temp = payroll_ids[0][2]
        if not payroll_ids_temp:
            payroll_ids_temp = salary_scale_obj.search(cr, uid, [])
        if type1 == 'addendum':
            dict_list['value']['addendum_ids'] = False
        

        if ids:
            addendum=self.browse(cr,uid,ids[0])
            if addendum.employee_ids:
                for emp in addendum.employee_ids:
                    salary_per_obj.unlink(cr,uid,emp.id)
        job_obj = self.pool.get('hr.job')
        job_ids = job_obj.search(cr,uid,[])
        for x in job_obj.browse(cr,uid,job_ids):
            job_obj.write(cr,uid,x.id,{'no_of_recruitment':x.no_of_recruitment+1})

        dict_list['value']['employee_ids'] = False
        dict_list['value']['payroll_ids_me'] = [[6, False, emp_ids]]
        return dict_list

    def addendum_change(self, cr, uid, ids, name,month,year,compute_per,type1,addendum_ids,payroll_ids, context=None):
        emp_obj = self.pool.get('hr.employee')
        salary_scale_obj = self.pool.get('hr.salary.scale')
        allowance_obj = self.pool.get('hr.allowance.deduction')
        termination_obj = self.pool.get('hr.employment.termination')
        salary_per_obj = self.pool.get('hr.salary.addendum.percentage')

        dict_list = self.name_changeeeee(cr,uid,ids,name,month,year,compute_per,type1,addendum_ids,payroll_ids)
        emp_list = []
        domain1 = ['|',('state', 'not in', ('draft','refuse')),('delegation', '=', True),('payroll_id','in',payroll_ids[0][2]),('salary_suspend','!=',True)]
        domain2 = ['|',('state', '=', 'refuse'),('delegation', '=', True),('payroll_id','in',payroll_ids[0][2]),('salary_suspend','!=',True)]
        emp_ids = emp_obj.search(cr,uid,domain1)
        payroll_ids_temp = payroll_ids[0][2]
        if not payroll_ids_temp:
            payroll_ids_temp = salary_scale_obj.search(cr, uid, [])
        if type1 == 'addendum' and addendum_ids[0][2]:
            for rec in allowance_obj.browse(cr,uid,addendum_ids[0][2]):
                if rec.allow_out_employee:
                    emp_termi_id=termination_obj.search(cr, uid,[], context=context) 
                    if emp_termi_id:
                        for line in termination_obj.browse(cr, uid, emp_termi_id , context=context) :
                            date = mx.DateTime.Parser.DateTimeFromString(line.dismissal_date)
                            if (year == date.year or year == date.year+1) and line.employee_id.payroll_id.id in payroll_ids[0][2]:     
                                if line.employee_id.id not in emp_list:
                                    emp_list.append(line.employee_id.id)
                    emp_list_id = emp_obj.search(cr,uid,domain2)
                    if emp_list_id: 
                        for emp in emp_obj.browse(cr, uid, emp_list_id , context=context) :
                            date = mx.DateTime.Parser.DateTimeFromString(emp.end_date)
                            if (year == date.year or year == date.year+1) and emp.payroll_id.id in payroll_ids[0][2]:     
                                if emp.id not in emp_list:
                                    emp_list.append(emp.id)
                    emp_ids += emp_list
                    break
        if ids:
            addendum=self.browse(cr,uid,ids[0])
            if addendum.employee_ids:
                for emp in addendum.employee_ids:
                    salary_per_obj.unlink(cr,uid,emp.id)

        dict_list['value']['employee_ids'] = False
        dict_list['value']['payroll_ids_me'] = [[6, False, emp_ids]]
            
        
        
        
        return dict_list


    def scale_change(self, cr, uid, ids, name,month,year,compute_per,type1,addendum_ids,payroll_ids, context=None):
        dict_list = self.name_changeeeee(cr,uid,ids,name,month,year,compute_per,type1,addendum_ids,payroll_ids)
        dict_list['value']['type'] = False
        
        return dict_list

    def name_changeeeee(self, cr, uid, ids, name,month,year,compute_per,type1,addendum_ids,payroll_ids, context=None):
        """
        create the full name from it's components'

        @param the name components
        @return: Dictionary of name value
        """
        scale_object_record = payroll_ids[0][2] and self.pool.get('hr.salary.scale').browse(cr,uid,payroll_ids[0][2][0]) or False
        allowance_obj = self.pool.get('hr.allowance.deduction')
        month = month and self.get_months(cr,uid,ids,month) or ""
        year = year and str(year).lstrip().rstrip() or ""
        type_t = ""
        if type1:
            type_t = type1 == 'salary' and 'المرتبات' or 'الحوافز و البدلات'
        compute_per_t = ""
        if compute_per:
            compute_per_t = compute_per == 'batch' and 'للدفعات' or 'للموظفين'
            if compute_per == 'employee' and payroll_ids[0][2] and scale_object_record.employee_type=='trainee':
                compute_per_t = 'للمتدريبين'
            if compute_per == 'employee' and payroll_ids[0][2] and scale_object_record.employee_type=='contractor':
                compute_per_t = 'للمتعاقيدين'
            if compute_per == 'employee' and payroll_ids[0][2] and scale_object_record.employee_type=='recruit':
                compute_per_t = 'للمجندين'
        addendum_ids_t = ""
        addendum_list = ""
        if addendum_ids:
            for x in addendum_ids:
                if x[2]:
                    for n in allowance_obj.browse(cr,uid,x[2]):
                        addendum_ids_t += n.name + ","

        new_name = ""
        text_t = type1 == 'salary' and "" or 'حساب'
        if addendum_ids_t:
            addendum_ids_t = addendum_ids_t[:len(addendum_ids_t)-1]

        new_name += text_t and text_t + " " or "" 
        new_name += type_t and type_t + " " or ""
        new_name += type_t == 'الحوافز و البدلات' and addendum_ids_t and "(" + str(addendum_ids_t.encode('utf8')) + ")" + " " or ""
        new_name += compute_per_t and compute_per_t + " " or ""
        if len(month) > 0:
            new_name += "لشهر" + " " + month + " "
        if len(year) > 0:
            new_name += "لسنة" + " " + year
        new_name = new_name.lstrip().rstrip()
        new_name = len(new_name) > 0 and new_name or name
        return {
            'value': {
                'name':new_name,
                }
            }

    def onchange_compute_perrr(self, cr, uid, ids, name,month,year,compute_per,type1,addendum_ids,payroll_ids, context=None):

        self.onchange_compute_per(cr,uid,ids,compute_per)
        return self.name_changeeeee(cr,uid,ids,name,month,year,compute_per,type1,addendum_ids,payroll_ids)

    def create(self, cr, uid,vals, context=None):
        salary_scale_obj = self.pool.get('hr.salary.scale')
        employee_obj = self.pool.get('hr.employee')
        salary_adden_obj = self.pool.get('hr.salary.addendum.percentage')
        sub_lines=[]
        scale_id = []
        if not vals['employee_ids'] :
            for scale in vals['payroll_ids'][0][2]:
                scale_id.append(scale)
            if vals['payroll_ids_me'][0][2]:
                for emp in vals['payroll_ids_me'][0][2]:
                    ###############attendance##################
                    '''if 'addendum_ids' in vals:
                        addendum_ids = vals['addendum_ids'][0][2]

                        hr_allowance_deduction_obj = self.pool.get('hr.allowance.deduction')

                        attendance_line_obj = self.pool.get('suggested.attendance.line')

                        related_attendance = hr_allowance_deduction_obj.read(cr, uid,addendum_ids,['related_attendance'],context={} )

                        related_attendance = related_attendance[0]['related_attendance']

                        if related_attendance:
                            attendance_ids = attendance_line_obj.search(cr, uid, [('state', '=', 'done'), ('flage', '=', False),('emp_id','=', emp)],context={})
                            
                            att_percent = attendance_line_obj.read(cr, uid, attendance_ids,['added_percent'], context={})

                            num_attend = 0.0
                            if att_percent:
                                num_attend = att_percent[0]['added_percent']
                            
                            #print ".........................preamount",amount
                            #amount = (amount*num_attend)/100.0
                            #print ".........................posramount",amount
                            vals['percentage'] = num_attend'''
                            ###########################################
                    datal={
                            'employee_id': emp,
                            'percentage':vals['percentage']
                            }
                    sub_lines.append([0,False,datal])
               
                vals['employee_ids'] = sub_lines
        new_id = super(hr_employee_salary_addendum, self).create(cr, uid, vals, context=context)
        for rec in self.browse(cr,uid,[new_id]):
            if rec.compute_per == 'batch' :
                self.onchange_compute_per(cr, uid, [new_id], rec.compute_per)
             
        return new_id

    def write(self, cr, uid, ids, vals, context=None):
        """Method that overwrites write method and detects changes in the configuration of salary scale
          and calls  change_allow_deduct function to recalculate allowances and deductions amount if change in substitution congfiguration.
          @param vals: Dictionary contains the entered values
          @return: Boolean True
        """
        salary_scale_obj = self.pool.get('hr.salary.scale')
        employee_obj = self.pool.get('hr.employee')
        salary_adden_obj = self.pool.get('hr.salary.addendum.percentage')
        sub_lines=[]
        scale_id = []
        write_allow_deduct = super(hr_employee_salary_addendum, self).write(cr, uid, ids, vals, context)
        record = self.browse(cr,uid,ids[0])
        employee_ids = vals.has_key('employee_ids') and True or False
        if (not record.employee_ids) and (not employee_ids) :
            for emp in record.payroll_ids_me:
                datal={
                        'employee_id': emp.id,
                        'emp_code': emp.emp_code,
                        'percentage':record.percentage,
                        'adden_id': record.id,
                        }
                x = salary_adden_obj.create(cr,uid,datal,context)

        if vals.has_key('state'):
            result = self.check_manager_email(cr,uid,ids,context)

        return write_allow_deduct


    def check_manager_email(self, cr, uid, ids, context=None):
        """
        Send Emails
        """
        for h in self.browse(cr, uid, ids, context=context):
            if h.state == 'approve' :
                send_mail(self, cr, uid, ids[0], 'purchase_ntc.group_internal_auditor',u'تصديق المرتبات/حوافز'.encode('utf-8'), u'هناك سجل مرتبات/حوافز في انتظار تصديق المراجع'.encode('utf-8'), context=context)
            if h.state == 'confirm' :
                send_mail(self, cr, uid, ids[0], 'base.group_hr_manager',u'تصديق المرتبات/حوافز'.encode('utf-8'), u'هناك سجل مرتبات/حوافز في انتظار تصديق مدير الموارد البشرية'.encode('utf-8'), context=context) 
            if h.state == 'validate' :
                send_mail(self, cr, uid, ids[0], 'base.group_hr_user',u'ترحيل المرتبات/الحوافز'.encode('utf-8'), u'هناك سجل مرتبات/حوافز في انتظار الترحيل'.encode('utf-8'), context=context) 

    
    def get_data(self, cr, uid, ids, context={}):
        salary_scale_obj = self.pool.get('hr.salary.scale')
        main_archive_obj = self.pool.get('hr.payroll.main.archive')
        archive_obj = self.pool.get('hr.allowance.deduction.archive')
        employee_obj = self.pool.get('hr.employee')
        res_company_obj = self.pool.get('res.company')
        termination_obj = self.pool.get('hr.employment.termination')
        
        employee_ids = []
        emp_list = []
        res = {}
        for record in self.browse(cr, uid, ids, context=context):
            addendum_ids = []
            deduct_ids = []
            if record.company_id:
                company_ids = [company.id for company in record.company_id]
            else:
                company_ids = res_company_obj.search(cr, uid, [ ], context=context)

            if record.payroll_ids:
                payroll_ids = [payroll.id for payroll in record.payroll_ids]
            else:
                payroll_ids = salary_scale_obj.search(cr, uid, [])

            if record.addendum_ids:
                addendum_ids = [x.id for x in record.addendum_ids]
                deduct_ids = [z.id for z in record.deduction_ids]
                for x in record.addendum_ids:
                    if x.allow_out_employee and not record.payroll_ids:
                        employee_ids = employee_obj.search(cr, uid, ['|',('state', 'not in', ('draft','refuse')),('delegation', '=', True),
                                                                 ('salary_suspend', '!=', True),('payroll_id', 'in', payroll_ids), 
                                                                 ('company_id', 'in', company_ids), ])
                        domain2 = ['|',('state', '=', 'refuse'),('delegation', '=', True),
                                                                 ('salary_suspend', '!=', True),('payroll_id', 'in', payroll_ids), 
                                                                 ('company_id', 'in', company_ids), ]
                        emp_termi_id=termination_obj.search(cr, uid,[], context=context) 
                        if emp_termi_id:
                            for line in termination_obj.browse(cr, uid, emp_termi_id , context=context) :
                                date = mx.DateTime.Parser.DateTimeFromString(line.dismissal_date)
                                if (record.year == date.year or record.year == date.year+1) and line.employee_id.payroll_id.id in payroll_ids:     
                                    if line.employee_id.id not in emp_list:
                                        emp_list.append(line.employee_id.id)

                        emp_list_id = emp_obj.search(cr,uid,domain2)
                        if emp_list_id: 
                            for emp in emp_obj.browse(cr, uid, emp_list_id , context=context) :
                                date = mx.DateTime.Parser.DateTimeFromString(emp.end_date)
                                if (year == date.year or year == date.year+1) and emp.payroll_id.id in payroll_ids[0][2]:     
                                    if emp.id not in emp_list:
                                        emp_list.append(emp.id)

                        employee_ids += emp_list
                        break
            
            if record.compute_per=='employee':
                if record.employee_ids:
                    [employee_ids.append((emp.employee_id.id)) for emp in  record.employee_ids]
                      
                else:
                    employee_ids = employee_ids and employee_ids or [x.id for x in record.payroll_ids_me]
            else:
                if record.state=='approve' and record.arch_ids:
                    employee_ids = record.batch_ids and [arc.employee_id.id for arc in record.arch_ids]
                else:
                    emp_ids =  [emp.id for emp in self.pool.get('hr.salary.batch').browse(cr, uid, [context['salary_batch_id']])[0].batch_id.employee_ids]
                    if emp_ids:
                        '''employee_ids = employee_obj.search(cr, uid, ['|',('state', '!=', 'refuse'),('delegation', '=', True),
                                                                 ('salary_suspend', '!=', True),('payroll_id', 'in', payroll_ids), 
                                                                 ('company_id', 'in', company_ids),  ('id', 'in', emp_ids)])'''
                        list_ids = employee_ids and employee_ids or [x.id for x in record.payroll_ids_me]
                        for x in emp_ids:
                            if x in list_ids:
                                employee_ids.append(x)

            domain = [('month', '=', record.month), ('year', '=', record.year), ('scale_id', 'in', payroll_ids),
                      ('employee_id', 'in', employee_ids), ('company_id', 'in', company_ids)]

            if record.type == 'salary':
                domain.append(('in_salary_sheet', '=', True))
            else:
                domain.append(('in_salary_sheet', '=', False))
            
            archive_ids = main_archive_obj.search(cr, uid, domain, context=context)
            addendums_arch_ids = []
            if archive_ids:
                if record.type == 'addendum':
                    addendums_arch_ids = archive_obj.search(cr, uid, [('main_arch_id', 'in', archive_ids),
                                                                      ('allow_deduct_id', 'in', addendum_ids)], context=context)
                    if not addendums_arch_ids:
                        archive_ids = []
            
           
            res = {
                'company_id':company_ids ,
                'payroll_ids': payroll_ids,
                'addendum_ids':addendum_ids ,
                'employee_ids':employee_ids,
                'month' :record.month,
                'year' :record.year,
                'date' :record.date,
                'type':record.type,
                'archive_ids':archive_ids,
                'addendums_arch_ids':addendums_arch_ids,
                'record_id':record.id,
                'deduct_ids':deduct_ids,
            }
        return res


    def compute(self, cr, uid, ids, context = {}):
        """Compute salary/addendum for all employees or specific employees in specific month.
           @return: Dictionary 
        """
        payroll_obj = self.pool.get('payroll')
        employee_obj = self.pool.get('hr.employee')
        addendum_perc_obj = self.pool.get('hr.salary.addendum.percentage')
        main_arch_obj = self.pool.get('hr.payroll.main.archive')
        status_obj = self.pool.get('hr.holidays.status')
        holiday_obj = self.pool.get('hr.holidays')
        delegation_obj = self.pool.get('hr.employee.delegation')
        allow_deduct_obj = self.pool.get('hr.allowance.deduction')
        attendance_line_obj = self.pool.get('suggested.attendance.line')
        data = self.get_data(cr, uid, ids, context=context)
        related_attendance = False
        if data['addendum_ids']:
            basic = allow_deduct_obj.browse(cr, uid, data['addendum_ids'],context=context)
            if len(data['addendum_ids']) == 1:
                related_attendance = basic[0].related_attendance
        '''if  data['archive_ids']:
            for record in self.browse(cr, uid, ids, context=context):
                lists=[]
                for arch in main_arch_obj.browse(cr, uid, data['archive_ids'], context=context):
                    if arch.employee_id.id not in lists:
                        lists.append((arch.employee_id.id))
                for rec in lists:
                    sum = 0
                    arch_ids=addendum_perc_obj.search(cr, uid, [('employee_id','=',rec),] , context=context)
                    for rec in addendum_perc_obj.browse(cr, uid, arch_ids, context=context):
                        if rec.adden_id.type == record.type and rec.adden_id.month == record.month:
                            if rec.adden_id.id != record.id:
                                sum += rec.percentage
                                if sum == 100:
                                    raise osv.except_osv(_('Error'), _('The  %s For Employee %s In The %sth Month Year Of %s It is  Already Computed')
                                                    % (record.type, rec.employee_id.name , record.month, record.year))     
                                if sum > 100:
                                    raise osv.except_osv(_('Error'), _('The  %s For Employee %s In The %sth Month Year Of %s It is Cannot Exceed %s  The Already Computed is %s')
                                                    % (record.type,rec.employee_id.name , record.month, record.year,100, sum-rec.percentage)) 
                            else:
                                sum += rec.percentage
                                if sum > 100:
                                    raise osv.except_osv(_('Error'), _('The  %s For Employee %s In The %sth Month Year Of %s It is Cannot Exceed %s  The Already Computed is %s')
                                                    % (record.type,rec.employee_id.name , record.month, record.year,100, sum-rec.percentage)) 
                                if rec.adden_id.id >= record.id :
                                    sum =0'''

        if  context.get('salary_batch_id'):
            self.pool.get('hr.salary.batch').write(cr,uid,[context.get('salary_batch_id')],{'batch_total':len(data['employee_ids']),} )
        paroll_date = (datetime.date (int(data['year']), int(data['month']), 1) + relativedelta(day=1, months= +1, days= -1))
        #paroll_date = mx.DateTime.Parser.DateTimeFromString(paroll_date)
        unpaied = status_obj.search(cr, uid, [('payroll_type', '=', 'unpaied')])
        customized = status_obj.search(cr, uid, [('payroll_type', '=', 'customized')])
        hol = self._get_leave_status(cr, uid, ids, data['employee_ids'] , data['month'], data['year'], paroll_date)
        #hol_adden = self._get_leave_status_addendum(cr, uid, ids, data['employee_ids'] , data['month'], data['year'], paroll_date)
        hol_adden = hol
        unpaied_del = delegation_obj.search(cr, uid, [('payroll_type', '=', 'unpaied')])
        customized_del = delegation_obj.search(cr, uid, [('payroll_type', '=', 'customized')])
        deligation = self._get_delgation(cr, uid , ids, data['employee_ids'], data['month'], data['year'],paroll_date)
        
        for employee in employee_obj.browse(cr, uid, data['employee_ids'], context=context):
            basic_salary = 0.0
            days = 30
            leave_days = 0
            in_salary_sheet = False
            addendum_amount =0
            percentage= 1
            percent=0
            allow_deduct_dict = []

            for x in  self.browse(cr,uid,ids)[0].employee_ids:
                if x.employee_id.id == employee.id:
                    percent = x.percentage
                    percentage = percent
            percentage = float('{0:.2f}'.format((percentage/100)))
            if data['type'] == 'salary':
                check_emp_holi=holiday_obj.search(cr,uid,[('employee_id','=',employee.id),('date_from','<=',data['date']),('date_to','>=',data['date']),('state','=','validate')])
                check_emp_holi_ids=holiday_obj.browse(cr,uid,check_emp_holi)
                if not check_emp_holi_ids or check_emp_holi_ids[0].holiday_status_id.payroll_type !='unpaied':
                    in_salary_sheet = True
                    basic_salary = employee.bonus_id.basic_salary
                    
                    salary = basic_salary * percentage
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
                            leave_days = dict1['days']
                            if leave_days < 0 : leave_days = 0
                            if leave_days >= 0 :
                                unpaied_salary = (basic_salary / 30) * leave_days
                                salary = (salary) - (unpaied_salary * percentage)
                                #basic_salary = (basic_salary / 30) * days 
                    basic_salary = salary
                    
                    customized_allow_deduct = []
                    for cus in customized:
                        dict2 = hol.get((employee.id, 'customized', cus), {})
                        if dict2:
                            days -= dict2['days']
                            customized_allow_deduct += self.write_allow_deduct(cr, uid, ids, employee.id, dict2['days'], dict2['allow_deduct_ids'], data['date'])
                    # unpaied and  customized delegation
                    for un in unpaied_del:
                        dict1 = deligation.get((employee.id, 'unpaied', un), {})
                        if dict1:
                            days -= dict1['days']
                            if days < 0 : days = 0
                            if days >= 0 :
                                basic_salary = (basic_salary / 30) * days
                                customized_allow_deduct = []
                    for cus in customized_del:
                        dict2 = deligation.get((employee.id, 'customized', cus), {})
                        if dict2:
                            days -= dict2.get('days', 0)
                            customized_allow_deduct += self.write_allow_deduct(cr, uid, ids, employee.id, dict2['days'], dict2['allow_deduct_ids'], data['date'])
                    allow_deduct_dict = self.write_allow_deduct(cr, uid, ids, employee.id, days,[], data['date'])
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
            else:
                for addendum in data['addendum_ids']+data['deduct_ids']:
                    addendum_amount_t = 0.0
                    addendum_rec = allow_deduct_obj.browse(cr,uid,addendum)
                    if addendum_rec.link_with_unpaid_leaves == False:
                        check_employment=addendum_rec.based_employment
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
                               if check_employment == 'based':
                                    amount = addendum_rec.linked_absence and amount_dict['result'][0]['amount'] or (amount_dict['result'][0]['amount'])/365 * days
                               else:
                                    amount = addendum_rec.linked_absence and amount_dict['result'][0]['amount'] or (amount_dict['result'][0]['amount'])
                               if amount != 0.0:
                                   addendum_dict = {
                                        'allow_deduct_id': addendum,
                                        'amount':amount,
                                        'tax_deducted':amount_dict['result'][0]['tax'],
                                        'imprint':amount_dict['result'][0]['imprint'],
                                        'remain_amount':amount_dict['result'][0]['remain_amount'],
                                    }
                                   allow_deduct_dict.append(addendum_dict)
                    else:
                        check_emp_holi=holiday_obj.search(cr,uid,[('employee_id','=',employee.id),('date_from','<=',data['date']),('date_to','>=',data['date']),('state','=','validate')])
                        check_emp_holi_ids=holiday_obj.browse(cr,uid,check_emp_holi)
                        check_employment=addendum_rec.based_employment
                        if not check_emp_holi_ids or check_emp_holi_ids[0].holiday_status_id.payroll_type !='unpaied':
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
                                if check_employment == 'based':
                                    amount = addendum_rec.linked_absence and amount_dict['result'][0]['amount'] or (amount_dict['result'][0]['amount'])/365 * days
                                else:
                                    amount = addendum_rec.linked_absence and amount_dict['result'][0]['amount'] or (amount_dict['result'][0]['amount'])
                                if amount != 0.0:
                                    addendum_dict = {
                                        'allow_deduct_id': addendum,
                                        'amount':amount,
                                        'tax_deducted':amount_dict['result'][0]['tax'],
                                        'imprint':amount_dict['result'][0]['imprint'],
                                        'remain_amount':amount_dict['result'][0]['remain_amount'],
                                    }
                                    allow_deduct_dict.append(addendum_dict)
                                #amount = amount_dict['result'][0]['holiday_amount'] and amount_dict['result'][0]['holiday_amount'] or amount_dict['result'][0]['amount']
                                '''leave_total =0                           
                                addendum_amount = amount * percentage
                                for un in unpaied:
                                    dict1 = hol_adden.get((employee.id, 'unpaied', un), {})
                                    if dict1:
                                        #days -= dict1['days']
                                        leave_days = dict1['days']
                                        if leave_days <= 0 : leave_days = 0
                                        if leave_days > 0 :
                                            #amount = (amount / 365) * days
                                            leave_total +=  leave_days

                                unpaied_amount = (amount/30) * leave_total
                                addendum_amount = (addendum_amount) - (unpaied_amount * percentage)
                                addendum_amount_t += addendum_amount
                                amount -= unpaied_amount
                                addendum_dict = {
                                    'allow_deduct_id': addendum,
                                    'amount':addendum_amount_t  ,
                                    'tax_deducted':amount_dict['result'][0]['tax'],
                                    'imprint':amount_dict['result'][0]['imprint'],
                                    'remain_amount':amount_dict['result'][0]['remain_amount'],
                                }
                                allow_deduct_dict.append(addendum_dict)'''
            if data['type'] == 'salary':
                for allwance in allow_deduct_dict:
                    allwance['percentage']= percent
                    allwance['final_amount']= allwance['amount'] * percentage
            else:
                for allwance in allow_deduct_dict:
                    allwance['percentage']= percent
                    allwance['final_amount']= addendum_amount
            if allow_deduct_dict and data['type'] != 'salary':
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
                    'allow_deduct' : data['addendum_ids'][0] or False,
                }, context = context)
            else:
                if allow_deduct_dict :
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
                    }, context = context)
            ##attendance###############employee.id
            if related_attendance:
                arch_ids=addendum_perc_obj.search(cr, uid, [('employee_id','=',employee.id),('adden_id','in',ids )] , context=context)
                
                attendance_ids = attendance_line_obj.search(cr, uid, [('state', '=', 'done'), ('flage', '=', False),('emp_id','=', employee.id)],context={})
                
                att_percent = attendance_line_obj.read(cr, uid, attendance_ids,['added_percent'], context={})

                num_attend = 0.0
                if att_percent:
                    try:
                        num_attend = att_percent[0]['added_percent']
                        num_attend = round(num_attend,0)
                    except:
                        pass
                addendum_perc_obj.write(cr, uid, arch_ids,{'percentage':num_attend})
                    
                
        if not context.get('salary_batch_id'):
            self.write(cr, uid, ids, { 'state': 'compute'}, context=context)
        else :
            state = len([btch.id for btch in self.browse(cr,uid,ids)[0].batch_ids if btch.state not in ('compute','approve')])-1 > 0 and 'draft' or 'compute'
            self.write(cr, uid, ids, { 'state': state}, context=context)
        return {}

    def _get_leave_status_addendum(self, cr, uid, ids, employee_ids , month, year, paroll_date):
        month = int(month)
        year = int(year)
        holidays = {}
        status_obj = self.pool.get('hr.holidays.status')
        status_ids = status_obj.search(cr, uid, [('payroll_type', 'in', ('customized', 'unpaied'))])
        if status_ids:
            cr.execute("""select h.id AS holiday_id, s.id AS status_id  ,h.employee_id AS employee_id,s.payroll_type AS type,
                         (CASE WHEN  EXTRACT(YEAR FROM h.date_from) =%s THEN
                                    30-EXTRACT(DAY FROM h.date_from)+1
                                      ELSE 30 
                                END)+
                         (CASE WHEN EXTRACT(YEAR FROM h.date_to) =%s THEN
                                    EXTRACT(DAY FROM h.date_to)
                                      ELSE 30
                                END) - 30 as days
                          from  hr_holidays h 
                          LEFT JOIN hr_holidays_status s ON (s.id=h.holiday_status_id)
                          where h.state NOT IN ('cancel','refuse')
                          and h.type='remove'
                          and (h.date_from <= %s and h.date_to >=%s or 
                               EXTRACT(YEAR FROM h.date_from) =%s or
                               EXTRACT(YEAR FROM h.date_to) =%s)
                          and h.holiday_status_id IN %s
                          and h.employee_id IN %s
                          """ , ( year, year, paroll_date, paroll_date ,year,  year, tuple(status_ids), tuple(employee_ids),))
            res = cr.dictfetchall()
            for r in res:
                key = (r['employee_id'], r['type'], r['status_id'])
                if not key in holidays:
                    allow_deduct_ids = []
                    holidays[key] = r
                    if r['type'] == 'customized':
                        allow_deduct_ids = [r.id for r in status_obj.browse(cr, uid, r['status_id']).allow_deduct_ids]
                    holidays[key].update({'allow_deduct_ids':allow_deduct_ids})
                else:
                    holidays[key]['days'] += r['days']
        return holidays

    def write_allow_deduct(self, cr, uid, ids, emp_id, days, allow_deduct_ids=[], date=None):
        """Create allowances and deductions dictionaries for employees salary in specific month.
        @param emp_id : Id of employee
        @param days : Number of employment days
        @return: List of dictionaries
        """
        emp_salary_obj = self.pool.get('hr.employee.salary')
        payroll_obj = self.pool.get('payroll')
        salary_allow_deduct_obj = self.pool.get('hr.salary.allowance.deduction')
        employee_obj = self.pool.get('hr.employee')
        employee = employee_obj.browse(cr, uid, emp_id)
        
        dict_list = []
        allow_deduct_list = []
        if days > 0:
            if days > 30 : days = 30
            domin = [('employee_id', '=', emp_id)]
            if allow_deduct_ids:
                domin += [('allow_deduct_id', 'in', allow_deduct_ids)]
            #first re_calc allowances for the employee if he has Mile allowances
            if employee.mile_allowance:
                employee_obj.write_employee_salary(cr, uid, [emp_id], [], date)

            allow_deduct_ids = emp_salary_obj.search(cr, uid, domin)
            for allow_deduct1 in emp_salary_obj.browse(cr, uid, allow_deduct_ids):
                if allow_deduct1.allow_deduct_id.linked_absence and allow_deduct1.allow_deduct_id.id not in allow_deduct_list:
                    allow_deduct_list.append(allow_deduct1.allow_deduct_id.id)
            
            '''if allow_deduct_list:
                    employee_obj.write_employee_salary(cr, uid, [emp_id], [], date)
                    allow_deduct_dict = payroll_obj.allowances_deductions_calculation(cr, uid, date, emp, {}, [allow_deduct_rec.id])'''

            if allow_deduct_ids:
                for allow_deduct in emp_salary_obj.browse(cr, uid, allow_deduct_ids):
                    if allow_deduct.allow_deduct_id.name_type == 'deduct' and  allow_deduct.allow_deduct_id.deduction_from == 'addendum':
                        continue
                    
                    #allow_deduct_amount = allow_deduct.holiday_amount and (allow_deduct.holiday_amount / 30) * days or (allow_deduct.amount / 30) * days
                    #else:
                    allow_deduct_amount = allow_deduct.allow_deduct_id.linked_absence and allow_deduct.amount or (allow_deduct.amount / 30) * days
                    company_amount = 0.0
                    if allow_deduct.allow_deduct_id.company_load:
                        deduct_salary_id = salary_allow_deduct_obj.search(cr, uid, [
                                                    ('degree_id', '=', allow_deduct.employee_id.degree_id.id),
                                                    ('allow_deduct_id', '=', allow_deduct.allow_deduct_id.id)])
                        if deduct_salary_id:
                            deduct_percentage = salary_allow_deduct_obj.browse(cr, uid, deduct_salary_id)[0].amount
                            company_amount = allow_deduct_amount * allow_deduct.allow_deduct_id.percentage / deduct_percentage
                    tax_deducted = (allow_deduct.tax_deducted / 30) * days
                    allow_deduct_dict = {
                        'allow_deduct_id': allow_deduct.allow_deduct_id.id,
                        'type' : allow_deduct.allow_deduct_id.name_type,
                        'amount': allow_deduct_amount ,
                        'percentage': 0.0,
                        'final_amount': 0.0,
                        'tax_deducted':tax_deducted ,
                        'company_amount':company_amount,
                        'remain_amount': allow_deduct.remain_amount ,
                    }
                    dict_list.append(allow_deduct_dict)
        return dict_list

    def transfer(self, cr, uid, ids, context = None):
        """Override transfer function for ntc customization in case for salary transfer
        @return: Dictionary 
        """
        #### from hr_payroll_custom
        if context is None: context = {}
        salary_scale_obj = self.pool.get('hr.salary.scale')
        degree_cat_obj = self.pool.get('hr.degree.category')
        degree_obj = self.pool.get('hr.salary.degree')
        tax_amount = 0.0
        stamp_amount = 0.0
        zakat_amount = 0.0
        lines = []
        cat_ids = []
        voucher_ids = []
        user = self.pool.get('res.users').browse(cr, uid, uid, context=context)
        if not user.company_id.hr_analytic_account_id:
                raise osv.except_osv(_('ERROR'), _('Please enter Analytic Account for Your Company'))
        data = self.get_data(cr, uid, ids, context=context)
        data['payroll_ids'] += [0]
        reference = "HR/PAY/" + str(data['type']) + str(data['month']) + "/" + str(data['year'])
        narration = "تاريخ حساب الحافز: " + str(data['date'])
        if data['type'] == 'salary':
            narration = "تاريخ حساب المرتب: " + str(data['date'])
        arc_ids = self.pool.get('hr.payroll.main.archive').search(cr,uid,[('arch_id','=',ids[0])])
        data['archive_ids'] = arc_ids
        if not data['archive_ids']:
            raise osv.except_osv(_('Error'), _('No Such %s In The %sth Month Year Of %s To Be Transfer')
                                    % (data['type'], data['month'], data['year']))
        where = [tuple(data['archive_ids'])]
        in_salary_sheet = True
        if data['type'] == 'salary':
            cr.execute("select scale_id from category_degree_payroll_rel where cat_id in %s", (tuple(data['payroll_ids']),))
            cat_ids += [x['scale_id'] for x in cr.dictfetchall()] 
            for cat_rec in degree_cat_obj.browse(cr,uid,cat_ids):
                degrees = degree_obj.search(cr,uid,[('category_id','=',cat_rec.id)])
                if degrees:
                    where2 = []
                    degrees.append(0)
                    where2 += [x for x in where]
                    where2.append(tuple(degrees))
                    cr.execute(
                        'select scale_id as scale_id ,sum(COALESCE(basic_salary,0)) as basic_salary, ' \
                        'sum(COALESCE(tax,0)) as tax , '\
                        'sum(COALESCE(zakat,0)) as zakat '\
                        'from hr_payroll_main_archive '\
                        'where id IN %s '\
                        'and degree_id IN %s '\
                        'group by  scale_id', (tuple(where2)) )
                    ress = cr.dictfetchall()
                    for r in ress:
                        tax_amount += r.get('tax', 0.0)
                        zakat_amount += r.get('zakat', 0.0)
                        account_id = salary_scale_obj.browse(cr, uid, r['scale_id'], context=context).account_id
                        if not account_id:
                            raise osv.except_osv(_('Configuration Error !'),
                                                 _('Please Enter Account for salary scale !'))
                        if not cat_rec.account_id:
                            raise osv.except_osv(_('Configuration Error Of Degrees Category!'),
                                                 _('Please Enter Account for %s !')%(cat_rec.name))
                        line = {
                            'name':'Basic Salary',
                            'account_id':cat_rec.account_id.id,
                            'amount':round(r['basic_salary'], 2),
                            'account_analytic_id':user.company_id.hr_analytic_account_id.id,
                        }
                        lines.append(line)
            if zakat_amount:
                if not user.company_id.zakat_account_id:
                    raise osv.except_osv(_('ERROR'), _('Please enter zakat account for Your Company')) 
                zakat_line = {
                    'name':'Salary zakat',
                    'account_id':user.company_id.zakat_account_id.id,
                    'amount':-zakat_amount,
                }
                lines.append(zakat_line)
                zakat_line2 = zakat_line.copy()
                zakat_line2.update({'amount':zakat_amount})
                zakat_voucher_id = self.pool.get('payroll').create_payment(cr, uid, ids,
                            {'reference':"HR/Salary Zakat" + "/" + str(data['month']) + "/" + str(data['year']),
                             'lines':[zakat_line]}, context=context)
                voucher_ids.append(zakat_voucher_id)
        addendum_clause = ''
        if data['addendum_ids']:
            in_salary_sheet = False
            addendum_clause = ' and ad.allow_deduct_id in %s '
            where.append(tuple(data['addendum_ids']+data['deduct_ids']))
        cr.execute(
            'select ad.allow_deduct_id as allow_deduct_id ,sum(COALESCE(ad.amount,0)) as amount,'\
            'sum(ad.tax_deducted) as tax_deducted,sum(COALESCE(ad.imprint,0)) as imprint, '\
            'sum(COALESCE(ad.company_amount,0)) as company_amount '\
            'from hr_allowance_deduction_archive ad '\
            'LEFT JOIN hr_payroll_main_archive m ON (ad.main_arch_id=m.id) '\
            'where m.id IN %s '\
            + addendum_clause + 
            'group by  ad.allow_deduct_id', tuple(where))

        res = cr.dictfetchall()
        for r in res:
            line = {
                'allow_deduct_id':r['allow_deduct_id'],
                'amount':round(r['amount'], 2),
                'company_amount':round(r['company_amount'], 2),
                'account_analytic_id':user.company_id.hr_analytic_account_id.id,
            }
            lines.append(line)
            tax_amount += r.get('tax_deducted', 0.0)
            stamp_amount += r.get('imprint', 0.0)
        number = self.pay(cr, uid, ids, {'reference':reference, 'lines':lines, 'narration':narration,
                                           'tax_amount':tax_amount, 'stamp_amount':stamp_amount,
                                           'in_salary_sheet':in_salary_sheet}, context=context)
      
        '''if tax_amount:
            tax_voucher_id = self.pool.get('payroll').create_payment(cr, uid, ids,
                            {'reference':"HR/Taxs" + "/" + str(data['type']) + str(data['month']) + "/" + str(data['year']),
                             'lines':[], 'tax_amount':-tax_amount}, context=context)
            voucher_ids.append(tax_voucher_id)'''
            
        voucher_ids += self.company_load_transfer(cr, uid, ids, lines, context)
        for rec in self.browse(cr, uid, ids):
            if rec.compute_per=='batch' and rec.batch_ids:
                self.pool.get('hr.salary.batch').write(cr, uid, [bat.id for bat in rec.batch_ids  ], {'state': 'transferred'}, context=context)

        self.write(cr, uid, ids, {'number':number, 'voucher_ids':[(6, 0, voucher_ids)], 'state': 'transferred'}, context=context)
        
        ######## from hr_loan
        user = self.pool.get('res.users').browse(cr, uid, uid, context = context)
        journal_id = user.company_id.hr_journal_id and user.company_id.hr_journal_id.id or False
        ctx = context.copy()
        ctx.update({'company_id': user.company_id.id, 'account_period_prefer_normal': True})
        period_id = self.pool.get('account.period').find(cr, uid, time.strftime('%Y-%m-%d'), context=ctx)[0]
        data = self.get_data(cr, uid, ids, context = context)
        res = {}
        move_lines = []
        loan_move={
            'journal_id':journal_id,
            'period_id': period_id,
            'date':time.strftime('%Y-%m-%d'),
        }
        
        move_id = self.pool.get('account.move').create(cr,uid,loan_move) 
        loan_arc=[]
        #arc_ids = self.pool.get('hr.payroll.main.archive').search(cr,uid,[('arch_id','=',ids[0])])
        for arc in self.pool.get('hr.payroll.main.archive').browse(cr, uid, arc_ids, context=context):
            for loan in arc.loan_ids:
                loan_arc.append(loan.id) 
        for archive in self.pool.get('hr.loan.archive').browse(cr, uid, loan_arc, context):
            if archive.loan_id.loan_id.transfer_with_partner != 'with_partner': continue
            loan = archive.loan_id.loan_id
            voucher_line_loan={
                'journal_id':journal_id,
                'account_id':loan.loan_account_id.id,
                'date':time.strftime('%Y-%m-%d'),
                'name':archive.loan_id.name,
                'period_id':period_id,
                'debit':0,
                'credit':archive.loan_amount,
                'partner_id':archive.employee_id.user_id.partner_id.id,
                'move_id':move_id
                }
            move_lines = move_lines + [self.pool.get('account.move.line').create(cr,uid,voucher_line_loan)]
            if loan.id in res:
                res[loan.id].update({'debit':res[loan.id]['debit']+archive.loan_amount})
            else:
                res[loan.id] = voucher_line_loan.copy()
                res[loan.id].update({'debit':archive.loan_amount, 'credit':0 })
        if not move_lines:
            self.pool.get('account.move').unlink(cr,uid,[move_id])
        if move_lines:
            for r in res:
                res[r].update({'partner_id':False})
                move_lines = move_lines + [self.pool.get('account.move.line').create(cr,uid,res[r])]

        basic = self.browse(cr, uid, ids, context=context)
        for x in basic:
            for addendum in x.addendum_ids:
                if addendum.related_attendance:
                    attendance_line_obj = self.pool.get('suggested.attendance.line')
                    attendance_ids = attendance_line_obj.search(cr, uid, [('state', '=', 'done'), ('flage', '=', False)],context={})
                    attendance_line_obj.write(cr, uid, attendance_ids, {'flage': True},context={})
                            
        return True
    
class hr_payroll_main_archive(osv.Model):

    _inherit = "hr.payroll.main.archive"
    
    def create_loan_archive(self, cr, uid, arch_type, rec, loan, net, loan_dict, ad_arch=False, context=None):
        loan_archive_obj = self.pool.get('hr.loan.archive')
        emp_perc_obj = self.pool.get('hr.salary.addendum.percentage')
        wf_service = netsvc.LocalService("workflow")
        paid_amount = 0
        domain = [('employee_id','=',rec.employee_id.id),\
            ('loan_id','=',loan.id),('month','=',rec.month),('year','=',rec.year)]
        if arch_type ==  'salary':
            loan_ids= loan_archive_obj.search(cr,uid, domain+[('payment_type','=','salary')])
            for l in loan_archive_obj.browse(cr, uid,  loan_ids, context):
                paid_amount += l.loan_amount
            refund_amount = loan.salary_refund
            installment = loan.installment_amount
        else:   
            loan_ids= loan_archive_obj.search(cr,uid, domain+[('addendum_id','=',ad_arch)])
            for l in loan_archive_obj.browse(cr, uid,  loan_ids, context):
                paid_amount += l.loan_amount
            refund_amount = loan.addendum_refund
            installment = loan.addendum_install
            #do this check in salary case only 
        amount = 0.0
        if installment:
            if loan.state <> 'suspend':
                amount = installment
            else:
            #if loan suspend compare the end date of suspend with salary date  
                for suspend in loan.loan_suspend_ids:
                    if suspend.start_date >= rec.salary_date or \
                    (suspend.start_date <= rec.salary_date and(suspend.end_date and suspend.end_date <= rec.salary_date)):
                        amount=installment
                        if suspend.start_date <= rec.salary_date and suspend.end_date <= rec.salary_date:
                            wf_service.trg_validate(uid,'hr.employee.loan', loan.id, 'paid', cr)

        remain = refund_amount - paid_amount         
        if remain:
            if remain < amount:
                amount =  remain 
            if loan.remain_installment -loan.remission_amount < amount:
                amount = loan.remain_installment-loan.remission_amount
        
        if amount and net > 0.0:
            #TODO: what if (loan.remain_installment<loan.remission)??
            if amount >= net:
                amount= net

        archive_id = False                        
        if amount > 0:	
            percentage =1		
            idss =emp_perc_obj.search(cr, uid, [('employee_id', 'in', [rec.employee_id.id]),('adden_id','=',rec.arch_id.id)])
            if idss:
                addendum_percentage = emp_perc_obj.browse(cr, uid, idss)[0].percentage
                percentage = float('{0:.2f}'.format((addendum_percentage/100)))    
            loan_dict.update({'loan_id':loan.id,'loan_amount':amount,'percentage': percentage*100,'final_amount':amount*percentage})  
            archive_id = loan_archive_obj.create(cr, uid, loan_dict, context)    
        return {'archive_id': archive_id, 'amount': amount}

    def total_allow_deduct(self, cr, uid, ids, name, args, context=None):
        """
        Method for functional fieldl that overwrites hr.payroll.main.archive 
        total_allow_deduct mehtod and caluclates the totals of employee's 
        allowances, deductions, tax, loans and gets the net.
        
        @param name: name of field to be updated
        @param args: other arguments
        @return: Dictionary of values 
        """
        emp_perc_obj = self.pool.get('hr.salary.addendum.percentage')
        emp_loan_obj = self.pool.get('hr.employee.loan')
        loan_archive_obj = self.pool.get('hr.loan.archive')
        alw_dec_arch = self.pool.get('hr.allowance.deduction.archive')
        tax = self.pool.get('hr.tax')
        zakat_obj = self.pool.get('hr.zakat')
        result = {}
        for rec in self.browse(cr, uid, ids, context=context):
            taxable_amount = 0.0
            allowances_tax = 0.0
            income_tax = 0.0
            total_deduction = 0.0
            zakat_amount = 0.0
            percentage =1
            idss =emp_perc_obj.search(cr, uid, [('employee_id', 'in', [rec.employee_id.id]),('adden_id','=',rec.arch_id.id)])
            if idss:
		        addendum_percentage = emp_perc_obj.browse(cr, uid, idss)[0].percentage
		        percentage = float('{0:.2f}'.format((addendum_percentage/100)))
            total_allowance = rec.basic_salary
            
            for line in rec.allow_deduct_ids:
                if line.type == 'allow':
                    total_allowance += line.amount*percentage
                    allowances_tax += line.tax_deducted
                    total_deduction += line.imprint
                    if rec.employee_id.degree_id.taxable and line.allow_deduct_id.taxable and not rec.employee_id.tax_exempted:
                        taxable_amount += line.amount - line.allow_deduct_id.exempted_amount
                else:
                    total_deduction += line.amount*percentage
                    if rec.employee_id.degree_id.taxable and line.allow_deduct_id.taxable and not rec.employee_id.tax_exempted:
                        taxable_amount -= line.amount - line.allow_deduct_id.exempted_amount
            if rec.in_salary_sheet:
                zakat_id = zakat_obj.search(cr, uid, ['|', ('end_date', '>=', rec.salary_date), ('end_date', '=', False), ('start_date', '<=', rec.salary_date)])
                if zakat_id:
                    zakat = zakat_obj.browse(cr, uid, zakat_id)[0]
                    if rec.employee_id.religion == 'muslim':
                        amount = rec.basic_salary - zakat.minimal_amount
                        if amount >= zakat.monthly_value:
                            zakat_amount = amount * zakat.zakat_percentage / (100)
                if rec.employee_id.degree_id.taxable and not rec.employee_id.tax_exempted:
                    taxable_amount += rec.basic_salary
                    tax_id = tax.search(cr, uid, [('taxset_min', '<=', taxable_amount), ('taxset_max', '>=', taxable_amount)], context=context)
                    if tax_id:
                        tax_rec = tax.browse(cr, uid, tax_id)[0]
                        taxable_amount = abs(taxable_amount * tax_rec.income_tax_percentage / 100) 
                        income_tax = (((taxable_amount - tax_rec.taxset_min) * tax_rec.percent) / 100) + tax_rec.previous_tax - zakat_amount
            if total_deduction > total_allowance:
                raise osv.except_osv(_('Error'), _('The deductions of employee %s exceed his total allowance . ') % (rec.employee_id.name)) 
            result[rec.id] = {
                'tax':income_tax,
                'zakat': zakat_amount,
                'total_allowance':total_allowance,
                'allowances_tax': allowances_tax,
                'total_deduction': total_deduction + allowances_tax + income_tax + zakat_amount,
                'net':(total_allowance - allowances_tax - total_deduction - income_tax - zakat_amount),
            }
            # Create loan deduction
            total_loans = 0.0
            loan_dict = {'payroll_id' :rec.employee_id.payroll_id.id,
                            'employee_id':rec.employee_id.id,
                            'month':rec.month,
                            'year':rec.year,
                            'payment_type':rec.arch_id.type ,
                            'main_arch_id' :rec.id,}
            net = result[rec.id]['net']
            #TODO: Add to domain salary type 
            '''domain = [('loan_id.refund_from','=',rec.arch_id.type),\
                      ('employee_id','=',rec.employee_id.id),('state','in',('paid','suspend')),\
                    ('start_date','<=',rec.salary_date)]'''
            domain = [('loan_id.refund_from','in',[rec.arch_id.type, 'both']),\
                      ('employee_id','=',rec.employee_id.id),('state','in',('paid','suspend')),\
                    ('start_date','<=',rec.salary_date)]
            if rec.arch_id.type == 'salary':
                loan_ids= emp_loan_obj.search(cr, uid, domain)
                if loan_ids:
                    for loan in emp_loan_obj.browse(cr,uid,loan_ids):
                        if net > 0 :
                            loan_dic = self.create_loan_archive(cr, uid, 'salary', rec, loan,  net, loan_dict)
                            amount = loan_dic['amount']
                            net-=amount
                            total_loans += amount*percentage
                    
            else:
            	if  rec.arch_id.loan_deduction == '1' :
	                loans_ids= emp_loan_obj.search(cr, uid, domain + \
	                [('loan_id.addendum_ids','in',[re.id for re in rec.arch_id.addendum_ids if re])])
	                if loans_ids:                           
	                    for loan in emp_loan_obj.browse(cr,uid,loans_ids):
	                        # its better to cancel this condition
	                        paid_installment= loan_archive_obj.search(cr,uid,[('employee_id','=',rec.employee_id.id),
	                                                                       ('loan_id','=',loan.id),
	                                                                       ('month','=',rec.month),('year','=',rec.year)])
	                        amount = 0.0
	                        if (loan.loan_id.refund_from == 'addendum' and not paid_installment) or loan.loan_id.refund_from == 'both':
	                            # if loan installment not paid from loan paid wizard for current month then get installment loan amount for current month to deduct from addendum  
	                            loan_adndm_ids= [ln.id for ln in loan.loan_id.addendum_ids]
	                            if loan.remain_installment and len(loan_adndm_ids)>0 :
	                                for adn in rec.arch_id.addendum_ids:
	                                    adndm_amount=0
	                                    if adn.id in loan_adndm_ids :
	                                        ad_arch_ids = alw_dec_arch.search(cr,uid,[('allow_deduct_id','=',adn.id),('main_arch_id','=',rec.id)])
	                                        if ad_arch_ids:
	                                            ad_arch = alw_dec_arch.browse(cr,uid,ad_arch_ids)[0]
	                                            adndm_amount=ad_arch.amount-ad_arch.imprint-ad_arch.tax_deducted#d ammount s d net
	                                            ather_loan_ids = loan_archive_obj.search(cr,uid,[('addendum_id','=',ad_arch.id),('main_arch_id','=',rec.id)])
	                                            if ather_loan_ids:
	                                                for sm in loan_archive_obj.browse(cr,uid,ather_loan_ids):
	                                                    adndm_amount-=sm.loan_amount
	                                            loan_dic = self.create_loan_archive(cr, uid, 'addendum',rec, \
	                                                            loan, adndm_amount*percentage, loan_dict, ad_arch.id)
	                                            amount = loan_dic['amount']
	                                            if 'archive_id' in loan_dic:
	                                                loan_archive_obj.write(cr,uid,loan_dic['archive_id'],{'addendum_id':ad_arch.id})
	                                                net-=amount
	                                                total_loans += amount                         
            
            result[rec.id].update({'total_loans':total_loans,'net':result[rec.id]['net']-total_loans,}) 
        return result

    _columns={
        'total_loans': fields.function(total_allow_deduct, string='Total Loans', type='float',
                                          digits_compute=dp.get_precision('Payroll'), multi='sum', readonly=True, store=True),
        'total_allowance' :fields.function(total_allow_deduct, string='Total Allowance', type='float',
                                          digits_compute=dp.get_precision('Payroll'), multi='sum', readonly=True, store=True),
        'tax' :fields.function(total_allow_deduct, string='Income Tax', type='float',
                                          digits_compute=dp.get_precision('Payroll'), multi='sum', readonly=True, store=True),
        'allowances_tax' :fields.function(total_allow_deduct, string='Allowance Taxes', type='float',
                                          digits_compute=dp.get_precision('Payroll'), multi='sum', readonly=True, store=True),
        'total_deduction' :fields.function(total_allow_deduct, string='Total Deduction', type='float',
                                          digits_compute=dp.get_precision('Payroll'), multi='sum', readonly=True, store=True),
        'net' :fields.function(total_allow_deduct, string='Salary Net', type='float',
                                          digits_compute=dp.get_precision('Payroll'), multi='sum', readonly=True, store=True),
        'zakat': fields.function(total_allow_deduct, string='Zakat', type='float',
                                      digits_compute=dp.get_precision('Payroll') ,  multi='sum',readonly=True, store=True),
        'allow_deduct':fields.many2one('hr.allowance.deduction', "Allowance"),
    }


class hr_allowance_deduction_archive(osv.Model):

    _inherit = "hr.allowance.deduction.archive"

    _columns = {
         'percentage' :fields.integer("Percentage", readonly=True),
         'final_amount' : fields.float("Final Amount", digits_compute=dp.get_precision('Payroll'), readonly=True),
    }

class hr_loan_archive(osv.osv):
    _inherit = "hr.loan.archive"
    
    _columns = {
		'percentage' :fields.integer("Percentage", readonly=True),
        'final_amount' : fields.float("Final Amount", digits_compute=dp.get_precision('Payroll'), readonly=True),
    }


class hr_salary_addendum_percentage(osv.Model):

    _inherit = 'hr.salary.scale'
    _columns = {
                'subs_period' :fields.integer("Substituation Period "),
                'active' : fields.boolean('Active'),
                'cat_ids': fields.many2many('hr.degree.category','category_degree_payroll_rel','cat_id','scale_id', 'Categries'),
                  
                }

    _defaults = {
        'active':'1',
    }


class hr_allowance_deduction(osv.osv):

    _inherit = "hr.allowance.deduction"


    _columns = {
        'allow_out_employee' : fields.boolean('Allow Out Of Service Employees'),
        'type3' :fields.selection([('1','Structural'),('2','Non-Structural')],"Allowance / Deduction Type"),
        'deduction_from' :fields.selection([('salary','Salary'),('addendum','Addendum')],"Deduction From"),
        'allowance_type':fields.selection([('serv_terminate', 'Allowance of Service Terminated'),
                                           ('qualification', 'Qualification'), ('substitution', 'Substitution'),
                                           ('family_relation', 'Family Relation'), ('general', 'General'),
                                           ('in_cycle', 'In Cycle'), ('mile_allowance', 'Mile Allowance')
                                           ], 'Allowance type'),
        'analytic_id': fields.property('account.analytic.account', type='many2one', relation='account.analytic.account',
                                       string='Analytic Account', method=True, view_load=True),
        }

    _defaults = {
        'type3':'1',
        'deduction_from':'salary',
    }


class hr_employee_substitution(osv.osv):

    _inherit = "hr.employee.substitution"
    _track = {
        'state': {
            'hr_ntc_custom.mt_substitution_draft': lambda self, cr, uid, obj, ctx=None: obj['state'] == 'draft',
            'hr_ntc_custom.mt_substitution_complete': lambda self, cr, uid, obj, ctx=None: obj['state'] == 'complete',
            'hr_ntc_custom.mt_substitution_confirm': lambda self, cr, uid, obj, ctx=None: obj['state'] == 'confirm',
            'hr_ntc_custom.mt_substitution_general_dep': lambda self, cr, uid, obj, ctx=None: obj['state'] == 'general_dep',
            'hr_ntc_custom.mt_substitution_hr_finance': lambda self, cr, uid, obj, ctx=None: obj['state'] == 'hr_finance',
            'hr_ntc_custom.mt_substitution_implement': lambda self, cr, uid, obj, ctx=None: obj['state'] == 'implement',
            'hr_ntc_custom.mt_substitution_approved': lambda self, cr, uid, obj, ctx=None: obj['state'] == 'approve',
            'hr_ntc_custom.mt_substitution_cancel': lambda self, cr, uid, obj, ctx=None: obj['state'] == 'cancel',
        },
    }

    _columns = {
        'state': fields.selection([('draft', 'Draft'), ('complete', 'Wating Department Manager Recommendation'),
                                   ('confirm', 'Wating General Department Manager Recommendation'),
                                   ('general_dep', 'Waiting HR and Financial Manager Approve'),
                                   ('hr_finance', 'Waiting General Manager Approve'),
                                   ('implement', 'Waiting HR Implementation'),
                                   #('review', 'Waiting General Manager Approve'),
                                   ('approve', 'Approved'),
                                   ('cancel', 'Cancel'),('done', 'Done')],'State', readonly=True),
    }

    def check_degree(self, cr, uid, ids, context={}):
        basic = self.browse(cr,uid,ids,context=context)[0]
        emp_degreee_sq=basic.employee_id.degree_id.sequence
        allow=basic.employee_id.payroll_id.subs_period
        new_sq = basic.degree_id.sequence
        if (emp_degreee_sq + allow ) < new_sq:
	        raise osv.except_osv(_('Error'), _('this degree is not allowed'))
        return True
	
		
    _constraints = [
	       (check_degree, '', []),       
    ]


    def check_general_dep_manager(self, cr, uid, ids, context=None):
        for h in self.browse(cr, uid, ids, context=context):
            user_id = h.employee_id.user_id.id
            flag = self.pool.get('res.users').has_group(cr, user_id, 'base_custom.group_general_department_manager')
            if flag:
                  return True
            else:
                  return False

    def check_unit(self, cr, uid, ids, context=None):
            for h in self.browse(cr, uid, ids, context=context):
                dep = h.employee_id.department_id
                res = []
                if dep.parent_id:
                    cr.execute('SELECT hr_department_cat.category_type as type ' \
                        'FROM hr_department_cat ' \
                        'LEFT JOIN hr_department on (hr_department.cat_id=hr_department_cat.id)' \
                        'WHERE hr_department.id = %s', (dep.parent_id.id,))
                    res = cr.dictfetchall()
                if h.employee_id.department_id.cat_id.category_type == 'unit' or (res and res[0]['type'] == 'unit' and h.state != 'confirm') :
                    return True
                else:
                    return False

    def check_dep_manager(self, cr, uid, ids, context=None):
        for h in self.browse(cr, uid, ids, context=context):
            user_id = h.employee_id.user_id.id
            flag1 = self.pool.get('res.users').has_group(cr, user_id, 'base.group_department_manager')
            #flag2 = self.pool.get('res.users').has_group(cr, user_id, 'base_custom.group_general_department_manager')
            if flag1 :
                  return True
            else:
                  return False
    
    def check_general_manager(self, cr, uid, ids, context=None):
        for h in self.browse(cr, uid, ids, context=context):
            user_id = h.employee_id.user_id.id
            flag = self.pool.get('res.users').has_group(cr, user_id, 'base_custom.group_account_general_manager')
            if flag:
                  return True
            else:
                  return False


    def dep_manager_user(self, cr, uid,ids, vals, context=None):
        cr.execute('SELECT res_users.id as user_id,  hr_department.manager_id as manager_id ' \
            'FROM public.res_users, public.hr_employee, public.resource_resource, public.hr_department ' \
            'WHERE hr_department.manager_id = hr_employee.id '\
            'AND hr_employee.resource_id = resource_resource.id '\
            'AND resource_resource.user_id = res_users.id '\
            'AND hr_department.id = %s', (vals['department_id'],))
        res = cr.dictfetchall()

        return res

    def manager(self, cr, uid, ids, context=None):
        for h in self.browse(cr, uid, ids, context=context):
            dep_cat = h.employee_id.department_id.cat_id
            parent_dep = h.employee_id.department_id.parent_id
            mang_user_id1 = self.dep_manager_user(cr,uid,ids,{'department_id':h.employee_id.department_id.id})

            if h.state == 'complete':
                
                if dep_cat.category_type == 'section':
                    mang_user_id = self.dep_manager_user(cr,uid,ids,{'department_id':h.employee_id.department_id.parent_id.id})
                    if mang_user_id and mang_user_id[0]['user_id'] == uid:
                        return True
                    else:
                        raise osv.except_osv(_('Warning!'),_('You are not this employee department manager'))
                        return False

                elif dep_cat.category_type == 'department' and mang_user_id1[0]['user_id'] == h.employee_id.user_id.id:
                    mang_user_id = self.dep_manager_user(cr,uid,ids,{'department_id':h.employee_id.department_id.parent_id.id})
                    if mang_user_id and mang_user_id[0]['user_id'] == uid:
                        return True
                    else:
                        raise osv.except_osv(_('Warning!'),_('You are not this employee department manager'))
                        return False 
                elif (dep_cat.category_type == 'department' or dep_cat.category_type == 'unit') and mang_user_id1[0]['user_id'] != h.employee_id.user_id.id:
                    if mang_user_id1[0]['user_id'] == uid:
                        return True
                    else:
                        raise osv.except_osv(_('Warning!'),_('You are not this employee department manager'))
                else:
                    if dep_cat.category_type == 'general_dep':
                        if mang_user_id1[0]['user_id'] == uid:
                            return True
                        else:
                            raise osv.except_osv(_('Warning!'),_('You are not this employee general department manager'))
                    return False

            if h.state == 'confirm':
                parent_dep = h.employee_id.department_id.parent_id
                
                if dep_cat.category_type == 'section':
                    mang_user_id = self.dep_manager_user(cr,uid,ids,{'department_id':h.employee_id.department_id.parent_id.parent_id.id})
                    if parent_dep and parent_dep.parent_id and mang_user_id[0]['manager_id'] and mang_user_id[0]['user_id'] == uid:
                        return True
                    else:
                        raise osv.except_osv(_('Warning!'),_('You are not this employee general department manager'))
                        return False

                if dep_cat.category_type == 'department' or dep_cat.category_type == 'unit' :
                    mang_user_id = self.dep_manager_user(cr,uid,ids,{'department_id':h.employee_id.department_id.parent_id.id})
                    if parent_dep and mang_user_id[0]['manager_id'] and mang_user_id[0]['user_id'] == uid:
                        return True
                    else:
                        raise osv.except_osv(_('Warning!'),_('You are not this employee general department manager'))
                        return False

                if dep_cat.category_type == 'general_dep':
                    if mang_user_id1[0]['user_id'] == uid and mang_user_id1[0]['user_id'] != h.employee_id.user_id.id:
                        return True
                    elif mang_user_id1[0]['user_id'] == h.employee_id.user_id.id:
                        mang_user_id = self.dep_manager_user(cr,uid,ids,{'department_id':h.employee_id.department_id.parent_id.id})
                        if parent_dep and mang_user_id[0]['manager_id'] and mang_user_id[0]['user_id'] == uid:
                            return True
                    else:
                        raise osv.except_osv(_('Warning!'),_('You are not this employee general department manager'))
                        return False


        return False

    def write(self, cr, uid, ids, vals, context=None):
        """
        Mehtod that updates holiday name by adding the date to the it 
        useful in the case of changing the holiday after the creation.

        @param vals: Dictionary contains the enterred values
        @return: Super write Mehtod
        """        
        if vals.has_key('end_date'):
            flag1 = self.pool.get('res.users').has_group(cr, uid, 'base.group_hr_user')
            flag2 = self.pool.get('res.users').has_group(cr, uid, 'base_custom.group_general_hr_manager')
            flag = self.pool.get('res.users').has_group(cr, uid, 'base_custom.group_account_general_manager')
            if not flag1 or not flag2 or not flag:
                raise osv.except_osv(_('Warning!'),_('You are not HR employee'))   

        if vals.has_key('state'):
            super(hr_employee_substitution, self).write(cr, uid, ids, vals, context=context)
            result = self.check_manager_email(cr,uid,ids,context=context)
            return True
        else: 
            return super(hr_employee_substitution, self).write(cr, uid, ids, vals, context=context)

    def check_manager_email(self, cr, uid, ids, context=None):
        
        for h in self.browse(cr, uid, ids, context=context):
            dep_cat = h.employee_id.department_id.cat_id
            parent_dep = h.employee_id.department_id.parent_id
            mang_user_id1 = self.dep_manager_user(cr,uid,ids,{'department_id':h.employee_id.department_id.id})
            group = False
            if h.state == 'complete':
                
                if dep_cat.category_type == 'section':
                    mang_user_id = self.dep_manager_user(cr,uid,ids,{'department_id':h.employee_id.department_id.parent_id.id})
                elif dep_cat.category_type == 'department' and mang_user_id1[0]['user_id'] == h.employee_id.user_id.id:
                    mang_user_id = self.dep_manager_user(cr,uid,ids,{'department_id':h.employee_id.department_id.parent_id.id})
                else:
                    mang_user_id = mang_user_id1

                if mang_user_id and mang_user_id[0]['user_id']:
                    send_mail(self, cr, uid, ids[0],group ,u'تصديق إنابة'.encode('utf-8'), 
                        u'هناك سجل إنابة في انتظار توصية مدير الادارة'.encode('utf-8'),[mang_user_id[0]['user_id']], context=context)
                         
            if h.state == 'confirm':
                parent_dep = h.employee_id.department_id.parent_id
                if dep_cat.category_type == 'section':
                    mang_user_id = self.dep_manager_user(cr,uid,ids,{'department_id':h.employee_id.department_id.parent_id.parent_id.id})

                if dep_cat.category_type == 'department' or dep_cat.category_type == 'unit' :
                    mang_user_id = self.dep_manager_user(cr,uid,ids,{'department_id':h.employee_id.department_id.parent_id.id})
                if dep_cat.category_type == 'general_dep':
                    if mang_user_id1[0]['user_id'] != h.employee_id.user_id.id:
                        mang_user_id = mang_user_id1
                    else:
                        mang_user_id = self.dep_manager_user(cr,uid,ids,{'department_id':h.employee_id.department_id.parent_id.id})

                if mang_user_id and mang_user_id[0]['user_id']:
                    send_mail(self, cr, uid, ids[0],group ,u'تصديق إنابة'.encode('utf-8'), 
                        u'هناك سجل إنابة في انتظار توصية مدير الادارة العامة'.encode('utf-8'),[mang_user_id[0]['user_id']], context=context)

            if h.state == 'general_dep' :
                send_mail(self, cr, uid, ids[0], 'base_custom.group_general_hr_manager',u'تصديق إنابة'.encode('utf-8'), 
                                            u'هناك سجل إنابة في انتظار تصديق مدير اﻹدارة العامة للموارد البشرية و المالية'.encode('utf-8'), context=context)
            
            if h.state == 'hr_finance' :
                send_mail(self, cr, uid, ids[0], 'base_custom.group_account_general_manager',u'تصديق إنابة'.encode('utf-8'), 
                                            u'هناك سجل إنابة في انتظار تصديق المدير العام'.encode('utf-8'), context=context)
            if h.state == 'implement' :
                send_mail(self, cr, uid, ids[0], 'base.group_hr_user',u'تنفيذ إنابة'.encode('utf-8'), 
                                            u'هناك سجل إنابة في انتظار تنفيذ الموارد البشرية'.encode('utf-8'), context=context)


        return True



'''class allow_deduct_exception(osv.osv_memory):
    _inherit = "hr.allow.deduct.exception"
    _columns = {
         'factor' :fields.integer("Factor"),
        'special_amount' :fields.float("specialization Amount"),
    }

    _defaults = {
       
        'company_id': lambda s,cr,uid,c: s.pool.get('res.company')._company_default_get(cr, uid, 'hr.allow.deduct.exception', context=c), 
        'factor':1,
        'special_amount' : 0.0,
    
    }


    def onchange_factor(self, cr, uid, ids, amount,factor):
        x = 0.0
        if amount and factor:
            x = amount/factor
        return {'value':{'special_amount':x}}


    def onchange_action_type(self, cr, uid, ids, action, types):
        """
        Method that returns domain contains the criterias of allowances/deduction searching .
        @param action: String of process choice 
        @return: Dictionary 
        """
        domain = {'allow_deduct_id':[('allowance_type','!=','in_cycle'),('name_type','=',types)]}
        if action:
            if action=='special':
                domain['allow_deduct_id'].append(('special', '=', True))
            else:
                domain['allow_deduct_id'].append(('special', '=', False))
                domain['allow_deduct_id'].append(('in_salary_sheet', '=', True))
                
        return {'value': {'allow_deduct_id':False} , 'domain': domain}



    def create_exception(self,cr,uid,ids,context={}):
       """
       Method that adds special allowance/deduction for a group of employees in same dapartment in specific period .
       @return: Dictionary 
       """
       exception_obj = self.pool.get('hr.allowance.deduction.exception')
       for rec in self.browse(cr,uid,ids,context=context):
          for emp in rec.employee_ids:
                exception_obj.create(cr, uid, {
             'code' : emp.emp_code,
                 'employee_id':emp.id,
                 'allow_deduct_id' :rec.allow_deduct_id.id,
                 'start_date' : rec.start_date,
                 'end_date' : rec.end_date,
                 'amount':rec.amount,
                 'factor':rec.amount,
                 'special_amount':rec.amount,
                 'types':rec.allow_deduct_id.name_type,
                 'action':rec.action,
        },context=context)
       return {}'''



class hr_allowance_deduction_exception(osv.osv):

    _inherit = "hr.allowance.deduction.exception"

    def onchange_factor(self, cr, uid, ids, amount,factor):
        x = 0.0
        if amount and factor:
            x = amount/factor
        return {'value':{'special_amount':x}}


    _columns = {
        'factor' :fields.integer("Factor"),
        'special_amount' :fields.float("specialization Amount"),
        }

    _defaults = {
        'factor':1,
        'special_amount' : 0.0,
    }

    def create(self, cr, uid, vals, context=None):
        """
        Method adds new record of exception and recalculates employee's salary.
        @param vals: Dictionary contains entered values
        @return: Id of the created record
        """
        emp_obj = self.pool.get('hr.employee')
        allowance_obj = self.pool.get('hr.allowance.deduction')
        if vals['action'] == 'special':
            amount = vals['amount']
            factor = vals.has_key('factor') and vals['factor'] or 1
            special_amount = amount/factor
            vals['special_amount'] = special_amount
        emp_obj = self.pool.get('hr.employee')
        exception_create = super(hr_allowance_deduction_exception, self).create(cr, uid, vals)
        emp_id = self.read(cr, uid, exception_create, ['employee_id'])
        allow_rec = allowance_obj.browse(cr,uid,vals['allow_deduct_id'])
        if allow_rec.name_type == 'deduct' and allow_rec.deduction_from == 'salary' or allow_rec.name_type == 'allow':
            emp_obj.write_employee_salary(cr, uid, [emp_id['employee_id'][0]], [])
        return exception_create

    def write(self, cr, uid, ids, vals, context=None):
        """
        Method updates a record of exception and recalculates employee's salary.
        @param vals: Dictionary contains entered values
        @return: Boolean True
        """
        emp_obj = self.pool.get('hr.employee')
        allowance_obj = self.pool.get('hr.allowance.deduction')

        rec = self.browse(cr,uid,ids[0])
        amount = vals.has_key('amount') and vals['amount'] or rec.amount
        factor = vals.has_key('factor') and vals['factor'] or rec.factor
        special_amount = amount/factor
        vals['special_amount'] = special_amount
        exception_write = super(hr_allowance_deduction_exception, self).write(cr, uid, ids, vals)
        emp_id = self.read(cr, uid, ids[0], ['employee_id'])
        if rec.allow_deduct_id.name_type == 'deduct' and rec.allow_deduct_id.deduction_from == 'salary' or rec.allow_deduct_id.name_type == 'allow':
            emp_obj.write_employee_salary(cr, uid, [emp_id['employee_id'][0]], [])
        return exception_write

    def unlink(self, cr, uid, ids, context=None):
        """
        Method deletes a record of exception and recalculates employee's salary.
        @param vals: Dictionary contains entered values
        @return: Id of the deleted record
        """
        emp_obj = self.pool.get('hr.employee')
        emp_id = self.read(cr, uid, ids[0], ['employee_id'])
        rec = self.browse(cr,uid,ids[0])
        exception_unlink = super(hr_allowance_deduction_exception, self).unlink(cr, uid, ids)
        #if rec.allow_deduct_id.deduction_from == 'salary':
        emp_obj.write_employee_salary(cr, uid, [emp_id['employee_id'][0]], [])
        return exception_unlink


    def onchange_action_type(self, cr, uid, ids, action, types):
        """
        Method that returns domain contains the criterias of allowances/deduction searching .
        @param action: String of process choice 
        @return: Dictionary 
        """
        domain = {'allow_deduct_id':[('allowance_type','!=','in_cycle'),('name_type','=',types)]}
        if action:
            if action=='special':
                domain['allow_deduct_id'].append(('special', '=', True))
            else:
                domain['allow_deduct_id'].append(('special', '=', False))
                #domain['allow_deduct_id'].append(('in_salary_sheet', '=', True))
                
        return {'value': {'allow_deduct_id':False} , 'domain': domain}


class payroll(osv.osv):

    _inherit = "payroll"


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
        imprint = 0.0
        special_ids = allow_deduct_exception_obj.search(cr, uid, ['|', ('end_date', '>', emp_dict['date']), 
                         ('end_date', '=', False),('allow_deduct_id', '=', emp_dict['allow_deduct'].allow_deduct_id.id), 
                         ('employee_id', '=', emp_dict['emp_id']),('start_date', '<=', emp_dict['date']), ('action', '=', 'special')])
        if special_ids and not emp_dict['no_sp_rec']:
            for special in allow_deduct_exception_obj.browse(cr, uid, special_ids):
                if special.allow_deduct_id:
                    if special.amount:
                        # If there is amount then take the amount directly 
                        amount += (special.amount)/(special.factor)
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
            imprint = allow_deduct_dict['imprint']
            emp_dict.update({'special':False, })
        return {'amount':amount, 'tax':tax_amount, 'imprint':imprint}


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
                if emp_ids and not (allow_deduct_rec.name_type == 'deduct' and allow_deduct_rec.deduction_from == 'addendum'):
                    for emp in employee_obj.browse(cr, uid, emp_ids):
                        allow_deduct_dict = self.allowances_deductions_calculation(cr, uid, date, emp, {}, [allow_deduct_rec.id])
                        self.write_allow_deduct(cr, uid, emp.id, allow_deduct_dict['result'],emp_obj)
                if com_allow_deduct:
                    self.change_allow_deduct(cr, uid, com_allow_deduct, [])
        return True

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
                   record.allow_deduct_id.pay_sheet == 'first' or sub_setting['sub_setting'] == 'first_and_second')) and \
                   record.allow_deduct_id.name_type == 'allow' and record.allow_deduct_id.allowance_type != 'mile_allowance') or not substitution:
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
        emp_obj = self.pool.get('hr.employee')
        emp_rec = emp_obj.browse(cr,uid,emp_dict['emp_id'])
        amount = tax_amount = imprint = 0.0
        holiday_amount = 0.0
        remain_amount = 0.0
        exempted = emp_dict['allow_deduct'].allow_deduct_id.exempted_amount
        check = False
        allow_deduct= emp_dict['allow_deduct'].allow_deduct_id
        # check if allowance or deduction is special and special flag is false then call special function
        if allow_deduct.special and (allow_deduct.name_type == 'deduct' or (allow_deduct.name_type == 'allow' and allow_deduct.allowance_type != 'mile_allowance')) and not emp_dict['special']:
            special_dict = self.allowances_deductions_sp_calculation(cr, uid, emp_dict, allow_list)
            amount += special_dict['amount']
            tax_amount += special_dict['tax']
            imprint += special_dict['imprint']
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
                            jobs = [job.id for job in allow_deduct.job_ids]
                            if not jobs or emp_dict['job_id'] in jobs:
                                categs = allow_deduct.category_ids
                                if not categs or (categs and emp_dict['category'] and [g.id for g in emp_dict['category'] if g in categs]):
                                    check = True

                if check and not (allow_deduct.name_type == 'allow' and allow_deduct.allowance_type == 'mile_allowance' and emp_rec.mile_allowance == False):
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
                            if emp_rec.marital != 'single':
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
                        ################attendance#################
                        # Linked attendance
                        if allow_deduct.related_attendance:
                            attendance_line_obj = self.pool.get('suggested.attendance.line')
                            attendance_ids = attendance_line_obj.search(cr, uid, [('state', '=', 'done'), ('flage', '=', False),('emp_id','=', emp_dict['emp_id'])],context={})
                            
                            att_percent = attendance_line_obj.read(cr, uid, attendance_ids,['added_percent'], context={})

                            num_attend = 0.0
                            if att_percent:
                                try:
                                    num_attend = att_percent[0]['added_percent']
                                    num_attend = round(num_attend,0)
                                except:
                                    pass

                            amount = amount * num_attend/100.0

                    # Linked Absence
                    if allow_deduct.linked_absence:
                        holiday_amount , remain_amount = self.allowances_linked_absence_calculation(cr, uid, emp_dict,amount)
                        amount -= holiday_amount
                        #amount =  holiday_amount
                    if allow_deduct.distributed:
                        amount = amount / allow_deduct.distributed
                        if holiday_amount :
                            holiday_amount = holiday_amount / allow_deduct.distributed
                    # compute allowance/deduction amount based on marital status and number of children
                    if allow_deduct.related_marital_status:
                        family_relation=self.family_relation_calculation(cr, uid, emp_dict['emp_id'], emp_dict['date'])
                        married=False
                        if emp_dict['marital_status'] != 'single': married=True
                        children=family_relation['child_no']
                        degree_id = family_relation['degree_id']
                        if children > 2: children=2
                        status_ids2 = marital_status_obj.search(cr, uid, [
                                        ('allow_deduct_id', '=', allow_deduct.id),
                                        ('married', '=', married),('children_no', '=', children), ('degree_id','=',False)])
                        status_ids1 = marital_status_obj.search(cr, uid, [
                                        ('allow_deduct_id', '=', allow_deduct.id),
                                        ('married', '=', married),('children_no', '=', children),('degree_id','=',degree_id)])
                        status_ids = status_ids1 and status_ids1 or status_ids2
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
                            '''if holiday_amount :
                                tax_amount = ((holiday_amount-exempted) * allow_deduct.bonus_percent) / 100
                            else:
                                tax_amount = ((amount-exempted) * allow_deduct.bonus_percent) / 100'''
                            tax_amount = ((amount-exempted) * allow_deduct.bonus_percent) / 100
                    if allow_deduct.stamp:
                        imprint = allow_deduct.stamp
                    

        return {'amount':amount, 'tax':tax_amount ,'holiday_amount':holiday_amount , 'remain_amount' : remain_amount,'imprint': imprint}


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
        emp_obj = self.pool.get('hr.employee')
        employee_substitution_obj = self.pool.get('hr.employee.substitution')
        family = family_pool.read_group(cr, uid, [
                 ('employee_id', '=', emp_id), ('start_date', '<=', date),
                 ('state', '=', 'approved')
        ], ['relation_id'], ['relation_id'])

        emp_deg = emp_obj.browse(cr,uid,emp_id).degree_id.id

        substitue_ids = employee_substitution_obj.search(cr, uid, ['|', ('end_date', '>=', date), ('end_date', '=', False), 
                            ('employee_id', '=', emp_id), ('start_date', '<=', date)])
        if substitue_ids:
                for sub_record in employee_substitution_obj.browse(cr, uid, substitue_ids):
                    emp_deg = sub_record.degree_id.id


        for m in family:
            relation=relation_pool.browse(cr, uid,[m['relation_id'][0]] )[0]
            if m['relation_id_count'] > relation.max_number:
                m['relation_id_count']= relation.max_number 
            if relation.children:
                child_no +=  m['relation_id_count']
            rel_amount += m['relation_id_count']*relation.amount
        return {'rel_amount':rel_amount, 'child_no':child_no, 'degree_id':emp_deg}

class salary_scale_allow_deduct(osv.osv_memory):

    _inherit= "salary.scale.allow.deduct"

    _defaults = {
        'payroll_id': 5
    }


class employees_salary_report(osv.osv_memory):
    _inherit = "employees.salary.report"


    def _curr_user(self, cr, uid, context=None):
        result = False
        user_obj = self.pool.get('res.users')
        emp_obj = self.pool.get('hr.employee')
        if user_obj.has_group(cr,uid,'base.group_hr_user') or user_obj.has_group(cr,uid,'purchase_ntc.group_internal_auditor'):
                result = True
        
        return result

    def _curr_user_id(self, cr, uid, context=None):
        result = False
        user_obj = self.pool.get('res.users')
        emp_obj = self.pool.get('hr.employee')
        if context.has_key('employee_id'):
            emp_rec = emp_obj.browse(cr, uid, context['employee_id'], context=context)
            if emp_rec.user_id.id == uid:
                result = True
        
        
        return result

    _columns = {
        'curr_uid': fields.boolean(string='current_user', store=False),
        'curr_uid_hr': fields.boolean(string='hr user', store=False),
        }

    _defaults = {
        'year': int(time.strftime('%Y')),
        'month': int(time.strftime('%m')),
        'curr_uid_hr' : _curr_user,
        'curr_uid' : _curr_user_id,
        }


#----------------------------------------
# allowance marital status
#----------------------------------------
class hr_allow_marital_status(osv.osv):

    _inherit = "hr.allow.marital.status"


    _columns = {
        'degree_id' : fields.many2one('hr.salary.degree', 'Degree'),
     }
    

#----------------------------------------
# Degree category
#----------------------------------------
class hr_degree_category(osv.osv):

    _inherit = "hr.degree.category"

    _columns = {
        'name' : fields.char("Name", size=64, required=True),
        'code': fields.char('Code', size=64),
        'account_id': fields.property('account.account', type='many2one', relation='account.account', string='Account', view_load=True
                            , domain="[('user_type.report_type','=','expense'),('type','!=','view')]"),
        'worker' : fields.boolean('Classification of the degree of labor'),
    }

    _defaults = {
        'worker': False,
        
        }


class hr_additional_allowance(osv.osv):

    _inherit ='hr.additional.allowance'

    _columns = {
        'user_id': fields.many2one('res.users', "Manager user"),
        'url':fields.char('URL',size=156, readonly=True,),
        
    }

    _track = {
        'state': {
            'hr_ntc_custom.mt_additional_draft': lambda self, cr, uid, obj, ctx=None: obj['state'] == 'draft',
            'hr_ntc_custom.mt_additional_confirm': lambda self, cr, uid, obj, ctx=None: obj['state'] == 'confirm',
            'hr_ntc_custom.mt_additional_validate': lambda self, cr, uid, obj, ctx=None: obj['state'] == 'validate',
            'hr_ntc_custom.mt_additional_second_validate': lambda self, cr, uid, obj, ctx=None: obj['state'] == 'second_validate',
            'hr_ntc_custom.mt_additional_approved': lambda self, cr, uid, obj, ctx=None: obj['state'] == 'approved',
            'hr_ntc_custom.mt_additional_cancel': lambda self, cr, uid, obj, ctx=None: obj['state'] == 'cancel',
        },
    }


    def write(self, cr, uid, ids, vals, context=None):
        """
        Mehtod that updates holiday name by adding the date to the it 
        useful in the case of changing the holiday after the creation.

        @param vals: Dictionary contains the enterred values
        @return: Super write Mehtod
        """        
        if vals.has_key('state') :
            super(hr_additional_allowance, self).write(cr, uid, ids, vals, context=context)
            result = self.check_manager_email(cr,uid,ids,context)
            return True
        else: 
            return super(hr_additional_allowance, self).write(cr, uid, ids, vals, context=context)

    def check_manager_email(self, cr, uid, ids, context=None):
        """
            Send Notification
        """
        for h in self.browse(cr, uid, ids, context=context):
            if h.state == 'confirm' :
                send_mail(self, cr, uid, ids[0], 'base.group_hr_user',u'تصديق الاجر الاضافي'.encode('utf-8'), u'هناك سجل اجر إضافي في انتظار تصديق الموارد البشرية'.encode('utf-8'), context=context)
            if h.state == 'validate' :
                send_mail(self, cr, uid, ids[0], 'purchase_ntc.group_internal_auditor',u'تصديق الاجر الاضافي'.encode('utf-8'), u'هناك سجل اجر إضافي في انتظار تصديق المراجع'.encode('utf-8'), context=context)
            if h.state == 'second_validate' :
                send_mail(self, cr, uid, ids[0], 'base.group_hr_manager',u'تصديق الاجر الاضافي'.encode('utf-8'), u'هناك سجل اجر إضافي في انتظار تصديق و ترحيل مدير الموارد البشرية'.encode('utf-8'), context=context)
            
        return True


class hr_salary_bonuses(osv.osv):

    _inherit = "hr.salary.bonuses"
    _columns = {
        'active' : fields.boolean('Active'),
        
    }

    _defaults = {
            'active' : 1,
              } 