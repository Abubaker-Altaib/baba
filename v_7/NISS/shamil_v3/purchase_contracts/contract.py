# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

from osv import fields,osv
import netsvc
import time
import datetime
from tools.translate import _
import datetime as timedelta
from base_custom import amount_to_text_ar as amount_to_text_ar

class purchase_contract(osv.osv):
    """
    To manage the contract basic concepts and the purchase contracts operations """

    def create(self, cr, user, vals, context=None):
        """ 
        Override to edit the name field by a new sequence. 

        @return: super create method 
        """
        #this method override the create method to add value to the column name
        if ('name' not in vals) or (vals.get('name')=='/'):  
            vals['name'] = self.pool.get('ir.sequence').get(cr, user, 'purchase.contract')
        return super(purchase_contract, self).create(cr, user, vals, context)

    def _amount_all(self, cr, uid, ids, field_name, arg, context=None):
        """
        To calculate all the costs of contract products.

        @return: dictionary of the value of 'amount_untaxed',
                                            'amount_tax',
                                            'amount_total', 
        """
        res = {}
        freight = 0.0
        packing = 0.0
        for contract in self.browse(cr, uid, ids, context=context):
            res[contract.id] = {
                'amount_untaxed': 0.0,
                'amount_tax': 0.0,
                'amount_total': 0.0,
            }
            val = val1 = 0.0
            if contract.freight:freight = contract.freight
            if contract.packing:packing = contract.packing
            for line in contract.contract_line_ids:
                val1 += line.price_subtotal
                val += self._amount_line_tax(cr, uid, line, context=context)
            res[contract.id]['amount_tax'] = val#cur_obj.round(cr, uid, cur, val)
            res[contract.id]['amount_untaxed'] =val1# cur_obj.round(cr, uid, cur, val1)
            res[contract.id]['amount_total'] = res[contract.id]['amount_untaxed'] + res[contract.id]['amount_tax'] + freight + packing
        return res
    
    def _get_order(self, cr, uid, ids, context=None):
        """ 
	    Method that returns the ID of contract line update the 
	    functional field in the contract object consequently.

        @return: list of purchase order lines ids
        """
        result = {}
        for line in self.pool.get('purchase.contract.line').browse(cr, uid, ids, context=context):
            result[line.contract_id.id] = True
        return result.keys()

    def _get_fees_ids(self, cr, uid, ids, context=None):
        """ 
	    Method that returns the ID of contract fees ids update the 
	    functional field in the contract object consequently.

        @return: list of fees lines ids
        """
        result = {}
        for line in self.pool.get('contract.fees').browse(cr, uid, ids, context=context):
            result[line.contract_id.id] = True
        return result.keys()

    def _get_shipment_ids(self, cr, uid, ids, context=None):
        """ 
	    Method that returns the ID of contract shipment ids update the 
	    functional field in the contract object consequently.

        @return: list of shipment lines ids
        """
        result = {}
        for line in self.pool.get('contract.shipment').browse(cr, uid, ids, context=context):
            result[line.contract_id.id] = True
        return result.keys()

    def _amount_line_tax(self, cr, uid, line, context=None):
        """ 
        To calculate the line taxes amount. 

        @param line: contract line id
        @return: tax amount
        """
        val = 0.0
        for c in self.pool.get('account.tax').compute_all(cr, uid, line.tax_id, line.price_unit, line.product_qty)['taxes']:
            val += c.get('amount', 0.0)
        return val

    def _compute_duration(self, cr, uid, ids, field_name, arg, context=None):
        """ 
        Compute the difference between Begin date and end Date. 
        @return: Number of dates between Begin date and end Date
        """
        vals = {}
        for record in self.browse(cr, uid, ids, context):
            start_date = datetime.datetime.strptime(record.start_date, "%Y-%m-%d")
            end_date = datetime.datetime.strptime(record.end_date, "%Y-%m-%d")
            days_no = abs((end_date-start_date).days) + 1
            vals[record.id] = days_no
        return vals

    def _fees_total_amount(self, cr, uid, ids, field_name, arg, context=None):
        """ 
        To calculate the total amount of fees.
        """
        vals = {}
        for record in self.browse(cr, uid, ids):
            sum=0.0
            for fees_id in record.contract_fees_ids:
                sum += fees_id.fees_amount
            vals[record.id] = sum
        return vals

    def _shipment_total_amount(self, cr, uid, ids, field_name, arg, context=None):
        """ 
        To calculate the total amount of shipment.
        """
        vals = {}
        for record in self.browse(cr, uid, ids):
            sum=0.0
            for shipment_id in record.contract_shipment_ids:
                if shipment_id not in ['cancel'] :
                   sum += shipment_id.total_amount
            vals[record.id] = sum
        return vals
           
    TYPE = [
        ('open', 'Open Contract'),
        ('detail', 'Detail Contract'),
    ]
    STATE_SELECTION = [
        ('draft', 'Draft'),
	    ('confirmed', 'Confirmed'),
        ('done', 'Done'),
        ('cancel', 'Cancel'),
    ]
    
    DELIVERY_SELECTION = [
        ('air_freight', 'Air Freight'),
        ('sea_freight', 'Sea Freight'),
        ('land_freight', 'Land Freight'),
    ]
    PYMENT = [('lc','Letter of credit'),
              ('cash','Cash Transfer Advance'),
              ('cad','CAD Cash Against Document'),
              ('partial','Partial and complete after receipt'),
              ('defer','Defer Payment')              ]
    
    _name = 'purchase.contract'
    _description = "Base Contract"
    _columns = {
        'name': fields.char('Reference', size=64, required=True, readonly=1, select=True, 
            help="unique number of the contract, computed automatically when the contract is created"),
        'contract_date':fields.date('Contract Date', required=True, select=True, readonly=True, states={'draft':[('readonly',False)]},
            help="Date on which this document has been created."),
        'start_date': fields.date('Start Date', required=True, select=True, help="Date on which contract is started",readonly=True, states={'draft':[('readonly',False)]},), 
        'end_date': fields.date('End Date', select=True, help="Date on which contract is ended",readonly=True, states={'draft':[('readonly',False)]},),                
        'contract_title': fields.char('Contract Title', size=64, required=True, readonly=True, states={'draft':[('readonly',False)]},), 
        'contract_no' : fields.char('Contract Number' , size=64 ,readonly=True, states={'draft':[('readonly',False)]}, help='This The Internal Contract Number'),
        'contract_duration': fields.function(_compute_duration, string='Contract Duration', digits=(16,0), readonly=True,
            help="duration field is used to set the duration of the contract by days",),
        'contract_type': fields.selection(TYPE, 'Contract type', select=True, readonly=True, states={'draft':[('readonly',False)]},),
        'contract_amount': fields.float('Contract Amount', digits=(16,2), readonly=True, states={'draft':[('readonly',False)]},),
        'delivery_method': fields.selection(DELIVERY_SELECTION, 'Method of dispatch', select=True , readonly=True, states={'draft':[('readonly',False)]}),
        'delivery_period': fields.integer('Delivery period', 
            help="set the delivery period by days", readonly=True, states={'draft':[('readonly',False)]}),
        'delivery_date': fields.date('Delivery Date', select=True, help="Date on which delivery will be done",readonly=True, states={'draft':[('readonly',False)]}), 
        'partner_id': fields.many2one('res.partner', 'Supplier', required=True, select=True,readonly=True, states={'draft':[('readonly',False)]}),
        'pricelist_id': fields.many2one('product.pricelist', 'Pricelist', help="Pricelist for current supplier", readonly=True, states={'draft':[('readonly',False)]}),
        'currency_id': fields.many2one('res.currency','Currency',select=1, readonly=True, states={'draft':[('readonly',False)]}),        
        'contract_line_ids':fields.one2many('purchase.contract.line', 'contract_id' , 'Products',states={'confirmed':[('readonly',True)],'done':[('readonly',True)]}),
        'payment_term': fields.many2one('account.payment.term', 'Payment Term', readonly=True, states={'draft':[('readonly',False)]}),
        'incoterm': fields.many2one('stock.incoterms', 'Incoterm', help="Incoterm which stands for 'International Commercial terms' implies its a series of terms which are used in the commercial transaction.", readonly=True, states={'draft':[('readonly',False)]}),
        'other_conditions': fields.text('other conditions', readonly=True, states={'draft':[('readonly',False)]}),
        'items_types': fields.selection([('products', 'Products'),('service', 'Service'),('both', 'products and service'),
        ], 'Items types', help="the type of the contracts items", readonly=True, states={'draft':[('readonly',False)]}),
        'state': fields.selection(STATE_SELECTION, 'State', readonly=True, help="The state of the contract.", select=True),
        'notes': fields.text('Notes',states={'confirmed':[('readonly',True)],'done':[('readonly',True)],'cancel':[('readonly',True)]}),
        'invoice_ids':fields.one2many('account.invoice', 'contract_id' , 'Invoices', readonly=True),
        'contract_with': fields.selection([('internal', 'Local Supplier'),('foreign', 'Foreign Supplier')], 'Contract With', readonly=True, states={'draft':[('readonly',False)]}),
        'service_type': fields.selection([('urgent','Urgent'),('periodic','Periodic')], 'Service Type', select=True, readonly=True, states={'draft':[('readonly',False)]}),
        'first_party_duties': fields.text('Notes', readonly=True, states={'draft':[('readonly',False)]}),
        'second_party_duties': fields.text('Notes', readonly=True, states={'draft':[('readonly',False)]}),
        'first_party_conditions': fields.text('Notes', readonly=True, states={'draft':[('readonly',False)]}),
        'second_party_conditions': fields.text('Notes', readonly=True, states={'draft':[('readonly',False)]}),
        'first_party_name': fields.char('First Party Name', size=64, required=True, readonly=True, states={'draft':[('readonly',False)]}), 
        'second_party_name': fields.char('Second Party Name', size=64, required=True, readonly=True, states={'draft':[('readonly',False)]}), 
 	    'user':  fields.many2one('res.users', 'Responsible',readonly=True,),
        'shipment_complete': fields.boolean('Shipment Complete', help="If this field is true no more shipment,the state well be done ."),
	    'department_id':fields.many2one('hr.department', 'Department', readonly=True, states={'draft':[('readonly',False)]}),
        'payment_method': fields.selection(PYMENT, 'Payment Method', select=True, readonly=True, states={'draft':[('readonly',False)]}), 
        'contract_shipment_ids':fields.one2many('contract.shipment', 'contract_id' , 'Shipment', readonly=True, states={'draft':[('readonly',False)],'confirmed':[('readonly',False)]},),
        'shipment_total_amount': fields.function(_shipment_total_amount, method=True, string='Shipment Total Amount',digits=(16,2),      store = {
                'purchase.contract': (lambda self, cr, uid, ids, c={}: ids, ['contract_shipment_ids'], 10),
                'purchase.contract.line': (_get_shipment_ids, ['total_amount'], 10),
            },
            help="The total amount of shipment."),
        'fees_total_amount': fields.function(_fees_total_amount, method=True, digits=(16,2), string='Fees Total Amount',
            store = {
                'purchase.contract': (lambda self, cr, uid, ids, c={}: ids, ['contract_fees_ids'], 10),
                'purchase.contract.line': (_get_fees_ids, ['fees_amount'], 10),
            },
            help="The total amount of fees."),
        'contract_fees_ids':fields.one2many('contract.fees', 'contract_id' , 'Fees',  states={'done':[('readonly',True)],'cancel':[('readonly',True)]}), 
        'company_id': fields.many2one('res.company','Company',required=True,select=1, readonly=True,), 
        'contract_account': fields.many2one('account.account', 'Contract Account',required=True, readonly=True, states={'draft':[('readonly',False)]}), 
        'journal_id': fields.many2one('account.journal','Contract Journal', readonly=True, states={'draft':[('readonly',False)]}),
        'freight': fields.float('Freight', digits=(16, 2), readonly=True, states={'draft':[('readonly',False)]}),
        'packing': fields.float('Packing', digits=(16, 2), readonly=True, states={'draft':[('readonly',False)]}),
        'voucher_ids':fields.one2many('account.voucher', 'contract_id' , 'Voucher' , readonly=True),
        'contract_purpose': fields.selection([('purchase','Purchase'),('other','Other')],'Purpose', select=True, readonly=True, states={'draft':[('readonly',False)]}),           
        'amount_untaxed': fields.function(_amount_all, method=True, digits=(16,2), string='Untaxed Amount',
            store = {
                'purchase.contract': (lambda self, cr, uid, ids, c={}: ids, ['contract_line_ids'], 10),
                'purchase.contract.line': (_get_order, ['price_unit', 'tax_id','contract_line_ids','price_subtotal'], 10),
            },
            readonly=True, multi='sums', help="The amount without tax."),
        'amount_tax': fields.function(_amount_all, method=True, digits=(16,2), string='Taxes',
            store = {
                'purchase.contract': (lambda self, cr, uid, ids, c={}: ids, ['contract_line_ids'], 10),
                'purchase.contract.line': (_get_order, ['price_unit', 'tax_id','price_subtotal'], 10),
            },
            multi='sums1', help="The tax amount."),
        'amount_total': fields.function(_amount_all, method=True, digits=(16,2), string='Total',
            store = {
                'purchase.contract': (lambda self, cr, uid, ids, c={}: ids, ['contract_line_ids'], 10),
                'purchase.contract.line': (_get_order, ['price_unit', 'tax_id','price_subtotal'], 10),
            },
            multi='sums2'),
                } 

    def _get_journal(self, cr, uid, ids):
        ''' Get default journal from the company
            return the journal id if exist'''
        company_id = self.pool.get('res.users').browse(cr, uid, uid).company_id.id
        company_rec = self.pool.get('res.company').browse(cr, uid, company_id)
        journal_id = company_rec.purchase_foreign_journal and company_rec.purchase_foreign_journal.id or False
        return journal_id

    _defaults = {
        'name': lambda self, cr, uid, context: '/',
        'contract_date': lambda *a: time.strftime('%Y-%m-%d'),
        'state': 'draft',
        'user': lambda self, cr, uid, context: uid,
        'contract_type':'open',
        'shipment_complete': False,
        'company_id': lambda self,cr,uid,c: self.pool.get('res.company')._company_default_get(cr, uid, 'purchase.contract', context=c),
        'freight': 0.0,
        'packing': 0.0,
        'contract_purpose':'purchase',
        'journal_id':_get_journal
        }

    _sql_constraints = [('Date check',"CHECK (end_date>=start_date)",_("Start date must be prior to end date!")),
                        ('contract_amount_positive',"CHECK (contract_amount>=0)",_("Contract amount cannot be negative")),
                        #('contract_amount_bigger_total_shipment',"CHECK (contract_amount>=shipment_total_amount)",_("Contract amount must be bigger than or equal Shipment total amount")),
                        ('contract_amount_bigger_total_fees',"CHECK (contract_amount>=fees_total_amount)",_("Contract amount must be bigger than or equal Fees total amount"))]

    def copy(self, cr, uid, ids, default={}, context=None):
        """
        Override copy function to edit default value.

        @param default : default vals dict 
        @return: super copy method  
        """
        seq_obj = self.pool.get('ir.sequence')
        default.update({
            'state':'draft',
            'name': seq_obj.get(cr, uid, 'purchase.contract'),
            'contract_date':time.strftime('%Y-%m-%d'),
            'contract_line_ids':[],
        })
        return super(purchase_contract, self).copy(cr, uid, ids, default, context)
    
    def partner_id_change(self, cr, uid, ids,partner):
        """
        On change partner function to read pricelist.

        @param partner : partner id 
        @return: Dictionary of pricelist_id or Empty dictionary 
        """
        if partner:
            partner_id = self.pool.get('res.partner').search(cr, uid, [('id', '=', partner)])
            return {'value': {'second_party_name' : self.pool.get('res.partner').browse(cr, uid,partner).name, 'pricelist_id':self.pool.get('res.partner').browse(cr, uid,partner).property_product_pricelist_purchase.id }}
        return {}

    def button_dummy(self, cr, uid, ids, context=None):
        """ 
        Dummy function to recomputes the functional fieds. 

        @return: True
        """
        self._amount_all(cr,uid,ids,['amount_untaxed'], context)
        return True


    def confirmed(self,cr,uid,ids,*args):
        """
        Workflow function to change state of purchase contract to confirmed
        Call calculate_freight_packing method to calculate and write freight 
        and packing amount for every product price.. 

        @return: True
        """
        
        for contract in self.browse(cr, uid, ids):
            if contract.contract_amount <= 0: 
                    raise osv.except_osv(_('No Amount  !'), _('Please Enter The Amount of This Contract ..'))
            if contract.contract_type in ['detail']:
                amount = contract.amount_total -(contract.freight or 0.0) - (contract.freight or 0.0)                
                contract.calculate_freight_packing(contract,contract.freight,contract.packing,amount)
                if not contract.contract_line_ids: 
                    raise osv.except_osv(_('No Products  !'), _('Please fill the products list first ..'))
            self.write(cr, uid, ids, {'state':'confirmed'})
                
        return True
 
    def done(self,cr,uid,ids,*args):
        """
        Workflow function to change state of purchase contract to done. 

        @return: True
        """
        for record in self.browse(cr,uid,ids) :
            if record.contract_shipment_ids:
               for shipment in record.contract_shipment_ids:
                    if shipment.state not in ['cancel','done'] :
                       raise osv.except_osv(('Sorry !'), ('You Can not cancel this contract because it has shipment(s) in confirm or draft state ..'))
            if record.contract_fees_ids:
               for fee in record.contract_fees_ids:
                    if fee.state not in ['cancel','done']:
                       raise osv.except_osv(('Sorry !'), ('You Can not cancel this contract because it has fee(s) in confirm or draft state ..'))
        self.write(cr, uid, ids, {'state':'done'})
        return True

    def cancel(self,cr,uid,ids,notes=''):
        """
        Workflow function to change state of purchase contract to cancel. 

        @return: True
        """

        for record in self.browse(cr,uid,ids) :
          for shipment in record.contract_shipment_ids:
            if shipment.state in ['confirmed','done'] :
               raise osv.except_osv(('Sorry !'), ('You Can not cancel this contract because it has shipment(s) in confirm or done state ..'))
        
        for record in self.browse(cr,uid,ids) :
          for fee in record.contract_fees_ids:
            if fee.state in ['confirm','done'] :  
               raise osv.except_osv(('Sorry !'), ('You Can not cancel this contract because it has fee(s) in confirm or done state ..'))
        notes = ""
        u = self.pool.get('res.users').browse(cr, uid,uid).name
        notes = notes +'\n'+'purchase Contract Cancelled at : '+time.strftime('%Y-%m-%d') + ' by '+ u
        self.write(cr, uid, ids, {'state':'cancel','notes':notes})
        return True

    def action_cancel_draft(self, cr, uid, ids, *args):
        """ 
        Change contract state to Draft and reset the workflow.

        @return: True 
        """
        if not len(ids):
            return False
        wf_service = netsvc.LocalService("workflow")
        for s_id in ids:
            self.write(cr, uid, s_id, {'state':'draft'})
            wf_service.trg_delete(uid, 'purchase.contract', s_id, cr)            
            wf_service.trg_create(uid, 'purchase.contract', s_id, cr)
        return True
    
    def onchang_duration(self, cr, uid, ids, start_date, duration, context={}):
        """
        On change duration function to calculate end date of the contact.

        @param start_date: start date of the contract
        @param duration: contract duration
        @return: Dictionary of end_date valus
        """
        if not start_date:
            return{}
        if duration < 0 :
            raise osv.except_osv(('Wrong Value!'), ('Duration value can not be negative ..'))
        dif = datetime.timedelta(days=duration)
        statr = datetime.datetime.strptime(start_date,"%Y-%m-%d")
        end_date = statr + dif
        end_date = end_date.strftime('%Y-%m-%d')
        return {'value': {'end_date': end_date}}
    
    def onchang_end_date(self, cr, uid, ids, start_date, end_date, context={}):
        """
        On change end_date function to calculate the duration of the contact.

        @param start_date: start date of the contract
        @param end_date: end date of the contract
        @return: Dictionary of duration valus 
        """
        if not start_date:
            return{}
        from_dt = datetime.datetime.strptime(start_date, "%Y-%m-%d")
        to_dt = datetime.datetime.strptime(end_date, "%Y-%m-%d")
        timedelta = to_dt - from_dt        
        timedelta = timedelta.days
        if timedelta < 0 :
            raise osv.except_osv(('Wrong Value!'), ('This date is smaller than the starting date ..'))           
        return {'value': {'contract_duration': timedelta}}
    
    def prepare_purchase_order(self, cr, uid, ids, contract_object, partner, partner_addres, pricelist, contract_id, date, department, contract_with, currency, item_type='items'): 
        """
        To prepare the valus of purchase order field befor creation.

        @param contract_object: purchase contract object
        @param partner: partner id 
        @param partner_addres: partner address
        @param pricelist: pricelist id
        @param contract_id: contract id
        @param date: expeted date
        @param department: department id
        @param contract_with: supplier type
        @param currency: currency id
        @param item_type: products type items or service     
        @return: Dictionary of valus 
        """    
        dif = datetime.timedelta(days=contract_object.delivery_period)
        current_date = datetime.date.today()
        edate = current_date + dif
        invoice = 'manual'
        #if item_type == 'service': invoice = 'manual'


        result={                    'partner_id': partner, 
                                    'partner_address_id': partner_addres, 
                                    'pricelist_id': pricelist, 
                                    'state': 'draft', 
                                    'origin':contract_object.name, 
                                    'contract_id': contract_id, 
                                    'ir_date': date, 
                                    'department_id': department, 
                                    'delivery_period': contract_object.delivery_period,
                                    'delivery_method': contract_object.delivery_method, 
                                    'purchase_type': contract_with,
                                    'invoice_method':invoice,
                                    'e_date': edate,
                                    'currency_id': currency,
                                    'freight': contract_object.freight,
                                    'packing': contract_object.packing,
                                    'purpose':'store',
                                    }
        return result
    
    def prepare_purchase_order_lines(self, cr, uid, ids,contract_line_obj,order_id):
        """
        To prepare the valus of purchase order lines field befor creation.

        @param contract_line_obj: purchase contract line object
        @param order_id: purchase order id      
        @return: Dictionary of valus 
        """  

        product_obj = self.pool.get('product.product') 
        total = contract_line_obj.price_unit
        if contract_line_obj.price_unit_freight: 
            total += contract_line_obj.price_unit_freight
        if contract_line_obj.price_unit_packing: total += contract_line_obj.price_unit_packing
        p_uom = product_obj.browse(cr, uid, contract_line_obj.product_id.id).uom_po_id.id
        result={'name': contract_line_obj.product_id.name, 
                                 'product_id': contract_line_obj.product_id.id, 
                                 'product_qty': contract_line_obj.product_qty, 
                                 'date_planned':time.strftime('%Y-%m-%d'), 
                                 'product_uom':p_uom, 
                                 'price_unit':contract_line_obj.price_unit, 
                                 'order_id':order_id, 
                                 'notes': contract_line_obj.notes, 
                                 'price_unit_total':total,
                                 'price_unit_freight': contract_line_obj.price_unit_freight,
                                 'price_unit_packing': contract_line_obj.price_unit_packing, 
                                 }
        return result
    
    def make_purchase_order(self, cr, uid, ids, context=None): 
        """
        To create purchase order from selected and approved contract 
        and call create_letter_of_credit if required by invoice method.

        @return: creates purchase order id 
        """   
        purchase_obj = self.pool.get('purchase.order')
        purchase_line_obj = self.pool.get('purchase.order.line')
        partner_obj = self.pool.get('res.partner') 
        purchase_order={} 
        purchase_order_line={}          
        for purchase_contract in self.browse(cr, uid, ids):   
                    part_addr = partner_obj.address_get(cr, uid, [purchase_contract.partner_id.id], ['default'])['default']
                    pricelist=purchase_contract.partner_id.property_product_pricelist_purchase.id
                    date=purchase_contract.contract_date
                    department = purchase_contract.department_id.id
                    currency =purchase_contract.currency_id.id
                    partner = purchase_contract.partner_id.id
                    contract_with = purchase_contract.contract_with
                    items_type='items'
                    if purchase_contract.items_types=='service':items_type='service'
                    purchase_order=purchase_contract.prepare_purchase_order(purchase_contract, partner, part_addr, pricelist, purchase_contract.id, date, department, contract_with, currency,items_type )
                    or_id = purchase_obj.create(cr, uid, purchase_order)		                            
                    for product in purchase_contract.contract_line_ids:
                            purchase_order_line=purchase_contract.prepare_purchase_order_lines(product, or_id)
                            purchase_line_obj.create(cr, uid, purchase_order_line)
                    if purchase_contract.payment_method == 'lc':
                        self.create_letter_of_credit(cr, uid, ids, purchase_contract, or_id)
        return or_id
    
    def create_letter_of_credit(self, cr, uid, ids, purchase_contract,order_id):
        """
        To create letter of credit from selected and approved contract.

        @return: creates letter of credit id 
        """
        product_obj = self.pool.get('product.product')            
        letter_of_credit_obj = self.pool.get('purchase.letter.of.credit')
        letter_of_credit_line_obj = self.pool.get('purchase.letter.of.credit.line')  
        letter_of_credit_id = letter_of_credit_obj.create(cr, uid, {
            'amount':purchase_contract.amount_total,
            'partner_id':purchase_contract.partner_id.id, 
            'payment_term':purchase_contract.payment_term.id, 
            'source_number':purchase_contract.name, 
            'source_date':purchase_contract.contract_date, 
            'currency_id':purchase_contract.currency_id.id,
            'purchase_order_ref': order_id,
            'delivery_date': purchase_contract.delivery_date,
                                    })
        for products in purchase_contract.contract_line_ids:
            p_uom = product_obj.browse(cr, uid, products.product_id.id).uom_po_id.id
            letter_of_credit_line_obj.create(cr, uid, {
                'name': products.product_id.name, 
                'product_id': products.product_id.id, 
                'product_qty': products.product_qty, 
                'product_uom':p_uom,
                'price_subtotal':products.price_subtotal, 
                'price_unit':products.price_unit,
                'tax_id':products.tax_id,
                'product_packaging':products.product_packaging, 
                'letter_of_credit_line_ids': letter_of_credit_id,
                'notes': products.notes, 
                                 })        
        return letter_of_credit_id 
    
    def create_shipment(self, cr, uid, ids, context=None):
        """
        To create contract shipment called by button.

        @return: creates shipment id 
        """  
        shipment_obj = self.pool.get('contract.shipment')
        for contract in self.browse(cr, uid, ids): 
            shipment_id = shipment_obj.create(cr, uid,{'contract_id':contract.id,})
            return shipment_id

    def create_fees(self,cr,uid,ids,context={}):
        """
        To create contract fees called by button.

        @return: creates fees id 
        """ 
        fees_obj = self.pool.get('contract.fees')
        for contract in self.browse(cr,uid,ids):
            fees_id = fees_obj.create(cr,uid,{'contract_id' : contract.id,'purpose': contract.contract_purpose}) 
        return fees_id
        
    def calculate_freight_packing(self, cr, uid, ids, contract_obj, freight, packing,total):
        """
        To calculate and allocate the freight and packing value for every product.

        @return: True 
        """
        fright_unit = 0.0
        packing_unit = 0.0
        for line in contract_obj.contract_line_ids:
            fright_unit = (line.price_unit/total)* freight
            packing_unit = (line.price_unit/total) * packing
            line.write({'price_unit_freight':fright_unit,'price_unit_packing':packing_unit})
        return True
    


