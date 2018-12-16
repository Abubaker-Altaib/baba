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

#----------------------------------------
#Employee delegation
#----------------------------------------
class hr_employee_delegation(osv.Model):
    _inherit = "hr.employee.delegation"
    _columns = {
        'destination' : fields.many2one('hr.department', string="Destination", required=True,readonly=True, states={'draft':[('readonly',False)]}),
        'destin' : fields.many2one("process.destin",'Destination',required=True,readonly=True, states={'draft':[('readonly',False)]}),
    }
    

class employee_family(osv.Model):

    _inherit = "hr.employee.family"
    _columns = {
        'card_no': fields.char("Card Number", size=64),
        'card_state': fields.selection([('active', 'Active'), ('not_active', 'Not Active')], 'State'),
    }

    _defaults = {
        'card_state': 'active',
    }


class hr_military_training_category(osv.Model):
    _name = "hr.military.training.category"
    _columns = {
        'code': fields.char("Code", size=64),
        'name': fields.char("Name", required=True, size=64),
    }

    _sql_constraints = [
        ('model_uniq', 'unique(name,model_id)', _(
            'The Model Must Be Unique For Each Name!')),
    ]


class hr_military_training_place(osv.Model):
    _name = "hr.military.training.place"
    _columns = {
        'code': fields.char("Code", si0ze=64),
        'name': fields.char("Name", required=True, size=64),
    }

    _sql_constraints = [
        ('model_uniq', 'unique(name,model_id)', _(
            'The Model Must Be Unique For Each Name!')),
    ]


class hr_military_training(osv.Model):
    _name = 'hr.military.training'
    _columns = {
        'type': fields.many2one('hr.military.training.category', string="Type", required=True),
        'place': fields.many2one('hr.military.training.place', string="Place", required=True),
        'start_date': fields.date('Start Date', required=True),
        'end_date': fields.date('End Date', required=True),
        'employee_id': fields.many2one('hr.employee', string="Employee"),

    }


class hr_service_state(osv.Model):
    _name = 'hr.service.state'
    _columns = {
        'code': fields.char("Code", size=64),
        'name': fields.char("Name", required=True, size=64),
        'type': fields.selection([('specific' , 'Specified') , ('takeout' , 'Takeout')] , string="Type"),
        'inside_corp' : fields.boolean('Movements inside Corporation only') ,
    }
    _default = {
        'type' : 'specific'
    }

    _sql_constraints = [
        ('model_uniq', 'unique(name,model_id)', _(
            'The Model Must Be Unique For Each Name!')),
    ]


class hr_service_end_reason(osv.Model):
    _name = 'hr.service.end.reason'
    _columns = {
        'code': fields.char("Code", size=64),
        'name': fields.char("Name", required=True, size=64),
    }

    _sql_constraints = [
        ('model_uniq', 'unique(name,model_id)', _(
            'The Model Must Be Unique For Each Name!')),
    ]


