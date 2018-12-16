# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

from odoo import api, fields, models, exceptions,_
#import netsvc
import time
import datetime
from odoo.exceptions import UserError ,ValidationError

import datetime as timedelta
#from base_custom.models import amount_to_text_ar as amount_to_text_ar





class purchase_contract_line(models.Model):
    """
    To manage contract products if type is detail"""

    @api.depends('price_unit', 'product_qty')
    def _amount_line(self):
        '''
        Functional filed function to compute product total price amount.

        @return: dictionary which contains the subtotal for each line
        '''
        res = {}
        for line in self:
            #res[line.id] = line.price_unit * line.product_qty
            self.price_subtotal = line.price_unit * line.product_qty
        #return res

    def create(self, vals):
        """
        Override update price and quantity of contract products.

        @return: created line id
        """
        c_id = super(purchase_contract_line, self).create(vals)
        if ('price_unit' in vals and 'product_qty' in vals):
            self._cr.execute('''update purchase_contract_line set  price_subtotal =%s WHERE id=%s''',
                             (vals['price_unit'] * vals['product_qty'], c_id))
        return c_id

    @api.onchange('price_unit','product_qty')
    def subtotal(self):
        """
        On change function to recompute the total price after changing product qty or product unit

	    @param price: price of the product.
        @param qty: quantity of the product.
        @return: price_subtotal.
        """
        res = {}
        for product in self:
            if product.product_id.uom_id.id != product.product_uom.id:
                raise exceptions.ValidationError(
                    _(' Please Select the Correct Unit of Measure for this Product '))
        if self.product_price or self.product_qty:
            res = {}
            res = {'value': {'price_subtotal': self.product_price * self.product_qty, }}
        return res

    _name = 'purchase.contract.line'
    _description = "Purchase Contract line"

    name = fields.Char('Reference', size=256, required=True)
    vocab = fields.Char('Vocab', size=64)
    part_code = fields.Char('Part Code', size=64)
    product_qty = fields.Float('Quantity', required=True, digits=(16, 2))
    product_uom = fields.Many2one('product.uom', 'Product UOM', required=True)
    product_id = fields.Many2one('product.product', 'Product')
    price_unit = fields.Float('Unit Price', required=True, digits=(16, 2))
    price_subtotal = fields.Float(compute="_amount_line", string='Subtotal', store=True, )
    contract_id = fields.Many2one('purchase.contract', 'Contract', )
    tax_id = fields.Many2many('account.tax', 'contract_tax', 'purchase_contract_line_id', 'tax_id', 'Taxes')
    product_packaging = fields.Many2one('product.packaging', 'Packaging', help="Control the packages of the products")
    notes = fields.Text('Notes')
    all_quantity_purchased = fields.Boolean('All Quantity Purchased', default=False)
    purchased_quantity = fields.Float('Purchased Quantity', digits=(16, 4), default=0.0)
    price_unit_freight = fields.Float('Freight', digits=(16, 4))
    price_unit_packing = fields.Float('Packing', digits=(16, 2))

    _sql_constraints = [
        ('produc_uniq', 'unique(contract_id,product_id)',
         'Sorry You Entered Product Two Time You are not Allow to do this.... So We going to delete The Duplicts!'),
    ]

    @api.onchange('product_id')
    def product_id_change(self):
        """
        On change product function to read the default name and UOM of the product.

        @param product: product_id
        @return: dictionary of product name,uom,vocab and part code or Empty dictionary
        """
        if self.product_id:
            prod = self.product_id
            return {'value': {'name': prod.name,
                              'product_uom': prod.uom_po_id.id,
                              'vocab': prod.code}}
        return {}


