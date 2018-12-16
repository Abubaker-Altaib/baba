# -*- coding:utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools.safe_eval import safe_eval

from odoo.addons import decimal_precision as dp

class HrPayrollStructure(models.Model):
    _name = 'hr.payroll.structure'
    _inherit = ['hr.payroll.structure', 'mail.thread']

    _parent_name = "parent_id"
    _parent_store = True
    _parent_order = 'sequence, name'
    _order = 'parent_left'

    active = fields.Boolean(default=True,
        help="If the active field is set to false, it will allow you to hide the salary rule without removing it.")
    number = fields.Integer(required=False, )
    sequence = fields.Integer(required=True, index=True)
    amount = fields.Integer(string='Start Sector', required=True, track_visibility='onchange')
    margin = fields.Integer(string='Margin Time')
    age_pension = fields.Integer(string='Pension Age')
    code = fields.Char(string='Reference', required=False)
    parent_id = fields.Many2one('hr.payroll.structure',required=False,default=False)
    children_ids = fields.One2many('hr.payroll.structure', 'parent_id', string='Children', copy=True,readonly=True)
    level_id = fields.Many2one('hr.payroll.structure',required=False,domain=[('type','=','level')])
    structure_id = fields.Many2one('hr.payroll.structure',required=False, domain=[('type','=','structure')])
    grade_ids = fields.One2many('hr.payroll.structure','structure_id',required=True,readonly=True,domain=[('type','=','grade')])
    degree_ids = fields.One2many('hr.payroll.structure','structure_id',required=True,readonly=True,domain=[('type','=','degree')])
    structure_type = fields.Selection([
        ('educational', 'Educational'),
        ('general administration', 'General Administration'),
        ('both', 'Both'),
    ], string='Type', index=True, required=False,default='general administration')
    type = fields.Selection([
        ('structure', 'Structure'),
        ('level', 'Level'),
        ('grade', 'Grade'),
        ('degree', 'Degree'),
    ], string='Type', index=True, required=False)
    date_from= fields.Date('Start Date', required=False ,copy=False, track_visibility='onchange')
    date_to= fields.Date('End Date', required=False ,copy=False, track_visibility='onchange')
    job_ids = fields.One2many('hr.job','grade_id')
    parent_left = fields.Integer(string='Left Parent', index=True)
    parent_right = fields.Integer(string='Right Parent', index=True)
    job_count = fields.Integer(compute='_compute_job_count', type='integer')


    @api.multi
    def get_all_rules(self):
        """
        @return: returns a list of tuple (id, sequence) of rules that are maybe to apply
        """
        all_rules = []
        if  self.env.context.get('rules'):
            all_rules = self.env.context.get('rules')
        else:
            for struct in self:
                all_rules += struct.rule_ids._recursive_search_of_rules()
        
        return all_rules
        
    @api.one
    def _compute_job_count(self):
            self.job_count = self.env['hr.job'].search_count([('grade_id', '=', self.id)])

    @api.one
    @api.constrains('number')
    def _check_number(self):
        if self.number == 0:
            if self.type=='structure':
                raise ValidationError(_('The number of level must be grater than zero.'))
            if self.type=='level':
                raise ValidationError(_('The number of grate must be grater than zero.'))
            if self.type=='grade':
                raise ValidationError(_('The number of degree must be grater than zero.'))

    @api.one
    @api.constrains('name')
    def _check_name(self):
        if self.name:
            name_const=self.env['hr.payroll.structure']
            name_Result=[]
            if self.type=='structure':
                name_Result = name_const.search([('name','=',self.name),('type','=','structure'),('id','!=',self.id)])
                if name_Result:
                    raise ValidationError(_('The name of structure must be unique.'))
            if self.type=='level':
                name_Result = name_const.search([('name','=',self.name),('type','=','level'),('parent_id','=',self.parent_id.id),('id','!=',self.id)])
                if name_Result:
                    raise ValidationError(_('The name of level must be unique .'))
            if self.type=='grade':
                name_Result = name_const.search([('name','=',self.name),('type','=','grade'),('parent_id','=',self.parent_id.id),('structure_id','=',self.structure_id.id),('id','!=',self.id)])
                if name_Result:
                    raise ValidationError(_('The name of grate  must be unique.'))
            if self.type=='degree':
                name_Result = name_const.search([('name','=',self.name),('type','=','degree'),('parent_id','=',self.parent_id.id),('structure_id','=',self.structure_id.id),('level_id','=',self.level_id.id),('id','!=', self.id)])
                if name_Result:
                    raise ValidationError(_('The name of degrees  must be unique.'))


    @api.onchange('level_id')
    def _onchange_level_id(self):
        if self.type=='degree':
            self.parent_id=None




    @api.one
    @api.constrains('parent_id')
    def _check_parent(self):
        if self.parent_id:
            if len(self.parent_id.children_ids.ids)>self.parent_id.number:
                raise ValidationError(_('The child of %s  cant not be grater than planned.')%(self.parent_id.type))

            
    
class Job(models.Model):
    _inherit = "hr.job"

    grade_id = fields.Many2one('hr.payroll.structure',required=False,domain="[('type','=','grade')]")