class purchase_contract_line(osv.osv):
    """
    To manage contract products if type is detail"""       

    def _amount_line(self, cr, uid, ids, field_name, arg, context=None):
        '''
        Functional filed function to compute product total price amount.

        @return: dictionary which contains the subtotal for each line
        '''       
        res = {}
        for line in self.browse(cr, uid, ids):
            res[line.id] = line.price_unit * line.product_qty
        return res

    def create(self, cr, uid, vals, context=None):
        """ 
        Override update price and quantity of contract products. 

        @return: created line id 
        """
        c_id=super(purchase_contract_line, self).create(cr, uid, vals, context)       
        if ('price_unit' in vals and 'product_qty' in vals ) :  
            cr.execute('''update purchase_contract_line set  price_subtotal =%s WHERE id=%s''',(vals['price_unit']* vals['product_qty'],c_id))
        return  c_id 

    def subtotal(self, cr, uid, ids, price, qty):
        """ 
        On change function to recompute the total price after changing product qty or product unit

	    @param price: price of the product.
        @param qty: quantity of the product.	
        @return: price_subtotal.
        """
        res = {}
        for product in self.browse(cr,uid,ids):
            if product.product_id.uom_id.id != product.product_uom.id :
               raise osv.except_osv(_('Error !'), _(' Please Select the Correct Unit of Measure for this Product '))
        if price or qty:
            res = {}
            res = {'value': {'price_subtotal': price * qty, }}
        return res 
      
    _name = 'purchase.contract.line'
    _description = "Purchase Contract line"
    _columns = {
        'name': fields.char('Reference', size=256, required=True),
        'vocab' : fields.char('Vocab' , size=64 ),
        'part_code' : fields.char('Part Code', size=64),
        'product_qty': fields.float('Quantity', required=True, digits=(16,2)),
        'product_uom': fields.many2one('product.uom', 'Product UOM', required=True),
        'product_id': fields.many2one('product.product', 'Product'),
        'price_unit': fields.float('Unit Price', required=True, digits=(16, 2)),
        'price_subtotal': fields.function(_amount_line, method=True, string='Subtotal',store=True ,),
        'contract_id': fields.many2one('purchase.contract', 'Contract',),
        'tax_id': fields.many2many('account.tax', 'contract_tax', 'purchase_contract_line_id', 'tax_id', 'Taxes'),
        'product_packaging': fields.many2one('product.packaging', 'Packaging', help="Control the packages of the products"),
        'notes': fields.text('Notes'),  
        'all_quantity_purchased': fields.boolean('All Quantity Purchased',),
        'purchased_quantity': fields.float('Purchased Quantity',digits=(16,4)),  
        'price_unit_freight': fields.float('Freight',digits=(16,4)),
        'price_unit_packing': fields.float('Packing',digits=(16, 2)),    
        }
    _defaults = {
        'purchased_quantity': 0.0,
        'all_quantity_purchased': False,
                 }
    _sql_constraints = [
        ('produc_uniq', 'unique(contract_id,product_id)', 'Sorry You Entered Product Two Time You are not Allow to do this.... So We going to delete The Duplicts!'),
            ]
    
    def product_id_change(self, cr, uid, ids,product):
        """
        On change product function to read the default name and UOM of the product.

        @param product: product_id 
        @return: dictionary of product name,uom,vocab and part code or Empty dictionary
        """
        if product:
            prod= self.pool.get('product.product').browse(cr, uid,product)
            return {'value': { 'name':prod.name,
                    'product_uom':prod.uom_po_id.id,
                    'vocab' : prod.code,
                    'part_code' : prod.ean13}}
        return {}
    


