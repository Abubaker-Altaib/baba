# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

from odoo import api,fields, models,_
import odoo.addons.decimal_precision as dp
from odoo.exceptions import UserError, ValidationError
import time

class budget_operation_history(models.Model):
    """ This Class use for Keeping a record as log for each Budget operation (increase, transfer, ...) """
    
    _name = "account.budget.operation.history"
    
    _description = 'Budget Operation History'


    @api.multi
    def unlink(self):
        for s in self.read(['reference']):
            if s['reference'] is not None:
                raise ValidationError(_('Can not  delete operation history while it has a related operation !'))
        return super(budget_operation_history, self).unlink()
                
    reference= fields.Reference(selection=[('account.budget.operation', 'account.budget.operation')],size=128)
    budget_line_id_from= fields.Many2one('crossovered.budget.lines', 'From Budget line', readonly=True, ondelete='restrict')   
    budget_line_id_to= fields.Many2one('crossovered.budget.lines', 'To Budget line', readonly=True, ondelete='restrict')   
    amount=fields.Float('Amount', digits_compute=dp.get_precision('Account'), readonly=True)
    user_id= fields.Many2one('res.users', 'User', readonly=True,default=lambda self: self.env.user)
    company_id= fields.Many2one(related='budget_line_id_to.company_id',string='Company')
    date= fields.Date('Date', readonly=True,default=lambda *args: time.strftime('%Y-%m-%d'))
    name= fields.Selection([('transfer', 'Transfer'), ('increase', 'Increase'),
                                  ('confirm_transfer', 'Confirmation Transfer'),
                                  ('close_transfer', 'Closing Budget Transfer')],
                                  'Type' , readonly=True)


