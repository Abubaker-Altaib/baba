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



class employee_mission_line(osv.osv):
    _inherit = "hr.employee.mission.line"
    _columns = {
		'move_order_id' : fields.many2one('hr.move.order.line' , string="Move Order" ,domain=[('mission_id' , '=' , False) , ('type' , 'in' , ['mission', "transmission","opreation" ])]) , 
	 	}


class hr_mission(osv.Model):
	_inherit = 'hr.employee.mission'
	_columns = {
		'move_order_id' : fields.many2one('hr.move.order' , string="Move Order" ,domain=[('mission_move_id' , '=' , False) , ('type' , 'in' , ['mission', "transmission","opreation" ])]) , 
	 	'need_move_order' : fields.boolean('Need Move Orders' , help='when True (move order button) will appear on UI') ,
	 	'move_order_dest' : fields.many2one( 'hr.department','Move Order Destination') ,
	 	'road_days' : fields.integer('Road Days') ,
	 	'source' : fields.char('Source') ,
	 	'return_place' : fields.char('Return To') , 
	 }

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
			move_emps = [i.id for i in obj.move_order_id.employee_ids ]
			if set(miss_emps) != set(move_emps) : 
				return False
		return True


	#_constraints = [ (_check_move_order_employee,"employee entries must be same as enries in move order screen!!", ['move_order_id' , 'mission_line']),]

