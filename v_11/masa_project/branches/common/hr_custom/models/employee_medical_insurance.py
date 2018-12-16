# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2018-2019 NCTR (<http://www.nctr.sd>).
#
##############################################################################
from odoo import api , fields, models,_
from odoo.exceptions import ValidationError

class InsuranceCompany(models.Model):
    _name = "hr.insurance.company"

    name = fields.Char(string='Name', required=True)
    partner_id = fields.Many2one('res.partner', 'Partner')
    active = fields.Boolean('Active', default=True)

class InsuranceCategory(models.Model):
    _name = "hr.insurance.category"

    name = fields.Char(string='Name', required=True)
    code = fields.Char(string='Code', required=True)
    active = fields.Boolean('Active', default=True)
    insurance_company_id = fields.Many2one('hr.insurance.company', 'Insurance Company', required=True)
    category_ids = fields.Many2many('hr.employee.category', string='Employee Tags')
    
    
class InsuranceDocument(models.Model):
    _name = "hr.insurance.document"

    name = fields.Char(string='Name', required=True)
    code = fields.Char(string='Code', required=True)
    active = fields.Boolean('Active', default=True)
    start_date = fields.Date(string="Start Date", required=True)
    end_date = fields.Date(string="End Date")
    insurance_company_id = fields.Many2one('hr.insurance.company', 'Insurance Company', required=True)
    prices_ids = fields.One2many('hr.insurance.price','insurance_document_id', string="Prices")
    
    
class InsurancePrice(models.Model):
    _name = "hr.insurance.price"

    insurance_document_id = fields.Many2one('hr.insurance.company', 'Insurance Document')
    insurance_category_id = fields.Many2one('hr.insurance.category', 'Insurance Category', required=True)
    price = fields.Float(string="Price", required=True)
    relation = fields.Selection([('employee', 'Employee'),('father', 'Father'),
                                 ('mother', 'Mother'),
                                 ('daughter', 'Daughter'),
                                 ('son', 'Son'),
                                 ('husband', 'husband'),
                                 ('wife', 'Wife')], string='Relation', required=True, default='employee' )
                                 
                                 
class InsuranceEmployee(models.Model):
    _name = "hr.employee.insurance"
    
    start_date = fields.Date(string="Start Date", required=True)
    end_date = fields.Date(string="End Date")
    employee_id = fields.Many2one('hr.employee','Employee',required=True)
    insurance_company_id = fields.Many2one('hr.insurance.company', 'Insurance Company', required=True)
    insurance_document_id = fields.Many2one('hr.insurance.document', 'Insurance Document', required=True)
    insurance_category_id = fields.Many2one('hr.insurance.category', 'Insurance Category', required=True)
    type = fields.Selection([
        ('employee', 'By Employee'),
        ('company', 'By Company')], string='Type',  default='company',required=True)
    price = fields.Float(string="Price", required=True)
    relation_id = fields.Many2one('hr.employee.family', 'Relation')
    insurance_no = fields.Char(string='Insurance Number', required=True)
    state = fields.Selection([
        ('draft', 'New'),
        ('open', 'Running'),
        ('pending', 'Pending'),
        ('close', 'Expired'),
        ('cancel', 'Cancelled')
    ], readonly=True, string='Status',  default='draft')


    @api.onchange('insurance_company_id','employee_id')
    def onchange_company_employee(self):
        categories=[]
        for category in self.employee_id.category_ids:
            for price in self.insurance_document_id.prices_ids:
                if price.insurance_category_id==category: 
                    categories.append(price.insurance_category_id.id)
        
        return {'domain': {'insurance_category_id': [('id', 'in', categories)]}}


    @api.multi
    def set_draft(self):
        self.write({'state': 'draft'})

    @api.multi
    def set_open(self):
        self.write({'state': 'open'})

    @api.multi
    def set_pending(self):
        self.write({'state': 'pending'})

    @api.multi
    def set_close(self):
        self.write({'state': 'close'})

    @api.multi
    def set_cancel(self):
        self.write({'state': 'cancel'})

    

