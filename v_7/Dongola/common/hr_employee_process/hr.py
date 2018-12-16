# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################
from datetime import datetime
import time
from openerp.osv import fields, osv, orm
from openerp.tools.translate import _
from openerp import netsvc

'''
    looking for last record of an employee in passed model_name then set the value of field is_last to False
'''
def edit_last_employee_arch(cr , uid , model_obj, employee_id,context=None):
        arch_ids = model_obj.search(cr , uid , [('employee_id' , '=' , employee_id) , ('is_last' , '=' , True)],context=context)
        if arch_ids :
            model_obj.write(cr , uid , arch_ids , {'is_last' : False})


class HR_Movements(osv.Model):
    _inherit = "hr.process.archive"

    def onchange_reference(self, cr, uid, ids, reference, employee_id, context=None):
        return {}
    def _check_reference(self, cr, uid, ids, context=None):
        return True

    def unlink(self , cr , uid , ids , context=None):
        for i in self.browse(cr , uid , ids):
            if i.state != 'draft':
                raise osv.except_osv(_('warning') , _('You Connot delete records not in Draft state !!'))
        return super(HR_Movements , self).unlink(cr , uid , ids , context)

    def _check_approve_date(self, cr, uid, ids, context=None):
        for i in self.browse(cr , uid , ids):
            if i.approve_date and i.date > i.approve_date:
                return False
        return True

    _constraints = [
        (_check_approve_date , 'approve date must be same or after than date' , ['approve_date' , 'date']) ,
    ]

    _defaults = {
        #'date': time.strftime('%Y-%m-%d'),
        'state': 'draft',
    }

class employee_movements_department(HR_Movements):
    _name = "hr.movements.department"
    _columns = {
        'employee_salary_scale' : fields.many2one('hr.salary.scale' , required=False) ,
        'description' : fields.text('Description') ,
        'reference' : fields.many2one('hr.department' , string="New Department" , required=True) , 
        'last_department_id' : fields.many2one('hr.department' , string="Previous") , 
        'state':fields.selection([ ('draft','Draft'),('approved','Approved')] ,'Status' ,select=True, readonly=True),                                       
        'is_last' : fields.boolean('Last Archive'),
        'new_company_id' : fields.many2one('res.company' , string="Company"),
        'prev_company_id' : fields.many2one('res.company' , string="Company"),
    
    }

    _defaults = {
        'state': 'draft',
    }


    def set_to_draft(self, cr , uid , ids , context=None):
        for obj in self.browse(cr, uid, ids):
            if not obj.is_last :
               raise orm.except_orm(_('Warning'), _("Connot Edit this record because it is not the last record for this employee")) 
            else:
                emp = self.pool.get('hr.employee')
                emp.write(cr, uid, [obj.employee_id.id], { 'department_id': obj.last_department_id.id , 'company_id' : obj.prev_company_id.id})
                user_id = obj.employee_id.user_id.id
                user = self.pool.get('res.users')
                user.write(cr , uid , [user_id] , {'company_ids' : [(6,0,[obj.prev_company_id.id])] , 'company_id' : obj.prev_company_id.id})            
                return self.write(cr , uid , ids , {'state' : 'draft' , 'is_last' : False , 'approve_date' : False})

    def name_get(self, cr, uid, ids, context=None):
        key = 'movements department'
        if context and 'lang' in context:
            translation_obj = self.pool.get('ir.translation')
            translation_ids = translation_obj.search(
                cr, uid, [('src', '=', key), ('lang', '=', context['lang'])], context=context)
            translation_recs = translation_obj.read(
                cr, uid, translation_ids, [], context=context)
            
            key = translation_recs and translation_recs[0]['value'] or key
        return ids and [(item.id, "%s-%s-%s" % ( key , item.employee_id.name, item.reference.name_get()[0][1])) for item in self.browse(cr, uid, ids, context=context)] or []


    def do_approve(self, cr, uid, ids, context=None):
        for obj in self.browse(cr , uid , ids):
            edit_last_employee_arch(cr , uid , self , obj.employee_id.id)
            emp_obj = self.pool.get('hr.employee')
            user_id = obj.employee_id.user_id.id
            user = self.pool.get('res.users')
            user.write(cr , uid , [user_id] , {'company_ids' : [(6,0,[obj.new_company_id.id])] , 'company_id' : obj.new_company_id.id})           
            if obj.employee_id.company_id.id != obj.new_company_id.id:
               emp_obj.write(cr , uid , [obj.employee_id.id] , {"department_id" : obj.reference.id , 'company_id' : obj.new_company_id.id,'location_id':False,'address_id':False})
            elif obj.employee_id.company_id.id == obj.new_company_id.id:
               emp_obj.write(cr , uid , [obj.employee_id.id] , {"department_id" : obj.reference.id , 'company_id' : obj.new_company_id.id})
            vals = {'state' : 'approved' , 'is_last' : True }
            if not obj.approve_date :
                vals['approve_date'] = time.strftime('%Y-%m-%d')
            return self.write(cr , uid , ids , vals)

    def do_approve_with_date(self , cr , uid , ids , approve_date , context=None):        
        if approve_date :
            self.write(cr , uid , ids , {'approve_date' : approve_date})
        return self.do_approve(cr , uid , ids , context)

    def _check_reference(self, cr, uid, ids, context=None):
        pass

    def onchange_company(self, cr, uid, ids, comp_id,context={}):
        return {
            'domain' : {
                'reference' : [('company_id' , '=' , comp_id)]
            }
        }

    def onchange_employee(self, cr, uid, ids, emp_id,context={}):
        #employee_type domain
        if emp_id:
            emp_obj = self.pool.get('hr.employee')
            emp = emp_obj.browse(cr , uid , [emp_id])[0]
            comp_id = emp.company_id.id 
            ref_id = emp.department_id.id
            return {
                'value' : {
                    'previous' : emp.department_id.name ,
                    'last_department_id' : emp.department_id.id ,
                    'employee_salary_scale' : emp.payroll_id.id ,
                    'reference' : None , 
                    'company_id' : comp_id , 
                    'new_company_id' : comp_id , 
                    'prev_company_id' : comp_id , 
                } ,
                'domain' : {              
                    'reference' : [('id' , '!=' , ref_id)] , 
                }
            }
        return {}

    def get_corporation(self , cr , uid ,  dep_id , context=None):
        dep_pool = self.pool.get('hr.department')
        dep = dep_pool.browse(cr , uid , [dep_id])[0]
        flag = True
        current = dep
        while current :
            if current.cat_id :
                if current.cat_id.category_type == 'corp' :
                    return current.id
            current = current.parent_id
        return False

    def create(self , cr , uid , vals , context=None):
        prev = self.pool.get('hr.employee').browse(cr , uid , [vals['employee_id']])[0].department_id
        if prev:
            vals['previous'] = prev.name
            vals['last_department_id'] = prev.id
        return super(employee_movements_department,self).create(cr , uid , vals , context)


