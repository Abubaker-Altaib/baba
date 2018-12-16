# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
############################################################################
from openerp.osv import fields, osv
from openerp import netsvc
from openerp.tools.translate import _
from openerp.osv.orm import browse_record, browse_null
import openerp.addons.decimal_precision as dp








class purchase_requisition(osv.Model):
    _inherit = "purchase.requisition"
    STATE_SELECTION =  [
         ('draft', 'Draft'),
         ('confirm', 'Confirm'),
         ('confirm_dept', 'General Department Approve'),
         ('approve', 'General Manager Approve'),
         ('in_progress', 'Purchases Manager Sign'),
         ('done', 'Purchase Done'),
         ('cancel', 'Cancelled'),
         ('budget_approve', 'Budget Approve'),
         ('purchase_order', 'Purchase Order'),]

    _track = {
        'state': {
            'purchase_wafi.mt_rfq_in_progress': lambda self, cr, uid, obj, ctx = None: obj['state'] == 'in_progress',
            'purchase_wafi.mt_rfq_cancel': lambda self, cr, uid, obj, ctx = None: obj['state'] == 'cancel',
            'purchase_wafi.mt_rfq_approved': lambda self, cr, uid, obj, ctx = None: obj['state'] == 'approve1',
        },
    }
    _columns = {
	'department_id': fields.many2one('hr.department',string ='Department',required=True),
        'category_id': fields.many2one('product.category',string ='Category',required=True),
        'user_ids': fields.many2many('res.users',string='Users'),
        'budget_confirm_id': fields.many2one('account.budget.confirmation', 'Confirmation'),
        'supplier_ids': fields.many2many('res.partner', 'purchase_supplier_rel', 'purchase_id', 'supplier_id', 'Suppliers'),
        'state': fields.selection(STATE_SELECTION, 'Status', required=True, readonly=True),
        'exclusive': fields.selection([('exclusive','Purchase Requisition (exclusive)'),('multiple','Multiple Requisitions')],'Requisition Type', required=True, help="Purchase Requisition (exclusive):  On the confirmation of a purchase order, it cancels the remaining purchase order.\nPurchase Requisition(Multiple):  It allows to have multiple purchase orders.On confirmation of a purchase order it does not cancel the remaining orders"""),
    }

    _defaults = {
        'exclusive': '',
    }

    def fields_view_get(self, cr, uid, view_id=None, view_type='form', context=None, toolbar=False, submenu=False):
        """ Returns views and fields for current model.
        @param cr: A database cursor
        @param user: ID of the user currently logged in
        @param view_id: list of fields, which required to read signatures
        @param view_type: defines a view type. it can be one of (form, tree, graph, calender, gantt, search, mdx)
        @param context: context arguments, like lang, time zone
        @param toolbar: contains a list of reports, wizards, and links related to current model

        @return: Returns a dictionary that contains definition for fields, views, and toolbars
        """
        if not context:
            context = {}
        user_obj = self.pool.get('res.users')


        res = super(purchase_requisition, self).fields_view_get(cr, uid, view_id=view_id, view_type=view_type, context=context, toolbar=toolbar, submenu=submenu)
        grop_id = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'purchase_wafi', 'group_committee_user')

        
        


        

        for field in res['fields']:
            if field == 'user_ids':
                res['fields'][field]['domain'] = [('groups_id.id','=',grop_id[1])]
        return res

    def _check_product_categ(self, cr, uid, ids, context=None):
        """
        Method checks that amount of roof's upper and lower limit are greater than zero or not
        and whether the roof's upper limit is greater than the lower limit or not.

        @return: Boolean True Or False
        """
        purchase_req=self.browse(cr, uid, ids)[0].category_id.id
        pro_ids=self.pool.get('product.category').search(cr, uid, [('id', 'child_of', [purchase_req])], context=context)
        pro_ids.append(purchase_req)

        for record in self.browse(cr, uid, ids):
            for line in record.line_ids:
                if line.product_id.categ_id.id not in pro_ids:
                    raise osv.except_osv(_('Error!'), _('Products You Selected Must Be With The Same Category or Sub Categories'))
        return True

    _constraints = [
        (_check_product_categ, '',[''])
    ]

    def tender_done(self, cr, uid, ids, context=None):
        for req in self.browse(cr, uid, ids, context=context):
            if not req.purchase_ids:
                raise osv.except_osv(_('Error!'), _('You cannot approve a purchase requisition without any Quotation.'))
            if all([x.state in ('draft' ,'cancel') for x in req.purchase_ids]):
                raise osv.except_osv(_('Error!'), _('You cannot approve a purchase requisition without confirmed Quotation.'))
        return super(purchase_requisition, self).tender_done(cr, uid, ids, context=context)

    def tender_confirm(self, cr, uid, ids, context=None):
        for req in self.browse(cr, uid, ids, context=context):
            if not req.line_ids:
                raise osv.except_osv(_('Error!'), _('You cannot confirm a purchase requisition without any Product.'))
        self.write(cr, uid, ids, {'state':'confirm'}, context=context)
        return True

    def tender_reset(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state': 'draft'})
        wf_service = netsvc.LocalService("workflow")
        for reset_id in ids:
            wf_service.trg_create(uid, 'purchase.requisition', reset_id, cr)
        return True

    def request_quotation(self, cr, uid, ids, context=None):
        users=[]
        req_obj = self.browse(cr, uid, ids, context=context)[0]
        for user in req_obj.user_ids:
            users.append(user.id)
        if uid not in users:
            raise osv.except_osv(_('Error!'), _('This User is not included in requisition Users.'))
        else:
            dummy , view_id = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'purchase_requisition', 'view_purchase_requisition_partner')
            return {
                'name':_("Purchase Requisition"),
                'view_mode': 'form',
                'view_id': view_id,
                'view_type': 'form',
                'res_model': 'purchase.requisition.partner',
                'type': 'ir.actions.act_window',
                'nodestroy': True,
                'target': 'new',
                'domain': '[]',
                'context': context,
                }

    def do_merge(self, cr, uid, ids, context=None):
        """
        To merge similar type of purchase requisitions.
        requisitions will only be merged if:
        * Purchase requisitions are in draft
        * Purchase requisitions belong to the same partner
        * Purchase requisitions are have same stock location, same pricelist
        Lines will only be merged if:
        * requisition lines are exactly the same except for the quantity and unit

         @return: new purchase requisition id

        """
        #TOFIX: merged requisition line should be unlink
        wf_service = netsvc.LocalService("workflow")
        def make_key(br, fields):
            list_key = []
            for field in fields:
                field_val = getattr(br, field)
                if field in ('product_id'):
                    if not field_val:
                        field_val = False
                if isinstance(field_val, browse_record):
                    field_val = field_val.id
                elif isinstance(field_val, browse_null):
                    field_val = False
                elif isinstance(field_val, list):
                    field_val = ((6, 0, tuple([v.id for v in field_val])),)
                list_key.append((field, field_val))
            list_key.sort()
            return tuple(list_key)

        # Compute what the new requisitions should contain

        new_requisitions = {}

        for prequisition in [requisition for requisition in self.browse(cr, uid, ids, context=context) if requisition.state == 'approve']:
            requisition_key = make_key(prequisition, ('warehouse_id',))
            new_requisition = new_requisitions.setdefault(requisition_key, ({}, []))
            new_requisition[1].append(prequisition.id)
            requisition_infos = new_requisition[0]
            if not requisition_infos:
                requisition_infos.update({
                    'origin': prequisition.origin,
                    'date_start': prequisition.date_start,
                    'warehouse_id': prequisition.warehouse_id.id,
                    'state': 'draft',
                    'line_ids': {},
                    'description': '%s' % (prequisition.description or '',),
                })
            else:
                if prequisition.date_start < requisition_infos['date_start']:
                    requisition_infos['date_start'] = prequisition.date_start
                if prequisition.description:
                    requisition_infos['description'] = (requisition_infos['description'] or '') + ('\n%s' % (prequisition.description,))
                if prequisition.origin:
                    requisition_infos['origin'] = (requisition_infos['origin'] or '') + ' ' + prequisition.origin
            for requisition_line in prequisition.line_ids:
                line_key = make_key(requisition_line, ('product_id',))
                o_line = requisition_infos['line_ids'].setdefault(line_key, {})
                if o_line:
                    # merge the line with an existing line
                    o_line['product_qty'] += requisition_line.product_qty * requisition_line.product_uom_id.factor / o_line['uom_factor']
                else:
                    # append a new "standalone" line
                    for field in ('product_qty', 'product_uom_id'):
                        field_val = getattr(requisition_line, field)
                        if isinstance(field_val, browse_record):
                            field_val = field_val.id
                        o_line[field] = field_val
                    o_line['uom_factor'] = requisition_line.product_uom_id and requisition_line.product_uom_id.factor or 1.0



        allrequisitions = []
        requisitions_info = {}
        for requisition_key, (requisition_data, old_ids) in new_requisitions.iteritems():
            # skip merges with only one requisition
            if len(old_ids) < 2:
                allrequisitions += (old_ids or [])
                continue

            # cleanup requisition line data
            for key, value in requisition_data['line_ids'].iteritems():
                del value['uom_factor']
                value.update(dict(key))
            requisition_data['line_ids'] = [(0, 0, value) for value in requisition_data['line_ids'].itervalues()]

            # create the new requisition
            newrequisition_id = self.create(cr, uid, requisition_data)
            requisitions_info.update({newrequisition_id: old_ids})
            allrequisitions.append(newrequisition_id)

            # make triggers pointing to the old requisitions point to the new requisition
            for old_id in old_ids:
                wf_service.trg_redirect(uid, 'purchase.requisition', old_id, newrequisition_id, cr)
                wf_service.trg_validate(uid, 'purchase.requisition', old_id, 'action_cancel', cr)
        return requisitions_info