class contract_shipment(osv.osv):
    """
    To manage contract shipment """

    def _amount_all(self, cr, uid, ids, field_name, arg, context=None):
        """
        Functional field function to calculate the total amount of shipment

        @return: Dictionary of amount total valus 
        """
        res = {}
    
        for shipment in self.browse(cr, uid, ids, context=context):
            amount = 0.0
            for line in shipment.contract_shipment_line_ids:
                amount = amount + line.price_subtotal 
            if shipment.freight: amount += shipment.freight
            if shipment.packing: amount += shipment.packing
            res[shipment.id]= amount
        return res

    def create(self, cr, user, vals, context=None):
        """ 
        Override to edit the name field by a new sequence. 

        @return: super create method 
        """
        if ('name' not in vals) or (vals.get('name')=='/'):  
            vals['name'] = self.pool.get('ir.sequence').get(cr, user, 'contract.shipment')

        shipment_id = super(contract_shipment, self).create(cr, user, vals, context)
        contract_id = self.pool.get('purchase.contract').search(cr, user, [('contract_shipment_ids','=',shipment_id)])
        type =''
        for contract in self.pool.get('purchase.contract').browse(cr, user, contract_id):
            type = contract.contract_with
            self.write(cr, user, shipment_id,{'contract_with': type})
        return shipment_id


    def unlink(self, cr, uid, ids, context=None):
        """ 
        Ovrride to add constrain on deleting the Shipment. 

        @return: super unlink() method
        """
        if context is None:
            context = {}
        if [shipment for shipment in self.browse(cr, uid, ids, context=context) if shipment.state not in ['draft']]:
            raise osv.except_osv(_('Invalid action !'), _('You cannot remove shipment not in draft state !'))
        return super(contract_shipment, self).unlink(cr, uid, ids, context=context) 



    def _check_negative(self, cr, uid, ids, context=None):
        """ 
        Constrain function to check the quantity and price and frieght and packing should be greater than 0
        @return Boolean True or False
        """
        record = self.browse(cr, uid, ids[0], context=context)
        if record.freight < 0 :
           raise osv.except_osv(_('Error !'), _('Freight must be Positive'))
        if record.packing < 0:
           raise osv.except_osv(_('Error !'), _('Packing must be Positive'))

        return True 


    def change_product_type(self , cr , uid , ids , product_type , context=None):
        """  On_Change Function to prevent conflicting between product type in the shipment and type of the product """
        for record in self.browse(cr, uid, ids , context=context):
            for product in record.contract_shipment_line_ids :
                if record.contract_shipment_line_ids :
                    pct_type = product.product_id.type
                    if ( product_type == 'service' and pct_type != 'service' ) or ( product_type != 'service' and pct_type == 'service' ):
                        raise osv.except_osv(_('Conflicting Data  !'), _('Your items or Some of them and the Products Type is not match.'))
        return True 



    def _check_product_type(self,cr,uid,ids,context=None):
        """ Constrain function to check the products type
        @return Boolean True or False
        """
        record = self.browse(cr, uid, ids[0], context=context)
        for product in record.contract_shipment_line_ids :
            if record.contract_shipment_line_ids :
               product_type = product.product_id.type
               if (record.product_type == 'service' and product_type != 'service' ) or (record.product_type != 'service' and product_type == 'service' ):
                  raise osv.except_osv(_('Conflicting Data  !'), _('Your items or Some of them and the Products Type is not match ... '))
                  
        return True
    

    _name = 'contract.shipment'
    _description = "Contract Shipment"
    
    STATE_SELECTION = [
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('done', 'Done'),
        ('cancel', 'Cancel'),
    ]
    PRODUCTS_TYPE = [
        ('service', 'Service'),
        ('items', 'Items'),
    ]

    _columns = { 
        'name': fields.char('Reference', size=256, required=True),
        'bill_of_lading':fields.char('Bill of Lading NO', size=64),
        'final_invoice_no':fields.char('Final Invoice No',size=64),
        'delivery_date':fields.date('Delivery Date'),
        'final_invoice_date':fields.date('Final Invoice Date'),
        'delivery_method': fields.selection([('air_freight', 'Air Freight'),('sea_freight', 'Sea Freight'),('free_zone','Free Zone')], 'Method of dispatch', select=True),
        'delivery_period': fields.integer('Delivery period', help="set the delivery period by days",states={'done':[('readonly',True)]}),
        'contract_id': fields.many2one('purchase.contract', 'Contract',),
        'contract_shipment_line_ids':fields.one2many('contract.shipment.line', 'contract_shipment_id' , 'Products',),
        'total_amount': fields.function(_amount_all, method=True, string='Total Amount',type='float',digits=(16,2),store=True ),
        'state': fields.selection(STATE_SELECTION, 'State', readonly=True, help="The state of the contract.", select=True),
        'freight': fields.float('Freight', digits=(16, 2)),
        'packing': fields.float('Packing', digits=(16, 2)),
        'picking_policy': fields.selection([('partial', 'Partial Delivery'), ('complete', 'Complete Delivery')],
            'Picking Policy', required=True, help="""deliver all at once as (complete), or partial shipments""",),

        'contract_with': fields.selection([('internal', 'Local Supplier'),('foreign', 'Foreign Supplier')], 'Contract With',), 
        'purchase_id' : fields.many2one('purchase.order' , 'Reference'),
        'product_type':fields.selection(PRODUCTS_TYPE, 'Product Type', select=True),
        'notes': fields.text('Notes',states={'confirmed':[('readonly',True)],'done':[('readonly',True)],'cancel':[('readonly',True)]}),                      
                } 
    _defaults = {  
        'picking_policy':'partial',
        'state': lambda *a: 'draft',
        'freight': 0.0,
        'packing': 0.0,
       }

    _constraints = [

            (_check_product_type, 'Your items or Some of them and the Products Type is not match ... ',['product_type']),
            (_check_negative, 'One of this Fields[ Quantity ,Product UOM , Freight and Packing ] is less than one ... ',['product_qty']),
          ]

   
    
    
    def button_dummy(self, cr, uid, ids, context={}):
        """ 
        Dummy function to recomputes the functional felids and force 
        calculation of freight and packing of each product. 

        @return: True
        """
        total = 0.0

        for shippment in self.browse(cr, uid, ids):
            for product in shippment.contract_shipment_line_ids:
                total = total +  (product.product_qty * product.price_unit)

            if shippment.freight : 
               total = total + shippment.freight
            if shippment.packing : 
               total = total + shippment.packing

            self.write(cr, uid, ids, {'total_amount': 0.0 })
        return True
    
    def check_amount(self, cr, uid, ids , shipment_object):
        """ 
        To add shipment value to total shipment amount, prohibit 
        shipment amount from exceeding the contract amount and 
        change the value of shipment_complete flag.
       
        @return: True
        """

        contract_obj = self.pool.get('purchase.contract')
        contract = shipment_object.contract_id
        for record in self.browse(cr, uid, ids):
            sum=0.0
            for shipment_id in contract.contract_shipment_ids:
                if shipment_id.state not in ['cancel']:
                    sum += shipment_id.total_amount
                    #if sum > contract.contract_amount:
                        #raise osv.except_osv(_('Wrong value!'), _("The amount of shipments '%s' well be more than contract amount.."))
                    #else:
                    contract.write({'shipment_total_amount':sum})  
                    #if sum == contract.contract_amount:
                    #contract.write({'shipment_complete':True})    
        return True
    
    def confirmed(self, cr, uid, ids, context={}):
        """ 
        Workflow function to change the shipment state to confirm and 
        check shipment products data that was required.
       
        @return: True
        """
        for shipment in self.browse(cr, uid, ids):
            if shipment.contract_id.state in ['draft' , 'cancel' ]:
               raise osv.except_osv(_('Sorry ...'), _('You can not confirm this shipment and the contract in draft or cancel state ..'))                
            if shipment.contract_shipment_line_ids:
               #TODO: add dumy button to calculate 
               amount = shipment.total_amount - (shipment.freight or 0.0) - (shipment.packing or 0.0) 
               shipment.calculate_freight_packing(shipment,shipment.freight,shipment.packing, amount)
               if not shipment.total_amount:
                    raise osv.except_osv(_('Missing Data  !'), _("Please press compute first.."))
               else:
                    shipment.check_amount(shipment)
               self.write(cr, uid, ids, {'state':'confirmed'})
            else:
                raise osv.except_osv(_('No Products  !'), _('Please fill the products list first ..'))                
        return True
    
    def cancel(self,cr,uid,ids,notes=''):
        """ 
        Workflow function changes shipment state to cancell and writes note
	    which contains Date and username who do cancellation.

	    @param notes: contains information of who & when cancelling order.
        @return: Boolean True
        """
        notes = ""
        user = self.pool.get('res.users').browse(cr, uid,uid).name
        notes = notes +'\n'+'purchase Contract Cancelled at : '+time.strftime('%Y-%m-%d') + ' by '+ user
        self.write(cr, uid, ids, {'state':'cancel','notes':notes})
        for shipment in self.browse(cr, uid, ids):
            contract = shipment.contract_id
            total_amount = contract.shipment_total_amount
            new_amount = total_amount - shipment.total_amount
            contract.write({'shipment_total_amount': new_amount})
        return True 
    
    def action_cancel_draft(self, cr, uid, ids, *args):
        """ 
        Changes shipment state to Draft and reset the workflow.

        @return: True 
        """
        if not len(ids):
            return False
        wf_service = netsvc.LocalService("workflow")
        for s_id in ids:
            self.write(cr, uid, s_id, {'state':'draft'})
            wf_service.trg_delete(uid, 'contract.shipment', s_id, cr)            
            wf_service.trg_create(uid, 'contract.shipment', s_id, cr)
        return True  
    
    def done(self, cr, uid, ids):
        """ 
        Workflow function to creating purchase order from the shipment 
        and changes shipment state to done.

        @return: purchase order id 
        """
        purchase_obj = self.pool.get('purchase.order')
        purchase_line_obj = self.pool.get('purchase.order.line')
        partner_obj = self.pool.get('res.partner') 
        purchase_order={} 
        purchase_order_line={}          
        for shipment in self.browse(cr, uid, ids): 
                    purchase_contract = shipment.contract_id           
                    part_addr = partner_obj.address_get(cr, uid, [purchase_contract.partner_id.id], ['default'])['default']
                    pricelist=purchase_contract.partner_id.property_product_pricelist_purchase.id
                    date=purchase_contract.contract_date
                    department = purchase_contract.department_id.id
                    currency =purchase_contract.currency_id.id
                    partner = purchase_contract.partner_id.id
                    contract_with = purchase_contract.contract_with
                    purchase_order=purchase_contract.prepare_purchase_order(shipment, partner, part_addr, pricelist, purchase_contract.id, date, department, contract_with, currency,shipment.product_type )
                    or_id = purchase_obj.create(cr, uid, purchase_order) 
                    for product in shipment.contract_shipment_line_ids:
                            purchase_order_line=purchase_contract.prepare_purchase_order_lines(product, or_id)
                            purchase_line_obj.create(cr, uid, purchase_order_line)
                    
        self.write(cr, uid, ids, {'state':'done' , 'purchase_id' : or_id})
        if purchase_contract.shipment_complete:
            purchase_contract.write({'state':'done'})
        return or_id  

    def calculate_freight_packing(self, cr, uid, ids, contract_obj, freight, packing,total):
        """
        To calculate and allocate the freight and packing value for every product.

        @return: True 
        """
        fright_unit = 0.0
        packing_unit = 0.0
        for line in contract_obj.contract_shipment_line_ids:
            fright_unit = (line.price_unit /total) * freight
            packing_unit = (line.price_unit /total) * packing
            line.write({'price_unit_freight':fright_unit,'price_unit_packing':packing_unit})
        return True
    

 
