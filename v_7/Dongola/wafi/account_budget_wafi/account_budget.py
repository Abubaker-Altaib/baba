# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

from openerp.osv import fields, osv
from openerp.tools.translate import _


#---------------------------------------------------
# Account Budget (Inherit)
# --------------------------------------------------
class account_budget(osv.Model):
   
    _inherit = "account.budget"
    
    _columns = {
        'state' : fields.selection([('draft', 'Draft'), ('validate', 'Validated'), ('done', 'Done'), ('cancel', 'Cancelled')],
                                   'Status', required=True, readonly=True),
    }
# ---------------------------------------------------------
# FiscalYear Budgets (Inherit)
# ---------------------------------------------------------
class account_fiscalyear_budget(osv.Model):
    """
    Inherit fiscal year budget to modify it's workflow
    """
    _inherit = "account.fiscalyear.budget"
    
    _columns = {
        'state' : fields.selection([('draft', 'Draft') ,('complete','Waiting for Manager Confirm'),  ('confirm','Waiting for Ministry Approve'),
                                    ('approve', 'Ministry Approved'), ('validate', 'Budget Flow Created'),('cancel', 'Cancelled')], 'Status', required=True, readonly=True),
    }

    def budget_complete(self, cr, uid, ids, context=None):
        """
        Workflow function
        @return: change record state to 'complete'.
        """
        #budget_account_ids = [bl.general_account_id.id for b in self.browse(cr, uid, ids, context=context) for bl in b.account_fiscalyear_budget_line ]
        #account_ids = self.pool.get('account.account').search(cr, uid,[('id','not in', budget_account_ids),('budget_classification','!=',False)], context=context)
        #return self.write(cr, uid, ids, {'state': 'complete', 'account_fiscalyear_budget_line': [(0, 0, {'general_account_id': acc}) for acc in account_ids]}, context=context)
        return self.write(cr, uid, ids, {'state': 'complete'}, context=context)

    def budget_approve(self, cr, uid, ids, context=None):
        """
        Workflow function
        @return: change record state to 'approve'.
        """
        return self.write(cr, uid, ids, {'state': 'approve'}, context=context)


# ---------------------------------------------------------
# FiscalYear Budget lines (Inherit)
# ---------------------------------------------------------

class account_fiscalyear_budget_lines(osv.Model):
    """
    Inherit fiscal year line to prevent entering negative or zero value
    """
    _inherit = "account.fiscalyear.budget.lines"
    
    _sql_constraints = [('palnned_amount_check', 'CHECK (planned_amount>0)',  _("Your budget's plan amount must be more than zero!"))
    ]


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
