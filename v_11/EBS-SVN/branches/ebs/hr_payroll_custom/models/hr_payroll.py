from odoo import fields,models,api,_

class HrPayrollStructure(models.Model):
	_inherit = 'hr.payroll.structure'

	min_limit = fields.Float('Minimum Limit')
	max_limit = fields.Float('Maximum Limit')
	increase_rate = fields.Float('Increase Rate')
	margin_time = fields.Integer('Margin Time')

class HrSalaryRule(models.Model):
	_inherit = 'hr.salary.rule'
	rule_type = fields.Selection([('allow','Allowance'),('deduct','Deduction')],'Type')


########################## payslip for share #################################
class HrPayslip(models.Model):
    _inherit = 'hr.payslip'

    share_line_ids = fields.Many2many('hr.share.line',string='share lines')


    def get_inputs(self, contracts, date_from, date_to):
 
        res = super(HrPayslip, self).get_inputs(contracts, date_from, date_to)

        structure_ids = contracts.get_all_structures()
        rule_ids = self.env['hr.payroll.structure'].browse(structure_ids).get_all_rules()
        sorted_rule_ids = [id for id, sequence in sorted(rule_ids, key=lambda x:x[1])]
        inputs = self.env['hr.salary.rule'].browse(sorted_rule_ids).mapped('input_ids')
        emp_id = self.employee_id

        #search for share in deduction state 
        shares = self.env['hr.share'].search([('state','=','deduction'),('date','>=',date_from),('date','<=',date_to)])
        
        #count the total share amount for all the emp shares
        share_amount=0.0
        #list of all share line records to make their state deducted 
        share_lines = []
        for share in shares:
            for share_line in share.share_lines:
                if share_line.state == 'draft' and share_line.employee_id==emp_id :
                    share_amount+=share_line.amount
                    share_lines.append((4,share_line.id))

        if share_amount > 0 :
            input_data = {
                    'name': 'share',
                    'code': 'share',
                    'contract_id': contracts,
                    'amount':share_amount, 
                    'share_line_ids':share_lines}
            res += [input_data]  
            self.share_line_ids=share_lines
        return res

    # change state of computed share lines
    @api.multi
    def action_payslip_done(self):
        if self.share_line_ids:
            self.share_line_ids.write({'state': 'deducted'})
        return super(HrPayslip, self).action_payslip_done()


    # @api.onchange('employee_id', 'date_from', 'date_to')
    # def onchange_employee(self):
    #     if self.input_line_ids:
    #         self.input_line_ids=False
    #     if self.share_line_ids :    
    #         self.share_line_ids = False
    #     if self.loan_line_ids :
    #         self.loan_line_ids = False
        
    #     return super(HrPayslip,self).onchange_employee()

    # @api.constrains('date_from','date_to')
    # def peroid_constrain(self):
    #     if self.date_to < date_from :
    #         raise UserError(_("date to must be greater than date from"))


    ####################################################################### 
    @api.onchange('employee_id', 'date_from', 'date_to')
    def onchange_employee(self):
        self.input_line_ids = False
        return super(HrPayslip, self).onchange_employee()


class HrPayslipInput(models.Model):
    _inherit = 'hr.payslip.input'

    share_line_ids = fields.Many2many('hr.share.line',string='share lines')