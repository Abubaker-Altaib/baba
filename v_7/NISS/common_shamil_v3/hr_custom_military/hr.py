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
from lxml import etree
from openerp import addons

'''
    looking for last record of an employee in passed model_name then set the value of field is_last to False
'''
def edit_last_employee_arch(cr , uid , model_obj, employee_id,context=None):
        arch_ids = model_obj.search(cr , uid , [('employee_id' , '=' , employee_id) , ('is_last' , '=' , True)],context=context)
        if arch_ids :
            model_obj.write(cr , uid , arch_ids , {'is_last' : False})
#----------------------------------------
#Employee category Inherit
#----------------------------------------
class hr_employee_category(osv.osv):

    _inherit = "hr.employee.category"
    _columns = {
        'belong_to' : fields.selection([ ('officer_affairs' , 'Officers affairs'),('soldier_affairs' , 'Soldiers affairs'),('oc' , 'OC')], string='Belong To'),
    }

#----------------------------------------
#Employee delegation Inherit
#----------------------------------------
class hr_employee_delegation(osv.Model):
    _inherit = "hr.employee.delegation"

    _columns = {
        'destination' : fields.many2one('hr.department', string="Destination",readonly=True, states={'draft':[('readonly',False)]}),
        'current_state_id': fields.many2one("hr.service.state", string="Currrent State"),
        'new_state_id': fields.many2one("hr.service.state", string="New State"),
        'new_state_id_level2': fields.many2one("hr.service.state", string="New State"),
        'new_state_id_level3': fields.many2one("hr.service.state", string="New State"),
        'delegation_to' : fields.char('delegation destination' , size=156) ,
        'payroll_state' : fields.char('Payroll State' , size=156) ,
        'type': fields.selection([('mandate','Mandate'),('loaned','Loaned'),('transferred','Transferred')] ,'Type',readonly=True, states={'draft':[('readonly',False)]} ),                                       
        'payroll_type':fields.selection([('paied', 'Paied'), ('unpaied', 'Unpaied'),('customized', 'Customized')], 'Payroll',readonly=True, states={'draft':[('readonly',False)]}),
        'reason' : fields.text('Reason' , size=64) ,
        'takeout' : fields.boolean('Takeout') ,
        'is_last' : fields.boolean('Last Archive') ,
        'level2' : fields.boolean('level2') ,
        'level3' : fields.boolean('level3') ,
    }

    _defaults = {
        'is_last' : False ,
        'level2' : False ,
        'level3' : False ,

    }

    def fields_view_get(self, cr, uid, view_id=None, view_type='form', context=None, toolbar=False, submenu=False):
        #override of fields_view_get to change the String of employee_id fields
        emp_obj=self.pool.get('hr.employee')
        belong_to=False
        if context is None:
            context={}
        res = super(hr_employee_delegation, self).fields_view_get(cr, uid, view_id=view_id, view_type=view_type, context=context, toolbar=toolbar, submenu=submenu)
        emp=emp_obj.search(cr, uid, [('user_id','=',uid)])
        employee = emp_obj.browse(cr, uid, emp and emp[0] or 0)
        for cat in (emp and employee.category_ids or []):
            if cat.belong_to:
                belong_to=cat.belong_to
        if belong_to:
            doc = etree.XML(res['arch'])
            for node in doc.xpath("//field[@name='employee_id']"):
                if belong_to == 'officer_affairs':
                    node.set('string', _('Officer'))
                elif belong_to == 'soldier_affairs':
                    node.set('string', _('Soldier'))
                else:
                    node.set('string', _('Soldier'))
            for node in doc.xpath("//label[@for='employee_id']"):
                if belong_to == 'officer_affairs':
                    node.set('string', _('Officer'))
                elif belong_to == 'soldier_affairs':
                    node.set('string', _('Soldier'))
                else:
                    node.set('string', _('Soldier'))
            res['arch'] = etree.tostring(doc)
        return res

    def onchange_employee(self, cr, uid, ids, employee_id, context=None):
        emp = self.pool.get('hr.employee').browse(cr, uid, [employee_id])[0]
        state_ids = self.pool.get('hr.service.state').search(cr , uid , [('id' , '!=' , emp.service_state_id.id),('state_type','=','in'),('level','in',['1',False])])
        res = {
            'value': {
                'current_state_id': emp.service_state_id.id,
            },
        }
        if state_ids :
            res['domain'] = {'new_state_id' : [('id' , 'in' , state_ids)]}
        return res
    
    def on_change_state(self , cr, uid ,ids , state_id , context=None):
        res = {}
        value={}
        service_obj = self.pool.get('hr.service.state')
        if state_id:
            state_obj = service_obj.browse(cr , uid , [state_id])[0]
            value['takeout']=state_obj.type == 'takeout' 
            if state_obj.level in ('1',False):
                state_ids = service_obj.search(cr , uid , [('level' , '=' , '2'),('parent_id','=',state_id)])
                if state_ids:
                    value['level2'] = True
                    value['new_state_id_level2'] = False
                    value['new_state_id_level3'] = False
            if state_obj.level == '2':
                state_ids = service_obj.search(cr , uid , [('level' , '=' , '3'),('parent_id','=',state_id)])
                if state_ids:
                    value['level3'] = True
                    value['new_state_id_level3'] = False
        
        return {'value':value}

    def get_date(self, str):
        return datetime.strptime(str, "%Y-%m-%d")

    def _check_date(self, cr, uid, ids, context=None):
        """
        Check the value of start_date if less than employment_date or not.

        @return: Boolean of True or False
        """
        for act in self.browse(cr, uid, ids, context):
            if self.get_date(act.start_date) < self.get_date(act.employee_id.employment_date):
                raise osv.except_osv(_(''), _("Process Date Must Be after Than Employment Date!"))

            '''if self.search(cr, uid, [('employee_id','=',act.employee_id.id), ('start_date','>',act.start_date)]):
                raise osv.except_osv(_(''), _("fount some record after this record"))'''
            
        return True

    _constraints = [
        (_check_date, _(''), ['start_date']),
    ]

    def approved(self, cr, uid, ids, context=None):
        emp = self.pool.get('hr.employee')
        for obj in self.browse(cr, uid, ids):
            self.edit_last_employee_arch(cr , uid , obj.employee_id.id)
            emp.write(cr, uid, [obj.employee_id.id], {
                      'service_state_id': obj.new_state_id.id,
                      'service_state_id_level2': obj.new_state_id_level2.id,
                      'service_state_id_level3': obj.new_state_id_level3.id})
        self.write(cr, uid, ids, {'is_last' : True})
        self.write(cr, uid, ids, {'state':'approve'})
        return True


    def set_to_draft(self, cr , uid , ids , context=None):
        for obj in self.browse(cr, uid, ids):
            if not obj.is_last :
               raise orm.except_orm(_('Warning'), _("Connot Edit this record because it is not the last record for this employee")) 
            else:
                emp = self.pool.get('hr.employee')
                emp.write(cr, uid, [obj.employee_id.id], { 'service_state_id': obj.current_state_id.id})
                self.write(cr , uid , ids , {'state' : 'draft' , 'is_last' : False})
                wf_service = netsvc.LocalService("workflow")
                for id in ids:
                    wf_service.trg_delete(uid, 'hr.employee.delegation', id, cr)
                    wf_service.trg_create(uid, 'hr.employee.delegation', id, cr)
        return True

    def edit_last_employee_arch(self , cr , uid , employee_id,context=None):
        '''
        looking for the last service.state.archive record for an employee 
        and set value of  is_last to false. 
        '''
        arch_ids = self.search(cr , uid , [('employee_id' , '=' , employee_id) , ('is_last' ,'=' , True)],context=context)
        if arch_ids :
            self.write(cr , uid , arch_ids , {'is_last' : False})

    def create(self , cr , uid , vals , context=None):
        edit_last_employee_arch(cr , uid , self , vals['employee_id'])
        emp = self.pool.get('hr.employee').browse(cr, uid, [vals['employee_id']])[0]
        vals['current_state_id'] = emp.service_state_id.id
        return super(hr_employee_delegation, self).create(cr, uid, vals, context=context)

class employee_family(osv.Model):

    _inherit = "hr.employee.family"
    _columns = {
        'card_no': fields.char("Card Number", size=64),
        'card_state': fields.selection([('active', 'Active'), ('not_active', 'Not Active')], 'State'),
    }

    _defaults = {
        'card_state': 'active',
    }

    def name_get(self, cr, uid, ids, context=None):
        return ids and [(item.id, "%s-%s-%s" % ( item.relation_name, item.relation_id.name , item.employee_id.name)) for item in self.browse(cr, uid, ids, context=context)] or []



class hr_military_training_category(osv.Model):
    _name = "hr.military.training.category"
    _columns = {
        'code': fields.char("Code", size=64),
        'name': fields.char("Name", required=True, size=64),
    }

    _sql_constraints = [
        ('model_uniq', 'unique(name)', _(
            'you can not create same name !')),
    ]

    def _check_spaces(self, cr, uid, ids, context=None):
        for rec in self.browse(cr, uid, ids, context=context):
            if rec.name and (len(rec.name.replace(' ', '')) <= 0):
                raise osv.except_osv(_('ValidateError'),
                                     _("name must not be spaces"))
        return True
    _constraints = [
        (_check_spaces, '', ['name'])
    ]


class hr_military_training_place(osv.Model):
    _name = "hr.military.training.place"
    _columns = {
        'code': fields.char("Code", si0ze=64),
        'name': fields.char("Name", required=True, size=64),
    }

    _sql_constraints = [
        ('model_uniq', 'unique(name)', _(
            'you can not create same name !')),
    ]

    def _check_spaces(self, cr, uid, ids, context=None):
        for rec in self.browse(cr, uid, ids, context=context):
            if rec.name and (len(rec.name.replace(' ', '')) <= 0):
                raise osv.except_osv(_('ValidateError'),
                                     _("name must not be spaces"))
        return True
    _constraints = [
        (_check_spaces, '', ['name'])
    ]


