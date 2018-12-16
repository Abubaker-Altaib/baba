# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################
from odoo import api , fields, models,_
from datetime import date, datetime
from odoo.exceptions import UserError, ValidationError
import odoo.addons.decimal_precision as dp
from odoo.tools import  DEFAULT_SERVER_DATE_FORMAT
import operator
# ---------------------------------------------------------
# Utils
# ---------------------------------------------------------


class AccountInvoice(models.Model):
        
    _inherit = 'account.invoice'

    ## override to replace general_budget_id.account_ids with general_budget_id.account_id
    @api.multi
    def invoice_validate(self):
        """
        inherit workflow invoice_validate function 
        to add budget check when the analytic account
        in invoice line is Budget Required
        @return: call super function 
        """
        for invoice in self:
            date = invoice.date or invoice.date_invoice
            check=False
            for line in invoice.invoice_line_ids:
                if line.account_analytic_id.budget:
                    budget_line_ids=self.env['crossovered.budget.lines'].search([('analytic_account_id','=',line.account_analytic_id.id),('date_from','<=',date),('date_to','>=',date),('crossovered_budget_id.state','=','validate')])
                    if not budget_line_ids:
                        raise UserError(_("This analytic account (%s) is Budget Required ,And it is not included in any budget *or* customer invoice date not in range of budget_line date")%line.account_analytic_id.name)
                    for budget_line in budget_line_ids:
                        #if line.account_id.id not in budget_line.general_budget_id.account_ids.ids:
                        if line.account_id.id != budget_line.general_budget_id.account_id.id:
                            continue
                        check=True

                        """if not :
                            raise UserError(_("In This date (%s) analytic account (%s) whice is Budget Required ,Does not have budget")% (date,line.account_analytic_id.name))
                            """
                    if not check:
                        raise UserError(_("This account (%s) is not included in any Budgetary Positions ,With analytic account (%s) whice is Budget Required *or* customer invoice date not in range of budget_line date")% (line.account_id.name,line.account_analytic_id.name))
        return super(AccountInvoice, self).invoice_validate()



class AccountBudgetLines(models.Model):
    """
    Account Budget Lines Budget Details
    One line of detail of the duration Budget representing planned amount, Actual, operation and confirmation
    for special account and analytic account in  Budget which it belong to
    """

    _inherit = "crossovered.budget.lines"
    _description = "Budget Line"
    _rec_name = 'name_position_analytic'

    state = fields.Selection([('draft','Draft'),('confirmed','Confirmed')] , default='draft')
    parent_account_budget_id = fields.Many2one('parent.account.budget' , string='Parent Account Budget')
    parent_account_id = fields.Many2one('account.account' , string='Parent Account')
    confirm= fields.Float(compute='_confirm_amt',string='Confirm Amount',digits=0,store=True)
    practical_amount = fields.Float(compute='_compute_practical_amount', string='Practical Amount', store=True)



    @api.one
    def action_budget_line_confirm(self):
        self.write({'state':'confirmed'})


    ## override to replace general_budget_id.account_ids with general_budget_id.account_id
    @api.multi
    @api.depends('confirmation_ids')
    def _confirm_amt(self):
        """
        This Method use to compute the confirm_amount from confirmation_ids
        @return: dictionary {record_id: confirmation amount}
        """
        for line in self:
            result = 0.0
            date_to = line.date_to
            date_from = line.date_from
            if line.general_budget_id:
                #acc_ids = line.general_budget_id.account_ids.ids
                acc_ids = [line.general_budget_id.account_id.id]
            if not date_from or not date_to:
                continue
            if line.analytic_account_id and acc_ids:
                self.env.cr.execute("""SELECT SUM(residual_amount) FROM account_budget_confirmation WHERE analytic_account_id =%s AND (date between to_date(%s,'yyyy-mm-dd') AND
                 to_date(%s,'yyyy-mm-dd')) AND  account_id = ANY(%s) and state='valid'""",(line.analytic_account_id.id, date_from, date_to,acc_ids))
                result = self.env.cr.fetchone()[0] or 0.0
            line.confirm =-result


    @api.model
    def name_search(self, name, args, operator='ilike', limit=100):
        """
        Inherit name_search method to add dynamic domain to budget_line and line_id fields
        """
        context = self._context
        if 'model' in context and context['model'] == 'account.budget.operation':
            if 'field' in context and context['field'] == 'line_id':
                if context['type'] == 'transfer':
                    domain = [('analytic_account_id','=',context['analytic_account_id'] )]

                if context['type'] == 'increase':
                    domain = [('analytic_account_id','=',context['line_ids_analytic_account_id'])]

                records_ids = [record.id for record in self.env['crossovered.budget.lines'].search(domain)]

                args.append(('id','in',records_ids))

            if 'field' in context and context['field'] == 'budget_line':
                _list = []
                if context['type'] == 'transfer':
                    line_ids = context['line_ids']

                    _list = [line['line_id'][0] for line in self.env['account.budget.operation'].resolve_2many_commands('line_ids', context['line_ids']) if line.get('id')]

                    for line in line_ids:
                        if line[2]:
                            _list.append(line[2]['line_id'])

                    domain = [('id','not in',_list)]

                records_ids = [record.id for record in self.env['crossovered.budget.lines'].search(domain)]

                args.append(('id','in',records_ids))

        return super(AccountBudgetLines, self).name_search(name, args, operator, limit)

    ## override to replace general_budget_id.account_ids with general_budget_id.account_id
    #Inherit to add depends
    @api.multi
    @api.depends('analytic_account_id.line_ids')
    def _compute_practical_amount(self):
        for line in self:
            result = 0.0
            #acc_ids = line.general_budget_id.account_ids.ids
            acc_ids = [line.general_budget_id.account_id.id]
            if acc_ids[0] != False:
                date_to = self.env.context.get('wizard_date_to') or line.date_to
                date_from = self.env.context.get('wizard_date_from') or line.date_from
                if line.analytic_account_id.id:
                    self.env.cr.execute("""
	            SELECT SUM(amount)
	            FROM account_analytic_line
	            WHERE account_id=%s
	                AND (date between to_date(%s,'yyyy-mm-dd') AND to_date(%s,'yyyy-mm-dd'))
	                AND general_account_id=ANY(%s)""",
	        (line.analytic_account_id.id, date_from, date_to, acc_ids,))
                    result = self.env.cr.fetchone()[0] or 0.0
                line.practical_amount = result
            else:
                line.practical_amount = 0


    # this function add contrain on general_budget_id field ,
    # so the user cant't select budgetary position that its account != parent_account_id
    @api.one
    @api.constrains('general_budget_id')
    def check_general_budget_id_parent(self):
        if self.general_budget_id.account_id.parent_id.id != self.parent_account_id.id:
            raise ValidationError(_("The parent of '%s' account is not'%s' ")%(self.general_budget_id.name,self.parent_account_id.name))