class HrSalaryRule(models.Model):
    _inherit = 'hr.salary.rule'

    type = fields.Selection([
        ('public', 'Public'),
        ('special', 'Special'),
        ('incentives','Incentives'),
    ], string='Type', index=True)
    rule_type = fields.Selection([
        ('allowance', 'Allowance'),
        ('deduction', 'Deduction'),
    ], string='Rule Type', index=True, required=True,default='allowance')
    amount_select = fields.Selection([
        ('fix','Fixed Amount'),
        ('levels','Amount linked to levels'),
        ('grades','Amount linked to Grades'),
        ('degrees','Amount linked to Degrees'),
        ('percentage','Percentage (%)'),
        ('code', 'Python Code'),
    ], string='Amount Type', index=True, required=True, default='fix', help="The computation method for the rule amount.")
    deduct_absence = fields.Selection([
        ('day', 'Per Day'),
        ('hour', 'Per Hour'),
        ('none','None'),
    ], string='Deduction Absence', index=True, default='none',required=True)
    
    base_on = fields.Selection([
        ('fix','Fixed'),
        ('hour', 'Hour'),
        ('day', 'Day'),
        ('month', 'Month'),
        ('bi-month', 'Bi-month'),
        ('quarter', 'Quarter'),
        ('semi-annual', 'Semi-annual'),
        ('annual', 'Annual'),
        ('end', 'End of service'),
    ], string='Based On', index=True, default='month')
    qualifications_linked = fields.Boolean(string='Qualifications')
    Linked_to_sanctions = fields.Boolean(string='Penalty')
    start_date=fields.Date('Start Date')
    end_date=fields.Date('End Date')
    salary_amount_ids = fields.One2many('hr.salary.amount','salary_rule_id',required=False)
    amount_percentage_base = fields.Many2many('hr.salary.rule','hr_salary_rule_ids','hr_salary_rule_id','parent_rule_id',string='Percentage based on', help='result will be affected to a variable')
    account_id = fields.Many2one('account.account', 'Account', domain=[('deprecated', '=', False)])
    loan=fields.Boolean(string='Loan')

    @api.onchange('deduct_absence')
    def onchange_deduct_absence(self):
        if self.deduct_absence =='day':
           self.quantity="worked_days.WORK100.number_of_days"
        if self.deduct_absence =='hour':
           self.quantity="worked_days.WORK100.number_of_hours"
           
    @api.onchange('base_on')
    def onchange_base_on(self):
        if self.base_on =='day':
           self.quantity="worked_days.WORK100.number_of_days"
        if self.base_on =='hour':
           self.quantity="worked_days.WORK100.number_of_hours"
        
    
    @api.constrains('amount_percentage_base')
    def _check_sequence(self):
        for rec in self.amount_percentage_base:
            if rec.sequence > self.sequence:
                raise ValidationError(_('Please make salary rule %s  sequence less than %s sequence!!!!.') % (rec.name,self.name))
            if rec.id == self.id:
                raise ValidationError(_('You can not select salary rule %s for salary rule %s') % (rec.name,self.name))

    @api.constrains('sequence')
    def _check_seq_of_parent(self):
        records = self.env['hr.salary.rule'].search([])
        for rec in records:
            if self.id in rec.amount_percentage_base.ids:
                if self.sequence > rec.sequence:
                    raise ValidationError(_('You can make salary rule %s  sequence more than %s sequence!!!!.') % (self.name,rec.name))

    #TODO should add some checks on the type of result (should be float)
    @api.multi
    def _compute_rule(self, localdict):
        print (".....................here",localdict)
        """
        :param localdict: dictionary containing the environement in which to compute the rule
        :return: returns a tuple build as the base/amount computed, the quantity and the rate
        :rtype: (float, float, float)
        """
        self.ensure_one()
        clause_1 = ['&', ('date_to', '<=', localdict['payslip'].date_to), ('date_to', '>=', localdict['payslip'].date_from)]
        # OR if it starts between the given dates
        clause_2 = ['&', ('date_from', '<=', localdict['payslip'].date_to), ('date_from', '>=', localdict['payslip'].date_from)]
        # OR if it starts before the date_from and finish after the date_end (or never finish)
        clause_3 = ['&', ('date_from', '<=', localdict['payslip'].date_from), '|', ('date_to', '=', False), ('date_to', '>=', localdict['payslip'].date_to)]
        clause_final = [('expectation_type','=','allocation'),('contract_id','=',localdict['contract'].id),('employee_id','=',localdict['employee'].id),('salary_rule_id','=',self.id), '|', '|'] + clause_1 + clause_2 + clause_3
        exeption = self.env['hr.salary.expectation'].search(clause_final, limit=1)
        if exeption:
            return exeption.amount
        if self.amount_select == 'fix':
            try:
                return self.amount_fix, float(safe_eval(self.quantity, localdict)), 100.0
            except:
                raise UserError(_('Wrong quantity defined for salary rule %s (%s).') % (self.name, self.code))
        elif self.amount_select == 'levels':
            try:
                k = localdict['contract']
                fix_amount = 0.0
                if self.salary_amount_ids:
                    record = self.env['hr.salary.amount'].search([('salary_rule_id','=',self.id),
                         ('level_id','=',k.level_id.id)])
                    fix_amount = record.amount
                else:
                    fix_amount = k.level_id.amount
                return fix_amount, float(safe_eval(self.quantity, localdict)), 100.0
            except:
                raise UserError(_('Wrong quantity defined for salary rule %s (%s).') % (self.name, self.code))
        elif self.amount_select == 'grades':
            try:
                k = localdict['contract']
                fix_amount = 0.0
                if self.salary_amount_ids:
                    record = self.env['hr.salary.amount'].search([('salary_rule_id','=',self.id),
                         ('grade_id','=',k.grade_id.id)])
                    fix_amount = record.amount
                else:
                    fix_amoun = k.grade_id.amount
                return fix_amoun, float(safe_eval(self.quantity, localdict)), 100.0
            except:
                raise UserError(_('Wrong quantity defined for salary rule %s (%s).') % (self.name, self.code))
        elif self.amount_select == 'degrees':
            try:
                k = localdict['contract']
                fix_amount = 0.0
                if self.salary_amount_ids:
                    record = self.env['hr.salary.amount'].search([('salary_rule_id','=',self.id),
                        ('degree_id','=',k.degree_id.id)])
                    fix_amount = record.amount
                else:
                    fix_amount = k.degree_id.amount
                return fix_amount, float(safe_eval(self.quantity, localdict)), 100.0
            except:
                raise UserError(_('Wrong quantity defined for salary rule %s (%s).') % (self.name, self.code))
        elif self.amount_select == 'percentage':
            try:
                fix_amount = 0.0
                for x in self.amount_percentage_base:
                    if x.rule_type == 'allowance':
                        fix_amount += localdict.get(x.code, 0.0)
                    elif x.rule_type == 'deduction':
                        fix_amount -= localdict.get(x.code, 0.0)
                return (float(fix_amount), float(safe_eval(self.quantity, localdict)), self.amount_percentage)
            except:
                raise UserError(_('Wrong percentage base or quantity defined for salary rule %s (%s).') % (self.name, self.code))
        else:
            try:
                safe_eval(self.amount_python_compute, localdict, mode='exec', nocopy=True)
                return float(localdict['result']), 'result_qty' in localdict and localdict['result_qty'] or 1.0, 'result_rate' in localdict and localdict['result_rate'] or 100.0
            except:
                raise UserError(_('Wrong python code defined for salary rule %s (%s).') % (self.name, self.code))

    @api.multi
    def _satisfy_condition(self, localdict):
        """
        @param contract_id: id of hr.contract to be tested
        @return: returns True if the given rule match the condition for the given contract. Return False otherwise.
        """
        clause_1 = ['&', ('date_to', '<=', localdict['payslip'].date_to), ('date_to', '>=', localdict['payslip'].date_from)]

        # OR if it starts between the given dates
        clause_2 = ['&', ('date_from', '<=', localdict['payslip'].date_to), ('date_from', '>=', localdict['payslip'].date_from)]
        # OR if it starts before the date_from and finish after the date_end (or never finish)
        clause_3 = ['&', ('date_from', '<=', localdict['payslip'].date_from), '|', ('date_to', '=', False), ('date_to', '>=', localdict['payslip'].date_to)]
        clause_final = [('expectation_type','=','exclude'),('contract_id','=',localdict['contract'].id),('employee_id','=',localdict['employee'].id),('salary_rule_id','=',self.id), '|', '|'] + clause_1 + clause_2 + clause_3
        self.ensure_one()

        exeption = self.env['hr.salary.expectation'].search(clause_final)
        if exeption:
            return  False
        self.ensure_one()

        if self.condition_select == 'none':
            return True
        elif self.condition_select == 'range':
            try:
                result = safe_eval(self.condition_range, localdict)
                return self.condition_range_min <= result and result <= self.condition_range_max or False
            except:
                raise UserError(_('Wrong range condition defined for salary rule %s (%s).') % (self.name, self.code))
        else:  # python code
            try:
                safe_eval(self.condition_python, localdict, mode='exec', nocopy=True)
                return 'result' in localdict and localdict['result'] or False
            except:
                raise UserError(_('Wrong python condition defined for salary rule %s (%s).') % (self.name, self.code))


class SalaryAmount(models.Model):
    _name='hr.salary.amount'

    structure_id = fields.Many2one('hr.payroll.structure',required=True,domain=[('type','=','structure')])
    level_id = fields.Many2one('hr.payroll.structure',required=True,domain=[('type','=','level')])
    grade_id = fields.Many2one('hr.payroll.structure',domain=[('type','=','grade')])
    degree_id= fields.Many2one('hr.payroll.structure',domain=[('type','=','degree')])
    amount=fields.Float(required=True)
    salary_rule_id=fields.Many2one('hr.salary.rule')

    _sql_constraints = [
        ('name_line_uniq', 'unique (structure_id,level_id,grade_id,degree_id)', _('Line must be unique.')),
    ]



