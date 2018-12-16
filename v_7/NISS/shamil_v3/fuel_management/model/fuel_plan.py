# -*- coding: utf-8 -*-def create
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2016-2017 NCTR (<http://www.nctr.sd>).
#
##############################################################################

import time
import datetime
from tools.translate import _
from osv import fields,osv
import decimal_precision as dp
from admin_affairs.model.copy_attachments import copy_attachments as copy_attachments

class fuel_plan(osv.osv):
    """ 
    To manage fuel plan and its operations 
    """
    _name = "fuel.plan"

    _order = "name desc"

    STATE_SELECTION = [
        ('draft', 'Draft'),
        ('confirmed', 'Waiting Review and Accreditation'),
        #('approve', 'Service Section Manager Approved'),
        ('done', 'Done'),
        ('cancel', 'Cancel')]

    def _cost_total(self, cr, uid, ids, field_name, arg, context={}):
        """ 
        Functional field function Finds the total cost of fuel plan.
        
        @param field_name: list contains name of fields that call this method
        @param arg: extra arguments
        @return: Dictionary of cost values
        """
        res = {}
        for fuel_plan in self.browse(cr, uid, ids, context=context):
            val = 0.0
            for qty in fuel_plan.quantity_ids:
                val += qty.total_amount
            res[fuel_plan.id] = val 
        return res

    def _fuel_total(self, cr, uid, ids,field_name, arg, context={}):
        """ 
        Finds the total quantity of gasoline and petrol.

        @param field_name: list contains name of fields that call this method
        @param arg: extra arguments
        @return: Dictionary of fuel total values
        """
        res={}
        for fuel_order in self.browse(cr, uid, ids, context=context):
            res[fuel_order.id] = {'gasoline_total': 0.0, 'diesal_total': 0.0, 'electric_total': 0.0, 'hybrid_total': 0.0}
            gasoline_total = 0.0
            diesal_total = 0.0
            hybrid_total = 0.0
            electric_total = 0.0
            for line in fuel_order.quantity_ids:
                gasoline_total += line.fuel_qty if (line.fuel_type=='gasoline') else 0
                diesal_total += line.fuel_qty if (line.fuel_type=='diesel') else 0
                electric_total += line.fuel_qty if (line.fuel_type=='electric') else 0
                hybrid_total += line.fuel_qty if (line.fuel_type=='hybrid') else 0
                
            res[fuel_order.id]['gasoline_total'] = gasoline_total 
            res[fuel_order.id]['diesal_total'] = diesal_total
            res[fuel_order.id]['electric_total'] = electric_total
            res[fuel_order.id]['hybrid_total'] = hybrid_total
        return res

    _columns = {
        'name': fields.char('Reference', size=64, required=False, select=True, readonly=True, 
                            help="Unique Number for Fuel Plan, Computed Automatically When Fuel Plan Order Create"),
        'date' : fields.date('Date',required=True, readonly=True,),
        'month': fields.selection([(str(n),str(n)) for n in range(1,13)],'Month', readonly=True, select=True,),
        'year': fields.char('Year', size=64,readonly=True),
        'quantity_ids':fields.one2many('fuel.quantity', 'plan_id' , 'Department Fuel',
                                       states={'draft':[('readonly',True)],'confirmed':[('readonly',True)],'approve':[('readonly',True)]}),
        'state': fields.selection(STATE_SELECTION,'State', readonly=True, select=True,),
        'company_id': fields.many2one('res.company', 'Company', required=True, readonly=True,
                                      states={'draft':[('readonly',True)],'confirmed':[('readonly',True)],'approve':[('readonly',True)]}),
        'department_id': fields.many2one('hr.department', 'Department',readonly=True),
        'cost': fields.function(_cost_total, method=True, digits_compute=dp.get_precision('Account'), string='Cost',
                                states={'draft':[('readonly',True)],'confirmed':[('readonly',True)],'approve':[('readonly',True)]}),
        'partner_id': fields.many2one('res.partner', 'Partner', states={'done': [('readonly', True)]}),
        'voucher_no': fields.many2one('account.voucher', 'Voucher Number',readonly=True,),
        'gasoline_total': fields.function(_fuel_total, method=True, digits=(16,2), string='Total Gasoline', multi='total_fuel',
                                          states={'draft':[('readonly',True)],'confirmed':[('readonly',True)],'approve':[('readonly',True)]}),
        'diesal_total': fields.function(_fuel_total, method=True, digits=(16,2), string='Total Diesal', multi='total_fuel',
                                        states={'draft':[('readonly',True)],'confirmed':[('readonly',True)],'approve':[('readonly',True)]}),
        'electric_total': fields.function(_fuel_total, method=True, digits=(16,2), string='Total Electric', multi='total_fuel',
                                          states={'draft':[('readonly',True)],'confirmed':[('readonly',True)],'approve':[('readonly',True)]}),
        'hybrid_total': fields.function(_fuel_total, method=True, digits=(16,2), string='Total Hybrid', multi='total_fuel',
                                        states={'draft':[('readonly',True)],'confirmed':[('readonly',True)],'approve':[('readonly',True)]}),
        'notes': fields.text('Notes', size=512),
        'type_plan': fields.selection([('constant_fuel','Constant Fuel'),('mission_extra','Mission Extra')],'Plan Type', size=512,states={'draft':[('readonly',True)],'cancel':[('readonly',True)],'confirmed':[('readonly',True)],'approve':[('readonly',True)]}),
        'payment_method': fields.selection([('voucher', 'Voucher'),('enrich', 'Enrich')],'Payment',
                                           states={'done':[('readonly',True)],'draft':[('readonly',True)],'confirmed':[('readonly',True)]}, select=True),
        'enrich_id':fields.many2one('payment.enrich','Enrich'),
        
        'cost_subtype_id': fields.many2one('fleet.service.type', 'Type',help='Cost type purchased with this cost'),
        'place_id':fields.many2one('vehicle.place', 'Place',),
    }

    _sql_constraints = [
        ('name_uniq', 'unique(name)', _('Fuel Plan Order Reference Must Be Unique!')),
    ]

    _defaults = {
        'name': lambda self, cr, uid, context: '/',
        'state': 'draft',
        'payment_method':'enrich',
        'date': lambda *a: time.strftime('%Y-%m-%d'),
        'company_id': lambda self, cr, uid, c: self.pool.get('res.company')._company_default_get(cr, uid, 'fuel.plan', context=c),
    }

    def create(self, cr, uid, vals, context=None):
        """
        Create new entry sequence for every new fuel plan Record.

        @param vals: record to be created
        @return: return a result that create a new record in the database
        """
        if ('name' not in vals) or (vals.get('name')=='/'):  
            vals['name'] = self.pool.get('ir.sequence').get(cr, uid, 'fuel.plan')
        return super(fuel_plan, self).create(cr, uid, vals, context)

    def plan_cancel(self, cr, uid, ids, context=None):
        """
        change state of fuel plan order from any state To cancel.
 
        @return: Boolean True
        """
        return self.write(cr, uid, ids, {'state':'cancel'},context=context)

    def approve(self, cr, uid, ids, context=None):
        """
        change state of fuel plan order To approve.
 
        @return: Boolean True
        """
        return self.write(cr, uid, ids, {'state':'approve'},context=context)

    def confirmed(self, cr, uid, ids, context=None):
        """
        change state of fuel plan order To confirmed.
 
        @return: Boolean True
        """
        return self.write(cr, uid, ids, {'state':'confirmed'},context=context)
    
    def action_cancel_draft(self, cr, uid, ids,context=None):
        """ 
        Return fuel plan state to draft.
 
        @return: Boolean True or false
        """
        return self.write(cr, uid, ids, {'state':'draft'},context=context)
    
    def copy(self, cr, uid, id, default=None, context=None):
        """
        Duplicate the fuel plan record and generate sequence to the new record.

        @param default: dict that contains some fields default value and used in the copy method
        @return: Id of the new record
        """
        if default is None:
            default = {}
        default.update({'state':'draft', 'voucher_no':False, 'enrich_id':False,
                        'date':datetime.datetime.now().strftime ("%m/%d/%Y")})
        if ('name' not in default):
            default['name'] = self.pool.get('ir.sequence').get(cr, uid, 'fuel.plan')
        return super(fuel_plan, self).copy(cr, uid, id, default, context)
    
    def unlink(self, cr, uid, ids, context=None):
        """
        Delete the fuel plan record if record in draft state.

        @return: super unlink method
        """
        if self.search(cr, uid,[('id','in',ids),('state','!=','draft')],context=context):
            raise osv.except_osv(_('Invalid Action Error'), _('In Order To Delete Fuel Plan Order(s), It Must Be In Draft State!'))
        return super(fuel_plan, self).unlink(cr, uid, ids, context=context)
    
    def create_voucher(self,cr,uid,ids,context=None):
        """ 
        create a financial voucher for Fuel plan.
 
        @return: Boolean True
        """
        voucher_obj = self.pool.get('account.voucher')
        affairs_account_obj = self.pool.get('admin_affairs.account')
        for plan in self.browse(cr, uid, ids, context=context):
            affairs_account_ids = affairs_account_obj.search(cr, uid, [('model_id','=','fuel.plan'), ('service_id','=',plan.cost_subtype_id.id)], context=context)
            if not affairs_account_ids:
                raise osv.except_osv(_('Configuration Error'), _("There Is No Configuration For Fuel Plan Accounting!"))
            affairs_account = affairs_account_obj.browse(cr, uid, affairs_account_ids[0], context=context)
            voucher_id = voucher_obj.create(cr, uid, {
                'amount':plan.cost,
                'journal_id':affairs_account.journal_id.id , 
                'type': 'purchase',
                'date': time.strftime('%Y-%m-%d'),
                'partner_id': plan.partner_id.id, 
                'department_id': plan.department_id.id,
                'state': 'draft',
                'notes': plan.notes,
                'narration': _('Fuel Plan No: ')+plan.name,
                'line_dr_ids': [(0,0,{
                            "account_analytic_id":(affairs_account.analytic_id and affairs_account.analytic_id.id) or (plan.department_id and (plan.department_id.analytic_account_id and plan.department_id.analytic_account_id.id) or False),
                            'account_id': affairs_account.account_id.id,
                            'amount':plan.cost,
                            'type':'dr',
                            'name': plan.name,
                            })]
            }, context=context)
            self.write(cr, uid, plan.id,{'state': 'done','voucher_no':voucher_id},context=context)
            copy_attachments(self,cr,uid,[plan.id],'fuel.plan',voucher_id,'account.voucher', context)
            
        return True

    def done(self, cr, uid, ids, context={}):
        """ 
        Finish the fuel plan order and create two picking, one for 
        fixed fuel and another for extra fuel.

        @return: Boolean True
        """
        '''payment_enrich_lines_obj = self.pool.get('payment.enrich.lines')
        for fuel_plan in self.browse(cr, uid, ids,context):
            if not fuel_plan.quantity_ids:
                raise osv.except_osv(_('ValidateError'), _('In Order To Complete Fuel Plan Order You need To Enter Fuel Quantities!'))
            if fuel_plan.payment_method == 'enrich':
                    details = 'Fixed Fuel Plan No:'+fuel_plan.name
                    payment_enrich_lines_obj.create(cr, uid, {
                                'enrich_id':fuel_plan.enrich_id.id,
                                'cost': fuel_plan.cost,
                                'date':time.strftime('%Y-%m-%d'),
                                'state':'draft',
                                'name':details,
                                'department_id':fuel_plan.department_id.id,
                                'model_id':'fuel.plan',
                    }, context=context)
                    copy_attachments(self,cr,uid,[fuel_plan.id],'fuel.plan',fuel_plan.enrich_id.id,'payment.enrich', context)
            elif fuel_plan.payment_method == 'voucher':  
                self.create_voucher(cr,uid,ids,context)'''
        return self.write(cr, uid, ids, {'state':'done'}, context=context)

#----------------------------------------
# Class fuel quantity
#----------------------------------------
class fuel_quantity(osv.osv):
    """
    To manage fuel quantity and correspond 
    """
    _name = "fuel.quantity"
    
    _description = 'Fuel Quantity'
    
    def _amount_all(self, cr, uid, ids,field_name, arg, context={}):
        """ 
        Finds the value of fuel quantity.

        @param field_name: list contains name of fields that call this method
        @param arg: extra arguement
        @return: Dictionary of values
        """
        res={}
        for fuel_qty in self.browse(cr, uid, ids, context=context):
            val = 0.0
            for line in fuel_qty.qty_lines:
                val += line.price_subtotal
            res[fuel_qty.id] = val 
        return res

    def _spent_qty(self, cr, uid, ids,field_name, arg, context={}):
        '''
        Compute summation of the spent quantity.

        @return: Dictionary of value
        '''
        result = {}
        for spent in self.browse(cr, uid, ids, context=context):
            price =0
            for line in spent.qty_lines: 
                price += line.spent_qty
            result[line.id] = price
        return result

    _columns = {
        #'department_id': fields.related('plan_id','department_id',string='Department',type='many2one',relation='hr.department', store=True),
        'department_id': fields.many2one('hr.department',string='Department'),
        'plan_type': fields.selection([('fixed_fuel','Fixed fuel'),('extra_fuel','Extra fuel')],'Plan Type'),
        'qty_lines':fields.one2many('fuel.qty.line', 'qty_id' , 'Department Fuel',),
        'plan_id': fields.many2one('fuel.plan', 'Fuel Plan Order', ondelete='cascade'),
        'name': fields.text('Note', size=256),
        'total_amount': fields.function(_amount_all, method=True, digits_compute=dp.get_precision('Account'), string='Amount'),
        'fuel_qty': fields.float('Fuel Quantity', required=True, digits_compute=dp.get_precision('Product UoM')),
        'spent_qty':fields.function(_spent_qty, method=True, string='Spent Quantity'),
        'fuel_type': fields.selection([('gasoline','Gasoline'),('diesel','Diesel'),('electric','Electric'),('hybrid','Hybrid')],'Fuel Type'),
        'month': fields.related('plan_id','month', type='selection',selection=[(str(n),str(n)) for n in range(1,13)],string ='Month',readonly=True, ),
        'year': fields.related('plan_id','year', type='char',string ='Year',readonly=True, ),
        'type_plan': fields.related('plan_id','type_plan', type='selection',selection=[('constant_fuel','Constant Fuel'),('mission_extra','Mission Extra')],string ='Plan type',readonly=True, ),
        'place_id':fields.many2one('vehicle.place', 'Place',),
    }

    _defaults = {
        'name': '/',
    }

#----------------------------------------
# Class fuel qty line
#----------------------------------------
class fuel_qty_line(osv.osv):
    """
    To manage fuel quantity lines 
    """
    _name = "fuel.qty.line"
    
    _description = 'Fuel Quantity Details'
    
    def _amount_line(self, cr, uid, ids, field_name, arg, context=None):
        """ 
        Finds the value of fuel in the quantity line.

        @param field_name: list contains name of fields that call this method
        @param arg: extra argument
        @return: Dictionary of values
        """
        res = {}
        if context is None:
            context = {}
        for line in self.browse(cr, uid, ids, context=context):
            price = line.price_unit * line.product_qty or 0.0
            res[line.id] = price
        return res
    
    def _spent_qty_line(self, cr, uid, ids, field_name, arg, context=None):
        '''
        Compute the spent quantity.

        @return Dictionary of value
        '''
        result = {}
        uom_obj = self.pool.get('product.uom')
        fleet_log_obj= self.pool.get('fleet.vehicle.log.fuel')
        for spent in self.browse(cr, uid, ids, context=context):
            result[spent.id] = 0
            vehi_ids = fleet_log_obj.search(cr, uid, [('qty_line_id.id','=',spent.id)], context=context)
            for veh in fleet_log_obj.browse(cr, uid, vehi_ids, context=context):
                    un_convert_unit = veh.product_uom.id
                    convert_unit = spent.product_uom.id
                    result[spent.id] += uom_obj._compute_qty(cr, uid, un_convert_unit, veh.liter, convert_unit)
        return result

    _columns = {
        'vehicles_id': fields.many2one('fleet.vehicle', 'Car'),
        'department_id': fields.many2one('hr.department', 'Department',),
        'product_id': fields.many2one('product.product', 'Product', required=True),
        'product_qty': fields.float('Quantity', required=True, digits=(16,2)),
        'spent_qty':fields.function(_spent_qty_line, method=True, string='Spent Quantity'),
        'product_uom': fields.many2one('product.uom', 'Product UOM', required=True),
        'price_unit': fields.float('Unit Price', required=True, digits_compute=dp.get_precision('Account')),
        'qty_id': fields.many2one('fuel.quantity', 'Fuel Quantity',ondelete='cascade'),
        'name': fields.text('Note', size=256),
        'price_subtotal': fields.function(_amount_line, method=True, string='Sub Total',digits_compute=dp.get_precision('Account')),
        'month': fields.related('qty_id','month', type='selection',selection=[(str(n),str(n)) for n in range(1,13)],string ='Month',readonly=True, store=True),
        'year': fields.related('qty_id','year', type='char',string ='Year',readonly=True, store=True),
        'type_plan': fields.related('qty_id','type_plan', type='selection',selection=[('constant_fuel','Constant Fuel'),('mission_extra','Mission Extra')],string ='Plan type',readonly=True, store=True),
        'place_id':fields.many2one('vehicle.place', 'Place',),
        'company_id': fields.many2one('res.company','Company'),
        'share': fields.boolean('Share'),
    }

    _defaults = {
        'share': False,
    }

class  payment_enrich_lines_custom(osv.osv):
    """ To manage admin affairs payment lines """
    _inherit = "payment.enrich.lines"

    _columns = {
        'model_id': fields.selection([('fuel.plan','Fuel Plan'),('payment.enrich.lines','Enrich Lines'),
         ('fleet.vehicle.log.contract','Vehicle Contract'),('fleet.vehicle.log.fuel','Vehicle Log')],),
    }


