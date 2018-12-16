# -*- coding: utf-8 -*-
##############################################################################
#
# NCTR, Nile Center for Technology Research
# Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################
from openerp.osv import osv,fields
import time
from datetime import datetime,timedelta,date
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp
import netsvc
import calendar



class sales_partners_products(osv.Model):
       _name = 'sales.partners.products' 
       _columns = {

          'partner_id'  : fields.many2one('res.partner' , 'Partner' ),
          'product_id' : fields.many2one('product.product' , 'Product' ),
          'sum_product_qty' : fields.integer('Sell Sum Qty' ,default = 0),
                   }


class product_product(osv.Model):
    _inherit = "product.product"
    _columns = {
              
    	'sale_catgory_id': fields.many2one('sale.category', 'Sale Category'),
    }

class sale_category(osv.osv):
    
   
    def copy(self, cr, uid, ids, default={}, context=None):
        """
        Override copy function to edit defult value.

        @param default: default vals dict
        @return: super copy method  
        """
        category_name = self.browse(cr, uid, ids, context).name
        
        if category_name:
            default.update({'name': category_name + '(copy)'})
        
        return super(sale_category, self).copy(cr, uid, ids, default, context)


    def close(self, cr, uid, ids, default={}, context=None):
	for record in self.browse(cr, uid, ids):
		cr.execute(""" select p.id from product_product p where sale_catgory_id=%s"""%(record.id))
        	result = cr.dictfetchall()
		for product in result :
			cr.execute(""" update product_product set sale_catgory_id=null where id=%s"""%(product['id']))
		for line in record.product_ids:
			cr.execute(""" update product_product set sale_catgory_id=%s where id=%s""",(record.id,line.product_id.id))
			cr.execute(""" update product_template set cost_method ='average', list_price=%s
 where id=%s""",(line.total_amount,line.product_id.product_tmpl_id.id))
        self.write(cr, uid, ids, {'state':'close'}, context=context)
        return True

    def open_draft(self, cr, uid, ids, default={}, context=None):
        self.write(cr, uid, ids, {'state':'draft'}, context=context)
        return True

    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _name = "sale.category"
    _track = {
        'state': {
            'sale.mt_order_draft': lambda self, cr, uid, obj, ctx=None: obj['state'] in ['draft'],
            'sale.mt_order_close': lambda self, cr, uid, obj, ctx=None: obj['state'] in ['close']
        },
    }
    _columns = {
        'code' : fields.char('Code', size=54, required=True,readonly=True, states={'draft': [('readonly', False)]},track_visibility='onchange',),
        'name' : fields.char('Name', size=156, required=True,readonly=True, states={'draft': [('readonly', False)]},track_visibility='onchange',),
        'product_cat':fields.many2one('product.category', 'Category',readonly=True, states={'draft': [('readonly', False)]},track_visibility='onchange',),
        'need_confirm': fields.boolean('Need Manager Confirm',readonly=True, states={'draft': [('readonly', False)]},track_visibility='onchange',),
        'active': fields.boolean('Active',readonly=True, states={'draft': [('readonly', False)]},track_visibility='onchange',),      
        'installment' : fields.integer('Instalment', help="Determine the maximum allowed month for the sale loan payment",readonly=True, states={'draft': [('readonly', False)]},track_visibility='onchange',),
        'product_ids': fields.one2many('sale.category.line', 'sale_cat_line', 'Sale Gategory line',readonly=True, states={'draft': [('readonly', False)]},track_visibility='onchange',),
        'journal_id': fields.property('account.journal', required=True,
           type='many2one', 
           relation='account.journal',
           string='Journal', 
           method=True, 
           view_load=True,readonly=True, states={'draft': [('readonly', False)]},track_visibility='onchange',),             
       'account_id': fields.property('account.account',required=True , 
        type='many2one', 
        relation='account.account',
        string='Account', 
        method=True, 
        view_load=True,readonly=True, states={'draft': [('readonly', False)]},track_visibility='onchange',),
        'analytic_id': fields.property('account.analytic.account',
            type='many2one', 
            relation='account.analytic.account',
            string='Analytic account', 
            method=True, 
            view_load=True,readonly=True, states={'draft': [('readonly', False)]},track_visibility='onchange',),
        'state': fields.selection([
            ('draft', 'Open'),
            ('close', 'Closed'),
            ], 'Status', readonly=True, track_visibility='onchange',select=True),
        'create_month': fields.boolean('Create Loan in another date',readonly=True, states={'draft': [('readonly', False)]},track_visibility='onchange',),
        'loan_date': fields.date('loan Date',readonly=True, select=True, states={'draft': [('readonly', False)]},track_visibility='onchange',),
        'payment_type': fields.selection([('cash', 'Cash'),('installment', ' Installment'),('up_cash', 'Installment with Upfront')], 'can not sell by', required=True,select=True,readonly=True,states={'draft': [('readonly', False)]},track_visibility='onchange',), 


         'property_stock_journal': fields.property('stock.journal',
           type='many2one', 
           relation='stock.journal',
           string='Stock Journal', 
           #method=True, 
           view_load=True,readonly=True, states={'draft': [('readonly', False)]},track_visibility='onchange',),


          'property_barcode_group': fields.property('res.groups',
           type='many2one', 
           relation='res.groups',
           string='Barcode Group', 
           #method=True, 
           view_load=True,readonly=True, states={'draft': [('readonly', False)]},track_visibility='onchange',),
        'is_condition': fields.boolean('Contain condition',readonly=True, states={'draft': [('readonly', False)]},track_visibility='onchange',),
        'start_date': fields.date('Start Date',readonly=True, states={'draft': [('readonly', False)]},track_visibility='onchange',),
        'end_date': fields.date('End Date',readonly=True, states={'draft': [('readonly', False)]},track_visibility='onchange',), 
	'constraint_ids': fields.one2many('sale.constarint.line', 'sale_constraint_line', 'Sale Gategory Constraint',readonly=True, states={'draft': [('readonly', False)]},track_visibility='onchange',),

	}


    		
    _defaults = {
        'state': 'draft',
        'need_confirm': True,
	'active':True,
	'create_month':False,
    }

    _sql_constraints = [
       #('sale_category_code_uniq', 'unique(code)', 'Category code must be unique !'),
       ('product_category_name_uniq', 'unique(name)', 'Category name must be unique !'),
          ]
class sale_constarint_line(osv.osv):

    _name = "sale.constarint.line"
    _columns = {
        'sale_constraint_line':fields.many2one('sale.category', 'Sale cateory Ref', track_visibility='onchange',),
        'product_id': fields.many2one('product.product', 'Product',required=True,track_visibility='onchange',),
        'hr_salary_scale':fields.many2one('hr.salary.scale', 'Hr Scale', track_visibility='onchange',),
        'payment_type': fields.selection([('cash', 'Cash'),('installment', ' Installment'),('up_cash', 'Installment with Upfront')], 'Payment Type',select=True,track_visibility='onchange',),
        'approve_qty' : fields.integer('Approved qty',required=True,track_visibility='onchange',),
		}

    _defaults = {
        'approve_qty': 1.0,
    }



class sale_category_line(osv.osv):

    def _check_line(self, cr, uid, ids, context=None):
       """
       Constraints function to check sale configuration line     
        
       @return: Boolean True or False
       """
       for record in self.browse(cr, uid, ids): 
        if record.total_amount <=0 or record.installment < 0 :
                        return False
	    	
        return True


    def _amount_all(self, cr, uid, ids,field_name, arg, context={}):
        """ 
        Functional field function to finds the value of Installment_value.

        @param field_name: list contains name of fields that call this method
        @param arg: extra arguement
        @return: Dictionary of values
        """
        res={}
        val = 0.0
        for record in self.browse(cr, uid, ids, context=context):
            val = (record.total_amount - record.installment_upfront ) / record.installment
            res[record.id] = val 
        return res

    _name = "sale.category.line"
    _columns = {
        'sale_cat_line': fields.many2one('sale.category', 'Order Reference', ondelete='cascade', select=True, readonly=True),
        'product_id': fields.many2one('product.product', 'Product',required=True,track_visibility='onchange',),
        'product_qty' : fields.integer('Product Qty',required=True , readonly=1,track_visibility='onchange',),
        'total_amount' : fields.float('Price',required=True,digits=(16,2),track_visibility='onchange',),
        'installment' : fields.integer('Instalment', help="Determine the maximum allowed month for the sale loan payment",required=True,track_visibility='onchange',),
        'installment_value' : fields.function(_amount_all, method=True, digits=(16,2), string='installment value' , store = True , readonly=True),
        'installment_upfront' : fields.integer('Down payment',required=True,track_visibility='onchange',),
        'min_roof' : fields.integer('Min Limit',required=True,track_visibility='onchange',),
    }
    _defaults = {
        'product_qty': 1.0,
	'min_roof' : 1.0,
    }

    _sql_constraints = [
       ('sale_category_code_uniq', 'unique(code)', 'Category code must be unique !'),
       ('product_category_name_uniq', 'unique(name)', 'Category name must be unique !'),
          ]
    _constraints = [
        (_check_line, 
            '\nYour Product Configuration is not right please check it again . ',
            ['Product Qty , Amount , Installment , Upfront']),]


    def onchange_product_id(self, cr, uid, ids,product,context=None):
        """ 
        Read product data when selecting a product.

        @return: dict contain product name and uom 
        """
	
        prod = self.pool.get('product.product').browse(cr, uid,product)
        return {'value': { 'total_amount':prod.list_price}}

