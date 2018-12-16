# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################
import time
import datetime
import netsvc
from openerp.osv import fields, osv, orm
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp
import mx
from dateutil.relativedelta import relativedelta
#----------------------------------------
#Salary Scale
#----------------------------------------
class hr_salary_scale(osv.osv):

    def create(self, cr, uid,vals, context=None):
        new_id = super(hr_salary_scale, self).create(cr, uid, vals, context=context)
        for rec in self.browse(cr,uid,new_id).degree_ids:
            if rec.max_raise > 0 :
                call_load_bouns = self.pool.get("hr.salary.degree").load_bouns(cr,uid,[rec.id],context=None)
        return new_id

    _name = "hr.salary.scale"
    _description = "Salary scale"
    _columns = {
        'name' : fields.char("Name", size=64, required=True),
        'start_date' :fields.date("Start Date", required=True),
        'end_date' :fields.date("End Date"),
        'degree_ids': fields.one2many('hr.salary.degree', 'payroll_id', 'Degrees'),
        'code': fields.char('Code', size=64),
        'sub_salary':fields.selection([('ignore', 'Ignore Substitution'), ('diff', 'Compute Difference Between The 2 Degree '),
                              ('sustitut_degree', 'Compute Allowances of Sustitution Degree ')], 'Substitution in Payroll', required=True),
        'sub_bonus':fields.selection([('ignore', 'Ignore Substitution'), ('diff', 'Compute Difference Between The 2 Degree '),
                               ('sustitut_degree', 'Compute Allowances of Sustitution Degree ')], 'Substitution in Bonuses', required=True),
        'account_id': fields.property('account.account', type='many2one', relation='account.account', string='Account', view_load=True
                            ,domain="[('user_type.report_type','=','expense'),('type','!=','view')]"),

        'sub_setting' :fields.selection([('first', 'First sheet only'), ('first_and_second', 'First and second sheet ') ], 'Allowances'),

        'sub_prcnt_selection' :fields.selection([('percentge', 'Percentage only'),
                                                 ('bigest', 'Compare and choose the bigest'),
                                                 ('smalest','Compare and choose the smalest') ], 'Percentage Selection'),
        'sub_percentage': fields.float('Percentage', size=64),
        
        'employee_type': fields.selection([('employee', 'Employee'), ('trainee', 'Trainee'),
                                                ('contractor', 'Contractor'), ('recruit', 'Recruit')], 'Employee Type', required=True),
    }
    _defaults = {
        'sub_salary': 'ignore',
        'sub_bonus' : 'ignore',
    }

    def check_sub_percentage(self, cr, uid, ids, context={}):
        """Method that checks if the enterd persentage is less than zero it raise .
           @return: Boolean True or False
        """
        for rec in self.browse(cr, uid, ids):
            if rec.sub_prcnt_selection and rec.sub_prcnt_selection in ('percentge','bigest','smalest' ) and rec.sub_percentage <= 0:
                return False
        return True

    _constraints = [
       (check_sub_percentage, 'ERROR , Sorry the percentage must be greater than zero.', ['sub_percentage']),       
    ]

    _sql_constraints = [

       ('code_uniqe', 'unique (code)', 'you can not create same code !'),
       ('name_uniqe', 'unique (name)', 'Salary Scale name is already exist !'),
    ]


    def unlink(self, cr, uid, ids, context=None):
        for rec in self.browse(cr, uid, ids, context=context):
            check_employee = self.pool.get('hr.employee').search(cr,uid,[('payroll_id','=',rec.id)])
            check_main_arch = self.pool.get('hr.payroll.main.archive').search(cr,uid,[('scale_id','=',rec.id)])
            check_employee_sub = self.pool.get('hr.employee.substitution').search(cr,uid,[('payroll_id','=',rec.id)])
            if check_main_arch or check_employee or check_employee_sub:
                raise osv.except_osv(_('Warning!'),_('You cannot delete this salary scale which is refrence .'))
        return super(hr_salary_scale, self).unlink(cr, uid, ids, context)

    def copy(self, cr, uid, id, default=None, context=None):
        default = {} if default is None else default.copy()
        salary_scale = self.browse(cr, uid, id, context=context)
        default.update({'name':salary_scale.name+"(copy)"})
        return super(hr_salary_scale, self).copy(cr, uid, id, default, context=context)
 
    def write(self, cr, uid, ids, vals, context=None):
       """Method that overwrites write method and detects changes in the configuration of salary scale
          and calls  change_allow_deduct function to recalculate allowances and deductions amount if change in substitution congfiguration.
          @param vals: Dictionary contains the entered values
          @return: Boolean True
       """
       write_allow_deduct = super(hr_salary_scale, self).write(cr, uid, ids, vals, context)
       for rec in self.browse(cr,uid,ids):
            for line in rec.degree_ids :
                if line.max_raise > 0 :
                    call_load_bouns = self.pool.get("hr.salary.degree").load_bouns(cr,uid,[line.id],context=None)
       update_field = [key for key in vals.keys() if key  in ('sub_prcnt_selection', 'sub_percentage')]
       if update_field:
           sub_ids=self.pool.get('hr.allowance.deduction').search(cr,uid,[('allowance_type','=','substitution')])
           if sub_ids:
               update = self.pool.get('payroll').change_allow_deduct(cr, uid, sub_ids, ids)
       return write_allow_deduct
#----------------------------------------
# Degree category
#----------------------------------------
class hr_degree_category(osv.osv):
    _name = "hr.degree.category"
    _description = "Category Of Degree"
    _columns = {
        'name' : fields.char("Name", size=64, required=True),
        'code': fields.char('Code', size=64),
    }
    _sql_constraints = [

       ('code_uniqe', 'unique (code)', 'you can not create same code !'),
       ('name_uniqe', 'unique (name)', 'Degree Category name is already exist !'),
    ]

    def copy(self, cr, uid, id, default=None, context=None):
        default = {} if default is None else default.copy()
        degree_category = self.browse(cr, uid, id, context=context)
        default.update({'name':degree_category.name+"(copy)"})
        return super(hr_degree_category, self).copy(cr, uid, id, default, context=context)

#----------------------------------------
# Salary Degree
#----------------------------------------
class hr_salary_degree(osv.osv):
    _name = "hr.salary.degree"
    _description = "Salary scale Degree"
    _order='sequence'
    _columns = {
        'name' : fields.char("Name", size=64, required=True),
        'sequence': fields.integer('Sequence'),
        'payroll_id' : fields.many2one('hr.salary.scale', 'Salary', required=True , ondelete="cascade"),
        'basis' :fields.float("Basis", digits_compute=dp.get_precision('Payroll') , required=True),
        'max_raise' :fields.integer("Max Bonus" , required=True),
        'raise_type': fields.selection([ ('amount', 'Fixed Amount'), ('percentage', 'Percentage from basis'),
                                         ('complex', 'Complex percentage from basis') ] , 'Raise Type'),
        'raise_amount' :fields.float("Bonus Amount", digits_compute=dp.get_precision('Payroll') , required=True),
        'taxable' : fields.boolean('Taxable'),
        'exempted_amount' :fields.float("Exempted Amount", digits_compute=dp.get_precision('Payroll')),
        'notes' :fields.text("Description", size=254),
        'code': fields.char('Code', size=64),
        'category_id' : fields.many2one('hr.degree.category', 'Category' , ondelete="restrict"),
        'active' : fields.boolean('Active'),
        'bonus_ids': fields.one2many('hr.salary.bonuses', 'degree_id', 'Bonuses'),
        'allow_deduct_ids': fields.one2many('hr.salary.allowance.deduction', 'degree_id', 'Allowances/Deductions'),
    }

    _defaults = {
        'active' : 1,
        'raise_type' : 'amount',
    }
    _sql_constraints = [

       ('degree_uniqe', 'unique(payroll_id,name)', 'you can not duplicate the degree !'),
       ('sequence_uniqe', 'unique(payroll_id,sequence)', 'you can not duplicate the sequence !'),
    ]

    def change_fields(self, cr, uid, ids,basis,sequence,max_raise,context=None):
        """
        On change_basis or seq or max raise to update bouns lines.

        @param basis : basis 
        @return: Dictionary of bouns lines or Empty dictionary 
        """
        for rec in self.browse(cr, uid, ids, context=context):
            if basis or sequence : 
                if basis != rec.basis :
                   write_basis = self.write(cr,uid,rec.id,{'basis':basis},context=context)
                if sequence != rec.sequence :
                   write_basis = self.write(cr,uid,rec.id,{'sequence':sequence},context=context)
                for degrees in rec.payroll_id.degree_ids:
                    self.load_bouns(cr, uid, [degrees.id],context=None)
            if max_raise :                
                if max_raise != rec.max_raise :
                   write_basis = self.write(cr,uid,rec.id,{'max_raise':max_raise},context=context)
        return {}

    def load_bouns(self, cr, uid, ids,context=None):
        """
        On change max raise to create bouns lines.

        @param max_raise : max raise 
        @return: Dictionary of bouns lines or Empty dictionary 
        """
        salary_bouns_obj = self.pool.get('hr.salary.bonuses')
        salary_bouns_lines_obj = self.pool.get('hr.salary.bonuses.lines')
        rate = 0
        bouns_amount = 0 
        higher_degree_basis = 0
        current_degree = 0 
        higher_degree_seq = 0 
        back_seq = 1 
        for rec in self.browse(cr, uid, ids, context=context):
            max_raise = rec.max_raise
            old_max_raise = len(rec.bonus_ids)
            higher_degree_seq = (rec.sequence-1)
            if max_raise and max_raise > 0 : # why >= 0
                if max_raise < old_max_raise :
                    raise osv.except_osv(_('Warning!'),_('You cannot modify this degree because new max bonus is less than old max bouns...please contact Hr Adminstrator .'))
                bonus_line_seq = 0 
                seq = 0
                res_basis = [] 
                while not res_basis and higher_degree_seq > 0 : 
                    cr.execute("""select d.basis as basis from hr_salary_degree d 
                                  where d.sequence =%s and d.payroll_id = %s """,(higher_degree_seq,rec.payroll_id.id))
                    res_basis = cr.fetchone()
                    higher_degree_seq -=1
                if res_basis : 
                    higher_degree_basis = res_basis[0] 
                current_degree = rec.basis
                if higher_degree_basis == 0.0 : 
                   bouns_amount = current_degree
                if max_raise > 0 : # y need for check
                    bonus_line_seq =  old_max_raise
                    seq = bonus_line_seq
                    write_max_raise = self.write(cr,uid,rec.id,{'max_raise':max_raise},context=context)
                rate = (higher_degree_basis - current_degree)/ max_raise 
                while bonus_line_seq < max_raise: 
                    if bonus_line_seq==0: 
                        bouns_amount = current_degree + rate
                    elif bonus_line_seq > 0 : 
                        #add the max date in the querey
                        cr.execute("""select l.amount as pervious_bouns from hr_salary_bonuses b 
                                       left join hr_salary_bonuses_lines l on (b.id = l.hr_salary_bonuses_id)
                                       where b.sequence =%s and b.degree_id =%s and b.payroll_id = %s""",(seq,rec.id,rec.payroll_id.id))
                        res_amount = cr.fetchone()
                        bouns_amount = res_amount[0] + rate 
                    salary_bouns_id = salary_bouns_obj.create(cr, uid, {
                            'name':bonus_line_seq+1,
                            'payroll_id':rec.payroll_id.id, 
                            'degree_id':rec.id, 
                            'margin_time':365, 
                            'sequence':bonus_line_seq+1,
                            'old_basic_salary':0.0, 
                                    })
                    salary_bouns_lines_id = salary_bouns_lines_obj.create(cr, uid, {
                            'date':time.strftime('%Y-%m-%d'),
                            'amount':bouns_amount, 
                            'hr_salary_bonuses_id':salary_bouns_id, 
                                    })
                    bonus_line_seq+=1
                    seq+=1
                if old_max_raise :
                   rate = (higher_degree_basis - current_degree)/ max_raise #use d previous rate 
                   while back_seq <= max_raise :
                            bouns_seq = back_seq
                        #d query can be a function n jst call
                            cr.execute("""select l.id as id from hr_salary_bonuses b 
                                       left join hr_salary_bonuses_lines l on (b.id = l.hr_salary_bonuses_id)
                                       where b.sequence =%s and b.degree_id =%s and b.payroll_id = %s""",(back_seq,rec.id,rec.payroll_id.id))
                            res_id = cr.fetchone()
                            if res_id : 
                                if back_seq==1:
                                    if rate < 0 : 
                                        bouns_amount = current_degree
                                    else : 
                                        bouns_amount = current_degree + rate
                                    salary_bouns_lines_obj.write(cr, uid, res_id[0], {'amount':bouns_amount}, context)
                                elif back_seq > 1 :
                                    pervious = 0
                                    res_update = []
                                    while not res_update and bouns_seq > 0 :
                                        cr.execute("""select l.amount as pervious_bouns from hr_salary_bonuses b 
                                            left join hr_salary_bonuses_lines l on (b.id = l.hr_salary_bonuses_id)
                                            where b.sequence =%s and b.degree_id =%s and b.payroll_id = %s""",(bouns_seq-1,rec.id,rec.payroll_id.id))
                                        res_update = cr.fetchone()
                                        if res_update :
                                            pervious = res_update[0]
                                            bouns_amount = pervious + rate
                                salary_bouns_lines_obj.write(cr, uid, res_id[0], {'amount':bouns_amount}, context)
                            back_seq +=1 
        return {}

    def unlink(self, cr, uid, ids, context=None):
        for rec in self.browse(cr, uid, ids, context=context):
            check_employee = self.pool.get('hr.employee').search(cr,uid,[('degree_id','=',rec.id)])
            check_main_arch = self.pool.get('hr.payroll.main.archive').search(cr,uid,[('degree_id','=',rec.id)])
            check_employee_sub = self.pool.get('hr.employee.substitution').search(cr,uid,[('degree_id','=',rec.id)])
            scale = self.pool.get('hr.salary.scale').search(cr,uid,[('id','=',rec.payroll_id.id)])
            scale_ids = self.pool.get('hr.salary.scale').browse(cr,uid,scale[0])
            check_employee_process = self.pool.get('hr.process.archive').search(cr,uid,[('reference','=','hr.salary.degree,'+str(rec.id))])
            if check_main_arch or check_employee or check_employee_sub or check_employee_process:
                raise osv.except_osv(_('Warning!'),_('You cannot delete this salary degree which is refrence .'))
            delete_id = super(hr_salary_degree, self).unlink(cr, uid, ids, context)
            for degree in scale_ids.degree_ids :
                call_load_bouns = self.load_bouns(cr,uid,[degree.id],context=None)
        return delete_id

    def copy(self, cr, uid, id, default=None, context=None):
        default = {} if default is None else default.copy()
        salary_degree = self.browse(cr, uid, id, context=context)
        cr.execute("select max(sequence) from hr_salary_degree d where d.payroll_id =%s" , (salary_degree.payroll_id.id,))
        res = cr.fetchone()
        default.update({'name':salary_degree.name+"(copy)",
                        'bonus_ids':False,
                        'allow_deduct_ids':False,
                        'sequence': res[0]+1})  
        return super(hr_salary_degree, self).copy(cr, uid, id, default, context=context)

    def create(self, cr, uid,vals, context=None):
        vals.update({'bonus_ids':False,'allow_deduct_ids':False})
        degree_id= super(hr_salary_degree, self).create(cr, uid, vals, context=context)
        for rec in self.browse(cr,uid,[degree_id]):
            if rec.max_raise > 0 :
                call_load_bouns = self.load_bouns(cr,uid,[rec.id],context=None)
            scale = self.pool.get('hr.salary.scale').search(cr,uid,[('id','=',rec.payroll_id.id)])
            scale_ids = self.pool.get('hr.salary.scale').browse(cr,uid,scale[0])
            for degree in scale_ids.degree_ids :
                call_load_bouns = self.load_bouns(cr,uid,[degree.id],context=None)
        return degree_id


