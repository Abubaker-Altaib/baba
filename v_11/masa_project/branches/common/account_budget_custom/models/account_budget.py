# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################
from odoo import api , fields, models,_
from datetime import date, datetime
from odoo.exceptions import UserError, ValidationError
import time

class CrossoveredBudget(models.Model):
    _inherit = "crossovered.budget"
    _order = "date_from desc, id desc"

    allow_budget_overdraw =fields.Boolean(string='Allow Budget Overdraw',readonly=True, default=False, states={'draft': [('readonly', False)]})
    date_from= fields.Date('Start Date', required=False ,states={'done':[('readonly',True)]}, copy=False)
    date_to= fields.Date('End Date', required=False ,states={'done':[('readonly',True)]}, copy=False)
    amount = fields.Float('Amount',readonly=True, states={'draft': [('readonly', False)]})
    analytic_account_id = fields.Many2one('account.analytic.account', 'Analytic Account', readonly=True, states={'draft': [('readonly', False)]})
    creating_user_id = fields.Many2one('res.users', 'Responsible',domain=lambda self:[("groups_id", "in", self.env.ref("account_budget_custom.group_budget_user").id)], states={'done': [('readonly', True)]})
    type = fields.Selection([
        ('in', 'In'),
        ('out', 'Out')], required=True, default='in')

    @api.multi
    def write(self, vals):
        res = super(CrossoveredBudget, self).write(vals)
        for budget in self:
            for line in budget.crossovered_budget_line:
                line_vals = {}
                if not line.date_from:
                    line_vals.update({'date_from':budget.date_from})
                if not line.date_to:
                    line_vals.update({'date_to':budget.date_to})
                if line.analytic_account_id!=budget.analytic_account_id:
                    line_vals.update({'analytic_account_id':budget.analytic_account_id.id})
                line.write(line_vals)
        return  res

    @api.constrains('date_from', 'date_to')
    def _check_date_validity(self):
        """ verifies if date_from is earlier than date_to. """
        for budget in self:
            if budget.date_from and budget.date_to:
                if budget.date_to < budget.date_from:
                    raise ValidationError(_('End Date cannot be earlier than Start Date.'))


    @api.onchange('analytic_account_id')
    def onchange_analytic_account_id(self):
        self.creating_user_id = self.analytic_account_id.user_id

    @api.multi
    def action_budget_confirm(self):
        if not self.crossovered_budget_line:
            raise ValidationError(_('Please Enter Budget Lines'))
        if self.amount != sum(self.mapped('crossovered_budget_line.planned_amount' )):
            if self.type == 'in':
                raise ValidationError(_('Sumation of planned in amount in budget line must be equles to amount in budget'))
            else:
                raise ValidationError(_('Sumation of planned amount in budget line must be equles to amount in budget'))
        self.write({'state': 'confirm'})

    @api.multi
    @api.constrains('date_from','date_to','analytic_account_id')
    def _check_budget_overlap(self):
        if self.date_from  and self.date_to:
            overlap_ids = self.search([('date_from','<=',self.date_to),('date_to','>=',self.date_from),
               ('analytic_account_id','=',self.analytic_account_id.id),('id','!=',self.id),('type','=',self.type)])
            if overlap_ids:
                raise ValidationError(_(" The budgets are overlapping ."))

    @api.multi
    def print_Budget(self):
        return self.env.ref('account_budget_custom.report_print_budget').report_action(self)

    @api.multi
    def transfer(self):
        for rec in self:
            for line in rec.crossovered_budget_line:
                if line.residual <=0:
                    continue
                for next in self.env['crossovered.budget.lines'].search([
                    ('analytic_account_id','=', line.analytic_account_id.id),
                    ('general_budget_id', '=', line.general_budget_id.id),
                    ('date_from','>', line.date_to),('state','=','validate')], limit=1, order='date_from asc'):

                    vals ={
                        'budget_line_id_from':line.id,
                        'budget_line_id_to':next.id,
                        'analytic_account_id_from':line.analytic_account_id.id,
                        'analytic_account_id_to':next.analytic_account_id.id,
                        'name':'close',
                        'state':'done',
                        'amount':line.residual,
                        'date':time.strftime('%Y-%m-%d'),
                    }
                    self.env['account.budget.operation.line'].create(vals)
        return True


    @api.multi
    def button_open_operations(self):
        return {
            'name': _('Budget Operations'),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'account.budget.operation.line',
            'view_id': False,
            'type': 'ir.actions.act_window',
            'domain': ['|',('budget_line_id_from.crossovered_budget_id', 'in', self.ids),('budget_line_id_to.crossovered_budget_id', 'in', self.ids)],
        }

