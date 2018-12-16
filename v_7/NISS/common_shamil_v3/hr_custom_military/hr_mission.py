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


class hr_mission_category(osv.osv):
    _inherit = "hr.mission.category"
   
    _defaults = {
        'company_id':  lambda self, cr, uid, context: self.pool.get('res.users').browse(cr, uid, uid, context=context).company_id.id,
    }

class hr_employee_mission_line(osv.osv):
    _inherit = "hr.employee.mission.line"
    _columns = {
		'move_order_id' : fields.many2one('hr.move.order.line' , string="Move Order" ,domain=[('mission_id' , '=' , False) , ('type' , 'in' , ['mission', "transmission","opreation" ])]) , 
	 	'company_id': fields.many2one('res.company','company'),
	 	}
    _defaults = {
        'company_id':  lambda self, cr, uid, context: self.pool.get('res.users').browse(cr, uid, uid, context=context).company_id.id,

    }
    def fields_view_get(self, cr, uid, view_id=None, view_type='form', context=None, toolbar=False, submenu=False):
        #override of fields_view_get to change the String of employee_id fields
        emp_obj=self.pool.get('hr.employee')
        belong_to=False
        if context is None:
            context={}
        res = super(hr_employee_mission_line, self).fields_view_get(cr, uid, view_id=view_id, view_type=view_type, context=context, toolbar=toolbar, submenu=submenu)
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