#----------------------------------------
#Salary Bonuses
#----------------------------------------
class hr_salary_bonuses(osv.osv):
    _name = "hr.salary.bonuses"
    _description = "Salary scale Degree Bonus"
    _order='sequence'

    def name_get(self, cr, uid, ids, context=None):
       return [(r.id, (r.degree_id.name and r.degree_id.name+'-' or '') + (r.name and r.name+' ' or '') + (r.basic_salary and  '('+ str(r.basic_salary)+') ' or '')) for r in self.browse(cr, uid, ids, context=context)if r.id!=0]


    def _get_bonus_line(self, cr, uid, ids, context=None):
        """
	Method that returns the ID of job approval updated to update the 
	functional field in the job consequently.

        @return: List of the ids of the approved job
        """
        res = []
        for rec in self.pool.get('hr.salary.bonuses.lines').browse(cr, uid, ids, context=context):
             res.append(rec.id)
        return res

    _columns = {
        'name' :fields.char("Name", size=64 , required=True),
        'payroll_id' : fields.many2one('hr.salary.scale', 'Salary', required=True, ondelete="cascade"),
        'degree_id' : fields.many2one('hr.salary.degree', 'Degree', required=True , domain="[('payroll_id','=',payroll_id)]", ondelete="cascade"),
        'basic_salary' :  fields.float(string='Basic Salary' , required=True),
        'old_basic_salary' :fields.float("Old Basic Salary", digits_compute=dp.get_precision('Payroll') , required=True),
        'code': fields.char('Code', size=64),
        'margin_time': fields.integer('Margin time', required=True),
        'sequence': fields.integer('Sequence'),
        'bonuses_lines_ids': fields.one2many('hr.salary.bonuses.lines', 'hr_salary_bonuses_id', 'Rates'),
    }

    def unlink(self, cr, uid, ids, context=None):
        new_max_raise = 0.0
        for rec in self.browse(cr, uid, ids, context=context):
            check_employee = self.pool.get('hr.employee').search(cr,uid,[('bonus_id','=',rec.id)])
            check_main_arch = self.pool.get('hr.payroll.main.archive').search(cr,uid,[('bonus_id','=',rec.id)])
            check_employee_sub = self.pool.get('hr.employee.substitution').search(cr,uid,[('bonus_id','=',rec.id)])
            check_employee_process = self.pool.get('hr.process.archive').search(cr,uid,[('reference','=','hr.salary.bonuses,'+str(rec.id))])
            if check_main_arch or check_employee or check_employee_sub or check_employee_process:
                raise osv.except_osv(_('Warning!'),_('You cannot delete this salary bonus which is refrence .'))
            degrees = self.pool.get('hr.salary.degree').search(cr,uid,[('id','=',rec.degree_id.id)])
            degree_ids = self.pool.get('hr.salary.degree').browse(cr,uid,degrees[0])
            delete_id = super(hr_salary_bonuses, self).unlink(cr, uid, ids, context)
            new_max_raise = (degree_ids.max_raise-1)
            max_raise = self.pool.get('hr.salary.degree').write(cr,uid,degree_ids.id,{'max_raise':new_max_raise},context=context)
            call_load_bouns = self.pool.get('hr.salary.degree').load_bouns(cr,uid,[degree_ids.id],context=None)
        return delete_id

    def check_max_bonus(self, cr, uid, ids, context={}):
        """Method that checks if the enterd bonuses exceed the defind maximum bonuses for the degree or not.
           @return: Boolean True or False
        """
        for bonus in self.browse(cr, uid, ids):
            bonus_ids = self.search(cr, uid, [(('degree_id', '=', bonus.degree_id.id))])
            if bonus.degree_id.max_raise and len(bonus_ids) > bonus.degree_id.max_raise:
                    return False
        return True

    _constraints = [
        (check_max_bonus, 'ERROR , sorry you can not exceed the Max Number of bonuses for this degree.', ['degree_id']),
    ]
    _sql_constraints = [

       ('code_uniqe', 'unique (code)', 'you can not create same code !'),
       ('sequence_uniqe', 'unique(degree_id,sequence)', 'you can not duplicate the sequence !'),
       ('name_uniqe', 'unique (name,degree_id)', 'Bonus name is already exist for selected degree !'),
       ('salary_check', "CHECK ( basic_salary >= 0 and old_basic_salary >= 0)", "The basic salary must be greater than or equal 0."),
       ('margin_check', "CHECK ( margin_time >= 0)", "The margin time must be greater than or equal 0."),
    ]

    def copy(self, cr, uid, id, default=None, context=None):
        default = {} if default is None else default.copy()
        salary_bonus = self.browse(cr, uid, id, context=context)
        cr.execute("select max(sequence) from hr_salary_bonuses b where b.payroll_id =%s and b.degree_id =%s" , (salary_bonus.payroll_id.id , salary_bonus.degree_id.id,))
        res = cr.fetchone()
        default.update({'name':salary_bonus.name+"(copy)" , 'code':False , 'sequence':res[0]+1})
        return super(hr_salary_bonuses, self).copy(cr, uid, id, default, context=context)


#----------------------------------------
# Salary Bonuses Lines 
#---------------------------------------- 
class hr_salary_bonuses_lines(osv.osv):
    _name = "hr.salary.bonuses.lines"


    _columns = {
        'date': fields.date('Date', required=True, select=True),
        'amount': fields.float('amount', digits=(12,6), help='The rate of the currency to the currency of rate 1'),
        'hr_salary_bonuses_id': fields.many2one('hr.salary.bonuses', 'Bonuses', readonly=True),
        
    }
    _defaults = {
        'date': lambda *a: time.strftime('%Y-%m-%d'),
    }
    _order = "date desc"

#----------------------------------------
# Salary Bonuses Lines 
#---------------------------------------- 
class hr_salary_bonuses_lines(osv.osv):
    _name = "hr.salary.bonuses.lines"


    _columns = {
        'date': fields.date('Date', required=True, select=True),
        'amount': fields.float('amount', digits=(12,6), help='The rate of the currency to the currency of rate 1'),
        'hr_salary_bonuses_id': fields.many2one('hr.salary.bonuses', 'Bonuses', readonly=True),
        
    }
    _defaults = {
        'date': lambda *a: time.strftime('%Y-%m-%d'),
    }
    _order = "date desc"


#----------------------------------------
# allow_deduction job amount 
#----------------------------------------
'''
Calculate Allowance/Deduction amount by job
'''
class hr_allowance_job(osv.osv):
    _name = "hr.allowance.job"
    _columns = {
        'job_id' : fields.many2one('hr.job' , string='Job') ,
        'value' : fields.float('Percent') ,  
        'allow_deduct_id' : fields.many2one('hr.allowance.deduction' , string='Allowance/Deduction'),
    }



#----------------------------------------
# allow_deduction gender amount 
#----------------------------------------
'''
Calculate Allowance/Deduction amount by gender
'''
class hr_allowance_gender(osv.osv):
    _name = "hr.allowance.gender"
    _columns = {
        'gender' : fields.selection([('male','Male') ,('female','Female') ] , string='Gender', required=True) ,
        'value' : fields.float('percent' , required=True) ,  
        'allow_deduct_id' : fields.many2one('hr.allowance.deduction' , string='Allowance/Deduction'),
    }


#----------------------------------------
# allow_deduction category amount 
#----------------------------------------
'''
Calculate Allowance/Deduction amount by Category
'''
class hr_allowance_cat(osv.osv):
    _name = "hr.allowance.cat"
    _columns = {
        'cat_id' : fields.many2one('hr.employee.category' , string='Category' , required=True) ,
        'value' : fields.float('Percent' , required=True) ,  
        'allow_deduct_id' : fields.many2one('hr.allowance.deduction' , string='Allowance/Deduction'),
    }


