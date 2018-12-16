# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

from osv import fields,osv
import time
import netsvc
from tools.translate import _
import decimal_precision as dp
from collections import defaultdict
from admin_affairs.copy_attachments import copy_attachments as copy_attachments
from tools.amount_to_text_en import amount_to_text
from base_custom.amount_to_text_ar import amount_to_text as amount_to_text_ar

class fuel_plan(osv.osv):
    """
    To manage fule plane and its operations """

    def _cost_total(self, cr, uid, ids, field_name, arg, context={}):
        """ 
        Functional field function Finds the total cost of fuel plan.
        
        @param field_name: list contains name of fields that call this method
        @param arg: extra arguement
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
        @param arg: extra arguement
        @return: Dictionary of fule total values
        """
        res={}
        for fuel_order in self.browse(cr, uid, ids, context=context):
            res[fuel_order.id] = { 'gasoline_total': 0.0, 'petrol_total': 0.0}
            gasoline_total = 0.0
            petrol_total = 0.0
            for line in fuel_order.quantity_ids:
                gasoline_total += line.gasoline_qty
                petrol_total += line.petrol_qty
            res[fuel_order.id]['gasoline_total'] = gasoline_total 
            res[fuel_order.id]['petrol_total'] = petrol_total 
        return res
    
    def create(self, cr, uid, vals, context=None):
        """
        Create new entry sequence for every new fuel plan Record.

        @param vals: record to be created
        @return: return a result that create a new record in the database
        """
        if ('name' not in vals) or (vals.get('name')=='/'):  
            vals['name'] = self.pool.get('ir.sequence').get(cr, uid, 'fuel.plan')
        return super(fuel_plan, self).create(cr, uid, vals, context)
    
    def changes_state(self, cr, uid, ids, vals,context=None):
        """ 
        Changes fuel plan state.
 
        @vals: dict that will be used in write method
        @return: Boolean True
        """        
        for plan in self.browse(cr, uid, ids, context=context):
            self.write(cr, uid, [plan.id], vals)
        return True
    

    def confirmed(self, cr, uid, ids, context=None):
        """
        change state of fuel plan order from draft To confirmed.
 
        @return: Boolean True      
        """
        self.write(cr, uid, ids, {'state':'confirmed'},context=context)
        return True
    
    def action_cancel_draft(self, cr, uid, ids,context=None):
        """ 
        Changes fuel plan state
 
        @return: Boolean True or false
        """   
        if not len(ids):
            return False
        wf_service = netsvc.LocalService("workflow")
        for order_id in ids:
            # Deleting the existing instance of workflow for order
            wf_service.trg_delete(uid, 'fuel.plan', order_id, cr)
            wf_service.trg_create(uid, 'fuel.plan', order_id, cr)
        for (id, name) in self.name_get(cr, uid, ids):
            message = _("fuel plan order'%s' has been set in draft state.") % name
            self.log(cr, uid, id, message)
        self.changes_state(cr, uid, ids,{'state': 'draft'},context={})
        return True
    
    def copy(self, cr, uid, id, default=None, context=None):
        """
        Duplicate the fuel plan record and generate sequence to the new record.

        @param default: dict that contains some fields default value and used in the copy method
        @return: Id of the new record
        """
        if default is None:
            default = {}
        default = default.copy()
        plan_obj = self.browse(cr, uid, id, context=context)
        if ('name' not in default) or (plan_obj.name == '/'):
            seq_obj_name = 'fuel.plan'
            default['name'] = self.pool.get('ir.sequence').get(cr, uid, seq_obj_name)
            default['state'] = 'draft'
            default['voucher_no'] = ''
        res = super(fuel_plan, self).copy(cr, uid, id, default, context)
        return res
    
    def unlink(self, cr, uid, ids, context=None):
        """
        Delete the fuel plan record if record in draft or cancel state,
        and create log message to the deleted record.

        @return: super unlink method
        """
        fuel_plans = self.read(cr, uid, ids, ['state'], context=context)
        unlink_ids = []
        for s in fuel_plans:
            if s['state'] in ['draft', 'cancel']:
                unlink_ids.append(s['id'])
            else:
                raise osv.except_osv(_('Invalid action !'), _('In order to delete a fuel plan order(s), it must be cancelled first!'))
        wf_service = netsvc.LocalService("workflow")
        for id in unlink_ids:
            wf_service.trg_validate(uid, 'fuel.plan', id, 'fuel_cancel', cr)
            fuel_plan_name = self.browse(cr, uid, id, context=context).name
            message = _("fuel plan order '%s' has been deleted.") % fuel_plan_name
            self.log(cr, uid, id, message)
        return super(fuel_plan, self).unlink(cr, uid, unlink_ids, context=context)
    
    def _prepare_order_line_move(self, cr, uid,fuel_plan, product, picking_id, product_qty, fuel_type, context=None):
        """
        Prepare the dict of values to create the new stock move for a
        fuel plan order.

        @param browse_record order: fuel.plan record 
        @param browse_record product: product 
        @param int picking_id: ID of fuel picking 
        @param product_qty : product qty
        @return: dict of values to create() the stock move
        """
        location_dest_id = False
        if fuel_type == 'fixed_fuel':
            location_dest_id = product.property_fuel_fixed.id
        elif fuel_type == 'extra_fuel':
            location_dest_id = product.property_fuel_extra.id

        return {
            'name': product.name,
            'fuel_picking_id': picking_id,
            'product_id': product.id,
            'product_qty': product_qty,
            'product_uom': product.uom_id.id,
            'product_uos_qty':product_qty,
            'product_uos': product.uom_id.id,
            'location_id': fuel_plan.partner_id.property_stock_supplier.id ,
            'location_dest_id': location_dest_id ,
            'state': 'draft',
            #'note': line.notes,
            'price_unit': product.standard_price or 0.0,
        }

    def _prepare_order_picking(self, cr, uid, order, context=None):
        """
        Prepare the dict of values to create the new picking for a
        fuel plan order.

        @param browse_record order: fuel.plan record
        @return: dict of values to create() the picking
        """
        pick_name = self.pool.get('ir.sequence').get(cr, uid, 'fuel.picking.in')
        return {
            'name': pick_name,
            'origin': order.name,
            'date': order.date,
            'type': 'in',
            'note': order.notes,
            'department_id':order.department_id.id,
            'company_id':order.company_id.id,
            'fuel_plan_id':order.id,
        }
        
    def _create_picking(self, cr, uid, fuel_plan,fuel_type, context={}):
        """ 
        Finish the fuel plan order and create two picking : one for fixed fuel and another for extra fuel.
        @param fuel_plan: browse record
        @param fuel_type:fuel_type
        @return: True
        """
        pick_obj=self.pool.get('fuel.picking')
        move_obj = self.pool.get('stock.move')
        product_obj=self.pool.get('product.product')
        picking_id = pick_obj.create(cr, uid, self._prepare_order_picking(cr, uid, fuel_plan, context=context))  
        product_dict = defaultdict(list)
        for fuel_qty in fuel_plan.quantity_ids:
            if fuel_qty.fuel_type == fuel_type:
                for line in fuel_qty.qty_lines:
                    product_dict[line.product_id.id].append(line.product_qty)

        for product_id in product_dict.keys():
            product_qty = sum(product_dict[product_id])
            product = product_obj.browse(cr,uid,product_id,context)
            move_id = move_obj.create(cr, uid, self._prepare_order_line_move(cr, uid,fuel_plan, product, picking_id, product_qty,fuel_type, context=context))
            
        return picking_id 
 
    def _create_picking_out(self, cr, uid, ids,fuel_type, context={}):
        """ 
        Finish the fuel plan order and create out-picking for fixed_fuel orders.

        @param fuel_type:fuel_type
        @return: Boolean True
        """
        pick_obj=self.pool.get('fuel.picking')
	archive_obj = self.pool.get('fuel.archive.quantity')
        move_obj = self.pool.get('stock.move')
        product_obj=self.pool.get('product.product')
        plan_obj = self.browse(cr, uid, ids)
        for plan in plan_obj:
            for line in plan.quantity_ids:

		archive_id = archive_obj.create(cr,uid,{

                	'plan_id':plan.id,
                	'department_id':line.department_id.id,
			'fuel_type':line.fuel_type,
  			'month':plan.month,
    			'year': plan.year,
                	'gasoline_qty': line.gasoline_qty,
                	'petrol_qty': line.petrol_qty,



			})
                if line.fuel_type == 'fixed_fuel':

                    picking_id = pick_obj.create(cr, uid, {
                    'origin': line.plan_id.name,
                    'date': line.plan_id.date,
                    'type': 'out',
                    'note': line.plan_id.notes,
                    'department_id':line.department_id.id,
                    'fuel_plan_id':line.plan_id.id,

                                    })
                    for product in line.qty_lines:
                        location_id = product_obj.browse(cr, uid, product.product_id.id).property_fuel_fixed.id
                        move_obj.create(cr, uid, {
                        'name': product.product_id.name,
                        'fuel_picking_id': picking_id,
                        'product_id': product.product_id.id,
                        'product_qty': product.product_qty,
                        'product_uom': product.product_uom.id,
                        'location_id': location_id,
                        'location_dest_id': product.qty_id.plan_id.partner_id.property_stock_customer.id , 
                        'state': 'draft',
                        'price_unit': product.price_unit or 0.0, 
                        #'company_id':product.company_id.id     
                             })               
        return True    
    
    def create_financial_voucher(self,cr,uid,ids,context=None):
        """ 
        create a financial voucher for Fuel plan.
 
        @return: Boolean True
        """
        account_journal_obj = self.pool.get('account.journal')   
        account_obj = self.pool.get('account.account')
        voucher_obj = self.pool.get('account.voucher')
        voucher_line_obj = self.pool.get('account.voucher.line')
        affairs_account_obj = self.pool.get('admin_affairs.account') 
        affairs_model_obj = self.pool.get('admin.affairs.model') 
        for plan in self.browse(cr, uid, ids, context=context):
            affairs_model_ids = affairs_model_obj.search(cr, uid, [('model','=','fuel.plan')], context=context)
            affairs_account_ids = affairs_account_obj.search(cr, uid, [('model_id','=',affairs_model_ids[0])], context=context)
            if not affairs_account_ids:
                raise osv.except_osv(_('Error'), _("Please enter the fuel plan accounting configuration"))
            affairs_account = affairs_account_obj.browse(cr, uid, affairs_account_ids[0], context=context)
            account_ids = account_obj.search(cr, uid, [('company_id','=',plan.company_id.id),('code','=',str(affairs_account.code))], context=context)
            journal_ids =  account_journal_obj.search(cr, uid, [('company_id','=',plan.company_id.id),('name','=',affairs_account.name_type.name)], context=context)
            journal_id = journal_ids and journal_ids[0] or affairs_account.journal_id.id
            account_id = account_ids and account_ids[0] or affairs_account.account_id.id
            analytic_id = affairs_account.analytic_id 
            # Creating Voucher / Ratitication
            cr.execute('''SELECT distinct
 sum(line.product_qty *line.price_unit) as ful_total,a.id 
 from
  public.fuel_plan as plan, 
  public.fuel_qty_line as line, 
  public.fuel_quantity as qtun, 
  public.hr_department as h, 
  public.account_analytic_account as a
WHERE 
  qtun.plan_id = plan.id AND
  qtun.id = line.qty_id AND
  h.id = qtun.department_id AND
  a.id = h.analytic_account_id and plan.id=%s
GROUP BY  a.id '''%plan.id)
            res =  cr.dictfetchall()
            voucher_id = voucher_obj.create(cr, uid, {
                 'amount':plan.cost,
                 'journal_id':journal_id , 
                 'type': 'ratification',
                 'date': time.strftime('%Y-%m-%d'),
                 'partner_id': plan.partner_id.id, 
                 'department_id': plan.department_id.id,
                 'state': 'draft',
                 'notes': plan.notes,
                 'narration': 'Fuel plan No: ',
                'amount_in_word':amount_to_text_ar(plan.cost),
                                    }, context=context)
            for line in res:
                voucher_line_dict = {
                             'voucher_id':voucher_id,
                             'account_analytic_id': line['id'],
                             'account_id': account_id,
                             'amount':line['ful_total'],
                             'type':'dr',
                             'name': plan.name,
                               }
                voucher_line_obj.create(cr, uid, voucher_line_dict, context=context)
            # Selecting Voucher Number / Refernece 
            #voucher_number = voucher_obj.browse(cr,uid,voucher_id,context=context).number
            #################### update workflow state###############
            vouchser_state = 'draft'
            if plan.company_id.affairs_voucher_state : 
                vouchser_state = plan.company_id.affairs_voucher_state 
            wf_service = netsvc.LocalService("workflow")
            if voucher_id : res = wf_service.trg_validate(uid, 'account.voucher',voucher_id, vouchser_state, cr)
            #if voucher_id and plan.company_id.id!=16: res = wf_service.trg_validate(uid, 'account.voucher',voucher_id, 'prepost', cr)
            
            self.write(cr, uid, plan.id,{'state': 'done','voucher_no':voucher_id},context=context)
            copy_attachments(self,cr,uid,ids,'fuel.plan',voucher_id,'account.voucher', context)
        return True
        

    def done(self, cr, uid, ids, context={}):
        """ 
        Finish the fuel plan order and create two picking : one for 
        fixed fuel and another for extra fuel.

        @return: Boolean True
        """
        payment_enrich_obj = self.pool.get('payment.enrich')
        payment_enrich_lines_obj = self.pool.get('payment.enrich.lines')
        wf_service = netsvc.LocalService("workflow")
        for fuel_plan in self.browse(cr, uid, ids,context):
            if not fuel_plan.quantity_ids:
                raise osv.except_osv(_('Fuel quantities!'), _('You cannot complete fuel plan order without fuel quantities'))
            if fuel_plan.payment_selection == 'enrich':
                    #details = smart_str('Public Relation Request No:'+record.name+'\nProcedure For:'+record.procedure_for+'\nprocedure:'+record.procedure_id.name+'\nPurpose:'+record.purpose.name)
                    details = 'Fixed Fuel Plan No:'+fuel_plan.name
                    enrich_payment_lines_id = payment_enrich_lines_obj.create(cr, uid, {
					            'enrich_id':fuel_plan.enrich_category.id,
                        		'cost': fuel_plan.cost,
					            'date':time.strftime('%Y-%m-%d'),
					            'state':'draft',
                        		'name':details,
					            'department_id':fuel_plan.department_id.id,
                            				}, context=context)
                    #self.write(cr, uid, ids, {'state':'done'},context=context)
            elif fuel_plan.payment_selection == 'voucher':  
                #create picking for fixed fuel
                fixed_picking_id = self._create_picking(cr, uid, fuel_plan,'fixed_fuel', context)
                #create picking for extra fuel
                extra_picking_id = self._create_picking(cr, uid, fuel_plan,'extra_fuel', context)
                #create picking (picking-out) for fixed fuel
                self._create_picking_out(cr, uid, ids,'fixed_fuel', context)
                #create voucher for fuel plan
                self.create_financial_voucher(cr,uid,ids,context)

        
        self.write(cr, uid, ids, {'state':'done'})

        return True
     
    STATE_SELECTION = [
        ('draft', 'Draft'),
        ('confirmed', 'Officer approve'),
        ('approve', 'Waiting for section service'),
        ('done', 'Waiting for affair manager'),
        ('cancel', 'Cancel'), ]
   
    def _get_months(self, cr, uid, context):
       """
       Get month depend on date
       @return: List contain string of month
       """
       months=[(str(n),str(n)) for n in range(1,13)]
       return months

    PAYMENT_SELECTION = [
    		('voucher', 'Voucher'),
    		('enrich', 'Enrich'), 
    			]

    _name = "fuel.plan"
    _order = "name desc"
    _columns = {
    'name': fields.char('Reference', size=64, required=False, select=True, readonly=True, help="unique number of the fuel plan,computed automatically when the fuel plan order is created"),
    'date' : fields.date('Date',required=True, readonly=True, states={'draft': [('readonly', False)]}),
    'month': fields.selection(_get_months,'Month', readonly=True, select=True),
    'year': fields.char('Year', size=64,readonly=True),
    'quantity_ids':fields.one2many('fuel.quantity', 'plan_id' , 'Department fuel', readonly=True,),
    'state': fields.selection(STATE_SELECTION,'State', readonly=True, select=True),
    'company_id': fields.many2one('res.company', 'Company', required=True, readonly=True),
    'department_id': fields.many2one('hr.department', 'Department',readonly=True, states={'draft': [('readonly', False)]}),
    'cost': fields.function(_cost_total, method=True, digits_compute=dp.get_precision('Account'), string='Cost'),
    'partner_id': fields.many2one('res.partner', 'Partner', states={'done': [('readonly', True)]}),
    'voucher_no': fields.many2one('account.voucher', 'Voucher Number',readonly=True),
    'gasoline_total': fields.function(_fuel_total, method=True, digits=(16,2), string='Total gasoline', multi='total_fuel'),
    'petrol_total': fields.function(_fuel_total, method=True, digits=(16,2), string='Total petrol', multi='total_fuel'),
    'picking_ids':fields.one2many('fuel.picking', 'fuel_plan_id' , 'Fuel picking', readonly=True),
    'notes': fields.text('Notes', size=512),
    'type_plan': fields.char('Plan_type', size=512),
    'payment_selection': fields.selection(PAYMENT_SELECTION,'Payment',states={'done':[('readonly',True)]}, select=True),
    'enrich_category':fields.many2one('payment.enrich','Enrich',readonly=True,states={'approve':[('readonly',False)]}),


    }
    
    _sql_constraints = [
        ('name_uniq', 'unique(name)', 'fuel plan order reference must be unique !'),
        ]
    
    _defaults = {
        'name': lambda self, cr, uid, context: '/',
        'state': 'draft',
		'payment_selection':'enrich',
        'date': lambda *a: time.strftime('%Y-%m-%d'),
        #'company_id': lambda self, cr, uid, c: self.pool.get('res.company')._company_default_get(cr, uid, 'fuel.plan', context=c),
                }
    

