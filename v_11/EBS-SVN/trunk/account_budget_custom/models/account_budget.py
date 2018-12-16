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
def strToDate(dt):
    return date(int(dt[0:4]), int(dt[5:7]), int(dt[8:10]))

def strToDatetime(strdate):
    return datetime.strptime(strdate, DEFAULT_SERVER_DATE_FORMAT)
    
class AccountInvoice(models.Model):
        
    _inherit = 'account.invoice'

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
            """for line in invoice.invoice_line_ids:
                if line.account_analytic_id.budget:
                    budget_line_ids=self.env['crossovered.budget.lines'].search([('analytic_account_id','=',line.account_analytic_id.id),('date_from','<=',date),('date_to','>=',date)])
                    if not budget_line_ids:
                        raise UserError(_("This analytic account (%s) is Budget Required ,And it is not included in any budget *or* customer invoice date not in range of budget_line date")%line.account_analytic_id.name)
                    for budget_line in budget_line_ids:
                        if line.account_id.id not in budget_line.general_budget_id.account_ids.ids:
                            continue
                        check=True

                    if not check:
                        raise UserError(_("This account (%s) is not included in any Budgetary Positions ,With analytic account (%s) whice is Budget Required *or* customer invoice date not in range of budget_line date")% (line.account_id.name,line.account_analytic_id.name))"""
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


    @api.multi
    def _get_operation_line_ids(self):
        """ 
        Method used by functional field to return budget line IDs which where found on the
        operation history object.
        Budget line ID could be found on budget_line_id_from or budget_line_id_to fields in 
        history object based on operation type.

        @return: list of IDS    
        """
        lines = self.env['account.budget.operation.history'].read(['budget_line_id_from','budget_line_id_to'])
        return reduce(operator.add,[[l['budget_line_id_from'] and l['budget_line_id_from'][0],l['budget_line_id_to'] and l['budget_line_id_to'][0]] for l in lines])

    @api.multi
    def _get_confirm_ids(self):
        """
        get records of budget line to be updated
        @param ids: ids in account asset history
        return dictionary Keys
        """
        result = []
        for line in self.env['account.budget.confirmation'].browse():
            if line.state=='valid':
                position = self.env['account.budget.post']._get_budget_position(line.account_id.id)
                if position :
                    result = result + self.env['crossovered.budget.lines'].search([
                                         ('general_budget_id','=',position.id),
                                         ('analytic_account_id', '=', line.analytic_account_id.id),
                                         ('date_from','<=',line.date),
                                         ('date_to','>=',line.date)])
            else:
                continue
        return result

    @api.multi
    def _get_ids(self):
        """
        get records of budget line to be updated
        @param ids: ids in account asset history
        return dictionary Keys
        """               
        result = []
        for line in self.env['account.analytic.line'].browse():
            position = self.env['account.budget.post']._get_budget_position(line.general_account_id.id)
            if position:
                result = result + self.env['crossovered.budget.lines'].search([
                                            ('general_budget_id','=',position.id),
                                            ('analytic_account_id', '=', line.account_id.id),
                                            ('date_from','<=',line.date),
                                            ('date_to','>=',line.date)])
        return result
    
    name_position_analytic =fields.Char(compute='_budget_name_code',store=True, string='Name')
    code=fields.Char(compute='_budget_name_code',store=True, string='Code')
    residual = fields.Float(compute='_residual_balance', string='Residual Balance', store=True)
    analytic_account_id = fields.Many2one('account.analytic.account', 'Analytic Account', required=True)
    date_from = fields.Date('Start Date')
    date_to = fields.Date('End Date')
    theoritical_amount = fields.Float(compute='_compute_theoritical_amount', string='Theoretical Amount', digits=0,store=True)

    total_operation= fields.Float(compute='_operation_amt',string='In/De-crease Amount',digits=0,store=True)
    confirm= fields.Float(compute='_confirm_amt',string='Confirm Amount',digits=0,store=True)
    confirmation_ids=fields.One2many('account.budget.confirmation', 'budget_line_id', 'Confirmations')
    practical_amount = fields.Float(compute='_compute_practical_amount', string='Practical Amount', store=True)
    percentage = fields.Float(compute='_compute_percentage', string='Achievement', store=True)
    #add One2many fields to recompute total_operation field
    operation_id_from= fields.One2many('account.budget.operation.history', 'budget_line_id_from',string='line operation history From')   
    operation_id_to= fields.One2many('account.budget.operation.history', 'budget_line_id_to', string='line operation history To')   
    parent_account_id = fields.Many2one('account.account', 'Parent Account')


    #Inherit to add depends
    @api.multi
    @api.depends('practical_amount')
    def _compute_percentage(self):
        super(AccountBudgetLines, self)._compute_percentage()

    #Inherit to add depends
    @api.multi
    @api.depends('analytic_account_id.line_ids')
    def _compute_practical_amount(self):
        super(AccountBudgetLines, self)._compute_practical_amount()
    
  
    @api.multi
    @api.depends('planned_amount','practical_amount','confirm','total_operation')
    def _residual_balance(self):
        """
        This Method use to compute the actual_balance & the residual_balance for each budget_line.
                    
        @return: dictionary of residual balance for each budget line
        """
        for line in self: 
            line.residual = line.planned_amount + line.total_operation + line.practical_amount + line.confirm
              
    @api.multi
    @api.depends('general_budget_id','analytic_account_id','date_from','date_to')
    def _budget_name_code(self):
        """ 
        Global Function to get NAME & CODE for Budget Lines
        base on general_account, analytic_account.
        
        @param char field_name_position_analytic: functional field name,
        @return: name & code of each record    
        """

        for line in self: 
            analytic = line.analytic_account_id
            account = line.general_budget_id
            #name=str((account.name).encode('utf8') or ' ') + ' ' + str((analytic.name).encode('utf8') or ' ') + ' ' + (line.date_from  or ' ' )+ ' to ' + (line.date_to or ' ')
            #code= str((account.code and str((account.code).encode('utf8'))) or ' ' )+ ' ' + str((analytic.code and  str((analytic.code).encode('utf8')))  or ' ')
            name=str(account.name or ' ') + ' ' + str(analytic.name or ' ') + ' ' + (line.date_from  or ' ' )+ ' to ' + (line.date_to or ' ')
            code= str((account.code and str(account.code)) or ' ' )+ ' ' + str((analytic.code and  str(analytic.code))  or ' ')
            line.name_position_analytic=name
            line.code=code

    @api.multi
    @api.constrains('date_from','date_to','analytic_account_id','general_budget_id')
    def _check_year_limit(self):
        list_ids=self.search([('crossovered_budget_id', '=',self.crossovered_budget_id.id)])
        #this if to enable copy with date false
        if self.date_from != False and self.date_to != False:
            for obj_budget in list_ids:
                if obj_budget.date_from == False or obj_budget.date_to == False : 
                    continue
                else:
                    if obj_budget.id != self.id:
                        if ((self.date_from  >= self.date_to ) or \
                            ((self.date_from >= obj_budget.date_from and self.date_from <= obj_budget.date_to ) or \
                            (self.date_to >= obj_budget.date_from and self.date_to <= obj_budget.date_to ) or \
                            (self.date_from < obj_budget.date_from and self.date_to > obj_budget.date_to )) and \
                            ((self.analytic_account_id.id == obj_budget.analytic_account_id.id) and \
                            (self.general_budget_id.id == obj_budget.general_budget_id.id))):
                            raise ValidationError(_("The budget is invalid. The budgets are overlapping .")) 

    @api.multi
    @api.constrains('date_from','date_to')
    def _date_check(self):
        """ 
        Function to check the constrain : period of Budget Lines
        must be within the period of budget.
           
        """
    
        for line in self: 
            budget_from=line.crossovered_budget_id.date_from
            budget_to=line.crossovered_budget_id.date_to
            line_from=line.date_from
            line_to=line.date_to
            if line_from > line_to:
                raise ValidationError(_("Start Date must equal to or less than End date"))
            if line_from < budget_from or line_to > budget_to:
                raise ValidationError(_("The period of lines must be within the period of budget"))

            
    @api.multi
    @api.constrains('general_budget_id','analytic_account_id','date_from','date_to','planned_amount')
    def _check_operation(self):
        """ Raise an exception if Budge Lines to be modified have any transfer/increase operations. """
        if self.ids and not isinstance(self.ids,list): 
            self.ids = [self.ids]
        if self.env['account.budget.operation.history'].search(['|',('budget_line_id_from', 'in', self.ids),
                                                                            ('budget_line_id_to', 'in', self.ids)]):
            raise UserError(_("You cann't modify budget which has transfer or increase operation!"))
        
        for line in self:
            if line.practical_amount != 0:
                raise UserError(_("You cann't modify budgets which already expense from it!"))

    @api.multi
    def transfer(self,vals={}):
        """
        This Method execute any increase or transfer operation.
                                
        @param dictionary vals: all operation values (type, line_ids, to, reference),
        @return: dictionary (budget_line_id, history_ids
        """
        transfer_type = vals.get('type','')
        line_ids = vals.get('line_ids',[])
        to = vals.get('to',{})
        reference = vals.get('reference','')
        budget_line_id= to.get('budget_line')
        transfer_type2 = vals.get('transfer_type','')
        budget_line_id_from = False
        budget_line_id_to = False
        budget_history_pool = self.env['account.budget.operation.history']
        history_ids = []
        if len(line_ids) > 0:
            for line in line_ids:
                #this part requires residual_balance field and it is not migrated yet so I comment this part
                '''if line['line_id'].residual_balance < line['amount']:
                    raise orm.except_orm(_('Error!'), _("The amount you try to transfer (%s) is more than %s residual (%s)!") % (line['amount'], line['line_id'].name, line['line_id'].residual_balance,))'''
                budget_line_id_from =  line['line_id'].id
                budget_line_id_to = budget_line_id
                if transfer_type == 'transfer':
                    if transfer_type2 and transfer_type2 == 'to_multi':
                        budget_line_id_from =  budget_line_id
                        budget_line_id_to = line['line_id'].id

                vals = {
                    'budget_line_id_from':'' if (transfer_type == 'increase') else budget_line_id_from ,
                    'budget_line_id_to':  line['line_id'].id  if (transfer_type == 'increase') else budget_line_id_to,
                    'amount': line['amount'],
                    'name': transfer_type,
                    'reference': reference,
                    }
                history_id = budget_history_pool.create(vals)
                history_ids.append(history_id)

        else:
            vals = {
                    'budget_line_id_from': False,
                    'budget_line_id_to': budget_line_id,
                    'amount': to.get('amount'),
                    'name': transfer_type,
                    'voucher_id': to.get('voucher_id'),
                    'reference': reference,
            }
            history_id = budget_history_pool.create(vals)
            history_ids.append(history_id)
        return budget_line_id ,history_ids

    #v9:
    def fnct_residual_search(self, obj, name, domain=None):
        """
        Method to allow user to advanced search functional residual_balance by recalculate the 
        field amount and search based on entered criteria.
                    
        @param obj: object,
        @param name: char field name,
        @param domain: tuple of the entered search criteria,
        @return: list of tuple of the domain by record IDS
        """
        if context is None:
            context = {}
        if not domain:
            return []
        field, operator, value = domain[0]
        self.env.cr.execute('SELECT id FROM crossovered_budget_lines \
                    WHERE planned_amount+total_operation-balance '+operator+str(value))
        res = self.env.cr.fetchall()
        return [('id', 'in', [r[0] for r in res])]

    @api.multi
    def write(self, vals):
        """
        Before changing general_account_id/analytic_account_id/period_id of budget line,
        must check if it has any operation (transfer, increase,...)
        @return: Update Line values
        """
        """
        if 'general_budget_id' in vals or  'analytic_account_id' in vals \
                    or 'date_from' in vals or 'date_to' in vals:
            self._check_operation()
        """
        return super(AccountBudgetLines, self).write(vals)

    @api.multi
    def _get_move_ids(self):
        """
        get records of budget line to be updated
        @param ids: ids in account asset history
        return dictionary Keys
        """               
        lines = self.env['account.move.line'].search([('move_id','in',self.ids)])
        return self.env['crossovered.budget.lines']._get_ids(lines)

    @api.multi
    @api.depends('operation_id_from','operation_id_to')
    def _operation_amt(self):
        
        """
        This Method use to compute the transfer, increase amount from the operation object.
        @return: dictionary, amount of total operation for each line
        """ 
        for line in self:
            result = 0
            if line.date_from and line.date_to:
                line_ids = self.search([('general_budget_id', '=', line.general_budget_id.id),
                                                  ('analytic_account_id','=',line.analytic_account_id.id), 
                                                  ('date_to', '>=', line.date_to), ('date_from', '<=', line.date_from)
                                                ])
                for l in line_ids: 
                    self.env.cr.execute("SELECT sum(COALESCE(amount,0))  \
                        FROM   (SELECT CASE WHEN  budget_line_id_from = %s \
                                    THEN -amount \
                                    ELSE amount \
                                END AS amount \
                            FROM    account_budget_operation_history h \
                            where budget_line_id_from = %s or budget_line_id_to = %s  ) \
                            as result " , (l.id, l.id , l.id))
                    result += self.env.cr.fetchone()[0] or 0.0
            line.total_operation =result

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
                acc_ids = line.general_budget_id.account_ids.ids
            if not date_from or not date_to:
                continue
            if line.analytic_account_id and acc_ids:
                self.env.cr.execute("SELECT SUM(residual_amount) FROM account_budget_confirmation WHERE analytic_account_id =%s AND (date "
                           "between to_date(%s,'yyyy-mm-dd') AND to_date(%s,'yyyy-mm-dd')) AND "
                           "account_id =ANY(%s) and state='valid'", 
                           (line.analytic_account_id.id, date_from, date_to,acc_ids))
                result = self.env.cr.fetchone()[0] or 0.0
            line.confirm =-result

    @api.multi
    @api.constrains('total_operation','confirm','practical_amount','planned_amount')
    def _check_budget_overdraw(self):
        """
        This Method use to Check Budget overdrow.
        """
        for line in self:
            allow_budget_overdraw = line.crossovered_budget_id.allow_budget_overdraw
            if not allow_budget_overdraw and (line.planned_amount + line.total_operation + line.confirm + line.practical_amount < 0):
                raise ValidationError( _('Budget can\'t go overdrow!'))

    @api.multi
    @api.depends('planned_amount','total_operation')
    def _compute_theoritical_amount(self):
        """
        Inherit to add total_operation in theoritical_amount compute.
        """ 
        theo_amt = 0.00
        today = fields.Datetime.now()
        for line in self:
            # Used for the report
            if self.env.context.get('wizard_date_from') and self.env.context.get('wizard_date_to'):
                date_from = fields.Datetime.from_string(self.env.context.get('wizard_date_from'))
                date_to = fields.Datetime.from_string(self.env.context.get('wizard_date_to'))
                if date_from < fields.Datetime.from_string(line.date_from):
                    date_from = fields.Datetime.from_string(line.date_from)
                elif date_from > fields.Datetime.from_string(line.date_to):
                    date_from = False
                if date_to > fields.Datetime.from_string(line.date_to):
                    date_to = fields.Datetime.from_string(line.date_to)
                elif date_to < fields.Datetime.from_string(line.date_from):
                    date_to = False
                if date_from and date_to:
                    line_timedelta = fields.Datetime.from_string(line.date_to) - fields.Datetime.from_string(line.date_from)
                    elapsed_timedelta = date_to - date_from
                    if elapsed_timedelta.days > 0:
                        theo_amt = (elapsed_timedelta.total_seconds() / line_timedelta.total_seconds()) * (line.planned_amount + line.total_operation)
            else:
                if line.paid_date:
                    if line.date_to and fields.Datetime.from_string(line.date_to) <= fields.Datetime.from_string(line.paid_date):
                        theo_amt = 0.00
                    else:
                        theo_amt = (line.planned_amount + line.total_operation)
                elif line.date_from and line.date_to:
                    line_timedelta = fields.Datetime.from_string(line.date_to) - fields.Datetime.from_string(line.date_from)
                    elapsed_timedelta = fields.Datetime.from_string(today) - (fields.Datetime.from_string(line.date_from))
                    if elapsed_timedelta.days < 0:
                        # If the budget line has not started yet, theoretical amount should be zero
                        theo_amt = 0.00
                    elif line_timedelta.days > 0 and fields.Datetime.from_string(today) < fields.Datetime.from_string(line.date_to):
                        # If today is between the budget line date_from and date_to
                        theo_amt = (elapsed_timedelta.total_seconds() / line_timedelta.total_seconds()) * (line.planned_amount + line.total_operation)
                    else:
                        theo_amt = (line.planned_amount + line.total_operation)
            line.theoritical_amount = theo_amt