class hr_military_training(osv.Model):
    _name = 'hr.military.training'
    _columns = {
        'type': fields.many2one('hr.military.training.category', string="Type", required=True),
        'place': fields.many2one('hr.military.training.place', string="Place", required=True),
        'start_date': fields.date('Start Date', required=True),
        'end_date': fields.date('End Date', required=True),
        'employee_id': fields.many2one('hr.employee', string="Employee"),
        'state':fields.selection([('draft','Draft'), ('confirm', 'Confirm')] ,'Status'), 
        'course_type':fields.selection([('sureness','Sureness'), ('security', 'Security'),
                                        ('specialized','Specialized'), ('qualifying', 'Qualifying'),
                                        ('technician','Technician'), ('administrative', 'Administrative')] ,'Course Type'),
        'participation_type':fields.selection([('student','Student'), ('lecturer', 'Lecturer'),
                                        ('translator','Translator'), ('supervisor', 'Supervisor')],'Participation Type'),
        'reference':fields.selection([('file','File Certificate'), ('statement', 'Training Statement')],'Reference'),
        'training_eval': fields.selection([('excellent','Excellent'),('v_good','Very Good'),
                                            ('good','Good'),('middle','Middle'),
                                            ('u_middle','Under Middle'),('weak','Weak')], 'Training Eval'),
        'company_id': fields.many2one('res.company','company'),
        'location':fields.selection([('inside','Inside'), ('outside', 'Outside')] ,'Location'), 
    }

    def _default_company(self,cr,uid,context=None):
        List = []
        user_obj = self.pool.get('res.users')
        user = user_obj.browse(cr ,uid, uid)
        company = False
        if user.company_id:
            company = user.company_id.id
        return company

    _defaults = {
        'state' : 'draft',
        'company_id' : _default_company,
    }

    def fields_view_get(self, cr, uid, view_id=None, view_type='form', context=None, toolbar=False, submenu=False):
        #override of fields_view_get to change the String of employee_id fields
        emp_obj=self.pool.get('hr.employee')
        belong_to=False
        if context is None:
            context={}
        res = super(hr_military_training, self).fields_view_get(cr, uid, view_id=view_id, view_type=view_type, context=context, toolbar=toolbar, submenu=submenu)
        emp=emp_obj.search(cr, uid, [('user_id','=',uid)])
        employee = emp_obj.browse(cr, uid, emp and emp[0] or 0)
        for cat in (emp and employee.category_ids or []):
            if cat.belong_to:
                belong_to=cat.belong_to
        if belong_to:
            doc = etree.XML(res['arch'])
            for node in doc.xpath("//field[@name='employee_id']"):
                if belong_to == 'officer_affairs':
                    node.set('string', _('Officer'))
                elif belong_to == 'soldier_affairs':
                    node.set('string', _('Soldier'))
                else:
                    node.set('string', _('Soldier'))
            for node in doc.xpath("//label[@for='employee_id']"):
                if belong_to == 'officer_affairs':
                    node.set('string', _('Officer'))
                elif belong_to == 'soldier_affairs':
                    node.set('string', _('Soldier'))
                else:
                    node.set('string', _('Soldier'))
            res['arch'] = etree.tostring(doc)
        return res

    def name_get(self, cr, uid, ids, context=None):
        res = []
        for record in self.browse(cr, uid, ids, context=context):
            name = record.employee_id.name + ' / ' + record.type.name
            res.append((record.id, name))
        return res

    def get_date(self, str):
        return datetime.strptime(str, "%Y-%m-%d")


    def _check_date(self, cr, uid, ids, context=None):
        """
        Check the value of start_date if greater than end_date or not.

        @return: Boolean of True or False
        """
        for act in self.browse(cr, uid, ids, context):
            if act.start_date and act.end_date:
                if self.get_date(act.start_date) > self.get_date(act.end_date):
                    raise osv.except_osv(_(''), _("Start Date Must Be Less Than End Date!"))

            if self.get_date(act.start_date) < self.get_date(act.employee_id.employment_date):
                    raise osv.except_osv(_(''), _("Start Date Must Be Greater Than Employment Date!"))
            
        return True

    _constraints = [
        (_check_date, _(''), ['start_date','end_date']),
    ]

    def set_to_draft(self,cr,uid,ids,context=None):
        """
        Mehtod that sets the state to draft.

        @return: Boolean True
        """            
        return self.write(cr, uid, ids, {'state': 'draft'}, context=context)

    def confirm(self,cr,uid,ids,context=None):
        """
        Mehtod that sets the state to confirm.

        @return: Boolean True
        """
        return self.write(cr, uid, ids, {'state': 'confirm'}, context=context)



class hr_service_state(osv.Model):
    _name = 'hr.service.state'
    _columns = {
        'code': fields.char("Code", size=64),
        'name': fields.char("Name", required=True, size=64),
        'level': fields.selection([('1' , 'One') , ('2' , 'Tow'), ('3' , 'Three')] , string="Level"),
        'parent_id': fields.many2one('hr.service.state', string="Parent"),
        'type': fields.selection([('specific' , 'Specified') , ('takeout' , 'Takeout')] , string="Type"),
        'inside_corp' : fields.boolean('Movements inside Corporation only') ,
        'current_archive_ids': fields.one2many('hr.service.state.archive', 'current_state_id', string='current state archives'),
        'new_archive_ids': fields.one2many('hr.service.state.archive', 'new_state_id', string='new state archives'),
        'state_type': fields.selection([('in' , 'In Service') , ('out' , 'Out of Service')] , string="State Type"),
    }
    _default = {
        'type' : 'specific'
    }

    _sql_constraints = [
        ('model_uniq', 'unique(name)', _(
            'you can not create same name !')),
    ]

    def onchange_level(self, cr, uid, ids, level, context=None):
        """
        To make employee_id and department_id requierd base on use type.

        @param use: Id of use
        @return: Dictionary of values 
        """
        emp_obj = self.pool.get('hr.employee')
        dept_obj = self.pool.get('hr.department')
        vals={}
        domain={}
        if level:
            lev='1'
            if level == '2':
                lev='1'
            else:
                lev='2'

            domain['parent_id']=[('level','=',lev)]
            vals['parent_id'] = False
        return {'value':vals,'domain':domain}

    def _check_spaces(self, cr, uid, ids, context=None):
        for rec in self.browse(cr, uid, ids, context=context):
            if rec.name and (len(rec.name.replace(' ', '')) <= 0):
                raise osv.except_osv(_('ValidateError'),
                                     _("name must not be spaces"))
        return True
    _constraints = [
        (_check_spaces, '', ['name']),
    ]

    def unlink(self, cr, uid, ids, context=None):
        for rec in self.browse(cr, uid, ids):
            if rec.current_archive_ids or rec.new_archive_ids:
                raise osv.except_osv(
                    _(''), _("can not delete record linked with other record"))
        return super(hr_service_state, self).unlink(cr, uid, ids, context=context)


class hr_service_end_reason(osv.Model):
    _name = 'hr.service.end.reason'
    _columns = {
        'code': fields.char("Code", size=64),
        'name': fields.char("Name", required=True, size=64),
        'company_id': fields.many2one('res.company','company'),
    }

    def _default_company(self,cr,uid,context=None):
        List = []
        user_obj = self.pool.get('res.users')
        user = user_obj.browse(cr ,uid, uid)
        company = False
        if user.company_id:
            company = user.company_id.id
        return company

    _defaults = {
        'company_id' : _default_company,
    }
    _sql_constraints = [
        ('model_uniq', 'unique(name)', _(
            'you can not create same name !')),
    ]

    def _check_spaces(self, cr, uid, ids, context=None):
        for rec in self.browse(cr, uid, ids, context=context):
            if rec.name and (len(rec.name.replace(' ', '')) <= 0):
                raise osv.except_osv(_('ValidateError'),
                                     _("name must not be spaces"))
        return True
    _constraints = [
        (_check_spaces, '', ['name']),
    ]

# this object is not used it's functionality is merged with hr.employee.delegation object 
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

    def get_date(self, str):
        return datetime.strptime(str, "%Y-%m-%d")

    def _check_date(self, cr, uid, ids, context=None):
        """
        Check the value of process_date if less than employment_date or not.

        @return: Boolean of True or False
        """
        for act in self.browse(cr, uid, ids, context):
            if self.get_date(act.process_date) < self.get_date(act.employee_id.employment_date):
                raise osv.except_osv(_(''), _("Process Date Must Be after Than Employment Date!"))

            if self.search(cr, uid, [('employee_id','=',act.employee_id.id), ('process_date','>',act.process_date)]):
                raise osv.except_osv(_(''), _("fount some record after this record"))
            
        return True

    _constraints = [
        (_check_date, _(''), ['process_date']),
    ]

    def unlink(self , cr , uid , ids , context=None):
        for i in self.browse(cr , uid , ids):
            if i.state != 'draft':
                raise osv.except_osv(_('warning') , _('You Connot delete records not in Draft state !!'))
        return super(hr_service_state_archive , self).unlink(cr , uid , ids , context)

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
        'otherid': fields.related('employee_id', 'otherid', string="Code", type="char", store=True),
        'employee_salary_scale': fields.many2one('hr.salary.scale', "Employee Salary Scale", size=64,  required=False, states={'approved':[('readonly',True)]}),
        'reference': fields.reference('Event Ref', selection=[
            ('hr.salary.degree', 'Promotion'),
            ('hr.salary.bonuses', 'Annual Bonus'),
            ('hr.salary.degree.isolate', 'Isolate'),
            ('hr.department', 'Department Transfer'),
            ('hr.job', 'Job Transfer')], size=128, required=False, states={'approved': [('readonly', True)]}),
    }

    def fields_view_get(self, cr, uid, view_id=None, view_type='form', context=None, toolbar=False, submenu=False):
        #override of fields_view_get to change the String of employee_id fields
        emp_obj=self.pool.get('hr.employee')
        belong_to=False
        if context is None:
            context={}
        res = super(employee_process, self).fields_view_get(cr, uid, view_id=view_id, view_type=view_type, context=context, toolbar=toolbar, submenu=submenu)
        emp=emp_obj.search(cr, uid, [('user_id','=',uid)])
        employee = emp_obj.browse(cr, uid, emp and emp[0] or 0)
        for cat in (emp and employee.category_ids or []):
            if cat.belong_to:
                belong_to=cat.belong_to
        if belong_to:
            doc = etree.XML(res['arch'])
            for node in doc.xpath("//field[@name='employee_id']"):
                if belong_to == 'officer_affairs':
                    node.set('string', _('Officer'))
                elif belong_to == 'soldier_affairs':
                    node.set('string', _('Soldier'))
                else:
                    node.set('string', _('Soldier'))
            res['arch'] = etree.tostring(doc)
        return res

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
                                   'degree_id': id, 'is_isolated': True,'promotion_date': row['approve_date']})
                return self.write(cr, uid, ids, {'state': 'approved'})
            elif model_name == 'hr.salary.degree':
                employee_obj.write(cr, uid, [row['employee_id'][0]], {
                                   'is_isolated': False,'promotion_date': row['approve_date']})
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
                raise osv.except_osv(_('warning') , _('approve date must be same or after than date'))
        return True

    _constraints = [
        (_check_approve_date , '' , ['approve_date' , 'date']) ,
    ]

    _defaults = {
        'date': time.strftime('%Y-%m-%d'),
        'state': 'draft',
    }

