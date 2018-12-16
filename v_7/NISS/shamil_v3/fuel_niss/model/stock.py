# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2016-2017 NCTR (<http://www.nctr.sd>).
#
##############################################################################

from osv import osv, fields
from tools.translate import _
import sys
import openerp.addons.decimal_precision as dp
from base_custom.amount_to_text_ar import amount_to_text
import time
from openerp import netsvc
from openerp.addons.account_voucher.account_voucher import resolve_o2m_operations

#----------------------------------------------------------
# Stock Location
#----------------------------------------------------------


class stock_location(osv.osv):
    _inherit = "stock.location"

    def search(self, cr, uid, args, offset=0, limit=None, order=None,
            context=None, count=False):
        prod_id = context and context.get('product_id', False)
        model_id = context and context.get('active_model', False)
        if prod_id and model_id:
            basic = self.pool.get(model_id).read(cr, uid, prod_id, [])
            fuel_ok = context and basic.get('fuel_ok', False)
            if fuel_ok:
                args.append(('fuel_ok','=',True))

        return super(stock_location, self).search(cr, uid, args=args, offset=offset, limit=limit, order=order,
            context=context, count=count)

    _columns = {
        'fuel_ok': fields.boolean('Fuel Location', help="Determine This Location Is Fuel Location"),
        #'company_id': fields.many2one('res.company','company'),
    }

    '''def _default_company(self,cr,uid,context=None):
        List = []
        user_obj = self.pool.get('res.users')
        user = user_obj.browse(cr ,uid, uid)
        company = False
        if user.company_id:
            company = user.company_id.id

        return company
'''
    _defaults = {
        'fuel_ok': 0,
        #'company_id' : _default_company,

    }

    def name_search(self, cr, uid, name, args=None, operator='ilike', context=None, limit=100):
        """
        Method that overwrites name_search method Search for department (only departments 
        that requested trainings) and their display name.

        @param name: Object name to search
        @param args: List of tuples specifying search criteria
        @param operator: Operator for search criterion
        @param limit: Max number of records to return
        @return: Super name_search method 
        """
        if not args:
            args = []
        if context is None:
            context = {}
        idss = []
        fuel = 0
        if 'fuel_ok' in context:
            idss = self.search(
                cr, uid, [('fuel_ok', '=', context['fuel_ok'])], context=context)
            if context['fuel_ok'] == True:
                fuel = 0
            if idss:
                if fuel:
                    args.append(('id', 'in', idss))
                else:
                    args.append(('id', 'not in', idss))

        if 'fuel_delegate' in context and context['fuel_delegate'] != False:
            idss = []
            if 'fuel_type' in context and context['fuel_type'] != False:
                fuel_delegate_line_obj = self.pool.get('fuel.delegate.lines')
                fuel_delegate_ids = fuel_delegate_line_obj.search(cr, uid, [('delegate_id','=',context['fuel_delegate']),
                    ('fuel_type','=',context['fuel_type'])])
                if fuel_delegate_ids:
                    product = fuel_delegate_line_obj.browse(cr, uid, fuel_delegate_ids[0]).location_id.id
                    idss.append(product)

            args.append(('id', 'in', idss))
        return super(stock_location, self).name_search(cr, uid, name, args=args, operator=operator, context=context, limit=limit)


