# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2018-2019 NCTR (<http://www.nctr.sd>).
#
##############################################################################

from odoo import api,fields, models,_
import odoo.addons.decimal_precision as dp
from odoo.exceptions import UserError, ValidationError
import time

class AccountBudgetOperation(models.Model):

    _name = "account.budget.operation"
    _description = 'Budget Operations'
    
    name= fields.Char(copy=False, required=True,default='/')
    reference= fields.Char(copy=False)
    date= fields.Date('Date', required=True, readonly=True, 
        states={'draft':[('readonly', False)]}, default=lambda *args: time.strftime('%Y-%m-%d'))
    type= fields.Selection([('transfer', 'Transfer'), 
        ('increase', 'Increase')],'Operation Type',required=True, readonly=True, 
        states={'draft':[('readonly', False)]},default='transfer')
    company_id= fields.Many2one('res.company', 'Details Company', required=True, readonly=True, 
         states={'draft':[('readonly', False)]},default=lambda self: self.env.user.company_id)       
    amount=fields.Float('Amount', digits=0,readonly=True, 
         states={'draft':[('readonly', False)]})
    line_ids= fields.One2many('account.budget.operation.line', 'operation_id', 'Details',
                                      readonly=True, states={'draft':[('readonly', False)]})
    state= fields.Selection([('draft', 'Draft'), ('confirm', 'Confirmed'),
                             ('done','Done'), ('cancel', 'Canceled')], 'Status', required=True, readonly=True,default='draft')
    from_analytic_account_id = fields.Many2one('account.analytic.account', 'From Analytic Account', 
        required=True, readonly=True, states={'draft':[('readonly', False)]})
    to_analytic_account_id = fields.Many2one('account.analytic.account', 'To Analytic Account', required=True, readonly=True, 
        states={'draft':[('readonly', False)]})
    note =fields.Text('Note')

    @api.onchange('type')
    def _onchange_type(self):
        self.from_analytic_account_id=False
        self.to_analytic_account_id= False
        if self.type == 'increase':
            #return {'domain': {'from_analytic_account_id': [('reserve', '=', True),('company_id','=',self.company_id.id),('type','=','normal')]}}
            return {'domain': {'from_analytic_account_id': [('company_id','=',self.company_id.id),('type','=','normal')]}}
        else:
            #return {'domain': {'from_analytic_account_id': [('transferable', '=', True),('company_id','=',self.company_id.id),('type','=','normal')]}}
            return {'domain': {'from_analytic_account_id': [('company_id','=',self.company_id.id),('type','=','normal')]}}
        

    @api.multi
    def unlink(self):
        for rec in self:
            if rec.order.state !='draft':
                raise UserError(_('You can not delete none draft operation.'))
        return super(AccountBudgetOperation, self).unlink()

    @api.multi                   
    def confirm(self): 
        for rec in self:
            if  not rec.line_ids:
                raise ValidationError(_('You can not complete Operation without any line.'))
            for line in rec.line_ids:
                if  line.budget_line_id_from and line.budget_line_id_from.residual - line.amount < 0:
                    raise ValidationError(_("The amount you try to transfer (%s) is more than %s residual (%s)!") % \
                         (line.amount, line.budget_line_id_from.name_position_analytic, line.budget_line_id_from.residual,))
            
        self.write({
                'state':'confirm',
                'name': rec.name == '/' and self.env['ir.sequence'].next_by_code('account.budget.operation') or rec.name, 
                'amount': rec.amount or sum([l.amount for l in rec.line_ids])
            })
        self.line_ids.write({'state': 'confirm'})
        return True

    @api.multi   
    def cancel(self):
        self.line_ids.write({'state': 'draft'})
        return self.write({'state':'cancel'})

    @api.multi
    def action_cancel_draft(self):
        self.line_ids.write({'state': 'draft'})
        return self.write({'state': 'draft'})

    @api.multi
    def done(self):
        self.line_ids.write({'state':'done','name':self.type,'date':self.date})
        return self.write({'state':'done'})


class AccountBudgetOperationLine(models.Model):

    _name = "account.budget.operation.line"
    _description = 'Budget Line Transfer From'


    budget_line_id_from= fields.Many2one('crossovered.budget.lines', 'From Budgetary Positions', 
        required=True, ondelete='restrict')   
    budget_line_id_to= fields.Many2one('crossovered.budget.lines', 'To Budgetary Positions', 
        required=True, ondelete='restrict')             
    analytic_account_id_from = fields.Many2one('account.analytic.account', 'From Analytic Account')
    analytic_account_id_to = fields.Many2one('account.analytic.account', 'To Analytic Account')
    amount=fields.Float('Amount', digits=0, required=True)
    operation_id= fields.Many2one('account.budget.operation', 'Operation')
    company_id= fields.Many2one(related='operation_id.company_id',string='Company')
    date= fields.Date('Date')
    name= fields.Selection([('transfer', 'Transfer'), 
                           ('increase', 'Increase'),
                           ('close', 'Close')], 'Type' , readonly=True, states={'draft':[('readonly', False)]})
    state= fields.Selection([('draft', 'Draft'), ('confirm', 'Confirmed'),
                             ('done','Done'), ('cancel', 'Canceled')], 'Status', required=True, readonly=True,default='draft')
                             
    @api.one
    @api.constrains('amount')  
    def _check_amount(self):
        for line in self:
            if line.amount<=0 :
                raise ValidationError(_('Wrong amount, they must be positive!.'))

    @api.one
    @api.constrains('line_id') 
    def _check_budget_transfer(self):
        for line in self:
            if line.budget_line_id_from == line.budget_line_id_to:
                    raise ValidationError(_('You cannot Transfer to same budget line.'))


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