class employee_movements_department_description(osv.Model):
    _name = "hr.movements.department.description"

    _columns = {
        'name': fields.char('Transfer Description', size=256),
        
    }


class employee_movements_department_work_sector(osv.Model):
    _name = "hr.movements.department.work.sector"

    _columns = {
        'name': fields.char('Work Sector', size=256),
        
    }


class employee_movements_department(HR_Movements):
    _name = "hr.movements.department"
    def _time_in_previous(self, cr, uid, ids, name, args, context=None):
        result = {}
        for rec in self.browse(cr, uid, ids, context=context):
            rec_datetime = rec.employee_id.join_date
            result[rec.id] = False 
            if rec_datetime:
                rec_datetime = datetime.strptime(rec_datetime, '%Y-%m-%d')
                current_datetime = time.strftime('%Y-%m-%d')
                
                current_datetime = datetime.strptime(
                    current_datetime, '%Y-%m-%d')
                
                if rec_datetime < current_datetime:
                    period = str(current_datetime - rec_datetime)
                    result[rec.id] = period
        return result

    _columns = {
        'reference' : fields.many2one('hr.department' , string="New Department" , required=True) , 
        'last_department_id' : fields.many2one('hr.department' , string="Previous") ,
        'current_dept' : fields.char('New Department' , size=156) ,
        'last_dept' : fields.char('Previous' , size=156) , 
        'old_data' : fields.boolean('Old Data'),
        'move_order_line_id' : fields.many2one('hr.move.order.line' , string="Move Order") ,
        'move_order_id' : fields.many2one('hr.move.order' , string="Move Order") ,  
        'state':fields.selection([ ('draft','Draft'),('approved','Approved')] ,'Status' ,select=True, readonly=True),                                       
        'is_last' : fields.boolean('Last Archive'),
        'time_in_previous': fields.function(_time_in_previous, string='Time IN Previous Department', type='char',
                                           store={
            'hr.movements.department': (lambda self, cr,uid,ids,c: ids, ['last_department_id'], 10),
            }),
        'move_order_date' : fields.related('move_order_id', 'move_date', type='date', string='Move Order Date'),
        'emp_degree_id' : fields.many2one('hr.salary.degree' , string="Degree") , 
        'emp_job_id' : fields.many2one('hr.job' , string="Job") ,
        'join_date':fields.date(" Last Join Date", size=8 ),
        'move_from_dep_date':fields.date("Date of transfer form department", size=8 ),
        'transfer_by': fields.selection([('general','General Disclosure'),('private','Private Disclosure'),('sign','Sign')], 'Transfer By'),
        'transfer_description' : fields.many2one('hr.movements.department.description' , string="Transfer Description") ,
        'work_sector' : fields.many2one('hr.movements.department.work.sector' , string="Work Sector") ,
        'state':fields.selection([ ('draft','NOT Executed'),('approved','Executed'),('cancel','Cancelled')] ,'Status' ,select=True, readonly=True),
        'payroll_state':fields.selection([('khartoum', 'khartoum'), ('states', 'States')], "States or Khartoum"),
        'payroll_employee_id':fields.many2one('hr.department.payroll', 'Department of Payroll'),

        'old_payroll_state':fields.selection([('khartoum', 'khartoum'), ('states', 'States')], readonly=True, store=True, string="States or Khartoum"),
        'old_payroll_employee_id':fields.many2one('hr.department.payroll', readonly=True, store=True, string='Old Department of Payroll'),


    }


    def onchange_state(self, cr, uid, ids=[], payroll_state=True, context=None):
        """
        """
        vals = {}
        if payroll_state:
            vals = {'payroll_employee_id': False}
        return {'value': vals}


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
                emp.write(cr, uid, [obj.employee_id.id], { 'department_id': obj.last_department_id.id, 'join_date': obj.join_date, 'payroll_state':  obj.old_payroll_state and obj.old_payroll_state or obj.employee_id.payroll_state, 
                'payroll_employee_id': obj.old_payroll_employee_id and obj.old_payroll_employee_id.id or obj.employee_id.payroll_employee_id.id,})
                return self.write(cr , uid , ids , {'state' : 'draft' , 'is_last' : False , 'approve_date' : False})

    def cancel(self, cr , uid , ids , context=None):
        """
        """
            
        return self.write(cr , uid , ids , {'state' : 'cancel', 'is_last' : True })

    
    def name_get(self, cr, uid, ids, context=None):
        key = _('movements department')
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
            
            emp_obj.write(cr , uid , [obj.employee_id.id] , {"department_id" : obj.reference.id, 'join_date':obj.approve_date or vals['approve_date'], 'payroll_state': obj.payroll_state and obj.payroll_state or obj.employee_id.payroll_state,
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
		            'last_dept':emp.department_id.name,
                    'employee_salary_scale' : emp.payroll_id.id ,
                    'move_order_line_id' : None , 
                    'reference' : None , 
                    'emp_degree_id': emp.degree_id.id,
                    'emp_job_id': emp.job_id.id,
                    'join_date': emp.join_date,
                    'payroll_state': emp.payroll_state,
                    'payroll_employee_id': emp.payroll_employee_id.id,
                    'old_payroll_state': emp.payroll_state,
                    'old_payroll_employee_id': emp.payroll_employee_id.id,
                } ,
                'domain' : {              
                    'reference' : [('id' , '!=' , ref_id)] , 
                }
            }
        return {}



    def on_change_current_department(self , cr, uid ,ids , department , context={}):
        res = {}
        if department :
            department_obj = self.pool.get('hr.department').browse(cr , uid , [department])[0]
            return {
                'value' : {
                    'current_dept' : department_obj.name,
                }
            }
        
        return res


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
                    #'default_manger_id' : rec.reference.manager_id.name_related ,
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

        if 'employee_id' in vals:
                emp = self.pool.get('hr.employee').browse(cr , uid , vals['employee_id'])
                onchange_vals = self.onchange_employee(cr, uid, [], emp.id, context)['value']
                vals.update({
                    'previous' : onchange_vals['previous'] ,
                    'last_department_id' : onchange_vals['last_department_id']  ,
                    'employee_salary_scale' : onchange_vals['employee_salary_scale']  ,
                    'emp_degree_id': onchange_vals['emp_degree_id'],
                    'emp_job_id': onchange_vals['emp_job_id'],
                    'join_date': onchange_vals['join_date'],
                    'old_payroll_state': onchange_vals['payroll_state'],
                    'old_payroll_employee_id': onchange_vals['payroll_employee_id'],
                })
        return super(employee_movements_department,self).create(cr , uid , vals , context)

    def write(self , cr , uid , ids, vals , context=None):
        """
        """
        for rec in self.browse(cr, uid, ids, context):
            if 'employee_id' in vals:
                emp = self.pool.get('hr.employee').browse(cr , uid , vals['employee_id'])
                onchange_vals = self.onchange_employee(cr, uid, [rec.id], emp.id, context)['value']

                vals.update({
                    'previous' : onchange_vals['previous'] ,
                    'last_department_id' : onchange_vals['last_department_id']  ,
                    'employee_salary_scale' : onchange_vals['employee_salary_scale']  ,
                    'emp_degree_id': onchange_vals['emp_degree_id'],
                    'emp_job_id': onchange_vals['emp_degree_id'],
                    'join_date': onchange_vals['join_date'],
                    'old_payroll_state': onchange_vals['payroll_state'],
                    'old_payroll_employee_id': onchange_vals['payroll_employee_id'],
                })
            
        return super(employee_movements_department,self).write(cr , uid , ids, vals , context)

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
       'reference' : fields.many2one('hr.job' , string="New Job" , required=True) , 
        'last_job_id' : fields.many2one('hr.job' , string="Previous Job") , 
        'is_last' : fields.boolean('Last Archive'),
        'parent_job_id' : fields.many2one('hr.job' , string="Job group") , 
        'approve_date' :fields.date("Date of entry into job", size=8  , select=True , states={'approved':[('readonly',True)]}),
        'qualification_ids':fields.one2many('hr.employee.qualification', 'movement_job_id', "New Qualifications"),
    }

    def name_get(self, cr, uid, ids, context=None):
        key = _('movements job')
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
                # 'domain' : {              
                #     'reference' : [('id' , '!=' , ref_id)] , 
                # }
            }
        return {}

    def create(self , cr , uid , vals , context=None):
        job_id = self.pool.get('hr.employee').browse(cr , uid , [vals['employee_id']])[0].job_id
        vals['last_job_id'] = job_id.id
        vals['previous'] = job_id.name
        if 'employee_id' in vals:
                emp = self.pool.get('hr.employee').browse(cr , uid , vals['employee_id'])
                onchange_vals = self.onchange_employee(cr, uid, [], emp.id, context)['value']
                vals.update({
                    'previous' : onchange_vals['previous'] ,
                    'last_job_id' : onchange_vals['last_job_id']  ,
                    'employee_salary_scale' : onchange_vals['employee_salary_scale']  ,
                })
        return super(employee_movements_job , self).create(cr , uid , vals , context)

    def onchange_parent_job_id(self, cr, uid, ids=[], parent_job_id=True, context=None):
        """
        """
        vals = {}
        if parent_job_id:
            vals = {'reference': False}
        return {'value': vals}


    def write(self , cr , uid , ids, vals , context=None):
        """
        """
        for rec in self.browse(cr, uid, ids, context):
            if 'employee_id' in vals:
                emp = self.pool.get('hr.employee').browse(cr , uid , vals['employee_id'])
                onchange_vals = self.onchange_employee(cr, uid, [rec.id], emp.id, context)['value']

                vals.update({
                    'previous' : onchange_vals['previous'] ,
                    'last_job_id' : onchange_vals['last_job_id']  ,
                    'employee_salary_scale' : onchange_vals['employee_salary_scale']  ,
                })

        return super(employee_movements_job,self).write(cr , uid , ids, vals , context)

        

