# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

from openerp.tools.translate import _
from openerp.osv import fields, osv
from openerp.tools.amount_to_text_en import amount_to_text
from base_custom.amount_to_text_ar import amount_to_text as amount_to_text_ar

class account_ratification_purpose(osv.osv):
   """ Object for the ratifcation pupose to allow user to configure the account 
        of select ratfication
   """

   _name = 'account.ratification.purpose'
   _columns = {
             'name':fields.char('Name',size=256,required=True),
             'code':fields.char('Code',size=256),
             #'type':fields.selection([('central', 'Central'),('decentralized', 'Decentralized'),], ' Type'),
             'account_id':fields.many2one('account.account', 'Account'),
              }


class account_budget_confirmation(osv.Model):
    """Inherit budget confirmation object to add to the type 'ratification'
    """

    _inherit = 'account.budget.confirmation'

    _columns = {
    
            'type' : fields.selection([('stock_in','Stock IN'),('stock_out','Stock OUT'),('purchase','Purchase'),
                                   ('ratification','Ratification'),('other','Others')], 'Type'),
    }         
    '''def budget_complete(self, cr, uid, ids, context=None):
        """
        Inherited budget_complete methond in Budget Confirmation class,
        if confirmation type is not ratification all confirmation details 
        even partner_id must be fill before complete confirmation 
        """
        for confirm in self.browse(cr, uid, ids, context=context):
            if not(confirm.general_account_id and confirm.analytic_account_id and confirm.period_id) and \
                  (not confirm.partner_id) and confirm.type!= 'ratification':
                    return False
        return super(account_budget_confirmation, self).budget_complete(cr, uid, ids, context=context)'''
    

class res_company(osv.Model):
    """ inherit company model to add configuration for the ratification journal field """
    _inherit = "res.company"

    _columns = {
        'ratification_journal_id':fields.many2one('account.journal', 'Ratification Journal',
                         domain="[('company_id','=',id),('type','=','purchase')]"),
    }

