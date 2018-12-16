# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

from openerp.osv import osv, fields
from tools.translate import _
import time

#----------------------------------------------------------
# product_product (Inherit)
#----------------------------------------------------------
class product_category(osv.Model):

    _inherit = "product.category"

    _columns = {
        'asset_category_id': fields.many2one('account.asset.category','Asset Category'),
        'journal_id': fields.many2one('account.journal', 'Journal'),
        'account_asset_id': fields.many2one('account.account', 'Asset Account', domain=[('type','=','other')]),
        'account_depreciation_id': fields.many2one('account.account', 'Depreciation Account', domain=[('type','=','other')]),
        'account_expense_depreciation_id': fields.many2one('account.account', 'Depr. Expense Account', domain=[('type','=','other')]),
        }

    def create(self, cr, uid, vals, context=None):
        if vals['custody']:
            vals.update({'asset_category_id': self.create_asset_category(cr, uid, vals, context)})
        return super(product_category, self).create(cr, uid, vals, context)


    def create_asset_category(self, cr, uid, vals, context=None):
        """
        this Function create asset category for each Product category
        @return: ID of created asset category
        """    
        asset_pool = self.pool.get('account.asset.category')
        name = vals['name']

        data = {
            'name': name,
            'code': name + _('Custody'),
            'journal_id' : vals['journal_id'],
            'account_asset_id': vals['account_asset_id'],
            'account_depreciation_id' : vals['account_depreciation_id'],
            'account_expense_depreciation_id': vals['account_expense_depreciation_id'],
        }

        return asset_pool.create(cr, uid, data)


#----------------------------------------------------------
# Exchange Order inherit
#----------------------------------------------------------
class exchange_order(osv.osv):
    _inherit = "exchange.order"

    _columns = {
        'custody_type': fields.selection([('personal','Personal'),('management','Management')], string='Custody Type' , states={'approved': [('readonly', False)]}),	
	    'employee_to': fields.many2one('hr.employee', string='Destination Employee' , states={'approved': [('readonly', False)]}),
        'office': fields.many2one('office.office','office' , states={'approved': [('readonly', False)]}),
        'custody': fields.boolean('Custody'),
	 
    }
    _defaults = {
	'custody_type' : 'management',
	 
		 }
    def action_confirm_order(self, cr, uid, ids, context=None):
        """ wf_service
        Changes order state to confirm.
        @return: True
        """
        for order in self.browse(cr, uid, ids, context=context):
            
            if not order.order_line:
                raise osv.except_osv(_('Error !'), _('You can not confirm the order without  order lines.'))
            x=0 # custody count in order line
            for line in order.order_line:
                if line.product_id.asset==True:
                    x+=1
            if x>0 and order.custody==False:
                 
                self.write(cr, uid, ids, {'custody':'True'})
                

            '''if order.ttype=='store':
                manager_id=order.department_id.manager_id 
                if not manager_id or  not manager_id.user_id or  manager_id.user_id.id!=uid:
                    raise osv.except_osv(_('Error !'), _('Department  manager who only can confirm this order.'))
            else:
                manager_id=order.department_id.manager_id 
                if not manager_id or  not manager_id.user_id or  manager_id.user_id.id!=uid:
                    manager_id=order.department_id.parent_id.manager_id 
                    if not manager_id or  not manager_id.user_id or  manager_id.user_id.id!=uid:
                        raise osv.except_osv(_('Error !'), _('Department  manager who only can confirm this order.'))'''  
            self.changes_state(cr, uid, ids, {'state': 'confirmed'},context=context)
        return True

    def _prepare_order_picking(self, cr, uid, order, context=None):
        """
        Prepare the dict of values to create the new picking for a
        exchange order. This method may be overridden to implement custom
        picking generation (making sure to call super() to establish a clean extension chain).
        @param browse_record order: exchange.order.line record to invoice
        @return: dict of values to create() the picking
        """
        
        res = super(exchange_order, self)._prepare_order_picking(cr, uid, order, context)
        new_dict={
              'custody':order.custody,
              'office':order.office.id,
              'custody_type':order.custody_type,
              'employee_to':order.employee_to.id  }
        res.update(new_dict)
        return res

    '''def _prepare_order_line_move(self, cr, uid, order, line, picking_id,product_qty ,context=None):
        """
        Prepare the dict of values to create the new stock move for a
        exchange order line. This method may be overridden to implement custom
        move generation (making sure to call super() to establish a clean extension chain).
        @param browse_record order: exchange.order record 
        @param browse_record line: exchange.order.line record 
        @param int picking_id: ID of stock  picking 
        @param product_qty : product qty(this is used for returning products including service)
        @return: dict of values to create() the stock move
        """

        res = super(exchange_order, self)._prepare_order_line_move(cr, uid, order, line, picking_id,product_qty ,context=None)
        if line.product_id.custody and order.ttype == 'other' :
            asset_picking_dict = {
                'product_id': line.product_id.id,
                'picking_id': int(picking_id),
                'office': False,
                'asset_id': False,
            }
            #frac,whole = math.mod(product_qty)
            piching_out_asset_obj = self.pool.get('stock.picking.out.asset')
            for x in range(0,int(product_qty)):
                piching_out_asset_obj.create(cr, uid, asset_picking_dict, context=context)
        return res'''