class employee_movements_promotion(HR_Movements):
    _name = "hr.movements.degree"
    _columns = {
        'reference' : fields.many2one('hr.salary.degree' , string="New Degree" , required=True) , 
        'process_type' : fields.selection([('promotion' , 'Promotion') , ('isolate' , 'Isolataion')]),
        'new_scale_id' : fields.many2one('hr.salary.scale' , string='Salary Scale') ,
        'new_bonuse_id' : fields.many2one('hr.salary.bonuses' , string='Bonuse'),
        'last_bonus_id' : fields.many2one('hr.salary.bonuses' , string='Previous Bonus'),
        'last_degree_id' : fields.many2one('hr.salary.degree' , string='Previous Degree'),
        'is_last' : fields.boolean('Last Archive'),
        'approve_date' :fields.date("Date of entry into degree", size=8  , select=True , states={'approved':[('readonly',True)]}),
        'promotion_date':fields.date("Date of entry into previous degree", size=8 ),
        'bonus_date':fields.date("Date of entry into previous bonus", size=8 ),
        'notes' : fields.text('Notes') ,
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
                    'promotion_date' : obj.promotion_date,
                    'military_type':obj.employee_salary_scale.military_type,
                }
                if obj.process_type == "isolate" : vals['is_isolated'] = True
                if obj.process_type == "promotion" : 
                    vals['is_isolated'] = False
                    vals['bonus_date'] = obj.bonus_date 
                emp = self.pool.get('hr.employee')
                emp.write(cr, uid, [obj.employee_id.id], vals)
                return self.write(cr , uid , ids , {'state' : 'draft' , 'is_last' : False , 'approve_date' : False})

    def name_get(self, cr, uid, ids, context=None):
        key1 = ['promotion',_('Promotion')]
        key2 = ['isolate' , _('Isolataion')]
        if context and 'lang' in context:
            translation_obj = self.pool.get('ir.translation')
            translation_ids = translation_obj.search(
                cr, uid, [('src', '=', key1[1]), ('lang', '=', context['lang'])], context=context)
            translation_recs = translation_obj.read(
                cr, uid, translation_ids, [], context=context)
            
            key1[1] = translation_recs and translation_recs[0]['value'] or key1[1]


            translation_ids = translation_obj.search(
                cr, uid, [('src', '=', key2[1]), ('lang', '=', context['lang'])], context=context)
            translation_recs = translation_obj.read(
                cr, uid, translation_ids, [], context=context)
            
            key2[1] = translation_recs and translation_recs[0]['value'] or key2[1]


        return ids and [(item.id, "%s-%s-%s" % ( item.process_type == key1[0] and key1[1] or  item.process_type == key2[0] and key2[1], item.employee_id.name, item.reference.name_get()[0][1])) for item in self.browse(cr, uid, ids, context=context)] or []

    def do_approve(self, cr, uid, ids, context=None):
        for obj in self.browse(cr , uid , ids):
            edit_last_employee_arch(cr , uid , self ,obj.employee_id.id)
            emp_obj = self.pool.get('hr.employee')
            vals = {"degree_id" : obj.reference.id , "payroll_id" : obj.new_scale_id.id , "bonus_id" : obj.new_bonuse_id.id,'promotion_date':obj.approve_date,"military_type":obj.new_scale_id.military_type}
            #print ">>>>>>>>>>>>>>>>>>>>>>>>>>>>>",vals
            if obj.process_type == "isolate" : vals['is_isolated'] = True
            if obj.process_type == "promotion" : 
                vals['is_isolated'] = False
                vals['bonus_date'] = obj.approve_date

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
                'promotion_date': emp.promotion_date ,
                'bonus_date': emp.bonus_date ,
                'previous' : emp.degree_id.name,
            }
        return res

    def onchange_salary(self, cr, uid, ids, emp_id,new_scale_id ,process_type ,context={}):
        res = {}
        emp_obj = self.pool.get('hr.employee')
        degree_domain = [('payroll_id' , '=' , new_scale_id )]
        if emp_id:
            emp = emp_obj.browse(cr , uid , [emp_id])[0]
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
  
        if 'employee_id' in vals:
                emp = self.pool.get('hr.employee').browse(cr , uid , vals['employee_id'])
                onchange_vals = self.onchange_employee(cr, uid, [], emp.id, context)['value']

                vals.update({
                    'previous': onchange_vals['previous']  ,
                    'last_degree_id' : onchange_vals['last_degree_id']  ,
                    'last_bonus_id' : onchange_vals['last_bonus_id']  ,
                    'promotion_date' : onchange_vals['promotion_date']  ,
                    'bonus_date' : onchange_vals['bonus_date']  ,
                    'employee_salary_scale' : onchange_vals['employee_salary_scale']  ,
                })
        return super(employee_movements_promotion , self).create(cr , uid , vals , context)


    def write(self , cr , uid , ids, vals , context=None):
        """
        """
        for rec in self.browse(cr, uid, ids, context):
            if 'employee_id' in vals:
                emp = self.pool.get('hr.employee').browse(cr , uid , vals['employee_id'])
                onchange_vals = self.onchange_employee(cr, uid, [rec.id], emp.id, context)['value']

                vals.update({
                    'previous': onchange_vals['previous']  ,
                    'last_degree_id' : onchange_vals['last_degree_id']  ,
                    'last_bonus_id' : onchange_vals['last_bonus_id']  ,
                    'promotion_date' : onchange_vals['promotion_date']  ,
                    'bonus_date' : onchange_vals['bonus_date']  ,
                    'employee_salary_scale' : onchange_vals['employee_salary_scale']  ,
                })

        return super(employee_movements_promotion,self).write(cr , uid , ids, vals , context)


    def fields_view_get(self, cr, uid, view_id=None, view_type='form', context=None, toolbar=False, submenu=False):
        #override of fields_view_get in employee to change the String of some fields
        if context is None:
            context={}
        res = super(employee_movements_promotion, self).fields_view_get(cr, uid, view_id=view_id, view_type=view_type, context=context, toolbar=toolbar, submenu=submenu)
        type = context.get('default_process_type', False)
        if type:
            doc = etree.XML(res['arch'])
            for node in doc.xpath("//field[@name='approve_date']"):
                if type == 'promotion':
                    node.set('string', _('Date of entry into degree'))
                elif type == 'isolate':
                    node.set('string', _('Isolate Date'))
            res['arch'] = etree.tostring(doc)
        return res


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
        'company_id': fields.many2one('res.company','company'),
    }

    def fields_view_get(self, cr, uid, view_id=None, view_type='form', context=None, toolbar=False, submenu=False):
        #override of fields_view_get to change the String of employee_id fields
        emp_obj=self.pool.get('hr.employee')
        belong_to=False
        if context is None:
            context={}
        res = super(hr_service_end, self).fields_view_get(cr, uid, view_id=view_id, view_type=view_type, context=context, toolbar=toolbar, submenu=submenu)
        emp=emp_obj.search(cr, uid, [('user_id','=',uid)])
        employee = emp_obj.browse(cr, uid, emp and emp[0] or 0)
        for cat in (emp and employee.category_ids or []):
            if cat.belong_to:
                belong_to=cat.belong_to
        if belong_to:
            doc = etree.XML(res['arch'])
            for node in doc.xpath("//field[@name='employee_id']"):
                if belong_to == 'officer_affairs':
                    node.set('string', _('Officer'))
                elif belong_to == 'soldier_affairs':
                    node.set('string', _('Soldier'))
                else:
                    node.set('string', _('Soldier'))
            for node in doc.xpath("//label[@for='employee_id']"):
                if belong_to == 'officer_affairs':
                    node.set('string', _('Officer'))
                elif belong_to == 'soldier_affairs':
                    node.set('string', _('Soldier'))
                else:
                    node.set('string', _('Soldier'))
            res['arch'] = etree.tostring(doc)
        return res

    def _default_company(self,cr,uid,context=None):
        List = []
        user_obj = self.pool.get('res.users')
        user = user_obj.browse(cr ,uid, uid)
        company = False
        if user.company_id:
            company = user.company_id.id
        return company

    _defaults = {
        'end_date': time.strftime('%Y-%m-%d'),
        'state': 'draft',
        'company_id' : _default_company,
    }

    def copy(self, cr, uid, id, default=None, context=None):
        """
        Override copy function to edit default value.

        @param default : default vals dict
        @return: super copy() method
        """
        raise osv.except_osv(_('Warning!'),_('You cannot duplicate record.'))
        return super(hr_service_end, self).copy(cr, uid, id, default, context)


    def get_date(self, str):
        return datetime.strptime(str, "%Y-%m-%d")

    def _check_date(self, cr, uid, ids, context=None):
        """
        Check the value of end_date if less than employment_date or not.

        @return: Boolean of True or False
        """
        for act in self.browse(cr, uid, ids, context):
            if self.get_date(act.end_date) < self.get_date(act.employee_id.employment_date):
                raise osv.except_osv(_(''), _("End Date Must Be Greater Than Employment Date!"))
        return True

    _constraints = [
        (_check_date, _(''), ['end_date']),
    ]

    def unlink(self , cr , uid , ids , context=None):
        for i in self.browse(cr , uid , ids):
            if i.state != 'draft':
                raise osv.except_osv(_('warning') , _('You Connot delete records not in Draft state !!'))
        return super(hr_service_end , self).unlink(cr , uid , ids , context)

    def name_get(self, cr, uid, ids, context=None):
        key = _('service end')
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
       'reference' : fields.many2one('hr.salary.bonuses' , string="New Bonus" , required=True) , 
       'last_bonus_id' : fields.many2one('hr.salary.bonuses' , string="Previous Bonus") ,
       'is_last' : fields.boolean('Last Archive') ,   
       'approve_date' :fields.date(string="Date of entry into bonus", size=8  , select=True , states={'approved':[('readonly',True)]}),
       'bonus_date':fields.date("Date of entry into previous bonus", size=8 ),
    }

    def set_to_draft(self, cr , uid , ids , context=None):
        for obj in self.browse(cr, uid, ids):
            if not obj.is_last :
               raise orm.except_orm(_('Warning'), _("Connot Edit this record because it is not the last record for this employee")) 
            else:
                vals = {
                    'bonus_id' : obj.last_bonus_id.id ,
                    'bonus_date': obj.bonus_date,
                }
                emp = self.pool.get('hr.employee')
                emp.write(cr, uid, [obj.employee_id.id], vals)
                return self.write(cr , uid , ids , {'state' : 'draft' , 'is_last' : False , 'approve_date' : False})

    def name_get(self, cr, uid, ids, context=None):
        key = _('movements bonus')
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
            emp_obj.write(cr , uid , [obj.employee_id.id] , {"bonus_id" : obj.reference.id, 'bonus_date':obj.approve_date})
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
                'bonus_date': emp.bonus_date,
            }
            dom = [('degree_id' , '=' , emp.degree_id.id) , ('sequence' , '>' , ref.sequence)]
            res['domain'] = {'reference' : dom}
        return res

    def create(self , cr ,uid , vals , context=None):
        """
        """
        if 'employee_id' in vals:
                emp = self.pool.get('hr.employee').browse(cr , uid , vals['employee_id'])
                onchange_vals = self.onchange_employee(cr, uid, [], emp.id, context)['value']

                vals.update({
                    'previous': onchange_vals['previous']  ,
                    'last_bonus_id' : onchange_vals['last_bonus_id']  ,
                    'bonus_date' : onchange_vals['bonus_date']  ,
                })
        return super(employee_movements_bonus , self).create(cr , uid , vals , context)

    def write(self , cr , uid , ids, vals , context=None):
        """
        """
        for rec in self.browse(cr, uid, ids, context):
            if 'employee_id' in vals:
                emp = self.pool.get('hr.employee').browse(cr , uid , vals['employee_id'])
                onchange_vals = self.onchange_employee(cr, uid, [rec.id], emp.id, context)['value']

                vals.update({
                    'previous': onchange_vals['previous']  ,
                    'last_bonus_id' : onchange_vals['last_bonus_id']  ,
                    'bonus_date' : onchange_vals['bonus_date']  ,
                })

        return super(employee_movements_bonus,self).write(cr , uid , ids, vals , context)


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
        'date': fields.date('decision Date'),
        'illness': fields.char("Illness", size=64),
        'type' : fields.selection([('holiday' , 'Holiday') , ('transmission' , 'Transmission') ,('commision' , 'Commision'), ('work' , 'Work')] , 'Type') ,
        'holiday_id': fields.many2one('hr.holidays', string="Holiday"  , domain=[('sick_leave' , '=' , 'True')]),
        'commision_id': fields.many2one('hr.commision', string="Commision"),
        'transmission_id': fields.many2one('hr.employee.mission', string="Transmission" , domain=[('type' , '=' , '3')]),
        #'station' : fields.char('Station') ,
        'station': fields.many2one('hr.mission.category', "Station"),
        'company_id': fields.many2one('res.company','company'),
    }

    def fields_view_get(self, cr, uid, view_id=None, view_type='form', context=None, toolbar=False, submenu=False):
        #override of fields_view_get to change the String of employee_id fields
        emp_obj=self.pool.get('hr.employee')
        belong_to=False
        if context is None:
            context={}
        res = super(hr_employee_illness, self).fields_view_get(cr, uid, view_id=view_id, view_type=view_type, context=context, toolbar=toolbar, submenu=submenu)
        emp=emp_obj.search(cr, uid, [('user_id','=',uid)])
        employee = emp_obj.browse(cr, uid, emp and emp[0] or 0)
        for cat in (emp and employee.category_ids or []):
            if cat.belong_to:
                belong_to=cat.belong_to
        if belong_to:
            doc = etree.XML(res['arch'])
            for node in doc.xpath("//field[@name='employee_id']"):
                if belong_to == 'officer_affairs':
                    node.set('string', _('Officer'))
                elif belong_to == 'soldier_affairs':
                    node.set('string', _('Soldier'))
                else:
                    node.set('string', _('Soldier'))
            res['arch'] = etree.tostring(doc)
        return res

    def _default_company(self,cr,uid,context=None):
        List = []
        user_obj = self.pool.get('res.users')
        user = user_obj.browse(cr ,uid, uid)
        company = False
        if user.company_id:
            company = user.company_id.id
        return company
        
    _defaults = {
        'date': time.strftime('%Y-%m-%d'),
        'state': 'draft',
        'company_id' : _default_company,
    }

    def copy(self, cr, uid, id, default=None, context=None):
        """
        Override copy function to edit default value.

        @param default : default vals dict
        @return: super copy() method
        """
        raise osv.except_osv(_('Warning!'),_('You cannot duplicate record.'))
        return super(hr_employee_illness, self).copy(cr, uid, id, default, context)
    
    def unlink(self , cr , uid , ids , context=None):
        for i in self.browse(cr , uid , ids):
            if i.state != 'draft':
                raise osv.except_osv(_('warning') , _('You Connot delete records not in Draft state !!'))
        return super(hr_employee_illness , self).unlink(cr , uid , ids , context)

    def _check_spaces(self, cr, uid, ids, context=None):
        for rec in self.browse(cr, uid, ids, context=context):
            if rec.illness and (len(rec.illness.replace(' ', '')) <= 0):
                raise osv.except_osv(_('ValidateError'),
                                     _("illness must not be spaces"))
        return True

    def get_date(self, str):
        return datetime.strptime(str, "%Y-%m-%d")

    def _check_date(self, cr, uid, ids, context=None):
        """
        @return: Boolean of True or False
        """
        current_date = time.strftime('%Y-%m-%d')
        current_date = datetime.strptime(
            current_date, '%Y-%m-%d')

        for act in self.browse(cr, uid, ids, context):
            if self.get_date(act.date) > current_date:
                raise osv.except_osv(_(''), _("decision date must be less than or equal current date!"))
            
            if act.end_date and self.get_date(act.date) > self.get_date(act.end_date):
                raise osv.except_osv(_(''), _("decision date must be less than or equal end date!"))
        return True

    _constraints = [
        (_check_spaces, '', ['illness']),
        (_check_date, _(''), ['date','end_date']),
    ]

    def name_get(self, cr, uid, ids, context=None):
        key = _('Illness')
        if context and 'lang' in context:
            translation_obj = self.pool.get('ir.translation')
            translation_ids = translation_obj.search(
                cr, uid, [('src', '=', key), ('lang', '=', context['lang'])], context=context)
            translation_recs = translation_obj.read(
                cr, uid, translation_ids, [], context=context)
            
            key = translation_recs and translation_recs[0]['value'] or key
        return ids and [(item.id, "%s-%s-%s" % ( key , item.employee_id.name, item.date)) for item in self.browse(cr, uid, ids, context=context)] or []


    def do_confirm(self, cr, uid, ids, context=None):
        for rec in self.browse(cr, uid, ids, context=context):
            if not rec.end_date:
                raise osv.except_osv(_(''), _("You Must enter the End date before confirm!"))
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
        'company_id': fields.many2one('res.company','company'),
    }

    def _default_company(self,cr,uid,context=None):
        List = []
        user_obj = self.pool.get('res.users')
        user = user_obj.browse(cr ,uid, uid)
        company = False
        if user.company_id:
            company = user.company_id.id
        return company

    _defaults = {
        'company_id' : _default_company,
    }