class employee_movements_job(HR_Movements):
    _name = "hr.movements.job"
    _columns = {
        'employee_salary_scale' : fields.many2one('hr.salary.scale' , required=False) ,
        'description' : fields.text('Description') ,
       'reference' : fields.many2one('hr.job' , string="New Job" , required=True) , 
        'last_job_id' : fields.many2one('hr.job' , string="Previous") , 
        'is_last' : fields.boolean('Last Archive'),
    }

    def name_get(self, cr, uid, ids, context=None):
        key = 'movements job'
        if context and 'lang' in context:
            translation_obj = self.pool.get('ir.translation')
            translation_ids = translation_obj.search(
                cr, uid, [('src', '=', key), ('lang', '=', context['lang'])], context=context)
            translation_recs = translation_obj.read(
                cr, uid, translation_ids, [], context=context)
            
            key = translation_recs and translation_recs[0]['value'] or key
        return ids and [(item.id, "%s-%s-%s" % ( key , item.employee_id.name, item.reference.name_get()[0][1])) for item in self.browse(cr, uid, ids, context=context)] or []

    def set_to_draft(self, cr , uid , ids , context=None):
        for obj in self.browse(cr, uid, ids):
            if not obj.is_last :
               raise orm.except_orm(_('Warning'), _("Connot Edit this record because it is not the last record for this employee")) 
            else:
                emp = self.pool.get('hr.employee')
                emp.write(cr, uid, [obj.employee_id.id], { 'job_id': obj.last_job_id.id})
                return self.write(cr , uid , ids , {'state' : 'draft' , 'is_last' : False , 'approve_date' : False})

    def do_approve(self, cr, uid, ids, context=None):
        for obj in self.browse(cr , uid , ids):
            edit_last_employee_arch(cr , uid , self ,obj.employee_id.id )
            emp_obj = self.pool.get('hr.employee')
            emp_obj.write(cr , uid , [obj.employee_id.id] , {"job_id" : obj.reference.id})
            vals = {'state' : 'approved' , 'is_last' : True}
            if not obj.approve_date :
                vals['approve_date'] = time.strftime('%Y-%m-%d')
            return self.write(cr , uid , ids , vals)

    def do_approve_with_date(self , cr , uid , ids , approve_date , context=None):
        
        if approve_date :
            self.write(cr , uid , ids , {'approve_date' : approve_date})
        return self.do_approve(cr , uid , ids , context)


    def onchange_employee(self, cr, uid, ids, emp_id,context={}):
        #employee_type domain
        if emp_id:
            emp_obj = self.pool.get('hr.employee')
            emp = emp_obj.browse(cr , uid , [emp_id])[0]
            ref_id = emp.job_id.id
            return {
                'value' : {
                    'previous' : emp.job_id.name ,
                    'last_job_id' : emp.job_id.id ,
                    'employee_salary_scale' : emp.payroll_id.id , 
                } ,
                'domain' : {              
                    'reference' : [('id' , '!=' , ref_id)] , 
                }
            }
        return {}

    def create(self , cr , uid , vals , context=None):
        job_id = self.pool.get('hr.employee').browse(cr , uid , [vals['employee_id']])[0].job_id
        vals['last_job_id'] = job_id.id
        vals['previous'] = job_id.name
        return super(employee_movements_job , self).create(cr , uid , vals , context)

