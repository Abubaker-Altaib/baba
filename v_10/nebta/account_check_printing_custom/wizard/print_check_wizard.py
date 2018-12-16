# -*- coding: utf-8 -*-

from odoo import models,fields
from odoo.tools.translate import _
from odoo import api

class wiz_print_check(models.TransientModel):
    _name = 'wiz.print.check'

    next_check_number = fields.Integer('Next Check Number', required=True)
    action = fields.Selection([('reprint', 'Reprint'), ('update', 'Update'), ('delete','Delete')], string='Process') 
    reason = fields.Selection([('void', 'Void'), ('loss', 'Loss'), ('cancelation','Cancelation'), ('unk', 'Unknown')], string='Reason') 
    preprinted = fields.Boolean('Pre-printed')

    
    def print_checks(self):
        check_number = self.browse(self._ids).next_check_number
        payments = self.env['account.payment'].browse(self.env.context['payment_ids'])
        for payment in payments:
            check_id = self.env['check.log'].search([('name', '=', payment.id),('status', '=', 'active')], limit=1)
            #check = self.env['check.log'].browse(check_id)
            action = self.browse(self._ids).action

            if action == 'reprint':
                return payment.print_check_report()
            if not action:
                payment.do_print_checks(check_number)
                return payment.print_check_report()

            if not check_id:
                raise UserError(_("Selected check is not exist!")) 

            if action == 'delete':
                check_id.status = 'deleted'
                if payments.is_approval == True:
                    self.env['finance.approval.payment'].search([('payment_id','=',payments.id)]).state = 'canceled'
                payment.check_number = 0
                return True
            else:
                check_id.status = 'canceled'
                if payments.is_approval == True:
                    self.env['finance.approval.payment'].search([('payment_id','=',payments.id)]).state = 'canceled'
                return payment.do_print_checks(check_number)