class contract_shipment(models.Model):
    """
    To manage contract shipment """

    @api.one
    @api.depends('contract_shipment_line_ids','freight','packing')
    def _amount_all(self):
        """
        Functional field function to calculate the total amount of shipment

        @return: Dictionary of amount total valus
        """
        res = {}

        for shipment in self:
            amount = 0.0
            for line in shipment.contract_shipment_line_ids:
                amount = amount + line.price_subtotal
            if shipment.freight: amount += shipment.freight
            if shipment.packing: amount += shipment.packing
            #res[shipment.id]= amount
            self.total_amount = amount
        #return res

    def create(self, vals):
        """
        Override to edit the name field by a new sequence.

        @return: super create method
        """
        if ('name' not in vals) or (vals.get('name')=='/'):
            vals['name'] = self.env['ir.sequence'].get('contract.shipment')
        return super(contract_shipment, self).create( vals)


    def unlink(self):
        """
        Ovrride to add constrain on deleting the Shipment.

        @return: super unlink() method
        """
        if self._context is None:
            self._context = {}
        if [shipment for shipment in self if shipment.state not in ['draft']]:
            raise exceptions.ValidationError(
                _('You cannot remove shipment not in draft state !'))

        return super(contract_shipment, self).unlink()


    @api.constrains('product_qty')
    def _check_negative(self):
        """
        Constrain function to check the quantity and price and frieght and packing should be greater than 0
        @return Boolean True or False
        """
        record = self
        if record.freight < 0 :
           raise exceptions.ValidationError(
               _('Freight must be Positive'))
        if record.packing < 0:
           raise exceptions.ValidationError(
               _('Packing must be Positive'))
        return True

    @api.onchange('product_type')
    def change_product_type(self ):
        """  On_Change Function to prevent conflicting between product type in the shipment and type of the product """
        for record in self:
            for product in record.contract_shipment_line_ids :
                if record.contract_shipment_line_ids :
                    pct_type = product.product_id.type
                    if ( self.product_type == 'service' and pct_type != 'service' ) or ( self.product_type != 'service' and pct_type == 'service' ):

                        raise exceptions.ValidationError(
                            _('Your items or Some of them and the Products Type is not match.'))



    @api.constrains('product_type')
    def _check_product_type(self):
        """ Constrain function to check the products type
        @return Boolean True or False
        """
        record = self
        for product in record.contract_shipment_line_ids :
            if record.contract_shipment_line_ids :
               product_type = product.product_id.type
               if (record.product_type == 'service' and product_type != 'service' ) or (record.product_type != 'service' and product_type == 'service' ):
                  raise exceptions.ValidationError(
                      _('Your items or Some of them and the Products Type is not match ... '))
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


    name = fields.Char('Reference', size=256, required=True,default='/')
    bill_of_lading = fields.Char('Bill of Lading NO', size=64)
    final_invoice_no = fields.Char('Final Invoice No',size=64)
    delivery_date = fields.Date('Delivery Date')
    final_invoice_date = fields.Date('Final Invoice Date')
    delivery_method = fields.Selection([('air_freight', 'Air Freight'),('sea_freight', 'Sea Freight'),('free_zone','Free Zone')], 'Method of dispatch', index=True)
    delivery_period = fields.Integer('Delivery period', help="set the delivery period by days",states={'done':[('readonly',True)]})
    contract_id = fields.Many2one('purchase.contract', 'Contract')
    contract_shipment_line_ids = fields.One2many('contract.shipment.line', 'contract_shipment_id' , 'Products',)
    total_amount = fields.Float(compute="_amount_all", string='Total Amount',digits=(16,2))
    state = fields.Selection(STATE_SELECTION, 'State',default='draft', readonly=True, help="The state of the contract.", index=True)
    freight = fields.Float('Freight', digits=(16, 2),default=0.0)
    packing = fields.Float('Packing', digits=(16, 2),default=0.0)
    picking_policy = fields.Selection([('partial', 'Partial Delivery'), ('complete', 'Complete Delivery')],default='partial',
        string='Picking Policy', required=True, help="""deliver all at once as (complete), or partial shipments""",)
    purchase_id= fields.Many2one('purchase.order' , 'Reference')
    product_type=fields.Selection(PRODUCTS_TYPE, 'Product Type', index=True)
    notes= fields.Text('Notes',states={'confirmed':[('readonly',True)],'done':[('readonly',True)],'cancel':[('readonly',True)]})






    def button_dummy(self):
        """
        Dummy function to recomputes the functional felids and force
        calculation of freight and packing of each product.

        @return: True
        """
        total = 0.0

        for shippment in self:
            for product in shippment.contract_shipment_line_ids:
                total = total +  (product.product_qty * product.price_unit)

            if shippment.freight :
               total = total + shippment.freight
            if shippment.packing :
               total = total + shippment.packing

            self.write({'total_amount': 0.0 })
        return True

    def check_amount(self, shipment_object):
        """
        To add shipment value to total shipment amount, prohibit
        shipment amount from exceeding the contract amount and
        change the value of shipment_complete flag.

        @return: True
        """
        contract = shipment_object.contract_id
        contract_shipment_amount =contract.shipment_total_amount
        sum_total = contract_shipment_amount + shipment_object.total_amount
        if sum_total > contract.contract_amount:
            raise exceptions.ValidationError(
                _("The amount of shipments '%s' well be more than contract amount.."))
        else:
            contract.write({'shipment_total_amount':sum_total})
        if sum_total == contract.contract_amount:
            contract.write({'shipment_complete':True})
        return True

    def confirmed(self):
        """
        Workflow function to change the shipment state to confirm and
        check shipment products data that was required.

        @return: True
        """
        for shipment in self:
            if shipment.contract_id.state in ['draft' , 'cancel' ]:

               raise exceptions.ValidationError(
                   _('You can not confirm this shipment and the contract in draft or cancel state ..'))
            if shipment.contract_shipment_line_ids:
               #TODO: add dumy button to calculate
               amount = shipment.total_amount - (shipment.freight or 0.0) - (shipment.packing or 0.0)
               shipment.calculate_freight_packing(shipment,shipment.freight,shipment.packing, amount) #-
               if not shipment.total_amount:

                    raise exceptions.ValidationError(
                        _("Please press compute first.."))
               else:
                    shipment.check_amount(shipment)
               self.write( {'state':'confirmed'})
            else:

                raise exceptions.ValidationError(
                    _('Please fill the products list first ..'))
        return True

    def cancel(self,notes=''):
        """
        Workflow function changes shipment state to cancell and writes note
	    which contains Date and username who do cancellation.

	    @param notes: contains information of who & when cancelling order.
        @return: Boolean True
        """
        notes = ""
        user = self.env.user.name
        notes = notes +'\n'+'purchase Contract Cancelled at : '+time.strftime('%Y-%m-%d') + ' by '+ user
        self.write({'state':'cancel','notes':notes})
        for shipment in self:
            contract = shipment.contract_id
            total_amount = contract.shipment_total_amount
            new_amount = total_amount-shipment.total_amount
            contract.write({'shipment_total_amount':new_amount})
        return True

    def action_cancel_draft(self):
        """
        Changes shipment state to Draft and reset the workflow.

        @return: True
        """
        if not self:
            return False
        #wf_service = netsvc.LocalService("workflow")

        self.write({'state':'draft'})

        return True

    def done(self):
        """
        Workflow function to creating purchase order from the shipment
        and changes shipment state to done.

        @return: purchase order id
        """
        purchase_obj = self.env['purchase.order']
        purchase_line_obj = self.env['purchase.order.line']
        partner_obj = self.env['res.partner']
        purchase_order={}
        purchase_order_line={}
        for shipment in self:
                    purchase_contract = shipment.contract_id
                    part_addr = partner_obj.address_get([purchase_contract.partner_id.id])
                    pricelist=purchase_contract.partner_id.property_product_pricelist.id
                    date=purchase_contract.contract_date
                    department = purchase_contract.department_id.id
                    currency =purchase_contract.currency_id.id
                    partner = purchase_contract.partner_id.id
                    contract_with = purchase_contract.contract_with
                    purchase_order=purchase_contract.prepare_purchase_order(shipment, partner, part_addr, pricelist, purchase_contract.id, date, department, contract_with, currency,shipment.product_type )
                    or_id = purchase_obj.create( purchase_order)
                    for product in shipment.contract_shipment_line_ids:
                            purchase_order_line = purchase_contract.prepare_purchase_order_lines(product, or_id)
                            purchase_line_obj.create(purchase_order_line)
                    #if purchase_contract.payment_method == 'lc':
                    #    self.env['purchase.contract'].create_letter_of_credit(purchase_contract, or_id)
        self.write({'state':'done' , 'purchase_id' : or_id.id})
        if purchase_contract.shipment_complete:
            purchase_contract.write({'state':'done'})
        #return or_id

    def calculate_freight_packing(self,contract_obj, freight, packing,total):
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