#----------------------------------------------------------
# Stock Picking IN
#----------------------------------------------------------
class stock_picking(osv.osv):
    _inherit = "stock.picking"

    def _amount_all(self, cr, uid, ids, name, args, context=None):
        res = {}
        for picking in self.browse(cr, uid, ids, context=context):
            res[picking.id] = 0.0
            for line in picking.move_lines:
                if picking.type == 'in':
                    res[picking.id] += line.product_id.standard_price * \
                        line.product_qty
        return res

    def _get_stock_move(self, cr, uid, ids, context=None):
        result = {}
        for line in self.pool.get('stock.move').browse(cr, uid, ids, context=context):
            if line.fuel_ok:
                result[line.picking_id.id] = True
        return result.keys()

    def _amount_to_text(self, cr, uid, ids, fields, args, context=None):
        res = {}
        for rec in self.browse(cr, uid, ids, context):
            res[rec.id] = rec.amount_total
            if res[rec.id]:
                res[rec.id] = amount_to_text(res[rec.id])
        return res

    def _get_child_location(self, cr, uid, ids, name, args, context=None):
        result = {}
        for line in self.browse(cr, uid, ids, context=context):
            result[line.id] = False
            for move in line.move_lines:
                result[line.id] = move.location_id.id
        return result

    _columns = {
        'fuel_ok': fields.boolean('Fuel Location', help="Determine This Location Is Fuel Location"),
        'amount_total': fields.function(_amount_all, digits_compute=dp.get_precision('Account'), string='Total Price',
                                        store={
            'stock.picking': (lambda self, cr, uid, ids, c={}: ids, ['move_lines'], 20),
            'stock.move': (_get_stock_move, ['picking_id', 'product_id', 'product_qty', 'product_amount', 'id'], 10),
        }),
        'department_id': fields.many2one('hr.department', 'Requesting Party'),
        'amount_total_ch': fields.function(_amount_to_text, string='Total Price in words', type="char"),
        'stock_in_type': fields.selection([('claim','Claim'),('requisition','Requisition')],'Incoming Type'),
        'hq': fields.boolean('Is HQ'),
        'fleet_employee_id': fields.many2one('hr.employee', 'Driver'),
        'fleet_degree_id': fields.many2one('hr.salary.degree', 'Driver Degree'),
        'fleet_department_id': fields.many2one('hr.department', 'Driver Department'),
        'fleet_emp_code': fields.char('Military Number'),
        'fuel_type': fields.selection([('gasoline', 'Gasoline'), ('diesel', 'Benzene'), ('electric', 'Electric'), ('hybrid', 'Hybrid')],
                                      'Fuel Type', help='Fuel Used by the vehicle'),
        'stock_fuel_id': fields.one2many('stock.picking.fuel','picking_id','Receiving lines'),
        'fuel_product_id': fields.many2one('product.product', 'Fuel'),
        #'product_uom': fields.many2one('product.uom', 'Unit of Measure'),
        'fuel_product_qty': fields.float('Quantity', digits_compute=dp.get_precision('Product Unit of Measure')),
        'product_qty_before': fields.float('Quantity Before', digits_compute=dp.get_precision('Product Unit of Measure')),
        'product_qty_after': fields.float('Quantity After', digits_compute=dp.get_precision('Product Unit of Measure')),
        'hole_num': fields.char('Hole Number'),
        'fuel_receiver_id': fields.many2one('hr.employee', 'Receiver'),
        'fuel_invoice_num': fields.char('Invoice Number'),
        'deliver_fuel_product_id': fields.many2one('product.product', 'Fuel'),
        'deliver_product_price': fields.float('Price'),
        'deliver_product_uom': fields.many2one('product.uom', 'Unit of Measure'),
        'deliver_fuel_product_qty': fields.float('Quantity', digits_compute=dp.get_precision('Product Unit of Measure')),
        'fuel_deliver_date': fields.date('Delivery Date'),
        'fuel_receive_date': fields.date('Receiving Date'),
        'fuel_location_id': fields.many2one('stock.location', 'Location',),
        'fuel_location_dest_id': fields.many2one('stock.location', 'Dest. Location'),
        'card_no': fields.char('Fuel Card Number'), 
        'fuel_delegate_id': fields.many2one('fuel.delegate', 'Fuel Delegation'),
        'outgoing_fuel_type': fields.many2one('outgoing.fuel.type', 'Outgoing Type'),
        'require_user': fields.boolean(string="Require Employee",readonly=1),
        'wells_ids': fields.one2many('picking.well','picking_id','Wells'),
        'deliver_fuel_product_fuel_type' : fields.related('deliver_fuel_product_id', 'fuel_type', 
        type="selection",selection=[('gasoline', 'Gasoline'), ('diesel', 'Benzene'), ('electric', 'Electric'), ('hybrid', 'Hybrid')], string="Fuel Type"),
        'reason': fields.text('Reason'),
        'desc': fields.text('Description'),
        'receipt_no': fields.char('Receipt Number'),
        'confiscation_employee_id': fields.many2one('hr.employee', 'Confiscation Employee'),

        'fuel_out_location_id': fields.function(_get_child_location, type='many2one', relation='stock.location', string='Location', store={
            'stock.picking': (lambda self, cr, uid, ids, c={}: ids, ['move_lines'], 20),
            'stock.move': (_get_stock_move, ['picking_id', 'product_id', 'product_qty', 'product_amount', 'id', 'location_id'], 10),
        }),
    }
    _defaults = {
        'fuel_ok': 0,
        'require_user': 0,
        'exchange_id': False,
        'hq': lambda self, cr, uid, context: self.pool.get('res.users').browse(cr, uid, uid, context=context).company_id.hq,
    }


    def onchange_fuel_company_id(self, cr, uid, ids, company_id, context={}):
        """
        method return value of hq
        """
        hq = self.pool.get('res.company').browse(cr, uid, company_id, context).hq
        if hq is None:
            hq = False

        return {'value':{'hq':hq},'domain':{}}


    def _check_quantity(self, cr, uid, ids, context=None):
        
        for rec in self.browse(cr, uid, ids, context=context):
            if rec.fuel_ok:
                if rec.type == 'in' and rec.hq == True:
                    if rec.deliver_fuel_product_qty <= 0 and rec.state == 'assigned':
                        raise osv.except_osv(_(''), _("Fuel Quantity should be more than Zero "))
                    if rec.product_qty_before < 0:
                        raise osv.except_osv(_(''), _("Quantity Before should not be negative "))
                    if rec.product_qty_after < 0:
                        raise osv.except_osv(_(''), _("Quantity After  should not be negative "))
                    #if rec.product_qty_after < rec.product_qty_before:
                    #    raise osv.except_osv(_(''), _("Quantity aftre should be more than Quantity before "))

        return True 


    def _check_location(self, cr, uid, ids, context=None):
        
        for rec in self.browse(cr, uid, ids, context=context):
            if rec.fuel_ok:
                if rec.type == 'in' and rec.hq == True:
                    if rec.fuel_location_id.id == rec.fuel_location_dest_id.id:
                        raise osv.except_osv(_(''), _("You can not transfer fuel from/to the same location"))
                    

        return True 

    def _check_fuel(self, cr, uid, ids, context=None):
        
        for rec in self.browse(cr, uid, ids, context=context):
            if rec.fuel_ok:
                if rec.type == 'in' and rec.hq == True and rec.state == 'assigned':
                    if rec.fuel_product_id and rec.fuel_product_id.id != rec.deliver_fuel_product_id.id:
                        raise osv.except_osv(_(''), _("Received fuel should be the same as the delivery fuel"))
                    

        return True 


    _constraints = [
        (_check_quantity, _(''), ['deliver_fuel_product_qty','product_qty_before','product_qty_after']),
        (_check_location, _(''), ['fuel_location_id','fuel_location_dest_id']),
        (_check_fuel, _(''), ['fuel_product_id']),
    ]



