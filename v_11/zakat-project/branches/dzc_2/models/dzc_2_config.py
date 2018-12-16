# -*- coding: utf-8 -*-

import re
import math
import datetime
from calendar import monthrange
from odoo import models, fields, api, exceptions ,_
from odoo.exceptions import ValidationError, AccessError

###################################################
# Committee of project 
##################################################
class Project_Committee(models.Model):
    _name = 'dzc2.project.project.committee'

    name = fields.Char(string='Name')
    state_id = fields.Many2one('zakat.state',string='State')
    employee_ids = fields.One2many('dzc2.project.employee' , 'committee_id' , string="Employees")
    company_id = fields.Many2one('res.company', string="Company", default=lambda self: self.env.user.company_id,
                                 ondelete='restrict')
    @api.constrains('name')
    def name_field_required(self):
        increment = 0
        if len(self.name) > 1 :
            for record in self.name[1:]:
                if record.isalpha() or record.isdigit():
                    increment +=1

                elif increment == 0 :
                    raise ValidationError(_("Sorry! Name Field is Required and Must begin with Char ."))

        elif len(self.name) <= 1 and self.name[0] == ' ':
            raise ValidationError(_("Sorry! Name Field is Required and Must begin with Char ."))

#################################
# Project Employee committee members
#################################
class Project_Employee(models.Model):
    _name = 'dzc2.project.employee'

    name = fields.Char(string="Employee Name" , required=True)
    committee_id = fields.Many2one('dzc2.project.project.committee' ,string='Field Label')
    
    _sql_constraints = [
        ('name_uniq', 'unique(name)',
         'Sorry! Employee Name Must Be Unique .')]

    @api.constrains('name')
    def _validate_name(self):
        for record in self:

            if record.name.isalpha() or ' ' in record.name:
                return True
            else:
                raise ValidationError(_('Sorry ! Name can not contain digits only chars.'))
 
    
###################################################
# PROJECTS
##################################################

class dzc2_project(models.Model):
    _name = 'dzc2.project'

    user_id = fields.Many2one('res.users', string="User", default=lambda self: self.env.user, ondelete='restrict')
    company_id = fields.Many2one('res.company', string="Company", default=lambda self: self.env.user.company_id, ondelete='restrict')
    name = fields.Char(string = "Name")
    code = fields.Integer( string = "Code")
    view_type = fields.Selection([('view','View'),('normal','Normal')], string = "Type of View")
    is_basic = fields.Boolean(string = 'Basic Root')
    project_type = fields.Selection([('individual_production','Individual Production'),('collective_production','Collective Production'),('service','Service')], string = "Type of Project")
    require_purchase_order = fields.Boolean(string = 'Require Purchase Order')
    require_exchange_order = fields.Boolean(string = 'Require Exchange Order')
    parent_ids = fields.Many2one('dzc2.project',string = "Parent" ,domain=[('view_type','=','view')])
    ###########rules###############
    case_study = fields.Boolean(String = "Case Study")
    managment_ability_confirmation = fields.Boolean(String = "Confirmation of the ability to manage the project")
    project_licence = fields.Boolean(String = "Licence")
    implementation_contracts = fields.Boolean(string ="Project Implementation Contracts")
    experience_certificate = fields.Boolean(string = "Experience Certificate")
    practicing_certificate = fields.Boolean(string = "Practicing Certificate")
    residence_certificate = fields.Boolean(string = "Residence Certificate")
    product_p_ids = fields.One2many('project.products.purchase' , 'project_id')
    product_e_ids = fields.One2many('project.products.exchange' , 'project_id')
    type_of_products = fields.Selection([('fixed' , 'Fixed') , ('not_fixed' , 'Not Fixed')])
    ###########sql constraints##############
    _sql_constraints = [
        ('code_uniq', 'unique(code)',
         'Sorry! Project Code Must Be Unique .')]

    @api.multi
    @api.constrains('name','parent_ids')
    def name_parent(self):
        for rec in self :
            if rec.parent_ids.name == rec.name :
                raise ValidationError(_('sorry! project name and parent name must be different'))
            else:
                True

    
    @api.constrains('name','code')
    def check_name(self):
        if not re.match("^[\u0600-\u065F\u066A-\u06EF\u06FA-\u06FFa-zA-Z]+[\u0600-\u065F\u066A-\u06EF\u06FA-\u06FFa-zA-Z-_]*$", self.name.replace(" ","")):
            raise ValidationError(_('name Field must be Literal'))
        if self.name and (len(self.name.replace(' ', '')) <= 0):
            raise exceptions.ValidationError(_("name must not be spaces"))
        if self.code <=0:
            raise exceptions.ValidationError(_("Code must not be minus or zero"))
    
class ProjectsProducsLines(models.Model):
    _name = 'project.products.purchase'
    product_id = fields.Many2one('product.product','Product')
    project_id = fields.Many2one('dzc2.project' , '')
    product_qty = fields.Integer(string='Quantity')

    @api.constrains('product_qty')
    def qty_check(self):
        if self.product_qty <= 0:
            raise ValidationError(_('Product Quantity must be grater than zero'))

class ProjectProducsLines(models.Model):
    _name = 'project.products.exchange'
    product_id = fields.Many2one('product.product','Product')
    project_id = fields.Many2one('dzc2.project' , '')
    product_qty = fields.Integer(string='Quantity')

    @api.constrains('product_qty')
    def qty_check(self):
        if self.product_qty <= 0:
            raise ValidationError(_('Product Quantity must be grater than zero'))