class fuel_quantity(osv.osv):
    """
    To manage fule quantity and correspond """

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
   
    def _total_qty(self, cr, uid, ids,field_name, arg, context={}):
        """ 
        Finds the value total of gasoline and petrol quantity.

        @param field_name: list contains name of fields that call this method
        @param arg: extra arguement
        @return: Dictionary of values
        """
        res={}
        for fuel_qty in self.browse(cr, uid, ids, context=context):
            res[fuel_qty.id] = { 'gasoline_qty': 0.0, 'petrol_qty': 0.0}
            gasoline_qty = 0.0
            petrol_qty = 0.0
            for line in fuel_qty.qty_lines:
                gasoline_qty += line.product_qty if (line.product_id.fuel_type=='gasoline') else 0
                petrol_qty += line.product_qty if (line.product_id.fuel_type=='petrol') else 0
            res[fuel_qty.id]['gasoline_qty'] = gasoline_qty 
            res[fuel_qty.id]['petrol_qty'] = petrol_qty 
        return res
    
    _name = "fuel.quantity"
    _description = 'fuel quantity'
    _columns = {
                'department_id': fields.many2one('hr.department', 'Department'),
                'fuel_type': fields.selection([('fixed_fuel','Fixed fuel'),('extra_fuel','Extra fuel')],'Fuel type'),
                'gasoline_qty': fields.function(_total_qty, method=True, digits=(16,2), string='Gasoline Qty', multi='qty_fuel' ),
                'petrol_qty': fields.function(_total_qty, method=True, digits=(16,2), string='Petrol Qty', multi='qty_fuel' ),
                'qty_lines':fields.one2many('fuel.qty.line', 'qty_id' , 'Department fuel',),
                'plan_id': fields.many2one('fuel.plan', 'fuel plan order'),
                'name': fields.text('Note', size=256),
                'total_amount': fields.function(_amount_all, method=True, digits_compute=dp.get_precision('Account'), string='Amount'),
               }
    _defaults = {
        'name': '/',
                }     