#----------------------------------------------------------
# Stock Picking IN
#----------------------------------------------------------
class stock_picking_in(osv.osv):
    _inherit = "stock.picking.in"

    def _amount_all(self, cr, uid, ids, name, args, context=None):
        res = {}
        for picking in self.browse(cr, uid, ids, context=context):
            res[picking.id] = 0.0
            for line in picking.move_lines:
                if picking.type == 'in':
                    res[picking.id] += line.product_id.standard_price * \
                        line.product_qty
        return res

    def _get_stock_move(self, cr, uid, ids, context=None):
        result = {}
        for line in self.pool.get('stock.move').browse(cr, uid, ids, context=context):
            #if line.fuel_ok and line.state == 'draft':
            if line.fuel_ok :
                result[line.picking_id.id] = True
        return result.keys()

    def _amount_to_text(self, cr, uid, ids, fields, args, context=None):
        res = {}
        for rec in self.browse(cr, uid, ids, context):
            res[rec.id] = rec.amount_total
            if res[rec.id]:
                res[rec.id] = amount_to_text(res[rec.id])
        return res

    def _get_child_location(self, cr, uid, ids, name, args, context=None):
        result = {}
        for line in self.browse(cr, uid, ids, context=context):
            result[line.id] = False
            for move in line.move_lines:
                result[line.id] = move.location_id.id
        return result

    _columns = {
        'fuel_ok': fields.boolean('Fuel Location', help="Determine This Location Is Fuel Location"),
        'amount_total': fields.function(_amount_all,  string='Total Price',
                                        store={
                                            'stock.picking': (lambda self, cr, uid, ids, c={}: ids, ['move_lines'], 20),
                                            'stock.move': (_get_stock_move, ['picking_id', 'product_id', 'product_qty', 'product_amount', 'id'], 10),
                                        }),
        'department_id': fields.many2one('hr.department', 'Requesting Party / Exceuting'),
        'exchange_id': fields.many2one('exchange.order', 'Exchange Order', readonly=True,
                                       ondelete='set null', select=True),
        'amount_total_ch': fields.function(_amount_to_text, string='Total Price in words', type="char"),
        'hq': fields.boolean('Is HQ'),
        'stock_in_type': fields.selection([('claim','Claim'),('requisition','Requisition')],'Incoming Type'),
        'fleet_employee_id': fields.many2one('hr.employee', 'Driver / Authority'),
        'fleet_degree_id': fields.many2one('hr.salary.degree', 'Driver Degree / Authority'),
        'fleet_department_id': fields.many2one('hr.department', 'Driver Department / Authority'),
        'fleet_emp_code': fields.char('Military Number'),
        'fuel_type': fields.selection([('gasoline', 'Gasoline'), ('diesel', 'Benzene'), ('electric', 'Electric'), ('hybrid', 'Hybrid')],
                                      'Fuel Type', help='Fuel Used by the vehicle'),
        'stock_fuel_id': fields.one2many('stock.picking.fuel','picking_id','Receiving lines'),
        'fuel_product_id': fields.many2one('product.product', 'Fuel'),
        #'product_uom': fields.many2one('product.uom', 'Unit of Measure'),
        'fuel_product_qty': fields.float('Quantity', digits_compute=dp.get_precision('Product Unit of Measure')),
        'product_qty_before': fields.float('Quantity Before', digits_compute=dp.get_precision('Product Unit of Measure')),
        'product_qty_after': fields.float('Quantity After', digits_compute=dp.get_precision('Product Unit of Measure')),
        'hole_num': fields.char('Hole Number'),
        'fuel_receiver_id': fields.many2one('hr.employee', 'Receiver'),
        'fuel_invoice_num': fields.char('Invoice Number'),
        'deliver_fuel_product_id': fields.many2one('product.product', 'Fuel'),
        'deliver_product_price': fields.float('Price'),
        'deliver_product_uom': fields.many2one('product.uom', 'Unit of Measure'),
        'deliver_fuel_product_qty': fields.float('Quantity', digits_compute=dp.get_precision('Product Unit of Measure')),
        'fuel_deliver_date': fields.date('Request Date'),
        'fuel_receive_date': fields.date('Receiving Date'),
        'fuel_location_id': fields.many2one('stock.location', 'Location',),
        'fuel_location_dest_id': fields.many2one('stock.location', 'Dest. Location'),
        'wells_ids': fields.one2many('picking.well','picking_id','Wells'),
        'deliver_fuel_product_fuel_type' : fields.related('deliver_fuel_product_id', 'fuel_type', 
        type="selection",selection=[('gasoline', 'Gasoline'), ('diesel', 'Benzene'), ('electric', 'Electric'), ('hybrid', 'Hybrid')], string="Fuel Type"),
        'reason': fields.text('Reason'),
        'receipt_no': fields.char('Receipt Number'),
        'desc': fields.text('Description'),
        'confiscation_employee_id': fields.many2one('hr.employee', 'Confiscation Employee'),
        'fuel_out_location_id': fields.function(_get_child_location, type='many2one', relation='stock.location', string='Location', store={
            'stock.picking': (lambda self, cr, uid, ids, c={}: ids, ['move_lines'], 20),
            'stock.move': (_get_stock_move, ['picking_id', 'product_id', 'product_qty', 'product_amount', 'id', 'location_id'], 10),
        }),

    }
    _defaults = {
        'fuel_ok': 0,
        'exchange_id': False,
        'hq': lambda self, cr, uid, context: self.pool.get('res.users').browse(cr, uid, uid, context=context).company_id.hq,
        'fuel_deliver_date': time.strftime('%Y-%m-%d'),
        'fuel_receive_date': time.strftime('%Y-%m-%d'),
    }

    def create(self, cr, user, vals, context=None):
        """
        Override create to call create of stock.picking
        """
        # if 'default_fuel_ok' in context and context['default_fuel_ok'] == True:
        #picking_obj = self.pool.get('stock.picking')
        #seq_obj_name =  self._name
        #vals['name'] = self.pool.get('ir.sequence').get(cr, user, seq_obj_name)
        if context is None:
            context = {}
        hq = self.pool.get('res.users').browse(cr, user, user, context=context).company_id.hq
        vals['hq'] = hq
        if 'default_fuel_ok' in context and context['default_fuel_ok'] == True:
            if 'hq' in vals and vals['hq'] == True:
                deliver_fuel_product_id = vals['deliver_fuel_product_id']
                onchange_value = self.onchange_deliver_product(cr, user, [],deliver_fuel_product_id )['value']
                vals['deliver_product_uom'] = onchange_value['deliver_product_uom']
                vals['deliver_product_price'] = onchange_value['deliver_product_price']
                vals['fuel_product_id'] = onchange_value['fuel_product_id']
                if 'product_qty_before' in vals and 'product_qty_after' in vals:
                    product_qty_before = vals['product_qty_before']
                    product_qty_after = vals['product_qty_after']
                    onchange_quantity = self.onchange_quantity(cr, user, [],product_qty_before,product_qty_after, context)['value']
                    vals['fuel_product_qty'] = onchange_quantity['fuel_product_qty']
                if 'wells_ids' in vals:
                    onchange_wells_ids = self.onchange_wells_ids(cr, user, [],vals['wells_ids'], context)['value']
                    vals['fuel_product_qty'] = onchange_wells_ids['fuel_product_qty']
                    vals['product_qty_before'] = onchange_wells_ids['product_qty_before']
                    vals['product_qty_after'] = onchange_wells_ids['product_qty_after']

            if 'fleet_employee_id' in vals:
                onchange_emp = self.onchange_fleet_employee_id(cr, user, [], vals['fleet_employee_id'])['value']
                vals['fleet_degree_id'] = onchange_emp['fleet_degree_id']
                vals['fleet_department_id'] = onchange_emp['fleet_department_id']
                vals['fleet_emp_code'] = onchange_emp['fleet_emp_code']

        return super(stock_picking_in, self).create(cr, user, vals, context)

    def write(self, cr, uid, ids, vals, context=None):
        """
        Override write to call write of stock.picking
        """
        # if 'default_fuel_ok' in context and context['default_fuel_ok'] == True:
        picking_obj = self.pool.get('stock.picking')
        for rec in self.browse(cr, uid, ids, context):
            if rec.fuel_ok:
                hq = rec.hq
                if 'hq' in vals:
                    hq = vals['hq']
                if hq:
                    deliver_fuel_product_id = rec.deliver_fuel_product_id.id
                    if 'deliver_fuel_product_id' in vals:
                        deliver_fuel_product_id = vals['deliver_fuel_product_id']
                        onchange_value = self.onchange_deliver_product(cr, uid, ids,deliver_fuel_product_id )['value']
                        vals['deliver_product_uom'] = onchange_value['deliver_product_uom']
                        vals['deliver_product_price'] = onchange_value['deliver_product_price']
                        vals['fuel_product_id'] = onchange_value['fuel_product_id']
                    if 'product_qty_before' in vals or 'product_qty_after' in vals:
                        product_qty_before = rec.product_qty_before
                        if 'product_qty_before' in vals:
                            product_qty_before = vals['product_qty_before']
                        product_qty_after = rec.product_qty_after
                        if 'product_qty_after' in vals:
                            product_qty_after = vals['product_qty_after']
                        onchange_quantity = self.onchange_quantity(cr, uid, ids,product_qty_before,product_qty_after, context)['value']
                        vals['fuel_product_qty'] = onchange_quantity['fuel_product_qty']
                
                if 'wells_ids' in vals:
                    onchange_wells_ids = self.onchange_wells_ids(cr, uid, [],vals['wells_ids'], context)['value']
                    vals['fuel_product_qty'] = onchange_wells_ids['fuel_product_qty']
                    vals['product_qty_before'] = onchange_wells_ids['product_qty_before']
                    vals['product_qty_after'] = onchange_wells_ids['product_qty_after']

                if 'fleet_employee_id' in vals:
                    onchange_emp = self.onchange_fleet_employee_id(cr, uid, ids, vals['fleet_employee_id'])['value']
                    vals['fleet_degree_id'] = onchange_emp['fleet_degree_id']
                    vals['fleet_department_id'] = onchange_emp['fleet_department_id']
                    vals['fleet_emp_code'] = onchange_emp['fleet_emp_code']
                super(stock_picking_in, self).write(cr, uid, [rec.id], vals, context)
            else:
                super(stock_picking_in, self).write(cr, uid, [rec.id], vals, context)
        return True


    def onchange_fuel_company_id(self, cr, uid, ids, company_id, context={}):
        """
        method return value of hq
        """
        hq = self.pool.get('res.company').browse(cr, uid, company_id, context).hq
        if hq is None:
            hq = False

        return {'value':{'hq':hq},'domain':{}}

    def onchange_wells_ids(self, cr, uid, ids, wells_ids, context={}):
        """
        method return all recievied quantity
        """
        before = after = 0.0
        picking_well_obj = self.pool.get('picking.well')
        for well in wells_ids:
            if well[0] in [0]:
                before += well[2]['before_amount']
                after += well[2]['after_amount']
            elif well[0] in [1]:
                read = picking_well_obj.read(cr, uid, well[1],[])
                read['before_amount'] = 'before_amount' in well[2] and well[2]['before_amount'] or read['before_amount']
                read['after_amount'] = 'after_amount' in well[2] and well[2]['after_amount'] or read['after_amount']
                before += read['before_amount']
                after += read['after_amount']
            elif well[0] == 4:
                read = picking_well_obj.read(cr, uid, well[1],[])
                before += read['before_amount']
                after += read['after_amount']


        return {'value':{
                        'product_qty_before':before,
                        'product_qty_after':after,
                        'fuel_product_qty':after - before
                        },'domain':{}}

    def onchange_deliver_product(self, cr , uid, ids, deliver_fuel_product_id, context={}):
        """
        """
        vals = {'deliver_product_uom': False, 'deliver_product_price': False, 'fuel_product_id': False}
        if deliver_fuel_product_id:
            product = self.pool.get('product.product').browse(cr, uid, deliver_fuel_product_id, context)
            vals['deliver_product_uom'] = product.uom_id.id
            vals['deliver_product_price'] = product.standard_price
            vals['fuel_product_id'] = deliver_fuel_product_id
        return {'value': vals}

    def onchange_quantity(self,cr , uid, ids, product_qty_before,product_qty_after, context={}):
        """
        """
        vals = {'fuel_product_qty': 0.0}
        vals['fuel_product_qty'] = product_qty_after - product_qty_before
        if product_qty_before and product_qty_after:
            vals['fuel_product_qty'] = product_qty_after - product_qty_before

        return {'value': vals}

    def onchange_fleet_employee_id(self, cr, uid, ids, fleet_employee_id, context={}):
        """
        """
        vals = {'fleet_degree_id': False, 'fleet_department_id':False, 'fleet_emp_code': False}
        if fleet_employee_id:
            emp = self.pool.get('hr.employee').browse(cr, uid, fleet_employee_id)
            vals['fleet_degree_id'] = emp.degree_id.id
            vals['fleet_department_id'] = emp.department_id.id
            vals['fleet_emp_code'] = emp.emp_code

        return {'value': vals}


    def _check_quantity(self, cr, uid, ids, context=None):
        
        for rec in self.browse(cr, uid, ids, context=context):
            if rec.fuel_ok:
                if rec.type == 'in' and rec.hq == True:
                    if rec.deliver_fuel_product_qty <= 0 and rec.state == 'assigned':
                        raise osv.except_osv(_(''), _("Fuel Quantity should be more than Zero "))
                    if rec.product_qty_before < 0:
                        raise osv.except_osv(_(''), _("Quantity Before should not be negative "))
                    if rec.product_qty_after < 0:
                        raise osv.except_osv(_(''), _("Quantity After  should not be negative "))
                    #if rec.product_qty_after < rec.product_qty_before:
                    #    raise osv.except_osv(_(''), _("Quantity aftre should be more than Quantity before "))

        return True 


    _constraints = [
        (_check_quantity, _(''), ['deliver_fuel_product_qty','product_qty_before','product_qty_after']),
    ]


    def button_cancel_in_done(self, cr, uid, ids, context=None):
        """ cancel picking directly from done state.
        @return: True
        """
        for pick in self.browse(cr, uid, ids):
            if pick.fuel_ok == True:
                cr.execute("update stock_picking set state='cancel' where id="+str(pick.id)+";")
                cr.execute("update stock_move set state='cancel' where picking_id="+str(pick.id)+";")
        return True

    def draft_force_assign(self, cr, uid, ids, *args):
        """ Confirms picking directly from draft state.
        @return: True
        """
        wf_service = netsvc.LocalService("workflow")
        for pick in self.browse(cr, uid, ids):
            if pick.fuel_ok == True:
                ## for HQ picking in to create stock.move
                if pick.hq == True and pick.type == 'in':
                    name = self.pool.get('product.product').name_get(cr, uid, [pick.deliver_fuel_product_id.id])[0][1]
                    val = {
                        'name': name[:250],
                        'picking_id': pick.id,
                        'product_id': pick.deliver_fuel_product_id.id,
                        'product_qty': pick.deliver_fuel_product_qty,
                        'product_uom': pick.deliver_product_uom.id,
                        'product_uos_qty':pick.deliver_fuel_product_qty,
                        'product_uos':  pick.deliver_product_uom.id,
                        'location_id': pick.fuel_location_id.id ,
                        'location_dest_id': pick.fuel_location_dest_id.id,
                        'tracking_id': False,
                        'state': 'draft',
                        'price_unit': pick.deliver_product_price or 0.0,
                        'move_type': 'one',
                        'fuel_ok': True,
                            }
                    self.pool.get('stock.move').create(cr, uid, val, {})

        return super(stock_picking_in, self).draft_force_assign(cr, uid, ids, *args)

    def button_hq_receive(self, cr, uid, ids, context={}):
        """
        """
        stock_partial_obj = self.pool.get('stock.partial.picking')
        picking = self.browse(cr, uid, ids[0], context)
        
        if picking.product_qty_after == 0:
            raise osv.except_osv(_(''), _("Quantity after should be more than Zero "))
        if picking.product_qty_after < picking.product_qty_before:
            raise osv.except_osv(_(''), _("Quantity after should be more than Quantity before "))
        if picking.fuel_product_qty != picking.deliver_fuel_product_qty:
            if not picking.reason:
                raise osv.except_osv(_(''), _("You must enter reason"))

        move_list = []
        # fields = stock_partial_obj._columns.keys()
        # context['active_ids'] = ids 
        # context['active_id'] = ids[0]
        # context['active_model'] = self._name
        # res = stock_partial_obj.default_get(cr,uid,fields,context=context )
        # move_list = [[0,False, move] for move in res['move_ids']]
        
        if move_list or True:
            # partial_vals = res 
            # partial_vals['move_ids'] = move_list
            # parial_id = stock_partial_obj.create(cr, uid,partial_vals, context )
            # return_value = stock_partial_obj.do_partial(cr, uid, [parial_id], context)
            #print ".................return_value",return_value,picking.move_lines
            #o = p
            for line in picking.move_lines:
                line.write({'product_qty':picking.fuel_product_qty , 'product_uos_qty':picking.fuel_product_qty, 'state':'done'})
            #return return_value
        
        return self.write(cr, uid, ids, {'state':'done'})


