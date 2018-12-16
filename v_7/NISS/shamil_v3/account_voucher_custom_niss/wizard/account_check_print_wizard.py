# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

from openerp.osv import fields, osv
from openerp.tools.translate import _
from openerp.tools.amount_to_text_en import amount_to_text
from base_custom.amount_to_text_ar import amount_to_text as amount_to_text_ar

class account_check_print_wizard(osv.osv_memory):

    _inherit = "account.check.print.wizard"
    
    def check_payment(self, cr, uid, ids, context=None):
        res= super(account_check_print_wizard, self).check_payment(cr, uid, ids, context)
        self._amount_to_word(cr, uid, ids, context)
        #self._check_range(cr, uid, ids, context)
        return res 

    def print_report(self, cr, uid, ids, context=None):
        self._amount_to_word(cr, uid, ids, context)
        return super(account_check_print_wizard, self).print_report(cr, uid, ids, context)
    
    def _amount_to_word(self, cr, uid, ids, context=None):
        voucher_obj = self.pool.get('account.voucher')
        voucher_id =self._get_voucher_ids(cr, uid, context)
        if voucher_id :
            voucher =  voucher_obj.browse(cr,uid , voucher_id,context)
            currency_format = 'ar'
            currency_id = voucher.currency_id and voucher.currency_id.id
            if currency_id:
                currency = self.pool.get('res.currency').read(cr, uid, currency_id, ['units_name', 'cents_name'], context=context)
                amount_in_word = amount_to_text_ar(voucher.amount, currency_format, currency.get('units_name',''), currency.get('cents_name',''))
            else:
                amount_in_word = amount_to_text_ar(voucher.amount, currency_format)
            voucher_obj.write(cr, uid, [voucher.id],{'amount_in_word':amount_in_word})
        return True

    def _check_range(self, cr, uid, ids, context):
        """ 
        change checks_number field when changing first_number or last_number fields.
        @param first_number: First Number in range, last_number: Last Number in range
        @return: Dictionary of values of checks_number 
        """
        data = self.browse(cr, uid, ids, context=context)[0]
        voucher_obj = self.pool.get('account.voucher')
        check_range_obj = self.pool.get('check.range')
        voucher_id = data.payment_id and data.payment_id.id or None
        in_range = False
        new_no = int(data.new_no)
        print">>>>>>>",new_no,">>>>>>>>>>>",voucher_id,">>>>",data.payment_id and data.payment_id.id
        if voucher_id and new_no:

            journal_id = voucher_obj.browse(cr, uid ,voucher_id, context).pay_journal_id.id
            print"SSS",journal_id
            check_range_ids = check_range_obj.search(cr, uid, [('journal_id','=',journal_id),('archive','=',False)], context=context)
            print">>>>>>>>>",check_range_ids
            for check_range in check_range_obj.browse(cr, uid, check_range_ids, context):
                print">>>>>>", (new_no in range(check_range.first_number, check_range.last_number + 1))
                if new_no in range(check_range.first_number, check_range.last_number + 1):
                    in_range = True
                    break
        if not in_range:
            raise osv.except_osv(_('Error'),_('This check number is not register.'))
          
        return in_range

         

            
            




                ###################################################
