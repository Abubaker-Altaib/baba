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
import logging
_logger = logging.getLogger(__name__)



class ireq_m_inhiret(osv.osv):
    _inherit = 'ireq.m'


    USERS_SELECTION = [
        ('admin', 'Supply Department'),
        ('tech', 'Techncial Services Department'),
        ('arms', 'Arms Department'),
                     ]




    TYPE_SELECTION = [
        ('internal', 'Internal Purchase'),
        ('foreign', 'Foreign Purchase'),
    ]
    STATE_SELECTION = [
         ('draft', 'Draft Request'),
         ('in_progress','In Progress'),
         ('completed','Completed'),
         ('closed','Closed'),
         ('in_progress_quote','In Progress Quote'),
         ('wait_confirmed','Wait Confirmed'),
         ('completed_quote','Completed Quote'),
         ('closed_quote','Closed Quote'),
         ('in_progress_fin_request','In Progress Financial Request'),
         ('completed_fin_request','Completed Financial Request'),
         ('closed_fin_request','Closed Financial Request'),
         ('done','Done'),
         ('cancel', 'Cancelled')]
    
    
    def next_by_id(self, cr, uid, sequence_id, context=None):
        """
        Override to edit Sequences to read company from res_user.
 
        @param sequence_id: sequence id 
        @return: object _next method
        """
        seq_obj = self.pool.get('ir.sequence')
        user_obj = self.pool.get('res.users')
        self.check_access_rights(cr, uid, 'read')
        company_id = user_obj.browse(cr, uid, uid).company_id.id 
        ids = seq_obj.search(cr, uid, ['&',('id','=',
sequence_id),('company_id','in',[company_id, False])])
        return seq_obj._next(cr, uid, ids, context)
 
    def next_by_code(self, cr, uid, sequence_code,executing_agency, context=None):
        """
        Gets the sequence by code.
 
        @param sequence_code: Code of the sequence by which we'll fetch the sequence
        @param context: standard dictionary
        @return: object _next method
        """
        seq_obj = self.pool.get('ir.sequence')
        user_obj = self.pool.get('res.users')
        self.check_access_rights(cr, uid, 'read')
        #Get the company only from user

        company_id = user_obj.browse(cr, uid, uid).company_id.id 
        ids = seq_obj.search(cr, uid, ['&',('code','=',
sequence_code),('company_id','in',[company_id,False]),('executing_agency','=', executing_agency)])

        return seq_obj._next(cr, uid, ids, context)
     
 
    def get_id(self, cr, uid, executing_agency,  sequence_code_or_id,code_or_id='id', context=None):
        """ 
        Draw an interpolated string using the specified sequence.
        The sequence to use is specified by the ``sequence_code_or_id``
        argument, which can be a code or an id (as controlled by the
        ``code_or_id`` argument. This method is deprecated.
              
        @param sequence_code_or_id: code or id of the sequence
        @param code_or_id: type of the sequence
        @return: object next_by_code or next_by_id method
        """
        _logger.debug("ir_sequence.get() and ir_sequence.get_id() are deprecated. "
            "Please use ir_sequence.next_by_code() or ir_sequence.next_by_id().")

        if code_or_id == 'id':
            return self.next_by_id(cr, uid, sequence_code_or_id, executing_agency,context)
        else:
            return self.next_by_code(cr, uid, sequence_code_or_id, executing_agency,context)
 
    def get(self, cr, uid, code,executing_agency, context=None):
        """ 
        Draw an interpolated string using the specified sequence.
        The sequence to use is specified by its code. This method is
        deprecated.
 
        @param code: code of the sequence
        @return: object get_id method   
        """

        return self.get_id(cr, uid, executing_agency,  code, 'code', context)
 
    def create(self, cr, user, vals, context=None):
        """ 
        Override to edit the name field by a new sequence. 
 
        @return: new object id 
        """
        if ('name' not in vals) or (vals.get('name')=='/'):
            seq_obj_name =  'ireq.m'
            if vals.get('ir_ref') != None :
               order_id = self.pool.get('exchange.order').search(cr , user , [('name' , '=' , vals['ir_ref'])])
               for rec in self.pool.get('exchange.order').browse(cr,user,order_id):
                   executing_agency = rec.executing_agency
            else :
                   executing_agency= vals['executing_agency']
            vals['name'] = self.pool.get('ireq.m').get(cr, user, seq_obj_name , executing_agency)
        new_id = super(ireq_m_inhiret, self).create(cr, user, vals, context)
        return new_id 