#----------------------------------------------------------
# Stock Picking OUT
#----------------------------------------------------------
class stock_picking_out(osv.osv):
    _inherit = "stock.picking.out"

    def button_cancel_in_done(self, cr, uid, ids, context=None):
        """ cancel picking directly from done state.
        @return: True
        """
        for pick in self.browse(cr, uid, ids):
            if pick.fuel_ok == True:
                cr.execute("update stock_picking set state='cancel' where id="+str(pick.id)+";")
                cr.execute("update stock_move set state='cancel' where picking_id="+str(pick.id)+";")
        return True
    
    def _amount_all(self, cr, uid, ids, name, args, context=None):
        res = {}
        for move in self.browse(cr, uid, ids, context=context):
            res[move.id] = 0.0
            res[move.id] += move.product_id.standard_price * move.product_qty
        return res

    def _get_product(self, cr, uid, ids, context=None):
        idss = []
        for product in self.pool.get('product.product').browse(cr, uid, ids, context=context):
            if product.fuel_ok:
                idss = self.pool.get('stock.move').search(cr, uid, [(
                    'product_id', '=', product.id), ('state', '!=', 'done'), ('fuel_ok', '=', True)], context=context)
        return idss
    
    def _get_stock_move(self, cr, uid, ids, context=None):
        result = {}
        for line in self.pool.get('stock.move').browse(cr, uid, ids, context=context):
            if line.fuel_ok:
                result[line.picking_id.id] = True
        return result.keys()

    
    def _get_child_location(self, cr, uid, ids, name, args, context=None):
        result = {}
        for line in self.browse(cr, uid, ids, context=context):
            result[line.id] = False
            for move in line.move_lines:
                result[line.id] = move.location_id.id
        return result

    _columns = {
        'fuel_ok': fields.boolean('Fuel Location', help="Determine This Location Is Fuel Location"),
        'exchange_id': fields.many2one('exchange.order', 'Exchange Order', readonly=True,
                                       ondelete='set null', select=True),
        'hq': fields.boolean('Is HQ'),
        'fleet_employee_id': fields.many2one('hr.employee', 'Driver'),
        'fleet_degree_id': fields.many2one('hr.salary.degree', 'Driver Degree'),
        'fleet_department_id': fields.many2one('hr.department', 'Driver Department'),
        'fleet_emp_code': fields.char('Military Number'),
        'fuel_type': fields.selection([('gasoline', 'Gasoline'), ('diesel', 'Benzene'), ('electric', 'Electric'), ('hybrid', 'Hybrid')],
                                      'Fuel Type', help='Fuel Used by the vehicle'),
        'fuel_product_id': fields.many2one('product.product', 'Fuel'),
        'stock_fuel_id': fields.one2many('stock.picking.fuel','picking_id','Vehicle lines'),
        'card_no': fields.char('Fuel Card Number'), 
        'fuel_delegate_id': fields.many2one('fuel.delegate', 'Employee'),
        'outgoing_fuel_type': fields.many2one('outgoing.fuel.type', 'Outgoing Type'),
        'require_user': fields.boolean(string="Require Employee",readonly=1),
        'wells_ids': fields.one2many('picking.well','picking_id','Wells'),
        'deliver_fuel_product_fuel_type' : fields.related('deliver_fuel_product_id', 'fuel_type', 
        type="selection",selection=[('gasoline', 'Gasoline'), ('diesel', 'Benzene'), ('electric', 'Electric'), ('hybrid', 'Hybrid')], string="Fuel Type"),
        'reason': fields.text('Reason'),
        'receipt_no': fields.char('Receipt Number'),
        'desc': fields.text('Description'),
        'confiscation_employee_id': fields.many2one('hr.employee', 'Confiscation Employee'),

        'fuel_out_location_id': fields.function(_get_child_location, type='many2one', relation='stock.location', string='Location', store={
            'stock.picking': (lambda self, cr, uid, ids, c={}: ids, ['move_lines'], 20),
            'stock.move': (_get_stock_move, ['picking_id', 'product_id', 'product_qty', 'product_amount', 'id', 'location_id'], 10),
        }),
    }

    _defaults = {
        'fuel_ok': 0,
        'require_user': 0,
        'hq': lambda self, cr, uid, context: self.pool.get('res.users').browse(cr, uid, uid, context=context).company_id.hq,
    }

    def create(self, cr, user, vals, context=None):
        """
        Override create to call create of stock.picking
        """
        # if 'default_fuel_ok' in context and context['default_fuel_ok'] == True:
        #picking_obj = self.pool.get('stock.picking')
        #seq_obj_name =  self._name
        #vals['name'] = self.pool.get('ir.sequence').get(cr, user, seq_obj_name)
        if context is None:
            context = {}
        
        hq = self.pool.get('res.users').browse(cr, user, user, context=context).company_id.hq
        vals['hq'] = hq
        if 'default_fuel_ok' in context and context['default_fuel_ok'] == True:
            if 'fleet_employee_id' in vals and 'hq' in vals and vals['hq'] == True:
                onchange_emp = self.onchange_fleet_employee_id(cr, user, [], vals['fleet_employee_id'])['value']
                vals['fleet_degree_id'] = onchange_emp['fleet_degree_id']
                vals['fleet_department_id'] = onchange_emp['fleet_department_id']
                vals['fleet_emp_code'] = onchange_emp['fleet_emp_code']

            if 'fuel_delegate_id' in vals and 'hq' in vals and vals['hq'] != True:
                onchange_delegate_id = self.onchange_fuel_delegate_id(cr, user, [], vals['fuel_delegate_id'])['value']
                vals['fleet_degree_id'] = onchange_delegate_id['fleet_degree_id']
                vals['fleet_department_id'] = onchange_delegate_id['fleet_department_id']
                vals['fleet_emp_code'] = onchange_delegate_id['fleet_emp_code']

            if 'fuel_product_id' in vals and 'hq' in vals and vals['hq'] != True:
                fuel_product_id = vals['fuel_product_id']
                fuel_delegate_id = vals['fuel_delegate_id']
                fuel_type = vals['fuel_type']
                onchange_fuel_product_id = self.onchange_fuel_product_id(cr, user, [],fuel_product_id,fuel_delegate_id,fuel_type)['value']
                vals['card_no'] = onchange_fuel_product_id['card_no']


        return super(stock_picking_out, self).create(cr, user, vals, context)


    def write(self, cr, uid, ids, vals, context=None):
        """
        Override write to call write of stock.picking
        """
        # if 'default_fuel_ok' in context and context['default_fuel_ok'] == True:
        picking_obj = self.pool.get('stock.picking')
        for rec in self.browse(cr, uid, ids, context):
            if rec.fuel_ok:
                hq = rec.hq
                if 'hq' in vals:
                    hq = vals['hq']
                if 'fleet_employee_id' in vals and hq == True:
                    onchange_emp = self.onchange_fleet_employee_id(cr, uid, ids, vals['fleet_employee_id'])['value']
                    vals['fleet_degree_id'] = onchange_emp['fleet_degree_id']
                    vals['fleet_department_id'] = onchange_emp['fleet_department_id']
                    vals['fleet_emp_code'] = onchange_emp['fleet_emp_code']

                if 'fuel_delegate_id' in vals and hq != True:
                    onchange_delegate_id = self.onchange_fuel_delegate_id(cr, uid, ids, vals['fuel_delegate_id'])['value']
                    vals['fleet_degree_id'] = onchange_delegate_id['fleet_degree_id']
                    vals['fleet_department_id'] = onchange_delegate_id['fleet_department_id']
                    vals['fleet_emp_code'] = onchange_delegate_id['fleet_emp_code']

                if 'fuel_product_id' in vals and hq != True:
                    fuel_product_id = 'fuel_product_id' in vals and vals['fuel_product_id'] or rec.fuel_product_id.id
                    fuel_delegate_id = 'fuel_delegate_id' in vals and vals['fuel_delegate_id'] or rec.fuel_delegate_id.id
                    fuel_type = 'fuel_type' in vals and vals['fuel_type'] or rec.fuel_type
                    onchange_fuel_product_id = self.onchange_fuel_product_id(cr, uid, ids,fuel_product_id,fuel_delegate_id,fuel_type)['value']
                    vals['card_no'] = onchange_fuel_product_id['card_no']
                super(stock_picking_out, self).write(cr, uid, [rec.id], vals, context)
            else:
                super(stock_picking_out, self).write(cr, uid, [rec.id], vals, context)
        return True


    def onchange_fuel_company_id(self, cr, uid, ids, company_id, context={}):
        """
        method return value of hq
        """
        hq = self.pool.get('res.company').browse(cr, uid, company_id, context).hq
        if hq is None:
            hq = False

        return {'value':{'hq':hq},'domain':{}}

    def onchange_fleet_employee_id(self, cr, uid, ids, fleet_employee_id, context={}):
        """
        """
        vals = {'fleet_degree_id': False, 'fleet_department_id':False, 'fleet_emp_code': False, 'fuel_delegate_id': False}
        if fleet_employee_id:
            emp = self.pool.get('hr.employee').browse(cr, uid, fleet_employee_id)
            vals['fleet_degree_id'] = emp.degree_id.id
            vals['fleet_department_id'] = emp.department_id.id
            vals['fleet_emp_code'] = emp.emp_code
            #onchange_values = self.onchange_fuel_delegate_id(cr, uid, fleet_employee_id, context)['value']
            #vals.update(onchange_values)

        return {'value': vals}


    def onchange_outgoing_fuel_type(self, cr, uid, ids, outgoing_fuel_type, context={}):
        """
        """
        vals = {'require_user': False,}
        if outgoing_fuel_type:
            outgoing_fuel = self.pool.get('outgoing.fuel.type').browse(cr, uid, outgoing_fuel_type)
            vals['require_user'] = outgoing_fuel.require_user
        return {'value': vals}

    def onchange_fuel_delegate_id(self, cr, uid, ids, fuel_delegate_id, context={}):
        """
        """
        vals = {'fleet_degree_id': False, 'fleet_department_id':False, 'fleet_emp_code': False, 
            'stock_fuel_id': False, 'fuel_type':False}
        if fuel_delegate_id:
            fuel_delegate = self.pool.get('fuel.delegate').browse(cr, uid, fuel_delegate_id)
            vals['fleet_degree_id'] = fuel_delegate.degree_id.id
            vals['fleet_department_id'] = fuel_delegate.department_id.id
            vals['fleet_emp_code'] = fuel_delegate.emp_code        

        return {'value': vals}



    def onchange_fuel_type(self, cr, uid, ids, fuel_type, context={}):
        """
        """
        vals = {'fuel_product_id': False}

        return {'value': vals}


    def onchange_fuel_product_id(self, cr, uid, ids, fuel_product_id,fuel_delegate_id,fuel_type, context={}):
        """
        """
        vals = {'card_no': False}
        if fuel_product_id and fuel_delegate_id:
            fuel_delegate_line_obj = self.pool.get('fuel.delegate.lines')
            fuel_delegate_ids = fuel_delegate_line_obj.search(cr, uid, [('delegate_id','=',fuel_delegate_id),
                ('product_id','=',fuel_product_id)])
            if fuel_delegate_ids:
                card_no = fuel_delegate_line_obj.browse(cr, uid, fuel_delegate_ids[0]).card_no
                vals = {'card_no': card_no}

        return {'value': vals}


    def onchange_stock_fuel_id(self,cr, uid, ids, stock_fuel_id,fuel_delegate_id, context={}):
        """
        """
        if not fuel_delegate_id:
            raise osv.except_osv(_(''), _("You should select driver first"))

        return {}

    def draft_force_assign(self, cr, uid, ids, *args):
        """ Confirms picking directly from draft state.
        @return: True
        """
        wf_service = netsvc.LocalService("workflow")
        for pick in self.browse(cr, uid, ids):
            if pick.fuel_ok == True:
                ## for OC picking out to create stock.move
                if pick.hq == False and pick.type == 'out':
                    if not pick.stock_fuel_id:
                        raise osv.except_osv(_(''), _("Please enter vehicles data"))

                    for line in pick.stock_fuel_id:
                        name = self.pool.get('product.product').name_get(cr, uid, [line.product_id.id])[0][1]
                        val = {
                            'name': name[:250],
                            'picking_id': pick.id,
                            'product_id': line.product_id.id,
                            'product_qty': line.product_qty,
                            'product_uom': line.product_id.uom_id.id,
                            'product_uos_qty': line.product_qty,
                            'product_uos':  line.product_id.id,
                            'location_id': line.location_id.id ,
                            'location_dest_id': line.location_dest_id.id,
                            'tracking_id': False,
                            'state': 'draft',
                            'price_unit': line.product_id.standard_price or 0.0,
                            'move_type': 'one',
                            'fuel_ok': True,
                                }
                        self.pool.get('stock.move').create(cr, uid, val, {})

                    super(stock_picking_out, self).draft_force_assign(cr, uid, [pick.id], *args)
                    self.force_assign(cr, uid, [pick.id], *args)
                else:
                    super(stock_picking_out, self).draft_force_assign(cr, uid, [pick.id], *args)
            else:
                super(stock_picking_out, self).draft_force_assign(cr, uid, [pick.id], *args)

        return True


    def button_oc_receive(self, cr, uid, ids, context={}):
        """
        """
        stock_partial_obj = self.pool.get('stock.partial.picking')
        picking = self.browse(cr, uid, ids[0], context)

        move_list = []
        fields = stock_partial_obj._columns.keys()
        context['active_ids'] = ids 
        context['active_id'] = ids[0]
        context['active_model'] = self._name
        res = stock_partial_obj.default_get(cr,uid,fields, context=context)
        move_list = [[0,False, move] for move in res['move_ids']]

        if move_list:
            partial_vals = res 
            partial_vals['move_ids'] = move_list
            parial_id = stock_partial_obj.create(cr, uid,partial_vals, context )
            return_value = stock_partial_obj.do_partial(cr, uid, [parial_id], context)
            return return_value

        
        return True


