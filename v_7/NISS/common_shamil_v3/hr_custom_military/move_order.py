# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################
from openerp.osv import fields, osv, orm
from openerp.tools.translate import _
from openerp import netsvc
from datetime import datetime
import time
import traceback
from lxml import etree


move_order_types = [
    ('opreation', 'Opreation'),
    ('mission','Mission'),
    ('transmission', 'Transmission'),
    ('movement','Movement'),
    ('commision', 'Commision'),
    ('append', 'Append'),
    ('join', 'Join to Department'),
    ('course', 'Course Attending'),
    ('task', 'Task'),
    ('append_end', 'Append End'),
    ('delegation_end', 'Delegation End'),
    ('termination','Termination')
]

# 'type' : ('related.model.name' , 'related_field')
move_order_types_dict = {
    'opreation': ('hr.employee.mission.line' , 'mission_id' ,'move_order_id'),
    'mission':('hr.employee.mission.line' , 'mission_id' ,'move_order_id'),
    'transmission': ('hr.employee.mission.line' ,'mission_id' ,'move_order_id'),
    'movement':('hr.movements.department' ,'movement_id' , 'move_order_line_id'),
    'commision': ('hr.commision' ,  'commision_id','move_order_line_id'),
    'append': ('hr.append' , 'append_id','move_order_line_id' ),
    'termination':('hr.employment.termination','termination_id','move_order_line_id'),
}


class Move_order_line(osv.Model):
    _name = 'hr.move.order.line'
    _columns = {
        'mission_id' : fields.many2one('hr.employee.mission.line' , string="Mission") ,        
        'move_order_id' : fields.many2one('hr.move.order' , string='Move Order', ondelete='cascade'),
        'commision_id' : fields.many2one('hr.commision' , string="Commision") ,                
        'movement_id' : fields.many2one('hr.movements.department' , string="Movement") ,
        'append_id' : fields.many2one('hr.append' , string="Append") ,  
        'termination_id' : fields.many2one('hr.employment.termination' , string="Termination") ,                              
        'employee_id' : fields.many2one('hr.employee' , string='Employee'),
        'type' : fields.selection(move_order_types , string='Purpose'),
        'date' : fields.date('Date') ,
        'company_id': fields.related('move_order_id', 'company_id', relation='hr.department', type="many2one",string="Company"),

    }

    def _check_duplicate(self, cr, uid, ids, context=None):
        for rec in self.browse(cr, uid, ids, context=context):
            if self.search(cr, uid, [
                ('id','!=',rec.id),
                ('employee_id','=',rec.employee_id.id),
                ('type','=',rec.type),
                ('date','=',rec.date)]):
                raise osv.except_osv(_('ValidateError'),
                                     _("you can not have two moves from the same type in the same date"))
        return True
    _constraints = [
        (_check_duplicate, '', ['employee_id','type','date']),
    ]

    def fields_view_get(self, cr, uid, view_id=None, view_type='form', context=None, toolbar=False, submenu=False):
        #override of fields_view_get to change the String of employee_id fields
        emp_obj=self.pool.get('hr.employee')
        belong_to=False
        if context is None:
            context={}
        res = super(Move_order_line, self).fields_view_get(cr, uid, view_id=view_id, view_type=view_type, context=context, toolbar=toolbar, submenu=submenu)
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
        return ids and [(item.id,item.move_order_id and "%s-%s-%s" % (item.move_order_id.source.name , item.move_order_id.destination.name
 , item.move_order_id.date) or '') for item in self.browse(cr, uid, ids, context=context)] or []
    def onchange_line(self , cr , uid , ids ,order_type ,employee_id,move_date , context=None):
        if not employee_id : return {}
        try:
                res = {}
                if order_type in ['mission' , 'opreation' , 'transmission']:
                    condition1 = ('start_date' , '<=' , move_date)
                    condition2 = ('end_date' , '>' , move_date)
                    if order_type == 'mission' :
                        mission_ids = self.pool.get('hr.employee.mission').search(cr , uid , [('state' , 'not in' , ['draft', 'refused' , 'closed']) , ('type' , '=' , '1')])
                        res['domain'] = {'mission_id' : [ ('move_order_id' , '=' , False) , ('employee_id' , '=' , employee_id),('emp_mission_id' , 'in' , mission_ids), condition1 , condition2]}
                    if order_type == 'transmission' :
                        mission_ids = self.pool.get('hr.employee.mission').search(cr , uid , [('state' , 'not in' , ['draft', 'refused' , 'closed']) , ('type' , '=' , '3')])
                        res['domain'] = {'mission_id' : [ ('move_order_id' , '=' , False), ('employee_id' , '=' , employee_id), ('emp_mission_id' , 'in' , mission_ids), condition1 , condition2]}
                    elif order_type == 'opreation' :
                        mission_ids = self.pool.get('hr.employee.mission').search(cr , uid , [('state' , 'not in' , ['draft', 'refused' , 'closed']) , ('type' , '=' , '2')])
                        res['domain'] = {'mission_id' : [ ('move_order_id' , '=' , False), ('employee_id' , '=' , employee_id), ('emp_mission_id' , 'in' , mission_ids), condition1 , condition2]}
                elif order_type == 'movement' :
                    res['domain'] = {'movement_id' : [('employee_id' , '=' , employee_id) , ('move_order_line_id' , '=' , False) , ('state' , '=' , 'approved') , ('approve_date' , '<=' , move_date)]}
                elif order_type == 'append' :
                    res['domain'] = {'append_id' : [('move_order_line_id' , '=' , False), ('employee_id' , '=' , employee_id),('state' , '=' , 'confirm') , ('start_date' , '<=' , move_date),('end_date' , '>' , move_date)]}
                elif order_type == 'commision' :
                    res['domain'] = {'commision_id' : [('move_order_line_id' , '=' , False), ('employee_id' , '=' , employee_id) , ('state' , '=' , 'validate3') , ('date' , '<=' , move_date)]}
                elif order_type == 'termination' :
                    res['domain'] = {'termination_id' : [('move_order_line_id' , '=' , False), ('employee_id' , '=' , employee_id) , ('state' , '=' , 'refuse') , ('dismissal_date' , '<=' , move_date)]}
                return res
        except Exception: 

            traceback.print_exc()

