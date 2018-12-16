# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

from odoo import models, fields, api, exceptions, _

class CustomHrEmployee(models.Model):
    _inherit = "hr.employee"

    employee_code = fields.Char(string="Code")

    @api.model
    def get_seq_code(self):
        """
        To create Sequence for employee as code
        :return:
        """
        sequence = self.env['ir.sequence'].search([('code', '=', self._name)])
        return sequence.get_next_char(sequence.number_next_actual)

    @api.model
    def create(self, vals):
        """
        :param vals:
        :return:
        """
        vals['employee_code'] = self.env['ir.sequence'].get(self._name) or '/'
        return super(CustomHrEmployee, self).create(vals)


class HRPayslip(models.Model):
    _inherit = "hr.payslip"

    salary = fields.Boolean(default=False)

    @api.multi
    @api.onchange('contract_id')
    def OnchangeStruc(self):
        """
        change struct_id when contract is change
        :return:
        """
        new_struct_id = []
        contract_ids = self.env['hr.contract'].search([('id', '=', self.contract_id.id)])
        for contract in contract_ids:
            new_struct_id.append(contract.struct_id.id)
        for struct in new_struct_id:
            self.struct_id = struct
            break
        return {
            'domain': {
                'struct_id': [('id', 'in', new_struct_id)]
            }
        }


class AccountVoucherCustom(models.Model):
    _inherit = 'account.voucher'

    journal_id = fields.Many2one(required=False)
    account_id = fields.Many2one(required=False)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('cancel', 'Cancelled'),
        ('proforma', 'Pro-forma'),
        ('posted', 'Posted'), ('transfered','Transfered'),], 'Status', readonly=True, track_visibility='onchange', copy=False, default='draft',)

   # inherit voucher_move_line_create to set debit and credit in p
    @api.multi
    def voucher_move_line_create(self, line_total, move_id, company_currency, current_currency):
        '''
        For more info see the default function in account_voucher
        '''
        for line in self.line_ids:
            # create one move line per voucher line where amount is not 0.0
            if not line.price_subtotal:
                continue
            # convert the amount set on the voucher line into the currency of the voucher's company
            # this calls res_curreny.compute() with the right context,
            # so that it will take either the rate on the voucher if it is relevant or will use the default behaviour
            amount = self._convert_amount(line.price_unit * line.quantity)
            if amount > 0:
                move_line = {
                    'journal_id': self.journal_id.id,
                    'name': line.name or '/',
                    'account_id': line.account_id.id,
                    'move_id': move_id,
                    'partner_id': self.partner_id.id,
                    'analytic_account_id': line.account_analytic_id and line.account_analytic_id.id or False,
                    'quantity': 1,
                    'credit': abs(amount) if self.voucher_type == 'sale' else 0.0,
                    'debit': abs(amount) if self.voucher_type == 'purchase' else 0.0,
                    'date': self.account_date,
                    'tax_ids': [(4, t.id) for t in line.tax_ids],
                    'amount_currency': line.price_subtotal if current_currency != company_currency else 0.0,
                }
            # this check has been add to see if the amount is less than zero it (-) then it
            # will be a credit
            elif amount < 0:
                move_line = {
                    'journal_id': self.journal_id.id,
                    'name': line.name or '/',
                    'account_id': line.account_id.id,
                    'move_id': move_id,
                    'partner_id': self.partner_id.id,
                    'analytic_account_id': line.account_analytic_id and line.account_analytic_id.id or False,
                    'quantity': 1,
                    'credit': abs(amount) if self.voucher_type == 'purchase' else 0.0,
                    'debit': abs(amount) if self.voucher_type == 'sale' else 0.0,
                    'date': self.account_date,
                    'tax_ids': [(4, t.id) for t in line.tax_ids],
                    'amount_currency': line.price_subtotal if current_currency != company_currency else 0.0,
                }

            self.env['account.move.line'].with_context(apply_taxes=True).create(move_line)
        return line_total

    @api.multi
    def pay_voucher(self):
        """
        create ne account.payment and set value from
        account.voucher screen to the new account.payment
        """
        self.write({'state': 'transfered'})
        payment_id = self.env['account.payment'].create(
            {
                'payment_type': 'outbound',
                'partner_type': 'supplier',
                'partner_id': self.partner_id.id,
                'amount': self.amount,
                'communication': _('Employee Salary'),
            }
         )



