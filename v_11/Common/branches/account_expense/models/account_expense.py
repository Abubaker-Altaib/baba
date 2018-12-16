# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.



from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from dateutil.relativedelta import relativedelta


class Product(models.Model):
    _inherit = 'product.product'
    
    
    allowed_employee_ids = fields.Many2many(
        'hr.employee', 'product_employee_rel','employee_id', string='Allowed Employees')
    allowed_department_ids = fields.Many2many(
        'hr.department', 'product_department_rel','department_id', string='Allowed Departments')
    allowed_job_ids = fields.Many2many(
        'hr.job', 'product_job_rel','job_id', string='Allowed Jobs')
    periodical = fields.Selection([
        ('once', 'Once'),
        ('annual', 'Annual'),
        ('monthly', 'Monthly')],string='Periodical',  size=32,)
    require_attachment = fields.Boolean(string="Requires an attachment")
    financial_era = fields.Boolean(string="Financial era")




class AccountVoucher(models.Model):
    _inherit = 'account.voucher'
            
    employee_id = fields.Many2one('hr.employee', string="Employee", required=True, readonly=True, 
        states={'submit': [('readonly', False)]}, 
        default=lambda self: self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1))
    department_id = fields.Many2one('hr.department', string='Department' , readonly=True, 
        states={'submit': [('readonly', False)]})
    state = fields.Selection([
        ('submit', 'To Submit'),
        ('complete', 'complete'),
        ('reported', 'Reported'),
        ('draft', 'Draft'),
        ('proforma', 'Pro-forma'),
        ('no_budget', 'Budget Not Appoved'),
        ('review', 'To Review'),
        ('confirm', 'To Confirm'),
        ('final_confirm', 'To Final Confirm'),
        ('approve', 'To Approve'),
        ('pay', 'To Pay'),
        ('paid', 'Paid'),
        ('posted', 'Posted'),
        ('refused', 'Refused'),
        ('cancel', 'Cancelled'),
        ],string='Status', readonly=True, size=32, track_visibility='onchange')
        
    priority=fields.Many2one('account.voucher.priority',string='Priority',readonly=True, states={'submit': [('readonly', False)]})
    color = fields.Selection(related='priority.color_name', store=True,string='Color')
    validity_date=fields.Date(string='Validity Date',readonly=True, states={'submit': [('readonly', False)]})
    attachment_number = fields.Integer(compute='_compute_attachment_number', string='Number of Attachments')
    account_analytic_id = fields.Many2one(related='department_id.account_analytic_id', string='Analytic Account')
    financial_era = fields.Boolean(related='journal_id.financial_era')


    


    @api.model
    def check_attach_lines(self):
        """
        Check If it Require an Attachment or not
        :raise: exception
        """
        for line in self.line_ids:
            if line.product_id.require_attachment == True:
                if self.attachment_number == 0:
                    raise ValidationError(_("Please Attach an File"))
            break

    @api.multi
    def copy(self, default=None):
        self.ensure_one()
        if self.state in ['submit','complete','reported']:
            default = dict(default or {}, state='submit')
        return super(AccountVoucher, self).copy(default)

    @api.multi
    def _compute_attachment_number(self):
        attachment_data = self.env['ir.attachment'].read_group([('res_model', '=', 'account.voucher'), ('res_id', 'in', self.ids)], ['res_id'], ['res_id'])
        attachment = dict((data['res_id'], data['res_id_count']) for data in attachment_data)
        for expense in self:
            expense.attachment_number = attachment.get(expense.id, 0) 

    @api.multi
    def week_range(self):
        """
        Find the first/last day of the week for the given day.
        Returns a tuple of ``(start_date, end_date)``.
        """
        date=fields.Date.from_string(self.date)
        year, week, dow = date.isocalendar()

        # Find the first day of the week.
        if dow == 6:
            start_date = date
        else:
            start_date = date - relativedelta(days=+1)
            st_year, st_week, st_dow = start_date.isocalendar()
            while st_dow != 6:
                start_date = start_date - relativedelta(days=+1)
                st_year, st_week, st_dow = start_date.isocalendar()
        end_date = start_date + relativedelta(days=+6)

        return (start_date, end_date)


    @api.multi
    @api.constrains('priority')
    def _check_priority(self):
        for expense in self:
            for line in expense.priority.line_ids:
                if expense.department_id == line.department_id:
                    result={}
                    limit=line.limit
                    if line.according_to == 'week':
                        start_date, end_date = self.week_range()
                        self.env.cr.execute("""
                            SELECT count(id)
                            FROM account_voucher
                            WHERE state not in ('refused','cancel') and department_id =%s and priority=%s and 
                                date BETWEEN %s AND %s""",
                        (expense.department_id.id, expense.priority.id, start_date, end_date))
                        result = self.env.cr.dictfetchall()[0]
                    elif line.according_to == 'month':
                        date=fields.Date.from_string(expense.date)
                        self.env.cr.execute("""
                            SELECT count(id)
                            FROM account_voucher
                            WHERE state not in ('refused','cancel') and department_id =%s and priority=%s and 
                                extract(month from date) = %s AND extract(year from date) = %s""",
                        (expense.department_id.id, expense.priority.id, str(date.month), str(date.year)))
                        result = self.env.cr.dictfetchall()[0]
                    elif line.according_to == 'year':
                        date=fields.Date.from_string(expense.date)
                        self.env.cr.execute("""
                            SELECT count(id)
                            FROM account_voucher
                            WHERE state not in ('refused','cancel') and department_id =%s and priority=%s AND extract(year from date) = %s""",
                        (expense.department_id.id, expense.priority.id,str(date.year)))
                        result = self.env.cr.dictfetchall()[0]
                    if result['count'] > limit:
                        raise ValidationError(_('Limit exceeded in This priority (%s) For requests')%(expense.priority.name))


            
    @api.multi
    def action_get_attachment_view(self):
        self.ensure_one()
        res = self.env['ir.actions.act_window'].for_xml_id('base', 'action_attachment')
        res['domain'] = [('res_model', '=', 'account.vouchere'), ('res_id', 'in', self.ids)]
        res['context'] = {'default_res_model': 'account.voucher', 'default_res_id': self.id}
        return res      
        
    @api.onchange('employee_id')
    def _onchange_employee_id(self):
        self.department_id = self.employee_id.department_id
            
    @api.multi
    def submit_expenses(self):
        self.check_attach_lines()
        self.write({'state': 'complete'})
        
    @api.multi
    def complete_voucher(self):
        line_obj = self.env['crossovered.budget.lines']
        for voucher in self:
            for line in voucher.line_ids:
                position = self.env['account.budget.post']._get_budget_position(line.account_id.id)
                if not position:
                    continue
                budget_line = line_obj.search([('analytic_account_id','=', line.account_analytic_id.id),
                    ('date_from','<=', voucher.date),
                    ('date_to','>=', voucher.date),
                    ('general_budget_id','=',position.id)])
                if budget_line:
                    if budget_line.state != 'validate':
                        raise ValidationError(_('The Budget not Validated yet!'))
                    else:
                        allow_budget_overdraw = budget_line.crossovered_budget_id.allow_budget_overdraw 
                        if not allow_budget_overdraw and  line.price_subtotal > budget_line.residual: 
                            raise ValidationError(_('The %s has no budget The residual is %s')%(line.account_id.name,budget_line.residual))
                # elif line.account_analytic_id.budget:
                #     raise ValidationError(_('The %s has no budget ')%(line.account_analytic_id.name))
                else:
                    raise ValidationError(_('The %s has no budget ')%(line.account_analytic_id.name))
        self.write({'state': 'reported'})
        
        
    @api.multi
    def action_to_edit(self):
        self.write({'state': 'submit'})




