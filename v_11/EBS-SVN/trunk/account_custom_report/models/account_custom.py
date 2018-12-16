# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2018-2019 NCTR (<http://www.nctr.sd>).
#
##############################################################################

from odoo import api , fields,exceptions, models,_

class account_approve(models.Model):
    _name= 'account.approve'
    name= fields.Char()
    employee_ids= fields.Many2many("hr.employee", required= True, string= "many2many_tags")
    min_amount= fields.Float()
    max_amount= fields.Float()


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


    code = fields.Char(string ="Code" ,required = True)
    date =fields.Date(string ="Date" ,required = True)
    type_tax_use  = fields.Selection([("purchase","In"),("sale","Out")],"Tax Scope" ,required=True)


    @api.constrains('amount_type')
    def _not_equel_zero(self):
        for record in self:
            if record.amount_type:
                if record.amount_type != 'group' and record.amount == 0:
                    raise Warning(_("The amoun can not equal zero !!!!!"))
