# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

import netsvc
from openerp.osv import fields, osv, orm
from openerp.tools.translate import _
from openerp.tools.amount_to_text_en import amount_to_text
from base_custom.amount_to_text_ar import amount_to_text as amount_to_text_ar

check_layout_report = {
    'top' : 'account.print.check.top',
    'middle' : 'account.print.check.middle',
    'bottom' : 'account.print.check.bottom',
}

class account_voucher(osv.Model):
    """
    Inherit voucher object to add fields and method that let object to
    support printing checks.
    """

    _inherit = 'account.voucher'

    _columns = {
        'amount_in_word' : fields.char("Amount in word" , size=128, readonly=True, states={'draft':[('readonly', False)]}),
        'allow_check' : fields.boolean('Allow Check Writing'),
        'chk_seq' : fields.char("Check Number", size=64,readonly=True),
        'chk_status' : fields.boolean("Check Status"),
        'pay_type': fields.selection([('cash', 'Cash'), ('chk', 'Check'), ('letter', 'Bank Letter')], 'Pay Type'),
    }

    def _operation_type_pay_type_check(self, cr, uid, ids, context=None):
        """
        Constraint method that check integrity between operation_type & pay_type values
            * When operation_type is "bank" then pay_type should be "chk" or "letter"
            * When operation_type is "supply_cash" then pay_type should be "cash"
            * When operation_type is "treasury" or "petty" then pay_type should be "chk" or "cash" 
        
        @return: boolean
        """
        for voucher in self.browse(cr, uid, ids, context=context):
            if voucher.operation_type == 'bank' and voucher.pay_type not in ['chk','letter']:
                raise orm.except_orm(_('Integrity Error!'), _("When operation is bank feeding, then pay type should be by check or bank letter"))
            if voucher.operation_type == 'supply_cash' and voucher.pay_type != 'cash':
                raise orm.except_orm(_('Integrity Error!'), _("When operation is supply cash, then pay type should be by cash"))
            if voucher.operation_type in ['treasury','petty'] and voucher.pay_type not in ['chk', 'cash']:
                raise orm.except_orm(_('Integrity Error!'), _("When operation is treasury or petty cash feeding, then pay type should be by check or cash"))
        return True

    _constraints = [
         (_operation_type_pay_type_check, "", ['pay_type','operation_type']),
    ]

    def onchange_pay_type(self, cr, uid, ids, context=None):
        """
        @return: Reset pay_journal_id value
        """
        return {'value': {'pay_journal_id': False}}

    def onchange_date(self, cr, uid, ids, date, currency_id, payment_rate_currency_id, amount, company_id, context=None):
        """
        Inherited - add date_due in return value dictionary.
        
        @return: dictionary of values
        """
        res = super(account_voucher, self).onchange_date(cr, uid, ids, date, currency_id, payment_rate_currency_id, amount, company_id, context=context).get('value', {})
        if res:
            res.update({'date_due':date})
        return {'value':res}

    def onchange_price(self, cr, uid, ids, line_ids, tax_id, partner_id=False, context=None):
        """
        Inherit method to update the text value of the check amount in the field 
        amount_in_word based on the language format of the currency.

        @return: dictionary of values of fields to be updated 
        """
        res = super(account_voucher,self).onchange_price(cr, uid, ids, line_ids, tax_id, partner_id=partner_id, context=context)
        amount = res.get('value',{}).get('amount',0)
        currency_format = self.pool.get('res.users').browse(cr, uid, uid).company_id.currency_format
        if currency_format == 'ar':
            currency_id = ids and self.browse(cr, uid, ids,context=context)[0].currency_id.id
            if currency_id:
                currency = self.pool.get('res.currency').read(cr, uid, currency_id, ['units_name', 'cents_name'], context=context)
                amount_in_word = amount_to_text_ar(amount, currency_format, currency.get('units_name',''), currency.get('cents_name',''))
            else:
                amount_in_word = amount_to_text_ar(amount, currency_format)
        else: 
            amount_in_word = amount_to_text(amount)
        res.get('value', {}).update({'amount_in_word':amount_in_word})
        return res

    def onchange_journal_id(self, cr, uid, ids, journal,pay_journal, line_ids, tax_id, partner_id, date, amount, ttype, company_id, pay_now, context={}):
        """
        Inherit onchange method to update the field allow_check in voucher to allow/disallow
        user to print check based on the configuration found in journal object in 
        allow_check_writing field.

        @return: dictionary of values of fields to be updated 
        """
        res = super(account_voucher, self).onchange_journal_id(cr, uid, ids, journal, pay_journal, line_ids, tax_id, partner_id, date, amount, ttype, company_id, pay_now, context)
        if pay_journal:
            journal =  self.pool.get('account.journal').browse(cr, uid, pay_journal)
            res['value'].update({'allow_check':journal.allow_check_writing })
        return res  

    def onchange_partner(self, cr, uid, ids, partner_id, journal_id, price, currency_id, ttype, date, context={}):
        """
        Inherited - add amount_in_word in return value dictionary.
        
        @return: dictionary of values
        """
        default = super(account_voucher, self).onchange_partner_id(cr, uid, ids, partner_id, journal_id, price, currency_id, ttype, date, context=context)
        if journal_id:
            allow_check_writing = journal_id and self.pool.get('account.journal').browse(cr, uid, journal_id, context=context).allow_check_writing or False
        default.get('value',{}).update({'allow_check':allow_check_writing})
        return default

    def check_voucher_amount(self, cr, uid, ids, context=None):
        """
        Checks are not print for Zero or less than Zero payments.
        If check pass, payment state changes, or raising an exception.
        """
        if self.browse(cr, uid, ids, context=context)[0].amount <= 0:
            raise osv.except_osv(_('Could not validate check!'), _("Checks with amount zero couldn't pay!"))
        wf_service = netsvc.LocalService("workflow")
        wf_service.trg_validate(uid, 'account.voucher', ids[0], 'proforma_voucher', cr)

    def copy(self, cr, uid, ids, default={}, context=None, done_list=[], local=False):
        """
        Inherit copy method to reset check no and check statuse to False.
        
        @return: super copy method
        """
        default.update({'chk_seq': False, 'chk_status': False})
        return super(account_voucher, self).copy(cr, uid, ids, default=default, context=context)


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