#----------------------------------------------------------
# Stock Move
#----------------------------------------------------------
class stock_move(osv.osv):
    _inherit = "stock.move"

    def _amount_all(self, cr, uid, ids, name, args, context=None):
        res = {}
        for move in self.browse(cr, uid, ids, context=context):
            res[move.id] = 0.0
            if move.type == 'in':
                res[move.id] += move.product_id.standard_price * move.product_qty
            elif move.type == 'out':
                res[move.id] += move.product_id.standard_price * move.product_qty
            else:
                continue
        return res

    def _get_product(self, cr, uid, ids, context=None):
        idss = []
        for product in self.pool.get('product.product').browse(cr, uid, ids, context=context):
            if product.fuel_ok:
                idss = self.pool.get('stock.move').search(cr, uid, [
                    ('product_id', '=', product.id), ('state', '!=', 'done')], context=context)
        return idss

    def _amount_to_text(self, cr, uid, ids, fields, args, context=None):
        res = {}
        for rec in self.browse(cr, uid, ids, context):
            res[rec.id] = rec.product_amount
            if res[rec.id]:
                res[rec.id] = amount_to_text(res[rec.id])
        return res

    def _amount_to_text_qty(self, cr, uid, ids, fields, args, context=None):
        res = {}
        for rec in self.browse(cr, uid, ids, context):
            res[rec.id] = rec.product_qty
            if res[rec.id]:
                res[rec.id] = amount_to_text(res[rec.id]).replace( unicode('جنيه', 'utf-8'), '' ).replace( unicode('قرش', 'utf-8'), '' )
        return res

    _columns = {
        'fuel_ok': fields.boolean('Fuel Location', help="Determine This Location Is Fuel Location"),
        'product_amount': fields.function(_amount_all,  string='Price',
                                          store={
                                              'stock.move': (lambda self, cr, uid, ids, c={}: ids, ['product_id', 'product_qty'], 20),
                                              'product.product': (_get_product, ['standard_price'], 20),
                                          }),
        'product_amount_ch':fields.function(_amount_to_text, string='Price in words', type="char"),
        'product_qty_ch':fields.function(_amount_to_text_qty, string='Quantity in words', type="char"),
        'hq': fields.boolean('Is HQ'),
        'stock_in_type': fields.selection([('claim','Claim'),('requisition','Requisition')],'Incoming Type'),
        'fuel_type': fields.selection([('gasoline', 'Gasoline'), ('diesel', 'Benzene'), ('electric', 'Electric'), ('hybrid', 'Hybrid')],
                                      'Fuel Type', help='Fuel Used by the vehicle'),
        'vehicle_id': fields.many2one('fleet.vehicle', 'Vehicle'),
        'standard_price' : fields.related('product_id', 'standard_price', type='float', string='Standard Price'),

    }

    def _default_location_destination(self, cr, uid, context=None):
        """ Gets default address of partner for destination location
        @return: Address id or False
        """
        mod_obj = self.pool.get('ir.model.data')
        picking_type = context.get('picking_type')
        location_id = False
        if context is None:
            context = {}
        if 'default_fuel_ok' in context and context['default_fuel_ok'] == True:
            return False
        else:
            return super(stock_move, self)._default_location_destination(cr, uid, context)

    def _default_location_source(self, cr, uid, context=None):
        """ Gets default address of partner for source location
        @return: Address id or False
        """
        mod_obj = self.pool.get('ir.model.data')
        picking_type = context.get('picking_type')
        location_id = False

        if context is None:
            context = {}

        if 'default_fuel_ok' in context and context['default_fuel_ok'] == True:
            return False
        else:
            return super(stock_move, self)._default_location_source(cr, uid, context)

    def onchange_fuel_company_id(self, cr, uid, ids, company_id, context={}):
        """
        method return value of hq
        """
        hq = self.pool.get('res.company').browse(cr, uid, company_id, context).hq
        if hq is None:
            hq = False

        return {'value':{'hq':hq},'domain':{}}

    _defaults = {
        'fuel_ok': 0,
        'location_id': _default_location_source,
        'location_dest_id': _default_location_destination,
        'hq': 0,
        'stock_in_type': False,
    }