#     def make_purchase_order(self, cr, uid, ids, partner_id, context=None):
#         """
#         Create New RFQ for Supplier
#         """
#         if context is None:
#             context = {}
#         assert partner_id, 'Supplier should be specified'
#         purchase_order = self.pool.get('purchase.order')
#         purchase_order_line = self.pool.get('purchase.order.line')
#         picking_obj = self.pool.get('stock.picking')
# 
#         res_partner = self.pool.get('res.partner')
#         fiscal_position = self.pool.get('account.fiscal.position')
#         supplier = res_partner.browse(cr, uid, partner_id, context=context)
# 
#         supplier_pricelist = supplier.property_product_pricelist_purchase or False
#         res = {}
#         for requisition in self.browse(cr, uid, ids, context=context):
#             location_id = requisition.warehouse_id.lot_input_id.id
#             if supplier.id in filter(lambda x: x, [rfq.state <> 'cancel' and rfq.partner_id.id or None for rfq in requisition.purchase_ids]):
#                 raise osv.except_osv(_('Warning!'), _('You have already one %s purchase order for this partner, you must cancel this purchase order to create a new quotation.') % rfq.state)
#             if  requisition.origin :
#                 pick_id = picking_obj.search(cr,uid,[('name' , '=' , requisition.origin ),('type' , '=' , 'out')])
#                 if pick_id :
#                    location_id = picking_obj.browse(cr,uid,pick_id)[0].location_id.id
#                    
#             purchase_id = purchase_order.create(cr, uid, {
#                         'origin': requisition.name,
#                         'partner_id': supplier.id,
#                         'pricelist_id': supplier_pricelist.id,
#                         'company_id': requisition.company_id.id,
#                         'fiscal_position': supplier.property_account_position and supplier.property_account_position.id or False,
#                         'requisition_id':requisition.id,
#                         'notes':requisition.description,
#                         'warehouse_id':requisition.warehouse_id.id ,
#                         'location_id':  location_id ,
#                         'department_id':requisition.department_id.id ,
#                         'category_id':requisition.category_id.id ,
#             })
#             res[requisition.id] = purchase_id
#             for line in requisition.line_ids:
#                 product = line.product_id
#                 seller_price, qty, default_uom_po_id, date_planned = self._seller_details(cr, uid, line, supplier, context=context)
#                 taxes_ids = product.supplier_taxes_id
#                 taxes = fiscal_position.map_tax(cr, uid, supplier.property_account_position, taxes_ids)
#                 purchase_order_line.create(cr, uid, {
#                     'order_id': purchase_id,
#                     'name': product.partner_ref,
#                     'product_qty': qty,
#                     'product_id': product.id,
#                     'product_uom': default_uom_po_id,
#                     'price_unit': 0.0,
#                     'date_planned': date_planned,
#                     'taxes_id': [(6, 0, taxes)],
#                 }, context=context)
#         return res
#     

    def test_state(self, cr, uid, ids, context=None):
        List = self.browse(cr,uid,ids[0],context=context).purchase_ids
        all = filter(lambda x : x.state == 'budget_approved' or x.state == 'cancel' ,List)
        any = filter(lambda x : x.state == 'budget_approved',all)
        if len(any) > 0 and len(List) == len(all):
            return True
        return False
    
    def purchase_order(self, cr, uid, ids, context=None):
        wf_service = netsvc.LocalService('workflow')
        for req in self.browse(cr, uid, ids, context=context):
            req.write({'state':'purchase_order'})
            for order in req.purchase_ids:
                wf_service.trg_validate(uid, 'purchase.requisition', order.id, 'purchase_order', cr)

