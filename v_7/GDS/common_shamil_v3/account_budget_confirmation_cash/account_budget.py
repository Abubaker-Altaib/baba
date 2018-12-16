# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

from openerp.osv import fields, osv, orm
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp
from openerp import netsvc

from openerp.addons.account_budget_confirmation.account_budget import account_budget_lines as abl

fnct_residual_search=abl.fnct_residual_search

# ---------------------------------------------------------
# Budget Confirmation (inherit)
# ---------------------------------------------------------
class account_budget_confirmation(osv.Model):

    _inherit = "account.budget.confirmation"


    def check_budget(self, cr, uid, ids, context={}):
        """
        This method check whether the budget line residual allow to validate this confirmation or not
        @return: boolean True if budget line residual more that confirm amount, or False
        """
        line_obj = self.pool.get('account.budget.lines')
        for confirmation in self.browse(cr, uid, ids, context=context):
            budget_line = line_obj.search(cr, uid,[('analytic_account_id','=', confirmation.analytic_account_id.id),
                                                   ('period_id','=', confirmation.period_id.id),
                                                   ('general_account_id','=',confirmation.general_account_id.id)], context=context)
            if budget_line:
                if confirmation.residual_amount > line_obj.browse(cr, uid, budget_line, context=context)[0].residual_balance or \
                   confirmation.residual_amount > line_obj.browse(cr, uid, budget_line, context=context)[0].cash_residual_balance:
                    return False
            elif confirmation.analytic_account_id.budget:
                raise orm.except_orm(_('Warning!'), _('This account has no budget!'))
        return True


# ---------------------------------------------------------
# Account Budget Lines  (inherit)
# ---------------------------------------------------------
class account_budget_lines(osv.Model):

    _inherit = "account.budget.lines"

    
    def _residual_balance(self, cr, uid, ids, field_name, arg=None, context={}):
        """
        Recalcute Budget Lines residual_amount by substract confirm amount  
                    
        @param char field_name: functional field name,
        @param list arg: additional arguments,
        @return: dictionary {record_id: residual amount}
        """
        cr.execute('SELECT id,planned_amount+total_operation-balance-confirm,cash_total_operation-balance-confirm FROM account_budget_lines WHERE id IN (%s)'% (','.join(map(str,ids)),))
        return dict([(l[0],{'residual_balance':l[1],'cash_residual_balance':l[2]}) for l in cr.fetchall()])

    
    def fnct_cash_residual_search(self, cr, uid, obj, name, domain=None, context=None):
        if context is None:
            context = {}
        if not domain:
            return []
        field, operator, value = domain[0]
        cr.execute('SELECT id FROM account_budget_lines \
                    WHERE cash_total_operation-balance-confirm  '+operator+str(value))
        res = cr.fetchall()
        return [('id', 'in', [r[0] for r in res])]
        
    _columns = {
        'residual_balance': fields.function(_residual_balance, fnct_search=fnct_residual_search, method=True,
                                                    multi='residual', digits_compute=dp.get_precision('Account'), string='Residual Balance'),  
        'cash_residual_balance': fields.function(_residual_balance, fnct_search=fnct_cash_residual_search, method=True, multi='residual', 
                                                 digits_compute=dp.get_precision('Account'), string='Cash Residual Balance'),
    
    }

    _sql_constraints = [('cash_residual_check_confirm', 'CHECK ((cash_total_operation-balance-confirm)>=0)',  _("Cash Budget cann't go overdrow!"))]
    

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
