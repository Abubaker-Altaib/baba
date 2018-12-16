# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2018-2019 NCTR (<http://www.nctr.sd>).
#
##############################################################################

from odoo.exceptions import Warning, ValidationError
from odoo import api, fields, models, _ 

class AccountRejectReasonWiz(models.TransientModel):
    _name = "account.voucher.reject.reason.wiz"
    _description = "Refuse Expense"

    reason_id=fields.Many2one('account.reject.reason', string="Reject Reason", required=True)
    voucher_ids = fields.Many2many('account.voucher')

    @api.model
    def default_get(self, fields):
        res = super(AccountRejectReasonWiz, self).default_get(fields)
        active_ids = self.env.context.get('active_ids', [])
        res.update({
            'voucher_ids': active_ids,
        })
        return res

    @api.multi
    def reject_reason(self):
        self.ensure_one()
        if self.voucher_ids:
            self.voucher_ids.voucher_reject_reason(self.reason_id)
        return {'type': 'ir.actions.act_window_close'}