class fuel_qty_line(osv.osv):
    """
    To manage fule quantity lines """
    
    def _amount_line(self, cr, uid, ids, field_name, arg, context=None):
        """ 
        Finds the value of fuel in the quantity line.

        @param field_name: list contains name of fields that call this method
        @param arg: extra arguement
        @return: Dictionary of values
        """
        res = {}
        if context is None:
            context = {}
        for line in self.browse(cr, uid, ids, context=context):
            price = line.price_unit * line.product_qty or 0.0
            res[line.id] = price
        return res
    
    _name = "fuel.qty.line"
    _description = 'Fuel Quantity line'
    _columns = {
                'vehicles_id': fields.many2one('fleet.vehicle', 'Car'),
                'department_id': fields.many2one('hr.department', 'Department',),
                'product_id': fields.many2one('product.product', 'Product', required=True),
                'product_qty': fields.float('Quantity', required=True, digits=(16,2)),
                'product_uom': fields.many2one('product.uom', 'Product UOM', required=True),
                'price_unit': fields.float('Unit Price', required=True, digits_compute=dp.get_precision('Account')),
                'qty_id': fields.many2one('fuel.quantity', 'fuel quantity'),
                'name': fields.text('Note', size=256),
                'price_subtotal': fields.function(_amount_line, method=True, string='Sub total',digits_compute=dp.get_precision('Account')),
               }
       

class fuel_archive_quantity(osv.osv):
    """
    To manage fule archive """

    _name = "fuel.archive.quantity"
    _columns = {
                'plan_id': fields.many2one('fuel.plan', 'fuel plan order'),
                'fuel_type': fields.selection([('fixed_fuel','Fixed fuel'),('extra_fuel','Extra fuel')],'Fuel type'),
                'department_id': fields.many2one('hr.department', 'Department'),
  		'month': fields.char('Month', size=64,readonly=True),
    		'year': fields.char('Year', size=64,readonly=True),
                'gasoline_qty': fields.float(digits=(16,2), string='Gasoline Qty'),
                'petrol_qty': fields.float(digits=(16,2), string='Petrol Qty'),
                'name': fields.text('Note', size=256),
               }

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