class contract_shipment_line(osv.osv):
    """
    To manage contract shipment products """
    def _amount_line(self, cr, uid, ids, prop, unknow_none, unknow_dict):
        """
        To compute the total price amount of shipment line.

        @return returns res which is contains the subtotal for each line
        """       
        res = {}
        for line in self.browse(cr, uid, ids):
            res[line.id] = line.price_unit * line.product_qty
        return res

    def subtotal(self, cr, uid, ids, product, price=0, qty=0):
        """ 
        On change function to recompute the total price after changing product qty or product unit

	    @param price: price of the product.
        @param qty: quantity of the product.
        @para product uom : product unit of measure	
        @return: price_subtotal.
        """  
        res = {}
        prod= self.pool.get('product.product').browse(cr, uid,product)
        for product in self.browse(cr,uid,ids):
            if product.product_id.uom_id.id != product.product_uom.id :
               raise osv.except_osv(_('Error !'), _(' Please Select the Correct Unit of Measure for this Product '))
        if price or qty:
            res = {'value': {'price_subtotal': price * qty, }}
        return res 
       
    def _check_negative(self, cr, uid, ids, context=None):

        """ 
        Constrain function to check the quantity and price and frieght and packing should be greater than 0
        @return Boolean True or False
        """
        record = self.browse(cr, uid, ids[0], context=context)
        if record.product_qty <= 0 :
           raise osv.except_osv(_('Error !'), _('Product Quantity must be greater than zero'))
        if record.price_unit <= 0 :
           raise osv.except_osv(_('Error !'), _('Price Unit must be greater than zero'))
        if record.price_unit_freight < 0 :
           raise osv.except_osv(_('Error !'), _('Price Unit Freight must be Positive'))
        if record.price_unit_packing < 0:
           raise osv.except_osv(_('Error !'), _('Price Unit Packing must be Positive'))

        return True 

    _name = 'contract.shipment.line'
    _description = "Contract Shipment Line"
    _columns = {
        'name': fields.char('Reference', size=256, required=True),
        'vocab' : fields.char('Vocab' , size=64 ),
        'part_code' : fields.char('Part Code', size=64),
        'product_qty': fields.float('Quantity', required=True, digits=(16,2)),
        'product_uom': fields.many2one('product.uom', 'Product UOM', required=True),
        'product_id': fields.many2one('product.product', 'Product'),
        'price_unit': fields.float('Unit Price', required=True, digits=(16, 2)),
        'price_subtotal': fields.function(_amount_line, method=True, string='Subtotal',),
        'contract_shipment_id': fields.many2one('contract.shipment', 'Contract shipment',),
        'tax_id': fields.many2many('account.tax', 'contract_tax', 'purchase_contract_line_id', 'tax_id', 'Taxes'),
        'product_packaging': fields.many2one('product.packaging', 'Packaging', help="Control the packages of the products"),
        'price_unit_freight': fields.float('Freight',digits=(16,4)),
        'price_unit_packing': fields.float('Packing',digits=(16, 2)),
        'notes': fields.text('Notes',states={'confirmed':[('readonly',True)],'done':[('readonly',True)],'cancel':[('readonly',True)]}),        
        }

    _constraints = [
        (_check_negative, 'One of this Fields[ Quantity ,Product UOM , Freight and Packing ] is less than one ... ',['product_qty']),
      ]

    _sql_constraints = [
        ('product_contract_shipment_uniq','unique(contract_shipment_id,product_id)','Sorry You Entered Product Two Time You are not Allow to do this.'),]

    
    def product_id_change(self, cr, uid, ids,product,product_type):

        """
        On change product function to read the default name and UOM of the product.

        @param product: product_id 
        @return: dictionary of product name,uom,vocab and part code or Empty dictionary
        """
        if product:
            prod= self.pool.get('product.product').browse(cr, uid,product)

            if product_type == 'service' :
               product_list = self.pool.get('product.product').search(cr,uid,[('type','=','service')])
            else :
               product_list = self.pool.get('product.product').search(cr,uid,[('type','!=','service')])

            return {'value': { 'name':prod.name,
                               'product_uom':prod.uom_po_id.id,
                               'vocab' : prod.code,
                               'part_code' : prod.ean13}, 'domain':{'product_id': [('id', 'in' , product_list)] }}
        return {}
           