class AccountBudgetLines(models.Model):
    _inherit = "crossovered.budget.lines"

    name_position_analytic =fields.Char(compute='_budget_name_code',store=True, string='Name')
    code=fields.Char(compute='_budget_name_code',store=True, string='Code')
    date_from = fields.Date('Start Date', required=False, copy=False)
    date_to = fields.Date('End Date', required=False, copy=False)
    residual = fields.Float(compute='_compute_residual_balance', string='Residual Balance', store=True)
    analytic_account_id = fields.Many2one('account.analytic.account', 'Analytic Account', required=True)
    theoritical_amount = fields.Float(compute='_compute_theoritical_amount', string='Theoretical Amount', digits=0,store=True)
    total_operation= fields.Float(compute='_compute_operation_amount',string='In/De-crease Amount',digits=0,store=True)
    transfer_amount= fields.Float(compute='_compute_operation_amount',string='Transfer Amount',digits=0,store=True)
    confirm= fields.Float(compute='_compute_confirm_amount',string='Confirm Amount',digits=0,store=True)
    confirmation_ids=fields.One2many('account.budget.confirmation', 'budget_line_id', 'Confirmations', copy=False)
    practical_amount = fields.Float(compute='_compute_practical_amount', string='Practical Amount', store=True)
    percentage = fields.Float(compute='_compute_percentage_deviation', string='Achievement', store=True)
    deviation=fields.Float(string="deviation", compute='_compute_percentage_deviation', store=True)
    operation_id_from= fields.One2many('account.budget.operation.line', 'budget_line_id_from',string='line operation history From' ,copy=False)
    operation_id_to= fields.One2many('account.budget.operation.line', 'budget_line_id_to', string='line operation history To', copy=False)
    state = fields.Selection(related='crossovered_budget_id.state',string='State', store=True, readonly=True)


    @api.constrains('date_from', 'date_to')
    def _check_date_validity(self):
        """ verifies if date_from is earlier than date_to. """
        for budget in self:
            if budget.date_from and budget.date_to:
                if budget.date_to < budget.date_from:
                    raise ValidationError(_('End Date cannot be earlier than Start Date.'))
                    
    @api.multi
    @api.constrains('operation_id_from','operation_id_to','confirmation_ids','date_from','date_to')
    def _check_operation_period(self):
        for line in self:
            for operation_from in line.operation_id_from:
                if operation_from.operation_id.state == 'done':
                    if operation_from.date < line.date_from or operation_from.date > line.date_to:
                        raise ValidationError(_("You cann't modify budget period which has transfer or increase operation!"))
            for operation_to in line.operation_id_to:
                if operation_to.operation_id.state == 'done':
                    if operation_to.date < line.date_from or operation_to.date > line.date_to:
                        raise ValidationError(_("You cann't modify budget period which has transfer or increase operation!"))
            for confirmation in line.confirmation_ids:
                if confirmation.state == 'valid':
                    if confirmation.date < line.date_from or confirmation.date > line.date_to:
                        raise ValidationError(_("You cann't modify budget period which has confirmation!"))

    @api.one
    @api.depends('planned_amount','practical_amount','confirm','total_operation')
    def _compute_percentage_deviation(self):
        amount = self.planned_amount + self.total_operation
        self.deviation = amount != 0 and self.residual*100/(self.planned_amount + self.total_operation) or 100
        self.percentage = 100 - self.deviation

    @api.multi
    @api.depends('analytic_account_id.line_ids')
    def _compute_practical_amount(self):
        for line in self:
            result = 0.0
            acc_ids = line.general_budget_id.account_ids.ids
            date_to = self.env.context.get('wizard_date_to') or line.date_to
            date_from = self.env.context.get('wizard_date_from') or line.date_from
            if line.analytic_account_id.id and line.date_from  and line.date_to:
                self.env.cr.execute("""
                    SELECT SUM(amount)
                    FROM account_analytic_line
                    WHERE account_id=%s
                        AND (date between to_date(%s,'yyyy-mm-dd') AND to_date(%s,'yyyy-mm-dd'))
                        AND general_account_id=ANY(%s)""",
                (line.analytic_account_id.id, date_from, date_to, acc_ids,))
                result = self.env.cr.fetchone()[0] or 0.0
            line.practical_amount = result

    @api.depends('planned_amount','practical_amount','confirm','total_operation','transfer_amount')
    def _compute_residual_balance(self):
        for line in self:
            line.residual = line.planned_amount + line.total_operation + \
                line.practical_amount + line.confirm + line.transfer_amount

    @api.multi
    @api.depends('confirmation_ids')
    def _compute_confirm_amount(self):
        for line in self:
            result = 0.0
            acc_ids = line.general_budget_id.account_ids.ids
            date_to = self.env.context.get('wizard_date_to') or line.date_to
            date_from = self.env.context.get('wizard_date_from') or line.date_from
            if line.analytic_account_id.id and line.date_from  and line.date_to:
                self.env.cr.execute("""
                    SELECT SUM(residual_amount)
                    FROM account_budget_confirmation
                    WHERE state ='valid' and analytic_account_id=%s
                        AND (date between to_date(%s,'yyyy-mm-dd') AND to_date(%s,'yyyy-mm-dd'))
                        AND account_id=ANY(%s)""",
                (line.analytic_account_id.id, date_from, date_to, acc_ids,))
                result = self.env.cr.fetchone()[0] or 0.0
            line.confirm = -result

    @api.multi
    @api.depends('operation_id_from.state','operation_id_to.state')
    def _compute_operation_amount(self):
        for line in self:
            operation =0
            close = 0
            if line.date_from and line.date_to:
                    self.env.cr.execute(""" SELECT name ,
                         COALESCE(SUM((CASE WHEN  budget_line_id_from = %s
                                    THEN - amount
                                    ELSE amount
                                END  )),0) AS amount
                            FROM  account_budget_operation_line h
                            where  state='done' and (budget_line_id_from = %s or budget_line_id_to = %s)
                            group by name""" , (line.id, line.id , line.id))
                    result =  self.env.cr.dictfetchall()

                    for r in result:
                       if r['name']=='close':
                          close += r['amount']
                       else:
                          operation += r['amount']
            line.total_operation = operation
            line.transfer_amount = close

    @api.multi
    @api.depends('analytic_account_id','general_budget_id','date_from','date_to')
    def name_get(self):
        result = []
        for line in self:
            analytic = line.analytic_account_id
            account = line.general_budget_id
            name = str(account.name) + '/' + str(analytic.name) +\
                ' / ' + str(line.date_from  or '') + ' - ' + str(line.date_to or '') + _(' / residual:') + str(line.residual)
            result.append((line.id, name))
        return result


    @api.multi
    @api.depends('analytic_account_id','general_budget_id')
    def _budget_name_code(self):
        for line in self:
            analytic = line.analytic_account_id
            account = line.general_budget_id
            line.name_position_analytic = str(account.name) + '/' + str(analytic.name) +\
                ' -' + (line.date_from  or '') + ' / ' + (line.date_to or '')
            line.code=str(account.code or '')+ '/ ' + str(analytic.code or '')

    @api.multi
    @api.constrains('planned_amount')
    def _check_amount(self):
        for obj in self:
            if obj.planned_amount <= 0:
                raise ValidationError(_('The planned amount must be greater than zero.'))

    @api.multi
    @api.constrains('date_from','date_to','analytic_account_id','general_budget_id')
    def _check_budget_overlap(self):
        if self.date_from  and self.date_to:
            overlap_ids = self.search([('date_from','<=',self.date_to),('date_to','>=',self.date_from),
               ('analytic_account_id','=',self.analytic_account_id.id),('id','!=',self.id),
               ('general_budget_id','=',self.general_budget_id.id)])
            if overlap_ids:
                raise ValidationError(_("The budget is invalid. The budgets are overlapping ."))

    @api.multi
    @api.constrains('date_from','date_to')
    def _date_check(self):
        for line in self:
            if line.date_from < line.crossovered_budget_id.date_from or line.date_to > line.crossovered_budget_id.date_to:
                raise ValidationError(_("The period of lines must be within the period of budget"))

    @api.multi
    def write(self, vals):
        if 'general_budget_id' in vals or  'analytic_account_id' in vals:
            for line in self:
                if vals.get('general_budget_id') and vals.get('general_budget_id') != line.general_budget_id.id \
                or vals.get('analytic_account_id') and vals.get('analytic_account_id') != line.analytic_account_id.id:
                    if line.operation_id_from or line.operation_id_to:
                        raise UserError(_("You cann't modify budget which has transfer or increase operation!"))
                    if line.confirmation_ids:
                        raise UserError(_("You cann't modify budgets which has confirmation!"))
                    if line.practical_amount != 0:
                        raise UserError(_("You cann't modify budgets which already expense from it!"))
        return super(AccountBudgetLines, self).write(vals)

    @api.multi
    @api.constrains('total_operation','confirm','practical_amount','planned_amount', 'transfer_amount')
    def _check_budget_overdraw(self):
        for line in self:
            allow_budget_overdraw = line.crossovered_budget_id.allow_budget_overdraw
            if not allow_budget_overdraw and (line.residual  < 0):
                raise ValidationError( _('Budget can\'t go overdrow!'))

    @api.multi
    @api.depends('planned_amount','total_operation','date_to','date_from', 'transfer_amount')
    def _compute_theoritical_amount(self):
        """
        Inherit to add total_operation in theoritical_amount compute.
        """
        theo_amt = 0.00
        today = fields.Datetime.now()
        for line in self:
            # Used for the report
            if self.env.context.get('wizard_date_from') and self.env.context.get('wizard_date_to'):
                date_from = fields.Datetime.from_string(self.env.context.get('wizard_date_from'))
                date_to = fields.Datetime.from_string(self.env.context.get('wizard_date_to'))
                if date_from < fields.Datetime.from_string(line.date_from):
                    date_from = fields.Datetime.from_string(line.date_from)
                elif date_from > fields.Datetime.from_string(line.date_to):
                    date_from = False
                if date_to > fields.Datetime.from_string(line.date_to):
                    date_to = fields.Datetime.from_string(line.date_to)
                elif date_to < fields.Datetime.from_string(line.date_from):
                    date_to = False
                if date_from and date_to:
                    line_timedelta = fields.Datetime.from_string(line.date_to) - fields.Datetime.from_string(line.date_from)
                    elapsed_timedelta = date_to - date_from
                    if elapsed_timedelta.days > 0:
                        theo_amt = (elapsed_timedelta.total_seconds() / line_timedelta.total_seconds()) * (line.planned_amount + line.total_operation +line.transfer_amount)
            else:
                if line.paid_date:
                    if line.date_to and fields.Datetime.from_string(line.date_to) <= fields.Datetime.from_string(line.paid_date):
                        theo_amt = 0.00
                    else:
                        theo_amt = (line.planned_amount + line.total_operation +line.transfer_amount)
                elif line.date_from and line.date_to:
                    line_timedelta = fields.Datetime.from_string(line.date_to) - fields.Datetime.from_string(line.date_from)
                    elapsed_timedelta = fields.Datetime.from_string(today) - (fields.Datetime.from_string(line.date_from))
                    if elapsed_timedelta.days < 0:
                        # If the budget line has not started yet, theoretical amount should be zero
                        theo_amt = 0.00
                    elif line_timedelta.days > 0 and fields.Datetime.from_string(today) < fields.Datetime.from_string(line.date_to):
                        # If today is between the budget line date_from and date_to
                        theo_amt = (elapsed_timedelta.total_seconds() / line_timedelta.total_seconds()) * (line.planned_amount + line.total_operation +line.transfer_amount)
                    else:
                        theo_amt = (line.planned_amount + line.total_operation+line.transfer_amount)
            line.theoritical_amount = theo_amt