# ---------------------------------------------------------
#  Account budget  (Inherit)
# ---------------------------------------------------------

class CrossoveredBudget(models.Model):
    _inherit = "crossovered.budget"

    parent_account_budget_ids = fields.One2many('parent.account.budget','budget_id' , string='Parent Account Budgets')

    _sql_constraints = [
        ('name_unique', 'unique (name)', _('Budget name must be unique'))
    ]

    @api.constrains('name')
    def check_budget_name(self):
        if not all(x.isalpha() or x.isspace() for x in self.name):
            raise UserError(_("budget name should not contains symbols or numbers "))



    @api.multi
    def action_budget_confirm(self):
        """
        Inherit to check budget_line and date_from , date_to
        """
        if not self.crossovered_budget_line:
            raise ValidationError(_('Please Enter Budget Lines'))
        else:
            for line in self.crossovered_budget_line:
                if line.date_to == False or line.date_from == False:
                    raise ValidationError( _('Please Enter The Start Date And The End Date For The Budget Lines'))
                else:
                    self.write({'state': 'confirm'})
                    line.write({'state':'confirmed'})



class account_budget_post(models.Model):
    """
    Budgetary Position
    It add the code to the Budgetary Position,
    """
    _inherit = "account.budget.post"

    account_id = fields.Many2one ('account.account' , string='Account')

    def _check_account_ids(self, vals):
        # Raise an error to prevent the account.budget.post to have not specified account_ids.
        # This check is done on create because require=True doesn't work on Many2many fields.
        #if 'account_ids' in vals:
        #    account_ids = self.resolve_2many_commands('account_ids', vals['account_ids'])
        #else:
        #    account_ids = self.account_ids
        #if not account_ids:
        #    raise ValidationError(_('The budget must have at least one account.'))
        return True

    #this function prevent user to delete budgetary postion that has budget line
    @api.multi
    def unlink(self):
        for budgetary_position in self :
            budgetary=self.env['crossovered.budget.lines'].search([('general_budget_id','=',budgetary_position.id)])
            if budgetary:
                raise ValidationError(_('Can not  delete (%s) budgetary position! , it has budget lines')%budgetary_position.name)
        return super(account_budget_post, self).unlink()


    @api.multi
    def _get_budget_position(self,account_id):
        positions_ids = self.search([])
        for post in positions_ids:
            #if account_id in post.account_ids.ids:
            if account_id == post.account_id.id:
                return post
        return False



    _sql_constraints = [
        ('ligne_unique', 'unique (account_id)', _('Budgetary account must be unique'))
    ]



class ParentAccountBudget(models.Model):
    _name='parent.account.budget'

    account_id = fields.Many2one('account.account' , string='Account')
    amount = fields.Float(compute='_compute_amount', string='Amount')
    budget_id = fields.Many2one('crossovered.budget' , string='Budget')
    budget_line_ids = fields.One2many('crossovered.budget.lines' , 'parent_account_budget_id', string='budget lines')

    #this function add budget lines based on budgetary postions it found
    @api.multi
    def find_budgetary_positions(self):
        budgetary_positions=self.env['account.budget.post'].search([('account_id.parent_id','=',self.account_id.id)
                                                                   , ('account_id.internal_type', '!=' ,'view') ])
        for b in budgetary_positions :
            self.env["crossovered.budget.lines"].create({'parent_account_id':self.account_id.id,
                                                          'general_budget_id':b.id ,
                                                          'planned_amount' : 0 ,
                                                          'crossovered_budget_id' : self.budget_id.id ,
                                              'analytic_account_id':self.budget_id.analytic_account_id.id ,
                                               'date_from':self.budget_id.date_from ,
                                                'date_to': self.budget_id.date_to })

    @api.multi
    @api.depends('budget_line_ids')
    def _compute_amount(self):
        #this function compute amount by calculating planned amount for budget lines
        for line in self:
            budgetary_positions = self.env["crossovered.budget.lines"].search([('parent_account_id','=',line.account_id.id),
                                                                                ('crossovered_budget_id','=',line.budget_id.name)])

            amount = 0
            for b in budgetary_positions:
                amount = amount + b.planned_amount

            line.amount =  amount

    @api.multi
    def unlink(self):
        for account in self:
            budget_lines = self.env['crossovered.budget.lines'].search([('parent_account_id','=',self.account_id.id),
                                                             ('crossovered_budget_id','=',self.budget_id.id) ,
                                                               ('parent_account_budget_id','=',self.id) ]).unlink()
        return super(ParentAccountBudget, self).unlink()
