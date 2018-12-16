
from odoo import api,models,fields
#osv.Model
class hr_config_settings_inherit(models.Model):
    """Inherits res.company to add feilds that spesify the employee types that can undergone the process.
    """
    _inherit = 'res.company'

    loan_employee = fields.Boolean(string='Loan for Employee' , default=True)
    loan_contractors = fields.Boolean(string='Loan for Contractors')
    loan_recruit = fields.Boolean(string='Loan for Recruit')
    loan_trainee = fields.Boolean(string='Loan for Trainee')


    # hr_loan settings
    max_employee =fields.Float(string="Max Percentage for Total Loans Per Employee", digits=(18,2) ,default=100)
    max_department =fields.Float(string="Max Percentage for Total Loans Per Department", digits=(18,2) ,default=100)
    allowed_number =fields.Integer(string="Allowed Number",help='Number of loans per employee , if its 0 thats mean no limit for number of loans',default=0)
    # group_tax = fields.Boolean("Use Taxes")
    salary_rule_id = fields.Many2one('hr.salary.rule','Salary')
    restrict_reject = fields.Boolean(string='Restrict Reject', default=False , 
                                 help='Restrict rejection of Loan Request \
                                        if the request does not meet all the conditions')

