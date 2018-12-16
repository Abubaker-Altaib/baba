# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################
from openerp.osv import fields, osv, orm
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp
import time
import netsvc
#import decimal_precision as dp
#from admin_affairs.copy_attachments import copy_attachments as copy_attachments


#----------------------------------------------------------
# Accident Configuration
#----------------------------------------------------------

class accident_type(orm.Model):
    
    _name = "accident.type"
    _description = 'Accident Type'
    
    _columns = {
                'name': fields.char('Accident Type', size=64 ,required=True),
                'code': fields.integer('Code',size=5), 
               }
       
#----------------------------------------------------------
# Buliding accident 
#----------------------------------------------------------
class building_accident(orm.Model):

    def create(self, cr, user, vals, context=None):
        """
        Create new entry sequence for every building accident Record
        @param cr: cursor to database
        @param user: id of current user
        @param vals: list of record to be process
        @param context: context arguments, like lang, time zone
        @return: return a result 
      	"""
        if ('name' not in vals) or (vals.get('name')=='/'):  
            vals.update({'name': self.pool.get('ir.sequence').get(cr, user, 'building.accident')})
        return super(building_accident, self).create(cr, user, vals, context)


    def copy(self, cr, uid, id, default=None, context=None):
        """ Override copy function to edit sequence """
        if default is None:
            default = {}
        if context is None:
            context = {}
        default.update({
            'name': self.pool.get('ir.sequence').get(cr, uid, 'building.accident'),
            'maintenance_id': False,
            'maintenance_creation': False
        })
        return super(building_accident, self).copy(cr, uid, id, default, context)

    def onchange_building_id(self,cr,uid,ids,building_id,context=None):
       for building in self.browse(cr,uid,ids,context=context):
            if building.lines_ids:
               delete = self.pool.get('accident.lines').unlink(cr,uid,[line.id for line in building.lines_ids],context=context)
       return True

    _name = "building.accident"
    _columns = {
    'name': fields.char('Reference', size=64, select=True, required=True, readonly=True  , help="unique number of the building accident,computed automatically when occasion services record is created"),
    'date' : fields.date('Date',readonly=True),
    'accident_date' : fields.date('Accident Date',required=True ,states={'done':[('readonly',True)],'cancel':[('readonly',True)]}),
    'building_id': fields.many2one('building.building','Building',required=True ,states={'done':[('readonly',True)],'cancel':[('readonly',True)]}),
    'user_id':  fields.many2one('res.users', 'Responsible', readonly=True , ),
    'notes': fields.text('Notes', size=256 ,states={'done':[('readonly',True)],'cancel':[('readonly',True)]}),
    'company_id': fields.many2one('res.company', 'Company',states={'done':[('readonly',True)],'cancel':[('readonly',True)]}),
    'estimated_cost':fields.float('Estimated Cost',size=64,states={'done':[('readonly',True)],'cancel':[('readonly',True)]}),
    'notify_insurance_date' : fields.date('Insurance Date',help="This is the date you notify The Insurance Company",states={'done':[('readonly',True)],'cancel':[('readonly',True)]}),
    'coverage_date' : fields.date('Coverage Date',states={'done':[('readonly',True)],'cancel':[('readonly',True)]}),
    'repayment_cost':fields.float('Repayment Cost',size=64,states={'done':[('readonly',True)],'cancel':[('readonly',True)]}),
    'partner_id':fields.many2one('res.partner','Partner',states={'done':[('readonly',True)],'cancel':[('readonly',True)]}),
    'state': fields.selection([('draft', 'Draft'),
			       ('confirm', 'Confirm '),
			       ('done', 'Done'),
			       ('cancel', 'Cancel'), ] ,'State', readonly=True, select=True),
    'insurance_selection':fields.selection([('yes','Yes'),('no','No'),],'Insured',select=True,help="Is your building Insured?. if insured you can add insurance information, if not insured you can add maintenance information.",states={'done':[('readonly',True)],'cancel':[('readonly',True)]},required=True),
    'maintenance_selection':fields.selection([('automatic','Automaticly'),('manual','Manual'),('none','None')],'Maintenance order',select=True,states={'done':[('readonly',True)],'cancel':[('readonly',True)]},help="How you want to create your manitenance order:\n1-Automaticly:means that the system will create maintenance order automatic when the  building accident state is done.\n2-Manual:means that the user will create the maintenace order by himsefl either by the button above or from maintenace request form.\n3-None: means that the user dosn't want to create maintenance order"),
    'maintenance_creation': fields.boolean('Maintenance order created',readonly=True,help="Maintenance order creation:\n1-True: Maintenace order has been created.\n2-False: Maintenance order is not created yet"),
    'maintenance_id': fields.many2one('building.maintenance','Maintenance No', size=125,readonly=True),
    'lines_ids':fields.one2many('accident.lines', 'accident_id' , 'Items',states={'done':[('readonly',True)],'cancel':[('readonly',True)]}), 

    }
    
    _defaults = {
        'name': lambda self, cr, uid, context: '/',
        'user_id': lambda self, cr, uid, context: uid,
        'date': lambda *a: time.strftime('%Y-%m-%d'),
	'state':'draft',
	'maintenance_creation':False,
	'maintenance_selection':'automatic',
 	'company_id': lambda self, cr, uid, c: self.pool.get('res.users').browse(cr, uid, uid, context=c).company_id.id,
                }

    _sql_constraints = [
        ('accident_name_uniq', 'unique(name)', 'Building Accident Reference must be unique !'),
        ]

    def confirm(self, cr, uid, ids, context=None):
        for record in self.browse(cr, uid, ids, context=context):
		if not record.lines_ids:
                	raise orm.except_orm(_('Error !'), _('You can not confirm the record without Building accident lines.'))             
        self.write(cr, uid, ids, {'state':'confirm'})
        return True

    def create_maintenance_order(self,cr,uid,ids,context=None):
        maintenance_order_obj = self.pool.get('building.maintenance')
        maintenance_order_line_obj = self.pool.get('building.maintenance.line')
        for record in self.browse(cr, uid, ids, context=context):
		if record.estimated_cost < 1 :
                	raise orm.except_orm(_('Error !'), _('You can not confirm this order without estimated cost.')) 
        # Creating maintenance order 
                maintenance_order_id = maintenance_order_obj.create(cr, uid, {
                        'date': time.strftime('%Y-%m-%d'),
			'building_id':record.building_id.id,
			'notes':record.notes,
			'cost':record.estimated_cost,
                            }, context=context)
        #Creating maintenance order lines
		for lines in record.lines_ids :
                	maintenance_order_lines = maintenance_order_line_obj.create(cr, uid, {
                        	'maintenance_id': maintenance_order_id,
				'item_id':lines.item_id.id,
				'qty':lines.qty,
                            }, context=context)
        self.write(cr, uid, ids, {'state':'done','maintenance_id':maintenance_order_id,'maintenance_creation':True})
        return True

    def done(self,cr,uid,ids,context=None):
        for record in self.browse(cr, uid, ids, context=context):
		if record.insurance_selection == 'no' and record.maintenance_selection == 'automatic':
			        maintenance_id = self.create_maintenance_order(cr, uid, ids, context)
                self.write(cr, uid, ids, {'state':'done'},context=context)
        return True

    def cancel(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state':'cancel'})
        return True

    def ir_action_cancel_draft(self, cr, uid, ids, context=None):
        # Reset the Building Accident 
        if not len(ids):
            return False
        wf_service = netsvc.LocalService("workflow")
        for id in ids:
            self.write(cr, uid, id, {'state':'draft'})
            wf_service.trg_delete(uid, 'building.accident', id, cr)            
            wf_service.trg_create(uid, 'building.accident', id, cr)
        return True

    def unlink(self, cr, uid, ids, context=None):
        """delete the Building Accident record,
        and create log message to the deleted record
        @return: res,
        """
        for rec in self.browse(cr, uid, ids, context=context):
            if record.state not in  ['draft','cancel']:
                 raise osv.except_osv(_('Invalid action !'), _('In order to delete a building accident record, you must first cancel it or set it to draft state .'))
            message = _("Buliding Accident '%s' has been deleted.") % rec.name
            self.log(cr, uid, ids, message)
        return super(building_accident, self).unlink(cr, uid, unlink_ids, context=context)

#----------------------------------------------------------
# Accident lines
#----------------------------------------------------------

class accident_lines(orm.Model):
    
    _name = "accident.lines"
    _description = 'Accident lines'

    def onchange_qty(self,cr,uid,ids,building_id,item_id,context=None):
       domain= {}
       if building_id and not item_id:
            building = self.pool.get('building.building').browse(cr,uid,building_id,context=context)
            domain={'item_id':[('id','in',[item.item_id.id for item in building.item_ids])]}
       return {'domain': domain}

    def check_qty(self, cr, uid,ids,context=None):
        for line in self.browse(cr,uid,ids,context=context):
           if line.accident_id.building_id:
              item_qty = sum(item.qty for item in line.accident_id.building_id.item_ids if item.item_id.id == line.item_id.id)
              item_line = self.search (cr,uid,[('accident_id','=',line.accident_id.id),('item_id','=',line.item_id.id)],context=context)
              total_item_qty = item_line and sum(item.qty for item in self.browse(cr,uid,item_line,context=context))
              if total_item_qty > item_qty:
                 raise orm.except_orm(_('Error !'),_('sorry you can not exceed item quantity of the selected building %s' % (item_qty)))
        return True
    
    _columns = {
                'name': fields.char('Accident Description', size=256,),
                'item_id': fields.many2one('item.item', 'Item', required=True),
                'qty': fields.float('Qty', required=True),        
                'accident_type': fields.many2one('accident.type','Accident Type',required=True),
                'accident_id': fields.many2one('building.accident', 'Building Accident', required=True),
               }
    _defaults = {
        'qty': 1.0,
                }
    
    _sql_constraints = [
       ('building_item_uniq', 'unique(item_id, accident_id, accident_type)', 'Item must be unique per Accident type! '),
       ('qty_check', 'Check (qty > 0 )', 'The item quantity must be greater than zero'),
            ] 

    _constraints = [
        (check_qty, 'sorry you can not exceed item quantity of the selected building', ['qty']),
                    ]