class sale_order_line(osv.Model):

    def _updateLines(self, cr, uid, record, line, context=None): 
	val = 0.0
	sub_total = 0.0
	if record.order_id.payment_type != 'cash':
		val = (line.total_amount - record.up_front ) / record.period
		sub_total = val * record.product_uom_qty
		cr.execute(""" update sale_order_line set period = %s , price_unit=%s, installment_value =%s, up_front =%s , total_price=%s where id=%s""",(record.period , val , val , record.up_front , line.total_amount,record.id))
	else : 
		cr.execute(""" update sale_order_line set period = 1.0 , price_unit=%s, installment_value =%s, up_front =%s ,total_price=%s where id=%s""",(line.total_amount , line.total_amount , record.up_front , line.total_amount,record.id))

	return True

    def _check_product_line(self, cr, uid, ids, context=None):
       """
       Constraints function to check sale order line     
        
       @return: Boolean True or False
       """
       for record in self.browse(cr, uid, ids): 
		items = self.pool.get('sale.category.line').search(cr,uid,[('sale_cat_line','=',record.order_id.category_id.id),('product_id','=',record.product_id.id)])
		for line in self.pool.get('sale.category.line').browse(cr, uid, items) : 
			if record.period > line.installment or record.up_front < line.installment_upfront :
                        	return False
       return self._updateLines(cr, uid, record, line, context=context)


    """def _check_available(self, cr, uid, ids, context=None):
       
       Constraints function to check sale order line     
        
       @return: Boolean True or False
       
       for record in self.browse(cr, uid, ids):
		#if record.order_id.prepare == False :
			print "????????????????????????????????????????????????????????",record.stock_available , record.product_uos_qty
			if record.stock_available < record.product_uos_qty :
				raise osv.except_osv(_('Error'), _('Your Product Qty is not right please check it again\n %s')% (record.product_id.name))
	    	
       return True"""


    def _check_minum(self, cr, uid, ids, context=None):
       
       """Constraints function to check sale order line     
        
       @return: Boolean True or False"""
       stock_move_obj=self.pool.get('stock.move')
       stock_location_obj=self.pool.get('stock.location')
       sale_category_line = self.pool.get('sale.category.line')  
       for record in self.browse(cr, uid, ids):
		if record.order_id.prepare == False :
			""" 1- To check Qty on hand and future qty (not done , cancel) picking
		    		2- check product limit  
			""" 
  			check_move_ids = stock_move_obj.search(cr,uid,[('product_id','=',record.product_id.id),('state','not in',('done','cancel')),('picking_id','!=',False),('location_id','=',record.order_id.shop_id.warehouse_id.lot_stock_id.id)],context=context)
  			check_limit_ids = sale_category_line.search(cr,uid,[('product_id','=',record.product_id.id),('sale_cat_line','=',record.order_id.category_id.id)],context=context)
			"""Check Product Limit """
			prod_limit = 0
			if check_limit_ids :
				for li in check_limit_ids :
					limit = sale_category_line.browse(cr,uid,li,context=context)
					prod_limit = limit.min_roof
			"""Check Future Product QTY """
			future_prod_qty = 0.0
			if check_move_ids :
				for move in check_move_ids :
					move_line = stock_move_obj.browse(cr,uid,move,context=context)
					future_prod_qty += move_line.product_qty
			"""Qty On Hand"""
            		location_id = record.order_id.shop_id.warehouse_id and record.order_id.shop_id.warehouse_id.lot_stock_id.id
            		#if location_id and self.check_access_rule_location(cr, uid, [location_id], 'read')==True:
			qty_on_hand = stock_location_obj._product_get(cr, uid, location_id, [record.product_id.id], context = context)[record.product_id.id]
			"""Avaiable Qty = QTY on hand - Future product QTY"""
			avaiable = qty_on_hand - future_prod_qty
			#print "////////////////////////////////////////////////////////////////////////",avaiable,prod_limit
			"""Conditions : """
			if prod_limit == 0.0 or prod_limit == False :
				raise osv.except_osv(_('Error'), _('Your Product Qty have no limit insert please contact adminstrator\n %s')% (record.product_id.name))
			if avaiable <= 0.0 or avaiable <= prod_limit :
				raise osv.except_osv(_('Error'), _('Your Product Qty is reach the limit contact adminstrator\n %s')% (record.product_id.name))
			if avaiable <= record.product_uos_qty :
				raise osv.except_osv(_('Error'), _('Your Product Qty avaiable is %s contact adminstrator or change order QTY\n %s')% (avaiable,record.product_id.name))
            		"""location_id = record.order_id.shop_id.warehouse_id and record.order_id.shop_id.warehouse_id.lot_stock_id.id
            		if location_id and self.check_access_rule_location(cr, uid, [location_id], 'read')==True:
					res = stock_location_obj._product_get(cr, uid, location_id, [record.product_id.id], context = context)[record.product_id.id]
			if res < record.min_roof:
				raise osv.except_osv(_('Error'), _('Your Product Qty is reach the limit\n %s')% (record.product_id.name))
			if res < record.product_uos_qty or res < record.product_uom_qty:
				raise osv.except_osv(_('Error'), _('Your Product Qty is not right please check it again\n %s')% (record.product_id.name))"""
	    	
       return True

    def check_access_rule_location(self, cr, uid, ids, operation, context=None):
        """
        Verifies that the operation given by ``operation`` is allowed for the user
        according to ir.rules in a location.

        @param operation: one of ``write``, ``unlink``
        @return: None if the operation is allowed
        """
        where_clause, where_params, tables = self.pool.get('ir.rule').domain_get(cr, uid, 'stock.location', operation, context=context)
        if where_clause:
            where_clause = ' and ' + ' and '.join(where_clause)
            for sub_ids in cr.split_for_in_conditions(ids):
                cr.execute('SELECT ' + 'stock_location' + '.id FROM ' + ','.join(tables) +
                           ' WHERE ' + 'stock_location' + '.id IN %s' + where_clause,
                           [sub_ids] + where_params)
                if cr.rowcount != len(sub_ids):
                    return False
        return True

    def _real_stock_dest(self, cr, uid, ids, field_name, arg, context=None):
        """
        Compute real stock destnation quanity 
        @param field_names: Name of field
        @param args: other arguments
        @return Dictinory of value
        """
        res = {}
        if context is None:
            context = {}
        stock_location_obj=self.pool.get('stock.location')
        for line in self.browse(cr, uid, ids, context=context):
            context.update({'uom': line.product_id.uom_id.id,})
            res[line.id] =  0.0
            location_id = line.order_id.shop_id.warehouse_id and line.order_id.shop_id.warehouse_id.lot_stock_id.id
            if location_id and self.check_access_rule_location(cr, uid, [location_id], 'read')==True:
                    res[line.id] = stock_location_obj._product_get(cr, uid, location_id, [line.product_id.id], context = context)[line.product_id.id]
        return res


    def _real_available_dest(self, cr, uid, ids, field_name, arg, context=None):
        """
        Compute real stock destnation quanity 
        @param field_names: Name of field
        @param args: other arguments
        @return Dictinory of value
        """
        res = {}
        if context is None:
            context = {}
        stock_location_obj=self.pool.get('stock.location')
        stock_move_obj=self.pool.get('stock.move')
	sale_category_line = self.pool.get('sale.category.line') 
        for record in self.browse(cr, uid, ids):
            	context.update({'uom': record.product_id.uom_id.id,})
            	res[record.id] =  0.0
		if record.order_id.prepare == False :
			""" 1- To check Qty on hand and future qty (not done , cancel) picking
		    		2- check product limit  
			""" 
  			check_move_ids = stock_move_obj.search(cr,uid,[('product_id','=',record.product_id.id),('state','not in',('done','cancel')),('picking_id','!=',False),('location_id','=',record.order_id.shop_id.warehouse_id.lot_stock_id.id)],context=context)
			"""Check Future Product QTY """
			future_prod_qty = 0.0
			if check_move_ids :
				for move in check_move_ids :
					move_line = stock_move_obj.browse(cr,uid,move,context=context)
					future_prod_qty += move_line.product_qty
			"""Qty On Hand"""
            		location_id = record.order_id.shop_id.warehouse_id and record.order_id.shop_id.warehouse_id.lot_stock_id.id
            		#if location_id and self.check_access_rule_location(cr, uid, [location_id], 'read')==True:
			qty_on_hand = stock_location_obj._product_get(cr, uid, location_id, [record.product_id.id], context = context)[record.product_id.id]
			"""Avaiable Qty = QTY on hand - Future product QTY"""
			avaiable = qty_on_hand - future_prod_qty
			res[record.id] = avaiable

	return res

    _inherit = "sale.order.line"
    _columns = {
        'order_id': fields.many2one('sale.order', 'Order Reference', required=True, ondelete='cascade', select=True, readonly=True),
        'product_id': fields.many2one('product.product', 'Product',required=True),
        'product_uom_qty': fields.float('Quantity',required=True, digits=(16,3),readonly=True, states={'draft': [('readonly', False)]}),
        'period': fields.integer('Instalment',),
        'up_front': fields.float('Down payment',),
	'total_price':fields.float('Total Price',readonly=True ,),
        'installment_value': fields.float('Installment value',readonly=True ,),
        #'stock_available': fields.function(_real_stock_dest, method=True, type="float", digits=(16,0),string="Real Stock"),
        #'real_available': fields.function(_real_available_dest, method=True, type="float", digits=(16,0),string="Avaiable"),
        'payment_type': fields.selection([('cash', 'Cash'),('installment', ' Installment'),], 'Payment type', readonly=True,select=True),
        'min_roof' : fields.integer('Min Limit',),
    }
    _constraints = [
        (_check_product_line, 
            '\nYour Product value is not right please check it again . ',
            ['Installment , Upfront']),
	#(_check_available, 
            #'\nYour Product Qty is not right please check it again . ',
            #['Product Qty']),
	#(_check_minum, 
           # '\nYour Product Qty is reach Min Call Adminstrator . ',
           # ['Product Qty']),
	   ]



    def product_id_change(self, cr, uid, ids,pricelist, product,  qty=0,
            uom=False, qty_uos=0, uos=False, name='', partner_id=False,
            lang=False,  update_tax=True, date_order=False, packaging=False, fiscal_position=False, flag=False,  context=None):
        """res = super(sale_order_line, self).product_id_change(cr, uid, ids,pricelist, product,
                qty=qty, uom=uom, qty_uos=qty_uos, uos=uos, name=name,
                partner_id=partner_id, lang=lang, update_tax=update_tax,
                date_order=date_order, context=context)"""
        context = context or {}
        lang = lang or context.get('lang',False)
	sale_cat = ''
	sale_cat = sale_cat or context.get('category_id',False)
        if not  partner_id:
            raise osv.except_osv(_('No Customer Defined!'), _('Before choosing a product,\n select a customer in the sales form.'))

        warning = {}
        product_uom_obj = self.pool.get('product.uom')
        partner_obj = self.pool.get('res.partner')
        product_obj = self.pool.get('product.product')
        sale_cat_obj = self.pool.get('sale.category')
        sale_cat_line_obj = self.pool.get('sale.category.line')
        context = {'lang': lang, 'partner_id': partner_id}
        if partner_id:
            lang = partner_obj.browse(cr, uid, partner_id).lang
        context_partner = {'lang': lang, 'partner_id': partner_id}

        if not product:
            return {'value': {'th_weight': 0,
                'product_uos_qty': qty}, 'domain': {'product_uom': [],
                   'product_uos': []}}
        if not date_order:
            date_order = time.strftime(DEFAULT_SERVER_DATE_FORMAT)

        result = {}
        warning_msgs = ''
	catgory_obj = sale_cat_obj.browse(cr, uid,sale_cat, context=context_partner)
	value = 0.0
	period = 0.0
	for line in catgory_obj.product_ids :
		if line.product_id.id == product :
			if flag == 'cash':
				period = 1.0
				value = line.total_amount
        		result['installment_value'] = value or line.installment_value
        		result['period'] = period or line.installment
        		result['up_front'] = value or line.installment_upfront
			result['price_unit'] = value or line.installment_value
			result['total_price'] = line.total_amount
			result['min_roof'] = line.min_roof				
        product_obj = product_obj.browse(cr, uid, product, context=context_partner)
        uom2 = False
        if uom:
            uom2 = product_uom_obj.browse(cr, uid, uom)

            if product_obj.uom_id.category_id.id != uom2.category_id.id:
                uom = False
        if uos:
            if product_obj.uos_id:
                uos2 = product_uom_obj.browse(cr, uid, uos)
                if product_obj.uos_id.category_id.id != uos2.category_id.id:
                    uos = False
            else:
                uos = False
        fpos = fiscal_position and self.pool.get('account.fiscal.position').browse(cr, uid, fiscal_position) or False
        #if not flag:
        result['name'] = self.pool.get('product.product').name_get(cr, uid, [product_obj.id], context=context_partner)[0][1]
        if product_obj.description_sale:
                result['name'] += '\n'+product_obj.description_sale
        domain = {}
        if (not uom) and (not uos):
            result['product_uom'] = product_obj.uom_id.id
            if product_obj.uos_id:
                result['product_uos'] = product_obj.uos_id.id
                result['product_uos_qty'] = qty * product_obj.uos_coeff
                uos_category_id = product_obj.uos_id.category_id.id
            else:
                result['product_uos'] = False
                result['product_uos_qty'] = qty
                uos_category_id = False
            result['th_weight'] = qty * product_obj.weight
            domain = {'product_uom':
                        [('category_id', '=', product_obj.uom_id.category_id.id)],
                        'product_uos':
                        [('category_id', '=', uos_category_id)]}
        elif uos and not uom: # only happens if uom is False
            result['product_uom'] = product_obj.uom_id and product_obj.uom_id.id
            result['product_uom_qty'] = qty_uos / product_obj.uos_coeff
            result['th_weight'] = result['product_uom_qty'] * product_obj.weight
        elif uom: # whether uos is set or not
            default_uom = product_obj.uom_id and product_obj.uom_id.id
            q = product_uom_obj._compute_qty(cr, uid, uom, qty, default_uom)
            if product_obj.uos_id:
                result['product_uos'] = product_obj.uos_id.id
                result['product_uos_qty'] = qty * product_obj.uos_coeff
            else:
                result['product_uos'] = False
                result['product_uos_qty'] = qty
            result['th_weight'] = q * product_obj.weight        # Round the quantity up

        if not uom2:
            uom2 = product_obj.uom_id
        if warning_msgs:
            warning = {
                       'title': _('Configuration Error!'),
                       'message' : warning_msgs
                    }

        return {'value': result, 'domain': domain, 'warning': warning}


    def _prepare_order_line_invoice_line(self, cr, uid, line, account_id=False, context=None):
	#if :
            #return super(sale_order_line, self)._prepare_order_line_invoice_line(cr, uid, line, account_id, context)
        res = {}
        if not line.invoiced:
            if not account_id:
                if line.product_id:
                    account_id = line.product_id.property_account_income.id
                    if not account_id:
                        account_id = line.product_id.categ_id.property_account_income_categ.id
                    if not account_id:
                        raise osv.except_osv(_('Error!'),
                                _('Please define income account for this product: "%s" (id:%d).') % \
                                    (line.product_id.name, line.product_id.id,))
                else:
                    prop = self.pool.get('ir.property').get(cr, uid,
                            'property_account_income_categ', 'product.category',
                            context=context)
                    account_id = prop and prop.id or False
            uosqty = self._get_line_qty(cr, uid, line, context=context)
            uos_id = self._get_line_uom(cr, uid, line, context=context)
            pu = 0.0
            if uosqty:
                price_unit = line.order_id.payment_type=='cash' and line.price_unit or  line.up_front
                pu = round(price_unit * line.product_uom_qty / uosqty,
                        self.pool.get('decimal.precision').precision_get(cr, uid, 'Product Price'))
            fpos = line.order_id.fiscal_position or False
            account_id = self.pool.get('account.fiscal.position').map_account(cr, uid, fpos, account_id)
            if not account_id:
                raise osv.except_osv(_('Error!'),
                            _('There is no Fiscal Position defined or Income category account defined for default properties of Product categories.'))
            res = {
                'name': "Advance for: "+line.name,
                'sequence': line.sequence,
                'origin': line.order_id.name ,
                'account_id': account_id,
                'price_unit': pu,
                'quantity': uosqty,
                'discount': line.discount,
                'uos_id': uos_id,
                'product_id': line.product_id.id or False,
                'invoice_line_tax_id': [(6, 0, [x.id for x in line.tax_id])],
                'account_analytic_id': line.order_id.project_id and line.order_id.project_id.id or False,
            }

        return res

