# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2013-2014 NCTR (<http://www.nctr.sd>).
#
##############################################################################

import time
from openerp.osv import fields, osv, orm
from openerp.tools.translate import _



#----------------------------------------------------------
#  Bank Statement (Inherit)
#----------------------------------------------------------
class account_bank_statement(osv.Model):

    _inherit = "account.bank.statement"

    def _get_statement(self, cr, uid, ids, context=None):
        """
        Method that maps record ids of a trigger model to ids of the corresponding records 
        in the source model (whose field values need to be recomputed).
        
        @param: list of statement line ids
        @return:  list of statement ids
        """
        result = {}
        for line in self.pool.get('account.bank.statement.line').browse(cr, uid, ids, context=context):
            result[line.statement_id.id] = True
        return result.keys()

    _columns = {
        'ceiling': fields.float('Ceiling', readonly=True, states={'draft':[('readonly',False)]}),
        'journal_id': fields.many2one('account.journal', 'Journal', required=True,
            readonly=True, states={'draft':[('readonly',False)]}),
    }

    def _check_journal_id_amount(self, cr, uid, ids, context=None):
        message = 'Account '
        amount = 0
        account_amount = 0
        flag = False
        for statement in self.browse(cr, uid, ids, context=context):
            account_type = statement.journal_id.default_debit_account_id.user_type.name
            account_amount = statement.journal_id.default_debit_account_id.payment_ceiling
            count = 0
            for line in statement.line_ids:
                amount += line.amount
                if account_type == 'Cash' and line.line_type == 'out_line':
                    if line.amount > account_amount and account_amount > 0:
                        flag = True
                if flag == True and count == 0:
                    message += statement.journal_id.default_debit_account_id.name
                    message += ' amount is '
                    message += str(account_amount)
                    message += '\nAmount doesn\'t cover Lines amount!'
                count += 1
        if amount > account_amount and account_amount > 0:
           flag = True
        if flag == True:
           raise orm.except_orm(_('Warning!'),_(message))
        return True

    _constraints = [
        (_check_journal_id_amount, 'The journal and period chosen have to belong to the same company.', ['journal_id']),
    ]


    def onchange_journal_id(self, cr, uid, statement_id, journal_id, date, context=None):
        """
        @return: selected journal account's balance
        """
        res = super(account_bank_statement, self).onchange_journal_id(cr, uid, statement_id, journal_id, date, context=context)
        ceiling = journal_id and self.pool.get('account.journal').browse(cr, uid, journal_id, context=context).default_debit_account_id.ceiling or 0
        res.get('value', {}).update( {'ceiling': ceiling})
        return res

    def button_cancel(self, cr, uid, ids, context=None):
        """
        Call by 'Cancel' button, prevent reopening the statement if there is
        another bank statement used the current statement balance as opening balance
        If not change the statement state to draft
        
        @return: update state to draft
        """
        for st in self.browse(cr, uid, ids, context=context):
            if self.search(cr, uid, [('journal_id', '=', st.journal_id.id), ('date', '>', st.date)], context=context):
                raise orm.except_orm(_('Error !'), _('You can\'t cancel this operation, another one depend on this already exist.'))
        return self.write(cr, uid, ids, {'state':'draft'}, context=context)

    def balance_check(self, cr, uid, st_id, journal_type='bank', context=None):
        """
        Check if calculated balance match the expected balance which configure as statement_condition in company
        
        @return: raise an exception if balances not match or True
        """
        st = self.browse(cr, uid, st_id, context=context)
        if journal_type == 'bank':
            if not st.company_id.statement_condition:
                raise orm.except_orm(_('Warning!'),
                        _('Kindly enter the statement check condition for your company'))
            expect_balance = self.read(cr, uid, st.id, [st.company_id.statement_condition], context=context)[st.company_id.statement_condition]
            if st.journal_id.type == 'bank' and st.balance_end != expect_balance:
                raise orm.except_orm(_('Error !'),
                        _('The statement balance is incorrect (%.2f)!\nThe expected balance (%.2f) is different than the computed one. ')
                        % (expect_balance, st.balance_end))
            return True
        else:
            if not(st.balance_end == st.balance_end_real == st.journal_balance):
                raise osv.except_osv(_('Error!'),
                    _('The statement balance is incorrect !\nThe expected balance (%.2f), the computed balance (%.2f) and the journal balance (%.2f) are not equals!') % (st.balance_end_real, st.balance_end, st.journal_balance))
        return True

    def button_confirm_bank(self, cr, uid, ids, context=None):
        """
        Confirm bank statement button check statement balance before closing the statement
        change state to 'confirm' and set closing_date
        
        @return: update statement record
        """
        for st in ids:
            self.balance_check(cr, uid, st, context=context)
        return self.write(cr, uid, ids, {'state':'confirm', 'closing_date': time.strftime("%Y-%m-%d %H:%M:%S")}, context=context)

    def button_confirm_cash(self, cr, uid, ids, context=None):
        """ 
        Confirm Cash Register Button calculate  balance_end_real from closing_details_ids,
        Then check statement balance before closing the statement
        
        @return: boolean
        """
        for st in self.browse(cr, uid, ids, context=context):
            self.write(cr, uid, [st.id], {'balance_end_real':sum([c.subtotal_closing for c in st.closing_details_ids]),
                                          'state':'confirm', 'closing_date':time.strftime("%Y-%m-%d %H:%M:%S")}, context=context)
            self.balance_check(cr, uid, st.id, 'cash', context=context)
        return True


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