#----------------------------------------
# Allowance/Deduction 
#----------------------------------------
class hr_allowance_deduction(osv.osv):
    _name = "hr.allowance.deduction"
    _description = "Allowance and Deduction"
    _columns = {
        'name' :fields.char("Name", size=64, required=True),
        'company_id' : fields.many2one('res.company', 'Company'),
        'pay_sheet':fields.selection([('first', 'First Pay Sheet'), ('second', 'Second Pay Sheet')], 'Pay Sheet'),
        'allowance_type':fields.selection([('serv_terminate', 'Allowance of Service Terminated'),
                                       ('qualification','Qualification'),('substitution','Substitution'),
                                       ('family_relation','Family Relation'),('general', 'General'), 
                                       ('in_cycle', 'In Cycle')], 'Allowance type'),
        'name_type':fields.selection([('allow', 'Allowance'), ('deduct', 'Deduction')], 'Type', required=True),
        'sequence' :fields.integer("Sequence"),
        'type':fields.selection([('amount', 'Amount'), ('complex', 'Complex'), ], 'Type', required=True),
        'taxable' : fields.boolean('Taxable'),
        'exempted_amount' :fields.float("Exempted Amount", digits_compute=dp.get_precision('Payroll'), required=False),
        'bonus_percent' :fields.float("Bonus Taxes Percent", digits_compute=dp.get_precision('Payroll')),
        'start_date' :fields.date("Start Date", required=True),
        'end_date' :fields.date("End Date"),
        'notes' :fields.text("Notes", size=256),
        'account_id': fields.property('account.account', type='many2one', relation='account.account', string='Account', view_load=True
                             ,domain="[('type','in',('payable','receivable','other'))]"),
        'category_ids': fields.many2many('hr.employee.category', 'allow_deduct_category_rel', 'allow_deduct_id', 'category_id', 'Categories'),
        'active' : fields.boolean('Active'),
        'in_salary_sheet' : fields.boolean('In Salary Sheet'),
        'special' : fields.boolean('Special'),
        'penalty' : fields.boolean('Penalty'),
        'linked_absence' : fields.boolean('Linked With Absence'),
        'code': fields.char('Code', size=64),
        'marital_status_ids': fields.one2many('hr.allow.marital.status', 'allow_deduct_id', 'Marital Status'),
        'related_marital_status' :fields.selection([ ('yes', 'Yes'), ('no', 'No')], 'Related To Marital Status', required=True),
        'department_ids': fields.many2many('hr.department', 'allow_deduct_department_rel', 'allow_deduct_id', 'department_id', 'Departments'),
        'distributed' :fields.float("Distributed by ", digits_compute=dp.get_precision('Payroll')),
        'stamp' :fields.float("Stamp", digits_compute=dp.get_precision('Payroll')),
        'based_employment':fields.selection([('based', 'Percentage Based On Employment Date'),
                                         ('not_based', 'Not Based On Employment Date')], 'Based on Employment', required=True),
        'salary_included' : fields.boolean('Salary Included'),
        'started_section_included' : fields.boolean('Started Section Included'),
        'old_salary_included' : fields.boolean('Old Salary Included'),
        'allowances_ids':fields.many2many('hr.allowance.deduction', 'com_allow_deduct_rel', 'com_allow_deduct_id', 'allowance_id', 'Allowances'),
        'holiday_ids':fields.many2many('hr.holidays.status', 'holiday_allow_deduct_rel', 'allow_deduct_id', 'holiday_id', 'Holidays'),
        'job_ids': fields.many2many('hr.job', 'allow_deduct_job_rel', 'allow_deduct_id', 'job_id', 'Jobs'),
        'allow_job_ids': fields.one2many('hr.allowance.job', 'allow_deduct_id', 'Jobs'),
        'allow_gender_ids' : fields.one2many('hr.allowance.gender', 'allow_deduct_id', 'Genders'),
        'related_gender_type': fields.boolean('Related To Gender Type'),
        'allow_cat_ids' : fields.one2many('hr.allowance.cat', 'allow_deduct_id', 'Category'),
   
    }
    _defaults = {
        'active' : 1,
        'type' : 'amount',
        'related_marital_status' :'no',
        'allowance_type' :'general',
        'based_employment' :'based',
    }
    _order = "sequence"
    def _positive_allow(self, cr, uid, ids, context=None):
        for allows in self.browse(cr, uid, ids, context=context):
          if allows.stamp<0 or allows.distributed<0 or allows.bonus_percent<0 or allows.exempted_amount<0:
               return False
        return True 

    def _check_recursion(self, cr, uid, ids, context=None):
       """Checks recursion to avoid choosing allowance in complex allowances for the allowance it self.
          @param ids: List of allowances/deductions ids
          @return: True or False
       """
       for c in self.browse(cr, uid, ids):
          if c in tuple(c.allowances_ids):
             return False
       return True

    def copy(self, cr, uid, ids, default={}, context=None):
        default.update({'name':None })
        return super(hr_allowance_deduction, self).copy(cr, uid, ids, default=default, context=context)


    _sql_constraints = [
       ('name_uniqe', 'unique (name)', 'you can not create same name !')
    ]

    _constraints = [
        (_check_recursion, 'Error ! You cannot create recursive Allowance or Deduction.', ['name']),
        (_positive_allow, 'The value  must be more than zero!', ['Same Fields']),
    ]

    def write(self, cr, uid, ids, vals, context=None):
       """Method that overwrites write method and detects changes in the configuration of the allowances and deductions 
          and calls  change_allow_deduct function to recalculate allowances and deductions amount.
          @param vals: Dictionary contains the entered values
          @return: Boolean True
       """
       write_allow_deduct = super(hr_allowance_deduction, self).write(cr, uid, ids, vals, context)
       if 'in_salary_sheet' in vals and not vals['in_salary_sheet']:
          emp_salary_obj = self.pool.get('hr.employee.salary')
          emp_salary_id = emp_salary_obj.search(cr, uid, [('allow_deduct_id', '=', ids[0])])
          emp_salary_obj.unlink(cr, uid, emp_salary_id)
       else:
          update_field = [key for key in vals.keys() if key not in  ('name', 'code', 'sequence', 'notes', 'account_id')]
          if update_field:
              update = self.pool.get('payroll').change_allow_deduct(cr, uid, ids, [])
       return write_allow_deduct


    def write_scheduler(self, cr, uid, ids=None, use_new_cursor=False, context=None):
       """Scheduler to check end date of allowances and deductions periodically 
       @return True
       """
       date = time.strftime('%Y-%m-%d')
       allow_deduct_ids = self.search(cr, uid, [('end_date', '<=', date), ('in_salary_sheet', '=', True), ('special', '=', False)])
       if allow_deduct_ids:
          for allow_deduct in self.browse(cr, uid, allow_deduct_ids):
             write_allow_deduct = self.write(cr, uid, [allow_deduct.id], {'active':False})
       return True

    def unlink(self, cr, uid, ids, context=None):
        for rec in self.browse(cr, uid, ids, context=context):
            cr.execute("select leave_id from hol_allow_deduct_rel where allow_deduct_id = %s" , (rec.id,))
            res = cr.fetchone()
            if res:
                raise orm.except_orm(_('ERROR'), _('Sorry deletion not permitted because it reference in holidays'))
            
        return super(osv.osv, self).unlink(cr, uid, ids, context)


#----------------------------------------
#allowance marital status
#----------------------------------------
class hr_allow_marital_status(osv.osv):
    _name = "hr.allow.marital.status"
    _description = "Marital Status Allowance And Deduction Settings "
    _columns = {
        'allow_deduct_id' : fields.many2one('hr.allowance.deduction', 'Allowance'),
        'percentage' :fields.float("Percentage", digits_compute=dp.get_precision('Payroll')),
        'taxable' :fields.float("Taxable Amount", digits_compute=dp.get_precision('Payroll')),
        'married': fields.boolean('Married'),
        'children_no' : fields.integer('Children No'),
     }

#----------------------------------------
#Salary Scale Allowances Deduction 
#----------------------------------------
class hr_salary_allowance_deduction(osv.osv):
    _name = "hr.salary.allowance.deduction"
    _description = "The Amount Or Percentage Of Allowance / Deduction For The Degree "
    _columns = {
        'payroll_id' : fields.many2one('hr.salary.scale', 'Salary', required=True , readonly = True),
        'degree_id' : fields.many2one('hr.salary.degree', 'Degree', required=True , domain="[('payroll_id','=',payroll_id)]", readonly = True),
        'allow_deduct_id' :fields.many2one('hr.allowance.deduction', 'Name', required=True, ondelete='cascade', readonly = True),
        'amount' :fields.float("Amount/Percentage", digits_compute=dp.get_precision('Payroll')),
    }
    _sql_constraints = [

       ('degree_allow_deduct_uniqe', 'unique(degree_id,allow_deduct_id)', 'you can not duplicate the allowance for degree !'),
                      ]
    def create(self, cr, uid, vals, context=None):
       """Method that overwrites create method adds a new record and calculates allowances and deductions amount.
           @param vals: dictionary contains the entered values 
           @return: Id of the created record 
       """
       create_allow_deduct = super(osv.osv, self).create(cr, uid, vals, context)
       update = self.pool.get('payroll').change_allow_deduct(cr, uid, [], [create_allow_deduct])

       return create_allow_deduct

    def write(self, cr, uid, ids, vals, context=None):
       """Method that overwrites write method and calls change_allow_deduc function to re-calculate allowances and deductions amount
           if any changes happened.
           @param vals: dictionary contains the entered values 
           @return: Boolean True
       """
       write_allow_deduct = super(osv.osv, self).write(cr, uid, ids, vals, context)
       update = self.pool.get('payroll').change_allow_deduct(cr, uid, [], ids)
       return write_allow_deduct

    def unlink(self, cr, uid, ids, context=None):
        """Method that overwrites unlink mehtod and deletes record from hr.salary.allowance.deduction and updates hr.employee.salary 
           by deleting the associated allowance/deduction of the spacefic degree from it.
           if any changes happened.
           @return: Boolean True
        """
        employee_salary_obj = self.pool.get("hr.employee.salary")
        employee_obj = self.pool.get("hr.employee")
        for rec in self.browse(cr, uid, ids, context=context):
            allow_deduct_id = rec.allow_deduct_id.id
            payroll = rec.payroll_id.id
            degree = rec.degree_id.id
            super(osv.osv, self).unlink(cr, uid, ids, context)
            employee_ids = employee_obj.search(cr, uid, [('payroll_id', '=', payroll), ('degree_id', '=', degree)])
            if employee_ids:
               emp_salary_ids = employee_salary_obj.search(cr, uid, [('employee_id', 'in', tuple(employee_ids)), ('allow_deduct_id', '=', allow_deduct_id)])
               if emp_salary_ids:
                  employee_salary_obj.unlink(cr, uid, emp_salary_ids)
        return True
#----------------------------------------
#Zakat
#----------------------------------------
class hr_zakat(osv.osv):

    _name = "hr.zakat"
    _description = "Zakat Configuration"
    _columns = {
        'name' : fields.char("Name", size=64, required=True),
        'zakat_year' :fields.date("Zakat Year", required=False),
        'start_date' :fields.date("Start Date",),
        'end_date' :fields.date("End Date"),
        'monthly_value' :fields.float("Monthly Value", digits_compute=dp.get_precision('Payroll') , required=True),
        'minimal_amount' :fields.float("Minimal Amount", digits_compute=dp.get_precision('Payroll') , required=True),
        'religion': fields.selection([('muslim', 'Muslim'), ('christian', 'Christian'), ('others', 'Others')], 'Religion', required=True),
        'account_id': fields.property('account.account', type='many2one', relation='account.account', string="Account",
                                        method=True, view_load=True, required=False ,domain="[('user_type.report_type','=','expense'),('type','!=','view')]"),
        'active' : fields.boolean('Active'),
    }
    _defaults = {
        'active' :  1,
        'religion' : 'muslim',
   }
    def _check_not_zero(self, cr, uid, ids, context=None):
        for zakats in self.browse(cr, uid, ids, context=context):
          if zakats.monthly_value<0 or zakats.minimal_amount<0:
               return False
        return True 
    _constraints = [
        (_check_not_zero, 'The value  must be more than zero!', ['monthly_value','minimal_amount']),
                    ]
    _sql_constraints = [
          ('name_unique', 'unique(zakat_year)', 'The zakat year of zakat should be unique!'),
          ('date_check', 'CHECK( start_date < end_date)', 'The start date must be anterior to the end date.'),
        ]

    def copy(self, cr, uid, ids, default={}, context=None):
        default.update({'zakat_year':False,'start_date':False,'end_date':False,'monthly_value':0.00,'minimal_amount':0.00})
        return super(hr_zakat, self).copy(cr, uid, ids, default=default, context=context)