class purchase_order(osv.Model):





    def _get_order(self, cr, uid, ids, context={}):
        """ 
        To read the products of quotaion.

        @return: products ids
        """
        line_ids = [line.id for line in self.pool.get('purchase.order.line').browse(cr, uid, ids, context=context)]
        return line_ids
    
    
    def _amount_all(self, cr, uid, ids, field_name, arg, context=None):
        
        res = {}
        #result = super(purchase_order,self)._amount_all(cr, uid, ids, field_name, arg , context=context)
        
        cur_obj=self.pool.get('res.currency')
        for order in self.browse(cr, uid, ids, context=context):
            res[order.id] = {
                'amount_untaxed': 0.0,
                'amount_tax': 0.0,
                'amount_total': 0.0,
            }
#             val = val1 = 0.0
#             cur = order.pricelist_id.currency_id
#             for line in order.order_line:
#                val1 += line.price_subtotal
#                for c in self.pool.get('account.tax').compute_all(cr, uid, order.taxes_id, line.price_unit, line.product_qty, line.product_id, order.partner_id)['taxes']:
#                     val += c.get('amount', 0.0)
            total_with_tax = total_without_taxes = 0.0
            for line in order.order_line:
                    unit_price = line.price_subtotal
                    total_without_taxes += unit_price
                    tax_to_unit = 0.0
                    for tax in self.pool.get('account.tax').compute_all(cr, uid, order.taxes_id, line.price_unit, line.product_qty)['taxes']:
                        unit_tax= tax.get('amount', 0.0)
                        tax_to_unit += unit_tax/line.product_qty
                        total_with_tax += unit_tax
                    line_tax = tax_to_unit + line.price_unit 
                    #cr.execute("UPDATE purchase_order_line SET price_unit_tax=%s, price_unit_total=%s where id = %s ", (tax_to_unit, line_tax, line.id))
                    res[order.id] = {
                    'amount_tax':total_with_tax, 
                    'amount_untaxed':total_without_taxes, 
                    'amount_total':total_with_tax + total_without_taxes
                }
                    
            
        return res





    _inherit = 'purchase.order'
    STATE_SELECTION = [
        ('draft', 'Draft PO'),
        ('sent', 'RFQ Sent'),
        ('confirmed', 'Waiting Approval'),
        ('approved', 'Purchase Order'),
        ('except_picking', 'Shipping Exception'),
        ('except_invoice', 'Invoice Exception'),
        ('waiting_budget', 'Waiting for Budget Approve'),
        ('budget_approved', 'Budget Approved'),
        ('not_approve','Budget Not Approved'),
        ('done', 'Done'),
        ('cancel', 'Cancelled'),]

    _columns = {

        'taxes_id': fields.many2many('account.tax', 'purchase_order_taxes', 'ord_id', 'tax_id', 'Taxes'),
        'good_delivery': fields.boolean('Good delivery' , ),
        'high_quality': fields.boolean('High quality',),
        'good_price': fields.boolean('Good price', ),
        'other_reason': fields.char('Other Reasons', size=256 , readonly=True, states={'confirmed':[('readonly', False)], 'wait_confirmed':[('readonly', False)]},),
	'department_id': fields.many2one('hr.department',string ='Department',required=True),
        'category_id': fields.many2one('product.category',string ='Category',required=True),
        'state': fields.selection(STATE_SELECTION, 'Status', readonly=True),
        'amount_untaxed': fields.function(_amount_all, method=True, string='Untaxed Amount',
            store={
                'purchase.order': (lambda self, cr, uid, ids, c={}: ids, ['order_line', 'taxes_id'], 10), 
                'purchase.order.line': (_get_order,  ['price_unit','product_qty'], 10), 
            }, multi="sums", help="The amount without tax"), 
        'amount_tax': fields.function(_amount_all, method=True, string='Taxes', 
            store={
                'purchase.order': (lambda self, cr, uid, ids, c={}: ids, ['order_line', 'taxes_id'], 10), 
                'purchase.order.line': (_get_order, ['price_unit','product_qty'], 10), 
            }, multi="sums", help="The tax amount"), 
        'amount_total': fields.function(_amount_all, method=True, string='Total',
            store={
                'purchase.order': (lambda self, cr, uid, ids, c={}: ids, ['order_line', 'taxes_id'], 10), 
                'purchase.order.line': (_get_order, ['price_unit','product_qty'], 10), 
            }, multi="sums"), 

    }

    

    def action_cancel(self, cr, uid, ids, context=None):
        re = super(purchase_order,self).action_cancel(cr, uid, ids, context)
        browse = self.browse(cr,uid,ids,context=context)
        search_list = [i.requisition_id.id for i in browse]
        self.pool.get('purchase.requisition').write(cr,uid,search_list,{'state':'cancel'},context=context)
        return re
    def create_budget_confirmation(self, cr, uid, ids, context={}):
        budget_pool=self.pool.get('account.budget.confirmation')
        period_pool=self.pool.get('account.period')
        ctx = context.copy()
        wf_service = netsvc.LocalService('workflow')
        for order in self.browse(cr, uid, ids, context=context):
            ctx.update({'account_period_prefer_normal': True, 'company_id': order.company_id.id})
            pids = period_pool.find(cr, uid, order.date_order, context=ctx)
            for order_line in order.order_line:
                val = {
                     'reference': order.name+'/'+order_line.name,
                     'partner_id': order.partner_id.id,
                     'general_account_id':self._choose_account_from_po_line(cr, uid, order_line, context=context),
                     'period_id': pids and pids[0],
                     'analytic_account_id': order_line.account_analytic_id.id or order_line.order_id.department_id.analytic_account_id.id,
                     'amount':order_line.price_subtotal,
                     'residual_amount':order_line.price_subtotal,
                     'date': order.date_order,
                     'type' : 'purchase',
                     'note':order_line.name,
                }
                confirm_id = budget_pool.create(cr, uid, val, context=context)
                order_line.write({'budget_confirm_id':confirm_id})
                if order.requisition_id.exclusive  == 'exclusive':
                    for orders in order.requisition_id.purchase_ids:
                        if orders.id != order.id:
                            print orders.state
                            orders.write({'state': 'cancel'})
                            
                 
            
            #print order.requisition_id.order_ids
   
    def test_state(self, cr, uid, ids, context=None):
        flag = False
        for order in self.browse(cr, uid, ids, context={}):
                if all([line.budget_confirm_id.state in ('valid') for line in order.order_line]):
                    flag=True
        return flag

    def confirmation_get(self, cr, uid, ids, context=None):
        """
        This method gets all budget confirmation ids of purchase.

        @return: list of budget confirmation id
        """
        res = []
        for order in self.browse(cr, uid, ids, context=context):
            for line in order.order_line:
                if line.budget_confirm_id:
                    res.append(line.budget_confirm_id.id)
        return res

    def _prepare_inv_line(self, cr, uid, account_id, order_line, context=None):
        """Collects require data from purchase order line that is used to create invoice line
        for that purchase order line
        :param account_id: Expense account of the product of PO line if any.
        :param browse_record order_line: Purchase order line browse record
        :return: Value for fields of invoice lines.
        :rtype: dict
        """
        res = super(purchase_order, self)._prepare_inv_line(cr, uid, account_id, order_line, context=context)
        res.update({
            'account_analytic_id': order_line.account_analytic_id.id or order_line.order_id.department_id.analytic_account_id.id,
            'budget_confirm_id': order_line.budget_confirm_id.id
        })
        return res

    def _check_product_categ(self, cr, uid, ids, context=None):
        """
        Method checks that product category is chiled of order category.

        @return: Boolean True Or False
        """
        purchase_order = self.browse(cr, uid, ids)[0].category_id.id
        pro_ids = self.pool.get('product.category').search(cr, uid, [('id', 'child_of', [purchase_order])], context=context)
        pro_ids.append(purchase_order)
        for record in self.browse(cr, uid, ids[0]).order_line:
            if record.product_id.categ_id.id not in pro_ids:
                raise osv.except_osv(_('Error!'), _('Products You Selected Must Be With The Same Category or Sub Categories'))
        return True

    _constraints = [
        (_check_product_categ, '',[''])
    ]



