# -*- coding: utf-8 -*-
import time
import babel
from odoo import models, fields, api, tools, _
from datetime import datetime
from dateutil import relativedelta
from odoo.exceptions import UserError


class hr_tax(models.Model):
    
    _name = "hr.tax"

    _description = "Tax Configuration"

   
    name =  fields.Char("Name", size=64, required=True, translate=True)
    taxset_min = fields.Float("Taxset Min" )
    taxset_max = fields.Float("Taxset Max")
    taxset_age = fields.Integer("Taxset Age", required=True)
    no_years_service = fields.Integer("Number of years service", required=True)
    percent  = fields.Float("Percent" )
    previous_tax  = fields.Float("Previous Tax")
    income_tax_percentage = fields.Float('Personal Tax Percentage',digits = (16,2), 
                  help="represents the percentage of salary that the tax will be taken from" , default=100)
    active = fields.Boolean('Active', default='True')
    


    @api.constrains('account_analytic_id')
    def _check_income_tax_percentage(self):
        """
        Constrain method that check digit you insert.

        @return: Boolean True or False
        """
        for tax in self: 
            if tax.income_tax_percentage < 0 :
               raise UserError(_("Income percentage must be greater than 0"))


    # def check_Taxset(self):
    #     res = []
    #     for tax in self:
    #         if tax.taxset_min < tax.taxset_max:
    #             res.append(rec.taxset_min)
    #     return res



    @api.constrains('taxset_age','no_years_service','taxset_min','taxset_max','percent','previous_tax')
    def check_not_zero(self):
        for tax in self:
            if tax.taxset_age < 0 or tax.no_years_service < 0  or tax.taxset_min < 0 or tax.taxset_max < 0 or tax.percent < 0 or tax.previous_tax < 0 :
                raise UserError(_("values of must be greater than  0"))
            if tax.taxset_min > tax.taxset_max:
                raise UserError(_("sorry the taxset_min is  Greater than taxset_max"))


    @api.constrains('id','taxset_min','taxset_max')   
    def _check_overlap(self):
        for tax in self:
            tax_ids = self.search([('taxset_max', '>=', tax.taxset_min), ('taxset_min', '<=', tax.taxset_max), ('id', '<>', tax.id)])
            if tax_ids:
                raise UserError(_("The tax is invalid. Taxes are overlapping"))
        return True
    
    # _constraints = [
    #     (check_Taxset, 'sorry the taxset_min is  Greater than taxset_max', ['taxset_min']),
    #     (check_not_zero, 'The value  must be more than zero!', ['Value Fields']),
    #     (_check_overlap, 'Error!\nThe tax is invalid. Taxes are overlapping ', ['taxset_max']),
    #     (_check_income_tax_percentage, 'Please insert the right digit', ['personal tax']),     
    #                 ]
    # _sql_constraints = [
    #      ('name_unique', 'unique(name)', _('The name of tax should be unique!')),
    # ]



    @api.one  
    def copy(self,default=None):
        if default is None:
            default = {}
        default.update({'name':None, 'taxset_min':0.00, 'percent':0.00, 'previous_tax':0.00})
        return super(hr_tax, self).copy(default=default)