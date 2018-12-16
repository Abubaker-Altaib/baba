# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

from odoo import api , fields, models,_
import odoo.addons.decimal_precision as dp
from odoo.exceptions import UserError, ValidationError

# ---------------------------------------------------------
# Budget Confirmation
# ---------------------------------------------------------

class AccountBudgetConfirmation(models.Model):
    """ Object of reserve some amount from the budget  """
    _inherit = "account.budget.confirmation"

    state=fields.Selection([('draft','Draft'),('waiting_valid','Waiting Valid'),('complete','Waiting For Approve'),
                                    ('check','Waiting Check'),('valid','Approved'),
                                    ('unvalid','Not Approved'),('cancel', 'Cancelled')],
                                    'Status', required=True, readonly=True,default='draft')

    @api.multi
    def check_budget(self):
        """
        This method check whether the budget line residual allow to validate this confirmation or not
        @return: boolean True if budget line residual more that confirm amount, or False
        """
        budget_line = []
        line_obj = self.env['crossovered.budget.lines']
        for confirmation in self:
            position = self.env['account.budget.post']._get_budget_position(confirmation.account_id.id)

            if not position:
                # self.budget_valid()
                raise UserError(_("Confirmation Has no Budget Position!"))
            else:
                budget_line = line_obj.search([('analytic_account_id', '=', confirmation.analytic_account_id.id),
                                               ('date_from', '<=', confirmation.date),
                                               ('date_to', '>=', confirmation.date),
                                               ('general_budget_id', '=', position.id),
                                               ('crossovered_budget_id.state', '=', 'validate')])


            if budget_line:
                # FIXME: allow_budget_overdraw
                allow_budget_overdraw = budget_line.crossovered_budget_id.allow_budget_overdraw
                if not allow_budget_overdraw and confirmation.residual_amount > budget_line.residual:
                    self.budget_unvalid()
                elif confirmation.residual_amount <= budget_line.residual:
                    #    self.budget_valid()
                    if self.state == 'waiting_valid':
                        self.budget_valid()
                    else:
                        self.state = 'waiting_valid'
                else:
                    #    self.budget_valid()
                    if self.state == 'waiting_valid':
                        self.budget_valid()
                    else:
                        self.state = 'waiting_valid'
            elif confirmation.analytic_account_id.budget:  # v9: test me
                raise ValidationError(_('This account has no budget!'))
        return True