# ---------------------------------------------------------
#  Account budget  (Inherit)
# ---------------------------------------------------------   

class CrossoveredBudget(models.Model):
    _inherit = "crossovered.budget"

    allow_budget_overdraw =fields.Boolean(string='Allow Budget Overdraw', default=False)
    date_from= fields.Date('Start Date', states={'done':[('readonly',True)]})
    date_to= fields.Date('End Date', states={'done':[('readonly',True)]})
    analytic_account_id = fields.Many2one('account.analytic.account', 'Analytic Account')
    creating_user_id = fields.Many2one('res.users', 'Responsible',domain=lambda self:[("groups_id", "in", self.env.ref("account_budget_custom.group_budget_user").id)])


    @api.onchange('company_id')
    def onchange_company_id(self):
        for budget in self:
            for line in budget.crossovered_budget_line:
                line.write({'company_id': budget.company_id})

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


    @api.one
    @api.returns('self', lambda value: value.id)
    def copy(self,default=None):
        """
        Inherit copy method to set date_from and date_to To False.
        @return: ID of new record copied
        """
        default = dict(default or {})
        default.setdefault('date_from', False)
        default.setdefault('date_to', False)
        copy_id =super(CrossoveredBudget, self).copy(default)
        for line  in copy_id.crossovered_budget_line:
            line.date_from=False
            line.date_to=False
        return copy_id

    @api.constrains('date_from','date_to')
    def _date_check(self):
        """ 
        Function to check the constrain : date_from of Budget must be 
        eqauls to or less than date_to
        budget lines must be withen budget period
           
        """
        
        for line in self:
            if line.date_from > line.date_to:
                raise ValidationError(_("Start Date must equal to or less than End date"))
            self.crossovered_budget_line._date_check()

    @api.multi
    @api.constrains('date_from','date_to','analytic_account_id')
    def _check_budget_overlap(self):
        list_ids=self.search([])
        #this if to enable copy with date false
        if self.date_from != False and self.date_to != False:
            for obj_budget in list_ids:
                if obj_budget.date_from == False or obj_budget.date_to == False : 
                    continue
                else:
                    if obj_budget.id != self.id:
                        if ((self.date_from  >= self.date_to ) or \
                            ((self.date_from <= obj_budget.date_from and self.date_to >= obj_budget.date_to ) or \
                            (self.date_from > obj_budget.date_from and self.date_from < obj_budget.date_to and self.date_to > obj_budget.date_to ) or \
                            (self.date_from < obj_budget.date_from and self.date_to > obj_budget.date_from and self.date_to < obj_budget.date_to ) or \
                            (self.date_from > obj_budget.date_from and self.date_from < obj_budget.date_to and self.date_to < obj_budget.date_to )) and \
                            ((self.analytic_account_id.id == obj_budget.analytic_account_id.id))):
                                print(self.date_from+"---"+self.date_to+"---"+self.analytic_account_id.name)
                                print(obj_budget.date_from+"---"+obj_budget.date_to+"---"+obj_budget.analytic_account_id.name)
                                raise ValidationError(_(" The budgets are overlapping .")) 