#----------------------------------------
#Taxes
#----------------------------------------
class hr_tax(osv.osv):
    
    _name = "hr.tax"
    _description = "Tax Configuration"
    _columns = {
        'name' : fields.char("Name", size=64, required=False),
        'taxset_min' :fields.float("Taxset Min", digits_compute=dp.get_precision('Payroll') , required=True),
        'taxset_max' :fields.float("Taxset Max", digits_compute=dp.get_precision('Payroll') , required=True),
        'taxset_age' :fields.integer("Taxset Age", required=True),
        'no_years_service':fields.integer("NO years service", required=True),
        'percent' :fields.float("Percent", digits_compute=dp.get_precision('Payroll') , required=True),
        'previous_tax' :fields.float("Previous Tax", digits_compute=dp.get_precision('Payroll') , required=True),
        'account_id': fields.property('account.account', type='many2one', relation='account.account', string="Account",
                                       method=True, view_load=True, required=False,domain="[('type','!=','view')]"),
        'bon_account_id': fields.property('account.account', type='many2one', relation='account.account', string="Bonuses Account",
                                        method=True, view_load=True, required=False,domain="[('type','!=','view')]"),
        'income_tax_percentage': fields.float('Personal Tax Percentage',digits = (16,2),help="represents the percentage of salary that the tax will be taken from"),
        'active' : fields.boolean('Active'),
    }

    _defaults = {
        'active' : 1,
        'income_tax_percentage' : 100,
    }


    def _check_income_tax_percentage(self, cr, uid, ids, context=None):
        """
        Constrain method that check digit you insert.

        @return: Boolean True or False
        """
        for tax in self.browse(cr, uid, ids): 
            if tax.income_tax_percentage < 0 :
               return False    	
        return True   

    def check_Taxset(self, cr, uid, ids, context={}):
       res = []
       for taxset in self.browse(cr, uid, ids, context=context):
         if taxset.taxset_min<taxset.taxset_max:
           res.append(taxset.taxset_min)
       return res

    def check_not_zero(self, cr, uid, ids, context=None):
        for taxs in self.browse(cr, uid, ids, context=context):
          if taxs.taxset_age<0 or taxs.no_years_service<0  or taxs.taxset_min<0 or taxs.taxset_max<0 or taxs.percent<0 or taxs.previous_tax<0 :
               return False
        return True 
    
    _constraints = [
        (check_Taxset, 'sorry the taxset_min is  Greater than taxset_max', ['taxset_min']),
        (check_not_zero, 'The value  must be more than zero!', ['Value Fields']),
        (_check_income_tax_percentage, 'Please insert the right digit', ['personal tax']),     
                    ]
    _sql_constraints = [
         ('name_unique', 'unique(name)', _('The name of tax should be unique!')),
        ]

    def copy(self, cr, uid, ids, default={}, context=None):
        default.update({'name':None,'taxset_min':0.00,'percent':0.00,'previous_tax':0.00})
        return super(hr_tax, self).copy(cr, uid, ids, default=default, context=context)

#----------------------------------------
#Allowance Deduction Exception
#----------------------------------------           
class hr_allowance_deduction_exception(osv.osv):
    _name = "hr.allowance.deduction.exception"
    _description = "Allowance / Deduction Exception"
    _columns = {

        'employee_id': fields.many2one('hr.employee', "Employee", required=True, readonly=False),
        'allow_deduct_id': fields.many2one('hr.allowance.deduction', 'Allowance/Deduction', domain="[('in_salary_sheet','=','True')]", required=True , ondelete="restrict"),
        'start_date' :fields.date("Start Date", required=True),
        'end_date' :fields.date("End Date"),
        'amount' :fields.float("Amount", digits=(18, 2)),
        'types':fields.selection([('allow', 'Allowance'), ('deduct', 'Deduction')], 'Type', required=True),
        'action':fields.selection([('special', 'Specialization'), ('exclusion', 'Exclusion')], 'Process Type', required=True),
        'comments':fields.char("Comments", size=100),
        'active' : fields.boolean('Active'),
    }
    _defaults = {
        'active':1,
        'employee_id': lambda *a: False,
    }
    def check_dates(self, cr, uid, ids, context=None):
         exp = self.read(cr, uid, ids[0], ['start_date', 'end_date'])
         if exp['start_date'] and exp['end_date']:
             if exp['start_date'] > exp['end_date']:
                 return False
         return True

    _constraints = [
        (check_dates, 'Error! Exception start-date must be lower then Exception end-date.', ['start_date', 'end_date'])
    ]

    _sql_constraints = [('amount_check', 'CHECK ((amount)>=0)', _("Only Positive Value Allowed For Amount Field!")),('unique_check', 'unique(employee_id,action,types,allow_deduct_id,start_date)', _('You Can Not Duplicate Two Exception Records With The Same Information!')),]
    def onchange_employee(self, cr, uid, ids, emp_id, context={}):
        """
           Method returns the employee_type that allowance/deduction exception is enabled for them.
           @param emp_id: ID of the employee
           @return: Dictionary contains the domain of the employee_type
        """
        emp_obj = self.pool.get('hr.employee')
        company_obj = self.pool.get('res.users').browse(cr, uid, uid).company_id
        contractors = company_obj.allowance_deduction_contractors
        employee = company_obj.allowance_deduction_employee
        recruit = company_obj.allowance_deduction_recruit
        trainee = company_obj.allowance_deduction_trainee
        employee_domain = emp_obj._get_default_employee_domain(cr, uid, ids, contractors, employee, recruit, trainee)
        employee_domain['employee_id'].append(('state', '=', 'approved'))
        domain = {'employee_id':employee_domain['employee_id']}
        return {'domain': domain}
    def onchange_type(self, cr, uid, ids, types):
        domain = {'allow_deduct_id':[('name_type','!=','deduct')]}
        if types:
            if types=='allow':
                domain = {'allow_deduct_id':[('name_type', '=', 'allow')]}
            else:
                domain = {'allow_deduct_id':[('name_type', '=', 'deduct')]}
        return {'value': {'allow_deduct_id':False} , 'domain': domain}

    def onchange_action(self, cr, uid, ids, action):
        domain = {'allow_deduct_id':[('allowance_type','!=','in_cycle'),('special', '=', False),('in_salary_sheet', '=', True)]}
        if action:
            if action=='special':
                domain = {'allow_deduct_id':[('special', '=', True),('allowance_type','!=','in_cycle'),('in_salary_sheet', '=', True)]}
            else:
                domain = {'allow_deduct_id':[('special', '=', False),('allowance_type','!=','in_cycle'),('in_salary_sheet', '=', True)]}
        return {'value': {'allow_deduct_id':False} , 'domain': domain}

    def duplicate_rec(self, cr, uid, ids, context=None): 
        process_obj = self.pool.get('hr.allowance.deduction.exception')      
        for record in self.browse(cr, uid,ids):
	     check_salary = process_obj.search(cr,uid,[('employee_id','=',record.employee_id),('action','=',record.action),('start_date','=',record.start_date)])
        if check_salary:
                raise orm.except_orm(_('Warning'), _('This employee already has been existed')) 
        return super(osv.osv, self).duplicate_rec(cr, uid, ids, context)

    def onchange_name_code(self, cr, uid, ids, emp, code=True):
        """
        Method sets employee code if name is entered or sets employee name if code is entered
        and reterns employee_type that allowed to undergone the process.
        @param emp: ID of the employee
        @param code: Code of the employee

        @return: Dictionary of values 
        """
        result = {}
        emp_obj = self.pool.get('hr.employee')
        if code:
            emp_id = emp_obj.search(cr, uid, [('emp_code', '=', emp)])
            if emp_id:
                result['value'] = {'employee_id':emp_id }
            else:
                raise orm.except_orm(_('ERROR'), _('Sorry this code is not exist'))
        else:
            result['value'] = {'code':emp_obj.browse(cr, uid, [emp])[0].emp_code, }
        emp_obj = self.pool.get('hr.employee')
        company_obj = self.pool.get('res.users').browse(cr, uid, uid).company_id
        contractors = company_obj.allowance_deduction_contractors
        employee = company_obj.allowance_deduction_employee
        recruit = company_obj.allowance_deduction_recruit
        trainee = company_obj.allowance_deduction_trainee
        employee_domain = emp_obj._get_default_employee_domain(cr, uid, ids, contractors, employee, recruit, trainee)
        domain = {'employee_id':employee_domain['employee_id']}
        result['domain'] = domain
        return result

    def create(self, cr, uid, vals, context=None):
       """
          Method adds new record of exception and recalculates employee's salary.
          @param vals: Dictionary contains entered values
          @return: Id of the created record
       """
       emp_obj = self.pool.get('hr.employee')
       exception_create = super(hr_allowance_deduction_exception, self).create(cr, uid, vals)
       emp_id = self.read(cr, uid, exception_create, ['employee_id'])
       update = emp_obj.write_employee_salary(cr, uid, [emp_id['employee_id'][0]], [])
       return exception_create

    def write(self, cr, uid, ids, vals, context=None):
       """
          Method updates a record of exception and recalculates employee's salary.
          @param vals: Dictionary contains entered values
          @return: Boolean True
       """
       emp_obj = self.pool.get('hr.employee')
       exception_write = super(hr_allowance_deduction_exception, self).write(cr, uid, ids, vals)
       emp_id = self.read(cr, uid, ids[0], ['employee_id'])
       update = emp_obj.write_employee_salary(cr, uid, [emp_id['employee_id'][0]], [])
       return exception_write

    def unlink(self, cr, uid, ids, context=None):
       """
          Method deletes a record of exception and recalculates employee's salary.
          @param vals: Dictionary contains entered values
          @return: Id of the deleted record
       """
       emp_obj = self.pool.get('hr.employee')
       emp_id = self.read(cr, uid, ids[0], ['employee_id'])
       exception_unlink = super(hr_allowance_deduction_exception, self).unlink(cr, uid, ids)
       update = emp_obj.write_employee_salary(cr, uid, [emp_id['employee_id'][0]], [])
       return exception_unlink

    def exception_scheduler(self, cr, uid, ids=None, use_new_cursor=False, context=None):
       """Scheduler to check end date of allowances and deductions Specialization/Exclusion
       @return True
       """
       date = time.strftime('%Y-%m-%d')
       end_exception_ids = self.search(cr, uid, [('end_date', '<=', date)])
       if end_exception_ids:
          for exception in self.browse(cr, uid, end_exception_ids):
              self.write(cr, uid, [exception.id], {'active':False})
       start_exception_ids = self.search(cr, uid, ['|',('end_date', '>=', date),('end_date', '=', False),('start_date', '<=', date)])
       if start_exception_ids:
          for exception in self.browse(cr, uid, start_exception_ids):
              self.write(cr, uid, [exception.id], {})
       return True

#----------------------------------------
#employee substitution archive
#----------------------------------------
class hr_employee_substitution(osv.osv):
    _name = "hr.employee.substitution"
    _description = "Substitafution"
    _rec_name='employee_id'
    _columns = {
        'employee_id': fields.many2one('hr.employee', "Employee", domain="[('state','=','approved'),('substitution','!=','True')]",readonly=True, states={'draft':[('readonly', False)]}),
        'start_date' :fields.date('Start Date' ,readonly=True, states={'draft':[('readonly', False)]}),
        'end_date' :fields.date('End Date'),
        'payroll_id' :fields.many2one('hr.salary.scale', 'Salary',readonly=True, states={'draft':[('readonly', False)]}),
        'degree_id' :fields.many2one('hr.salary.degree', 'Degree', domain="[('payroll_id','=',payroll_id)]", required=True,readonly=True, states={'draft':[('readonly', False)]}),
        'bonus_id' :fields.many2one('hr.salary.bonuses', 'Bonus', domain="[('degree_id','=',degree_id)]", required=True,readonly=True,states={'draft':[('readonly', False)]}),
        'comments': fields.text("Comments", size=100),
        'state': fields.selection([('draft', 'Draft'), ('approve', 'Approve'),('done', 'Done')], 'State', readonly=True),
    }
    _defaults = {
        'state': 'draft',
    }
    _sql_constraints = [('Date_check',"CHECK (end_date>=start_date)",_("Start_date must be before End_date!")),
       ('employee_period_date', 'unique (employee_id,start_date,end_date)', 'You can enter the same employee in the same period date!'),
    ]
    
    def copy(self, cr, uid, ids, default={}, context=None):
        default.update({'start_date':False,'end_date':False})
        return super(hr_employee_substitution, self).copy(cr, uid, ids, default=default, context=context)
    
    def unlink(self, cr, uid, ids, context=None):
            for sub in self.browse(cr, uid, ids, context=context):
                if sub.state!='draft':
                    raise osv.except_osv(_('Warning!'),_('You cannot delete substitution not draft'))
            return super(hr_employee_substitution, self).unlink(cr, uid, ids, context)


    def action_approve(self, cr, uid, ids, context={}):
        """Method that changes the state to 'approve' and reflects the substitution to hr_employee object
        @return: Boolean True
        """
        emp_obj = self.pool.get('hr.employee')
        for rec in self.browse(cr, uid, ids):
            emp_obj.write(cr, uid, [rec.employee_id.id], {'substitution': 1}, context=context)
        self.write(cr, uid, ids, {'state': 'approve'}, context=context)
        return True
    
    def action_done(self, cr, uid, ids, context={}):
        """Method that changes the state to 'done' and removes the effects of substitution from hr_employee object (end substitution period)
        @return: Boolean True
        """
        emp_obj = self.pool.get('hr.employee')
        for rec in self.browse(cr, uid, ids):
            if not rec.end_date:
                 raise osv.except_osv(_('Error'), _('Enter End Date'))
            emp_obj.write(cr, uid, [rec.employee_id.id], {'substitution': 0}, context=context)
        self.write(cr, uid, ids, {'state': 'done'}, context=context)
        return True

    def substitution_scheduler(self, cr, uid, ids=None, use_new_cursor=False, context=None):
       """Scheduler to check end date of substitution
       @return True
       """
       date = time.strftime('%Y-%m-%d')
       subst_ids = self.search(cr, uid, [('end_date', '<=', date),('state', '=', 'approve')])
       self.action_done(cr, uid, subst_ids, context=context)
       return True