class employee_movements_promotion(HR_Movements):
    _name = "hr.movements.degree"
    _columns = {
        'employee_salary_scale' : fields.many2one('hr.salary.scale' , required=False) ,
        'description' : fields.text('Description') ,
        'reference' : fields.many2one('hr.salary.degree' , string="New Degree" , required=True) , 
        'process_type' : fields.selection([('promotion' , 'Promotion') , ('isolate' , 'Isolataion')]),
        'new_scale_id' : fields.many2one('hr.salary.scale' , string='Salary Scale') ,
        'new_bonuse_id' : fields.many2one('hr.salary.bonuses' , string='Bonuse'),
        'last_bonus_id' : fields.many2one('hr.salary.bonuses' , string='Previous Bonus'),
        'last_degree_id' : fields.many2one('hr.salary.degree' , string='Previous Degree'),
        'is_last' : fields.boolean('Last Archive'),
        'last_bonus_date' : fields.date("Last Bonus Date") ,
        'last_promo_date' : fields.date("Last Promotion Date"),
    }

    def set_to_draft(self, cr , uid , ids , context=None):
        for obj in self.browse(cr, uid, ids):
            if not obj.is_last :
               raise orm.except_orm(_('Warning'), _("Connot Edit this record because it is not the last record for this employee")) 
            else:
                vals = {
                    'bonus_id' : obj.last_bonus_id.id ,
                    'degree_id' : obj.last_degree_id.id ,
                    'payroll_id' : obj.employee_salary_scale.id ,
                    'bonus_date' : obj.last_bonus_date ,
                    'promotion_date' : obj.last_promo_date ,
                }
                emp = self.pool.get('hr.employee')
                emp.write(cr, uid, [obj.employee_id.id], vals)
                return self.write(cr , uid , ids , {'state' : 'draft' , 'is_last' : False , 'approve_date' : False})

    def name_get(self, cr, uid, ids, context=None):
        key = 'movements degree'
        if context and 'lang' in context:
            translation_obj = self.pool.get('ir.translation')
            translation_ids = translation_obj.search(
                cr, uid, [('src', '=', key), ('lang', '=', context['lang'])], context=context)
            translation_recs = translation_obj.read(
                cr, uid, translation_ids, [], context=context)
            
            key = translation_recs and translation_recs[0]['value'] or key
        return ids and [(item.id, "%s-%s-%s" % ( item.process_type , item.employee_id.name, item.reference.name_get()[0][1])) for item in self.browse(cr, uid, ids, context=context)] or []

    def do_approve(self, cr, uid, ids, context=None):
        for obj in self.browse(cr , uid , ids):
            obj_vals = {}
            if not obj.approve_date :
                obj_vals['approve_date'] = time.strftime('%Y-%m-%d')
            edit_last_employee_arch(cr , uid , self ,obj.employee_id.id)
            emp_obj = self.pool.get('hr.employee')
            vals = {"degree_id" : obj.reference.id , "payroll_id" : obj.new_scale_id.id ,
             "bonus_id" : obj.new_bonuse_id.id,
             'bonus_date' : obj.approve_date or time.strftime('%Y-%m-%d')  ,
             'promotion_date' : obj.approve_date or time.strftime('%Y-%m-%d')  ,
              }
            emp_obj.write(cr , uid , [obj.employee_id.id] , vals)
            obj_vals.update({
                'state' : 'approved' , 
                'is_last' : True , 
             })
            return self.write(cr , uid , ids , obj_vals)

    def do_approve_with_date(self , cr , uid , ids , approve_date , context=None):
        
        if approve_date :
            self.write(cr , uid , ids , {'approve_date' : approve_date})
        return self.do_approve(cr , uid , ids , context)

    def onchange_employee(self, cr, uid, ids, emp_id,process_type ,context={}):
        res = {}
        if emp_id :
            emp_obj = self.pool.get('hr.employee')
            emp = emp_obj.browse(cr , uid , [emp_id])[0]
            res['value'] = {
                'employee_salary_scale' : emp.payroll_id.id ,
                'last_degree_id' : emp.degree_id and emp.degree_id.id or None ,
                'last_bonus_id' : emp.bonus_id and emp.bonus_id.id or None ,
                'reference' : None , 
                'new_bonuse_id' : None , 
                'new_scale_id' :  emp.payroll_id.id , 
                'last_promo_date' : emp.promotion_date , 
                'last_bonus_date' : emp.bonus_date , 
            }    
            degree_domain = [('payroll_id' , '=' , emp.payroll_id.id )]
            if process_type == 'promotion' :
                degree_domain.append(('sequence' , '<' , emp.degree_id.sequence ))
            elif process_type == 'isolate' :
                degree_domain.append(('sequence' , '>' , emp.degree_id.sequence ))
            res['domain'] = {'reference' : degree_domain}
        return res
        return res

    def onchange_salary(self, cr, uid, ids, emp_id,new_scale_id ,process_type ,context={}):
        res = {}
        emp_obj = self.pool.get('hr.employee')
        emp = emp_obj.browse(cr , uid , [emp_id])[0]
        degree_domain = [('payroll_id' , '=' , new_scale_id )]
        if process_type == 'promotion' :
            degree_domain.append(('sequence' , '<' , emp.degree_id.sequence ))
        elif process_type == 'isolate' :
            degree_domain.append(('sequence' , '>' , emp.degree_id.sequence ))
        #res['domain'] = {'reference' : degree_domain}
        res['value'] = {
            'reference' : None ,
            'new_bonuse_id' : None ,
        }
        return res

    def onchange_degree(self, cr, uid, ids, degree_id,process_type ,context={}):
        res = {}
        if degree_id :
            degree_obj = self.pool.get('hr.salary.degree').browse(cr , uid , [degree_id])[0]
            min_bonus =  min(degree_obj.bonus_ids , key=lambda x : x.sequence)
            res['value'] = {'new_bonuse_id' : min_bonus.id}
            #res['domain'] = {'new_bonuse_id' : [('degree_id' , '=' , degree_id)]}
        return res

    def create(self , cr , uid , vals , context=None):
        emp = self.pool.get('hr.employee').browse(cr , uid , [vals['employee_id']])[0]
        vals['employee_salary_scale'] = emp.payroll_id.id 
        vals['last_bonus_id'] = emp.bonus_id and emp.bonus_id.id or None
        vals['last_degree_id'] = emp.degree_id and emp.degree_id.id or None
        vals['previous'] = emp.degree_id.name
        return super(employee_movements_promotion , self).create(cr , uid , vals , context)

