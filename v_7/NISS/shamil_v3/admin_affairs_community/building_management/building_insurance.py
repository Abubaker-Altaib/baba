# -*- coding: utf-8 -*-
##############################################################################
#
# NCTR, Nile Center for Technology Research
# Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##########################################################################

from openerp.osv import fields,orm
import time
from openerp.tools.translate import _
import netsvc

#----------------------------------------
# Class building insurance
#----------------------------------------
class building_insurance(orm.Model):
    _name = "building.insurance"
    _description = 'building insurance'

    def create(self, cr, user, vals, context=None):
        """
        Create new entry sequence for every new building insurance Record
        @param vals: record to be created
        @return: return a result that create a new record in the database
          """
        if ('name' not in vals) or (vals.get('name')=='/'):
            seq_obj_name =  'building.insurance'
            vals['name'] = self.pool.get('ir.sequence').get(cr, user, seq_obj_name) 
        return super(building_insurance, self).create(cr, user, vals, context) 
 
    def _total_cost(self, cr, uid, ids, field_name, arg, context={}):
        """ Finds the the total of insurance cost.
        @param field_name: list contains name of fields that call this method
        @param arg: extra arguement
        @return: Dictionary of values
        """
        res = {}
        for record in self.browse(cr, uid, ids, context=context):
            val = 0.0
            for line in record.insurance_lines:
                val += line.cost
            res[record.id] = val 
        return res
    
    STATE_SELECTION = [
    ('draft', 'Draft'),
    ('confirmed', 'Confirmed'),
    ('done', 'Done'),
    ('cancel', 'Cancel'), ]    

    _order = "name desc"
    _columns = {
    'name': fields.char('Reference', size=64, required=True, select=True, readonly=True, help="unique number of the building insurance"),
    'date' : fields.date('Date',required=True, readonly=True,),
    'begin_date' : fields.date('Insurance date', required=True , states={'done':[('readonly',True)],'cancel':[('readonly',True)]}),
    'end_date' : fields.date('End Date', required=True , states={'done':[('readonly',True)],'cancel':[('readonly',True)]}),
    'user_id':  fields.many2one('res.users', 'Responsible', readonly=True  ),
    'partner_id':  fields.many2one('res.partner', 'Partner',required=True,states={'done':[('readonly',True)],'cancel':[('readonly',True)]}),    
    'total_cost':fields.float('Total cost',states={'done':[('readonly',True)],'cancel':[('readonly',True)]}),
    'insurance_lines':fields.one2many('building.insurance.line', 'insurance_id' , 'Items', readonly=True, states={'draft':[('readonly',False)],'confirmed':[('readonly','False')]}),
    'company_id': fields.many2one('res.company','Company',states={'done':[('readonly',True)],'cancel':[('readonly',True)]}),
    'state': fields.selection(STATE_SELECTION,'State', readonly=True, select=True),
    'total_cost': fields.function(_total_cost, string='Total cost', readonly=True),    
    'notes': fields.text('Notes', size=256 , readonly=True,states={'draft':[('readonly',False)],'confirmed':[('readonly','False')]}), 
    }
    
    _sql_constraints = [
        ('name_uniq', 'unique(name)', 'Building insurance reference must be unique !'),
        ('date_check', 'CHECK (begin_date <= end_date)', "The start date must be anterior to the end date."),
        ]
    
    _defaults = {
                'name': lambda self, cr, uid, context: '/',
                'date': time.strftime('%Y-%m-%d'),
                'company_id': lambda self, cr, uid, c: self.pool.get('res.company')._company_default_get(cr, uid, 'building.insurance', context=c),
                'state': 'draft',
                'user_id': lambda self, cr, uid, context: uid,
                }
    
    """ Workflow Functions"""   
    def confirmed(self, cr, uid, ids, context=None):                   
        for order in self.browse(cr, uid, ids, context=context):
            if not order.insurance_lines:
                raise orm.except_orm(_('Error !'), _('You can not confirm this order without insurance lines.'))
        self.write(cr, uid, ids, {'state':'confirmed'})
        return True

    def done(self,cr,uid,ids,context=None):
        self.write(cr, uid, ids, {'state':'done'},context=context) 
        return True

    def cancel(self, cr, uid, ids, notes='', context=None):
        """ Cancel building insurance record"""
        user_obj = self.pool.get('res.users')
        for record in self.browse(cr, uid, ids,context=context):
            notes = record.notes or ""
            user_name = user_obj.browse(cr, uid, uid).name
            notes += 'This record cancelled at : ' + time.strftime('%Y-%m-%d') + ' by '+ user_name + '\n'
        self.write(cr, uid, ids, {'state':'cancel','notes':notes})
        return True

    def ir_action_cancel_draft(self, cr, uid, ids, context=None):
        """ convert the record from cancel state to draft state"""
        if not len(ids):
            return False
        wf_service = netsvc.LocalService("workflow")
        for record_id in ids:
            self.write(cr, uid, record_id, {'state':'draft'})
            wf_service.trg_delete(uid, 'building.insurance', record_id, cr)            
            wf_service.trg_create(uid, 'building.insurance', record_id, cr)
        return True

    def copy(self, cr, uid, ids, default=None, context=None):
        if default is None:
            default = {}
        default = default.copy()
        picking_obj = self.browse(cr, uid, ids, context=context)
        if ('name' not in default) or (picking_obj.name == '/'):
            seq_obj_name = 'building.insurance'
            default['name'] = self.pool.get('ir.sequence').get(cr, uid, seq_obj_name)
        return super(building_insurance, self).copy(cr, uid, ids, default, context)

    def unlink(self, cr, uid, ids, context=None):
        """Delete the building insurance record"""
        states = self.read(cr, uid, ids, ['state'], context=context)
        unlink_ids = []
        for state in states:
            if state['state'] in ('draft','cancel'):
                unlink_ids.append(state['id'])
            else:
                raise orm.except_orm(_('Invalid action !'), _('In order to delete a building insurance order, you must first cancel it or set to draft.'))
        osv.osv.unlink(self, cr, uid, unlink_ids, context=context)
        return True
                    

