# -*- coding: utf-8 -*-
##############################################################################
#
# NCTR, Nile Center for Technology Research
# Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##########################################################################

from openerp.osv import fields,orm
import time
from openerp import netsvc
from openerp.tools.translate import _

#----------------------------------------
# Class building maintenance type
#----------------------------------------
class building_maintenance_type(orm.Model):
    _name = "building.maintenance.type"
    _description = 'building maintenance type'
    _columns = {
                'name': fields.char('Name', size=64, required=True ),
               } 

#----------------------------------------
# Class building maintenance order
#----------------------------------------
class building_maintenance(orm.Model):
    _name = "building.maintenance"
    _description = 'building maintenance order'
  
    def create(self, cr, user, vals, context=None):
        """
        Create new entry sequence for every new building maintenance order Record
        @param vals: record to be created
        @return: return a result that create a new record in the database
          """
        if ('name' not in vals) or (vals.get('name')=='/'):  
            vals['name'] = self.pool.get('ir.sequence').get(cr, user, 'building.maintenance')
        return super(building_maintenance, self).create(cr, user, vals, context) 

    def onchange_building_id(self,cr,uid,ids,building_id,context=None):
       for building in self.browse(cr,uid,ids,context=context):
            if building.maintenance_lines:
               delete = self.pool.get('building.maintenance.line').unlink(cr,uid,[line.id for line in building.maintenance_lines], context=context)
       return True

    _order = "name desc"
    _columns = {
    'name': fields.char('Reference', size=64, required=True, select=True, readonly=True, help="unique number of the building maintenance "),
    'date' : fields.date('Date',required=True, states={'done': [('readonly', True)]}),
    'maintenance_type':  fields.many2one('building.maintenance.type', 'Maintenance type', states={'confirmed':[('required',True)],'done':[('required',True)],'done': [('readonly', True)]}),
    'partner_id':fields.many2one('res.partner', 'Partner', states={'confirmed':[('required',True)],'done':[('required',True)],'done':[('readonly',True)]}),
    'cost': fields.float('Cost',readonly=True, required=True, states={'draft':[('readonly',False)],'confirmed':[('readonly',False)]}),    
    'building_id': fields.many2one('building.building','Building', required=True, states={'done': [('readonly', True)]}),
    'company_id': fields.many2one('res.company','Company',required=True, states={'done': [('readonly', True)]}),
    'user_id':  fields.many2one('res.users', 'Responsible', readonly=True ),    
    'state': fields.selection([('draft', 'Draft'),
                               ('cancel', 'Cancelled'),
                               ('confirmed', 'Confirmed'),
                               ('done', 'Done'),
                                ],'State', readonly=True, select=True),
    'notes': fields.text('Notes', size=256 ), 
    'warranty_end_date' : fields.date('Warranty end date', help="The end date of maintenance warranty", states={'done': [('readonly', True)]}),
    'maintenance_lines':fields.one2many('building.maintenance.line', 'maintenance_id' , 'maintenance Lines', readonly=True, states={'draft':[('readonly',False)],'confirmed':[('readonly',False)]}),
    }
    
    _sql_constraints = [
        ('name_uniq', 'unique(name)', 'building maintenance reference must be unique !'),
        ]
    
    _defaults = {
                'name':'/',
                'date':time.strftime('%Y-%m-%d'),
                'company_id': lambda self, cr, uid, c: self.pool.get('res.company')._company_default_get(cr, uid, 'building.maintenance', context=c),
                'state': 'draft',
                'user_id': lambda self, cr, uid, context: uid,
                }
    
    _sql_constraints = [
        ('qty_check', 'check(qty > 0)', 'Item quantity must be bigger than zero!'),
        ]
 
    def _check_cost(self, cr, uid, ids, context=None):
        for order in self.browse(cr, uid, ids, context=context):
            if order.state in ['confirmed','done'] and order.cost <= 0:
                return False
        return True
    
    _constraints = [
        (_check_cost, 'Alert! , Cost must be greater than zero', ['cost']),
    ]


    """ Workflow Functions"""
     
    def confirmed(self, cr, uid, ids, context=None):
        for order in self.browse(cr, uid, ids, context=context):
            if not order.maintenance_lines:
                raise orm.except_orm(_('Error !'), _('You can not confirm this order without maintenance lines.'))
        self.write(cr, uid, ids, {'state':'confirmed'})
        return True

    def done(self,cr,uid,ids,context=None):
        self.write(cr, uid, ids, {'state':'done'},context=context)
        return True

    def cancel(self, cr, uid, ids, notes='', context=None):
        # Cancel Building Maintenance order 
        notes = ""
        user_name = self.pool.get('res.users').browse(cr, uid,uid).name
        notes = notes +'\n'+'Building maintenance order Cancelled at : '+time.strftime('%Y-%m-%d') + ' by '+ user_name
        self.write(cr, uid, ids, {'state':'cancel','notes':notes})
        return True

    def ir_action_cancel_draft(self, cr, uid, ids, context=None):
        # Reset the Car Maintenance Order 
        if not len(ids):
            return False
        wf_service = netsvc.LocalService("workflow")
        for building_id in ids:
            self.write(cr, uid, building_id, {'state':'draft'})
            wf_service.trg_delete(uid, 'building.maintenance', building_id, cr)            
            wf_service.trg_create(uid, 'building.maintenance', building_id, cr)
        return True

    def copy(self, cr, uid, ids, default=None, context=None):
        if default is None:
            default = {}
        default = default.copy()
        picking_obj = self.browse(cr, uid, ids, context=context)
        if ('name' not in default) or (picking_obj.name == '/'):
            seq_obj_name = 'building.maintenance'
            default['name'] = self.pool.get('ir.sequence').get(cr, uid, seq_obj_name)
        return super(building_maintenance, self).copy(cr, uid, ids, default, context)
        
    def unlink(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        for maintenance in self.browse(cr, uid, ids, context=context):
            if maintenance.state == 'done':
                raise osv.except_osv(_('Error!'), _('You cannot remove the maintenance order which is in done state!'))
       
        return super(building_maintenance, self).unlink(cr, uid, ids, context=context)

# ----------------------------------------------------
# Class building maintenance line
# ----------------------------------------------------
class building_maintenance_line(orm.Model):
    _name = "building.maintenance.line"
    _description = 'building maintenance line'

    def onchange_qty(self,cr,uid,ids,building_id,item_id,context=None):
       domain= {}
       if building_id and not item_id:
            building = self.pool.get('building.building').browse(cr,uid,building_id,context=context)
            domain={'item_id':[('id','in',[item.item_id.id for item in building.item_ids])]}
       return {'domain': domain}

    def check_qty(self, cr, uid,ids,context=None):
        for line in self.browse(cr,uid,ids,context=context):
           if line.maintenance_id.building_id:
              item_qty = sum(item.qty for item in line.maintenance_id.building_id.item_ids if item.item_id.id == line.item_id.id)
              if line.qty > item_qty:
                 raise orm.except_orm(_('Error !'),_('sorry you can not exceed item quantity of the selected building %s' % (item_qty)))
        return True
           
    _columns = {
                'name': fields.char('Description', size=256),
                'qty': fields.float('Quantity',digits=(16,2), required=True),        
                'item_id': fields.many2one('item.item', 'Item', required=True),
                'maintenance_id': fields.many2one('building.maintenance', 'Maintenance order', required=True),
               }
    _defaults = {
                'qty':1,       
                }
    _sql_constraints = [
        ('qty_check', 'check(qty > 0)', 'Item quantity must be bigger than zero!'),
        ]
    _constraints = [
        (check_qty, 'sorry you can not exceed item quantity of the selected building', ['qty']),
                    ]

    def onchange_item_id(self, cr, uid, ids, item_id ):

        if not item_id:
            return {'value': {'name': '',}}
        item_name = self.pool.get('item.item').name_get(cr, uid, [item_id ] )[0][1]
        result = {'name':item_name,}
        return {'value': result}
    
building_maintenance_line()
    
