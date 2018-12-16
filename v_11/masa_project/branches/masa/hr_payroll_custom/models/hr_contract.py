# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2018-2019 NCTR (<http://www.nctr.sd>).
#
##############################################################################

from odoo import api , fields,exceptions, tools, models,_
from odoo.exceptions import ValidationError, UserError


class Contract(models.Model):
    _inherit = "hr.contract"
    
    is_suspended =  fields.Boolean(string='IS Suspended',readonly=True, deafult=False )
    expectation_ids  =  fields.One2many('hr.salary.expectation','contract_id',string='Salary Expectations ')
    salary_type = fields.Selection([
            ('fixAmount', 'Fixed Amount'),
            ('struct', 'Structure'),
            ('hourly', 'Hourly'),
        ], string='Salary type', default='fixAmount' ,required =True)
    level_id = fields.Many2one('hr.payroll.structure')
    grade_id = fields.Many2one('hr.payroll.structure' )
    degree_id = fields.Many2one('hr.payroll.structure')
    analytic_account_id = fields.Many2one('account.analytic.account', 'Analytic Account')
    social_insurance = fields.Boolean('Social Insurance', default=True)
    last_bonus_date = fields.Date('Last Bonus Date')
    
    @api.onchange('degree_id')
    def onchange_degree_id(self):
        if self.degree_id:
           self.wage = self.degree_id.amount
        else:
          self.wage = 0.0
           
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


    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('salary.expectation.lines') or 'new'
        return super(SalaryExpectations, self).create(vals)


    @api.model
    def  sechduler_method(self):
        """
        not yet 
        """
        print ('---------------------------------====')
        
class SalarySuspendUnsuspend(models.Model):
    _name = "hr.salary.suspend.unsuspend"
    _inherit = ['mail.thread']
    
    name =  fields.Char(string='Name',default="New",readonly=True, )
    date_from = fields.Date(string='From Date', required=True , track_visibility='onchange')
    date_to = fields.Date(string='To Date',track_visibility='onchange')
    suspended_reasons = fields.Text(string='Suspend Reasons',required=True ,track_visibility='onchange')
    employee_id =  fields.Many2one('hr.employee',string='Employee',required=True,track_visibility='onchange')
    contract_id =  fields.Many2one('hr.contract',string='Contract',required=True,track_visibility='onchange' )
    state= fields.Selection([
    	('draft', 'Draft'),
    	('suspended', 'Suspended') ,
    	('ususpended','USuspended')], 'Status',default='draft',track_visibility='always')


    @api.multi
    def suspend(self):
    	for rec in self:
	    	rec.contract_id.write({"is_suspended":True})
	    	rec.write({'state':'suspended'})
	   
    @api.multi
    def ususpend(self):
    	for rec in self:
    		rec.contract_id.write({"is_suspended":False})
    		rec.write({'state':'ususpended'})

    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('payroll.suspended.unsuspend') or 'new'
        return super(SalarySuspendUnsuspend, self).create(vals)

