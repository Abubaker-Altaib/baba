# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2018-2019 NCTR (<http://www.nctr.sd>).
#
##############################################################################

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

class wiz_print_check(models.TransientModel):
    _name = 'wiz.print.check'

    next_check_number = fields.Integer('Next Check Number', required=True)
    action = fields.Selection([('reprint', 'Reprint'), ('update', 'Update'), ('delete','Delete')], string='Process') 
    reason = fields.Selection([('void', 'Void'), ('loss', 'Loss'), ('cancelation','Cancelation'), ('unk', 'Unknown')], string='Reason') 
    preprinted = fields.Boolean('Pre-printed')
    release_at = fields.Char('Release At', size=54, Translate=True)

    
    def print_checks(self):
        check_number = self.next_check_number
        if self.env.context.get('payment_ids'):
            payments = self.env['account.payment'].browse(self.env.context['payment_ids'])
            for payment in payments:
                check_id = self.env['check.log'].search([('name', '=', payment.id),('status', '=', 'active')], limit=1)
                action = self.action
                payment.check_number = check_number
                if action == 'reprint':
                    return payment.with_context(release_at=self.release_at).do_print_checks()
                if not action:
                    payment.create_check_log(check_number,self.release_at)
                    return payment.with_context(release_at=self.release_at).do_print_checks()

                if not check_id:
                    raise UserError(_("Selected check is not exist!")) 

                if action == 'delete':
                    check_id.status = 'deleted'
                    payment.check_number = 0
                    return True
                else:
                    check_id.status = 'canceled'
                    return payment.create_check_log(check_number,self.release_at)