#Model definition


    _columns = {

                'state': fields.selection(STATE_SELECTION, 'Status', readonly=True, select=True),
                'company_id': fields.many2one('res.company','Company',required=True,readonly=True),
                'department_id':fields.many2one('hr.department', 'Department',readonly=True, states={'draft':[('readonly',False)]}, ),
                'ir_date': fields.date('Request Date', readonly=True, states={'draft':[('readonly',False)]}),
                'cat_id':fields.many2one('product.category', 'Category',readonly=True, states={'draft':[('readonly',False)]} ),
                'purpose': fields.selection([('store', 'Feed Store')],'Purpose',readonly=True, states={'draft':[('readonly',False)]}),
                'pro_ids':fields.one2many('ireq.products', 'pr_rq_id' , 'Products',readonly=True, states={'draft':[('readonly',False)],'in_progress':[('readonly',False)],'completed':[('readonly',False)]} ),
                'q_ids':fields.one2many('pur.quote', 'pq_ir_ref' ,'Quotes',readonly=True, states={'in_progress_quote':[('readonly',False)]}),
                'r1':fields.boolean('Good delivery', readonly=True, states={'completed_quote':[('readonly',False)]}),
                'r2':fields.boolean('High quality',readonly=True, states={'completed_quote':[('readonly',False)]},),
                'r3':fields.boolean('Good price',readonly=True, states={'completed_quote':[('readonly',False)]}, ),
                'r4': fields.char('Other Reasons', size=256 ,readonly=True, states={'completed_quote':[('readonly',False)]},),
                'purchase_type':fields.selection(TYPE_SELECTION, 'Purchase Type', readonly=True, states={'closed':[('readonly',False)]},select=True),
                'executing_agency':fields.selection(USERS_SELECTION, 'Executing Agency',select=True,help='Department Which this request will executed it'),
                'purchase_purposes': fields.char('Purchase purposes', size=256 ,readonly=True, states={'draft':[('readonly',False)]},),

                }

    _defaults = {
                 
          'executing_agency' : lambda self, cr, uid, c: self.pool.get('res.users').browse(cr, uid, uid, context=c).belong_to ,

                }






    


    def in_progress(self,cr,uid,ids,context=None):
        """ 
        Workflow function checks the products lines, category and change order state to confirmed_d.

	    @return: True 
        """
        if [ir for ir in self.browse(cr, uid, ids) if ir.pro_ids ]:
            self.write(cr, uid, ids, {'state':'in_progress'}, context=context)
        else:
            raise osv.except_osv( _('No Products !'), _('Please make sure you fill the products ..'))
        for req in self.browse(cr, uid, ids):
            for line in req.pro_ids:
                if line.product_qty == 0.0:
                    raise osv.except_osv( _('Zero Products quantity !'), _('Please make sure you fill the products quantity..'))
        return True

    def completed(self, cr, uid, ids, context=None):
        """ 
        Workflow function changes order state to completed.
        
        @return: True 
        """
        self.write(cr, uid, ids, {'state':'completed'}, context=context)       
        return True

    def closed(self, cr, uid, ids, context=None):
        """ 
        Workflow function changes order state to closed.
        
        @return: True 
        """
        self.write(cr, uid, ids, {'state':'closed'}, context=context)       
        return True

    def in_progress_quote(self, cr, uid, ids, context=None):
        """ 
        Workflow function changes order state to in_progress_quote.
        
        @return: True 
        """
        self.write(cr, uid, ids, {'state':'in_progress_quote'}, context=context)       
        return True

    def completed_quote(self, cr, uid, ids, context=None):
        """ 
        Workflow function changes order state to completed_quote.
        
        @return: True 
        """
        self.write(cr, uid, ids, {'state':'completed_quote'}, context=context)       
        return True

    def closed_quote(self, cr, uid, ids, context=None):
        """ 
        Workflow function changes order state to closed_quote.
        
        @return: True 
        """
        self.write(cr, uid, ids, {'state':'closed_quote'}, context=context)       
        return True
    
    
    def back_to_quotes(self, cr ,uid ,ids , context=None):
        
        
        """ This Function For Return Request to Quotation Entry State When Missing something """
        
        wf_service = netsvc.LocalService("workflow")
        wf_service.trg_validate(uid , 'ireq.m' ,ids[0] , 'back_to_quotes' ,cr )
        self.write(cr ,uid ,ids , {'state' : 'in_progress_quote'},context = context)
        
        quote_obj = self.pool.get('pur.quote')
        
        for rec in self.browse(cr , uid ,ids) :
            for quote in rec.q_ids:
                if not len([quote.id]):
                   return False
                quote_obj.write(cr, uid, quote.id , {'state':'draft'}, context=context)
                wf_service = netsvc.LocalService("workflow")
                for s_id in [quote.id]:
                    # Deleting the existing instance of workflow for PO
                    wf_service.trg_delete(uid, 'pur.quote', s_id, cr)            
                    wf_service.trg_create(uid, 'pur.quote', s_id, cr) 
        
        
        return True
        
        
    def in_progress_fin_request(self, cr, uid, ids, context=None):
        """ 
        Workflow function changes order state to in_progress_quote.
        
        @return: True 
        """
        self.write(cr, uid, ids, {'state':'in_progress_fin_request'}, context=context)       
        return True

    def completed_fin_request(self, cr, uid, ids, context=None):
        """ 
        Workflow function changes order state to completed_quote.
        
        @return: True 
        """
        voucher_obj = self.pool.get('account.voucher')
        voucher_line_obj = self.pool.get('account.voucher.line')
        for order in self.browse(cr,uid,ids):
            for quote in order.q_ids:
                if quote.state == 'done' :
                   voucher_id = voucher_obj.create(cr, uid, {
                                        'amount': quote.amount_total,
                                        'type': 'purchase',
                                        'date': time.strftime('%Y-%m-%d'),
                                        'partner_id': quote.supplier_id.id , 
                                        'account_id': quote.supplier_id.property_account_payable.id , 
                                        'journal_id': order.company_id.purchase_foreign_journal.id,
                                        'reference':  order.name  ,
                                        'state': 'draft',
                                        'name': order.purchase_purposes })
               
                   for line in quote.pq_pro_ids :
                       if order.multi == 'multiple' :
                          if line.chosen == True :
                             vocher_line_id = voucher_line_obj.create(cr, uid, {
                                                    'amount': line.price_subtotal ,
                                                    'voucher_id': voucher_id,
                                                    'type': 'dr',
                                                    'account_id': line.product_id.product_tmpl_id.categ_id.property_account_expense_categ.id,
                                                    'name': line.product_id.name or '',
                                                     })
                               
                       else:
                            vocher_line_id = voucher_line_obj.create(cr, uid, {
                                                    'amount': line.price_subtotal ,
                                                    'voucher_id': voucher_id,
                                                    'type': 'dr',
                                                    'account_id': line.product_id.product_tmpl_id.categ_id.property_account_expense_categ.id,
                                                    'name': line.product_id.name or '',
                                                     })  
                   voucher_obj.compute_tax(cr, uid, [voucher_id], context=context)
        self.write(cr, uid, ids, {'state':'completed_fin_request'}, context=context)       
        return True

    def closed_fin_request(self, cr, uid, ids, context=None):
        """ 
        Workflow function changes order state to closed_quote.
        
        @return: True 
        """
        self.write(cr, uid, ids, {'state':'closed_fin_request'}, context=context)       
        return True
    def onchange_category_check_products_line(self,cr,uid,ids,cat_id,pro_ids,context=None):
        """
        This function overwrite the main function in purchase custom module to make the request contains different products categories .

        @param cat_id: product category id 
        @param pro_ids: product id 
        """
        super(exchange_order,self).onchange_category_check_products_line(cr,uid,ids,cat_id,pro_ids,context)
        
        return {}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
