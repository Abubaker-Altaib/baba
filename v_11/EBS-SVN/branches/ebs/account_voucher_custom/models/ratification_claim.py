
from odoo.exceptions import Warning,UserError, ValidationError
from odoo import api, fields, models, _


class productTemplate(models.Model):
    _inherit = "product.template"

    ratification = fields.Boolean(String="Ratification",default=False)


class accountVoucher(models.Model):
    _inherit = "account.voucher"

    ratification = fields.Boolean(String="Ratification", default=False)
    ratf_approve = fields.Boolean(compute="_approve_ratf")


    @api.one
    @api.depends('state')
    def _approve_ratf(self):
        self.retf_approve = False
        if self.state == 'budget_approved':
            employee = self.env['hr.employee'].search([('user_id', '=', self.env.user.id)])
            if employee:
                for line in self.env.user.company_id.account_approve_ids:
                    emp_list = [emp.id for emp in line.employee_ids]

                    if employee.id in emp_list:
                        if self.amount >= line.min_amount and self.amount <= line.max_amount:
                            self.retf_approve = True
                    emp_list = []

    @api.multi
    def action_requested(self):
        # if self.filtered(lambda voucher: voucher.state != 'draft'):
        #     raise UserError(_('Voucher must be in Draft state ("To Submit") in order to confirm it.'))
        self.ensure_one()
        write = self.write({'state': 'requested'})
        # filter line which required budget
        line_ids = self.line_ids.filtered(lambda r: r.account_id.budget_required and r.analytic_account_id and r.analytic_account_id.budget)
        if line_ids:
            line_ids.check_voucher_line_account_budget()
            self.create_budget_confirmation()
        return write

    @api.multi
    def action_service(self):
        return self.write({'state': 'service'})

    @api.multi
    def action_completed(self):
        return self.write({'state': 'completed'})

