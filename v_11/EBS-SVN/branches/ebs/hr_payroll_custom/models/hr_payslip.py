# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2018-2019 NCTR (<http://www.nctr.sd>).
#
##############################################################################

from odoo import api , fields,exceptions, tools, models,_
from odoo.exceptions import ValidationError, UserError

from odoo.addons import decimal_precision as dp

class HrPayslipEmployees(models.Model):
    _inherit = "hr.payslip"
    
    # net= fields.Float(compute='_compute_total', string='Net', digits=dp.get_precision('Payroll'), store=True)
    # total_allowance= fields.Float(compute='_compute_total', string='Total Allowances', digits=dp.get_precision('Payroll'), store=True)
    # total_deduction= fields.Float(compute='_compute_total', string='Total Deduction', digits=dp.get_precision('Payroll'), store=True)
    # total_loan= fields.Float(compute='_compute_total', string='Total Loan', digits=dp.get_precision('Payroll'), store=True)
    type = fields.Selection([
        ('salary', 'Salary'),
        ('bounes', 'Bounes'),
    ], string='Type', index=True, copy=False)
    # line_ids = fields.One2many('hr.payslip.line', 'slip_id', string='Payslip Lines', readonly=True,
    #     states={'draft': [('readonly', False)]},domain=[('loan','=','False')])
    # loan_ids = fields.One2many('hr.payslip.line', 'slip_id', string='Payslip Lines', readonly=True,
    #     states={'draft': [('readonly', False)]}, domain=[('loan','=','True'),('rule_type','=','deduction')])
    
    
    @api.multi
    @api.depends('line_ids','loan_ids','line_ids.total')
    def _compute_total(self):
        for pay in self:
           net = 0.0
           total_allowance = 0.0
           total_deduction = 0.0
           total_loan = 0.0
           for line in pay.line_ids:
               if line.salary_rule_id.rule_type == 'allowance':
                   total_allowance += line.total
               else:
                   total_deduction += line.total

           for loan in pay.loan_ids :
                total_loan += line.total
           self.total_allowance = total_allowance
           self.total_deduction = total_deduction
           self.total_loan = total_loan      
           self.net = total_allowance - (total_deduction+total_loan)
          
    # @api.multi
    # def compute_sheet(self):
    #     for payslip in self:
    #         number = payslip.number or self.env['ir.sequence'].next_by_code('salary.slip')
    #         # delete old payslip lines
    #         payslip.line_ids.unlink()
    #         rules = [(rule.id, rule.sequence) for rule in payslip.bonus_ids]
    #         # set the list of contract for which the rules have to be applied
    #         # if we don't give the contract, then the rules to apply should be for all current contracts of the employee
    #         contract_ids = payslip.contract_id.ids or \
    #             self.get_contract(payslip.employee_id, payslip.date_from, payslip.date_to)
    #         lines = [(0, 0, line) for line in self.with_context({'rules':rules})._get_payslip_lines(contract_ids, payslip.id)]
    #         payslip.write({'line_ids': lines, 'number': number})
    #     return True
     
    
    #Modify domain to return unsuspended contracts
    @api.model
    def get_contract(self, employee, date_from, date_to):
        """
        @param employee: recordset of employee
        @param date_from: date field
        @param date_to: date field
        @param is_suspended: boolean field
        @return: returns the ids of all the contracts for the given employee that need to be considered for the given dates and  return unsuspended contracts
        """
        # a contract is valid if it ends between the given dates
        clause_1 = ['&', ('date_end', '<=', date_to), ('date_end', '>=', date_from)]
        # OR if it starts between the given dates
        clause_2 = ['&', ('date_start', '<=', date_to), ('date_start', '>=', date_from)]
        # OR if it starts before the date_from and finish after the date_end (or never finish)
        clause_3 = ['&', ('date_start', '<=', date_from), '|', ('date_end', '=', False), ('date_end', '>=', date_to)]
        clause_final = [('employee_id', '=', employee.id), ('employee_id.is_suspended', '=', False),('state', '=', 'open'), '|', '|'] + clause_1 + clause_2 +  clause_3 
        return self.env['hr.contract'].search(clause_final).ids


    def compute_rule_custom(self, rule_id, contract_id, employee_id):
        '''
        this function calculate (a) rule base on emoplyee salary structure
        :param : containing the 'rule' which should be computed based on 'contract' with
                 specific 'employee'
        :return: returns the rule total_amount computed
        :rtype: (float)
        '''

        class BrowsableObject(object):
            # prepare categories and rules structure
            def __init__(self, employee_id, dict, env):
                self.employee_id = employee_id
                self.dict = dict
                self.env = env

            def __getattr__(self, attr):
                return attr in self.dict and self.dict.__getitem__(attr) or 0.0

        rule = self.env['hr.salary.rule'].browse(rule_id)
        contract = self.env['hr.contract'].browse(contract_id)
        employee = self.env['hr.employee'].browse(employee_id)

        if len(rule) != 1 or len(contract) != 1 or len(employee) != 1:
            raise UserError(_("Wrong Rule, Contract or Employee"))

        categories = BrowsableObject(employee.id, {}, self.env)
        rules = BrowsableObject(employee.id, {}, self.env)
        baselocaldict = {'categories': categories, 'rules': rules}
        localdict = dict(baselocaldict, employee=employee, contract=contract)
        amount, qty, rate = rule._compute_rule(localdict)
        print("amount, qty, rate:",amount, qty, rate)
        total_amount = amount * qty * rate / 100.0
        return total_amount
            
        
        