exchange_order()

#----------------------------------------------------------
# Stock Picking Out Asset
#----------------------------------------------------------

'''class stock_picking_out_asset(osv.Model):
    _name = "stock.picking.out.asset"

    def _is_serial(self, cr, uid, ids, name, args, context=None):
        result = {}
        for rec in self.browse(cr, uid, ids, context=context):
            if rec.product_id.is_serializable:
                result[rec.id] = True
            else:
                result[rec.id] = False
        return result

    _columns = {
        'product_id': fields.many2one('product.product','Product'),
        'asset_id': fields.many2one('account.asset.asset','Asset'),
        'serial': fields.char('Serial Number', size=256),
        'office': fields.many2one('office.office', string='office'),
        'picking_id': fields.many2one('stock.picking','Stock Order'),
        #'stock_partial_id': fields.many2one('stock.partial.move','Stock Order'),
        'is_serializable': fields.function(_is_serial,type="boolean", string='Serializable'),
        
    }

    def onchange_asset(self, cr, uid, ids, asset_id, product_id, context={}):
        """
        Method returns the default serial basedon given asset_id
        """
        asset_obj = self.pool.get('account.asset.asset')
        if asset_id and product_id:
            return {'value': {'serial':asset_obj.browse(cr, uid, asset_id).serial} }
        return {'value': {}}
        

    def onchange_serial(self, cr, uid, ids, serial, product_id, context={}):
        """
        Method returns the default asset_id based on the given serial
        """
        asset_obj = self.pool.get('account.asset.asset')
        asset_ids = []
        value = []
        if serial and product_id :
            asset_ids = asset_obj.search(cr, uid, [('product_id','=',product_id),('serial','=',serial)])
        if asset_ids:
            return {'value': {'asset_id':asset_ids[0]} }
        return {'value': {'asset_id':False} }'''


#----------------------------------------------------------
# Stock Picking (Inherit)
#----------------------------------------------------------
class stock_picking(osv.Model):
 
    _inherit = "stock.picking"

    def _get_rec(self, cr, uid, ids, name, args, context=None):
 
        for pick in self.browse(cr,uid,ids,context):
            res = {}
            o_id=0
            if pick.purchase_id:
                order_name=pick.purchase_id.ir_id.ir_ref

                order_id= self.pool.get('exchange.order').search(cr, uid, [('name','=',order_name)])

                order=self.pool.get('exchange.order').browse(cr, uid,order_id)
                for order in order:
                    o_id=order.id
                res[pick.id] = o_id 

            return res

    _columns = {
        'custody_type': fields.selection([('personal','Personal'),('management','Management')], string='Custody Type'),	
        'employee_to': fields.many2one('hr.employee', string='Destination Employee'),
        'office': fields.many2one('office.office','office'  ),
        'custody': fields.boolean('Custody',),
        'rec_id': fields.function(_get_rec, string='order', type='many2one',relation='exchange.order',store=True),
        #'picking_out_assets': fields.one2many('stock.picking.out.asset', 'picking_id', 'Assets'),
    }

stock_picking()