class hr_employee_qualificationt(osv.Model):

    _inherit = 'hr.employee.qualification'

    _columns = {
        'organization' : fields.many2one('hr.qualification.org' , string="Organization", domain=[('type' , '=' , 'category')]) ,
        'org_unit' : fields.many2one('hr.qualification.org' , string="Organization Unit", domain=[('type' , '=' , 'element')]) ,
        'company_id': fields.many2one('res.company','company'),
        'parent_qual_id': fields.many2one('hr.qualification','Educational Level'),
        'movement_job_id': fields.many2one('hr.movements.job','Job Movement', ondelete='cascade'),
        'start_date': fields.date('Start Date'),
        'end_date': fields.date('End Date'),
    }

    def _default_company(self,cr,uid,context=None):
        List = []
        user_obj = self.pool.get('res.users')
        user = user_obj.browse(cr ,uid, uid)
        company = False
        if user.company_id:
            company = user.company_id.id
        return company

    _defaults = {
        'company_id' : _default_company,
    }

    def fields_view_get(self, cr, uid, view_id=None, view_type='form', context=None, toolbar=False, submenu=False):
        #override of fields_view_get to change the String of employee_id fields
        emp_obj=self.pool.get('hr.employee')
        belong_to=False
        if context is None:
            context={}
        res = super(hr_employee_qualificationt, self).fields_view_get(cr, uid, view_id=view_id, view_type=view_type, context=context, toolbar=toolbar, submenu=submenu)
        emp=emp_obj.search(cr, uid, [('user_id','=',uid)])
        employee = emp_obj.browse(cr, uid, emp and emp[0] or 0)
        for cat in (emp and employee.category_ids or []):
            if cat.belong_to:
                belong_to=cat.belong_to
        if belong_to:
            doc = etree.XML(res['arch'])
            for node in doc.xpath("//field[@name='employee_id']"):
                if belong_to == 'officer_affairs':
                    node.set('string', _('Officer'))
                elif belong_to == 'soldier_affairs':
                    node.set('string', _('Soldier'))
                else:
                    node.set('string', _('Soldier'))
            for node in doc.xpath("//label[@for='employee_id']"):
                if belong_to == 'officer_affairs':
                    node.set('string', _('Officer'))
                elif belong_to == 'soldier_affairs':
                    node.set('string', _('Soldier'))
                else:
                    node.set('string', _('Soldier'))
            res['arch'] = etree.tostring(doc)
        return res


    def onchange_org(self , cr , uid , ids , context=None):
        return {
            'value' : {
                'org_unit' : False ,
            },
        }

    def onchange_parent_qual_id(self, cr, uid, ids, parent_qual_id, context={}):
        """
        """
        vals = {'emp_qual_id': False}
        return {'value':vals}


    def onchange_emp_qual_id(self, cr, uid, ids, emp_qual_id, context={}):
        """
        """
        vals = {'specialization': False}
        return {'value':vals}


    
    def name_get(self, cr, uid, ids, context=None):
        return ids and [(item.id, "%s-%s-%s" % ( item.emp_qual_id.name , item.employee_id.name, item.qual_date)) for item in self.browse(cr, uid, ids, context=context)] or []