class hr_service_state_archive(osv.Model):
    _name = 'hr.service.state.archive'
    _columns = {
        'employee_id': fields.many2one('hr.employee', string="Employee", required=True , domain=[('state' , '=' , 'approved')]),
        'current_state_id': fields.many2one("hr.service.state", string="Currrent State"),
        'new_state_id': fields.many2one("hr.service.state", string="New State"),
        'state': fields.selection([('draft', 'Draft'), ('done', 'Done')], string="State", required=True),
        'process_date': fields.date('Date', required=True),
        'reason' : fields.text('Reason' , size=64) ,
        'takeout' : fields.boolean('Takeout') ,
        'is_last' : fields.boolean('Last Archive') ,
    }

    def on_change_state(self , cr, uid ,ids , state_id , context=None):
        res = {}
        if state_id :
            state_obj = self.pool.get('hr.service.state').browse(cr , uid , [state_id])[0]
            return {
                'value' : {
                    'takeout' : state_obj.type == 'takeout' ,
                }
            }
        
        return res

    _defaults = {
        'state': 'draft',
        'process_date': time.strftime('%Y-%m-%d'),
        'is_last' : False ,
    }

    '''
        looking for the last service.state.archive record for an employee 
        and set value of  is_last to false. 
    '''
    def edit_last_employee_arch(self , cr , uid , employee_id,context=None):
       # state_arch_model = self.pool.get('hr.service.state.archive')
        arch_ids = self.search(cr , uid , [('employee_id' , '=' , employee_id) , ('is_last' ,'=' , True)],context=context)
        if arch_ids :
            self.write(cr , uid , arch_ids , {'is_last' : False})


    def confirm_new_state(self, cr, uid, ids, context=None):
        emp = self.pool.get('hr.employee')
        for obj in self.browse(cr, uid, ids):
            self.edit_last_employee_arch(cr , uid , obj.employee_id.id)
            emp.write(cr, uid, [obj.employee_id.id], {
                      'service_state_id': obj.new_state_id.id})
        self.write(cr, uid, ids, {'state': 'done' , 'is_last' : True})


    def set_to_draft(self, cr , uid , ids , context=None):
        for obj in self.browse(cr, uid, ids):
            if not obj.is_last :
               raise orm.except_orm(_('Warning'), _("Connot Edit this record because it is not the last record for this employee")) 
            else:
                emp = self.pool.get('hr.employee')
                emp.write(cr, uid, [obj.employee_id.id], { 'service_state_id': obj.current_state_id.id})
                return self.write(cr , uid , ids , {'state' : 'draft' , 'is_last' : False})


    def onchange_employee(self, cr, uid, ids, employee_id, context=None):
        emp = self.pool.get('hr.employee').browse(cr, uid, [employee_id])[0]
        state_ids = self.pool.get('hr.service.state').search(cr , uid , [('id' , '!=' , emp.service_state_id.id)])
        res = {
            'value': {
                'current_state_id': emp.service_state_id.id,
            },
        }
        if state_ids :
            res['domain'] = {'new_state_id' : [('id' , 'in' , state_ids)]}
        return res

    def create(self , cr , uid , vals , context=None):
        edit_last_employee_arch(cr , uid , self , vals['employee_id'])
        emp = self.pool.get('hr.employee').browse(cr, uid, [vals['employee_id']])[0]
        vals['current_state_id'] = emp.service_state_id.id
        return super(hr_service_state_archive, self).create(cr, uid, vals, context=context)


class hr_salary_degree_isolate(osv.Model):
    _name = "hr.salary.degree.isolate"
    _inherit = "hr.salary.degree"
    _table = 'hr_salary_degree'



class employee_process(osv.Model):
    _inherit = "hr.process.archive"
    _columns = {
        'employee_id': fields.many2one('hr.employee', "Employee", required=True, readonly=False ,select=True , change_default=True , states={'approved':[('readonly',True)]} , domain=[('state' , '=' , 'approved')]), 
        'employee_salary_scale': fields.many2one('hr.salary.scale', "Employee Salary Scale", size=64,  required=False, states={'approved':[('readonly',True)]}),
        'reference': fields.reference('Event Ref', selection=[
            ('hr.salary.degree', 'Promotion'),
            ('hr.salary.bonuses', 'Annual Bonus'),
            ('hr.salary.degree.isolate', 'Isolate'),
            ('hr.department', 'Department Transfer'),
            ('hr.job', 'Job Transfer')], size=128, required=False, states={'approved': [('readonly', True)]}),
    }

    def onchange_reference(self, cr, uid, ids, reference, employee_id, context=None):
        if reference and employee_id:
            (model_name, id) = reference.split(',')
            employee_obj = self.pool.get('hr.employee')
            emp = employee_obj.browse(cr, uid, employee_id, context=context)
            if model_name == 'hr.salary.degree.isolate':
                return {'value': {'previous': emp.degree_id.name, 'employee_salary_scale': emp.payroll_id.id}}
        return super(employee_process, self).onchange_reference(cr, uid, ids, reference, employee_id, context=context)

    def _check_reference(self, cr, uid, ids, context=None):
        for record in self.browse(cr, uid, ids, context=context):
            if record.state == 'done' : 
                return True
            elif record.state == 'draft':
                if record.reference._name == 'hr.salary.degree.isolate':
                    if record.reference.sequence >= record.employee_id.degree_id.sequence:
                        raise orm.except_orm(_('Warning'), _(
                            "You must choose a Lower degree !!"))
                elif record.reference._name == 'hr.salary.degree':
                    if record.reference.sequence <= record.employee_id.degree_id.sequence:
                        if record.process_type == 'isolate' : return True
                        raise orm.except_orm(_('Warning'), _(
                            "You must choose a higher degree !!"))
        return super(employee_process, self)._check_reference(cr, uid, ids, context=context)

    def create_new(self, cr, uid, ids, context=None):
        employee_obj = self.pool.get('hr.employee')
        for row in self.read(cr, uid, ids, context=context):
            (model_name, id) = row['reference'].split(',')
            if model_name == 'hr.salary.degree.isolate':
                employee_obj.write(cr, uid, [row['employee_id'][0]], {
                                   'degree_id': id, 'is_isolated': True})
                return self.write(cr, uid, ids, {'state': 'approved'})
            elif model_name == 'hr.salary.degree':
                employee_obj.write(cr, uid, [row['employee_id'][0]], {
                                   'is_isolated': False})
            return super(employee_process, self).create_new(cr, uid, ids, context=context)

    _constraints = [
        #(_check_reference, "You can not choose an employee's current department!", ['reference']),
    ]

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
        'date': time.strftime('%Y-%m-%d'),
        'state': 'draft',
    }