class employee_movements_bonus(HR_Movements):
    _name = "hr.movements.bonus"
    _columns = {
       'employee_salary_scale' : fields.many2one('hr.salary.scale' , required=False) ,
       'description' : fields.text('Description') ,
       'reference' : fields.many2one('hr.salary.bonuses' , string="New Bonus" , required=True) , 
       'last_bonus_id' : fields.many2one('hr.salary.bonuses' , string="Previous") ,
       'is_last' : fields.boolean('Last Archive') ,   
       'last_bonus_date' : fields.date("Last Bonus Date") ,
    }

    def set_to_draft(self, cr , uid , ids , context=None):
        for obj in self.browse(cr, uid, ids):
            if not obj.is_last :
               raise orm.except_orm(_('Warning'), _("Connot Edit this record because it is not the last record for this employee")) 
            else:
                vals = {
                    'bonus_id' : obj.last_bonus_id.id ,
                    'bonus_date' : obj.last_bonus_date ,
                } 
                emp = self.pool.get('hr.employee')
                emp.write(cr, uid, [obj.employee_id.id], vals)
                return self.write(cr , uid , ids , {'state' : 'draft' , 'is_last' : False , 'approve_date' : False})

    def name_get(self, cr, uid, ids, context=None):
        key = 'movements bonus'
        if context and 'lang' in context:
            translation_obj = self.pool.get('ir.translation')
            translation_ids = translation_obj.search(
                cr, uid, [('src', '=', key), ('lang', '=', context['lang'])], context=context)
            translation_recs = translation_obj.read(
                cr, uid, translation_ids, [], context=context)
            
            key = translation_recs and translation_recs[0]['value'] or key
        return ids and [(item.id, "%s-%s-%s" % ( key , item.employee_id.name, item.reference.name_get()[0][1])) for item in self.browse(cr, uid, ids, context=context)] or []


    def do_approve(self, cr, uid, ids, context=None):
        for obj in self.browse(cr , uid , ids):
            #print '\n\n *********** ' ,obj.last_bonus_date
            obj_vals = {}
            if not obj.approve_date :
                obj_vals['approve_date'] = time.strftime('%Y-%m-%d')
            edit_last_employee_arch(cr , uid , self ,obj.employee_id.id)
            emp_obj = self.pool.get('hr.employee')
            emp_obj.write(cr , uid , [obj.employee_id.id] , {"bonus_id" : obj.reference.id , 'bonus_date' : obj.approve_date or time.strftime('%Y-%m-%d')})
            obj_vals.update({'state' : 'approved' , 'is_last' : True}) 
            return self.write(cr , uid , ids , obj_vals)
    def do_approve_with_date(self , cr , uid , ids , approve_date , context=None):
        
        if approve_date :
            self.write(cr , uid , ids , {'approve_date' : approve_date})
        return self.do_approve(cr , uid , ids , context)
        
    def onchange_employee(self, cr, uid, ids, emp_id,context={}):
        res = {}        
        if emp_id:
            emp_obj = self.pool.get('hr.employee')
            emp = emp_obj.browse(cr , uid , [emp_id])[0]
            ref = emp.bonus_id
            res['value'] = {
                'last_bonus_id' : ref.id ,
                'previous' : ref.name ,
                'reference' : None ,
                'last_bonus_date' : emp.bonus_date , 
            }
            print "\n\n\n\n " , emp.bonus_date
            dom = [('degree_id' , '=' , emp.degree_id.id) , ('sequence' , '>' , ref.sequence)]
            res['domain'] = {'reference' : dom}
        return res

    def create(self , cr ,uid , vals , context=None):
        emp = self.pool.get('hr.employee').browse(cr , uid , [vals['employee_id']])[0]
        vals['last_bonus_id'] = emp.bonus_id.id
        vals['previous'] = emp.bonus_id.name
        return super(employee_movements_bonus , self).create(cr , uid , vals , context)