class sale_shop(osv.osv):
    _inherit = "sale.shop"

    _columns = {
        'project_id': fields.many2one('account.analytic.account', 'Analytic Account',required=True, domain=[('parent_id', '!=', False)]),
        'user_ids': fields.many2many('res.users', 'user_sale_order', 'order_id', 'user_id', 'Users'),
    }
sale_shop()

class hr_employee_loan(osv.Model):

    _inherit = "hr.employee.loan"

    _columns = {
        'sale_order_id' : fields.many2one('sale.order','sale order',select=True, invisible=True, readonly=True),
	}

class sale_order(osv.Model):

    def create(self, cr, uid, vals, context=None):
        if vals.get('name','/')=='/':
		if vals.get('order_type') == 'specific' :
            		employee = self.pool.get('hr.employee').browse(cr, uid, vals['employee_id'])
	    		vals['partner_id'] = employee.user_id.partner_id.id
            		vals['name'] = self.pool.get('ir.sequence').get(cr, uid, 'sale.order') or '/'
        return super(sale_order, self).create(cr, uid, vals, context=context)

    def write(self, cr, uid, ids, vals, context=None):
       """Method that overwrites write method and detects changes in sale_order
          @param vals: Dictionary contains the entered values
          @return: Boolean True
       """
       if 'employee_id' in vals:
      	    employee = self.pool.get('hr.employee').browse(cr, uid, vals['employee_id'])
            vals['partner_id'] = employee.user_id.partner_id.id
       return super(sale_order, self).write(cr, uid, ids, vals, context)

    def copy(self, cr, uid, id, default=None, context=None):
        if not default:
            default = {}
        default.update({
            'date_order': fields.date.context_today(self, cr, uid, context=context),
            'state': 'draft',
            'invoice_ids': [],
            'date_confirm': False,
            'create_done': False,
	    'print_order': False,
	    'print_financial': False,
	    'financial_note': '',
            'note': '',
            'client_order_ref': '',
	    'start_date':False,
            'name': self.pool.get('ir.sequence').get(cr, uid, 'sale.order'),
        })
        return super(sale_order, self).copy(cr, uid, id, default, context=context)



    def default_get(self, cr, uid, fields, context=None):
        res = super(sale_order, self).default_get(cr, uid, fields, context=context)

        has_barcode_group = self.pool.get('res.users').has_group(cr, uid, 'cooperative_sale.group_cooperative_barcode_members')

        if has_barcode_group :
           sale_categ_ids = self.pool.get('sale.category').search(cr,uid,[('active' , '=' , True),('property_barcode_group' , '!=' , False)])
           if sale_categ_ids :
              res.update({
			    'category_id': sale_categ_ids[0],			    
                        })
        return res



    _inherit = "sale.order"
    _columns = {
        'employee_id' : fields.many2one('hr.employee','Customer name',select=True, invisible=False,readonly=True,states={'draft': [('readonly', False)]},track_visibility='onchange',),
        'department_id':fields.related('employee_id', 'department_id', string='Department', type='many2one', relation='hr.department', readonly=True, store=True),
       
        'degree_id' : fields.related('employee_id','degree_id', string='Customer grade', type='many2one', readonly=True, relation='hr.salary.degree',store=True,ondelete="restrict"),
        'partner_id' : fields.related('employee_id','partner_id', string='Customer p', type='many2one', readonly=True, relation='res.partner',store=True,ondelete="restrict"),
        #'emp_code' : fields.many2one('hr.employee','Customer No' ,readonly=True,select=True, invisible=False),
        #'emp_code' : fields.related('employee_id', 'emp_code',  string='Customer No',  type='many2one',readonly=True, relation='hr.employee',store=True,ondelete="restrict"),
 
        'partner_invoice_id': fields.many2one('res.partner', 'Invoice Address', readonly=True, required=False, help="Invoice address for current sales order."),
        'partner_shipping_id': fields.many2one('res.partner', 'Delivery Address', readonly=True, required=False,  help="Delivery address for current sales order."),
       
        'category_id':fields.many2one('sale.category', 'Sale Category',readonly=True,states={'draft': [('readonly', False)]},track_visibility='onchange',),
        'product_cat': fields.related('category_id','product_cat', string='Product Category', type='many2one', readonly=True, relation='product.category',store=True,ondelete="restrict"),

        'loan_date': fields.related('category_id','loan_date', string='Loan Date', type='date', readonly=True, relation='sale.category',store=True,ondelete="restrict"),

        'picking_policy': fields.selection([('direct', 'Deliver each product when available'), ('one', 'Deliver all products at once')],'Shipping Policy', required=False , readonlt=True),
        'fiscal_position': fields.many2one('account.fiscal.position', 'Fiscal Position',required=False , readonlt=True),
        'user_id': fields.many2one('res.users', 'Salesperson', select=True, track_visibility='onchange',readonly=True),
        'payment_type': fields.selection([('cash', 'Cash'),('installment', ' Installment'),('up_cash', 'Installment with Upfront')], 'Payment type', required=True,select=True,readonly=True,states={'draft': [('readonly', False)]},track_visibility='onchange',),
        'partner_id': fields.many2one('res.partner', 'Customer', readonly=True, change_default=True, select=True, track_visibility='always'),
        'state': fields.selection([
            ('draft', 'Draft Quotation'),
            ('sent', 'Quotation Sent'),
            ('cancel', 'Cancelled'),
            ('waiting_date', 'Waiting Schedule'),
            ('progress', 'Sales Order'),
            ('manual', 'Sale to Invoice'),
            ('invoice_except', 'Invoice Exception'),
            ('complete', 'Complete'),
            ('complete2', 'Complete'),
            ('invoice', 'waiting to pay'),
            ('done', 'Done'),
            ], 'Status', readonly=True, track_visibility='onchange',
            help="Gives the status of the quotation or sales order. \nThe exception status is automatically set when a cancel operation occurs in the processing of a document linked to the sales order. \nThe 'Waiting Schedule' status is set when the invoice is confirmed but waiting for the scheduler to run on the order date.", select=True),

        'print_order': fields.boolean('Order Printed',readonly=True , states={'done': [('readonly', False)]},track_visibility='onchange',),
        'barcode_order': fields.boolean('Barcode Order',readonly=True,track_visibility='onchange',),
        'print_financial': fields.boolean('Financial Printed',readonly=True , states={'done': [('readonly', False)],'invoice': [('readonly', False)]},track_visibility='onchange',),
        'deliver_order': fields.boolean('Deduction Printed',readonly=True),
        'prepare': fields.boolean('Ready to cancel', readonly=True,states={'draft': [('readonly', False)], 'complete2': [('readonly', False)],'invoice': [('readonly', False)]}),      
        'company_id': fields.related('shop_id','company_id',type='many2one',relation='res.company',string='Company',store=True,readonly=True),
        'confirm_id': fields.many2one('res.users', 'Confirm By', select=True, track_visibility='onchange',readonly=True),
        'approve_id': fields.many2one('res.users', 'Approve By', select=True, track_visibility='onchange',readonly=True),
        'process_id': fields.many2one('res.users', 'Process By', select=True, track_visibility='onchange',readonly=True),
        'roll_id': fields.many2one('res.users', 'Roll By', select=True, track_visibility='onchange',readonly=True),
        'order_line': fields.one2many('sale.order.line', 'order_id', 'Order Lines', readonly=True, states={'draft': [('readonly', False)], 'complete2': [('readonly', False)],'invoice': [('readonly', False)]}),
        'note': fields.text('Terms and conditions',size=256),
       'shop_id': fields.many2one('sale.shop', 'Shop', required=True, readonly=True,),
       'create_done': fields.boolean('Created',readonly=True , states={'done': [('readonly', False)]},track_visibility='onchange',),
       'financial_note': fields.text('financial note',size=256,readonly=True,), 
       'product_qty' :fields.float('Product QTY',track_visibility='onchange',digits=(16,3),readonly=True, states={'draft': [('readonly', False)]}),
       'product_id': fields.many2one('product.product', 'Product',readonly=True , states={'draft': [('readonly', False)]}),
       'start_date': fields.date('Start Date', readonly=True,),
       'active': fields.boolean('Active',readonly=True),
       'order_type': fields.selection([
            ('specific', 'Specific Order'),
            ('colleactive', 'Partner Order'),
            ], 'Order Type', track_visibility='onchange',required=True,select=True,readonly=True,states={'draft': [('readonly', False)]}),
        'partner_order_id': fields.many2one('res.partner', 'Partner Address', readonly=True,states={'draft': [('readonly', False)]},track_visibility='onchange',), 
    }
    _defaults = {
        'state': 'draft',
        'prepare': False,
        'active': True,
        'create_done': False,
	'shop_id' : 2 ,
	'product_qty':1.0,
        'deliver_order': False,
	'order_type':'specific',
        'company_id': lambda s, cr, uid, c: s.pool.get('res.company')._company_default_get(cr, uid, 'account.account', context=c),
    }







    def _check_quantity(self, cr, uid, ids, context=None): 
        """ 
        Constrain function to check the Approved Quantity .

        @return: Boolean True or False  
        """
        for order in self.browse(cr, uid, ids, context=context):
            if order.category_id :
               if order.category_id.is_condition == True :
                  for product_constraint in order.category_id.constraint_ids:
                      for product_line in order.order_line :
                          if product_constraint.product_id.id == product_line.product_id.id :
                             if product_line.product_uom_qty  > product_constraint.approve_qty : 
                                raise osv.except_osv(_('Product Quantity Exceed !'), _('This Partner was exceed the Approved Qty .\n%s')% (order.partner_id.name))

                             #if order.partner_id.partner_sales_ids:
                             #   for line in order.partner_id.partner_sales_ids:
                             #       if line.product_id.id == product_constraint.product_id.id:
                             if ( order.partner_id.sum_product_qty + product_line.product_uom_qty)  > product_constraint.approve_qty :
                                raise osv.except_osv(_('Product Quantity Exceed !'), _('This Partner was exceed the Approved Qty .\n%s')% (order.partner_id.name))


        return True


    def _check_created(self, cr, uid, ids, context=None): 
        """ 
        Constrain function to check the Approved Quantity .

        @return: Boolean True or False  
        """
        picking_obj = self.pool.get('stock.picking')
        for order in self.browse(cr, uid, ids, context=context):
  		check_picking = picking_obj.search(cr,uid,[('sale_id','=',order.id),('state','=','done')],context=context)
		if check_picking :
                	raise osv.except_osv(_('Already created !'), _('This Records details already created for .\n%s')% (order.partner_id.name))
        return True


    _constraints = [        
#(_check_quantity, 'Products quantity Exceed ! \n This Partner was exceed the Approved Qty .',['partner_id']),
#(_check_created, 'Already created ! \n This Records details already created for .',['partner_id']),        
]





    def unlink(self, cr, uid, ids, context=None):
        for o in self.browse(cr, uid, ids):
	    if o.state in ('draft', 'cancel'):
                raise osv.except_osv(_('Error!'),_('You can not delete sale order confirmed or approved.'))    
        return super(sale_order, self).unlink(cr, uid, ids, context=context)


    def action_to_invoice(self, cr, uid, ids, context=None):
        loan_obj = self.pool.get('hr.employee.loan')
	check_roll_loan = False
        for record in self.browse(cr, uid, ids):
		if not record.payment_type == 'cash' or not record.order_type == 'specific': 
			raise osv.except_osv('ERROR', 'You can not Back to Invoice please Contact Adminstrator')
  		check_loan = loan_obj.search(cr,uid,[('sale_order_id','=',record.id)],context=context)
		if check_loan :
			for loan in check_loan :
				loan_id = loan_obj.browse(cr,uid,loan,context=context)
				if loan_id.state != 'done':
					check_roll_loan = True
                                	loan_obj.write(cr ,uid , loan_id.id , {'state' : 'rejected'},context = context)
				if not check_roll_loan :
	      				raise osv.except_osv('ERROR', 'Frist Roll back Payroll calculation')
		if record.print_financial == True :
                	raise osv.except_osv(_('Error!'),_('You cannot roll back this record because financial is printed.'))    
                u = self.pool.get('res.users').browse(self, cr, uid, ids).id
            	self.write(cr, uid, ids, {'state':'invoice','roll_id':u}, context=context)
      		for line in record.order_line:
					new_sell_qty = record.partner_id.sum_product_qty - line.product_uom_qty
                			self.pool.get('res.partner').write(cr,uid,[record.partner_id.id],{'sum_product_qty' : new_sell_qty })
        return True

    def onchange_product_barcode(self, cr, uid, ids,pricelist_id,employee_id,partner_id,category_id,product_id,product_qty,payment_type,flag=False,order_lines=False,context=None):
		if not ids :
			pass
			#raise osv.except_osv(_('Error!'),_('Please Save The record First'))    
		else :
			new_id = ids[0]
		sale_line_obj = self.pool.get('sale.order.line')
		sale_cat_obj = self.pool.get('sale.category')
		sale_cat_line_obj = self.pool.get('sale.category.line')
		result = {}
			#result = {'value': {'product_id': False}}
		
		if product_id:
			product_id = self.pool.get('product.product').browse(cr, uid, product_id)
		installment_value = 0.0
		period = 0.0
		up_front = 0.0
		price_unit = 0.0
		total_price = 0.0
		min_roof = 0.0
		list_new = []
		value_list = {
				'order_line':[],'product_id':False,'product_qty':1.0}
		flage_ex = False
		if any(ids):
			record = self.browse(cr, uid, ids[0])
			catgory_obj = sale_cat_obj.browse(cr, uid,record.category_id.id, context=context)
			value = 0.0
			for line in catgory_obj.product_ids :
				if line.product_id.id == product_id.id :
					if payment_type == 'cash':
						value = line.total_amount
						installment_value = value 
						period = line.installment
						up_front = 0.0 
						price_unit = value
						total_price = line.total_amount * product_qty
						min_roof = line.min_roof
					else:
						value = line.total_amount
						installment_value = line.installment_value
						period = line.installment
						price_unit = line.installment_value
						total_price = line.installment_value * product_qty
						min_roof = line.min_roof
						up_front = 0.0
						if payment_type == 'up_cash':
							up_front = line.installment_upfront
			
			if record.order_line :
				for record_line in record.order_line:
					if record_line.product_id.id == product_id.id:
						qty = 0.0
						qty=record_line.product_uom_qty+product_qty
									#sale_line_obj.write(cr ,uid , check_product , {'product_uom_qty' : qty},context = context)
						order_lines.append( (1,record_line.id,{'product_uom_qty':qty}) )
						cou = 0
						for line in order_lines:
							if line == [4, record_line.id, False]:
								del order_lines[cou]
							cou+=1
						
						flage_ex = True
								
		if not flage_ex :
			for line in order_lines:
				if line[0] == 0:
					if line[2]['product_id'] == product_id.id:
						qty = 0.0
						line[2]['product_uom_qty']+=product_qty
						flage_ex = True
		if not flage_ex:
			catgory_obj = sale_cat_obj.browse(cr, uid,category_id, context=context)
			value = 0.0
			for line in catgory_obj.product_ids :
				if line.product_id.id == product_id.id :
					if payment_type == 'cash':
						value = line.total_amount
						installment_value = value 
						period = line.installment
						up_front = 0.0 
						price_unit = value
						total_price = line.total_amount * product_qty
						min_roof = line.min_roof
					else:
						value = line.total_amount
						installment_value = line.installment_value
						period = line.installment
						price_unit = line.installment_value
						total_price = line.installment_value * product_qty
						min_roof = line.min_roof
						up_front = 0.0
						if payment_type == 'up_cash':
							up_front = line.installment_upfront

			order_lines.append( (0,0, {
			'name':product_id.name,\
			'product_id': product_id.id,\
			'product_uom_qty': product_qty,\
			'installment_value':installment_value,
			'period':period,\
			'up_front':up_front,\
			'price_unit':price_unit,\
			'total_price':total_price,\
			'min_roof':min_roof,\
			}) )
		value_list['order_line'] = order_lines				
		result['value'] = value_list
		return result


    def action_roll(self, cr, uid, ids, context=None):
        picking_obj = self.pool.get('stock.picking')
        picking_in_obj = self.pool.get('stock.picking.in')
        stock_move = self.pool.get('stock.move')
        loan_obj = self.pool.get('hr.employee.loan')
	check_roll_pick = False
	check_roll_loan = False
        for record in self.browse(cr, uid, ids):
                u = self.pool.get('res.users').browse(self, cr, uid, ids).id
  		check_picking = picking_obj.search(cr,uid,[('sale_id','=',record.id)],context=context)
  		check_loan = loan_obj.search(cr,uid,[('sale_order_id','=',record.id)],context=context)
		if not record.payment_type == 'cash': 
			if not check_picking or not check_loan : 
	      			raise osv.except_osv('ERROR', 'No Picking or Loan Found check Admininstator')
		for line in check_picking :
			picking = picking_obj.browse(cr,uid,line,context=context)
			if picking.state != 'done':
			   check_roll_pick = True
                           picking_obj.write(cr ,uid , picking.id , {'state' : 'cancel'},context = context)
			   move_ids = stock_move.search(cr,uid,[('picking_id','=',picking.id)],context=context)
			   for move in move_ids :
                           	stock_move.write(cr ,uid , move , {'state' : 'cancel'},context = context)
			if picking.state == 'done' and '-return' in picking.name :
			   check_roll_pick = True
		if not check_roll_pick :
	      		raise osv.except_osv('ERROR', 'Frist return items to stock')
		for loan in check_loan :
			loan_id = loan_obj.browse(cr,uid,loan,context=context)
			if loan_id.state != 'done':
				check_roll_loan = True
                                loan_obj.write(cr ,uid , loan_id.id , {'state' : 'rejected'},context = context)
		if not record.payment_type == 'cash':  
			if not check_roll_loan :
	      			raise osv.except_osv('ERROR', 'Frist Roll back Payroll calculation')
		if (check_roll_pick == True and check_roll_loan == True) or (check_roll_pick == True and record.payment_type == 'cash'):
            		self.write(cr, uid, ids, {'state':'cancel','roll_id':u}, context=context)
        return True

    def onchange_employee(self, cr, uid, ids, employee_id):
        result = {'value': {'department_id': False}}
        if employee_id:
            employee = self.pool.get('hr.employee').browse(cr, uid, employee_id)
            sale_order_obj = self.browse(cr, uid, employee_id)
            result['value'] = {'department_id': employee.department_id.id,'degree_id':employee.degree_id.id,'partner_id':employee.user_id.partner_id.id}
            
        return result


    def onchange_payment_type(self, cr, uid, ids,payment,context=None):
	result = {}
	value_list = {'order_line':[]}
        if payment:
            for record in self.browse(cr, uid, ids):
		if not record.order_line :
            		result['value'] = {'payment_type':payment}
		else:

			for line in record.order_line :
			         all_ids = []
				 all_ids.append(line.id)
			del_items = self.pool.get('sale.order.line').unlink(cr, uid, all_ids, context=context)
	      		#raise osv.except_osv('ERROR', 'We Already Reomved order Lines')
	result['value'] = value_list	
        return result

    def onchange_sale_cat(self, cr, uid, ids,category_id,context=None):
	result = {}
        if category_id:
            for record in self.browse(cr, uid, ids):
		if not record.order_line :
            		sale = self.pool.get('sale.category').browse(cr, uid, category_id)
            		result['value'] = {'product_cat':sale.product_cat.id}
		else:

			for line in record.order_line :
			         all_ids = []
				 all_ids.append(line.id)
			del_items = self.pool.get('sale.order.line').unlink(cr, uid, all_ids, context=context)
	      		#raise osv.except_osv('ERROR', 'We Already Reomved order Lines')
			
        return result

    def complete(self, cr, uid, ids, context=None):
	sale_category_line = self.pool.get('sale.category.line')
        stock_location_obj=self.pool.get('stock.location')  
        wf_service = netsvc.LocalService("workflow")
        has_barcode_group = self.pool.get('res.users').has_group(cr, uid, 'cooperative_sale.group_cooperative_barcode_members')
        sale_rec = self.browse(cr,uid,ids)[0]
	if not sale_rec.order_line :
		raise osv.except_osv(_('Error'), _('Your Sale order is Wrong , please Enter Items\n Order id %s')% (sale_rec.name))
        for line in sale_rec.order_line:
			if line.order_id.prepare == False :
				""" 1- To check Qty on hand and future qty (not done , cancel) picking
		    		2- check product limit  
				""" 
  				#check_move_ids = move_obj.search(cr,uid,[('product_id','=',line.product_id.id),('state','not in',('done','cancel')),('picking_id','!=',False),('location_id','=',order.shop_id.warehouse_id.lot_stock_id.id)],context=context)
  				check_limit_ids = sale_category_line.search(cr,uid,[('product_id','=',line.product_id.id),('sale_cat_line','=',line.order_id.category_id.id)],context=context)
				"""Check Product Limit """
				prod_limit = 0
				if check_limit_ids :
					for li in check_limit_ids :
						limit = sale_category_line.browse(cr,uid,li,context=context)
						prod_limit = limit.min_roof
				"""Check Future Product QTY """
				#future_prod_qty = 0.0
                		#future_qty = move_obj.read(cr, uid, check_move_ids, ['product_qty'], context=context)
                		#total_future_qty = []
                		#for future_record in future_qty:
                    		#	total_future_qty.append(future_record['product_qty'])
                		#future_prod_qty = sum(total_future_qty)
				'''if check_move_ids :
					for move in check_move_ids :
						move_line = move_obj.browse(cr,uid,move,context=context)
						future_prod_qty += move_line.product_qty'''
				"""Qty On Hand"""
            			location_id = line.order_id.shop_id.warehouse_id and line.order_id.shop_id.warehouse_id.lot_stock_id.id
            			#if location_id and self.check_access_rule_location(cr, uid, [location_id], 'read')==True:
				qty_on_hand = stock_location_obj._product_get(cr, uid, location_id, [line.product_id.id], context = context)[line.product_id.id]
				"""Avaiable Qty = QTY on hand - Future product QTY"""
				#avaiable = qty_on_hand - future_prod_qty
				avaiable = qty_on_hand
				#print "////////////////////////////////////////////////////////////////////////",avaiable,qty_on_hand , prod_limit
				"""Conditions : """
				#if prod_limit == 0.0 or prod_limit == False :
				#	raise osv.except_osv(_('Error'), _('Your Product Qty have no limit insert please contact adminstrator\n %s\n Order id %s')% (line.product_id.name,line.order_id.name))
				if avaiable <= 0.0 or avaiable < prod_limit :
					raise osv.except_osv(_('Error'), _('Your Product Qty is reach the limit contact adminstrator\n %s \nlimit %s \nand avaible : %s\n Order id %s')% (line.product_id.name,prod_limit,avaiable,line.order_id.name))
				if avaiable < line.product_uos_qty :
					raise osv.except_osv(_('Error'), _('Your Product Qty avaiable is %s contact adminstrator or change order QTY\n %s\n Order id %s')% (avaiable,line.product_id.name,line.order_id.name))
        if has_barcode_group :
           if sale_rec.category_id.payment_type == sale_rec.payment_type :
			raise osv.except_osv(_('Error'), _('Your Sale order is Wrong , modify it and you can contact adminstartor for more information\n Order id %s')% (record.name))
           #if  sale_rec.payment_type == 'up_cash' :
	   #	raise osv.except_osv(_('Error'), _('Your Sale order is Wrong , Order id %s')% (sale_rec.name))
           self.action_ship_create(cr, uid, ids, context=context)
           for pick in sale_rec.picking_ids:
               self.pool.get('stock.picking').action_done(cr, uid, [pick.id] , context=context)
               for move in pick.move_lines:
                   self.pool.get('stock.move').action_done(cr, uid, [move.id] , context=context)

           if  sale_rec.payment_type != 'cash' :
               self.stock_loan_create(cr, uid, ids,picking_created=True,context=context)
           self.action_done(cr, uid, ids, context=context)
           wf_service.trg_validate(uid, 'sale.order', ids[0], 'draft_to_done', cr)
	   self.write(cr ,uid , ids[0] , {'barcode_order':True},context = context)

        else:
		payroll_obj = self.pool.get('payroll')
		to_date = datetime.today().strftime('%Y-%m-%d')
		today = datetime.strptime(to_date, '%Y-%m-%d')
		stock_location_obj=self.pool.get('stock.location')
		stock_move_obj=self.pool.get('stock.move')
		sale_category_line = self.pool.get('sale.category.line') 
		for record in self.browse(cr, uid, ids):
		  if record.order_type == 'specific':
		    if record.category_id.payment_type == record.payment_type :
			raise osv.except_osv(_('Error'), _('Your Sale order is Wrong , modify it and you can contact adminstartor for more information\n Order id %s')% (record.name))
		    if record.employee_id.employee_type == 'contractor' and record.payment_type != 'installment' :
			raise osv.except_osv(_('Error'), _('Your Sale order is Wrong , modify it and you can contact adminstartor for more information\n Order id %s')% (record.name))
		    u = self.pool.get('res.users').browse(self, cr, uid, ids).id
	       	    for line in record.order_line:
			if line.order_id.prepare == False :
				""" 1- To check Qty on hand and future qty (not done , cancel) picking
		    		2- check product limit  
				""" 
  				#check_move_ids = move_obj.search(cr,uid,[('product_id','=',line.product_id.id),('state','not in',('done','cancel')),('picking_id','!=',False),('location_id','=',order.shop_id.warehouse_id.lot_stock_id.id)],context=context)
  				check_limit_ids = sale_category_line.search(cr,uid,[('product_id','=',line.product_id.id),('sale_cat_line','=',line.order_id.category_id.id)],context=context)
				"""Check Product Limit """
				prod_limit = 0
				if check_limit_ids :
					for li in check_limit_ids :
						limit = sale_category_line.browse(cr,uid,li,context=context)
						prod_limit = limit.min_roof
				"""Check Future Product QTY """
				#future_prod_qty = 0.0
                		#future_qty = move_obj.read(cr, uid, check_move_ids, ['product_qty'], context=context)
                		#total_future_qty = []
                		#for future_record in future_qty:
                    		#	total_future_qty.append(future_record['product_qty'])
                		#future_prod_qty = sum(total_future_qty)
				'''if check_move_ids :
					for move in check_move_ids :
						move_line = move_obj.browse(cr,uid,move,context=context)
						future_prod_qty += move_line.product_qty'''
				"""Qty On Hand"""
            			location_id = line.order_id.shop_id.warehouse_id and line.order_id.shop_id.warehouse_id.lot_stock_id.id
            			#if location_id and self.check_access_rule_location(cr, uid, [location_id], 'read')==True:
				qty_on_hand = stock_location_obj._product_get(cr, uid, location_id, [line.product_id.id], context = context)[line.product_id.id]
				"""Avaiable Qty = QTY on hand - Future product QTY"""
				#avaiable = qty_on_hand - future_prod_qty
				avaiable = qty_on_hand
				#print "////////////////////////////////////////////////////////////////////////",avaiable,prod_limit
				"""Conditions : """
				#if prod_limit == 0.0 or prod_limit == False :
				#	raise osv.except_osv(_('Error'), _('Your Product Qty have no limit insert please contact adminstrator\n %s\n Order id %s')% (line.product_id.name,line.order_id.name))
				if avaiable <= 0.0 or avaiable < prod_limit :
					raise osv.except_osv(_('Error'), _('Your Product Qty is reach the limit contact adminstrator\n %s \nlimit %s \nand avaible : %s\n Order id %s')% (line.product_id.name,prod_limit,avaiable,line.order_id.name))
				if avaiable < line.product_uos_qty :
					raise osv.except_osv(_('Error'), _('Your Product Qty avaiable is %s contact adminstrator or change order QTY\n %s\n Order id %s')% (avaiable,line.product_id.name,line.order_id.name))
		    start_loan_date = ''
		    if record.category_id.create_month :
				start_loan_date = record.loan_date
		    else :
				start_loan_date = record.date_order
		    #last of the month
		    date_string = datetime.strptime(start_loan_date,'%Y-%m-%d')
		    if date_string.month < 12:
            	    		next_month = date(year=date_string.year, month=date_string.month+1, day=1)
		    else:
            	    		next_month = date(year=date_string.year+1, month=1, day=1)
            	    last_day = next_month - timedelta(days=1)
		    last_day = datetime.strftime (last_day,'%Y-%m-%d')
                    current_salary = payroll_obj.current_salary_status(cr, uid,ids, record.employee_id, last_day)
		    balance = current_salary.get('balance',0.0)
		    date_order	= datetime.strptime(record.date_order, '%Y-%m-%d')
		    if date_order.month < today.month :
			raise osv.except_osv(_('Error!'),_('The order date is before current date .'))
		    if not record.order_line :
		    	raise osv.except_osv(_('Error!'),_('No Items inserted,  Please insert items .'))
		    if record.employee_id.salary_suspend == True:
			raise osv.except_osv(_('Error!'),_('this employe have suspend payroll salary\n %s.')% (record.name))
		    	self.write(cr, uid, ids, {'state':'cancel','print_order':False}, context=context)
		    if record.payment_type =='installment' and balance<record.amount_total:
			raise osv.except_osv(_('Error!'),_('this employe is not enough balance\n %s.')% (record.name))
		    #self._check_quantity(cr, uid, ids, context=context)
		    #if record.category_id.need_confirm != True:
			#self.action_ship_create(cr, uid,ids, context=context)
		    if record.category_id.need_confirm == True:
		    	self.write(cr, uid, ids, {'state':'complete2','confirm_id':u,'print_order':False}, context=context)
		  else :
			if record.payment_type !='cash' :
				raise osv.except_osv(_('Error!'),_('Please Insert Record Right\n %s.')% (record.name))
           		self.action_ship_create(cr, uid, ids, context=context)
           		for pick in record.picking_ids:
               			self.pool.get('stock.picking').action_done(cr, uid, [pick.id] , context=context)
               			for move in pick.move_lines:
                   			self.pool.get('stock.move').action_done(cr, uid, [move.id] , context=context)
           		self.action_done(cr, uid, ids, context=context)
           		wf_service.trg_validate(uid, 'sale.order', ids[0], 'draft_to_done', cr)
        return False


    def stock_loan_create(self, cr, uid, ids, context=None,picking_created=False):
        payroll_obj = self.pool.get('payroll')
        sale_obj = self.pool.get('sale.order')
        loan_obj = self.pool.get('hr.employee.loan')
        inv_obj = self.pool.get('account.invoice')
        inv_line_obj = self.pool.get('account.invoice.line')
        move_obj = self.pool.get('stock.move')
	sale_category_line = self.pool.get('sale.category.line') 
        picking_obj = self.pool.get('stock.picking')
        procurement_obj = self.pool.get('procurement.order')
	lines = []
	inv_ids = []
	lis_value = {}
	done_ids = []
	invoice_ids = []
	amount = 0.0
	up_front = 0.0
        stock_location_obj=self.pool.get('stock.location') 
	for order in self.browse(cr, uid, ids, context):
		if not order.order_line :
		    	raise osv.except_osv(_('Error!'),_('No Items inserted,  Please insert items .'))
	    	if order.category_id.payment_type == order.payment_type :
			raise osv.except_osv(_('Error'), _('Your Sale order is Wrong , modify it and you can contact adminstartor for more information\n Order id %s')% (order.name))
	        if order.employee_id.employee_type == 'contractor' and order.payment_type != 'installment' :
			raise osv.except_osv(_('Error'), _('Your Sale order is Wrong , modify it and you can contact adminstartor for more information\n Order id %s')% (order.name))
       		for line in order.order_line:
			if line.order_id.prepare == False and picking_created==False:
				""" 1- To check Qty on hand and future qty (not done , cancel) picking
		    		2- check product limit  
				""" 
  				#check_move_ids = move_obj.search(cr,uid,[('product_id','=',line.product_id.id),('state','not in',('done','cancel')),('picking_id','!=',False),('location_id','=',order.shop_id.warehouse_id.lot_stock_id.id)],context=context)
  				check_limit_ids = sale_category_line.search(cr,uid,[('product_id','=',line.product_id.id),('sale_cat_line','=',line.order_id.category_id.id)],context=context)
				"""Check Product Limit """
				prod_limit = 0
				if check_limit_ids :
					for li in check_limit_ids :
						limit = sale_category_line.browse(cr,uid,li,context=context)
						prod_limit = limit.min_roof
				"""Check Future Product QTY """
				#future_prod_qty = 0.0
                		#future_qty = move_obj.read(cr, uid, check_move_ids, ['product_qty'], context=context)
                		#total_future_qty = []
                		#for future_record in future_qty:
                    		#	total_future_qty.append(future_record['product_qty'])
                		#future_prod_qty = sum(total_future_qty)
				'''if check_move_ids :
					for move in check_move_ids :
						move_line = move_obj.browse(cr,uid,move,context=context)
						future_prod_qty += move_line.product_qty'''
				"""Qty On Hand"""
            			location_id = line.order_id.shop_id.warehouse_id and line.order_id.shop_id.warehouse_id.lot_stock_id.id
            			#if location_id and self.check_access_rule_location(cr, uid, [location_id], 'read')==True:
				qty_on_hand = stock_location_obj._product_get(cr, uid, location_id, [line.product_id.id], context = context)[line.product_id.id]
				"""Avaiable Qty = QTY on hand - Future product QTY"""
				#avaiable = qty_on_hand - future_prod_qty
				avaiable = qty_on_hand
				#print "////////////////////////////////////////////////////////////////////////",avaiable,prod_limit
				"""Conditions : """
				#if prod_limit == 0.0 or prod_limit == False :
				#	raise osv.except_osv(_('Error'), _('Your Product Qty have no limit insert please contact adminstrator\n %s\n Order id %s')% (line.product_id.name,line.order_id.name))
				if avaiable <= 0.0 or avaiable < prod_limit :
					raise osv.except_osv(_('Error'), _('Your Product Qty is reach the limit contact adminstrator\n %s \nlimit %s \nand avaible : %s\n Order id %s')% (line.product_id.name,prod_limit,avaiable,line.order_id.name))
				if avaiable < line.product_uos_qty :
					raise osv.except_osv(_('Error'), _('Your Product Qty avaiable is %s contact adminstrator or change order QTY\n %s\n Order id %s')% (avaiable,line.product_id.name,line.order_id.name))
		#self._check_quantity(cr, uid, ids, context=context)
		if order.payment_type == 'installment' :
			start_loan_date = ''
			if order.category_id.create_month :
				start_loan_date = order.loan_date
			else :
				start_loan_date = order.date_order
			#last of the month
			date_string = datetime.strptime(start_loan_date,'%Y-%m-%d')
			if date_string.month < 12:
            	    		next_month = date(year=date_string.year, month=date_string.month+1, day=1)
			else:
            	    		next_month = date(year=date_string.year+1, month=1, day=1)
            		last_day = next_month - timedelta(days=1)
		        last_day = datetime.strftime (last_day,'%Y-%m-%d')
                	current_salary = payroll_obj.current_salary_status(cr, uid,ids, order.employee_id, last_day)
                	balance = current_salary.get('balance',0.0)
	        	if order.employee_id.salary_suspend == True:
				raise osv.except_osv(_('Error!'),_('this employe have suspend payroll salary \n %s.')% (order.name))
            			self.write(cr, uid, ids, {'state':'cancel','print_order':False}, context=context)
	        	if order.payment_type =='installment' and balance<order.amount_total:
				raise osv.except_osv(_('Error!'),_('this employe is not enough balance \n %s.')% (order.name))
			if order.payment_type =='installment':
				if order.create_done == False:
             				if order.company_id.loan_id.id :
				#up_front = 0
						cr.execute ("""select l.period as period , sum (l.installment_value * l.product_uom_qty) installment 
						from sale_order_line l
                                                left join sale_order so on (so.id = l.order_id)  
						where l.order_id = '%s'
						group by l.period """%order.id)
        					result = cr.dictfetchall()
						for record in result :
							loan_amount = 0.0
							#loan_amount = record['price'] - record['front']
							loan_id = loan_obj.create(cr, uid, {'employee_id':order.employee_id.id,\
	                                			'refund_from':'salary',\
								'loan_id':order.company_id.loan_id.id ,\
					 			'total_installment':record['period'],\
								'loan_amount': record['installment'] * record['period'] ,
								'salary_refund':record['installment'],
			   					'addendum_refund' : 1,
			   					'state':'draft',
								'sale_order_id':order.id,
								'start_date':start_loan_date,
								'comments':'أقساط المؤسسة التعاونية',
			   					'addendum_install_no' : 1 , }, context)
                                        		wf_service = netsvc.LocalService("workflow")
                                        		wf_service.trg_validate(uid , 'hr.employee.loan' , loan_id , 'cooperative_loan_paid' ,cr )
                                        		loan_obj.write(cr ,uid , loan_id , {'state' : 'paid'},context = context)
                                        		self.write(cr ,uid , order.id , {'start_date':start_loan_date},context = context)

             				else:
             					raise osv.except_osv(_('Error!'),_('No loan created, Please creat a loan in the company form in Hr setting page .'))
		if order.payment_type != 'installment' :
			if order.payment_type == 'up_cash' :
		    		start_loan_date = ''
		    		if order.category_id.create_month :
					start_loan_date = order.loan_date
		    		else :
					start_loan_date = order.date_order
				#last of the month
				date_string = datetime.strptime(start_loan_date,'%Y-%m-%d')
				if date_string.month < 12:
            	    			next_month = date(year=date_string.year, month=date_string.month+1, day=1)
				else:
            	    			next_month = date(year=date_string.year+1, month=1, day=1)
            			last_day = next_month - timedelta(days=1)
		        	last_day = datetime.strftime (last_day,'%Y-%m-%d')
                    		current_salary = payroll_obj.current_salary_status(cr, uid,ids, order.employee_id, last_day)
                		balance = current_salary.get('balance',0.0)
	        		if order.employee_id.salary_suspend == True:
					raise osv.except_osv(_('Error!'),_('this employe have suspend payroll salary \n %s.')% (order.name))
            				self.write(cr, uid, ids, {'state':'cancel','print_order':False}, context=context)
	        		if order.payment_type =='up_cash' and balance<order.amount_total:
					raise osv.except_osv(_('Error!'),_('this employe is not enough balance \n %s.')% (order.name))
				if order.payment_type =='up_cash':
					if order.create_done == False:
             					if order.company_id.loan_id.id :
				#up_front = 0
							cr.execute ("""select l.period as period , sum (l.installment_value * l.product_uom_qty) installment 
									from sale_order_line l
                                                			left join sale_order so on (so.id = l.order_id)  
									where l.order_id = '%s'
									group by l.period """%order.id)
        						result = cr.dictfetchall()
							for record in result :
								loan_amount = 0.0
								start_loan_date = ''
								if order.category_id.create_month :
									start_loan_date = order.loan_date
								else :
									start_loan_date = order.date_order
								#loan_amount = record['price'] - record['front']
								loan_id = loan_obj.create(cr, uid, {'employee_id':order.employee_id.id,\
	                                				'refund_from':'salary',\
									'loan_id':order.company_id.loan_id.id ,\
					 				'total_installment':record['period'],\
									'loan_amount': record['installment'] * record['period'] ,
									'salary_refund':record['installment'],
			   						'addendum_refund' : 1,
			   						'state':'draft',
									'sale_order_id':order.id,
									'start_date':start_loan_date,
									'comments':'أقساط بمقدمات - أقساط المؤسسة التعاونية - أجهزة كهربائية',
			   						'addendum_install_no' : 1 , }, context)
                                        			wf_service = netsvc.LocalService("workflow")
                                        			wf_service.trg_validate(uid , 'hr.employee.loan' , loan_id , 'cooperative_loan_paid' ,cr )
                                        			loan_obj.write(cr ,uid , loan_id , {'state' : 'paid'},context = context)
                                        		        self.write(cr ,uid , order.id , {'start_date':start_loan_date},context = context)

             					else:
             						raise osv.except_osv(_('Error!'),_('No loan created, Please creat a loan in the company form in Hr setting page .'))
             		
			picking_id = ''
       			for line in order.order_line:
            			"""if line.state == 'done':
                			continue"""
            			if line.product_id and line.order_id.create_done == False and picking_created == False:
                			if line.product_id.type in ('product', 'consu'):
                    				if not picking_id :
                        				picking_id = picking_obj.create(cr, uid, self._prepare_order_picking(cr, uid, order, context=context))
                    			move_id = move_obj.create(cr, uid, self._prepare_order_line_move(cr, uid, order, line, picking_id, order.date_order, context=context))
        				self.write(cr, uid, order.id, {'create_done':True}, context=context)
        	#wf_service = netsvc.LocalService("workflow")
        	#wf_service.trg_validate(uid, 'stock.picking', picking_id, 'done', cr)
		#self._create_pickings_and_procurements(cr, uid, order, order.order_line, None, context=context)
                	#u = self.pool.get('res.users').browse(self, cr, uid, ids).id
                        done_ids.append(order.id)

        	else :
                        invoice_ids.append(order.id)
                	#u = self.pool.get('res.users').browse(self, cr, uid, ids).id
        
        self.write(cr, uid, done_ids, {'state':'done','approve_id':uid,'print_order':False}, context=context)
	self.write(cr, uid, invoice_ids, {'state':'invoice','approve_id':uid,'print_order':False}, context=context)

        return True


    def invoice(self, cr, uid, ids, context=None):
        payroll_obj = self.pool.get('payroll')
        sale_obj = self.pool.get('sale.order')
        loan_obj = self.pool.get('hr.employee.loan')
        inv_obj = self.pool.get('account.invoice')
        inv_line_obj = self.pool.get('account.invoice.line')
        move_obj = self.pool.get('stock.move')
	sale_category_line = self.pool.get('sale.category.line') 
        picking_obj = self.pool.get('stock.picking')
        procurement_obj = self.pool.get('procurement.order')
	lines = []
	inv_ids = []
	lis_value = {}
	amount = 0.0
	up_front = 0.0
        stock_location_obj=self.pool.get('stock.location') 
	for order in self.browse(cr, uid, ids, context):
       		for line in order.order_line:
			if not order.order_line :
		    		raise osv.except_osv(_('Error!'),_('No Items inserted,  Please insert items .'))
			if line.order_id.prepare == False :
				""" 1- To check Qty on hand and future qty (not done , cancel) picking
		    		2- check product limit  
				""" 
  				#check_move_ids = move_obj.search(cr,uid,[('product_id','=',line.product_id.id),('state','not in',('done','cancel')),('picking_id','!=',False),('location_id','=',order.shop_id.warehouse_id.lot_stock_id.id)],context=context)
  				check_limit_ids = sale_category_line.search(cr,uid,[('product_id','=',line.product_id.id),('sale_cat_line','=',line.order_id.category_id.id)],context=context)
				"""Check Product Limit """
				prod_limit = 0
				if check_limit_ids :
					for li in check_limit_ids :
						limit = sale_category_line.browse(cr,uid,li,context=context)
						prod_limit = limit.min_roof
				"""Check Future Product QTY """
				#future_prod_qty = 0.0
                		#future_qty = move_obj.read(cr, uid, check_move_ids, ['product_qty'], context=context)
                		#total_future_qty = []
                		#for future_record in future_qty:
                     		#	total_future_qty.append(future_record['product_qty'])
                		#future_prod_qty = sum(total_future_qty)
				'''if check_move_ids :
					for move in check_move_ids :
						move_line = move_obj.browse(cr,uid,move,context=context)
						future_prod_qty += move_line.product_qty'''
				"""Qty On Hand"""
            			location_id = line.order_id.shop_id.warehouse_id and line.order_id.shop_id.warehouse_id.lot_stock_id.id
            			#if location_id and self.check_access_rule_location(cr, uid, [location_id], 'read')==True:
				qty_on_hand = stock_location_obj._product_get(cr, uid, location_id, [line.product_id.id], context = context)[line.product_id.id]
				"""Avaiable Qty = QTY on hand - Future product QTY"""
				avaiable = qty_on_hand
				"""Conditions : """
				#if prod_limit == 0.0 or prod_limit == False :
					#raise osv.except_osv(_('Error'), _('Your Product Qty have no limit insert please contact adminstrator\n %s \n Order id %s')% (line.product_id.name,line.order_id.name))
				if avaiable <= 0.0 or avaiable < prod_limit :
					raise osv.except_osv(_('Error'), _('Your Product Qty is reach the limit contact adminstrator\n %s \n Order id %s')% (line.product_id.name,line.order_id.name))
				if avaiable < line.product_uos_qty :
					raise osv.except_osv(_('Error'), _('Your Product Qty avaiable is %s contact adminstrator or change order QTY\n %s \n Order id %s')% (avaiable,line.product_id.name ,line.order_id.name))
		#self._check_quantity(cr, uid, ids, context=context)
		if order.payment_type != 'installment' :
			if order.payment_type == 'up_cash' :
		    		start_loan_date = ''
		    		if order.category_id.create_month :
					start_loan_date = order.loan_date
		    		else :
					start_loan_date = order.date_order
				#last of the month
				date_string = datetime.strptime(start_loan_date,'%Y-%m-%d')
				if date_string.month < 12:
            	    			next_month = date(year=date_string.year, month=date_string.month+1, day=1)
				else:
            	    			next_month = date(year=date_string.year+1, month=1, day=1)
            			last_day = next_month - timedelta(days=1)
		        	last_day = datetime.strftime (last_day,'%Y-%m-%d')
                    		current_salary = payroll_obj.current_salary_status(cr, uid,ids, order.employee_id, last_day)
                		balance = current_salary.get('balance',0.0)
	        		if order.employee_id.salary_suspend == True:
					raise osv.except_osv(_('Error!'),_('this employe have suspend payroll salary \n %s.')% (order.name))
            				self.write(cr, uid, ids, {'state':'cancel','print_order':False}, context=context)
	        		if order.payment_type =='up_cash' and balance<order.amount_total:
					raise osv.except_osv(_('Error!'),_('this employe is not enough balance \n %s.')% (order.name))
				if order.payment_type =='up_cash':
					if order.create_done == False:
             					if order.company_id.loan_id.id :
				#up_front = 0
							cr.execute ("""select l.period as period , sum (l.installment_value * l.product_uom_qty) installment 
									from sale_order_line l
                                                			left join sale_order so on (so.id = l.order_id)  
									where l.order_id = '%s'
									group by l.period """%order.id)
        						result = cr.dictfetchall()
							for record in result :
								loan_amount = 0.0
								start_loan_date = ''
								if order.category_id.create_month :
									start_loan_date = order.loan_date
								else :
									start_loan_date = order.date_order
								#loan_amount = record['price'] - record['front']
								loan_id = loan_obj.create(cr, uid, {'employee_id':order.employee_id.id,\
	                                				'refund_from':'salary',\
									'loan_id':order.company_id.loan_id.id ,\
					 				'total_installment':record['period'],\
									'loan_amount': record['installment'] * record['period'] ,
									'salary_refund':record['installment'],
			   						'addendum_refund' : 1,
			   						'state':'draft',
									'sale_order_id':order.id,
									'start_date':start_loan_date,
									'comments':'أقساط المؤسسة التعاونية',
			   						'addendum_install_no' : 1 , }, context)
                                        			wf_service = netsvc.LocalService("workflow")
                                        			wf_service.trg_validate(uid , 'hr.employee.loan' , loan_id , 'cooperative_loan_paid' ,cr )
                                        			loan_obj.write(cr ,uid , loan_id , {'state' : 'paid'},context = context)
                                        		        self.write(cr ,uid , order.id , {'start_date':start_loan_date},context = context)

             					else:
             						raise osv.except_osv(_('Error!'),_('No loan created, Please creat a loan in the company form in Hr setting page .'))
             		
			picking_id = ''
       			for line in order.order_line:
            			"""if line.state == 'done':
                			continue"""
            			if line.product_id and line.order_id.create_done == False:
                			if line.product_id.type in ('product', 'consu'):
                    				if not picking_id:
                        				picking_id = picking_obj.create(cr, uid, self._prepare_order_picking(cr, uid, order, context=context))
                    			move_id = move_obj.create(cr, uid, self._prepare_order_line_move(cr, uid, order, line, picking_id, order.date_order, context=context))
        				self.write(cr, uid, ids, {'create_done':True}, context=context)
                u = self.pool.get('res.users').browse(self, cr, uid, ids).id
        	self.write(cr, uid, ids, {'state':'done','process_id':u,'print_order':False}, context=context)
		################################### update parner with qty roof 
       		"""for line in order.order_line:
					new_sell_qty = order.partner_id.sum_product_qty + line.product_uom_qty
                			self.pool.get('res.partner').write(cr,uid,[order.partner_id.id],{'sum_product_qty' : new_sell_qty })"""
		###############################################################
                

 
        return True

    def _prepare_order_line_move(self, cr, uid, order, line, picking_id, date_planned, context=None):
        location_id = order.shop_id.warehouse_id.lot_stock_id.id
        output_id = order.shop_id.warehouse_id.lot_output_id.id
        return {
            'name': '',
            'picking_id': picking_id,
            'product_id': line.product_id.id,
            'date': date_planned,
            'date_expected': date_planned,
            'product_qty': line.product_uom_qty,
            'product_uom': line.product_uom.id,
            'product_uos_qty': (line.product_uos and line.product_uos_qty) or line.product_uom_qty,
            'product_uos': (line.product_uos and line.product_uos.id)\
                    or line.product_uom.id,
            'product_packaging': line.product_packaging.id,
            'partner_id': line.address_allotment_id.id or order.partner_shipping_id.id,
            'location_id': location_id,
            'location_dest_id': output_id,
            'sale_line_id': line.id,
            'tracking_id': False,
            'state': 'draft',
            #'state': 'waiting',
            'company_id': order.company_id.id,
            'price_unit': line.product_id.standard_price or 0.0
        }

    def _prepare_order_picking(self, cr, uid, order, context=None):
        pick_name = self.pool.get('ir.sequence').get(cr, uid, 'stock.picking.out')
        return {
            'name': pick_name,
            'origin': order.name,
            'date': self.date_to_datetime(cr, uid, order.date_order, context),
            'type': 'out',
            'state': 'draft',
            'move_type': order.picking_policy,
            'sale_id': order.id,
	    'stock_journal_id':18,
            'partner_id': order.partner_shipping_id.id,
            'note': order.note,
            'invoice_state': (order.order_policy=='picking' and '2binvoiced') or 'none',
            'company_id': order.company_id.id,
        }




    def check_access_rule_location(self, cr, uid, ids, operation, context=None):
        """
        Verifies that the operation given by ``operation`` is allowed for the user
        according to ir.rules in a location.

        @param operation: one of ``write``, ``unlink``
        @return: None if the operation is allowed
        """
        where_clause, where_params, tables = self.pool.get('ir.rule').domain_get(cr, uid, 'stock.location', operation, context=context)
        if where_clause:
            where_clause = ' and ' + ' and '.join(where_clause)
            for sub_ids in cr.split_for_in_conditions(ids):
                cr.execute('SELECT ' + 'stock_location' + '.id FROM ' + ','.join(tables) +
                           ' WHERE ' + 'stock_location' + '.id IN %s' + where_clause,
                           [sub_ids] + where_params)
                if cr.rowcount != len(sub_ids):
                    return False
        return True

class res_company(osv.Model):
    _inherit = "res.company"
    """Inherits res.company to add feild for accounting configuration for admin affairs
    """
    _columns = {
              
    	'loan_id': fields.many2one('hr.loan', 'loan'),
    }

class hr_employee(osv.Model):

    _inherit = "hr.employee"

    def name_search(self, cr, user, name, args=None, operator='ilike', context=None, limit=100):
        if not args:
            args = []
        ids = self.search(cr, user, [('otherid', operator, name)]+ args, limit=limit, context=context)
        ids += self.search(cr, user, [('emp_code', operator, name)]+ args, limit=limit, context=context)
        ids += self.search(cr, user, [('name_related', operator, name)]+ args, limit=limit, context=context)
        return self.name_get(cr, user, ids, context)