#----------------------------------------------------------
# Stock Partial Picking
#----------------------------------------------------------
class stock_partial_picking(osv.osv_memory):
    _inherit = "stock.partial.picking"


    def do_partial(self, cr, uid, ids, context=None):
        """
        Inherit fuction to add constrains in picking 
        @return: super function of stock_partial_move
        """
        uom_obj = self.pool.get('product.uom')
        partial = self.browse(cr, uid, ids[0], context=context)
        picking_type = partial.picking_id.type
        if partial.picking_id.fuel_ok == True and picking_type == 'in':

            for wizard_line in partial.move_ids:
                line_uom = wizard_line.product_uom

                #Adding a check whether any move line contains exceeding  real location qty to original moveline
                qty_in_line_uom = uom_obj._compute_qty(cr, uid, line_uom.id, wizard_line.quantity,  wizard_line.move_id.product_uom.id)
                if wizard_line.move_id.location_id.usage == 'internal' and qty_in_line_uom > wizard_line.real_qty:
                        raise osv.except_osv(_('Warning'), _('Processing quantity  is larger than the available quantity in the fuel location!'))
            
        return super(stock_partial_picking, self).do_partial(cr, uid, ids, context=context)


#----------------------------------------------------------
# Stock Picking fuel
#----------------------------------------------------------
class stock_picking_fuel(osv.osv_memory):
    _name = "stock.picking.fuel"

    _columns = {
        'picking_id': fields.many2one('stock.picking', 'Picking', ondelete="cascade"),
        'product_id': fields.many2one('product.product', 'Fuel'),
        'vehicle_id': fields.many2one('fleet.vehicle', 'Vehicle'),
        'location_id': fields.many2one('stock.location', 'Location',),
        'location_dest_id': fields.many2one('stock.location', 'Dest. Location'),
        'product_qty': fields.float('Quantity', digits_compute=dp.get_precision('Product Unit of Measure')),
    }


    def onchange_product(self,cr , uid, ids, product_id, context={}):
        """
        """
        vals = {'product_uom': False}
        if product_id:
            product = self.pool.get('product.product').browse(cr, uid, product_id, context)
            vals['product_uom'] = product.uom_id.id
        return {'value': vals}



    def create(self, cr, uid, vals, context={}):
        """
        overwrite create method to change related vehicle fieldsvals['product_qty_before']
        @return: super method
        """
        product_id = vals['product_id']
        vals['product_uom'] = self.onchange_product(cr, uid, [],product_id )['value']['product_uom']

        return super(stock_picking_fuel, self).create(cr, uid, vals, context)


    def write(self, cr, uid, ids, vals, context={}):
        """
        overwrite write method to change related vehicle fields
        @return: super method
        """
        for rec in self.browse(cr, uid, ids, context):
            
            product_id = 'product_id' in vals and vals['product_id'] or rec.product_id.id
            vals['product_uom'] = self.onchange_product(cr, uid, [],product_id )['value']['product_uom']

        return super(stock_picking_fuel, self).write(cr, uid, ids, vals, context)

    def _check_location(self, cr, uid, ids, context=None):
        
        for rec in self.browse(cr, uid, ids, context=context):
            if rec.location_id.id == rec.location_dest_id.id:
                raise osv.except_osv(_(''), _("You can not transfer fuel from/to the same location"))
        return True 

    def _check_quantity(self, cr, uid, ids, context=None):
        for rec in self.browse(cr, uid, ids, context=context):
            if rec.product_qty <= 0:
                raise osv.except_osv(_(''), _("Quantity should be more than Zero "))
            

        return True


    _constraints = [
        (_check_quantity, _(''), ['product_qty']),
        (_check_location, _(''), ['location_id','location_dest_id']),
    ]