#----------------------------------------
#Payroll Main Archive
#---------------------------------------- 
class hr_employee_salary_addendum(osv.Model):

    _name = 'hr.employee.salary.addendum'

    def _get_months(self, cr, uid, context):
        months = [(n, n) for n in range(1, 13)]
        return months

    _columns = {
        'name':  fields.char('Name', size=64 , required = True),
        'company_id': fields.many2one('res.company', 'Company'),
        'payroll_ids': fields.many2many('hr.salary.scale', 'payroll_bonus_rel', 'pay_bonus', 'pay_id', 'Salary Scale'),
        'addendum_ids': fields.many2many('hr.allowance.deduction', 'addendum_payroll_rel3', 'payroll_addendum', 'addendum_id', 'Addendum'),
        'employee_ids': fields.many2many('hr.employee', 'payroll_employee_rels', 'pay_emp', 'employ_id', "Employees"),
        'month' :fields.selection([('1', "1"),('2', "2"),('3', "3"),('4', "4"),('5', "5"),('6', "6"),
                                   ('7', "7"),('8', "8"),('9', "9"),('10', "10"),('11', "11"),('12', "12")], "Month", required = True),
        'year' :fields.integer("Year", required = True),
        'date' :fields.date("Date", required = True),
        'type':fields.selection([('salary', 'Salary'), ('addendum', 'Addendum')], "Type", required = True),
        'arch_ids':fields.one2many('hr.payroll.main.archive', 'arch_id', "Employee Details"),
        'state': fields.selection([('draft', 'Draft'),('compute', 'compute'),('approve','Approved'),
                                   ('transferred', 'Transferred'),('cancel', 'Rejected'),
         ], 'Status', select=True, readonly=True),
         'number': fields.many2one("account.voucher",'Number' , readonly=True),
         'compute_per':fields.selection([('batch', 'Batch'), ('employee', 'Employees')], "Compute Per", required = True,readonly=True, states={'draft':[('readonly', False)]}),
         'batch_ids':fields.one2many('hr.salary.batch', 'salary_adden_id', "Salary Batchs"),
    }


    _defaults = {
        'year': int(time.strftime('%Y')),
        'month': int(time.strftime('%m')),
        'date': time.strftime('%Y-%m-%d'),
        'type':'salary',
        'compute_per':'batch',
        'state': 'draft',
        'name': '/',
    }
    def unlink(self, cr, uid, ids, context=None):
        rec = self.read(cr, uid, ids, ['state'], context=context)
        unlink_ids = []
        for s in rec:
            if s['state'] in ['draft','cancel']:
                unlink_ids.append(s['id'])
            else:
                raise osv.except_osv(_('Invalid Action!'), _('In order to delete a salary or addendum, you must cancel it first.'))
        return super(hr_employee_salary_addendum, self).unlink(cr, uid, unlink_ids, context=context)

    def create(self, cr, uid,vals, context=None):
        new_id = super(hr_employee_salary_addendum, self).create(cr, uid, vals, context=context)
        for rec in self.browse(cr,uid,[new_id]):
            if rec.compute_per == 'batch' :
                call = self.onchange_compute_per(cr, uid, [new_id], rec.compute_per)
        return new_id

    def copy(self, cr, uid, id, default=None, context=None):
        if not default:
            default = {}
        default.update({
            'state':'draft',
            'arch_ids': [],
            'name': '/',
            'number': '',})
        return super(hr_employee_salary_addendum, self).copy(cr, uid, id, default, context)

    def action_cancel(self, cr, uid, ids, context=None):
        archive_obj = self.pool.get('hr.payroll.main.archive')
        domain = []
        if context.get('employee_ids') :
            domain+=[('employee_id', 'in', context['employee_ids'] )]
        for rec in self.browse(cr, uid, ids, context=context):
            domain+=[('arch_id', '=', rec.id)]
            arch_ids= archive_obj.search(cr, uid, domain)
            if arch_ids: 
                archive_obj.unlink(cr, uid, arch_ids)
        if not context.get('employee_ids') : self.write(cr, uid, ids, {'state':'cancel'}, context=context)      
        else : self.write(cr, uid, ids, {'state':'draft'}, context=context)      
        return True

    def action_cancel_draft(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state':'draft'})        
        return True

    def get_data(self, cr, uid, ids, context = {}):
        salary_scale_obj = self.pool.get('hr.salary.scale')
        main_archive_obj = self.pool.get('hr.payroll.main.archive')
        archive_obj = self.pool.get('hr.allowance.deduction.archive')
        employee_obj = self.pool.get('hr.employee')
        res_company_obj = self.pool.get('res.company')
        res = {}
        for record in self.browse(cr, uid, ids, context = context):
            if record.company_id:
                company_ids = [record.company_id.id]
            else:
                company_ids = res_company_obj.search(cr, uid, [ ], context = context)
            if record.payroll_ids:
                payroll_ids = [payroll.id for payroll in record.payroll_ids]
            else:
                payroll_ids = salary_scale_obj.search(cr, uid, [])
            if record.compute_per=='employee':
                if record.employee_ids:
                    employee_ids = record.employee_ids and [x.id for x in record.employee_ids]
                else:
                    employee_ids = employee_obj.search(cr, uid, ['|',('state', '!=', 'refuse'),('delegation', '=', True),
                                                                 ('salary_suspend', '!=', True),('payroll_id', 'in', payroll_ids), 
                                                                 ('company_id', 'in', company_ids), ])
            else:
                if record.state=='approve' and record.arch_ids:
                    employee_ids = record.batch_ids and [arc.employee_id.id for arc in record.arch_ids]
                else:
                    emp_ids =  [emp.id for emp in self.pool.get('hr.salary.batch').browse(cr, uid, [context['salary_batch_id']])[0].batch_id.employee_ids]
                    if emp_ids:
                        employee_ids = employee_obj.search(cr, uid, ['|',('state', '!=', 'refuse'),('delegation', '=', True),
                                                                 ('salary_suspend', '!=', True),('payroll_id', 'in', payroll_ids), 
                                                                 ('company_id', 'in', company_ids),  ('id', 'in', emp_ids)])
            domain = [('month', '=', record.month), ('year', '=', record.year), ('scale_id', 'in', payroll_ids),
                                            ('employee_id', 'in', employee_ids), ('company_id', 'in', company_ids)]

            if record.type == 'salary':
                domain.append(('in_salary_sheet', '=', True))
            else:
                domain.append(('in_salary_sheet', '=', False))
            addendum_ids = []
            if record.addendum_ids:
                addendum_ids = [x.id for x in record.addendum_ids]
            archive_ids = main_archive_obj.search(cr, uid, domain, context = context)
            addendums_arch_ids = []
            if archive_ids:
                if record.type == 'addendum':
                    addendums_arch_ids = archive_obj.search(cr, uid, [('main_arch_id', 'in', archive_ids),
                                                                      ('allow_deduct_id', 'in', addendum_ids)], context = context)
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
            }
        return res

    def days_calculation(self, cr, uid,ids ,  employee,paroll_date, hol ,context={}):
        status_obj = self.pool.get('hr.holidays.status')
        delegation_obj = self.pool.get('hr.employee.delegation')
        unpaied = status_obj.search(cr, uid, [('payroll_type', '=', 'unpaied')])

        customized = status_obj.search(cr, uid, [('payroll_type', '=', 'customized')])
        unpaied_del = delegation_obj.search(cr, uid,[('payroll_type','=','unpaied')])
        customized_del = delegation_obj.search(cr, uid,[('payroll_type','=','customized')])
        basic_salary = employee.bonus_id and employee.bonus_id.basic_salary or 0
        # Check employment date & end_date during salary computation
        #FIXME:  February has 28/29 days with always less than 30 
        emp_date = mx.DateTime.Parser.DateTimeFromString(employee.employment_date)
        end_date = employee.end_date and mx.DateTime.Parser.DateTimeFromString(employee.end_date) or paroll_date
        emp_no_days = (paroll_date - emp_date).days+1
        end_no_days = (paroll_date - end_date).days
        days = (emp_no_days < 30 and emp_no_days or 30) - (0 <= end_no_days <=30 and end_no_days or 0)
        #TEST: if same month has holiday & delegation
        #unpaied and  customized holidays
        hol_type = ""
        for un in unpaied:
            dict1 = hol.get((employee.id, 'unpaied', un), {})
            if dict1:
                days -= dict1['days']
                hol_type = "unpaid"
        if days >= 0 :
            basic_salary = (basic_salary / 30) * days
        customized_allow_deduct = []
        for cus in customized:
            dict2 = hol.get((employee.id, 'customized', cus), {})
            if dict2:
                days -= dict2['days']
                customized_allow_deduct += self.write_allow_deduct(cr, uid, ids, employee.id, dict2['days'], dict2['allow_deduct_ids'])
        #unpaied and  customized delegation
        '''
        for un in unpaied_del:
            dict1= deligation.get((employee.id,'unpaied',un), {})
            if dict1:
                days-=dict1['days']
                if days >= 0 :
                    basic_salary=(basic_salary/30)*days
                    customized_allow_deduct=[]
        for cus in customized_del:
            dict2= deligation.get((employee.id,'customized',cus),{})
            if dict2:
                days -= dict2.get('days', 0)
                customized_allow_deduct+=self.write_allow_deduct(cr, uid, ids, employee.id,dict2['days'],dict2['allow_deduct_ids'])    
        '''
        return {'days':days,'customized_allow_deduct':customized_allow_deduct, 'basic_salary':basic_salary , 'hol_type' : hol_type}
                
    def compute(self, cr, uid, ids, context = {}):
        """Compute salary/addendum for all employees or specific employees in specific month.
           @return: Dictionary 
        """
        start_salary = time.time()

        part1_start = time.time()
        main_arch_obj = self.pool.get('hr.payroll.main.archive')
        status_obj = self.pool.get('hr.holidays.status')
        delegation_obj = self.pool.get('hr.employee.delegation')
        holidays_obj = self.pool.get('hr.holidays')

        payroll_obj = self.pool.get('payroll')
        employee_obj = self.pool.get('hr.employee')
        archive_obj = self.pool.get('hr.allowance.deduction')

        data= self.get_data(cr, uid, ids, context=context)
        if data['archive_ids']:
            raise osv.except_osv(_('Error'), _('The  %s In The %sth Month Year Of %s It is  Already Computed')
                                    % (data['type'], data['month'], data['year']))
        if not data['employee_ids']:
            raise osv.except_osv(_('Error'), _('No employee found.'))
        if  context.get('salary_batch_id'):
            self.pool.get('hr.salary.batch').write(cr,uid,[context.get('salary_batch_id')],{'batch_total':len(data['employee_ids']),} )
       # main_arch_obj.create_main_archive(cr, uid, \
                       # {'employee_ids':data['employee_ids'],'year':data['year'], 'month': data['month']})

        paroll_date = (datetime.date (int(data['year']),  int(data['month']), 1) + relativedelta(day=1, months=+1, days=-1)).strftime('%Y-%m-%d')
        paroll_date = mx.DateTime.Parser.DateTimeFromString(paroll_date)               
        #TODO: *** do upper update inside the for loop and use res dictionary in write_allow_deduct
        part1_stop = time.time()
        #print">>>>>>>>>>>>>>>",part1_stop- part1_start,"HHHHHHH", len(data['employee_ids'])
        ######## Used for copy feature ##############
        if data['type'] == 'salary':
            pre_month = data['month'] - 1
            arch_year = (pre_month == 1) and data['year'] -1 or data['year']
            #print"DDDDDDDDDDD",pre_month,"DDDDDDD",type(data['month'])
         
            domain = [('month', '=', pre_month), ('year', '=', arch_year), ('scale_id', 'in', data['payroll_ids']),
                      ('company_id', 'in', data['company_id']),('in_salary_sheet', '=', True)]

            archive_ids = main_arch_obj.search(cr, uid, domain, context = context)

            total_part0 = 0
            count = 0
            print">>>>>>>>>>>>>>>>>>",len(archive_ids)
            '''for archive_id in archive_ids:
                part0_start = time.time()
                main_arch_obj.copy(cr, uid, archive_id,{'arch_id' :data['record_id'], 
                                                        'year': data['year'], 'month': data['month']}, context)
                total_part0 += time.time() - part0_start
                count += 1
                print">>....Count>>>>>>>", count
                print">>>>>>>>>>>>>>>>>>",total_part0
            ss'''
        ######## End of copy feature ##############
        count = 0
        count2 = 0
        total_part2 = 0
        total_part3 = 0
        total_part4 = 0
        total_cal =0 
        total_create_time = 0
        new_archive_ids =[]
        query_2nd_part = ""
        query_2nd_part_args = []
        allow_deduct_list = []
        hol = self._get_leave_status(cr, uid, ids, data['employee_ids'] , data['month'], data['year'])
        for employee in employee_obj.browse(cr, uid, data['employee_ids'], context = context):
            employee_start = time.time()
            if data['type'] == 'salary': 
                part2_start = time.time()
                time1 = time.time()
                in_salary_sheet = True
                result = self.days_calculation(cr, uid, ids ,employee, paroll_date ,hol)
                #print "Time 1:   days_calculation ", time.time()-time1
                time2 = time.time()
                days = result['days']
                basic_salary = result['basic_salary']
                customized_allow_deduct = result['customized_allow_deduct']
                if days <= 0 and result['hol_type'] == "unpaid":
                    continue

                allow_deduct_dict = self.write_allow_deduct(cr, uid, ids, employee.id, days)
                #print "Time 2:   write_allow_deduct: ", time.time()-time2
                total_part2 += time.time() - part2_start
                part3_start = time.time()
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
                total_part3 += time.time() - part3_start

       