class HrPayslipRun(models.Model):
    _inherit = 'hr.payslip.run'
    
    
    employee_ids = fields.Many2many('hr.employee', string='Employees', states={'draft': [('readonly', False)]}, readonly=True)
    struct_ids =  fields.Many2many('hr.payroll.structure',string='Salary Structure', states={'draft': [('readonly', False)]}, readonly=True)
    emp_categ_ids = fields.Many2many('hr.employee.category',string='Employees Category', states={'draft': [('readonly', False)]}, readonly=True)
    department_ids =  fields.Many2many('hr.department',string='Departments', states={'draft': [('readonly', False)]}, readonly=True)
    journal_id = fields.Many2one('account.journal', 'Salary Journal', states={'confirm': [('readonly', False)]}, readonly=True,
        default=lambda self: self.env['account.journal'].search([('type', '=', 'general')], limit=1))
    voucher_id = fields.Many2one('account.voucher', 'Accounting Entry', readonly=True, copy=False)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirm', 'Confirm'),
        ('approve', 'Approve'),
        ('close', 'Close'),
        ('cancel', 'Rejected'),
    ], string='Status', index=True, readonly=True, copy=False, default='draft')
    type = fields.Selection([
        ('salary', 'Salary'),
        ('bounes', 'Bounes'),
    ], string='Type', default='salary',  index=True, copy=False)

    
    @api.multi
    def compute_sheet(self):
    
        self.slip_ids.unlink()
        payslips = self.env['hr.payslip']
        
        from_date = self.date_start
        to_date = self.date_end
        contracts = self.get_contract(self.struct_ids, self.department_ids, self.emp_categ_ids, self.employee_ids, from_date,to_date)
        for contract in self.env['hr.contract'].browse(contracts):
            for employee in contract.employee_id:
                slip_data = self.env['hr.payslip'].with_context(contract=True).onchange_employee_id(from_date, to_date, employee.id, contract_id=contract.id)
                res = {
                    'employee_id': employee.id,
                    'name': slip_data['value'].get('name'),
                    'struct_id': slip_data['value'].get('struct_id'),
                    'contract_id': contract.id,
                    'payslip_run_id': self.id,
                    'input_line_ids': [(0, 0, x) for x in slip_data['value'].get('input_line_ids')],
                    'worked_days_line_ids': [(0, 0, x) for x in slip_data['value'].get('worked_days_line_ids')],
                    'date_from': from_date,
                    'date_to': to_date,
                    'credit_note': self.credit_note,
                    'company_id': employee.company_id.id,
                    'bonus_ids': [(6, 0, self.bonus_ids.ids)],
                }
                payslips += self.env['hr.payslip'].create(res)
        payslips.compute_sheet()
        return True
        
    @api.multi
    def draft_payslip_run(self):
        self.slip_ids.write({'state': 'draft'})
        return self.write({'state': 'draft'})
        
    @api.multi
    def confirm_payslip_run(self):
        self.slip_ids.write({'state': 'verify'})
        return self.write({'state': 'confirm'})
        
    @api.multi
    def approve_payslip_run(self):
        return self.write({'state': 'approve'})

    @api.multi
    def close_payslip_run(self):
        # for run in self:
        #     voucher_id= self.env['account.voucher'].create({
        #         'voucher_type': 'purchase',
        #         'journal_id':run.journal_id.id,
        #         'line_ids': [(0, 0, x) for x in run.get_voucher_line()],
        #     })
        self.slip_ids.write({'state': 'done'})
        #self.write({'state': 'close','voucher_id':voucher_id.id})
        return self.write({'state': 'close'})
        
    @api.multi
    def get_voucher_line(self):
        lines =[]    
        self.env.cr.execute("""
            select pl.salary_rule_id as salary_rule_id, 
            hc.analytic_account_id as analytic_account_id, 
            sum(COALESCE(pl.total,0)) as total 
            from hr_payslip_line pl 
            LEFT JOIN hr_contract hc ON (pl.contract_id=hc.id) 
            where pl.slip_id IN %s 
            group by  pl.salary_rule_id, hc.analytic_account_id""" , (tuple(self.slip_ids.ids),)) 

        res = self.env.cr.dictfetchall()
        rules = self.env['hr.salary.rule']
        for r in res:
            rule = rules.browse(r['salary_rule_id'])
            if not rule.account_id:
                raise UserError(_('salary_rule has no account!'))
               
            line = {
                'name' : rule.name,
                'account_id':rule.account_id.id,
                'quantity':1,
                'price_unit':round(r['total'], 2),
                'account_analytic_id':r['analytic_account_id'],
            }
            lines.append(line)
        return lines
   
    @api.multi
    def cancel_payslip_run(self):
        if self.voucher_id:
            self.voucher_id.cancel_voucher()
        self.slip_ids.write({'state': 'cancel'})
        return self.write({'state': 'cancel'})

        
    @api.multi
    def unlink(self):
        if any(self.filtered(lambda run: run.state not in ('draft', 'cancel'))):
            raise UserError(_('You cannot delete a payslip which is not draft or cancelled!'))
        return super(HrPayslipRun, self).unlink()
        
    @api.model
    def get_contract(self, struct_ids, department_ids, categ_ids, employee_ids, date_from, date_to):
        """
        @param employee: recordset of employee
        @param date_from: date field
        @param date_to: date field
        @return: returns the ids of all the contracts for the given employee that need to be considered for the given dates
        """

        # a contract is valid if it ends between the given dates
        clause_1 = ['&', ('date_end', '<=', date_to), ('date_end', '>=', date_from)]
        # OR if it starts between the given dates
        clause_2 = ['&', ('date_start', '<=', date_to), ('date_start', '>=', date_from)]
        # OR if it starts before the date_from and finish after the date_end (or never finish)
        clause_3 = ['&', ('date_start', '<=', date_from), '|', ('date_end', '=', False), ('date_end', '>=', date_to)]
        clause_final = [('employee_id.is_suspended', '=', False),('state', '=', 'open'), '|', '|'] + clause_1 + clause_2 + clause_3 
        
        if struct_ids:
            clause_final += [('struct_id', 'in', struct_ids.ids)]

        if department_ids:
        	clause_final += [('department_id', 'in', department_ids.ids)]
        if categ_ids:
        	clause_final += [('employee_id.category_ids', 'in', categ_ids.ids)]
        	
        if employee_ids:
        	clause_final += [('employee_id', 'in', employee_ids.ids)]
        return self.env['hr.contract'].search(clause_final).ids
    
    
class SalaryExpectations(models.Model):
    _name = 'hr.salary.expectation'
    _description = 'Salary Expectation'
    _inherit = ['mail.thread']

    name = fields.Char(readonly=True,default="New",string='Refrance')
    contract_id = fields.Many2one('hr.contract',string='Contract',track_visibility='onchange',required=True)
    employee_id = fields.Many2one('hr.employee',string='Employee',required=True,track_visibility='onchange')
    expectation_type = fields.Selection([
        ('allocation', 'Allocation'),
        ('exclude','Exclude')], 'Expectation Type',track_visibility='always',required=True)
    salary_rule_id = fields.Many2one('hr.salary.rule',string='Salary Rule',track_visibility='onchange',required=True)
    amount =  fields.Float(string='Amount',required=True,)
    date_from =  fields.Date(string='From Date',required=True,)
    date_to =  fields.Date(string='To Date')
    active =  fields.Boolean(string='Is Activ',default=True)