class account_voucher(osv.Model):
    """Inherit voucher object to:
        * Add department field, purpose, ratification for ratification
        * Add ratification to the selection of the field type
        * Change voucher workflow
    """

    def create(self, cr, uid, vals, context={}):
        if vals.get('ratification',False):
           res = self.pool.get('res.company').browse(cr, uid, uid, context=context).ratification_journal_id
           if res:vals['journal_id'] =res.id 
        return super(account_voucher,self).create(cr, uid, vals, context=context)

    def test_amount(self, cr, uid, ids, min_amount=0, max_amount=0, context=None):
        for voucher in self.browse(cr, uid, ids):
            if  min_amount <=  voucher.amount <= max_amount:
                return True
            return False


    _inherit = 'account.voucher'

    _columns = {
	    'department_id':fields.many2one('hr.department', 'Department',readonly=True, 
                                        states={'draft':[('readonly',False)]}),
                                        
        'account_id':fields.many2one('account.account', 'Account', readonly=True,
                                     states={'draft':[('readonly',False)], 'approve':[('readonly',False)]}),
                                             
        'type':fields.selection([('sale','Sale'),('purchase','Purchase'),('payment','Payment'),('receipt','Receipt'),
                                 ('ratification','Ratification'),('pur_rat','Pur_Rat'),],'Default Type', 
                                 readonly=True, states={'draft':[('readonly',False)]}),

        'state':fields.selection([('draft','Draft'),('precomplete','Unit Complete'),('preclose','Unit Close'),
                                  ('prepost','Department Post'),('preapprove','Finantial Approve'),('complete','Waiting for Budget Confirmation'),
                                  ('approve','Approved'),('close','Closed'),('posted','Posted'),('paid','Paid'),
                                    ('approved','Approved Budget'),
                                  ('cancel','Cancel'),('reversed','Reversed')], 'State', readonly=True, size=32),
        
        'ratification': fields.boolean('Is Ratification?', required=False),
	    'purpose':fields.many2one('account.ratification.purpose', 'Purpose'),    
        'partner_id':fields.many2one('res.partner', 'Partner', change_default=1),      
        'journal_id':fields.many2one('account.journal', 'Journal', required=True),                              
        'pay_now':fields.selection([('pay_now','Pay Directly'), ('pay_later','Pay Later or Group Funds'),
                         ],'Payment', select=True),
        'account_id':fields.many2one('account.account', 'Account', required=False),
    }

    _defaults = {
        'currency_id': lambda self,cr,uid,c: self._get_currency(cr, uid, c) or self.pool.get('res.company').browse(cr, uid, self.pool.get('res.company')._company_default_get(cr, uid, 'account.voucher',context=c)).currency_id.id,
    }

    def pre_complete(self, cr, uid, ids, context={}):
        """
        Workflow function change ratification state to 'precomplete', 
        if it's amount is greater than Zero or raising an exception 
        @return: boolean True    
        """
        for voucher in self.browse(cr, uid, ids, context=context):
            if voucher.amount > 0.0:
	            self.write(cr, uid, ids, {'state': 'precomplete'}, context=context)
            else:
                raise osv.except_osv(_('Error!'), _('The amount is less than zero!'))
        return True

    def pre_close(self, cr, uid, ids, context={}):
        """
        Workflow function change ratification state to 'preclose'.
        @return: boolean True    
        """
        self.write(cr, uid, ids, {'state': 'preclose'}, context=context)
        return True

    def pre_post(self, cr, uid, ids, context={}):
        """
        Workflow function change ratification state to 'prepost'.
        @return: boolean True    
        """
        self.write(cr, uid, ids, {'state': 'prepost'}, context=context)
        return True

    def pre_approve(self, cr, uid, ids, context={}):
        """
        Workflow function create a Voucher Line and Budget Confirmation for each
        line has analytic account, then changes ratification state to "preapprove" 
        if it's lines has budget_confirm_id or make it "approve" directly
        @return: boolean True    
        """
    	for voucher in self.browse(cr, uid, ids, context=context):
    	    if  not voucher.department_id.analytic_account_id:
    	        raise osv.except_osv(_('Configration Check!'), _("Please add cost center for your department!"))
    	    periods = self.pool.get('account.period').search(cr, uid, [('date_start','<=',voucher.date),('date_stop','>=',voucher.date),('company_id','=',voucher.company_id.id)], context=context)


            res=0.0
            if voucher.purpose:
                if not voucher.purpose.account_id: raise osv.except_osv(_('Warning!'), _('Please configure account for this purpose!')) 
                voucher_line = {
            		'voucher_id': voucher.id,
            		'partner_id': voucher.partner_id.id,
            		'untax_amount': voucher.amount,
            		'amount': voucher.amount,
                    'name': voucher.narration,
            		'type': 'dr',
            		'account_analytic_id': voucher.department_id.analytic_account_id and voucher.department_id.analytic_account_id.id,
                    'account_id': voucher.purpose.account_id.id,
        	    }
                new_amount =  res and res or voucher.amount     
                voucher_line.update({'amount':new_amount,'untax_amount':new_amount})
    	        if voucher.line_ids :
                   for line in voucher.line_ids:
        		       self.pool.get('account.voucher.line').write(cr, uid, line.id,  {
                    		'voucher_id': voucher.id,
                    		'partner_id': voucher.partner_id.id,
                    		'untax_amount': res or line.amount,
                    		'amount': line.amount,
                            'name': voucher.narration,
                    		'type': 'dr',
                    		'account_analytic_id': line.account_analytic_id and line.account_analytic_id.id or voucher.department_id.analytic_account_id.id,
                            'account_id': voucher.purpose.account_id.id or line.account_id.id,
                	    }, context=context)
    	        else:

        		   new_voucher_line = self.pool.get('account.voucher.line').create(cr, uid, voucher_line, context=context)
                context.update({'purchase':True})
                self.create_budget_confirmation(cr, uid, [voucher.id], context)
    	self.write(cr, uid, ids,{'state': 'preapprove','type':'purchase','ratification':True}, context=context)
        #cxt = context.copy()
        #cxt.update({'type':'ratification'})
        if not super(account_voucher, self).create_budget_confirmation(cr, uid, ids, context=context):
            self.write(cr, uid, ids, {'state': 'approved'}, context=context)

    	'''self.write(cr, uid, ids, {'state': 'preapprove'})
        if not super(account_voucher, self).create_budget_confirmation(cr, uid, ids, context=context):
            self.write(cr, uid, ids, {'state': 'approve','type':'purchase','ratification':True}, context=context)'''
        return True

    def onchange_partner_id_ratification(self, cr, uid, ids, partner_id, journal_id, ttype, price, context={}):
        """
        This metthod call when changing Ratification amount or partner.
        @param int partner_id: Ratification record Partner,
        @param int journal_id: Ratification record Journal,
        @param char ttype: Ratification record type,
        @param float price: Ratification record amount,            
        @return: dictionary conatins amount_in_word value
        """
        ratification_journal = self.pool.get('res.company').browse(cr, uid, uid, context=context).ratification_journal_id
        default = {'value':{}}
        context.update({'type':'purchase'})
        default['value']['journal_id'] = ratification_journal.id and ratification_journal.id or self._get_journal(cr, uid, context=context)
        if partner_id and ttype == 'ratification':
            default['value']['account_id'] = self.pool.get('res.partner').browse(cr, uid, partner_id, context=context).property_account_payable.id
        amount = 'amount' in default['value'] and default['value']['amount'] or price
        currency_format =  self.pool.get('res.users').browse(cr, uid, uid, context=context).company_id.currency_format
        amount_in_word = currency_format=='ar' and amount_to_text_ar(amount, currency_format) or amount_to_text(amount)

        default['value'].update({'amount_in_word':amount_in_word})
        if journal_id:#TODO:
            allow_check_writing = self.pool.get('account.journal').browse(cr, uid, journal_id, context=context).allow_check_writing
            default['value'].update({'allow_check':allow_check_writing}) 
        return default

    def _required_line_id(self, cr, uid, ids, context=None):
        """
        This metthod override required_line_id in account_voucher_custom module to change the state 
        constraint from draft to posted .
            
        @return: Boolean True if the voucher lines is found
        """
        if self.search(cr, uid,[('id', 'in', ids),('line_ids', '=', False),('state', '=', 'posted'),('type', '<>', 'payment')], context=context):
            return False
        return True

    _constraints = [
        (_required_line_id, "Operation is not completed, Accounts & amounts details are missing!", ['line_ids']),    
      ]

class account_voucher_line(osv.Model):
    """ Inherit voucher line object to make the fiel account_id not required
    """

    _inherit = 'account.voucher.line'

    _columns = {
        'account_id':fields.many2one('account.account','Account'),
        
       #'state': fields.function(_test_state, method=True, type='char', size=64, string='Budget Confirmation State', 
       #                          store= {'account.budget.confirmation': (lambda self, cr, uid, ids, c={}: ids, ['state'], 10)}),
    }
    '''def _test_state(self, cr, uid, ids, name, args, context={}):
    	res = super(account_voucher_line, self)._test_state(cr, uid, ids, name, args, context=context)
    	for line in self.pool.get('account.voucher.line').browse(cr, uid, res.keys(), context=context):
    	    if line.voucher_id.state == 'approve' and line.voucher_id.type == 'ratification':
                self.pool.get('account.voucher').write(cr, uid, line.voucher_id.id, {'type':'purchase', 'ratification':True}, context=context)
    	    self.write(cr, uid, line.id, {'account_id':line.budget_confirm_id.general_account_id.id, 
                                          'account_analytic_id':line.budget_confirm_id.analytic_account_id.id}, context=context)
    	return res'''





# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