class contract_shipment_line(models.Model):
    _name = 'contract.shipment.line'
    _description = "Contract Shipment Line"

    """
    To manage contract shipment products """
    @api.depends('product_qty','product_uom','price_unit')
    def _amount_line(self):
        """
        To compute the total price amount of shipment line.

        @return returns res which is contains the subtotal for each line
        """
        res = {}
        for line in self:
            line.price_subtotal = line.price_unit * line.product_qty
            #res[line.id] = line.price_unit * line.product_qty
        #return res
    @api.onchange('product_qty','price_unit')
    def subtotal(self):
        """
        On change function to recompute the total price after changing product qty or product unit

	    @param price: price of the product.
        @param qty: quantity of the product.
        @para product uom : product unit of measure
        @return: price_subtotal.
        """
        print(">>>>>>>>>>>>>>>>>>>>>GO HERE")
        res = {}
        prod= self.product_id
        for product in self:
            if product.product_id.uom_id.id != product.product_uom.id :
               raise exceptions.ValidationError(
                   _(' Please Select the Correct Unit of Measure for this Product '))
        if self.price_unit or self.product_qty:
            res = {'value': {'price_subtotal': self.price_unit * self.product_qty, }}
        return res

    @api.constrains('product_qty')
    def _check_negative(self):

        """
        Constrain function to check the quantity and price and frieght and packing should be greater than 0
        @return Boolean True or False
        """
        record = self
        if record.product_qty <= 0 :
           raise exceptions.ValidationError(
               _('Product Quantity must be greater than zero'))
        if record.price_unit <= 0 :
           raise exceptions.ValidationError(
               _('Price Unit must be greater than zero'))
        if record.price_unit_freight < 0 :
           raise exceptions.ValidationError(
               _('Price Unit Freight must be Positive'))
        if record.price_unit_packing < 0:
           raise exceptions.ValidationError(
               _('Price Unit Packing must be Positive'))

        return True

    
    name = fields.Char('Reference', size=256, required=True)
    vocab = fields.Char('Vocab' , size=64 )
    part_code = fields.Char('Part Code', size=64)
    product_qty = fields.Float('Quantity', required=True, digits=(16,2))
    product_uom =  fields.Many2one('product.uom', 'Product UOM', required=True)
    product_id = fields.Many2one('product.product', 'Product')
    price_unit = fields.Float('Unit Price', required=True, digits=(16, 2))
    price_subtotal = fields.Float(compute="_amount_line",  string='Subtotal',)
    contract_shipment_id = fields.Many2one('contract.shipment', 'Contract shipment',)
    tax_id = fields.Many2many('account.tax', 'contract_tax', 'purchase_contract_line_id', 'tax_id', 'Taxes')
    product_packaging = fields.Many2one('product.packaging', 'Packaging', help="Control the packages of the products")
    price_unit_freight = fields.Float('Freight',digits=(16,4))
    price_unit_packing = fields.Float('Packing',digits=(16, 2))
    notes = fields.Text('Notes',states={'confirmed':[('readonly',True)],'done':[('readonly',True)],'cancel':[('readonly',True)]})


    _sql_constraints = [
        ('product_contract_shipment_uniq','unique(contract_shipment_id,product_id)','Sorry You Entered Product Two Time You are not Allow to do this.'),]

    @api.onchange('product_id','parent.')
    def product_id_change(self):

        """
        On change product function to read the default name and UOM of the product.

        @param product: product_id
        @return: dictionary of product name,uom,vocab and part code or Empty dictionary
        """
        if self.product_id:
            prod= self.product_id

            if self.contract_shipment_id.product_type == 'service' :
               product_list = self.env['product.product'].search([('type','=','service')])
            else :
               product_list = self.env['product.product'].search([('type','!=','service')])

            return {'value': { 'name':prod.name,
                               'product_uom':prod.uom_po_id.id,
                               'vocab' : prod.code}}

        return {}