class account_analytic(models.Model):
    """
    Inherit analytic object to add boolean field to allow user to configure
        if it is required to have budget for the corresponding analytic account or not.
        and add many2one field to add responsible user
    """
    _inherit = "account.analytic.account"
    
    _sql_constraints = [('analytic_account_name_uniq', 'unique (name)', _('Analytic Account name must be unique.')),]


    user_id= fields.Many2one('res.users',string='Responsible',required=True , domain=lambda self: [("groups_id", "in", self.env.ref("account_budget_custom.group_budget_user").id)])
    budget = fields.Boolean('Budget Required', default=True)

    

class res_config_settings(models.TransientModel):
    _inherit="res.config.settings"
    group_cash_budget= fields.Boolean("Cash Budget Management",implied_group='account_budget_custom.group_cash_budget',
            help="""This allows to Manage Cash Budgets.""")

# ---------------------------------------------------------
# Account Type (Inherit)
# ---------------------------------------------------------
#TODO: analytic_wk changed to analytic_wk & analytic_requied

class account_account_type(models.Model):
    """
    Inherit account type object to add analytic_wk field to allow user to 
    configure whether to go throw analytic workflow or not in move object
    based on selected account in the move. 
    """
    _inherit =  "account.account.type"

    analytic_wk = fields.Boolean('Budget Check',help="Check if this type of account has to go through budget confirmation check.",default=True)