class employee_movements_department(HR_Movements):
    _name = "hr.movements.department"
    _columns = {
        'description' : fields.text('Description') ,
        'reference' : fields.many2one('hr.department' , string="New Department" , required=True) , 
        'last_department_id' : fields.many2one('hr.department' , string="Previous") , 
        'move_order_line_id' : fields.many2one('hr.move.order.line' , string="Move Order") ,
        'move_order_id' : fields.many2one('hr.move.order' , string="Move Order") ,  
        'state':fields.selection([ ('draft','Draft'),('approved','Approved')] ,'Status' ,select=True, readonly=True),                                       
        'is_last' : fields.boolean('Last Archive'),
        'join_date':fields.date(" Last Join Date", size=8 ),
        'old_data' : fields.boolean('Old Data'),
        'move_from_dep_date':fields.date("Date of transfer form department", size=8 ),
        'payroll_employee_id':fields.many2one('hr.department.payroll', 'Department of Payroll'),
        'old_payroll_employee_id':fields.many2one('hr.department.payroll', readonly=True, store=True, string='Old Department of Payroll'),
    }


    def set_to_draft(self, cr , uid , ids , context=None):
        for obj in self.browse(cr, uid, ids):
            if obj.move_order_id:
                if obj.move_order_id.state == 'draft':
                    self.pool.get('hr.move.order').unlink(cr,uid,[obj.move_order_id.id])
                else:
                    raise osv.except_osv(_('warning') , _('There is a Confirmed Move Order releted to this record, you must delete it before set the record to draft'))
            if not obj.is_last :
               raise orm.except_orm(_('Warning'), _("Connot Edit this record because it is not the last record for this employee")) 
            else:
                emp = self.pool.get('hr.employee')
                emp.write(cr, uid, [obj.employee_id.id], { 'department_id': obj.last_department_id.id, 'join_date': obj.join_date, 
                'payroll_employee_id': obj.old_payroll_employee_id and obj.old_payroll_employee_id.id or obj.employee_id.payroll_employee_id.id,})
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
            
            vals = {'state' : 'approved' , 'is_last' : True }
            if not obj.approve_date :
                vals['approve_date'] = time.strftime('%Y-%m-%d')
            
            emp_obj.write(cr , uid , [obj.employee_id.id] , {"department_id" : obj.reference.id, 'join_date':obj.approve_date or vals['approve_date'], 
                    'payroll_employee_id': obj.payroll_employee_id and obj.payroll_employee_id.id or obj.employee_id.payroll_employee_id.id,})

            if obj.move_order_line_id :
                self.pool.get('hr.move.order.line').write(cr , uid , [obj.move_order_line_id.id] , {'movement_id' : ids[0]})
                vals['move_order_id'] = obj.move_order_line_id.move_order_id.id
            return self.write(cr , uid , ids , vals)

    def do_approve_with_date(self , cr , uid , ids , approve_date , context=None):
        
        if approve_date :
            self.write(cr , uid , ids , {'approve_date' : approve_date})
        return self.do_approve(cr , uid , ids , context)

    def _check_reference(self, cr, uid, ids, context=None):
        pass

    def onchange_employee(self, cr, uid, ids, emp_id,context={}):
        #employee_type domain
        if emp_id:
            emp_obj = self.pool.get('hr.employee')
            emp = emp_obj.browse(cr , uid , [emp_id])[0]
            ref_id = emp.department_id.id
            return {
                'value' : {
                    'previous' : emp.department_id.name ,
                    'last_department_id' : emp.department_id.id ,
                    'employee_salary_scale' : emp.payroll_id.id ,
                    'move_order_line_id' : None , 
                    'reference' : None , 
                    'join_date': emp.join_date,
                    'old_payroll_employee_id': emp.payroll_employee_id.id,
                } ,
                'domain' : {              
                    'reference' : [('id' , '!=' , ref_id)] , 
                }
            }
        return {}

    def create_move_order(self, cr, uid, ids,context={}):
        dummy, view_id = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'hr_custom_military', 'hr_move_order_with_footer')
        res = {
                    'name': _('Move Order'),
                    'view_type': 'form',
                    'view_mode': 'form',
                    'view_id' : view_id ,
                    'res_model': 'hr.move.order',
                    'type': 'ir.actions.act_window',
                    'target': 'new',
                }
        for rec in self.browse(cr , uid , ids , context):
            if not rec.move_order_id :
                data = {
                    'default_move_order_line_ids' : [[0 , 0 , {'employee_id' : rec.employee_id.id ,'movement_id' : rec.id , 'type' : 'movement' , 'date' : rec.approve_date or rec.date}]] ,
                    'default_source' : rec.last_department_id.id,
                    'default_destination' : rec.reference.id,
                    'default_manger_id' : rec.reference.manager_id.name_related ,
                    'default_department_move_id' : rec.id ,
                    'default_type' : 'movement' ,
                    'default_move_date' : time.strftime('%Y-%m-%d'),
                    'default_out_source' : True ,
                    'movement_id' : rec.id ,
                }
                res['context'] = data
            else :
                res['res_id'] = rec.move_order_id.id
            return res 


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

    def _check_corporation(self, cr, uid, ids, context=None):
        for rec in self.browse(cr , uid , ids):
            if rec.employee_id.service_state_id.inside_corp :
                dep1 = self.get_corporation(cr , uid , rec.reference.id)
                dep2 = self.get_corporation(cr , uid , rec.last_department_id.id)
                if dep1 and dep2 :
                    return dep1 == dep2
                else: return False
            else : return True

    _constraints = [
        (_check_corporation,
         "Movements must be inside corporation only!", ['reference']),
    ]