#######################################################################3
            else:
                basic_salary = 0.0
                days = 30
                in_salary_sheet = False
                allow_deduct_dict = []
                house=employee.house_type
                if house != '1' or data['addendum_ids'] !=[38] :
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
                           #print">>>>>>>>>>>>>>>>>>>>>>>>>1>>>>>>>allow_deduct_dict" ,allow_deduct_dict
                else:
                     allow_deduct_dict=[]
                     #print">>>>>>>>>>>>>>>>>>>>>>>>>>2>>>>>>allow_deduct_dict" ,allow_deduct_dict
            part4_start = time.time()
            '''new_id, temp_create_time = main_arch_obj.create(cr, uid, {
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
                #'allow_deduct_ids': [(0, 0, x) for x in allow_deduct_dict],
                'in_salary_sheet':in_salary_sheet,
                'arch_id':data['record_id'],
                'bank_account_id': employee.bank_account_id and employee.bank_account_id.id or False,
            }, context = context)'''

            emp_bonus = employee.bonus_id and employee.bonus_id.id or None
            emp_degree = employee.degree_id and employee.degree_id.id or None
            cr.execute("INSERT INTO hr_payroll_main_archive\
                        (code, employee_id, month, year,\
                        department_id,salary_date,\
                        basic_salary,company_id,job_id,scale_id,degree_id,\
                        bonus_id,in_salary_sheet,arch_id, \
                        bank_account_id,net)\
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,%s)",
                        (employee.emp_code, employee.id, data['month'], data['year'],
                        employee.department_id and employee.department_id.id or None ,data['date'],
                        basic_salary, employee.company_id.id, employee.job_id and employee.job_id.id or None ,  employee.payroll_id.id, 
                        emp_degree, emp_bonus,in_salary_sheet, data['record_id'],
                        employee.bank_account_id and employee.bank_account_id.id or None ,0))
            #cr.execute("Select id from hr_payroll_main_archive where arch_id=%s  order by id desc LIMIT 1",(ids[0],))          
            cr.execute("Select id from hr_payroll_main_archive order by id desc LIMIT 1")
            result = cr.fetchone()
            new_archive_ids.append(result[0])
           
            
            for line in allow_deduct_dict:
                count2 += 1 
                if query_2nd_part:
                    query_2nd_part += ','
                query_2nd_part += "(%s, %s, %s, %s, %s, %s, %s)"
                query_2nd_part_args += (True,
                        line['tax_deducted'],
                        line['amount'],
                        line.get('type', 'allow'),
                        line['remain_amount'],
                        line['allow_deduct_id'], 
                        result[0])#
                '''cr.execute("INSERT INTO hr_allowance_deduction_archive\
                           (tax_deducted, amount, type, remain_amount, allow_deduct_id,  main_arch_id) \
                            VALUES (%s, %s, %s, %s, %s, %s)",
                          (line['tax_deducted'],line['amount'],line['type'],line['remain_amount'],line['allow_deduct_id'],
                             result[0]))'''
                line.update({'main_arch_id':result[0]})
                allow_deduct_list.append(line)
            
            #total_create_time += temp_create_time
            
            total_part4 += time.time() - part4_start
            total_cal += time.time() - employee_start
            print">>>>>>>..count", count
            print">>>>>>>..part2", total_part2
            print">>>>>>>..part4", total_part4
            print">>>>>>>.total_calc", total_cal
            print">>>>>>>list>>>",allow_deduct_list
            #print">>>>>>>.total create time", total_create_time
            #raise
            count +=1
            if count == 222100:
                raise
        query_1st_part =""" INSERT INTO hr_allowance_deduction_archive\
                           (active, tax_deducted, amount, type, remain_amount, allow_deduct_id,  main_arch_id) \
                            VALUES """
        query_start = time.time()
        if query_2nd_part:
                cr.execute(query_1st_part + query_2nd_part, tuple(query_2nd_part_args))
        print">>>>> query time", time.time() - query_start,">>>>>>>>", count2
        #raise
        arc_start = time.time()
        if context.get('calculate_functional_field',True):
            main_arch_obj.write(cr, uid, new_archive_ids, {}, context)
        print">.Write time=",time.time() - arc_start
        if not context.get('salary_batch_id'):
            self.write(cr, uid, ids, { 'state': 'compute'}, context=context)
        else :
            state = len([btch.id for btch in self.browse(cr,uid,ids)[0].batch_ids if btch.state!='compute'])-1 > 0 and 'draft' or 'compute'
            self.write(cr, uid, ids, { 'state': state}, context=context)
        print "End of compute .....  ", time.time()-start_salary
        #raise
        return {'archive_ids':new_archive_ids}

    def _get_leave_status(self, cr, uid, ids, employee_ids , month, year):
        #print '_get_leave_status    ............. '
        month = str(month)
        year = str(year)    
        pyroll_date = len(month) == 1 and year+'-0' + month or year+'-'+month
        holidays = {}
        status_obj = self.pool.get('hr.holidays.status')
        status_ids = status_obj.search(cr, uid, [('payroll_type', 'in', ('customized', 'unpaied'))])
        if status_ids:
            cr.execute("""select h.id AS holiday_id, s.id AS status_id  ,h.employee_id AS employee_id,s.payroll_type AS type,
                         (CASE WHEN EXTRACT(MONTH FROM h.date_from) = %s
                                    and EXTRACT(YEAR FROM h.date_from) =%s THEN
                                    30-EXTRACT(DAY FROM h.date_from)+1
                                      ELSE 30 
                                END)+
                         (CASE WHEN EXTRACT(MONTH FROM h.date_to) = %s
                                    and EXTRACT(YEAR FROM h.date_to) =%s THEN
                                    EXTRACT(DAY FROM h.date_to)
                                      ELSE 30
                                END) - 30 as days
                          from  hr_holidays h  
                          LEFT JOIN hr_holidays_status s ON (s.id=h.holiday_status_id)
                          where h.state NOT IN ('cancel','refuse')
                          and h.type='remove'
                          and to_char(date_from , 'YYYY-MM') <= %s  
                          and to_char(date_to , 'YYYY-MM') >= %s
                          and h.holiday_status_id IN %s
                          and h.employee_id IN %s
                          """ , (month, year, month, year, pyroll_date , pyroll_date , tuple(status_ids), tuple(employee_ids),))
            res = cr.dictfetchall()
            for r in res:
                key = (r['employee_id'], r['type'], r['status_id'])
                if not key in holidays:
                    allow_deduct_ids = []
                    holidays[key] = r
                    if r['type'] == 'customized':
                        allow_deduct_ids = [r.id for r in status_obj.browse(cr, uid, r['status_id']).allow_deduct_ids]
                        holidays[key].update({'allow_deduct_ids':allow_deduct_ids})
        return holidays

    def write_allow_deduct(self, cr, uid, ids, emp_id, days, allow_deduct_ids = []):
        """Create allowances and deductions dictionaries for employees salary in specific month.
        @param emp_id : Id of employee
        @param days : Number of employment days
        @return: List of dictionaries
        """
        emp_salary_obj = self.pool.get('hr.employee.salary')
        dict_list = []
        res = []
        if days > 0:
            factor = days/30
            domin = " "
            if allow_deduct_ids:
                domin = ' AND allow_deduct_id in (%s)' % ','.join(map(str, allow_deduct_ids))
                #print domin
            cr.execute("""select  ad.id as allow_deduct_id, ad.name_type as type,               
                 (CASE WHEN s.holiday_amount>0 THEN
                  s.holiday_amount
                  ELSE s.amount  END) as amount,
                    s.tax_deducted as tax_deducted, s.remain_amount as remain_amount
                   from  hr_employee_salary s, hr_allowance_deduction ad
                   where ad.id=s.allow_deduct_id and s.employee_id=""" +str(emp_id)+ domin)
            res= cr.dictfetchall()
            print "##### res " , res
            if factor <> 1:
                for r in res:
                    r.update({'amount': r['amount']* factor, 'tax_deducted': r['tax_deducted']*factor })
        return res

    #This function was replaced with the above one to optimize performance
    '''def write_allow_deduct(self, cr, uid, ids, emp_id, days, allow_deduct_ids = []):
        """Create allowances and deductions dictionaries for employees salary in specific month.
        @param emp_id : Id of employee
        @param days : Number of employment days
        @return: List of dictionaries
        """
        emp_salary_obj = self.pool.get('hr.employee.salary')
        dict_list = []
        if days > 0:
            domin = [('employee_id', '=', emp_id)]
            if allow_deduct_ids:
                domin += [('allow_deduct_id', 'in', allow_deduct_ids)]
            allow_deduct_ids = emp_salary_obj.search(cr, uid, domin)
            if allow_deduct_ids:
                for allow_deduct in emp_salary_obj.browse(cr, uid, allow_deduct_ids):
                    allow_deduct_amount = allow_deduct.holiday_amount and (allow_deduct.holiday_amount / 30) * days or (allow_deduct.amount / 30) * days
                    tax_deducted = (allow_deduct.tax_deducted / 30) * days

                    allow_deduct_dict = {
                        'allow_deduct_id': allow_deduct.allow_deduct_id.id,
                        'type' : allow_deduct.allow_deduct_id.name_type,
                        'amount': allow_deduct_amount ,
                        'tax_deducted':tax_deducted ,
                        'remain_amount': allow_deduct.remain_amount ,
                    }
                    dict_list.append(allow_deduct_dict)
        return dict_list'''

    def transfer(self, cr, uid, ids, context = None):
        """Transfer Bonuses amounts and taxes to account module.
        @return: Dictionary 
        """
        result = self.pay( cr, uid, ids, context = None)
        number = self.pool.get('payroll').create_payment(cr, uid, ids, result, context=context)
        for rec in self.browse(cr, uid, ids):
            if rec.compute_per=='batch' and rec.batch_ids:
                self.pool.get('hr.salary.batch').write(cr, uid, [bat.id for bat in rec.batch_ids ], {'state': 'transferred'}, context=context)
        return self.write(cr, uid, ids, {'number':number, 'state': 'transferred'}, context=context)

    def pay(self, cr, uid ,ids,  context=None):
        salary_scale_obj = self.pool.get('hr.salary.scale')
        archive_obj = self.pool.get('hr.allowance.deduction')
        tax_amount = 0.0
        stamp_amount = 0.0
        lines = []
        reference=''
        employee_id = self.pool.get('hr.employee').search(cr, uid, [('user_id','=',uid)])
        department_id = employee_id and self.pool.get('hr.employee').browse(cr, uid,employee_id)[0].department_id or False
        account_analytic_id = department_id and department_id.analytic_account_id and department_id.analytic_account_id.id or department_id and  department_id.parent_id.analytic_account_id and department_id.parent_id.analytic_account_id.id or False
        if not  account_analytic_id:
            raise osv.except_osv(_('Warning!'),_('Please Set an analytic account for this department.'))
        data = self.get_data(cr, uid, ids, context = context)
        reference = "HR/PAY/" + data['type'] +str(data['month']) + "/" + str(data['year'])+'\n' 
        for l in data['addendum_ids']:
            allow_name=archive_obj.browse(cr,uid,l).name
            reference+=allow_name+'\n'
        if not data['archive_ids']:
            raise osv.except_osv(_('Error'), _('No Such %s In Thtotal_create_timee %sth Month Year Of %s To Be Transfer')
                                    % (data['type'], data['month'], data['year']))
        where = [tuple(data['archive_ids'])]
        if data['type'] == 'salary':
            cr.execute(
                'select scale_id as scale_id ,sum(COALESCE(basic_salary,0)) as basic_salary ' \
                'from hr_payroll_main_archive '\
                'where id IN %s '\
                'group by  scale_id', tuple(where))
            ress = cr.dictfetchall()
            #print">>>>>>>>>>>>>>>>>>>>>>>>>ress>>>>>>>>>>>>>>>>>>>>>",ress
            for r in ress:
                account_id = salary_scale_obj.browse(cr, uid, r['scale_id'], context = context).account_id
                if not account_id:
                    raise osv.except_osv(_('Configuration Error !'),
                                         _('Please Enter Account for salary scale !'))
                line = {
                    'name':'Basic Salary',
                    'account_id':account_id.id,
                    'amount':round(r['basic_salary'], 2),
                    'account_analytic_id':account_analytic_id,
                }
                lines.append(line)
            tax_amount+=sum([rcrd.tax for rcrd in self.pool.get('hr.payroll.main.archive').browse(cr, uid, data['archive_ids']) if rcrd.tax])

        addendum_clause = ''
        if data['addendum_ids']:
            addendum_clause = ' and ad.allow_deduct_id in %s '
            where.append(tuple(data['addendum_ids']))
        cr.execute(
            'select ad.allow_deduct_id as allow_deduct_id ,sum(COALESCE(ad.amount,0)) as amount,'\
            'sum(ad.tax_deducted) as tax_deducted,sum(COALESCE(ad.imprint,0)) as imprint '\
            'from hr_allowance_deduction_archive ad '\
            'LEFT JOIN hr_payroll_main_archive m ON (ad.main_arch_id=m.id) '\
            'where m.id IN %s '\
            + addendum_clause +
            'group by  ad.allow_deduct_id', tuple(where))
        res = cr.dictfetchall()
        #print"===========================================",res
        for r in res:
            line = {
                'allow_deduct_id':r['allow_deduct_id'],
                'amount':round(r['amount'], 2),
                'account_analytic_id':account_analytic_id,
            }
            lines.append(line)
            tax_amount += r.get('tax_deducted', 0.0)
            stamp_amount += r.get('imprint', 0.0)
        result = {
            'reference':reference, 
            'narration':reference, 
            'department_id':department_id.id,
            'lines':lines, 
            'tax_amount':tax_amount, 
            'stamp_amount':stamp_amount
            }
        return result


    def rollback(self, cr, uid, ids, context = {}):
        """delete records from main archive when rolback a calculated salary or addendum.
           @return: dictionary   
        """
        main_arch_obj = self.pool.get('hr.payroll.main.archive')
        loan_arch_obj = self.pool.get('hr.loan.archive')
        archive_obj = self.pool.get('hr.allowance.deduction.archive')
        emp_loan_obj = self.pool.get('hr.employee.loan')
        data = self.get_data(cr, uid, ids, context = context)
        emp_loan_ids=[]
    	time1 = time.time()   
        if not data['archive_ids']:
            raise osv.except_osv(_('Error'), _('No Such %s In The %sth Month Year Of %s To Be Rollbacked')
                                    % (data['type'], data['month'], data['year']))
        loan_arch_ids = loan_arch_obj.search(cr, uid, [('main_arch_id','in',data['archive_ids'])])
        if loan_arch_ids:
            emp_loan_ids=[rec.loan_id.id for rec in loan_arch_obj.browse(cr, uid,loan_arch_ids, context = context) ]


    	#print "Time 1:    ", time.time()-time1      
    	time2 = time.time()   

        if data['type'] == 'salary':
            testq = time.time()
            print">>>>>>>>>>>",data['archive_ids']
            cr.execute("""delete from hr_payroll_main_archive where id in %s """,(tuple( data['archive_ids']), ))
            #main_arch_obj.unlink(cr, uid, data['archive_ids'])
            print " Salary Time Rollbacking to unlink archive ids###########################", time.time()-testq
        else:
            testq = time.time()

            archive_obj.unlink(cr, uid, data['addendums_arch_ids'])
            print " Salary Time Rollbacking ###########################", time.time()-testq
            for e in main_arch_obj.browse(cr, uid, data['archive_ids'], context = context) :
                if not e.allow_deduct_ids:
                    main_arch_obj.unlink(cr, uid, e.id)
    	#print "Time 2:    ", time.time()-time2    
        if emp_loan_ids:
            loan = time.time()
            emp_loan_comnt = emp_loan_obj.read(cr, uid, emp_loan_ids, ['comments','end_date'])
            for rec in emp_loan_comnt:
                x=emp_loan_obj.write(cr,uid,rec['id'],{'comments':rec['comments'] and rec['comments']+'' or ''  },context)
            print " Salary Time Rollbacking Loan ###########################", time.time()-loan
 
        if  context.get('salary_batch_id'):
            self.pool.get('hr.salary.batch').write(cr,uid,[context.get('salary_batch_id')],{'batch_total':0,} ) 
        self.write(cr, uid, ids, { 'state': 'draft'}, context=context)
        return {}

    def approve(self, cr, uid, ids, context = None):
        for rec in self.browse(cr, uid, ids):
            if rec.compute_per == 'employee' :
                self.write(cr, uid, ids, { 'state': 'approve'}, context=context)
            else: 
                for bat in rec.batch_ids:
                    if bat.state!='approve':
                        raise osv.except_osv(_('Warning'), _('Sorry Batch %s has not been approved yet')% (bat.batch_id.name))
                self.write(cr, uid, ids, { 'state': 'approve'}, context=context)
        return {}

    def _get_delgation(self, cr, uid, ids,employee_ids,month,year):
        month=int(month)
        year=int(year)
        delegation={}
        delegation_obj = self.pool.get('hr.employee.delegation')
        delegation_ids = delegation_obj.search(cr, uid,[('payroll_type','in',('customized','unpaied'))])
        if delegation_ids:
            cr.execute("""select d.id AS delegation,d.employee_id AS employee_id,d.payroll_type AS type,
              (CASE WHEN EXTRACT(MONTH FROM d.start_date) = %s
                  and EXTRACT(YEAR FROM d.start_date) =%s THEN
                  30-EXTRACT(DAY FROM d.start_date)+1
                  ELSE 30 
                  END)+
                  (CASE WHEN EXTRACT(MONTH FROM d.end_date) = %s
                   and EXTRACT(YEAR FROM d.end_date) =%s THEN
                   EXTRACT(DAY FROM d.end_date)
                   ELSE 30
                   END) - 30 as days
                   from  hr_employee_delegation d  
                   where EXTRACT(MONTH FROM d.start_date) <= %s
                   and EXTRACT(YEAR FROM d.start_date) <=%s
                   and EXTRACT(MONTH FROM d.end_date)>=%s
                   and EXTRACT(YEAR FROM d.end_date)>=%s
                   and d.employee_id IN %s
              """ ,(month,year,month,year,month,year,month,year,tuple(employee_ids),))
            res= cr.dictfetchall()
            for r in res:
                key = ( r['employee_id'],r['type'],r['delegation'])
                if not key in delegation:
                    allow_deduct_ids = []
                    delegation[key]=r
                    if r['type']=='customized':
                        allow_deduct_ids=[a.id for a in delegation_obj.browse(cr, uid, r['delegation']).allow_deduct_ids ]  
                        delegation[key].update({'allow_deduct_ids':allow_deduct_ids})
                else:
                    delegation[key]['days'] += r['days']
        return delegation 
 
    def onchange_compute_per(self, cr, uid, ids, compute_per,context={}):
        if compute_per:
            emp_cat_obj = self.pool.get('hr.employee.category')
            salary_batch_obj = self.pool.get('hr.salary.batch')
            if compute_per=='batch' :
                batch_ids = emp_cat_obj.search(cr, uid,[('salary_batch','=',True),('active','=',True)])
                if not batch_ids: 
                    raise osv.except_osv(_('Warning!'), _('Sorry no batches in the configuration'))
                for rec in self.browse(cr, uid, ids) :
                    for batch in emp_cat_obj.browse(cr, uid,batch_ids):
                        domain = [('id', '!=' ,rec.id),('type' ,'=', 'salary'),('month', '=', rec.month),
                                  ('compute_per', '=', 'batch'),('year', '=', rec.year)]
                        sal_adn_ids = self.search(cr, uid, domain)
                        sal_adn_ids.append(0)
                        if  sal_adn_ids :
                            cr.execute("SELECT batch_id FROM hr_salary_batch WHERE salary_adden_id IN %s ",(tuple(sal_adn_ids),))
                            res = cr.fetchall()
                            if res and batch.id in [line[0] for line in res]: continue
                        salary_batch_obj.create(cr, uid,{'responsible_id':batch.responsible_id.id,
                                             'batch_id':batch.id,
                                             'salary_adden_id':ids and ids[0] or False,
                                             'state':'draft',})
            else:
                for rec in self.browse(cr, uid, ids):
                    batch_ids = [bat.id  for bat in rec.batch_ids if bat.state=='draft']
                    if len(batch_ids) < len( rec.batch_ids) :
                        self.write(cr, uid, ids, { 'compute_per': 'batch'}, context=context)
                        raise osv.except_osv(_('Warning!'), _('Sorry some batches are computed set them in draft state first '))
                    context['allow_delet']= True
                    salary_batch_obj.unlink(cr, uid ,batch_ids,context,)
        return {}

    '''def button_schedular(self, cr, uid, ids, context={}):
        for rec in self.browse(cr, uid, ids):
            test1 = time.time()
            data = {'year':rec.year, 'month': rec.month, 'employee_ids': [r.id for r in rec.employee_ids]}
            self.pool.get('hr.payroll.main.archive').create_main_archive(cr, uid, data=data, context=context)
        print " test schedular time  ..........", time.time()-test1
        return True'''

 
     
