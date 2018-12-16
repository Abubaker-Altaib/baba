# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

from openerp.osv import fields, osv
from openerp.tools.amount_to_text_en import amount_to_text
from base_custom.amount_to_text_ar import amount_to_text as amount_to_text_ar

class account_check_print_wizard(osv.osv_memory):

    _inherit = "account.check.print.wizard"
    
    def check_payment(self, cr, uid, ids, context=None):
        res= super(account_check_print_wizard, self).check_payment(cr, uid, ids, context)
        self._amount_to_word(cr, uid, ids, context)
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
                ###################################################
