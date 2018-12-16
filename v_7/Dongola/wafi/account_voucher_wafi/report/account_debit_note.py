# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

from report import report_sxw
from openerp.tools.amount_to_text_en import amount_to_text
from base_custom.amount_to_text_ar import amount_to_text as amount_to_text_ar

class report_debit_note(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(report_debit_note, self).__init__(cr, uid, name, context)
        self.context = context
        self.localcontext.update({
            'get_lines':self.get_lines,
            'convert':self.convert,
        })
 
    def convert(self, amount, currency_id):
        amount_in_word = ''
        currency_format =  self.pool.get('res.users').browse(self.cr, self.uid, self.uid).company_id.currency_format 
        if currency_format=='ar':
            if currency_id:
                currency = self.pool.get('res.currency').read(self.cr, self.uid, currency_id, ['units_name','cents_name'], context=self.context)
                amount_in_word = amount_to_text_ar(amount, currency_format, currency['units_name'], currency['cents_name'])
            else:
                amount_in_word = amount_to_text_ar(amount, currency_format)
        else: 
            amount_in_word = amount_to_text(amount)
        return amount_in_word
          
    def get_lines(self, voucher):
        result = []
        if voucher.type in ('payment','receipt'):
            type = voucher.line_ids and voucher.line_ids[0].type or False
            for move in voucher.line_ids:
                    res = {'pname': move.partner_id.name, 'ref': 'Agst Ref'+" "+str(move.name),
                           'aname': move.account_id.name,'name': move.name,'account_id': move.account_id, 'amount':                         move.amount,'account_analytic_id':move.account_analytic_id}
                    result.append(res)
        else:
            type = voucher.line_ids and voucher.line_ids[0].type or False
            for move in voucher.line_ids:
                    res = {'ref':  move.name, 'name': move.name, 'account_id': move.account_id.name, 'amount': move.amount,'account_analytic_id':move.account_analytic_id.name}
                    result.append(res)
        return result


report_sxw.report_sxw('report.debit.note', 'account.voucher', 'addons/account_voucher_wafi/report/account_debit_note.rml', parser=report_debit_note,header='external' )
report_sxw.report_sxw('report.petty.cash', 'account.voucher', 'addons/account_voucher_wafi/report/account_petty_cash.rml', parser=report_debit_note,header='external' )

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