class product_template(osv.Model):

    _inherit = 'product.template'

    _defaults = {
        'sale_ok': 0,
    }


class purchase_order_line(osv.Model):

    _inherit = 'purchase.order.line'

    _columns = {
        'budget_confirm_id': fields.many2one('account.budget.confirmation', 'Confirmation'),
    }

class purchase_requisition_line(osv.Model):
    _inherit = "purchase.requisition.line"

    def _check_positive(self, cr, uid, ids, context=None):
        """
        Method checks that product_qty is positive value.

        @return: Boolean True Or False
        """
        for record in self.browse(cr, uid, ids,context=context):
            if record.product_qty <= 0:
                raise osv.except_osv(_('Error!'), _('Product Quantity must be positive value'))
        return True


    _columns = {
        'name': fields.text('Specification', required=True),
    }


    _constraints = [
        (_check_positive, '',['product_qty'])
    ]

class product_product(osv.Model):
    _inherit = "product.product"
    def name_search(self, cr, uid, name, args=None, operator='ilike', context=None, limit=100):
        if context is None:
            context = {}
        List = []
        products = []            
        if 'products' in context:
            for i in context['products']:
                if not i[1] :
                    products.append(i[2]['product_id'])
                else:
                    List.append(i[1])

            List = filter(lambda x : x != False,List)
            purchase_requisition_line = self.pool.get("purchase.requisition.line")
            for line in purchase_requisition_line.browse(cr,uid,List,context=context):
                products.append(line.product_id.id)
            args.append(('id', 'not in', products))

        return super(product_product, self).name_search(cr, uid, name, args=args, operator=operator, context=context, limit=limit)