class employee_movements_job(HR_Movements):
    _name = "hr.movements.job"
    _columns = {
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
        'description' : fields.text('Description') ,
        'reference' : fields.many2one('hr.salary.degree' , string="New Degree" , required=True) , 
        'process_type' : fields.selection([('promotion' , 'Promotion') , ('isolate' , 'Isolataion')]),
        'new_scale_id' : fields.many2one('hr.salary.scale' , string='Salary Scale') ,
        'new_bonuse_id' : fields.many2one('hr.salary.bonuses' , string='Bonuse'),
        'last_bonus_id' : fields.many2one('hr.salary.bonuses' , string='Previous Bonus'),
        'last_degree_id' : fields.many2one('hr.salary.degree' , string='Previous Degree'),
        'is_last' : fields.boolean('Last Archive'),
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
            edit_last_employee_arch(cr , uid , self ,obj.employee_id.id)
            emp_obj = self.pool.get('hr.employee')
            vals = {"degree_id" : obj.reference.id , "payroll_id" : obj.new_scale_id.id , "bonus_id" : obj.new_bonuse_id.id}
            if obj.process_type == "isolate" : vals['is_isolated'] = True
            emp_obj.write(cr , uid , [obj.employee_id.id] , vals)
            obj_vals = {'state' : 'approved' , 'is_last' : True} 
            if not obj.approve_date :
                obj_vals['approve_date'] = time.strftime('%Y-%m-%d')
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
                'last_degree_id' : emp.degree_id.id ,
                'last_bonus_id' : emp.bonus_id.id ,
                'reference' : None , 
                'new_bonuse_id' : None , 
                'new_scale_id' :  emp.payroll_id.id , 
            }
        return res

    def onchange_salary(self, cr, uid, ids, emp_id,new_scale_id ,process_type ,context={}):
        res = {}
        emp_obj = self.pool.get('hr.employee')
        emp = emp_obj.browse(cr , uid , [emp_id])[0]
        degree_domain = [('payroll_id' , '=' , new_scale_id )]
        if process_type == 'promotion' :
            degree_domain.append(('sequence' , '>' , emp.degree_id.sequence ))
        elif process_type == 'isolate' :
            degree_domain.append(('sequence' , '<' , emp.degree_id.sequence ))
        res['domain'] = {'reference' : degree_domain}
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
            res['domain'] = {'new_bonuse_id' : [('degree_id' , '=' , degree_id)]}
        return res

    def create(self , cr , uid , vals , context=None):
        emp = self.pool.get('hr.employee').browse(cr , uid , [vals['employee_id']])[0]
        vals['employee_salary_scale'] = emp.payroll_id.id ,
        vals['last_bonus_id'] = emp.bonus_id.id ,
        vals['last_degree_id'] = emp.degree_id.id
        vals['previous'] = emp.degree_id.name
        return super(employee_movements_promotion , self).create(cr , uid , vals , context)