class AccountAnalytic(models.Model):

    _inherit = "account.analytic.account"


    @api.model
    def _default_user(self):
        return self.env.context.get('user_id', self.env.user.id)

    user_id= fields.Many2one('res.users',string='Responsible',required=True ,
        domain=lambda self: [("groups_id", "in", self.env.ref("account_budget_custom.group_budget_user").id)],default=_default_user,readonly=True)
    budget = fields.Boolean('Budget Required', default=True)
    budget_post_ids = fields.Many2many('account.budget.post', string='Budgetary Position')
    transferable = fields.Boolean('Transferable', default=True)
    stop = fields.Boolean('Stop')
    reserve = fields.Boolean('Reserve')
    tag_ids = fields.Many2many('account.analytic.tag', 'account_analytic_account_tag_rel', 'account_id', 'tag_id', string='Tags', copy=True , required=True)




class AccountAccountType(models.Model):

    _inherit =  "account.account.type"

    analytic_wk = fields.Boolean('Budget Check',
        help="Check if this type of account has to go through budget confirmation check.",default=True)


class AccountBudgetPost(models.Model):
    _inherit = "account.budget.post"

    code=fields.Char(string='Code')
    name=fields.Char('Name', required=True, translate=True)
    type = fields.Selection([
        ('in', 'In'),
        ('out', 'Out')], required=True, default='in')
    active = fields.Boolean(default=True, help="Set active to false to hide the Account Budget Post without removing it.")


    @api.multi
    def copy(self, default=None):
        self.ensure_one()
        default = dict(default or {}, name=_('%s (copy)') % self.name)
        return super(AccountBudgetPost, self).copy(default)

    @api.multi
    def _get_budget_position(self,account_id):
        positions_ids = self.search([])
        for post in positions_ids:
            if account_id in post.account_ids.ids:
                return post
        return False

    @api.multi
    @api.constrains('account_ids','type')
    def _check_account_ids_duplicate(self):
        positions_ids = self.search([('id','!=',self.id)])
        for post in self:
            for account in post.account_ids:
                for saved_post in positions_ids:
                    if account.id in saved_post.account_ids.ids and post.type == saved_post.type:
                        raise ValidationError(_('This account (%s) is already Enter in another Budgetary Position(%s).')%(account.name,saved_post.name))


    _sql_constraints = [
        ('name_Budgetary_uniq', 'unique (name,company_id)', _('Budgetary name must be unique.')),
        ('code_Budgetary_uniq', 'unique (code,company_id)', _('Budgetary Code must be unique.')),
    ]


