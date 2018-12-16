 # -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2018-2019 NCTR (<http://www.nctr.sd>).
#
##############################################################################


from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools.safe_eval import safe_eval
from datetime import datetime

from odoo.addons import decimal_precision as dp

class HrPromotions(models.Model):

    _name = 'hr.promotions' 
    _description = 'Employee Promotions'
    _inherit = ['mail.thread']

    name =  fields.Char(default="/",string='Refrance',readonly=True, )
    employee_id =  fields.Many2one('hr.employee',string='Employee',required=True,track_visibility='onchange')
    struct_id =  fields.Many2one('hr.payroll.structure',string='Payroll Structure',)
    current_levle_id = fields.Many2one('hr.payroll.structure',string='Current Level',
        track_visibility='onchange',domain=[('type','=','level'),])

    new_levle_id = fields.Many2one('hr.payroll.structure',string='New Level',
            track_visibility='onchange', domain=[('type','=','level'),])

    current_grade_id = fields.Many2one('hr.payroll.structure',string='Current Grade',
            track_visibility='onchange' , domain=[('type','=','grade'),])
    new_grade_id = fields.Many2one('hr.payroll.structure',string='New Grade',
            track_visibility='onchange', domain=[('type','=','grade'),])

    current_degree_id = fields.Many2one('hr.payroll.structure',string='Current Degree',
            track_visibility='onchange',domain=[('type','=','degree'),] )
    new_degree_id = fields.Many2one('hr.payroll.structure',string='New Degree',
            track_visibility='onchange',domain=[('type','=','degree'),])

    date =  fields.Date(string='Date',required=True,default=datetime.today().date())
    approval_date =  fields.Date(string='Approval Date',track_visibility='always')
    current_bounes_date = fields.Date(string='Last Bounes Date',help='this feild is used to set the last bonus date of employee and to role back the employee data when cancel the process', )
    state = fields.Selection([
            ('draft', 'Draft'),
            ('approved', 'Approved'),
            ('canceled', 'Canceled'),
        ], string='State', default='draft' , readonly=True,track_visibility='onchange' )
    nots =  fields.Text(string='Nots',)

    @api.one
    def approve_promotions(self):

        if not self.new_levle_id or not self.new_grade_id or not self.new_degree_id :
            raise UserError(_('Please Add Employee Promotion Information '))
        #Search of employee permanent contract
        self.approval_date = datetime.today().date() 
        self.employee_id.contract_id.write({ 
                    'level_id':self.new_levle_id.id, 
                    'grade_id':self.new_grade_id.id,
                    'degree_id':self.new_degree_id.id,
                    'last_bonus_date':self.approval_date,
                    })
        self.state = 'approved'
        return 

    @api.one
    def cancel_promotions(self):
        # write on employee permanent contract  
        self.employee_id.contract_id.write({ 
                    'level_id':self.current_levle_id.id, 
                    'grade_id':self.current_grade_id.id,
                    'degree_id':self.current_degree_id.id,
                    'last_bonus_date':self.current_bounes_date,
                    })
        #Un link the approved data in case exist to start the process over
        self.new_levle_id  = False
        self.new_grade_id  = False
        self.new_degree_id = False
        self.state = 'canceled'

        return 

    

    @api.multi
    @api.onchange('employee_id')
    def onchange_employee_id(self):
        if not self.employee_id:
            return
        values = ({
                'struct_id': self.employee_id.struct_id.id,
                'current_levle_id':self.employee_id.level_id.id,
                'current_grade_id':self.employee_id.grade_id.id,
                'current_degree_id':self.employee_id.degree_id.id,
                'current_bounes_date':self.employee_id.last_bonus_date or self.employee_id.contract_id.date_start,
            })
        self.update(values)
        domain = {'new_levle_id': [('parent_id', '=', self.employee_id.contract_id.struct_id.id),('type','=','level'),],
                  'current_levle_id': [('parent_id', '=', self.employee_id.contract_id.struct_id.id),('type','=','level'),]}
        return {'domain': domain}
    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('hr.promotions') or '/'
        return super(HrPromotions, self).create(vals)