#inherit hr.qualification 
class hr_qualificationt(osv.Model):

    _inherit = 'hr.qualification'

    _columns = {
        'special': fields.boolean('Special'),
        'company_id': fields.many2one('res.company','company'),
        'specification_ids': fields.one2many('hr.specifications','qual_id', 'Secifications'),
    }

    def _default_company(self,cr,uid,context=None):
        List = []
        user_obj = self.pool.get('res.users')
        user = user_obj.browse(cr ,uid, uid)
        company = False
        if user.company_id:
            company = user.company_id.id
        return company

    _defaults = {
        'company_id' : _default_company,
    }

    def _check_spaces(self, cr, uid, ids, context=None):
        for rec in self.browse(cr, uid, ids, context=context):
            if rec.name and (len(rec.name.replace(' ', '')) <= 0):
                raise osv.except_osv(_('ValidateError'),
                                     _("name must not be spaces"))
        return True
    _constraints = [
        (_check_spaces, '', ['name'])
    ]

    def unlink(self, cr, uid, ids, context=None):
        idss = self.pool.get('hr.employee.qualification').search(cr, uid, ids, [('emp_qual_id','in', ids)])
        idsss = self.pool.get('hr.qualification').search(cr, uid, ids, [('parent_id','in', ids)])
        if idss or idsss:
            raise osv.except_osv(
                _(''), _("can not delete record linked with other record"))
        return super(hr_qualificationt, self).unlink(cr, uid, ids, context=context)




class hr_specifications(osv.Model):

    _inherit = 'hr.specifications'

    _columns = {
        'company_id': fields.many2one('res.company','company'),
        'qual_id': fields.many2one('hr.qualification','Qualification', ondelete='cascade'),
    }

    def _default_company(self,cr,uid,context=None):
        List = []
        user_obj = self.pool.get('res.users')
        user = user_obj.browse(cr ,uid, uid)
        company = False
        if user.company_id:
            company = user.company_id.id
        return company

    _defaults = {
        'company_id' : _default_company,
    }

    def unlink(self, cr, uid, ids, context=None):
        idss = self.pool.get('hr.employee.qualification').search(cr, uid, ids, [('specialization','in', ids)])
        if idss:
            raise osv.except_osv(
                _(''), _("can not delete record linked with other record"))
        return super(hr_specifications, self).unlink(cr, uid, ids, context=context)

#----------------------------------------
#Employee Family Relation(inherit)
#----------------------------------------
class family_relation(osv.osv):
    _inherit = "hr.family.relation"

    _columns = {
        'company_id': fields.many2one('res.company','company'),
        'parent_relation': fields.boolean('Parent Relation'),
        'relation_type': fields.selection([('1', 'Partner'),('2','Child')],'Relation Type'),
    }

    def _default_company(self,cr,uid,context=None):
        List = []
        user_obj = self.pool.get('res.users')
        user = user_obj.browse(cr ,uid, uid)
        company = False
        if user.company_id:
            company = user.company_id.id
        return company

    _defaults = {
        'company_id' : _default_company,
    }

    def _check_spaces(self, cr, uid, ids, context=None):
        for rec in self.browse(cr, uid, ids, context=context):
            if rec.name and (len(rec.name.replace(' ', '')) <= 0):
                raise osv.except_osv(_('ValidateError'),
                                     _("name must not be spaces"))
        return True
    _constraints = [
        (_check_spaces, '', ['name'])
    ]

#----------------------------------------
#Employee Family(inherit)
#----------------------------------------
class employee_family(osv.osv):
    _inherit = "hr.employee.family"

    _columns = {
        'company_id': fields.many2one('res.company','company'),
        'reemployment' : fields.many2one('hr.employee.reemployment', "Reemployment", ondelete='cascade'),
    }

    # def _check_nuymber(self, cr, uid, ids, context=None):
    #     #check the number of relation in the same type 
    #     for rec in self.browse(cr, uid, ids, context=context):
    #         relatives = rec.employee_id.relation_ids
    #         relatives  = filter(lambda x:x.relation_id.id == rec.relation_id.id, relatives)
    #         if len(relatives) > rec.relation_id.max_number:
    #             raise osv.except_osv(_('ValidateError'),
    #                                  _("the number of relatives of this type is more than allowed"))
    #     return True
    # _constraints = [
    #     (_check_nuymber, '', ['employee_id','relation_id'])
    # ]

    def mymod_approved(self, cr, uid, ids, context=None):
        """Workflow function that changes the state to 'approved' and re-writes employee's salary.
           @return: Boolean True 
        """
        employee_obj = self.pool.get('hr.employee')
        vals = { 'state' : 'approved' }
        for relation in self.browse(cr, uid, ids, context=context):
            if not relation.start_date:
                vals['start_date'] = time.strftime('%Y-%m-%d')
            if not relation.relation_id.parent_relation:
               emp_id=relation.employee_id.id
               employee_obj.write(cr, uid,[emp_id], {'marital' : 'married'}, context=context)
        self.write(cr, uid, ids, vals, context=context)
        employee_obj.write_employee_salary(cr, uid, [relation.employee_id.id], [])
        return True


    def set_to_draft(self, cr, uid, ids, context=None):
        """Method that sets the state to 'draft' and re-writes employee's salary.
           @return: Boolean True 
        """
        employee_obj = self.pool.get('hr.employee')
        self.write(cr, uid, ids, {'state': 'draft' }, context=context)
        for relation in self.browse(cr, uid, ids, context=context):
            if not relation.relation_id.parent_relation:
                emp_id=relation.employee_id.id
                emp_relations = relation.employee_id.relation_ids
                emp_relations = filter(lambda x : x.id != relation.id and not x.relation_id.parent_relation and x.state=="approved", emp_relations )
                if emp_relations:
                    employee_obj.write(cr, uid,[emp_id], {'marital' : 'married'}, context=context)
                if not emp_relations:
                    employee_obj.write(cr, uid,[emp_id], {'marital' : 'single'}, context=context)
               
            update = employee_obj.write_employee_salary(cr, uid, [relation.employee_id.id], [])
        wf_service = netsvc.LocalService("workflow")
        for id in ids:
            wf_service.trg_delete(uid, 'hr.employee.family', id, cr)
            wf_service.trg_create(uid, 'hr.employee.family', id, cr)
        return True


    def _default_company(self,cr,uid,context=None):
        List = []
        user_obj = self.pool.get('res.users')
        user = user_obj.browse(cr ,uid, uid)
        company = False
        if user.company_id:
            company = user.company_id.id
        return company

    _defaults = {
        'company_id' : _default_company,
    }

    def fields_view_get(self, cr, uid, view_id=None, view_type='form', context=None, toolbar=False, submenu=False):
        #override of fields_view_get to change the String of employee_id fields
        emp_obj=self.pool.get('hr.employee')
        belong_to=False
        if context is None:
            context={}
        res = super(employee_family, self).fields_view_get(cr, uid, view_id=view_id, view_type=view_type, context=context, toolbar=toolbar, submenu=submenu)
        emp=emp_obj.search(cr, uid, [('user_id','=',uid)])
        employee = emp_obj.browse(cr, uid, emp and emp[0] or 0)
        for cat in (emp and employee.category_ids or []):
            if cat.belong_to:
                belong_to=cat.belong_to
        if belong_to:
            doc = etree.XML(res['arch'])
            for node in doc.xpath("//field[@name='employee_id']"):
                if belong_to == 'officer_affairs':
                    node.set('string', _('Officer'))
                elif belong_to == 'soldier_affairs':
                    node.set('string', _('Soldier'))
                else:
                    node.set('string', _('Soldier'))
            for node in doc.xpath("//label[@for='employee_id']"):
                if belong_to == 'officer_affairs':
                    node.set('string', _('Officer'))
                elif belong_to == 'soldier_affairs':
                    node.set('string', _('Soldier'))
                else:
                    node.set('string', _('Soldier'))
            res['arch'] = etree.tostring(doc)
        return res


class hr_employment_termination(osv.Model):
    _inherit = "hr.dismissal"
    _columns = {
        'martyrdom' : fields.boolean('Special for Martyrdom') ,
        'state_id': fields.many2one("hr.service.state", string="Service State"),
    }

    def _check_spaces(self, cr, uid, ids, context=None):
        for rec in self.browse(cr, uid, ids, context=context):
            if rec.name and (len(rec.name.replace(' ', '')) <= 0):
                raise osv.except_osv(_('ValidateError'),
                                     _("name must not be spaces"))
        return True

    def _check_negative(self, cr, uid, ids, context=None):
        for rec in self.browse(cr, uid, ids, context=context):
            if rec.period < 0:
                raise osv.except_osv(_('ValidateError'),
                                     _("Period must be greater than or equals to zero"))
        return True

    _constraints = [
        (_check_spaces, '', ['name']),
        (_check_negative, '', ['period']),
    ]