#----------------------------------------------------------
# product_product (Inherit)
#----------------------------------------------------------


class product_product(osv.Model):

    _inherit = "product.product"


    def name_search(self, cr, uid, name, args=None, operator='ilike', context=None, limit=100):
        if context is None:
            context = {}
        ids = []
        if 'fuel_delegate' in context and context['fuel_delegate'] != False:
            idss = []
            if 'fuel_type' in context and context['fuel_type'] != False:
                fuel_delegate_line_obj = self.pool.get('fuel.delegate.lines')
                fuel_delegate_ids = fuel_delegate_line_obj.search(cr, uid, [('delegate_id','=',context['fuel_delegate']),
                    ('fuel_type','=',context['fuel_type'])])
                if fuel_delegate_ids:
                    product = fuel_delegate_line_obj.browse(cr, uid, fuel_delegate_ids[0]).product_id.id
                    idss.append(product)

            args.append(('id', 'in', idss))

        return super(product_product, self).name_search(cr, uid, name, args=args, operator=operator, context=context, limit=limit)


#----------------------------------------------------------
# fleet_vehicle (Inherit)
#----------------------------------------------------------


class fleet_vehicle(osv.Model):

    _inherit = "fleet.vehicle"


    def name_search(self, cr, uid, name, args=None, operator='ilike', context=None, limit=100):
        """
        Overwite name_search to not select already existed record per lines
        @return: super 
        """
        lines = []
        emp_cost=[]
        vehicle_ids = []
        ids = []
        if context is None:
            context = {}
        if 'model' in context and context['model'] == 'stock.picking.fuel':

            line_ids = resolve_o2m_operations(cr, uid, self.pool.get(context['model']),
                                                context.get('line_ids'), ["vehicle_id"], context)            
            args.append(('id', 'not in', [isinstance(
                d['vehicle_id'], tuple) and d['vehicle_id'][0] or d['vehicle_id'] for d in line_ids]))

        return super(fleet_vehicle, self).name_search(cr, uid, name, args=args, operator=operator, context=context, limit=limit)