class contract_fees(osv.osv):
    """ 
    To Manage contract fees """

    def create(self, cr, user, vals, context=None):
        """ 
        Override the create method to add value to the column 
        name by a new sequence. 

        @return: super create method 
        """
        if ('name' not in vals) or (vals.get('name')=='/'):  
            vals['name'] = self.pool.get('ir.sequence').get(cr, user, 'contract.fees')
        return super(contract_fees, self).create(cr, user, vals, context)


    def _check_ammount(self, cr, uid, ids, context=None):
        for fees in self.browse(cr, uid, ids):
            if fees.fees_amount > 0:
                return True
        return False



    def unlink(self, cr, uid, ids, context=None):
        """ 
        Ovrride to add constrain on deleting the Contraint . 

        @return: super unlink() method
        """
        if context is None:
            context = {}
        if [fee for fee in self.browse(cr, uid, ids, context=context) if fee.state not in ['draft']]:
            raise osv.except_osv(_('Invalid action !'), _('You cannot remove Fee not in draft state !'))
        return super(contract_fees, self).unlink(cr, uid, ids, context=context) 



    MONTH = [
        ('jan', 'January'),
        ('feb', 'February'),
        ('mar','March'),
        ('apr','April'),
        ('may','May'),
        ('jun','June'),
        ('jul','July'),
        ('aug','August'),
        ('sep','September'),
        ('oct','October'),
        ('nov','November'),
        ('des','December'),
    ]

    _name = 'contract.fees'

    _description = "Contract Fees"
    _columns = { 
        'name': fields.char('Reference', size=64, required=True, readonly=True, select=True), 
        'fees_date':fields.date('Fees Date'),
        'month': fields.selection(MONTH, 'Month', select=True),   
        'contract_id': fields.many2one('purchase.contract', 'Contract',),
        'fees_amount': fields.float('Fees Amount', digits=(16,2)), 
        'fees_amount_in_euro': fields.float('Fees Amount In Euro', digits=(16,2)),     
        'description': fields.text('Description'),
        'notes': fields.text('Notes',states={'confirmed':[('readonly',True)],'done':[('readonly',True)],'cancel':[('readonly',True)]}),
        'purpose': fields.selection([('purchase','Purchase'),('other','Other')],'Purpose', select=True,),           
        'state' : fields.selection([('draft','Draft'),('confirm','Confirmed'),('done','Done'),('cancel','Canceled')],'State'),               
                }
    _defaults = {
                 'fees_amount': 1.0,
                 'fees_amount_in_euro': 0.0,
                 'state' : 'draft',
                 'purpose':'purchase',
      } 
       
    _constraints = [      
 
        (_check_ammount, 'Error! The fees amount must be positive', ['fees_amount']),]

    def amount_change(self,cr, uid, ids, amount,context={}):
        """
        On change amount function to calaulate fees amount in Euro.
      
        @return: Dictionary of fees amount in Euro
        """
        currency_obj = self.pool.get('res.currency')
        new_amount = 0.0
        for fee in self.browse(cr, uid, ids):
            contract = fee.contract_id
            contract_currency = contract.currency_id.id
            euro_id = currency_obj.search(cr, uid, [('name','=','EUR')],limit=1)
            curren = currency_obj.browse(cr, uid, euro_id)
            new_amount = currency_obj.compute(cr, uid, contract_currency, curren[0].id, amount, fee.fees_date)           
        return {'value': {'fees_amount_in_euro':new_amount }}  
  
    def confirm(self,cr,uid,ids,context={}):
        """
        Workflow function to change the state to confirm.
    
        @return: True
        """
        currency_obj = self.pool.get('res.currency')
        new_amount = 0.0
        for fees in self.browse(cr, uid, ids):

            contract = fees.contract_id
            contract_currency = contract.currency_id.id
            contract_state = contract.state
            if contract_state != "confirmed":
                raise osv.except_osv(_('fess confirmation !!!'), _('you can not confirm this fees until you confirmed the contract ..'))
            euro_id = currency_obj.search(cr, uid, [('name','=','EUR')],limit=1)
            curren = currency_obj.browse(cr, uid, euro_id)
            new_amount = currency_obj.compute(cr, uid, contract_currency, curren[0].id, fees.fees_amount, fees.fees_date) 
            all_amount = contract.fees_total_amount + fees.fees_amount
            if all_amount > contract.contract_amount :
                raise osv.except_osv(_('Amount exceed  !'), _('The total fees amount well be more than the contract amount ..'))
            else:
                contract.write({'fees_total_amount': all_amount})                
        self.write(cr,uid,ids,{'state' : 'confirm','fees_amount_in_euro':new_amount }),
         
        return True


    def create_invoice(self,cr,uid,ids,context={}):
        """
        Workflow function to generates invoice for given ids of purchase 
        contracts Fees and links that invoice ID to the contract and change
        the state to Done.
    
        @return: invoice id
        """
        #Generates invoice for given ids of purchase contracts Fees and links that invoice ID to the contract.

        user_obj = self.pool.get('res.users')
        inv_obj = self.pool.get('account.invoice')
        inv_line_obj = self.pool.get('account.invoice.line')
        for fees in self.browse(cr, uid, ids, context=context):
            contract = fees.contract_id
            pay_acc_id = contract.partner_id.property_account_payable.id
            # generate invoice line correspond to FC line and link that to created invoice (inv_id) 
            company = user_obj.browse(cr,uid,uid).company_id
            contract_account = contract.contract_account
            forgin_purchase_journal = contract.journal_id or company.purchase_foreign_journal
            #addres = self.pool.get('res.partner').search(cr, uid, [('partner_id','=',contract.partner_id.id)])
            #if not addres:
                #raise osv.except_osv(_('No Address !'),_('There No address Defined Fore This partner please fill the address first') )
            if not contract_account:
                raise osv.except_osv(_('Missing Account Number !'),_('There No Account Defined Fore This Contract    please choose the account first') )
            if not forgin_purchase_journal:
                raise osv.except_osv(_('Missing Data!'),_('There No Foreign Purchase Journal, please choose journal first') )
            inv_line_id = inv_line_obj.create(cr, uid,{
			    'name': fees.name,
			    'account_id': contract_account.id,
			    'price_unit': fees.fees_amount,
			    'quantity': 1,}, context=context)
            # get invoice data and create invoice
            inv_data = {
                'name': fees.description,
                'reference': contract.name +'/'+ fees.name ,
                'account_id': pay_acc_id,
                
                'type': 'in_invoice',
                'partner_id': contract.partner_id.id,
                'currency_id': contract.currency_id.id,
                'journal_id': forgin_purchase_journal.id or False,
                'invoice_line': [(6, 0, [inv_line_id])], 
                'origin': contract.name,
                'company_id': contract.company_id.id,
            }
            inv_id = inv_obj.create(cr, uid, inv_data, context=context)
            inv_obj.button_compute(cr, uid, [inv_id], context=context, set_total=True)
            contract.write({'invoice_ids': [(4, inv_id)]}, context=context)
        
        self.write(cr,uid,ids,{'state' : 'done'}),
        return inv_id

    def cancel(self,cr,uid,ids,context={}):
        """
        Workflow function to change the state to cancel.
    
        @return: True
        """
        for fees in self.browse(cr, uid, ids):
            contract = fees.contract_id
            new_amount = contract.fees_total_amount - fees.fees_amount
            contract.write({'fees_total_amount': new_amount})
        self.write(cr,uid,ids,{'state' : 'cancel'})
        return True
    
    def action_cancel_draft(self, cr, uid, ids, *args):
        """ 
        Change contract state to Draft and reset the workflow.

        @return: True 

        """
        if not len(ids):
            return False
        wf_service = netsvc.LocalService("workflow")
        for s_id in ids:
            self.write(cr, uid, s_id, {'state':'draft'})
            wf_service.trg_delete(uid, 'contract.fees', s_id, cr)            
            wf_service.trg_create(uid, 'contract.fees', s_id, cr)
        return True 
    
    def create_voucher(self,cr,uid,ids,context={}):
        """
        Workflow function to generates voucher for given ids of purchase 
        contracts Fees and links that voucher ID to the contract and change
        the state to Done.
    
        @return: voucher id
        """
        user_obj = self.pool.get('res.users')
        voucher_obj = self.pool.get('account.voucher')
        voucher_line_obj = self.pool.get('account.voucher.line')
        for fees in self.browse(cr, uid, ids, context=context):
            contract = fees.contract_id
            voucher_id = voucher_obj.create(cr, uid, {
                                        'amount': fees.fees_amount,
                                        'type': 'purchase',
                                        'contract_id':fees.contract_id.id,
                                        'date': time.strftime('%Y-%m-%d'),
                                        'partner_id': contract.partner_id.id,
                                        'journal_id': contract.journal_id and contract.journal_id.id,
                                        'reference': contract.name+"/"+ fees.name,
                                        'state': 'draft',
                                        'name':'Fees:'+fees.name ,
                                        'currency_id':contract.currency_id.id,
                                        })
            vocher_line_id = voucher_line_obj.create(cr, uid, {
                                        'amount': fees.fees_amount,
                                        'voucher_id': voucher_id,
                                        'type': 'dr',
                                        'account_id': contract.contract_account.id,
                                        'name': fees.description,
                                         })
            contract.write({'voucher_ids': [(4, voucher_id)]}, context=context)
            fees.write({'state':'done'})
        return voucher_id
    
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