class hr_move_order(osv.Model):

    def unlink(self , cr , uid , ids , context=None):
        for i in self.browse(cr , uid , ids):
            for line in i.move_order_line_ids:
                line.unlink()
        return super(hr_move_order , self).unlink(cr , uid , ids , context)


    _name = 'hr.move.order'
    _columns = {
        'source' : fields.many2one('hr.department' ,string="From", states={'confirm': [('readonly', True)]}) ,
        'destination' : fields.many2one('hr.department' ,string="To" , states={'confirm': [('readonly', True)]}) ,
        #'reason' : fields.char('Reason' , size=64, states={'confirm': [('readonly', True)]}) ,
        'weapon' : fields.char('Weapon' , size=64, states={'confirm': [('readonly', True)]}) ,
        'ammu' : fields.char('Ammunition' , size=64, states={'confirm': [('readonly', True)]}) ,
        'clothes' : fields.char('Clothes' , size=64, states={'confirm': [('readonly', True)]}) ,
        'method' : fields.char('Travel Method' , size=64, states={'confirm': [('readonly', True)]}) ,
        'state' : fields.selection([('draft' , 'Draft') , ('confirm' , 'Confirmed'), ('arrive' , 'Arrived')] , string="State", states={'confirm': [('readonly', True)]}),
        'date' : fields.date('Date', required=True, states={'confirm': [('readonly', True)]}) ,
        'move_date' : fields.date('Move Date' ,  states={'confirm': [('readonly', True)]}) ,
        'notes' : fields.text('Notes') ,
        'dest_manger' : fields.char(string="Destination Manager" , help="Destination department manager", states={'confirm': [('readonly', True)]}),
        'source_manger' : fields.char(string="Source Manager" , help="Source department manager", states={'confirm': [('readonly', True)]}),       
        'employee_ids' : fields.many2many('hr.employee' , 'hr_employee_move_orders', string="Employees" ,required=True , states={'confirm': [('readonly', True)]},domain=[('state' , '=' , 'approved')]),
        'mission_move_id' : fields.many2one('hr.employee.mission' , string="Related Process", states={'confirm': [('readonly', True)]}) ,        
        'commision_move_id' : fields.many2one('hr.commision' , string="Related Process", states={'confirm': [('readonly', True)]}) ,                
        'append_id' : fields.many2one('hr.append' , string="Related Process", states={'confirm': [('readonly', True)]}) ,
        'termination_id' : fields.many2one('hr.employment.termination' , string="Related Process", states={'confirm': [('readonly', True)]}) ,                        
        'type' : fields.selection(move_order_types , string="Purpose", states={'confirm': [('readonly', True)]}),
        'out_source' : fields.boolean('Out Source' , help="True if the move order was created from another process"),
        'move_order_line_ids' : fields.one2many('hr.move.order.line' ,  'move_order_id' ,string="Related Process", states={'confirm': [('readonly', True)]}) ,        
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
        'date': time.strftime('%Y-%m-%d'),
        'state': 'draft',
        'company_id' : _default_company,
    }

    def _check_lines(self, cr, uid, ids, context=None):
        for rec in self.browse(cr, uid, ids, context=context):
            if not rec.move_order_line_ids:
                raise osv.except_osv(_('ValidateError'),
                                     _("no employees entered"))
        return True
    _constraints = [
        (_check_lines, '', []),
    ]


    def get_department_manger(self , cr , uid , department_id , context=None):
        for rec in self.pool.get('hr.department').browse(cr , uid , [department_id]) :
            name = _('مدير') + ' '+ (rec.cat_id and rec.cat_id.name + ' ' or "") +rec.name
            return name            

    def on_change_source(self , cr , uid , ids , department_id , context=None):
        res = {}
        if department_id :
            manger_name = self.get_department_manger(cr , uid , department_id)
            res = {
                'value' : {
                    'source_manger' : manger_name,
                },
            }
        return res

    def on_change_dest(self , cr , uid , ids , department_id , context=None):
        res = {}
        if department_id :
            manger_name = self.get_department_manger(cr , uid , department_id)
            res = {
                'value' : {
                    'dest_manger' : manger_name,
                },
            }
        return res

    def create(self , cr , uid , vals , context=None):
        obj = super(hr_move_order , self).create(cr , uid , vals , context)
        for rec in self.browse(cr , uid , [obj]): 
            if rec.out_source :
                if rec.type in ['transmission' , 'mission' , 'opreation'] :
                    self.pool.get('hr.employee.mission').write(cr , uid , [context['mission_id']] , {'move_order_id' : obj})
                    #process_id = rec.mission_move_id.id
                    #model = self.pool.get('hr.employee.mission').write(cr , uid , [process_id] , {'move_order_id' : obj})
                elif rec.type == 'movement' :
                    movement_id = context['movement_id']
                    self.pool.get('hr.movements.department').write(cr , uid , [movement_id] , {'move_order_id' : obj})
                elif rec.type == 'commision':
                    commision_id = context['commision_id']
                    self.pool.get('hr.commision').write(cr , uid , [commision_id] , {'move_order_id' : obj})
                elif rec.type == 'append':
                    append_id = context['append_id']
                    self.pool.get('hr.append').write(cr , uid , [append_id] , {'move_order_id' : obj})
                elif rec.type == 'termination':
                    termination_id = context['termination_id']
                    self.pool.get('hr.employment.termination').write(cr , uid , [termination_id] , {'move_order_id' : obj})
                    for line in rec.move_order_line_ids:
                        type_obj = rec.type in move_order_types_dict and move_order_types_dict[rec.type] or False
                        if type_obj and line[type_obj[1]]:
                            self.link_2_model(cr , uid , type_obj[0] , type_obj[2],line[type_obj[1]].id , line.id)
        return obj

    def onchange_type(self , cr , uid , ids ,move_type ,move_date,lines ,context=None):
        try :
            if lines:
                flag = True
                for i in lines:
                    if i[0] == 0 or i[0] == 4 :
                        val = not ids and lines[0][2]['type'] or  self.browse(cr, uid , ids)[0].type
                        return {
                            'value' : {
                                'type' : val ,
                            } ,
                            'warning' : {
                                'title': _("Type Switch Warning"),
                                'message': _("Please Delete Move Order Lines Before change Type"),
                            }
                        }
            return {}
        except : 
            print "############# ERoRR def onchange_type at hr_move_order"
            traceback.print_exc()
            return {}
    def onchange_related_process(self , cr , uid , ids , val , model_name , context=None):
        if ids and val:
            self.pool.get(model_name).write(cr , uid , [val] , {'move_order_id' : ids[0]})
        return True

    def name_get(self, cr, uid, ids, context=None):
        return ids and [(item.id, "%s-%s-%s" % (item.source.name , item.destination.name , item.date)) for item in self.browse(cr, uid, ids, context=context)] or []

    def link_2_model(self , cr , uid ,model_name , field_name,res_id ,line_id ):
        return self.pool.get(model_name).write(cr , uid , [res_id] , {field_name : line_id})
     
    def do_arrive(self ,cr , uid , ids , context=None):
        return self.write(cr , uid , ids , {'state' : 'arrive'})

    def do_confirm(self, cr , uid , ids , context=None):
        for rec in self.browse(cr , uid , ids):
            if rec.type :
                for line in rec.move_order_line_ids :
                    type_obj = rec.type in move_order_types_dict and move_order_types_dict[rec.type] or False
                    if type_obj and line[type_obj[1]]:
                        self.link_2_model(cr , uid , type_obj[0] , type_obj[2],line[type_obj[1]].id , line.id)
        return self.write(cr , uid, ids , {'state' : 'confirm'})