class HrBonusesLines(models.Model):

    _name = 'hr.bonuses.lines' 

    employee_id =  fields.Many2one('hr.employee',string='Employee',required=True,)
    levle_id = fields.Many2one('hr.payroll.structure',string='Level',)
    grade_id = fields.Many2one('hr.payroll.structure',string='Grade',)
    current_degree_id = fields.Many2one('hr.payroll.structure',string=' Degree',)
    new_degree_id = fields.Many2one('hr.payroll.structure',string='new Degree',)
    state = fields.Selection([
            ('draft', 'Draft'),
            ('approved', 'Approved'),
            ('canceled', 'canceled'),
        ], string='State', default='draft' ,)
    bonus_id =  fields.Many2one('hr.bonus',string='Employee Bonuses',)
    same_dgree =  fields.Boolean(string='',default =False,help='this filed is just used in view to change the employee recred how has the same dgree id with defrent color', )

    @api.multi
    def approve_bonuses(self):
        self.state = 'approved'
    
    @api.multi    
    def cancel_bonuses(self):
        self.state = 'canceled'

class HrBonus(models.Model):

    _name = 'hr.bonus' 
    _description = 'Employee Bonus'
    _inherit = ['mail.thread']

    name =  fields.Char(default="/",string='Refrance',readonly=True, track_visibility='always')
    date =  fields.Date(string='Date',required=True,default=datetime.today().date(),track_visibility='always')   
    approval_date =  fields.Date(string='Approval Date',track_visibility='always')
    structure_id = fields.Many2one('hr.payroll.structure',required=True,track_visibility='always')
    levle_ids = fields.Many2many('hr.payroll.structure',string='Level',track_visibility='always')
    state = fields.Selection([
            ('draft', 'Draft'),
            ('approved', 'Approved'),
            ('canceled', 'Canceled'),
        ], string='State', default='draft' ,track_visibility='always')
    margin = fields.Integer(string='Margin Time',track_visibility='always')
    bonus_lines =  fields.One2many('hr.bonuses.lines','bonus_id',string='Bonuses Candidates',)
    nots =  fields.Text(string='Nots',track_visibility='always')
    
    def compute_candidates(self):

        #Un link the previous candidates in case there's candidates
        if self.bonus_lines:
            self.bonus_lines.unlink()
        clause_final = []
        if self.levle_ids :
            clause_final += [('level_id', 'in', self.levle_ids.ids)]
        else :
            clause_final += [('struct_id','=',self.structure_id.id)]
        #search for employees that fit in strctuer or salry  level 
        
        employees = self.env['hr.employee'].search(clause_final).filtered(
            lambda r:(r.last_bonus_date or r.contract_id.date_start ) and r.degree_id
            and 
            (r.degree_id.margin - self.margin <=
            (fields.Date.from_string(self.date) - fields.Date.from_string(r.contract_id.last_bonus_date or r.contract_id.date_start)).days 
                and  (fields.Date.from_string(self.date) - fields.Date.from_string(r.contract_id.last_bonus_date or r.contract_id.date_start)).days  <=
            r.degree_id.margin + self.margin ))
       
        
        for employee in employees:
            self.bonus_lines.create({
                'employee_id':employee.id,
                'levle_id':employee.level_id.id,
                'grade_id':employee.grade_id.id,
                'current_degree_id':employee.degree_id.id,
                'new_degree_id':self.get_employee_next_degree(employee.degree_id),
                'state':'draft',
                'bonus_id':self.id,
                'same_dgree': employee.degree_id.id == self.get_employee_next_degree(employee.degree_id)
                })

    #note add param and descrption about this method please
    def approve_bonuses(self):
        
        if not self.bonus_lines :
            raise UserError(_('There is no candidates?!! '))
        self.state= 'approved'
        
        self.approval_date = datetime.today().date()
        for line in self.bonus_lines: 
            if line.state !='canceled':
                line.state = 'approved'
                line.employee_id.contract_id.write({ 
                    'level_id':line.levle_id.id, 
                    'grade_id':line.grade_id.id,
                    'degree_id':line.new_degree_id.id,
                    'last_bonus_date':self.approval_date,})


    def cancel_bonuses(self):
        self.state= 'canceled'
        self.bonus_lines.unlink()


    def get_employee_next_degree(self,degree_id):
        next_degree_id = self.env['hr.payroll.structure'].search([('parent_id','=',degree_id.parent_id.id),('type','=','degree'),('sequence','>',degree_id.sequence)],order='id asc',limit=1)
        return next_degree_id.id or degree_id.id


    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('hr.bonus') or '/'
        return super(HrBonus, self).create(vals)


    
