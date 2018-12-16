# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################
import math
from odoo.tools.translate import _
from odoo import tools
from odoo import models, fields, api , exceptions
#from odoo.tools import amount_to_text_en, float_round
from odoo.addons.account_check_printing_custom.models import amount_to_text_ar
from odoo.exceptions import UserError, ValidationError


class account_payment(models.Model):
    """
    Inherit object payment to add function that 
    """
    _inherit = 'account.payment'

    @api.multi
    def print_checks(self):
        """ Check that the recordset is valid, set the payments state to sent and call print_checks() """
        self = self.filtered(lambda r: r.payment_method_id.code == 'check_printing' and r.state != 'reconciled')

        if len(self) == 0:
            raise UserError(_("Payments to print as a checks must have 'Check' selected as payment method and "
                              "not have already been reconciled"))
        if any(payment.journal_id != self[0].journal_id for payment in self):
            raise UserError(_("In order to print multiple checks at once, they must belong to the same bank journal."))

        self.filtered(lambda r: r.state == 'draft').post()
        #same func in custom , just we comment state change
        #self.write({'state': 'sent'})

        if not self[0].journal_id.check_manual_sequencing:
            is_printed = False
            if self.check_number != 0:
                is_printed = True
            return {
                'name': _('Print Check Report'),
                'type': 'ir.actions.act_window',
                'res_model': 'wiz.print.check',
                'view_type': 'form',
                'view_mode': 'form',
                'target': 'new',
                'context': {
                    'payment_ids': self.ids,
                    'default_next_check_number': self._get_next_check_no()[0],
		            'default_preprinted': is_printed,
                }
            }
        else:
            return self.do_print_checks()

    @api.multi
    def print_report(self):
        datas = {}
        [data] = self.read()
        data['payment_ids']=self.ids
        datas = {
             'ids': self._ids,
             'model': 'account.payment',
             'form': data
                }
        
        return self.env.ref('account_check_printing_custom.bank_letter_qweb_report').report_action(self, data=datas)

