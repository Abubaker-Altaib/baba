# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

from openerp.tools.translate import _
from openerp.osv import fields, osv
import decimal_precision as dp
from openerp.tools.amount_to_text_en import amount_to_text
from base_custom.amount_to_text_ar import amount_to_text as amount_to_text_ar


class res_company(osv.Model):
    """ inherit company model to add configuration for the ratification journal field """
    _inherit = "res.company"

    _columns = {
        'vice_max_amount':fields.float('Vice manager amount',digits_compute=dp.get_precision('Account')),
        'gen_max_amount':fields.float('General manager Amount',digits_compute=dp.get_precision('Account')),
    }


class account_voucher(osv.Model):
    """Inherit voucher object to:
        * Add department field, purpose, ratification for ratification
        * Add ratification to the selection of the field type
        * Change voucher workflow
    """

    _inherit = 'account.voucher'
    _columns = {
	    'department_id':fields.many2one('hr.department', 'Department',readonly=True, 
                                        states={'draft':[('readonly',False)]}),
                                        
        'account_id':fields.many2one('account.account', 'Account', readonly=True,
                                     states={'draft':[('readonly',False)], 'approve':[('readonly',False)]}),
                                             
        'type':fields.selection([('sale','Sale'),('purchase','Purchase'),('payment','Payment'),('receipt','Receipt'),
                                 ('ratification','Ratification'),('pur_rat','Pur_Rat'),],'Default Type', 
                                 readonly=True, states={'draft':[('readonly',False)]}),

        'state':fields.selection([('draft','Draft'),('precomplete','Unit Complete'),('preclose','Unit Close'),('precomplete1','Unit Complete1'),('precomplete2','Unit Complete2'),('precomplete3','Unit Complete3'),('precomplete4','Unit Complete4'),('precomplete5','Unit Complete5'),('precomplete6','Unit Complete6'),('prepost','Department Post'),('preapprove','Finantial Approve'),('complete','completed'),
('approve','Approved'),('close','Closed'),('posted','Posted'),('paid','Paid'),('approved','Approved Budget'),('cancel','Cancel'),('reversed','Reversed'),('no_approve','Budget Not Approved')], 'State', readonly=True, size=32),
        
        'ratification': fields.boolean('Is Ratification?', required=False),
	    'purpose':fields.many2one('account.ratification.purpose', 'Purpose'),    
        'partner_id':fields.many2one('res.partner', 'Partner', change_default=1),      
        'journal_id':fields.many2one('account.journal', 'Journal', required=True),                              
        'pay_now':fields.selection([('pay_now','Pay Directly'), ('pay_later','Pay Later or Group Funds'),
                         ],'Payment', select=True),
        'account_id':fields.many2one('account.account', 'Account', required=False),
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
    def pre_complete1(self, cr, uid, ids, context={}):
        """
        Workflow function change ratification state to 'precomplete', 
        if it's amount is greater than Zero or raising an exception 
        @return: boolean True    
        """
        for voucher in self.browse(cr, uid, ids, context=context):
            if voucher.amount > 0.0:
	            self.write(cr, uid, ids, {'state': 'precomplete1'}, context=context)
            else:
                raise osv.except_osv(_('Error!'), _('The amount is less than zero!'))
        return True

    def pre_complete2(self, cr, uid, ids, context={}):
        """
        Workflow function change ratification state to 'precomplete', 
        if it's amount is greater than Zero or raising an exception 
        @return: boolean True    
        """
        for voucher in self.browse(cr, uid, ids, context=context):
            if voucher.amount > 0.0:
	            self.write(cr, uid, ids, {'state': 'precomplete2'}, context=context)
            else:
                raise osv.except_osv(_('Error!'), _('The amount is less than zero!'))
        return True

    def pre_complete3(self, cr, uid, ids, context={}):
        """
        Workflow function change ratification state to 'precomplete', 
        if it's amount is greater than Zero or raising an exception 
        @return: boolean True    
        """
        for voucher in self.browse(cr, uid, ids, context=context):
            if voucher.amount > 0.0:
	            self.write(cr, uid, ids, {'state': 'precomplete3'}, context=context)
            else:
                raise osv.except_osv(_('Error!'), _('The amount is less than zero!'))
        return True

    def pre_complete4(self, cr, uid, ids, context={}):
        """
        Workflow function change ratification state to 'precomplete', 
        if it's amount is greater than Zero or raising an exception 
        @return: boolean True    
        """
        for voucher in self.browse(cr, uid, ids, context=context):
            if voucher.amount > 0.0:
	            self.write(cr, uid, ids, {'state': 'precomplete4'}, context=context)
            else:
                raise osv.except_osv(_('Error!'), _('The amount is less than zero!'))
        return True

    def pre_complete5(self, cr, uid, ids, context={}):
        """
        Workflow function change ratification state to 'precomplete', 
        if it's amount is greater than Zero or raising an exception 
        @return: boolean True    
        """
        for voucher in self.browse(cr, uid, ids, context=context):
            if voucher.amount > 0.0:
	            self.write(cr, uid, ids, {'state': 'precomplete5'}, context=context)
            else:
                raise osv.except_osv(_('Error!'), _('The amount is less than zero!'))
        return True
    def router(self, cr, uid, ids, context={}):
        """
        Workflow function change ratification state to 'precomplete', 
        if it's amount is greater than Zero or raising an exception 
        @return: boolean True    
        """
        return True

    def pre_complete6(self, cr, uid, ids, context={}):
        """
        Workflow function change ratification state to 'precomplete', 
        if it's amount is greater than Zero or raising an exception 
        @return: boolean True    
        """
        for voucher in self.browse(cr, uid, ids, context=context):
            if voucher.amount > 0.0:
	            self.write(cr, uid, ids, {'state': 'precomplete6'}, context=context)
            else:
                raise osv.except_osv(_('Error!'), _('The amount is less than zero!'))
        return True

    def test_wkf(self, cr, uid, ids,mode, context=None):

        assert mode in ('gmanager', 'vmanager','other'), _("invalid mode for test_state")
        gmanager=True
        vmanager=True
        other=True
        for voucher in self.browse(cr, uid, ids):
            if mode=='gmanager':
               if voucher.amount>=voucher.company_id.gen_max_amount:
                  return True 
               else:
                 return False
            elif mode=='vmanager':
               if voucher.amount<voucher.company_id.gen_max_amount and voucher.amount>=voucher.company_id.vice_max_amount:
                  return True 
               else:
                 return False
            elif mode=='other' :
               if voucher.amount<voucher.company_id.vice_max_amount :
                  return True
               return False   

                 




 

  
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
