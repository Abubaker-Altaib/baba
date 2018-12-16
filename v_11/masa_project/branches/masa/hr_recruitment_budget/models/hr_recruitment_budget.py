
from odoo import api , fields, models,_
from odoo.exceptions import ValidationError


class Job(models.Model):
    _inherit = "hr.job"

    grade_id = fields.Many2one('hr.payroll.structure',required=False,domain="[('type','=','grade')]")

class HrPayrollStructure(models.Model):
    _inherit = 'hr.payroll.structure'

    job_ids = fields.One2many('hr.job','grade_id')
    job_count = fields.Integer(compute='_compute_job_count', type='integer')

    @api.one
    def _compute_job_count(self):
            self.job_count = self.env['hr.job'].search_count([('grade_id', '=', self.id)])
 
class RecruitmentNeeds(models.Model):
    _inherit = "hr.recruitment.needs"

    @api.multi
    def action_compute(self):
        for rec in self:
            salary = 0.0
            if rec.job_id.grade_id:
                grade_id = rec.job_id.grade_id
                degree_id = self.env['hr.payroll.structure'].search([('sequence', '=', 1), 
                    ('parent_id', '=', grade_id.id)], limit=1)
                if degree_id:
                    for rule in grade_id.rule_ids:
                        if rule.rule_type == 'allowance' and not rule.special:
                            salary += self._compute_rule(rule, degree_id)
            rec.salary = salary
        return True

    @api.multi
    def _rule_amount_percentage(self, rule,  degree_id):
        amount_percentage = 0.0
        if rule.select_linked == 'levels':
            if rule.salary_amount_ids:
                record = self.env['hr.salary.amount'].search([('salary_rule_id','=',rule.id),
                   ('level_id','=',degree_id.level_id.id)])
                amount_percentage = record.amount or 0.0
            else:
                amount_percentage = degree_id.level_id.amount
        elif rule.select_linked == 'grades':
            if rule.salary_amount_ids:
                record = self.env['hr.salary.amount'].search([('salary_rule_id','=',rule.id),
                         ('grade_id','=',degree_id.parent_id.id)])
                amount_percentage = record.amount or 0.0
            else:
                amount_percentage = degree_id.parent_id.amount
        elif rule.select_linked == 'degrees':
           if rule.salary_amount_ids:
                record = self.env['hr.salary.amount'].search([('salary_rule_id','=',rule.id),
                        ('degree_id','=',degree_id.id)])
                amount_percentage = record.amount or 0.0
           else:
                amount_percentage = degree_id.amount
        else:
            if rule.amount_select == 'fix':
                amount_percentage = rule.amount_fix
            else:
                amount_percentage = rule.amount_percentage
        return amount_percentage


    @api.multi
    def _compute_rule(self, rule,  degree_id):

        if rule.amount_select == 'fix':
            amount_fix = self._rule_amount_percentage(rule,  degree_id)
            return amount_fix, float(safe_eval(self.quantity, localdict)), 100.0
            
        elif rule.amount_select == 'percentage':
            fix_amount = 0.0
            amount_percentage = self._rule_amount_percentage(rule,  degree_id)
            for x in rule.amount_percentage_base:
                allow_deduct = localdict.get(x.code, 0.0)
                fix_amount += allow_deduct
            return (float(fix_amount), float(safe_eval(rule.quantity, localdict)), amount_percentage)
            
        else:
            return 0.0