class hr_employment_termination(osv.Model):

    _inherit = "hr.employment.termination"
    _columns = {
        'state': fields.selection([('draft', 'Draft'), ('confirmed' , 'Confirmed'), ('refuse', 'Out Of Service'), ('calculate', 'Calculated'),
                                   ('transfer', 'Transferred'), ], 'State', readonly=True),
    }

    def do_confirm(self, cr, uid, ids, context=None):
        for record in self.browse(cr, uid, ids):
            self.pool.get('hr.employee').write(cr, uid, [record.employee_id.id], {'end_date': record.dismissal_date})
            record.write({'state' : 'confirmed'})
        return True


    '''
        check if an employee has a computed salary in passed month
        @param employee_id : the employee id
        @param date : date string ex : 10-01-2020
        @return True if has a computed salary
    '''

    def check_employee_salary(self, cr, uid, employee_id, date):
        df = datetime.strptime(date, '%Y-%m-%d')
        year = df.year
        month = df.month
        search_condition = [('employee_id', '=', employee_id),
                            ('month', '=', month), ('year', '=', year)]
        salary = self.pool.get('hr.payroll.main.archive').search(cr, uid, search_condition)
        if salary:
            return True
        return False


    def do_terminate(self, cr, uid, ids, context=None):
        for record in self.browse(cr, uid, ids):
            if self.check_employee_salary(cr, uid, record.employee_id.id, record.dismissal_date):
                wf_service = netsvc.LocalService("workflow")
                wf_service.trg_validate(uid, 'hr.employee', record.employee_id.id, 'refuse', cr)
                record.write({'state': 'refuse'})
            else:
                raise osv.except_osv(_('ERROR'), _(
                    'Must compute employee salary before terminate his service!'))
        return True