class stock_picking_out(osv.osv):
     
    _inherit = "stock.picking.out"
     
    _columns = {
        'custody_type': fields.selection([('personal','Personal'),('management','Management')], string='Custody Type'),	
        'employee_to': fields.many2one('hr.employee', string='Destination Employee'),
        'office': fields.many2one('office.office','office'  ),
        'partner_id': fields.many2one('res.partner','partner'  ),
        'custody': fields.boolean('Custody',),
        #'picking_out_assets': fields.one2many('stock.picking.out.asset', 'picking_id', 'Assets'),
    }
     

stock_picking_out()

class stock_picking_in(osv.osv):
 
    _inherit = "stock.picking.in"
 
    def _get_rec(self, cr, uid, ids, name, args, context=None):
 
        for pick in self.browse(cr,uid,ids,context):
             res = {pick.id: False}
             o_id = False
             if pick.purchase_id:
                order_name=pick.purchase_id.ir_id.ir_ref
                
                order_id= self.pool.get('exchange.order').search(cr, uid, [('name','=',order_name)])
                
                order=self.pool.get('exchange.order').browse(cr, uid,order_id)
                
                for order in order:
                    o_id=order.id
                    res = {pick.id: o_id}
                
                return res
    _columns = {
        'custody_type': fields.selection([('personal','Personal'),('management','Management')], string='Custody Type'),	
        'employee_to': fields.many2one('hr.employee', string='Destination Employee'),
        'office': fields.many2one('office.office','office'  ),
        'rec_id': fields.function(_get_rec, string='order', type='many2one',relation='exchange.order',store=True),
        'custody': fields.boolean('Custody',),
 
    }

stock_picking_in()


'''class stock_partial_picking(osv.Model):
    _inherit = "stock.partial.picking"

    def do_partial(self, cr, uid, ids, context=None):
        value = super(stock_partial_picking, self).do_partial(
            cr, uid, ids, context=context)
        try:
            copy_obj = self.pool.get('stock.partial.picking.copy')
            is_exist = copy_obj.search(
                cr, uid, [('picking_id', '=', context['active_id'])])
            copy_obj.unlink(cr, uid, is_exist)
        except:
            pass
        return value

    def default_get(self, cr, uid, fields, context=None):
        print "----------------context", context
        value = super(stock_partial_picking, self).default_get(
            cr, uid, fields, context=context)
        if context and 'active_ids' in context and len(context['active_ids']) == 1 and 'move_ids' in value:
            copy_obj = self.pool.get('stock.partial.picking.copy')
            is_exist = copy_obj.search(
                cr, uid, [('picking_id', 'in', context['active_ids'])])
            if is_exist:
                is_exist = is_exist[0]
                is_exist = copy_obj.browse(cr, uid, is_exist, context=context)
                old_values = {i['product_id']: i['quantity']
                              for i in is_exist.move_ids}
                for move in value['move_ids']:
                    if move['product_id'] in old_values.keys():
                        move['quantity'] = old_values[move['product_id']]
        return value

    def save(self, cr, uid, ids, context=None):
        copy_obj = self.pool.get('stock.partial.picking.copy')
        is_exist = copy_obj.search(
            cr, uid, [('picking_id', 'in', context['active_ids'])])
        copy_obj.unlink(cr, uid, is_exist)
        copy_obj = self.pool.get('stock.partial.picking.copy')

        for rec in self.browse(cr, uid, ids, context):
            lines = []
            for line in rec.move_ids:
                line = line.read()[0]
                new_line = {}
                for k in line.keys():
                    if k in ['id', 'wizard_id']:
                        continue
                    if type(line[k]) == tuple:
                        line[k] = line[k][0]
                    new_line[k] = line[k]

                lines.append(
                    (0, 0, {"product_id": new_line['product_id'], "quantity": new_line['quantity']}))
            copy_obj.create(cr, uid, {'picking_id': rec.picking_id.id,
                                      'move_ids': lines})

        return True

    def un_save(self, cr, uid, ids, context=None):
        copy_obj = self.pool.get('stock.partial.picking.copy')
        is_exist = copy_obj.search(
            cr, uid, [('picking_id', '=', context['active_id'])])
        copy_obj.unlink(cr, uid, is_exist)
        return True
    '''

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