#----------------------------------------
# Class building insurance line
#----------------------------------------
class building_insurance_line(orm.Model):
    
    _name = "building.insurance.line"
    _description = 'Building insurance line'

    def check_qty(self, cr, uid,ids,context=None):
        for line in self.browse(cr,uid,ids,context=context):
           if line.building_id:
              item_qty = sum(item.qty for item in line.building_id.item_ids if item.item_id.id == line.item_id.id)
              if line.qty > item_qty:
                 raise orm.except_orm(_('Error !'),_('sorry you can not exceed item quantity of the selected building %s' % (item_qty)))
        return True

    _columns = { 
       'insurance_id':  fields.many2one('building.insurance', 'Building insurance',),
       'item_id': fields.many2one('item.item', 'Item',required = True,),
       'building_id':fields.many2one('building.building','Building', required = True,),
       'price': fields.float('Item Price', required=True),
       'qty': fields.float('Quantity', required=True),        
       'cost': fields.float('Insurance cost',),   
       'name': fields.char('Notes', size=256, ),                       
               }
    
    _defaults = {
         'price' : 1.0, 
         'qty' : 1.0, 
         'cost' : 1.0,     
            }
        
    _constraints = [
        (check_qty, 'sorry you can not exceed item quantity of the selected building', ['qty']),
                    ]

        
    def onchange_qty_price(self, cr, uid, ids, qty, price):
        result = {'cost':qty * price}
        return {'value': result}
    
    def onchange_building_id(self,cr,uid,ids,building_id,context=None):
       domain= {}
       if building_id:
            building = self.pool.get('building.building').browse(cr,uid,building_id,context=context)
            domain={'item_id':[('id','in',[item.item_id.id for item in building.item_ids])]}
       return {'value':{'item_id':False},'domain': domain}