class hr_payroll_main_archive(osv.Model):

    _name = "hr.payroll.main.archive"
    _description = "Payroll Main Archive"
    _rec_name = 'employee_id'

    def total_allow_deduct(self, cr, uid, ids, name, args, context=None):
        """Method that caluclates the totals of employee's allowances, deductions, taxes and gets the net.
	       @return: Dictionary of values
        """
        print""""""""""""""""""""""""""
        tax = self.pool.get('hr.tax')
        result = {}
        start = time.time()
        for rec in self.browse(cr, uid, ids, context=context):
            taxable_amount = 0.0
            total_allowance = rec.basic_salary
            allowances_tax = 0.0
            income_tax = 0.0
            total_deduction = 0.0
            for line in rec.allow_deduct_ids:
                if line.type == 'allow':
                    total_allowance += line.amount
                    allowances_tax += line.tax_deducted
                    if line.allow_deduct_id.taxable and not rec.employee_id.tax_exempted:
                        taxable_amount += line.amount - line.allow_deduct_id.exempted_amount
                else:
                    total_deduction += line.amount
                    if line.allow_deduct_id.taxable and not rec.employee_id.tax_exempted:
                        taxable_amount -= line.amount - line.allow_deduct_id.exempted_amount
            if not rec.employee_id.tax_exempted:
                taxable_amount += rec.basic_salary
                tax_id = tax.search(cr, uid, [('taxset_min', '<=', taxable_amount), ('taxset_max', '>=', taxable_amount)], context=context)
                if tax_id:
                    tax_rec = tax.browse(cr, uid, tax_id)[0]
                    taxable_amount = abs(taxable_amount * tax_rec.income_tax_percentage / 100) 
                    income_tax = (((taxable_amount - tax_rec.taxset_min) * tax_rec.percent) / 100) + tax_rec.previous_tax
            result[rec.id] = {
                'tax':income_tax,
                'total_allowance':total_allowance,
                'allowances_tax': allowances_tax,
                'total_deduction': total_deduction + allowances_tax + income_tax,
                'net':(total_allowance - allowances_tax - total_deduction - income_tax),
            }
        print">>>>>>>>>>>>>>>>>>",time.time() - start
        return result 

    def _salary_zakat(self, cr, uid, ids, name, args, context=None):
        """Method that caluclates zakat amount for the employee.
	       @return: Dictionary of values 
        """
        zakat_obj = self.pool.get('hr.zakat')
        res = {}
        start = time.time()
        for rec in self.browse(cr, uid, ids, context=context):
            zakat_amount = 0.0
            zakat_id = zakat_obj.search(cr, uid, [('start_date', '<=', rec.salary_date), ('end_date', '>=', rec.salary_date)])
            if zakat_id:
                zakat = zakat_obj.browse(cr, uid, zakat_id)[0]
                if zakat.religion_id.id == rec.employee_id.religion:
                    amount = rec.basic_salary - zakat.minimal_amount
                    if amount < zakat_id.monthly_value:
                        zakat_amount = amount * (2.5) / (100)
            res[rec.id] = zakat_amount
        #print"S Zakat", time.time() - start
        return res

    def get_responsible(self, cr, uid, ids, name, args, context=None):
        """
		Method for functional field that get the resopnsible officer for employee's batch if the salary is calculated in bateches

		@param name: name of field to be updated
		@param args: other arguments
	    @return: Dictionary of values 
        """
        responsible_id = False
        res = {}
        salary_batch_obj = self.pool.get('hr.salary.batch')
        for rec in self.browse(cr, uid, ids, context=context):
            if rec.arch_id.compute_per=='batch':
                salary_batch_ids = salary_batch_obj.search(cr ,uid, [('salary_adden_id','=',rec.arch_id.id)])
                if salary_batch_ids:
                    for batsh in salary_batch_obj.browse(cr, uid, salary_batch_ids):
                        if rec.employee_id.id in [bt.id for bt in batsh.batch_id.employee_ids]:
                            responsible_id = batsh.responsible_id.id
                    res[rec.id] = responsible_id 
        return res


    '''def create_main_archive(self, cr, uid, data=None, context=None):
        if context is None:
            context = {}
        start_salary = time.time()  
        employee = " "
        if data:
            year = data['year']
            month = data['month']
        if data['employee_ids']:
            employee = " id in (%s)" % ','.join(map(str, data['employee_ids'])) + "  and "
        else:
            year = int(time.strftime('%Y'))
            month = int(time.strftime('%m'))            
        cr.execute("""SELECT id, %s, %s, True,30 FROM hr_employee WHERE """ +employee+ """  \
                id NOT IN (SELECT employee_id FROM hr_payroll_main_archive \
                WHERE year=%s and month=%s)  """,( year, month, year, month))
        res = cr.fetchall()
        #TODO: delete unwanted!!
        #TODO: working days is hard coded
        #print '///////////////////////////',res
        if res:
            cr.execute("""INSERT INTO hr_payroll_main_archive \
            (employee_id, year, month, in_salary_sheet, working_days) VALUES %s """% ','.join(map(str, res)) )
            
            cr.execute("""SELECT id FROM hr_payroll_main_archive \
                    WHERE year=%s and month=%s""",(year, month))
            archive_ids = [a[0] for a in cr.fetchall()]    
            self.compute_days(cr, uid, archive_ids, context)
        return True'''
    
    _columns = {
         'code': fields.char('Code', size=64 ,  readonly=True),
         'employee_id': fields.many2one('hr.employee', "Employee", required=True, readonly=True, select=1),
         'year' :fields.integer("Year", required=True , readonly=True, select=1),
         'month' :fields.integer("Month" , required=True, readonly=True, select=1),
         'salary_date' :fields.date("Salary Date",  readonly=True),
         'company_id' : fields.many2one('res.company', 'Company',  readonly=True),
         'job_id' : fields.many2one('hr.job', 'Job' , readonly=True),
         'department_id' : fields.many2one('hr.department', 'Department', domain="[('company_id','=',company_id)]", readonly=True),
         'scale_id' : fields.many2one('hr.salary.scale', 'Salary Scale' , readonly=True),
         'degree_id' : fields.many2one('hr.salary.degree', 'Degree' , readonly=True),
         'bonus_id' :fields.many2one('hr.salary.bonuses', "Bonus"  , readonly=True),
         'basic_salary' :fields.float("Basic Salary", digits_compute=dp.get_precision('Payroll') ,  readonly=True),
         'zakat': fields.function(_salary_zakat, string='Zakat', type='float',
                                      digits_compute=dp.get_precision('Payroll') , readonly=True, store=True),
                
         'total_allowance' :fields.function(total_allow_deduct, multi='sum', string='Total Allowance', type='float',
                                               digits_compute=dp.get_precision('Payroll') , readonly=True, store=True),
         'tax' :fields.function(total_allow_deduct, string='Income Tax', type='float', digits_compute=dp.get_precision('Payroll'),
                                     multi='sum', readonly=True, store=True),
         'allowances_tax' :fields.function(total_allow_deduct, string='allowance Taxes', type='float',
                                          digits_compute=dp.get_precision('Payroll'), multi='sum', readonly=True, store=True),
         'total_deduction' :fields.function(total_allow_deduct, multi='sum', string='Total Deduction', type='float',
                                                digits_compute=dp.get_precision('Payroll'), required=True , readonly=True, store=True),
         'net' :fields.function(total_allow_deduct, string='Salary Net', multi='sum', type='float',
                                                    digits_compute=dp.get_precision('Payroll'),
                                   required=True , readonly=True, store=True),
                        
         'allow_deduct_ids':fields.one2many('hr.allowance.deduction.archive', 'main_arch_id', "Allowances"),
         'new_allow_deduct_ids':fields.many2many('hr.allowance.deduction.archive', 'main_arch_allow_deduct_arch_rel',
                                                 'main_arch_id','allow_deduct_arch_id', "New Allowances"),
         'in_salary_sheet':fields.boolean('In Salary Sheet', readonly=True, required=True),
         'arch_id': fields.many2one('hr.employee.salary.addendum', 'payroll',ondelete='cascade'),
         'bank_account_id':fields.many2one('res.partner.bank', 'Bank Account Number', readonly=True,),
         'responsible_id': fields.function( get_responsible, method=True, string='Responsible Officer', type='many2one',                obj="hr.employee",store = { 'hr.payroll.main.archive' : (lambda self,cr,uid,ids,ctx={}:ids, ['arch_id','net'], 10),}),
    }

    _defaults = {
        'basic_salary': 0.0,
        'total_allowance': 0.0,
        'zakat': 0.0,
        'tax' : 0.0,
        'allowances_tax' : 0.0,
        'total_deduction': 0.0,
        'net' : 0.0
    }