class AccountMoveline(models.Model):
    _inherit = 'account.move.line'

    budget_line_id=fields.Many2one('crossovered.budget.lines', 'Budget Line')

    @api.multi
    @api.constrains('analytic_account_id', 'account_id')
    def _check_analytic_required(self):
        for rec in self:
            if rec.account_id.analytic_required and not rec.analytic_account_id:
                raise ValidationError(_('The %s must have  Analytic Account ')%(rec.account_id.name))

    @api.onchange('analytic_account_id')
    def onchange_analytic_account_id(self):
        if self.analytic_account_id and self.analytic_account_id.budget_post_ids:
            self.account_id=False
            accounts=[]
            for post in self.analytic_account_id.budget_post_ids:
                accounts+= post.account_ids.ids
            return {'domain': {'account_id': [('id', 'in', accounts)]}}


class AccountAccount(models.Model):
    _inherit = 'account.account'

    analytic_required = fields.Boolean("Analytic Required")
    budget_account = fields.Boolean("Budget Account")


class AccountInvoice(models.Model):

    _inherit = 'account.invoice'

    @api.multi
    def invoice_validate(self):
        """
        inherit workflow invoice_validate function
        to add budget check when the analytic account
        in invoice line is Budget Required
        @return: call super function
        """
        for invoice in self:
            date = invoice.date or invoice.date_invoice
            check=False
            for line in invoice.invoice_line_ids:
                if line.account_analytic_id.budget:
                    budget_line_ids=self.env['crossovered.budget.lines'].search([('analytic_account_id','=',line.account_analytic_id.id),('state','=','validate')])
                    if not budget_line_ids:
                        raise UserError(_("This analytic account (%s) is Budget Required ,And it is not included in any budget")%line.account_analytic_id.name)
                    for budget_line in budget_line_ids:
                        if line.account_id.id not in budget_line.general_budget_id.account_ids.ids:
                            continue
                        check=True
                        if not (date >= budget_line.date_from and date <= budget_line.date_to):
                            raise UserError(_("In This date (%s) analytic account (%s) whice is Budget Required ,Does not have budget")% (date,line.account_analytic_id.name))
                    if not check:
                        raise UserError(_("This account (%s) is not included in any Budgetary Positions ,With analytic account (%s) whice is Budget Required")% (line.account_id.name,line.account_analytic_id.name))
        return super(AccountInvoice, self).invoice_validate()

class AccountInvoiceline(models.Model):
    _inherit = 'account.invoice.line'

    @api.multi
    @api.constrains('account_analytic_id', 'account_id')
    def _check_analytic_required(self):
        for rec in self:
            if rec.account_id.analytic_required and not rec.account_analytic_id:
                raise ValidationError(_('The %s must have  Analytic Account ')%(rec.account_id.name))


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