class AccountBudgetOperation(models.Model):
    """
    Account Budget Operation.
    Allow accountant to transfer special amount from multiple budget lines to another for plan budgets, Beside budget increase operation.   
    """
    _name = "account.budget.operation"
    _description = 'Budget Operations'

    name= fields.Char('Name', size=64, required=True,default='/')
    type= fields.Selection([('transfer', 'Transfer'), ('increase', 'Increase'), ('close', 'Close')],'Operation Type', 
                                 required=True, readonly=True, states={'draft':[('readonly', False)]},default='transfer')
    from_company_id= fields.Many2one('res.company', 'Details Company', required=True, readonly=True, 
                                           states={'draft':[('readonly', False)]},default=lambda self: self.env.user.company_id)       
    amount=fields.Float('Amount', digits_compute=dp.get_precision('Account'), readonly=True, 
                                 states={'draft':[('readonly', False)]}, 
                                 help="If the it's positive that's mean the amount  will increase this budget or it will decrease it.")
    budget_line= fields.Many2one('crossovered.budget.lines', 'To Budget Line')
    line_ids= fields.One2many('account.budget.operation.line', 'operation_id', 'Details',
                                      readonly=True, states={'draft':[('readonly', False)]})
    budget_type= fields.Selection([('plan', 'Plan Budget'), ('cash', 'Cash Budget')],'Budget Type', 
                                        required=True, readonly=True, states={'draft':[('readonly', False)]},default='plan')
    budget_line_ids= fields.Many2many('crossovered.budget.lines', 'account_budget_classification_rel', 'operation_id', 'budget_line_id', 'Accounts')
    state= fields.Selection([('draft', 'Draft'), ('complete', 'Waiting for Financial Manager Confirm'), 
                                    ('confirm', 'Waiting for General Manager Approve'), ('approve', 'Waiting for Execution'),
                                    ('done','Done'), ('cancel', 'Canceled')], 'Status', required=True, readonly=True,default='draft')
    transfer_type= fields.Selection([('from_multi','From Multi'),('to_multi','To Multi')], string="Transfer Type", default='to_multi')
    #_sql_constraints = [
       #('amount_check', "CHECK ((type='transfer') OR (amount > 0) OR (type='close'))",  _("Wrong amount, they must be positive")),
    #]

    @api.multi
    def unlink(self):
        for s in self.read(['state']):
            if s['state'] != 'draft':
                raise ValidationError(_('Can not  delete none draft  operation !'))
        return super(AccountBudgetOperation, self).unlink()

    @api.onchange('budget_type')
    def onchange_budget_type(self):
        if self.budget_type=='cash':
            self.type='transfer'

    @api.onchange('from_company_id')
    def onchange_company_id(self):
        """ 
        On change method when change the from company fields then 
        reset from_budget_line to False 
        """
        self.from_budget_line=False

    @api.multi                   
    def complete(self): 
        """
        Workflow function change state to complete and compute amount value & set operation number
        @return: True
        """
        for r in self:
            if r.type == 'close':
                for l in r.budget_line_ids:
                    if l.residual <= 0 :
                        raise ValidationError(_('To close budget line the residual balance must be greater than zero'))

            if (r.type=='transfer' or r.type=='increase') and not r.line_ids:
                raise ValidationError(_('You cannot complete Transfer/Increase Operations without any Budget line.'))
            for e in r.line_ids:
                if r.type=='transfer' and r.transfer_type == 'from_multi' and e.line_id.residual - e.amount <0:
                    raise ValidationError(_("The amount you try to transfer (%s) is more than %s residual (%s)!") % \
                         (e.amount, e.line_id.name_position_analytic, e.line_id.residual,))
                if r.type=='transfer' and r.transfer_type == 'to_multi' and r.budget_line.residual - e.amount <0:
                        raise ValidationError(_("The amount you try to transfer (%s) is more than %s residual (%s)!") % \
                             (e.amount, r.budget_line.name_position_analytic, r.budget_line.residual,))
            x=self.write({'state':'complete','name': r.name == '/' and 
                                     self.env['ir.sequence'].next_by_code('account.budget.operation') or 
                                     r.name, 'amount': r.type=='increase' and r.amount or sum([l.amount for l in r.line_ids])})
        return True

    @api.multi    
    def confirm(self):
        """
        Workflow function change state to confirm and 
        @return: True
        """
        return self.write({'state':'confirm'})
         
    @api.multi
    def approve(self):
        """
        Workflow function change state to approve and 
        @return: True
        """
        self.write({'state':'approve'})
        return True

    @api.multi   
    def cancel(self):
        """
        Workflow function change state to cancel and 
        @return: True
        """
        return self.write({'state':'cancel'})

    @api.multi
    def action_cancel_draft(self):
        """
        Workflow function change record state to 'draft', 
        @return: boolean True    
        """
        self.write({'state': 'draft'})
        return True

    #v9:
    def onchange_line_ids(self, cr, uid, ids, line_ids):
        """ 
		On change used to update to_amount when any change happened in 
            the account.budget.operation.line corresponding to account.budget.operation
            record
        
        @param line_ids: list of tuple of the all operation line values
        @return: dictionary of to_amount value to be change
        """
        '''return {'value': company == 'from' and {'from_budget_line':False} or
                        {'analytic_account_id':False, 'account_id':False}'''
    #v9:
    def onchange_ttype(self, cr, uid, ids, ttype):
        '''line_pool = self.pool.get('account.budget.operation.line')
        if ttype=='increase':
           line_ids = ids and line_pool.search(cr, uid, [('operation_id', '=', ids[0])]) or False
           if line_ids:
                line_pool.unlink(cr, uid, line_ids)
                return{'value': {'line_ids': [] } }
        return True'''
 
    @api.multi
    def done(self):
        """
        Execute the operation by calling transfer function in budget line and change state to done.
        """
        budget_lines = self.env['crossovered.budget.lines']
        budget_line_id = False
        r = self
        #CASE type='close'
        if r.type == 'close':
            for l in r.budget_line_ids:
                if l.residual <= 0 :
                    raise ValidationError(_('To close budget line the residual balance must be greater than zero'))
                    continue
                else:
                    line_list = []
                    obj_hist = self.env['account.budget.operation.history']
                    list_ids = obj_hist.search([('name','=', 'close_transfer')])
                    list_ids = [obj_hist.browse(x).budget_line_id_from.id for x in list_ids]
                    line_list = self.env['crossovered.budget.lines'].search([('analytic_account_id','=', l.analytic_account_id.id),\
                                 ('general_budget_id', '=', l.general_budget_id.id),\
                                 ('date_from','>=', l.date_to), ('id','not in',list_ids)], \
                                limit=1, order='date_from asc')
                    if not line_list :
                        raise ValidationError(_('%s can not be close because there is no budget line to move it to ')%(l.name_position_analytic))
                    if line_list:
                        line=budget_lines.browse(line_list)
                        to = {'budget_line': line.id, 'amount' : r.amount}
                        r.amount=l.residual
                        budget_line_id,history_ids = budget_lines.transfer(
                                                            {'type':'close_transfer', 
                                                            'line_ids': [{'line_id':l, 'amount':l.residual}], 
                                                            'to':to, 
                                                            'reference':self._name+','+str(r.id)})
                        self.write({'state':'done', 'budget_line':budget_line_id} )
        #CASE type ='transfer' OR 'increase'    
        else:
            to = {'budget_line': r.budget_line.id, 'amount' : r.amount}
            budget_line_id,history_ids = budget_lines.transfer( {'type':r.type, 'line_ids': r.line_ids, 'to':to, 'reference':self._name+','+str(r.id), 'transfer_type':r.transfer_type})
            self.write({'state':'done', 'budget_line':budget_line_id})
        return True

    @api.one
    @api.returns('self', lambda value: value.id)
    def copy(self,default=None):
        """Inherit copy method to reset name to /.
        
        @return: super copy method
        """
        line_obj=self.env['account.budget.operation.line']
        default = dict(default or {})
        default.update({'name': '/'})
        operation_id=super(AccountBudgetOperation, self).copy(default)
        for line in self.line_ids:
            line_obj.create({'line_id':line.line_id.id, 'amount':line.amount,'operation_id':operation_id})
        return operation_id


class AccountBudgetLineIds(models.Model):
    """
    Budget lines which want to transfer from and the amount to transfer from each one. 
    """
    _name = "account.budget.operation.line"
    _description = 'Budget Line Transfer From'

    @api.one
    @api.constrains('amount')  
    def _check_amount(self):
        """
        Constrain method to prohibit user from entering negative number.
        @return: Boolean True or False
        """
        for line in self:
            if line.amount<=0 :
                raise ValidationError(_('Wrong amount, they must be positive!.'))

    @api.one
    @api.constrains('line_id') 
    def _check_budget_transfer(self):
        for line in self.browse():
            if line.line_id.id == line.operation_id.budget_line.id:
                    raise ValidationError(_('You cannot Transfer to same budget line.'))

    name= fields.Char('Name', size=64, required=True,default='/')
    line_id= fields.Many2one('crossovered.budget.lines', 'Budget Line', required=True)
    to_budget_id= fields.Many2one('crossovered.budget.lines', 'To Budget Line')       
    amount=fields.Float('Amount', digits_compute=dp.get_precision('Account'), required=True,
                                help="If the it's positive that's mean the amount  will transfer from this budget to the main one and vice versa.")
    operation_id= fields.Many2one('account.budget.operation', 'Operation')


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