#----------------------------------------
#employment termination
#----------------------------------------
class hr_employment_termination(osv.Model):

    _inherit = "hr.employment.termination"

    _columns = {
        'move_order_line_id' : fields.many2one('hr.move.order.line' , string="Move Order") ,
        'move_order_id' : fields.many2one('hr.move.order' , string="Move Order") ,
        'company_id': fields.many2one('res.company','company'),
        'state': fields.selection([('draft', 'Draft'),('date_reflect', 'Date Reflect'), ('refuse', 'Out Of Service'), ('calculate', 'Calculated'),
                                   ('transfer', 'Transferred'), ], 'State', readonly=True),
    }
    def _default_company(self,cr,uid,context=None):
        List = []
        user_obj = self.pool.get('res.users')
        user = user_obj.browse(cr ,uid, uid)
        company = False
        if user.company_id:
            company = user.company_id.id
        return company

    _defaults = {
        'company_id' : _default_company,
    }

    def fields_view_get(self, cr, uid, view_id=None, view_type='form', context=None, toolbar=False, submenu=False):
        #override of fields_view_get to change the String of employee_id fields
        emp_obj=self.pool.get('hr.employee')
        belong_to=False
        if context is None:
            context={}
        res = super(hr_employment_termination, self).fields_view_get(cr, uid, view_id=view_id, view_type=view_type, context=context, toolbar=toolbar, submenu=submenu)
        emp=emp_obj.search(cr, uid, [('user_id','=',uid)])
        employee = emp_obj.browse(cr, uid, emp and emp[0] or 0)
        for cat in (emp and employee.category_ids or []):
            if cat.belong_to:
                belong_to=cat.belong_to
        if belong_to:
            doc = etree.XML(res['arch'])
            for node in doc.xpath("//field[@name='employee_id']"):
                if belong_to == 'officer_affairs':
                    node.set('string', _('Officer'))
                elif belong_to == 'soldier_affairs':
                    node.set('string', _('Soldier'))
                else:
                    node.set('string', _('Soldier'))
            for node in doc.xpath("//label[@for='employee_id']"):
                if belong_to == 'officer_affairs':
                    node.set('string', _('Officer'))
                elif belong_to == 'soldier_affairs':
                    node.set('string', _('Soldier'))
                else:
                    node.set('string', _('Soldier'))
            res['arch'] = etree.tostring(doc)
        return res

    def name_get(self, cr, uid, ids, context=None):
        key = _('Termination')
        if context and 'lang' in context:
            translation_obj = self.pool.get('ir.translation')
            translation_ids = translation_obj.search(
                cr, uid, [('src', '=', key), ('lang', '=', context['lang'])], context=context)
            translation_recs = translation_obj.read(
                cr, uid, translation_ids, [], context=context)
            
            key = translation_recs and translation_recs[0]['value'] or key
        return ids and [(item.id, "%s-%s-%s" % ( key , item.employee_id.name, item.dismissal_date)) for item in self.browse(cr, uid, ids, context=context)] or []

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
        for rec in self.browse(cr, uid, ids, context):
            if not rec.move_order_id :
                data = {
                    'default_move_order_line_ids': [[0 , 0 , {'employee_id' : rec.employee_id.id ,'termination_id' : rec.id , 'type' : 'termination' , 'date' : rec.dismissal_date}]],
                    'default_source': rec.employee_id.department_id.id or False,
                    #'default_destination': rec.destination.id,
                    'termination_id': rec.id,
                    'default_type': 'termination',
                    'default_move_date': rec.dismissal_date,
                    'default_out_source': True,
                }
                res['context'] = data
            else :
                res['res_id'] = rec.move_order_id.id
        return res

    def date_reflect(self, cr, uid, ids, context=None):
        """ 
        reflect date in employee
        """
        write_bool = self.write(cr, uid, ids, { 'state' : 'date_reflect' }, context=context)
        for emp in self.browse(cr, uid, ids, context=context):
            emp.employee_id.write({'end_date':emp.dismissal_date})
        return  write_bool
    
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

    def termination(self, cr, uid, ids, context=None):
        """ 
    Terminate employee service and change state to refuse
        """
        wf_service = netsvc.LocalService("workflow")
        write_bool = self.write(cr, uid, ids, { 'state' : 'refuse' }, context=context)
        for emp in self.browse(cr, uid, ids, context=context):
            if self.check_employee_salary(cr, uid, emp.employee_id.id, emp.dismissal_date) or True :# remove or True
                wf_service.trg_validate(uid, 'hr.employee', emp.employee_id.id , 'refuse', cr)
                emp.employee_id.write({'state':'refuse', 'end_date':emp.dismissal_date})
                delegation_obj = self.pool.get('hr.employee.delegation')
                new_id = delegation_obj.create(cr, uid, {'employee_id':emp.employee_id.id, 'new_state_id':emp.dismissal_type.state_id.id, 'start_date':emp.dismissal_date}, context=context)
                wf_service.trg_validate(uid, 'hr.employee.delegation', emp.employee_id.id , 'approve', cr)
                delegation_obj.write(cr, uid, new_id, {'state':'approve'})
            else:
                raise osv.except_osv(_('ERROR'), _(
                    'Must compute employee salary before terminate his service!'))
        return  write_bool

class hr_employee_location_state(osv.Model):
    _name = "hr.employee.location.state"
    _columns = {
        'name' : fields.char('Name') ,
        'type' : fields.selection([('state','State'),('local','Local'),('village','Village'),('unit','Administrative unit')], string="Type") ,
        'parent_id' : fields.many2one('hr.employee.location.state', 'Parent') ,
    }
class hr_employee_current_living(osv.Model):

    _name = "hr.employee.current.living"
    _order = 'degree_id desc,promotion_date,otherid_seniority'

    _columns = {
        'employee_id': fields.many2one('hr.employee', "Employee", domain="[('state','=','approved')]"),
        'current_living_state' : fields.many2one('hr.employee.location.state', 'Current Living State') ,
        'current_living_local' : fields.many2one('hr.employee.location.state', 'Current Living Local') ,
        'current_living_unit' : fields.many2one('hr.employee.location.state', 'Current Living Unit') ,
        'current_living_village' : fields.many2one('hr.employee.location.state', 'Current Living Village'),
        'date': fields.date("Date"),
        'company_id': fields.many2one('res.company','company'),
        'state': fields.selection([('draft','Draft'),('approved','Approved')], string='State'),
        'otherid_seniority' : fields.related('employee_id', 'otherid_seniority', type='integer',string='otherid seniority', store=True),
        'promotion_date' : fields.related('employee_id', 'promotion_date', type='date',string='promotion date', store=True),
        'degree_id' : fields.related('employee_id', 'degree_id', type='many2one',string='Degree', relation='hr.salary.degree', store=True),
    }
    def _default_company(self,cr,uid,context=None):
        List = []
        user_obj = self.pool.get('res.users')
        user = user_obj.browse(cr ,uid, uid)
        company = False
        if user.company_id:
            company = user.company_id.id
        return company

    _defaults = {
        'company_id' : _default_company,
        'state' : 'draft',
    }

    def approve(self, cr, uid, ids, context=None):
        for rec in self.browse(cr, uid, ids, context=context):
            cr.execute ("""update hr_employee set current_living_state=%s,
            current_living_local=%s,current_living_unit=%s,
            current_living_village=%s 
            where id=%s """%(rec.current_living_state.id,rec.current_living_local.id,rec.current_living_unit.id,
            rec.current_living_village.id,rec.employee_id.id))
            rec.write({'state':'approved'})
        return True
    
    def draft(self, cr, uid, ids, context=None):
        for rec in self.browse(cr, uid, ids, context=context):
            cr.execute ("""select id from hr_employee_current_living 
            where employee_id=%s and id != %s and state='approved' order by date desc"""%(rec.employee_id.id, rec.id))
            
            res = cr.dictfetchall()

            if not res:
                raise osv.except_osv(_('ERROR'), _(
                    'you have to make modification from employee record!'))
            res = [res[0]['id']]


            self.approve(cr, uid, res, context=context)
            rec.write({'state':'draft'})
        return True

class hr_employee(osv.Model):
    _inherit = "hr.employee"

    def _curr_user(self, cr, uid, context=None):
        result = False
        user_obj = self.pool.get('res.users')
        if user_obj.has_group(cr,uid,'base.group_hr_user') or user_obj.has_group(cr,uid,'hr_custom_employee_niss.group_hr_overview_employee_data') or user_obj.has_group(cr,uid,'hr_custom_military.hr_emp_base_military'):
                result = True
        
        return result

    def _curr_id_hr(self, cr, uid, ids, name, args, context=None):
        result = {}
        user_obj = self.pool.get('res.users')
        for emp in self.browse(cr, uid, ids, context=context):
            if user_obj.has_group(cr,uid,'base.group_hr_user') or user_obj.has_group(cr,uid,'hr_custom_employee_niss.group_hr_overview_employee_data') or user_obj.has_group(cr,uid,'hr_custom_military.hr_emp_base_military'):
                result[emp.id] = True
            else:
                result[emp.id] = False
        return result

    _columns = {
        'living_state' : fields.many2one('hr.employee.location.state', 'Living State') ,
        'living_local' : fields.many2one('hr.employee.location.state', 'Living Local') ,
        'living_village' : fields.char('Living Village'),

        'current_living_state' : fields.many2one('hr.employee.location.state', 'Current Living State') ,
        'current_living_local' : fields.many2one('hr.employee.location.state', 'Current Living Local') ,
        'current_living_unit' : fields.many2one('hr.employee.location.state', 'Current Living Unit') ,
        'current_living_village' : fields.many2one('hr.employee.location.state', 'Current Living Village'),
        'employement_qual_id' : fields.many2one('hr.employee.qualification', 'Employement Qualification'),
        'curr_uid_hr': fields.function(_curr_id_hr, type="boolean", string='hr user'),
        'image_lc': fields.char("image"),
      
    }
    def set_image_local(self , cr , uid, employee_id , img_data , context=None):
        save_path = addons.get_module_resource('hr_custom_military', 'static/')
        img_name = str(employee_id)+".png"
        fileTosave = save_path+"/"+img_name
        fh = open(fileTosave, "wb")
        fh.write(img_data.decode('base64'))
        fh.close()
        val = '/hr_custom_military/static/'+img_name
        #self.remove_image(cr, uid , [employee_id])
        self.pool.get("hr.employee").write(cr , uid , [employee_id] , {'image_lc' : val})
        return True



    def remove_image(self , cr , uid , ids , context={}):
        save_path = addons.get_module_resource('hr_custom_military', 'static/')
        for employee in self.pool.get('hr.employee').read(cr,uid , ids , ['image_lc']):
            employee_image = employee['image_lc']
            image_path = save_path + '/'+ employee_image.split('/')[-1]
            try:
                os.remove(image_path)
            except: pass
    

    def check_otherid(self, cr, uid, ids, context=None):
        """ 
        Constrain method to check otherid field

        @return: boolean True or False
        """
        
        for rec in self.browse(cr, uid, ids, context=context):
            if rec.otherid :
                if not rec.otherid.isdigit():
                    raise osv.except_osv(_('ERROR'), _('otherid Must be digit'))
                idss = self.search(cr,uid, [('otherid', '=', rec.otherid),('id','!=',rec.id),('state','=','approved')])
                if idss:
                    raise osv.except_osv(_('ERROR'), _('otherid Must be uniqu'))
                if not rec.emp_code.isdigit():
                    raise osv.except_osv(_('ERROR'), _('Employee Code Must be digit'))
        return True

    _constraints = [
         (check_otherid, '', []),
    ]

    def fields_view_get(self, cr, uid, view_id=None, view_type='form', context=None, toolbar=False, submenu=False):
        #override of fields_view_get in employee to change the String of some fields
        if context is None:
            context={}
        res = super(hr_employee, self).fields_view_get(cr, uid, view_id=view_id, view_type=view_type, context=context, toolbar=toolbar, submenu=submenu)
        type = context.get('default_military_type', False)
        if type:
            doc = etree.XML(res['arch'])
            for node in doc.xpath("//field[@name='otherid']"):
                if type == 'officer':
                    node.set('string', _('Officer Number'))
                elif type == 'soldier':
                    node.set('string', _('soldier Number'))
            for node in doc.xpath("//field[@name='parent_job_id']"):
                if type == 'officer':
                    node.set('string', _('Job groups'))
                elif type == 'soldier':
                    node.set('string', _('Job position groups'))
            for node in doc.xpath("//field[@name='job_id']"):
                if type == 'officer':
                    node.set('string', _('Job'))
                elif type == 'soldier':
                    node.set('string', _('Job position'))
            for node in doc.xpath("//field[@name='file_no']"):
                if type == 'soldier':
                    node.set('string', _('File No'))
            for node in doc.xpath("//field[@name='job_letter_no']"):
                if type == 'soldier':
                    node.set('string', _('Job letter no'))
            for node in doc.xpath("//field[@name='employment_date']"):
                if type == 'officer':
                    node.set('string', _('Employment Date'))
                elif type == 'soldier':
                    node.set('string', _('Start Date'))
            for node in doc.xpath("//label[@for='category_ids']"):
                node.set('string', _('Belong To'))
            res['arch'] = etree.tostring(doc)
        return res


    def unlink(self, cr, uid, ids, context=None):
        """Method that overwrites unlink method and prevents the deletion of employee not in the 'draft' state
           @return: Super unlink method
        """
        for e in self.browse(cr, uid, ids):
            if e.state != 'draft':
                raise osv.except_osv(_('Warning!'), _('You Connot delete records not in Draft state !!'))
        return super(hr_employee, self).unlink(cr, uid, ids, context)