class HrPayslipRun(models.Model):
    _inherit = "hr.payslip.run"

    is_salary = fields.Boolean(string='Basic Salary', default=False)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('close', 'Close'),
    ], string='Status', index=True, readonly=True, copy=False, default='draft')

    @api.multi
    @api.onchange('is_salary')
    def set_salary(self):
        for slip in self.slip_ids:
            slip.write({'salary': True})

    @api.multi
    def confirm(self):
        """
        get in each salary payslip and create new move line for all
        salary payslip
        :return:
        """
        self.write({'state': 'confirmed'})
        gross_account = []
        add_account = []
        ded_account = []
        for slip in self.slip_ids:
            for details in slip.details_by_salary_rule_category:
                if details.category_id.code == 'GROSS':
                    if details.salary_rule_id.account_debit.id not in gross_account and details.salary_rule_id.account_debit.id != False:
                        gross_account.append(details.salary_rule_id.account_debit.id)
                if details.category_id.code == 'ADD':
                    if details.salary_rule_id.account_debit.id not in add_account and details.salary_rule_id.account_debit.id != False:
                        add_account.append(details.salary_rule_id.account_debit.id)
                if details.category_id.code == 'DED':
                    if details.salary_rule_id.account_credit.id not in ded_account and details.salary_rule_id.account_credit.id != False:
                        ded_account.append(details.salary_rule_id.account_credit.id)
        line = []
        net_account_id = 0
        net_total = 0
        my_add = dict(map(lambda x: (x, {'name': '', 'total': 0.0, 'account_id': '', }), add_account))
        my_ded = dict(map(lambda x: (x, {'name': '', 'total': 0.0, 'account_id': '', }), ded_account))
        my_groos = dict(map(lambda x: (x, {'name': '', 'total': 0.0, 'account_id': '', }), gross_account))
        for slips in self.slip_ids:
            slips.write({'state': 'done'})
            for l in slips.details_by_salary_rule_category:

                """GROSS Line"""
                if l.category_id.code == 'GROSS' and l.salary_rule_id.account_debit.id != False:
                    my_groos[l.salary_rule_id.account_debit.id]['total'] += l.total
                    my_groos[l.salary_rule_id.account_debit.id].update(
                        {'name': l.name, 'account_id': l.salary_rule_id.account_debit.id})

                    """ADD Line"""
                elif l.category_id.code == 'ADD' and l.salary_rule_id.account_debit.id != False:
                    my_add[l.salary_rule_id.account_debit.id]['total'] += l.total
                    my_add[l.salary_rule_id.account_debit.id].update(
                        {'name': l.name, 'account_id': l.salary_rule_id.account_debit.id})

                    """DED Line"""
                elif l.category_id.code == 'DED' and l.salary_rule_id.account_credit.id != False:
                    my_ded[l.salary_rule_id.account_credit.id]['total'] += l.total
                    my_ded[l.salary_rule_id.account_credit.id].update(
                        {'name': l.name, 'account_id': l.salary_rule_id.account_credit.id})

                    """NET Line"""
                elif l.category_id.code == 'NET' and l.salary_rule_id.account_credit.id != False:
                    net_account_id = l.salary_rule_id.account_credit.id
                    net_total += l.total

        for gross in gross_account:
            line += [(0, 6, {
                'name': my_groos[gross]['name'],
                'account_id': my_groos[gross]['account_id'],
                'quantity': 1,
                'price_unit': my_groos[gross]['total'],
            })]
        for add in add_account:
            line += [(0, 6, {
                'name': my_add[add]['name'],
                'account_id': my_add[add]['account_id'],
                'quantity': 1,
                'price_unit': my_add[add]['total'],
            })]
        for ded in ded_account:
            line += [(0, 6, {
                'name': my_ded[ded]['name'],
                'account_id': my_ded[ded]['account_id'],
                'quantity': 1,
                'price_unit': (my_ded[ded]['total'] * -1),
            })]

        voucher_id = self.env['account.voucher'].create(
            {
                'name': '',
                'account_id': 6514,
                'journal_id': 70,
                'pay_now': 'pay_later',
                'reference': _('Employee Salary'),
                'voucher_type': 'purchase',
                'company_id': self.env.user.company_id.id,
                'line_ids': line,

            })