class contract_fees(models.Model):
    """
    To Manage contract fees """

    @api.model
    def create(self, vals):
        """
        Override the create method to add value to the column
        name by a new sequence.

        @return: super create method
        """
        if ('name' not in vals) or (vals.get('name')=='/'):
            vals['name'] = self.env['ir.sequence'].get('contract.fees')
        return super(contract_fees, self).create(vals)

    @api.constrains('fees_amount')
    def _check_ammount(self):
        for fees in self:
            if fees.fees_amount > 0:
                return True
        return False



    def unlink(self):
        """
        Ovrride to add constrain on deleting the Contraint .

        @return: super unlink() method
        """
        if self._context is None:
            self._context = {}
        if [fee for fee in self if fee.state not in ['draft']]:
            raise exceptions.ValidationError(
                _('You cannot remove Fee not in draft state !'))

        return super(contract_fees, self).unlink()



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

    name = fields.Char('Reference', size=64, required=True, readonly=True, index=True)
    fees_date = fields.Date('Fees Date')
    month = fields.Selection(MONTH, 'Month', index=True)
    contract_id = fields.Many2one('purchase.contract', 'Contract')
    fees_amount = fields.Float('Fees Amount', digits=(16,2),default=1.0)
    fees_amount_in_euro = fields.Float('Fees Amount In Euro', digits=(16,2),default=0.0)
    description = fields.Text('Description')
    notes = fields.Text('Notes',states={'confirmed':[('readonly',True)],'done':[('readonly',True)],'cancel':[('readonly',True)]})
    purpose = fields.Selection([('purchase','Purchase'),('other','Other')],'Purpose', index=True,default='purchase')
    state = fields.Selection([('draft','Draft'),('confirm','Confirmed'),('done','Done'),('cancel','Canceled')],'State',default='draft')

    @api.onchange('fees_amount')
    def amount_change(self):
        """
        On change amount function to calaulate fees amount in Euro.

        @return: Dictionary of fees amount in Euro
        """
        currency_obj = self.env['res.currency']
        new_amount = 0.0
        for fee in self:
            contract = fee.contract_id
            contract_currency = contract.currency_id
            euro_id = currency_obj.search([('name','=','EUR')],limit=1)
            curren = currency_obj.search([('name','=','EUR')],limit=1)
            #new_amount = contract_currency.compute( contract_currency,  self.fees_amount, curren.id,round=False)
            
            new_amount = contract_currency.with_context(date=fee.fees_date).compute(self.fees_amount,
                                                                                 curren)
        return {'value': {'fees_amount_in_euro':new_amount }}

    def confirm(self):
        """
        Workflow function to change the state to confirm.

        @return: True
        """
        currency_obj = self.env['res.currency']
        new_amount = 0.0
        for fees in self:

            contract = fees.contract_id
            #contract_currency = contract.currency_id.id
            contract_currency = contract.currency_id
            contract_state = contract.state
            if contract_state != "confirmed":

                raise exceptions.ValidationError(
                    _('you can not confirm this fees until you confirmed the contract ..'))
            #euro_id = currency_obj.search([('name','=','EUR')],limit=1)
            #curren = currency_obj.search([('name','=','EUR')],limit=1)
            

            #new_amount = currency_obj.compute(contract_currency,fees.contract_id.currency_id ,fees.fees_amount)
            new_amount = contract_currency.with_context(date=fees.fees_date).compute(self.fees_amount,
                                                                                    fees.contract_id.currency_id)
            all_amount = contract.fees_total_amount + fees.fees_amount
            if all_amount > contract.contract_amount :
                raise exceptions.ValidationError(
                    _('The total fees amount well be more than the contract amount ..'))
            else:
                contract.write({'fees_total_amount': all_amount})
        self.write({'state' : 'confirm','fees_amount_in_euro':new_amount }),

        return True


    def create_invoice(self):
        """
        Workflow function to generates invoice for given ids of purchase
        contracts Fees and links that invoice ID to the contract and change
        the state to Done.

        @return: invoice id
        """
        #Generates invoice for given ids of purchase contracts Fees and links that invoice ID to the contract.

        user_obj = self.env['res.users']
        inv_obj = self.env['account.invoice']
        inv_line_obj = self.env['account.invoice.line']
        for fees in self:
            contract = fees.contract_id
            pay_acc_id = contract.partner_id.property_account_payable_id.id
            # generate invoice line correspond to FC line and link that to created invoice (inv_id)
            company = user_obj.browse(self._uid).company_id
            contract_account = contract.contract_account
            forgin_purchase_journal = contract.journal_id or company.purchase_foreign_journal
            #addres = self.pool.get('res.partner').search(cr, uid, [('partner_id','=',contract.partner_id.id)])
            #if not addres:
                #raise osv.except_osv(_('No Address !'),_('There No address Defined Fore This partner please fill the address first') )
            if not contract_account:

                raise exceptions.ValidationError(
                    _('There No Account Defined Fore This Contract    please choose the account first'))
            if not forgin_purchase_journal:
                raise exceptions.ValidationError(
                    _('There No Foreign Purchase Journal, please choose journal first'))
            inv_line_id = inv_line_obj.create({
			    'name': fees.name,
			    'account_id': contract_account.id,
			    'price_unit': fees.fees_amount,
			    'quantity': 1,})
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
            inv_id = inv_obj.create( inv_data)
            #RECOMUPTE TO SET TOTAL ?!!!!!!?
            #inv_obj.compute_amount([inv_id], context=self._context, set_total=True)
            #contract.write({'invoice_ids': [(4, inv_id)]})
            contract.write({'invoice_ids': [(4, 6,  inv_id)]})

        self.write({'state' : 'done'}),
        return inv_id

    def cancel(self):
        """
        Workflow function to change the state to cancel.

        @return: True
        """
        for fees in self:
            contract = fees.contract_id
            new_amount = contract.fees_total_amount - fees.fees_amount
            contract.write({'fees_total_amount': new_amount})
        self.write({'state' : 'cancel'})
        return True

    def action_cancel_draft(self):
        """
        Change contract state to Draft and reset the workflow.

        @return: True

        """

        self.write( {'state':'draft'})

        return True

    def create_voucher(self):
        """
        Workflow function to generates voucher for given ids of purchase
        contracts Fees and links that voucher ID to the contract and change
        the state to Done.

        @return: voucher id
        """
        user_obj = self.env['res.users']
        voucher_obj = self.env['account.voucher']
        voucher_line_obj = self.env['account.voucher.line']
        for fees in self:
            contract = fees.contract_id
            voucher_id = voucher_obj.create({
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
                                        'account_id':contract.contract_account.id,
                                        })
            vocher_line_id = voucher_line_obj.create({
                                        'amount': fees.fees_amount,
                                        'voucher_id': voucher_id.id,
                                        'type': 'dr',
                                        'account_id': contract.contract_account.id,
                                        'name': fees.description or "/",
                			'price_unit':1
                                         })
            contract.write({'voucher_ids': [(4,0, voucher_id)]})
            fees.write({'state':'done'})
        return voucher_id

class invoice(models.Model):
    """
    To add contract id to account invoice """

    _inherit = 'account.invoice'

    contract_id = fields.Many2one('purchase.contract', 'Contract', )