class hr_service_end(osv.Model):
    _name = 'hr.service.end'
    _columns = {
        'employee_id': fields.many2one('hr.employee', string="Employee", required=True, domain=[('state', '=', 'approved')]),
        'state': fields.selection([('draft', 'Draft'), ('done', 'Confirmed'), ('refused', 'Refused')], 'State'),
        'end_date': fields.date('Service End Date', required=True),
        'department_id': fields.related('employee_id', 'department_id', relation='hr.department',  type='many2one',  string='Department', readonly=True),
        'reason_id': fields.many2one('hr.service.end.reason', string="Reason", required=True),
        'reason': fields.text('Reason', help="", states={'done': [('readonly', True)]}),
        'decision_date': fields.date('decision Date'),
    }
    _defaults = {
        'end_date': time.strftime('%Y-%m-%d'),
        'state': 'draft',
    }

    def name_get(self, cr, uid, ids, context=None):
        key = 'service end'
        if context and 'lang' in context:
            translation_obj = self.pool.get('ir.translation')
            translation_ids = translation_obj.search(
                cr, uid, [('src', '=', key), ('lang', '=', context['lang'])], context=context)
            translation_recs = translation_obj.read(
                cr, uid, translation_ids, [], context=context)
            
            key = translation_recs and translation_recs[0]['value'] or key
        return ids and [(item.id, "%s-%s" % ( key , item.employee_id.name_get()[0][1])) for item in self.browse(cr, uid, ids, context=context)] or []


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
        print "##############  " , salary
        if salary:
            return True
        return False

    def do_confirm(self, cr, uid, ids, context=None):
        decision_date = time.strftime('%Y-%m-%d')
        for record in self.browse(cr, uid, ids):
            if self.check_employee_salary(cr, uid, record.employee_id.id, decision_date):
                self.pool.get('hr.employee').write(cr, uid, [record.employee_id.id], {
                    'end_date': decision_date, 'state': 'refuse'})
                wf_service = netsvc.LocalService("workflow")
                wf_service.trg_validate(uid, 'hr.employee', record.employee_id.id, 'refuse', cr)
                self.write(cr, uid, ids, {
                           'decision_date': decision_date, 'state': 'done', })
            else:
                raise osv.except_osv(_('ERROR'), _(
                    'Must compute employee salary before terminate his service!'))
        return True

class employee_movements_bonus(HR_Movements):
    _name = "hr.movements.bonus"
    _columns = {
       'description' : fields.text('Description') ,
       'reference' : fields.many2one('hr.salary.bonuses' , string="New Bonus" , required=True) , 
       'last_bonus_id' : fields.many2one('hr.salary.bonuses' , string="Previous") ,
       'is_last' : fields.boolean('Last Archive') ,   
    }

    def set_to_draft(self, cr , uid , ids , context=None):
        for obj in self.browse(cr, uid, ids):
            if not obj.is_last :
               raise orm.except_orm(_('Warning'), _("Connot Edit this record because it is not the last record for this employee")) 
            else:
                vals = {
                    'bonus_id' : obj.last_bonus_id.id ,
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
            edit_last_employee_arch(cr , uid , self ,obj.employee_id.id)
            emp_obj = self.pool.get('hr.employee')
            emp_obj.write(cr , uid , [obj.employee_id.id] , {"bonus_id" : obj.reference.id})
            obj_vals = {'state' : 'approved' , 'is_last' : True} 
            if not obj.approve_date :
                obj_vals['approve_date'] = time.strftime('%Y-%m-%d')
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
            }
            dom = [('degree_id' , '=' , emp.degree_id.id) , ('sequence' , '>' , ref.sequence)]
            res['domain'] = {'reference' : dom}
        return res

    def create(self , cr ,uid , vals , context=None):
        emp = self.pool.get('hr.employee').browse(cr , uid , [vals['employee_id']])[0]
        vals['last_bonus_id'] = emp.bonus_id.id
        vals['previous'] = emp.bonus_id.name
        return super(employee_movements_bonus , self).create(cr , uid , vals , context)