class AccountVoucherLine(models.Model):

    _inherit = 'account.voucher.line'


    @api.multi
    @api.onchange('account_id','account_analytic_id','price_unit')
    def _onchange_line(self):
        if self.account_id and self.account_analytic_id and self.voucher_id.date:
            line_obj = self.env['crossovered.budget.lines']
            position = self.env['account.budget.post']._get_budget_position(self.account_id.id)

            if position:
                budget_line = line_obj.search([('analytic_account_id','=', self.account_analytic_id.id),
                        ('date_from','<=', self.voucher_id.date),
                        ('date_to','>=', self.voucher_id.date),
                        ('general_budget_id','=',position.id)])
                if budget_line:
                    if budget_line.state != 'validate':
                        raise ValidationError(_('The Budget not Validated yet!'))
                    else:
                        allow_budget_overdraw = budget_line.crossovered_budget_id.allow_budget_overdraw 
                        if not allow_budget_overdraw and  self.price_subtotal > budget_line.residual: 
                            raise ValidationError(_('The %s has no budget The residual is %s')%(self.account_id.name,budget_line.residual))
                            # elif line.account_analytic_id.budget:
                            #     raise ValidationError(_('The %s has no budget ')%(line.account_analytic_id.name))
                else:
                    raise ValidationError(_('The %s has no budget ')%(self.account_analytic_id.name))


class Accountvoucherpriority(models.Model):
    _name='account.voucher.priority'

    name = fields.Char(string="Expense Requests Priority", required=True,copy=False)
    color = fields.Char(string='Color Index')
    color_name=fields.Selection([
        ('red','Red'),
        ('brown','Brown'),
        ('black','Black')], string='Colors', default='black')
    line_ids = fields.One2many('account.voucher.priority.line','priority_id',string='Priority Lines')

    _sql_constraints = [
        ('name_uniq', 'unique (name)', "Priority name already exists !"),
    ]
    
    @api.multi
    def copy(self, default=None):
        self.ensure_one()
        default = dict(default or {}, name=_('%s (copy)') % self.name)
        return super(Accountvoucherpriority, self).copy(default)

class AccountvoucherpriorityLine(models.Model):
    _name='account.voucher.priority.line'

    priority_id = fields.Many2one('account.voucher.priority',string="Expense Requests Priority")
    department_id = fields.Many2one('hr.department', string='Department')
    limit = fields.Integer(string='Limit')
    according_to=fields.Selection([
        ('week','Week'),
        ('month','Month'),
        ('year','Year')], string='According to', default='month')


class Department(models.Model):
    _inherit = "hr.department"

    account_analytic_id = fields.Many2one('account.analytic.account', 'Analytic Account')        
      