#----------------------------------------
#RE-Employement
#----------------------------------------
class hr_employee_reemployment(osv.Model):
    _inherit ='hr.employee.reemployment'
    _columns = {
        'emp_relation_ids':fields.one2many('hr.employee.family', 'reemployment', "New Relations"),
        'scale_id': fields.many2one('hr.salary.scale', 'Salary Scale'),
    }

    def fields_view_get(self, cr, uid, view_id=None, view_type='form', context=None, toolbar=False, submenu=False):
        #override of fields_view_get to change the String of employee_id fields
        emp_obj=self.pool.get('hr.employee')
        belong_to=False
        if context is None:
            context={}
        res = super(hr_employee_reemployment, self).fields_view_get(cr, uid, view_id=view_id, view_type=view_type, context=context, toolbar=toolbar, submenu=submenu)
        emp=emp_obj.search(cr, uid, [('user_id','=',uid)])
        employee = emp_obj.browse(cr, uid, emp and emp[0] or 0)
        for cat in (emp and employee.category_ids or []):
            if cat.belong_to:
                belong_to=cat.belong_to
        if belong_to:
            doc = etree.XML(res['arch'])
            for node in doc.xpath("//field[@name='employee_id']"):
                if belong_to == 'officer_affairs':
                    node.set('string', _('Officer'))
                elif belong_to == 'soldier_affairs':
                    node.set('string', _('Soldier'))
                else:
                    node.set('string', _('Soldier'))
            for node in doc.xpath("//label[@for='employee_id']"):
                if belong_to == 'officer_affairs':
                    node.set('string', _('Officer'))
                elif belong_to == 'soldier_affairs':
                    node.set('string', _('Soldier'))
                else:
                    node.set('string', _('Soldier'))
            res['arch'] = etree.tostring(doc)
        return res

    def action_done(self, cr, uid, ids, context=None):
        """
        Method for reemployement for ended services employee.

        @return: True 
        """
        emp_obj = self.pool.get('hr.employee')
        wf_service = netsvc.LocalService("workflow")
        process_obj = self.pool.get('hr.process.archive')
        dep_move_obj = self.pool.get('hr.movements.department')
        job_move_obj = self.pool.get('hr.movements.job')
        bonus_move_obj = self.pool.get('hr.movements.bonus')
        degree_move_obj = self.pool.get('hr.movements.degree')


        for record in self.browse(cr, uid,ids):
            if record.employee_id.state=='approved':
               raise osv.except_osv(_('Warning'), _('This employee already has been Re-employment'))
            emp_obj.write(cr, uid, [record.employee_id.id], {'re_employment_date': record.reemployment_date,} , context=context)
            #emp_obj.set_to_draft2(cr, uid, [record.employee_id.id], context)
            #wf_service.trg_validate(uid, 'hr.employee',record.employee_id.id ,'set_to_draft', cr)
            wf_service.trg_validate(uid, 'hr.employee',record.employee_id.id ,'approve', cr)
            vals= {
                   'code':record.employee_id.code,
                   'employee_id':record.employee_id.id,
                   'date': record.reemployment_date ,
                   'approve_date': time.strftime('%Y-%m-%d') ,
                   'company_id':record.company_id.id,
                   'comments':'Reemployement',
                   'associated_reemployment':record.id,
                   
            }

            ### for department movements
            if record.department_id.id!=record.employee_id.department_id.id:
                #vals.update({'reference':'hr.department'+','+str(record.department_id.id),
                #             'previous': record.employee_id.department_id.name,})
                vals.update({
                    'reference':record.department_id.id,
                    })
                #process_id=process_obj.create(cr,uid,vals,context=context)
                process_id = dep_move_obj.create(cr,uid,vals,context=context)
                dep_move_obj.do_approve(cr, uid, [int(process_id)], context)
                #wf_service.trg_validate(uid, 'hr.process.archive',process_id ,'approve', cr)


            ###  for job movements
            if record.job_id.id!=record.employee_id.job_id.id:
                #vals.update({'reference':'hr.job'+','+str(record.job_id.id),
                #              'previous': record.employee_id.job_id.name })
                vals.update({
                    'reference':record.job_id.id,
                    })
                #process_id=process_obj.create(cr,uid,vals,context=context)
                #wf_service.trg_validate(uid, 'hr.process.archive',process_id ,'approve', cr)
                process_id = job_move_obj.create(cr,uid,vals,context=context)
                job_move_obj.do_approve(cr, uid, [int(process_id)], context)

            ### for degree movements
            if record.degree_id.id != record.employee_id.degree_id.id:
                if record.degree_id.sequence > record.employee_id.degree_id.sequence:
                    process_type = 'isolate'
                else:
                    process_type = 'promotion'
                vals.update({
                    'reference':record.degree_id.id,
                    'process_type': process_type,
                    'new_scale_id': record.scale_id.id,
                    'new_bonuse_id': record.bonus_id.id,

                    })
                process_id = degree_move_obj.create(cr,uid,vals,context=context)
                degree_move_obj.do_approve(cr, uid, [int(process_id)], context)

            ### for bonus movements
            if record.degree_id.id == record.employee_id.degree_id.id and record.bonus_id.id != record.employee_id.bonus_id.id:
                vals.update({
                    'reference':record.bonus_id.id,
                    })

                process_id = bonus_move_obj.create(cr,uid,vals,context=context)
                bonus_move_obj.do_approve(cr, uid, [int(process_id)], context)

            self.write(cr, uid, ids, { 'state' : 'done' }, context=context)
        return True


    def onchange_scale_id(self, cr, uid, ids, scale_id, degree_id, context={}):
        """
        """
        vals = {
        'degree_id': False,
        }
        if scale_id:
            if degree_id:
                scale = self.pool.get('hr.salary.degree').browse(cr, uid, degree_id).payroll_id.id
                if scale == scale_id:
                    vals.update({'degree_id': degree_id})


        return {'value': vals}


    def onchange_degree_id(self, cr, uid, ids, degree_id, bonus_id, context={}):
        """
        """
        vals = {
        'bonus_id': False,
        }
        if degree_id:
            if bonus_id:
                degree = self.pool.get('hr.salary.bonuses').browse(cr, uid, bonus_id).degree_id.id
                if degree == degree_id:
                    vals.update({'bonus_id': bonus_id})


        return {'value': vals}


    def onchange_employee_id(self, cr, uid, ids, employee_id, context=None):
        """Method that returns employee's bonus and degree.
           @param employee_id: Id of employee
           @return: Dictionary of values 
        """
        if context is None: context = {}
        res = super(hr_employee_reemployment, self).onchange_employee_id(cr, uid, ids, employee_id, context=context)
        if employee_id:
            emp = self.pool.get('hr.employee').browse(cr, uid, employee_id , context=context)
            res['value'].update({ 'scale_id': emp.payroll_id.id})
        
        return res




#----------------------------------------
#hr job(inherit)
#----------------------------------------
class hr_job(osv.Model):
     _inherit="hr.job"
     _columns = {
        'no_of_recruitment': fields.float(string="Expected In Recruitment", readonly=False,digits=(6, 2)),
        'expected_employees': fields.float(string='Available position',readonly=False,digits=(6, 2)),
         'no_of_employee': fields.float(string="Current Number of Employees",readonly=False,digits=(6, 2)),
     }
     _defaults = {
        'state' : 'open',
    }

#     def check_no_of_emp(self, cr, uid, ids, context=None):
#         return True
    
#     _constraints = [
#          (check_no_of_emp, _('sorry you can not exceed the Max Number of exepected employees'), ['expected_employees']),
#     ]


from openerp.addons.hr.hr import hr_job
class hr_job_custom(hr_job):
    _columns = {
        'name': fields.char('Job Name', size=128, required=True, select=True),

        'no_of_recruitment': fields.float(string="Expected In Recruitment", readonly=False,digits=(6, 2)),
        'expected_employees': fields.float(string='Available position',readonly=False,digits=(6, 2)),
         'no_of_employee': fields.float(string="Current Number of Employees",readonly=False,digits=(6, 2)),

        'employee_ids': fields.one2many('hr.employee', 'job_id', 'Employees', groups='base.group_user'),
        'description': fields.text('Job Description'),
        'requirements': fields.text('Requirements'),
        'department_id': fields.many2one('hr.department', 'Department'),
        'company_id': fields.many2one('res.company', 'Company'),
        'state': fields.selection([('open', 'No Recruitment'), ('recruit', 'Recruitement in Progress')], 'Status', readonly=True, required=True,
            help="By default 'In position', set it to 'In Recruitment' if recruitment process is going on for this job position."),
    }
    hr_job._columns = _columns




    