class hr_service_end_reason(osv.Model):
    _name = 'hr.medication.option'
    _columns = {
        'code': fields.char("Code", size=64),
        'name': fields.char("Name", required=True, size=64),
    }


class hr_employee_illness(osv.Model):
    _name = 'hr.employee.illness'
    _columns = {
        'transmission_id': fields.many2one('hr.employee.mission', string="Transmission"),
        'employee_id': fields.many2one('hr.employee', string="Employee", required=True, domain=[('state', '=', 'approved')]),
        'state': fields.selection([('draft', 'Draft'), ('done', 'Confirmed'), ('refused', 'Refused')], 'State'),
        'end_date': fields.date('Service End Date'),
        'med_option_id': fields.many2one('hr.medication.option', string="Doctor Decision"),
        'doctor_comment': fields.text('Doctor Decision Text', help="", states={'done': [('readonly', True)]}),
        'date': fields.date('decision Date', required=True),
        'illness': fields.char("Illness", required=True, size=64),
        'type' : fields.selection([('holiday' , 'Holiday') , ('transmission' , 'Transmission') ,('commision' , 'Commision')] , 'Type') ,
        'holiday_id': fields.many2one('hr.holidays', string="Holiday"  , domain=[('sick_leave' , '=' , 'True')]),
        'commision_id': fields.many2one('hr.commision', string="Commision"),
        'transmission_id': fields.many2one('hr.employee.mission', string="Transmission" , domain=[('type' , '=' , '3')]),
        'station' : fields.char('Station') ,
        'family' : fields.selection( [('wife' , 'For Wife') , ('son' , 'For Son') ,('daughter' , 'For Daughter') , ('father' , 'For Father') , ('mother' , 'For Mother')] , string="Family"),
    }
    _defaults = {
        'date': time.strftime('%Y-%m-%d'),
        'state': 'draft',
    }

    def name_get(self, cr, uid, ids, context=None):
        key = 'Illness'
        if context and 'lang' in context:
            translation_obj = self.pool.get('ir.translation')
            translation_ids = translation_obj.search(
                cr, uid, [('src', '=', key), ('lang', '=', context['lang'])], context=context)
            translation_recs = translation_obj.read(
                cr, uid, translation_ids, [], context=context)
            
            key = translation_recs and translation_recs[0]['value'] or key
        return ids and [(item.id, "%s-%s-%s" % ( key , item.employee_id.name, item.date)) for item in self.browse(cr, uid, ids, context=context)] or []


    def do_confirm(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {'state': 'done'})

    def set_to_draft(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {'state': 'draft'})


class hr_department_cat(osv.Model):

    _inherit = 'hr.department.cat'

    _columns = {
        'category_type': fields.selection([('organization', 'Organization'), ('department', 'Department'),
                                           ('aria', 'Aria'),
                                           ('section', 'Section') ,
                                           ('corp' , 'Coropration')], 'Category Type'),
    }


class hr_qualificationt(osv.Model):
    _name = 'hr.qualification.org'
    _columns = {
        'name' : fields.char('Name') ,
        'code' : fields.char('Code') ,
        'type' : fields.selection([('category' , 'Main Category') , ('element' , 'Branch Element')] , string="Type"),
        'category_id' : fields.many2one('hr.qualification.org' , string="Main Category"),
    }



class hr_employee_qualificationt(osv.Model):

    _inherit = 'hr.employee.qualification'

    _columns = {
        'organization' : fields.many2one('hr.qualification.org' , string="Organization", domain=[('type' , '=' , 'category')]) ,
        'org_unit' : fields.many2one('hr.qualification.org' , string="Organization Unit", domain=[('type' , '=' , 'element')]) ,
 
    }

    def onchange_org(self , cr , uid , ids , context=None):
        return {
            'value' : {
                'org_unit' : False ,
            },
        }