class purchase_contract(models.Model):
    _name = 'purchase.contract'
    _description = "Base Contract"

    """
    To manage the contract basic concepts and the purchase contracts operations """

    @api.model
    def create(self, vals):
        """
        Override to edit the name field by a new sequence.

        @return: super create method
        """
        # this method override the create method to add value to the column name
        if ('name' not in vals) or (vals.get('name') == '/'):
            vals['name'] = self.env['ir.sequence'].get('purchase.contract')
        return super(purchase_contract, self).create(vals)

    @api.multi
    def unlink(self):
        """
        Ovrride to add constrain on deleting the contract.

        @return: super unlink() method
        """
        for line in self:
            if line.state in ['confirmed','done']:
                raise exceptions.ValidationError(_('You cannot remove Purchase Contract not in draft state !'))
        
        return super(purchase_contract, self).unlink()


    @api.depends('freight', 'packing', 'contract_line_ids')
    def _amount_all(self):
        """
        To calculate all the costs of contract products.

        @return: dictionary of the value of 'amount_untaxed',
                                            'amount_tax',
                                            'amount_total',
        """
        res = {}
        freight = 0.0
        packing = 0.0
        for contract in self:
            res[contract.id] = {
                'amount_untaxed': 0.0,
                'amount_tax': 0.0,
                'amount_total': 0.0,
            }
            val = val1 = 0.0
            if contract.freight: freight = contract.freight
            if contract.packing: packing = contract.packing
            for line in contract.contract_line_ids:
                val1 += line.price_subtotal
                val += self._amount_line_tax()
            res[contract.id]['amount_tax'] = val  # cur_obj.round(cr, uid, cur, val)
            res[contract.id]['amount_untaxed'] = val1  # cur_obj.round(cr, uid, cur, val1)
            res[contract.id]['amount_total'] = res[contract.id]['amount_untaxed'] + res[contract.id][
                'amount_tax'] + freight + packing
        return res

    def _get_order(self):
        """
        Method that returns the ID of contract line update the
        functional field in the contract object consequently.

        @return: list of purchase order lines ids
        """
        result = {}
        # need to migrate
        for line in self.env['purchase.contract.line'].search([]):
            result[line.contract_id.id] = True
        return result.keys()

    def _get_fees_ids(self):
        """
        Method that returns the ID of contract fees ids update the
        functional field in the contract object consequently.

        @return: list of fees lines ids
        """
        result = {}
        # need to migrate
        # for line in self.pool.get('contract.fees').browse():
        #    result[line.contract_id.id] = True
        return result.keys()

    def _get_shipment_ids(self):
        """
        Method that returns the ID of contract shipment ids update the
        functional field in the contract object consequently.

        @return: list of shipment lines ids
        """
        result = {}
        # need to migrate
        # for line in self.pool.get('contract.shipment').browse(cr, uid, ids, context=context):
        #    result[line.contract_id.id] = True
        return result.keys()

    def _amount_line_tax(self):
        """
        To calculate the line taxes amount.

        @param line: contract line id
        @return: tax amount
        """
        val = 0.0
        # need to migrate
        # for c in self.pool.get('account.tax').compute_all(cr, uid, line.tax_id, line.price_unit, line.product_qty)['taxes']:
        #    val += c.get('amount', 0.0)
        return val

    #@api.depends('date_start', 'end_date')
    @api.depends('start_date','end_date')
    def _compute_duration(self):
        """
        Compute the difference between Begin date and end Date.
        @return: Number of dates between Begin date and end Date
        """
        vals = {}
        for record in self:
            start_date = datetime.datetime.strptime(record.start_date, "%Y-%m-%d")
            end_date = datetime.datetime.strptime(record.end_date, "%Y-%m-%d")
            days_no = abs((end_date - start_date).days) + 1
            vals[record.id] = days_no
            self.contract_duration = days_no
        return vals

    @api.depends('contract_fees_ids')
    def _fees_total_amount(self):
        """
        To calculate the total amount of fees.
        """
        vals = {}
        for record in self:
            sum = 0.0
            for fees_id in record.contract_fees_ids:
                sum += fees_id.fees_amount
            vals[record.id] = sum
        return vals

    @api.depends('contract_shipment_ids')
    def _shipment_total_amount(self):
        """
        To calculate the total amount of shipment.
        """
        vals = {}
        for record in self:
            sum = 0.0
            for shipment_id in record.contract_shipment_ids:
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
    PYMENT = [('lc', 'Letter of credit'),
              ('cash', 'Cash Transfer Advance'),
              ('cad', 'CAD Cash Against Document'),
              ('partial', 'Partial and complete after receipt'),
              ('defer', 'Defer Payment')]

    _defaults = {

        # 'journal_id':_get_journal
    }

    name = fields.Char('Reference', size=64, readonly=1, index=True, default='/',
                       help="unique number of the contract, computed automatically when the contract is created")
    contract_date = fields.Date('Contract Date', required=True, default=fields.datetime.now(), index=True,
                                readonly=True, states={'draft': [('readonly', False)]},
                                help="Date on which this document has been created.")
    start_date = fields.Date('Start Date', required=True, index=True, help="Date on which contract is started",
                             readonly=True, states={'draft': [('readonly', False)]},default=fields.datetime.now() )
    end_date = fields.Date('End Date', index=True, help="Date on which contract is ended", readonly=True,
                           states={'draft': [('readonly', False)]}, default=fields.datetime.now())
    contract_title = fields.Char('Contract Title', size=64, default='/', required=True, readonly=True,
                                 states={'draft': [('readonly', False)]}, )
    contract_no = fields.Char('Contract Number', size=64, readonly=True, states={'draft': [('readonly', False)]},
                              help='This The Internal Contract Number')
    contract_duration = fields.Float(compute="_compute_duration", string='Contract Duration', digits=(16, 0),
                                     readonly=True,
                                     help="duration field is used to set the duration of the contract by days", )
    contract_type = fields.Selection(TYPE, 'Contract type', index=True, default='open', readonly=True,
                                     states={'draft': [('readonly', False)]}, )
    contract_amount = fields.Float('Contract Amount', digits=(16, 2), readonly=True,
                                   states={'draft': [('readonly', False)]}, )
    delivery_method = fields.Selection(DELIVERY_SELECTION, 'Method of dispatch', index=True, readonly=True,
                                       states={'draft': [('readonly', False)]})
    delivery_period = fields.Integer('Delivery period',
                                     help="set the delivery period by days", readonly=True,
                                     states={'draft': [('readonly', False)]})
    delivery_date = fields.Date('Delivery Date', index=True, help="Date on which delivery will be done",
                                readonly=True, states={'draft': [('readonly', False)]})
    partner_id = fields.Many2one('res.partner', 'Supplier', required=True, index=True, readonly=True,
                                 states={'draft': [('readonly', False)]})
    pricelist_id = fields.Many2one('product.pricelist', 'Pricelist', help="Pricelist for current supplier",
                                   readonly=True, states={'draft': [('readonly', False)]})
    currency_id = fields.Many2one('res.currency', 'Currency',default=lambda self: self.env['res.company']._company_default_get().currency_id , index=1, readonly=True,
                                  states={'draft': [('readonly', False)]})
    contract_line_ids = fields.One2many('purchase.contract.line', 'contract_id', 'Products',
                                        states={'confirmed': [('readonly', True)], 'done': [('readonly', True)]})
    payment_term = fields.Many2one('account.payment.term', 'Payment Term', readonly=True,
                                   states={'draft': [('readonly', False)]})
    incoterm = fields.Many2one('stock.incoterms', 'Incoterm',
                               help="Incoterm which stands for 'International Commercial terms' implies its a series of terms which are used in the commercial transaction.",
                               readonly=True, states={'draft': [('readonly', False)]})
    other_conditions = fields.Text('other conditions', readonly=True, states={'draft': [('readonly', False)]})
    items_types = fields.Selection(
        [('products', 'Products'), ('service', 'Service'), ('both', 'products and service'),
         ], 'Items types', help="the type of the contracts items", readonly=True,
        states={'draft': [('readonly', False)]})
    state = fields.Selection(STATE_SELECTION, 'State', default='draft', readonly=True,
                             help="The state of the contract.", index=True)
    notes = fields.Text('Notes', states={'confirmed': [('readonly', True)], 'done': [('readonly', True)],
                                         'cancel': [('readonly', True)]})
    invoice_ids = fields.One2many('account.invoice', 'contract_id', 'Invoices', readonly=True)
    contract_with = fields.Selection([('internal', 'Local Supplier'), ('foreign', 'National supplier')],
                                     'Contract With', readonly=True, states={'draft': [('readonly', False)]})
    service_type = fields.Selection([('urgent', 'Urgent'), ('periodic', 'Periodic')], 'Service Type', index=True,
                                    readonly=True, states={'draft': [('readonly', False)]})
    first_party_duties = fields.Text('Notes', readonly=True, states={'draft': [('readonly', False)]})
    second_party_duties = fields.Text('Notes', readonly=True, states={'draft': [('readonly', False)]})
    first_party_conditions = fields.Text('Notes', readonly=True, states={'draft': [('readonly', False)]})
    second_party_conditions = fields.Text('Notes', readonly=True, states={'draft': [('readonly', False)]})
    first_party_name = fields.Char('First Party Name', size=64, required=True, readonly=True,
                                   states={'draft': [('readonly', False)]})
    second_party_name = fields.Char('Second Party Name', size=64, required=True, readonly=True,
                                    states={'draft': [('readonly', False)]})
    user = fields.Many2one('res.users', 'Responsible', readonly=True, default=lambda self: self.env.user)
    shipment_complete = fields.Boolean('Shipment Complete', default=False,
                                       help="If this field is true no more shipment,the state well be done .")
    department_id = fields.Many2one('hr.department', 'Department', readonly=True,
                                    states={'draft': [('readonly', False)]})
    payment_method = fields.Selection(PYMENT, 'Payment Method', index=True, readonly=True,
                                      states={'draft': [('readonly', False)]})
    contract_shipment_ids = fields.One2many('contract.shipment', 'contract_id', 'Shipment', readonly=True,
                                            states={'draft': [('readonly', False)],
                                                    'confirmed': [('readonly', False)]}, )
    shipment_total_amount = fields.Float(compute="_shipment_total_amount", method=True,
                                         string='Shipment Total Amount', digits=(16, 2),
                                         help="The total amount of shipment.")
    fees_total_amount = fields.Float(compute="_fees_total_amount", method=True, digits=(16, 2),
                                     string='Fees Total Amount',
                                     help="The total amount of fees.")
    contract_fees_ids = fields.One2many('contract.fees', 'contract_id', 'Fees',
                                        states={'done': [('readonly', True)], 'cancel': [('readonly', True)]})
    company_id = fields.Many2one('res.company', 'Company',
                                 default=lambda self: self.env['res.company']._company_default_get(
                                     'purchase.contract'), required=True, index=1, readonly=True, )
    contract_account = fields.Many2one('account.account', 'Contract Account', required=True, readonly=True,
                                       states={'draft': [('readonly', False)]})
    journal_id = fields.Many2one('account.journal', 'Contract Journal', readonly=True,
                                 states={'draft': [('readonly', False)]})
    freight = fields.Float('Freight', digits=(16, 2), default=0.0, readonly=True,
                           states={'draft': [('readonly', False)]})
    packing = fields.Float('Packing', digits=(16, 2), readonly=True, states={'draft': [('readonly', False)]},
                           default=0)
    voucher_ids = fields.One2many('account.voucher', 'contract_id', 'Voucher', readonly=True)
    contract_purpose = fields.Selection([('purchase', 'Purchase'), ('other', 'Other')], 'Purpose',
                                        default='purchase', index=True, readonly=True,
                                        states={'draft': [('readonly', False)]})
    amount_untaxed = fields.Float(compute="_amount_all", method=True, digits=(16, 2), string='Untaxed Amount',
                                  readonly=True, multi='sums', help="The amount without tax.")
    amount_tax = fields.Float(compute="_amount_all", method=True, digits=(16, 2), string='Taxes',
                              multi='sums1', help="The tax amount.")
    amount_total = fields.Float(compute="_amount_all", method=True, digits=(16, 2), string='Total',
                                multi='sums2')

    """def _get_journal(self, cr, uid, ids):
        ''' Get default journal from the company
            return the journal id if exist'''
        company = self.pool.get('res.company').browse(cr, uid, uid)
        journal_id = company and company.purchase_foreign_journal and company.purchase_foreign_journal.id or False
        return journal_id"""

    _sql_constraints = [('Date check', "CHECK (end_date>=start_date)", _("Start date must be prior to end date!")),
                        ('contract_amount_positive', "CHECK (contract_amount>=0)",
                         _("Contract amount cannot be negative")),
                        ('contract_amount_bigger_total_shipment', "CHECK (contract_amount>=shipment_total_amount)",
                         _("Contract amount must be bigger than or equal Shipment total amount")),
                        ('contract_amount_bigger_total_fees', "CHECK (contract_amount>=fees_total_amount)",
                         _("Contract amount must be bigger than or equal Fees total amount"))]

    @api.one
    @api.constrains('contract_amount')  
    def _check_contract_amount(self):
            if self.contract_amount <= 0:
                raise UserError(_('Contract Amount, Must Be Grater Than 0!.'))


    

    def copy(self, default={}):
        """
        Override copy function to edit default value.

        @param default : default vals dict
        @return: super copy method
        """
        seq_obj = self.evn['ir.sequence']
        default.update({
            'state': 'draft',
            'name': seq_obj.get('purchase.contract'),
            'contract_date': time.strftime('%Y-%m-%d'),
            'contract_line_ids': [],
        })
        return super(purchase_contract, self).copy(default)

    def partner_id_change(self, partner):
        """
        On change partner function to read pricelist.

        @param partner : partner id
        @return: Dictionary of pricelist_id or Empty dictionary
        """
        if partner:
            return {'value': {'pricelist_id': self.env['res.partner'].search(
                [('id', '=', partner)]).property_product_pricelist_purchase.id}}
        return {}

    def button_dummy(self):
        """
        Dummy function to recomputes the functional fieds.

        @return: True
        """
        self._amount_all(['amount_untaxed'])
        return True

    def confirmed(self):
        """
        Workflow function to change state of purchase contract to confirmed
        Call calculate_freight_packing method to calculate and write freight
        and packing amount for every product price..

        @return: True
        """

        for contract in self:
            if contract.contract_type in ['detail']:
                amount = contract.amount_total - (contract.freight or 0.0) - (contract.freight or 0.0)
                contract.calculate_freight_packing(contract, contract.freight, contract.packing, amount)
                if not contract.contract_line_ids:
                    raise exceptions.ValidationError(_('Please fill the products list first ..'))
            self.write({'state': 'confirmed'})


    def done(self):
        """
        Workflow function to change state of purchase contract to done.

        @return: True
        """
        self.write({'state': 'done'})
        return True

    def cancel(self):
        """
        Workflow function to change state of purchase contract to cancel.

        @return: True
        """

        for record in self:
            for shipment in record.contract_shipment_ids:
                if shipment.state in ['confirmed', 'done']:
                    raise exceptions.ValidationError(
                        ('You Can not cancel this contract because it has shipment(s) in confirm or done state ..'))

        for record in self:
            for fee in record.contract_fees_ids:
                if fee.state in ['confirm', 'done']:
                    raise exceptions.ValidationError(
                        ('You Can not cancel this contract because it has fee(s) in confirm or done state ..'))

        notes = ""
        u = self.env.user.name
        notes = notes + '\n' + 'purchase Contract Cancelled at : ' + time.strftime('%Y-%m-%d') + ' by ' + u
        self.write({'state': 'cancel', 'notes': notes})
        return True

    def action_cancel_draft(self):
        """
        Change contract state to Draft and reset the workflow.

        @return: True
        """
        # if not len(ids):
        #    return False
        # wf_service = netsvc.LocalService("workflow")
        for s_id in self:
            self.write({'state': 'draft'})
            # wf_service.trg_delete(uid, 'purchase.contract', s_id, cr)
            # wf_service.trg_create(uid, 'purchase.contract', s_id, cr)
        return True

    def onchang_duration(self):
        """
        On change duration function to calculate end date of the contact.

        @param start_date: start date of the contract
        @param duration: contract duration
        @return: Dictionary of end_date valus
        """
        if not self.start_date:
            return {}
        if self.duration < 0:
            raise exceptions.ValidationError(
                ('Duration value can not be negative ..'))
        dif = datetime.timedelta(days=self.duration)
        statr = datetime.datetime.strptime(self.start_date, "%Y-%m-%d")
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
            return {}
        from_dt = datetime.datetime.strptime(start_date, "%Y-%m-%d")
        to_dt = datetime.datetime.strptime(end_date, "%Y-%m-%d")
        timedelta = to_dt - from_dt
        timedelta = timedelta.days
        if timedelta < 0:
            raise exceptions.ValidationError(
                ('This date is smaller than the starting date ..'))
        return {'value': {'contract_duration': timedelta}}

    def prepare_purchase_order(self, contract_object, partner, partner_addres, pricelist, contract_id, date, department, contract_with, currency, item_type='items'):
        """
        To prepare the valus of purchase order field befor creation.
        @return: Dictionary of valus
        """
        dif = datetime.timedelta(days=contract_object.delivery_period)
        current_date = datetime.date.today()
        edate = current_date + dif
        invoice = 'manual'
        if item_type == 'service': invoice = 'order'

        result = {'partner_id': partner,
                  'partner_address_id': partner_addres,
                  'pricelist_id': pricelist,
                  'state': 'draft',
                  'origin': contract_object.name,
                  'contract_id': contract_id,
                  'ir_date': date,
                  'department_id': department,
                  'delivery_period': contract_object.delivery_period,
                  'delivery_method': contract_object.delivery_method,
                  #'purchase_type': contract_with,
                  'purchase_type': 'local',
                  'invoice_method': invoice,
                  'e_date': edate,
                  'currency_id': currency,
                  'freight': contract_object.freight,
                  'packing': contract_object.packing,
                  'purpose': 'store',
                  }
        return result

    def prepare_purchase_order_lines(self,contract_line_obj,order_id):
        """
        To prepare the valus of purchase order lines field befor creation.

        @param contract_line_obj: purchase contract line object
        @param order_id: purchase order id
        @return: Dictionary of valus
        """

        product_obj = self.env['product.product']
        total = contract_line_obj.price_unit
        if contract_line_obj.price_unit_freight:
            total += contract_line_obj.price_unit_freight
        if contract_line_obj.price_unit_packing: total += contract_line_obj.price_unit_packing
        p_uom = contract_line_obj.product_id.uom_po_id.id
        result = {'name': contract_line_obj.product_id.name,
                  'product_id': contract_line_obj.product_id.id,
                  'product_qty': contract_line_obj.product_qty,
                  'date_planned': time.strftime('%Y-%m-%d'),
                  'product_uom': p_uom,
                  'price_unit': contract_line_obj.price_unit,
                  'order_id': order_id.id,
                  'notes': contract_line_obj.notes,
                  'price_unit_total': total,
                  'price_unit_freight': contract_line_obj.price_unit_freight,
                  'price_unit_packing': contract_line_obj.price_unit_packing,
                  }
        return result

    def make_purchase_order(self):
        """
        To create purchase order from selected and approved contract
        and call create_letter_of_credit if required by invoice method.

        @return: creates purchase order id
        """
        purchase_obj = self.env['purchase.order']
        purchase_line_obj = self.env['purchase.order.line']
        partner_obj = self.env['res.partner']
        purchase_order = {}
        purchase_order_line = {}
        for purchase_contract in self:
            part_addr = partner_obj.address_get([purchase_contract.partner_id.id], ['default'])['default']
            pricelist = purchase_contract.partner_id.property_product_pricelist_purchase.id
            date = purchase_contract.contract_date
            department = purchase_contract.department_id.id
            currency = purchase_contract.currency_id.id
            partner = purchase_contract.partner_id.id
            contract_with = purchase_contract.contract_with
            items_type = 'items'
            if purchase_contract.items_types == 'service': items_type = 'service'
            purchase_order = purchase_contract.prepare_purchase_order(purchase_contract, partner, part_addr,
                                                                      pricelist, purchase_contract.id, date,
                                                                      department, contract_with, currency,
                                                                      items_type)
            or_id = purchase_obj.create(purchase_order)
            for product in purchase_contract.contract_line_ids:
                purchase_order_line = purchase_contract.prepare_purchase_order_lines(product, or_id)
                purchase_line_obj.create(purchase_order_line)
            #if ebs want it then we must migrate models in create_letter_of_credit , purchase_foreign
            #if purchase_contract.payment_method == 'lc':
            #    self.create_letter_of_credit(purchase_contract, or_id)
        return or_id

    def create_letter_of_credit(self, purchase_contract, order_id):
        """
        To create letter of credit from selected and approved contract.

        @return: creates letter of credit id
        """
        product_obj = self.env['product.product']
        letter_of_credit_obj = self.env['purchase.letter.of.credit']
        letter_of_credit_line_obj = self.env['purchase.letter.of.credit.line']
        letter_of_credit_id = letter_of_credit_obj.create({
            'amount': purchase_contract.amount_total,
            'partner_id': purchase_contract.partner_id.id,
            'payment_term': purchase_contract.payment_term.id,
            'source_number': purchase_contract.name,
            'source_date': purchase_contract.contract_date,
            'currency_id': purchase_contract.currency_id.id,
            'purchase_order_ref': order_id,
            'delivery_date': purchase_contract.delivery_date,
        })
        for products in purchase_contract.contract_line_ids:
            p_uom = product_obj.search([('id', '=', products.product_id.id)]).uom_po_id.id
            letter_of_credit_line_obj.create({
                'name': products.product_id.name,
                'product_id': products.product_id.id,
                'product_qty': products.product_qty,
                'product_uom': p_uom,
                'price_subtotal': products.price_subtotal,
                'price_unit': products.price_unit,
                'tax_id': products.tax_id,
                'product_packaging': products.product_packaging,
                'letter_of_credit_line_ids': letter_of_credit_id,
                'notes': products.notes,
            })
        return letter_of_credit_id

    def create_shipment(self):
        """
        To create contract shipment called by button.

        @return: creates shipment id
        """
        shipment_obj = self.env['contract.shipment']
        for contract in self:
            shipment_id = shipment_obj.create({'contract_id': contract.id, })
            return shipment_id

    def create_fees(self):
        """
        To create contract fees called by button.

        @return: creates fees id
        """
        fees_obj = self.env['contract.fees']
        for contract in self:
            fees_id = fees_obj.create({'contract_id': contract.id, 'purpose': contract.contract_purpose})
        return fees_id

    def calculate_freight_packing(self, contract_obj, freight, packing, total):
        """
        To calculate and allocate the freight and packing value for every product.

        @return: True
        """
        fright_unit = 0.0
        packing_unit = 0.0
        for line in contract_obj.contract_line_ids:
            fright_unit = (line.price_unit / total) * freight
            packing_unit = (line.price_unit / total) * packing
            line.write({'price_unit_freight': fright_unit, 'price_unit_packing': packing_unit})
        return True

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
