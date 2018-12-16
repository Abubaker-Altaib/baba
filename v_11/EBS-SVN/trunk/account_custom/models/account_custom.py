# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2018-2019 NCTR (<http://www.nctr.sd>).
#
##############################################################################

from odoo import api , fields,exceptions, models,_
from odoo.exceptions import UserError, ValidationError
import re


#class AccountSitting(models.Model):
#    _inherit = 'res.config.settings'

#    account_approve_ids = fields.One2many('account.approve')

'''class account_approve(models.Model):
    _name= 'account.approve'

    name= fields.Char()
    employee_ids= fields.Many2many("hr.employee", "account_approve_rel_hr_employee", "account_id", "employee_id", required= True)
    min_amount= fields.Float()
    max_amount= fields.Float()
    company_id = fields.Many2one('res.company')


class company(models.Model):
    _inherit = 'res.company'

    account_approve_ids = fields.One2many('account.approve','company_id')


class AccountSetting(models.TransientModel):
    _inherit = 'res.config.settings'

    company_id = fields.Many2one('res.company', string="Company", required=True,
                                 default=lambda self: self.env.user.company_id)

    account_approve_ids = fields.One2many(related="company_id.account_approve_ids")'''




class resPartner(models.Model):
    _inherit = 'res.partner'
    
    code = fields.Char(strin="code")
     
    _sql_constraints = [
        ('code_name_uniq', 'unique (code,name,company_id)', 'The code,name must be unique per company !')
    ]

    property_account_payable_id = fields.Many2one('account.account', company_dependent=True,
        string="Account Payable", oldname="property_account_payable",
        domain=[],
        help="This account will be used instead of the default one as the payable account for the current partner",
        required=True)
    property_account_receivable_id = fields.Many2one('account.account', company_dependent=True,
        string="Account Receivable", oldname="property_account_receivable",
        domain=[],
        help="This account will be used instead of the default one as the receivable account for the current partner",
        required=True)

class AccountAccount(models.Model):
    _inherit = 'account.account'

    @api.model
    def name_search(self, name, args ,  operator='ilike', limit=100):
        context = self._context
        if 'model' in context and context['model'] == 'res.partner':
            if 'field' in context and context['field'] =='receivable' :  
                domain = [('internal_type','=','receivable'),('deprecated','=',False)]
                if context['customer'] and context['supplier'] :
                    domain = [('internal_type','in',['receivable','payable']),('deprecated','=',False)]
                   
            if 'field' in context and context['field'] =='payable' :
                domain = [('internal_type','=','payable'),('deprecated','=',False)]
                if context['customer'] and context['supplier'] :
                    domain = [('internal_type','in',['receivable','payable']) ,('deprecated','=',False)]        
                
            records_ids = [record.id for record in self.env['account.account'].search(domain)]
          
            if records_ids:
                args.append(('id','in',records_ids))

        return super(AccountAccount, self).name_search(name, args, operator, limit)



class account_tax(models.Model):
    _inherit ='account.tax'


    #code = fields.Char(string ="Code" ,required = True)
    #date =fields.Date(string ="Date" ,required = True)
    code = fields.Char(string ="Code" ,required = False)
    date =fields.Date(string ="Date" ,required = False)
    #type_tax_use  = fields.Selection([("purchase","In"),("sale","Out")],"Tax Scope" ,required=True)
    type_tax_use  = fields.Selection([("purchase","In"),("sale","Out")],"Tax Scope" ,required=False)


    @api.constrains('amount_type')
    def _not_equel_zero(self):
        for record in self:
            if record.amount_type:
                if record.amount_type != 'group' and record.amount == 0:
                    raise Warning(_("The amoun can not equal zero !!!!!"))

    @api.multi
    def unlink(self):
        parameter_obj = self.env['ir.config_parameter']
        sale_tax=parameter_obj.search([('key','=','account.default_sale_tax_id'),('value','=',self.id)])
        purchase_tax=parameter_obj.search([('key','=','account.default_purchase_tax_id'),('value','=',self.id)])
        if sale_tax or purchase_tax:
            raise ValidationError(_("can't delete this record, Because it is referred to in Default Taxes!"))
        return super(AccountTax, self).unlink()

class account_analytic_tag(models.Model):
    _inherit = 'account.analytic.tag'
    
     
    _sql_constraints = [
        ('name_uniq', 'unique (name)', 'Analytic Tag Name must be unique!')
    ]


class account_fiscal_position(models.Model):
    _inherit = 'account.fiscal.position'
    
     
    _sql_constraints = [
        ('fiscal_name_uniq', 'unique (name)', 'Fiscal Position name must be unique!')
    ]
    

class AccountPaymentTerm(models.Model):
    _inherit ='account.payment.term'

    @api.multi
    def unlink(self):

        for payment_term in self:
            invoices=self.env['account.invoice'].search([('payment_term_id','=', payment_term.id)])
            if invoices :
               raise ValidationError(_("can't delete (%s), there is operation uses this payment term")%payment_term.name)
        return super(AccountPaymentTerm, self).unlink()


class currency(models.Model):
    _inherit ='res.currency'

    @api.constrains('name')
    def check_currency_name(self):
        if not all(x.isalpha() or x.isspace() for x in self.name):
            raise UserError(_("currency name must not contains numbers or symbols"))


    @api.constrains('symbol')
    def check_currency_symbol(self):
        if bool(re.search(r'\d', self.symbol)) :
            raise UserError(_("currency symbol must not contains numbers"))        
            