#inherit hr.qualification 
class hr_qualificationt(osv.Model):

    _inherit = 'hr.qualification'

    _columns = {
        'special': fields.boolean('Special'),
    }


class hr_employment_termination(osv.Model):
    _inherit = "hr.dismissal"
    _columns = {
        'martyrdom' : fields.boolean('Special for Martyrdom') ,
        'escape' : fields.boolean('Special for Escape') ,
    }


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

    def set_to_draft(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {'state': 'draft'})


class hr_employment_martyrdom(osv.Model):
    _inherit = "hr.employment.termination"
    _name = "hr.employee.martyrdom"
    _columns = {
        'martyrdom_place' : fields.char('Martyrdom Place') ,
        'burial_place' : fields.char('Burial Place') , 
        'dismissal_date' :fields.date("Martyrdom Date", size=8 ,readonly= True,required=True, states={'draft':[('readonly', False)]}),
        'dismissal_type' : fields.many2one('hr.dismissal', 'Termination Reason', required=True,readonly= True, states={'draft':[('readonly', False)]}),
        'martyrdom_reason' : fields.many2one('hr.employee.martyrdom.reason', 'Martyrdom Reason', required=True,readonly= True, states={'draft':[('readonly', False)]}),
        'father_state' : fields.selection( [('life' , 'Life') , ('dead' , 'Not Life')], string="Father state") , 
        'mother_state' : fields.selection( [('life' , 'Life') , ('dead' , 'Not Life')], string="Mother state") , 
        'comment' : fields.text('Comment') , 
        'wifes' : fields.text('Comment') , 
        'childeren' : fields.text('Comment') , 
        'number' : fields.char('Number') ,
    }


    _defaults = {
        'dismissal_type': lambda self, cr, uid, context: self.pool.get('hr.dismissal').search(cr, uid,[('martyrdom','=',True)],limit=1,context=context),
    }
    '''def do_confirm(self, cr, uid, ids, context=None):
        employee_termination_obj = self.pool.get('hr.employment.termination')
        for record in self.browse(cr, uid, ids):
            self.pool.get('hr.employee').write(cr, uid, [record.employee_id.id], {'end_date': record.dismissal_date})
            
            termination_id = employee_termination_obj.create(cr, uid, { 'employee_id': record.employee_id.id,
                                                                        'dismissal_date': record.dismissal_date,
                                                                        'dismissal_type': record.dismissal_type.id,
                                                                        'state' : 'confirmed'})
            record.write({'state' : 'confirmed'})
        return True'''

    def do_terminate(self, cr, uid, ids, context=None):
        for record in self.browse(cr, uid, ids):
            if self.check_employee_salary(cr, uid, record.employee_id.id, record.dismissal_date):
                employee_termination_obj = self.pool.get('hr.employment.termination')
                termination_id = employee_termination_obj.create(cr, uid, { 'employee_id': record.employee_id.id,
                                                                        'dismissal_date': record.dismissal_date,
                                                                        'dismissal_type': record.dismissal_type.id,
                                                                        'state' : 'refuse'})
               
                wf_service = netsvc.LocalService("workflow")
                wf_service.trg_validate(uid, 'hr.employee', record.employee_id.id, 'refuse', cr)
                record.write({'state': 'refuse'})
            else:
                raise osv.except_osv(_('ERROR'), _(
                    'Must compute employee salary before terminate his service!'))
        return True

    def set_to_draft(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {'state': 'draft'})

class hr_event_register(osv.Model):
    _name = 'hr.event'
    _columns = {
        'name' : fields.char('Name') ,
        'identity' : fields.char('Personal Identity') ,
        'type' : fields.selection([('inside' , 'Inside Unit') , ('outsite' , 'Outsite Unit')] , string="location" ,required=True) ,
        'state' : fields.selection([('draft' , 'Draft') , ('confirm' , 'Confirm')] , string="state") ,        
        'notes' : fields.text('Notes' , required=True) ,
        'date' : fields.datetime('Date' , required=True) ,
        'employee_id' : fields.many2one('hr.employee' , 'Employee') ,
    }
    _defaults = {
        'state' : 'draft' ,
    }

    def onchange_type(self , cr, uid ,ids , type , context=None):
        return {
            'value' : {
                'name' : False ,
                'identity' : False ,
                'employee_id' : False ,
            }
        }

    def onchange_emp(self , cr, uid ,ids , emp_id , context=None):
        try : 
            if emp_id :
                for i in self.pool.get('hr.employee').browse(cr , uid , [emp_id]) :
                    return {
                        'value' : {
                            'name' : i.name_related , 
                            'identity' : i.emp_code ,
                        }
                    }
            return {}
        except : return {}

    def do_confirm(self , cr , uid , ids , context=None):
        return self.write(cr , uid , ids , {'state' : 'confirm'})

    def do_draft(self , cr , uid , ids , context=None):
        return self.write(cr , uid , ids , {'state' : 'draft'})        