class hr_mission(osv.Model):
	_inherit = 'hr.employee.mission'
	_columns = {
		'move_order_id' : fields.many2one('hr.move.order' , string="Move Order" ,domain=[('mission_move_id' , '=' , False) , ('type' , 'in' , ['mission', "transmission","opreation" ])]) , 
	 	'need_move_order' : fields.boolean('Need Move Orders' , help='when True (move order button) will appear on UI') ,
	 	'move_order_dest' : fields.many2one( 'hr.department','Move Order Destination') ,
		'arch_flag' : fields.boolean('archive flag') ,
	 }
	_defaults = {
       'company_id':  lambda self, cr, uid, context: self.pool.get('res.users').browse(cr, uid, uid, context=context).company_id.id,

    }

	def fields_view_get(self, cr, uid, view_id=None, view_type='form', context=None, toolbar=False, submenu=False):
	    #override of fields_view_get to change the String of employee_id fields
	    emp_obj=self.pool.get('hr.employee')
	    belong_to=False
	    if context is None:
	        context={}
	    res = super(hr_mission, self).fields_view_get(cr, uid, view_id=view_id, view_type=view_type, context=context, toolbar=toolbar, submenu=submenu)
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

	def name_search(self, cr, uid, name, args=None, operator='ilike', context=None, limit=100):
		if context is None:
			context = {}
		if 'default_type' in context and 'employee_id' in context:
			line_obj = self.pool.get('hr.employee.mission.line')
			lines_ids = line_obj.search(cr, uid, [('employee_id','=', context['employee_id'])])
			missions_ids = line_obj.read(cr, uid, lines_ids, ['emp_mission_id'])
			missions_ids = [x['emp_mission_id'][0] for x in missions_ids]
			recs_ids = self.search(cr, uid, [('id', 'in', missions_ids), ('state', '=', 'close'), ('type', '=', context['default_type'])])
			args.append(('id', 'in', recs_ids))
		return super(hr_mission, self).name_search(cr, uid, name, args=args, operator=operator, context=context, limit=limit)


	def _prepare_move_order_lines(self , lines , mission_type):
	 	data = []
	 	for line in lines:
	 		if not line.move_order_id :
	 			obj = [0 , 0 , {	
	 				'employee_id' : line.employee_id.id ,
	 				'mission_id' : line.id ,
	 				'date' : line.start_date ,
	 				'type' : mission_type ,
	 				  }]
	 			data.append(obj)
	 	return data

	def create_move_order(self, cr, uid, ids,move_type,context={}):
		for rec in self.browse(cr , uid , ids , context):
			if not rec.move_order_id :
				emps = []
				lines = self._prepare_move_order_lines(rec.mission_line , move_type)
				#if rec.mission_leader.id : emps.append(rec.mission_leader.id)
				for line in rec.mission_line :
					if line.employee_id.id not in emps:
						emps.append(line.employee_id.id)
					data = {
		                'default_source' : rec.department_id and rec.department_id.id or False ,
		                'default_destination' : rec.move_order_dest and rec.move_order_dest.id or False,
		                'default_type' : move_type ,
		                'default_move_date' : time.strftime('%Y-%m-%d'),
		                'default_mission_move_id' : rec.id ,
		                'default_out_source' : True ,
		                'default_move_order_line_ids' : lines ,
		                'mission_id' : rec.id,
					}
					dummy, view_id = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'hr_custom_military', 'hr_move_order_with_footer')
					return {
		                'name': _('Move Order'),
		                'view_type': 'form',
		                'view_id': view_id,
		                'view_mode': 'form',
		                'res_model': 'hr.move.order',
		                'type': 'ir.actions.act_window',
		                'context' : data,
		                'target': 'new',
		            }
			else :
				dummy, view_id = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'hr_custom_military', 'hr_move_order_with_footer')
				return {
		                'name': _('Move Order'),
		                'view_type': 'form',
		                'view_id': view_id,
		                'view_mode': 'form',
		                'res_model': 'hr.move.order',
		                'type': 'ir.actions.act_window',
		                'res_id' : rec.move_order_id.id,
		                'target': 'new',
		            }

	def check_need_move_order(self , cr , uid ,ids ,context=None):
		flag = False
		move_order_model = self.pool.get('hr.move.order.line')
		for rec in self.browse(cr , uid , ids) :
			for line in rec.mission_line:
				if line.move_order_id :
					move_order_model.write(cr , uid , [line.move_order_id.id] , {'mission_id' : line.id})
				else :
					flag = True
		if flag:
			return self.write(cr , uid , ids , {'need_move_order' : True})
		return self.write(cr , uid , ids , {'need_move_order' : False})

	def confirm_mission(self , cr , uid , ids , context=None):
		for obj_id in ids :
			self.check_need_move_order(cr , uid , ids , context)
			wf_service = netsvc.LocalService("workflow")
			wf_service.trg_validate(uid, 'hr.employee.mission', obj_id, 'confirm_mission', cr)
		return True

	def confirm_transmission(self,cr , uid , ids , context=None):
		for obj_id in ids :
			self.check_need_move_order(cr , uid , ids , context)
			wf_service = netsvc.LocalService("workflow")
			wf_service.trg_validate(uid, 'hr.employee.mission', obj_id, 'confirm_transmission', cr)
		return True

	def mission_move_order(self, cr, uid, ids,context={}):
		return self.create_move_order(cr , uid , ids ,'mission' , context={})

	def transmission_move_order(self, cr, uid, ids,context={}):
		return self.create_move_order(cr , uid , ids ,'transmission' , context={})

	def opreation_move_order(self, cr, uid, ids,context={}):
		return self.create_move_order(cr , uid , ids ,'opreation' , context={})

	def _check_move_order_employee(self, cr, uid, ids, context=None):
		obj = self.browse(cr , uid , ids)[0]
		if obj.move_order_id :
			miss_id = obj.id
			move_id = obj.move_order_id.id
			miss_emps = [i.employee_id.id for i in obj.mission_line ]
			move_emps = [i.employee_id.id for i in obj.move_order_id.move_order_line_ids]
			if set(miss_emps) != set(move_emps) : 
				raise osv.except_osv(_('warning') , _('employee entries must be same as enries in move order screen!!'))
				return False
		return True


	_constraints = [ (_check_move_order_employee,"employee entries must be same as enries in move order screen!!", ['move_order_id' , 'mission_line']),]