class account_budget_post(models.Model):
    """
    Budgetary Position
    It add the code to the Budgetary Position,
    """
    _inherit = "account.budget.post"

    code=fields.Char(string='Code')
    name=fields.Char('Name', required=True, translate=True)



    @api.multi
    def _get_budget_position(self,account_id):
        positions_ids = self.search([])
        for post in positions_ids:
            if account_id in post.account_ids.ids:
                return post
        return False

    @api.multi
    @api.constrains('name')
    def _check_name(self):
        name = self.name.strip()
        if not name:
            raise ValidationError(_('Budgetary position name must contains some letters!'))

    _sql_constraints = [
        ('name_Budgetary_uniq', 'unique (name)', _('Budgetary name must be unique.')),
    ]

    '''def copy(self, cr, uid, id, default={}, context=None):
        """
        Inherit copy method to reset state and analytic_account_id to default value.
        
        @return: super copy method
        """
        default.update({'state': 'draft', 'analytic_account_id': False})
        return super(account_budget, self).copy(cr, uid, id, default=default, context=context)'''


class account_move_line(models.Model):
    """ 
    Inherit move line object to  add budget line id to allow calculate the actual balance
    in the budget line object.
    """
    _inherit = 'account.move.line'

    budget_line_id=fields.Many2one('crossovered.budget.lines', 'Budget Line')

    @api.multi
    @api.constrains('analytic_account_id', 'account_id')
    def _check_analytic_required(self):
        for rec in self:
            if rec.account_id.analytic_required and not rec.analytic_account_id:
                raise ValidationError(_('The %s must have  Analytic Account ')%(rec.account_id.name))


class AccountAccount(models.Model):
    _inherit = 'account.account'

    analytic_required = fields.Boolean("Analytic Required")


class AccountInvoiceline(models.Model):
    _inherit = 'account.invoice.line'

    @api.multi
    @api.constrains('account_analytic_id', 'account_id')
    def _check_analytic_required(self):
        for rec in self:
            if rec.account_id.analytic_required and not rec.account_analytic_id:
                raise ValidationError(_('The %s must have  Analytic Account ')%(rec.account_id.name))


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