class hr_employment_martyrdom_reson(osv.Model):
    _name = "hr.employee.martyrdom.reason"
    _columns = {
        'name' : fields.char('Martyrdom Reason',required=True) ,
        #'medical_number' : fields.boolen('Require Medical Number') ,  
    }


class employee_freshment(osv.Model):
    _name = "hr.employee.freshment"
    _columns = {
		'employee_id' : fields.many2one('hr.employee' , 'Employee',required=True) , 
                'end_date' : fields.date('End Date' ) ,
                'start_date' : fields.date('Fresh Data') , 
                'reason' : fields.text('Reason' , required=True) ,
                'number' : fields.char("Number",required=True),
                'type' : fields.selection([('end' , 'End') , ('refresh' , 'Refresh')] , string="Type" ,required=True) ,
                'state' : fields.selection([('draft' , 'Draft') , ('confirm' , 'Confirm')] , string="State" ,readonly=True) ,
                'emp_type' : fields.selection([('contractor' , 'Contract') , ('from_out' , 'From Out')] , string="Employee Type") ,
    }

    _defaults = {
        'state' : 'draft' ,
    }

    def do_confirm(self , cr , uid , ids , context=None):
         for record in self.browse(cr, uid, ids):
             if record.start_date:
                    if record.start_date >= record.end_date:
		       raise orm.except_orm(_('Warning!'), _('The start date must be before end date'))
		    if record.start_date < record.employee_id.end_date:
		        raise orm.except_orm(_('Warning!'), _('The start date must be after employee end date'))
             elif record.end_date:
                 if record.end_date < record.employee_id.employment_date:
		        raise orm.except_orm(_('Warning!'), _('The end date must be after employee start date'))
             if record.type == 'refresh' and record.employee_id.state == 'approve':
                self.pool.get('hr.employee').write(cr, uid, [record.employee_id.id], {'end_date': record.end_date})
             elif record.type == 'refresh' and record.employee_id.state == 'refuse':
                 self.pool.get('hr.employee').write(cr, uid, [record.employee_id.id], {'end_date': record.end_date})
                 wf_service = netsvc.LocalService("workflow")
                 wf_service.trg_validate(uid, 'hr.employee', record.employee_id.id, 'approve', cr)
             elif record.type == 'end':
                 self.pool.get('hr.employee').write(cr, uid, [record.employee_id.id], {'end_date': record.end_date})
                 wf_service = netsvc.LocalService("workflow")
                 wf_service.trg_validate(uid, 'hr.employee', record.employee_id.id, 'refuse', cr)
         return self.write(cr , uid , ids , {'state' : 'confirm'})

    def onchange_emp(self , cr, uid ,ids , emp_id , context=None): 
         if emp_id :
                #raise orm.except_orm(_('Warning!'), _('Leave Limit is Once and Already Taken %s')%emp_id)
                for i in self.pool.get('hr.employee').browse(cr , uid , [emp_id]) :
                    return {
                        'value' : { 
                            'emp_type' : i.employee_type ,
                        }
                    }
         return {}

    '''def create(self, cr, uid, vals, context=None):
        for fresh in self.browse(cr, uid, ids):
            if fresh.start_date:
		    if fresh.start_date >= fresh.end_date:
		       raise orm.except_orm(_('Warning!'), _('The start date must be before end date'))
		    if fresh.start_date < fresh.employee_id.end_date:
		        raise orm.except_orm(_('Warning!'), _('The start date must be after employee end date'))
            elif fresh.end_date:
                 if fresh.end_date < fresh.employee_id.employment_date:
		        raise orm.except_orm(_('Warning!'), _('The end date must be after employee start date'))
        return super(hr_holidays_absence, self).create(cr, uid, vals, context=context)'''