#----------------------------------------
#Allowance Deduction Archive
#----------------------------------------           
class hr_allowance_deduction_archive(osv.osv):

    _name = "hr.allowance.deduction.archive"
    _description = "Allowance Deduction Archive"
    _columns = {
         'allow_deduct_id': fields.many2one('hr.allowance.deduction', 'Allowance/Deduction', required=True, readonly=True , ondelete="restrict", select=1),
         'type':fields.related('allow_deduct_id', 'name_type', type='selection', selection=[('allow', 'Allowance'), ('deduct', 'Deduction')], readonly=True, store=True, string='Type'),
         'amount' :fields.float("Amount", digits_compute=dp.get_precision('Payroll'), required=True, readonly=True),
         'tax_deducted' :fields.float("Tax Deducted", digits_compute=dp.get_precision('Payroll'), required=True, readonly=True),
         'imprint' :fields.float("Imprint", digits_compute=dp.get_precision('Payroll'), required=False, readonly=True),
         'main_arch_id' : fields.many2one('hr.payroll.main.archive', 'Payroll', required=True, ondelete='cascade' , select=1),
         'remain_amount' :fields.float("Amount", digits_compute=dp.get_precision('Payroll'), readonly=True),
          'active' :fields.boolean('Active')
    }
    _defaults = {
        'active': True
    }

    def delete_archive_scheduler_fun(self, cr, uid, ids=None, use_new_cursor=False, context=None):
       """Scheduler to delete archive
       @return True
       """
       print "REEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEest"
       cr.execute("delete from hr_allowance_deduction_archive where amount=0 and active is False")
       return True


#----------------------------------------
#Employee exempt tax 
#----------------------------------------
class hr_employee_exempt_tax(osv.osv):
    _name = "hr.employee.exempt.tax"
    _description = "Employee Exemption From Tax"
    _columns = {
        'employee_id' :fields.many2one("hr.employee", 'Employee', readonly=True, domain="[('state','=','approved')]"),
        'company_id' : fields.many2one('res.company', 'Company', readonly=True),
        'date':fields.date("Date", readonly=True),
        'birth_date':fields.date("Birthday Date", readonly=True),
        'employment_date':fields.date("Employment Date", readonly=True),
        'state':fields.selection([('draft', 'Draft'), ('approved', 'Approved'), ], "State", readonly=True),
    }

    _defaults = {
        'state': 'draft',
    }

    _sql_constraints = [
          ('name_unique', 'unique(employee_id)', 'Cannot Exempt Tax Employee more Than once for same employee!'),
        ]

    def approve_exempted(self, cr, uid, ids, context=None):
        """Method that exemptes employee from tax it changes the state to 'approved' and  updating hr.employee.
	       @return: Boolean True 
        """
        employee_obj = self.pool.get('hr.employee')
        for tax in self.browse(cr, uid, ids, context=context):
            employee_obj.write(cr, uid, [tax.employee_id.id], {'tax_exempted':True})
        return  self.write(cr, uid, ids, {'state':'approved'})

    def unlink(self, cr, uid, ids, context=None):
        for e in self.browse(cr, uid, ids):
            if e.state != 'draft':
                raise osv.except_osv(_('Warning!'), _('You Cannot Delete an Employee Exempt Tax Record Which Is Not In Draft State !'))
        return super(osv.osv, self).unlink(cr, uid, ids, context)  

#----------------------------------------
#salary batch 
#----------------------------------------
class hr_salary_batch(osv.osv):
    _name = "hr.salary.batch"
    _description = "Salary Batch"
    _columns = {
        'responsible_id' : fields.many2one('hr.employee', "Responsible Officer" , readonly=True,  ),
        'batch_id' : fields.many2one('hr.employee.category', 'Batch', readonly=True),
        'salary_adden_id' : fields.many2one('hr.employee.salary.addendum', 'Salary / Addendum', readonly=True, ondelete='cascade'),
        'batch_total' :fields.integer("Batch Total", required=True , readonly=True),
        'state':fields.selection([('draft','Draft'),('compute','computed'),('approve','Approved'),
                                  ('transferred', 'Transferred'),('cancel','cancelled')],"State", readonly=True),
    }

    _defaults = {
        'state': 'draft',
        'batch_total':0,
    }

    _sql_constraints = [
          ('name_unique', 'unique(employee_id)', 'Cannot Exempt Tax Employee more Than once for same employee!'),
        ]


    def compute_batch(self, cr, uid, ids, context = {}):
        """Compute salary/addendum for all employees in specific the batch month.
           @return: Dictionary 
        """
        for rec in self.browse(cr, uid, ids):
            ctx = context.copy()
            ctx.update({'salary_batch_id': rec.id })
            self.pool.get('hr.employee.salary.addendum').compute(cr, uid, [rec.salary_adden_id.id],ctx)
        return self.write(cr, uid, ids, { 'state': 'compute'}, context=context)

    def rollback_batch(self, cr, uid, ids, context = None):
        """delete records from main archive when rolback a calculated batch salary or addendum.
           @return: dictionary   
        """
        for rec in self.browse(cr, uid, ids):
            ctx = context.copy()
            ctx.update({'salary_batch_id': rec.id })
            self.pool.get('hr.employee.salary.addendum').rollback(cr, uid, [rec.salary_adden_id.id],ctx)
        self.write(cr, uid, ids, { 'state': 'draft'}, context=context)

    def approve_batch(self, cr, uid, ids, context = None):
        return self.write(cr, uid, ids, { 'state': 'approve'}, context=context)


    def action_cancel_batch(self, cr, uid, ids, context=None):
        for rec in self.browse(cr, uid, ids):
            emp_ids = [emp.id for emp in rec.batch_id.employee_ids ]
            ctx = context.copy()
            ctx.update({'employee_ids': emp_ids })
            self.pool.get('hr.employee.salary.addendum').action_cancel(cr, uid, [rec.salary_adden_id.id],ctx)
        self.write(cr, uid, ids, {'state':'cancel'}, context=context)      
        return True

    def action_cancel_draft_batch(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {'state':'draft'})        

    def unlink(self, cr, uid, ids, context=None):
        if not context.get('allow_delet') :
            for rec in self.browse(cr,uid, ids):
                if rec.state!='draft':
                    raise osv.except_osv(_('Warning!'), _('Sorry you Cannot delete salary batch that is not in draft state !'))
        return super(hr_salary_batch, self).unlink(cr, uid, ids, context)  
    
class hr_payroll_holidays(osv.osv):
    _name = "hr.payroll.holidays"
    _columns = {
        'employee_id' :fields.many2one("hr.employee", 'Employee', readonly=True, domain="[('state','=','approved')]"),
        'status_id' : fields.many2one("hr.holidays.status", 'Company', readonly=True),
        'holiday_id':fields.date("hr.holidays", readonly=True),
        'type':fields.selection([('paied', 'Paied'), ('unpaied', 'Un paied'), 
                                         ('customized', 'Customized')], 'Payroll', required=True),
         'main_arch_id' : fields.many2one('hr.payroll.main.archive', 'Payroll', required=True),
        'days':fields.integer("Days", readonly=True),
         
                
    }
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


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
