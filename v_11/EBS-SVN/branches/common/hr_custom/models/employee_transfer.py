# -*- coding: utf-8 -*-
from odoo import models, fields, api, _


class EmployeeTransfer(models.Model):
    _name = 'hr.employee.transfer'
    _description = 'Employee Transfer'


    employee_id = fields.Many2one('hr.employee', string='Employee', required=True ,readonly=True, states={'draft': [('readonly', False)]})
    date = fields.Date(string='Date', default=fields.Date.today() , required=True)
    deparment = fields.Many2one('hr.department', string='Transfer Deparment' ,readonly=True, states={'draft': [('readonly', False)]} )
    state = fields.Selection(
        [('draft', 'New'), ('transfer', 'Transferred'), ('done', 'Done'),('cancel', 'Cancelled')],
        string='Status', readonly=True, copy=False, default='draft')
    name = fields.Char(string='Reference', readonly=True)
    current_job = fields.Many2one('hr.job', string='Current Job',readonly=True, states={'draft': [('readonly', False)]})
    current_department = fields.Many2one('hr.department',string='Current Department',readonly=True, states={'draft': [('readonly', False)]})
    new_job = fields.Many2one('hr.job',string='New Job',readonly=True, states={'draft': [('readonly', False)]})
    note = fields.Text(string='Internal Notes')
    tranfer_number = fields.Char(string="Number Of Transfer letter" ,readonly=True, states={'draft': [('readonly', False)]})
    type_tranfer =fields.Selection([('with','With Job'),('without','Without Job')],string="Type Of Transfer")
    type =fields.Selection([('deparment','Deparment'),('job','Job')],string="Type")

    @api.multi
    @api.onchange('employee_id')
    def employee_change(self):
    	if self.employee_id:
    	    self.current_job = self.employee_id.job_id.id
    	    self.current_department = self.employee_id.department_id

    @api.multi
    def transfer(self):
        self.write({'state': 'transfer'})

    @api.multi
    def receive_employee(self):
        job = self.current_job.id
        if self.new_job :
            job = self.new_job.id
        self.employee_id.write({'department_id': self.deparment.id , 'job_id':job})
        
        contract_ids = self.env['hr.contract'].search([('department_id','=',self.current_department.id),
              ('employee_id','=',self.employee_id.id),('state', 'in', ['draft', 'open', 'pending'])])
        if contract_ids:
           contract_ids.write({'department_id': self.deparment.id , 'job_id':job})
        self.write({'state': 'done'})
        
    @api.multi
    def change_job(self):
        self.employee_id.write({'job_id':self.new_job.id})
        
        contract_ids = self.env['hr.contract'].search([('job_id','=',self.current_job.id),
              ('employee_id','=',self.employee_id.id),('state', 'in', ['draft', 'open', 'pending'])])
        if contract_ids:
           contract_ids.write({'job_id':self.current_job.id})
        self.write({'state': 'done'})
        
    @api.multi
    def cancel(self):
        self.write({'state': 'cancel'})

    @api.one
    def set_draft(self):
        self.write({'state': 'draft'})

    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].get('employee.transfer')
        return super(EmployeeTransfer, self).create(vals)
