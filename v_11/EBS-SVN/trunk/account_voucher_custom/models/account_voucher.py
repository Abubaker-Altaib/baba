# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

from odoo import netsvc
from odoo.exceptions import Warning,UserError, ValidationError
from odoo import api, fields, models, _


class ResCompany(models.Model):
    """ Inherit company model to add field auto_budget to be used in the
	create confirmation  as a condition when it is true to automatically
	check budget.
	"""
    _inherit = "res.company"

    
    auto_budget=fields.Boolean('Automatic Budget Check for vouchers.',default=True)
    


class AccountVoucher(models.Model):

    _inherit = 'account.voucher'

    
    state=fields.Selection(
            [('draft','Draft'),
             ('cancel','Cancelled'),
             ('proforma','Pro-forma'),
             ('no_approve','Waiting For Budget Appove'),
             ('no_approve2','Budget Not Appoved'),
             ('posted','Posted')
            ], 'Status', readonly=True, size=32, track_visibility='onchange',
            help=' * The \'Draft\' status is used when a user is encoding a new and unconfirmed Voucher. \
                        \n* The \'Pro-forma\' when voucher is in Pro-forma status,voucher does not have an voucher number. \
                        \n* The \'Waiting For Budget Appove\' when all budget confirmations related to this voucher didn\'t approve yet. \
                        \n* The \'Budget Not Appoved\' when at least one of budget confirmations related to this voucher didn\'t approve . \
                        \n* The \'Posted\' status is used when user create voucher,a voucher number is generated and voucher entries are created in account \
                        \n* The \'Cancelled\' status is used when user cancel voucher.')
    #v11 to invisible proforma_voucher button
    #check_lines=fields.Boolean(compute='_check_lines',string="Check Lines",store=True)

    '''@api.multi
                @api.depends('line_ids.state')
                def check_lines(self):
                    states=[]
                    for voucher in self:
                        state=self.env['account.voucher.line'].browse(voucher.line_ids.ids).read(['state'])
                        for rec in state:
                            states.append(rec['state'])
                        if states.count('approve') == len(states):
                            voucher.write({'state':'draft'})
                        elif 'no_approve' in states or 'cancel' in states:
                            voucher.write({'state':'no_approve2'})
                        elif 'complete' in states:
                            voucher.write({'state':'no_approve'})'''

    """@api.multi
    @api.depends('line_ids','line_ids.state')
    def _check_lines(self):
        states=[]
        for voucher in self:
            if voucher.voucher_type == 'purchase':
                state=self.env['account.voucher.line'].browse(voucher.line_ids.ids).read(['state'])
                for rec in state:
                    states.append(rec['state'])
                if states.count('approve') == len(states):
                    voucher.check_lines=True
                elif 'no_approve' in states or 'cancel' in states:
                    voucher.write({'state':'no_approve2'})
                    voucher.check_lines=False
                else:
                    voucher.write({'state':'no_approve'})
                    voucher.check_lines=False"""

        

    #v11 open if need to add check in analytic aacount
    '''def _check_analytic_account(self, cr, uid, ids, context=None):
        """
         Check state of voucher and user_type of account_id
         
         @return: boolean
        """
        for voucher in self.browse(cr, uid, ids, context=context):
            if voucher.state != "draft":
                for voucher_line in voucher.line_ids:
                    if voucher.state != "draft" and voucher_line.account_id.user_type_id.analytic_required \
                        and not voucher_line.account_analytic_id and voucher_line.amount > 0.0:
                        return False
        return True
    _constraints = [
        (_check_analytic_account, _('Some accounts required to add analytic account for it!'), ['account_id','account_analytic_id','amount']),
    ]'''

    @api.multi
    @api.constrains('amount')
    def _total_amount_check(self):
        """
        Constraint method that doesn't allow voucher's amount being Zero when state is not draft, cancel or no_approve
        
        @return: boolean
        """
        for voucher in self:
            if voucher.state not in ['draft','cancel','no_approve' ] and voucher.amount==0.0:
                raise ValidationError(_("Operation is not completed, Total amount shouldn't be zero!"))

    
    @api.multi
    def unlink(self):
        """
        Inherit unlink method to delete all confirmations that belong to the deleted voucher lines
        
        @return: super unlink
        """
        for record in self:
            if record.state not in ('draft', 'cancel'):
                raise Warning(_('Cannot delete voucher(s) which are already opened.'))
            if record.line_ids:
                #raise Warning(_('Ivalid Action:\nYou cannot delete this voucher until remove the related voucher lines!'))
                record.line_ids.unlink()
            confirmation_ids = self.approved_line()
            print("----------------------------confirmation_ids",confirmation_ids)
            if confirmation_ids:
                self.env['account.budget.confirmation'].unlink(confirmation_ids)
        return super(AccountVoucher, self).unlink()

    #v11 TOCHECK 
    def onchange_price(self, cr, uid, ids, line_ids, tax_id, partner_id=False, context=None):
        """
        Compute the amount from all voucher lines and return it in voucher amount.

        @param line_ids: list of voucher line ids
        @param tax_id: list of tax_ids for voucher
        @param partner_id: set partner_id =False as default
        @return: super of onchange_amount and it return total price of voucher line
        with tax_ids amount
        """
        line_pool = self.pool.get('account.voucher.line')
        line_ids = resolve_o2m_operations(cr, uid, line_pool, line_ids, ["amount","state"], context)
        approve_line_ids = [(0,0,l) for l in line_ids if l.get("state","complete") != "cancel"]
        return super(AccountVoucher,self).onchange_price(cr, uid, ids, approve_line_ids, tax_id, partner_id, context=context)



    @api.multi
    def voucher_move_line_create(self, line_total, move_id, company_currency, current_currency):
        '''
        Create one account move line, on the given account move, per voucher line where amount is not 0.0.
        It returns Tuple with tot_line what is total of difference between debit and credit and
        a list of lists with ids to be reconciled with this format (total_deb_cred,list_of_lists).

        :param voucher_id: Voucher id what we are working with
        :param line_total: Amount of the first line, which correspond to the amount we should totally split among all voucher lines.
        :param move_id: Account move wher those lines will be joined.
        :param company_currency: id of currency of the company to which the voucher belong
        :param current_currency: id of currency of the voucher
        :return: Tuple build as (remaining amount not allocated on voucher lines, list of account_move_line created in this method)
        :rtype: tuple(float, list of int)
        '''
        voucher_line_pool = self.env['account.voucher.line']
        for line in self.line_ids:
            #create one move line per voucher line where amount is not 0.0
            if not line.price_subtotal:
                continue
            # convert the amount set on the voucher line into the currency of the voucher's company
            # this calls res_curreny.compute() with the right context,
            # so that it will take either the rate on the voucher if it is relevant or will use the default behaviour
            amount = self._convert_amount(line.price_unit*line.quantity)
            move_line = {
                'journal_id': self.journal_id.id,
                'name': line.name or '/',
                'account_id': line.account_id.id,
                'move_id': move_id,
                'partner_id': self.partner_id.id,
                'analytic_account_id': line.account_analytic_id and line.account_analytic_id.id or False,
                'quantity': 1,
                'credit': abs(amount) if self.voucher_type == 'sale' else 0.0,
                'debit': abs(amount) if self.voucher_type == 'purchase' else 0.0,
                'date': self.account_date,
                'tax_ids': [(4,t.id) for t in line.tax_ids],
                'amount_currency': line.price_subtotal if current_currency != company_currency else 0.0,
                'currency_id': company_currency != current_currency and current_currency or False,
                'budget_confirm_id': hasattr(voucher_line_pool, "budget_confirm_id") and line.budget_confirm_id and line.budget_confirm_id.id,
                'budget_line_id': hasattr(voucher_line_pool, "budget_confirm_id") and line.budget_confirm_id.budget_line_id and line.budget_confirm_id.budget_line_id.id
            }

            self.env['account.move.line'].with_context(apply_taxes=True).create(move_line)
            #v11 this feature depends on module account_voucher_custom if need it migrate the dependency 
            '''if self.pay_now == 'pay_now':
                rec = self.get_voucher_payment_values(line_total)
                payment = self.env['account.payment'].create(rec)
                payment.post1()
                self.write({'payment_id': payment.id})'''
        return line_total

    @api.model
    def create(self, vals):
        """
        #v11
        Inherit create method to call create_budget_confirmation
        """
        voucher=super(AccountVoucher,self).create(vals)
        ######### to check ########
        #if voucher.voucher_type == 'purchase':
        #voucher.create_budget_confirmation()
        return voucher

    @api.multi
    def create_budget_confirmation(self):

        """ 
        This Method for creating Budget Confirmation for each Voucher Line with analytic account

        @return: boolean True it any confirmation created, or return False
        """
        
        confirmation_pool = self.env['account.budget.confirmation']
        currency_pool = self.env['res.currency']
        new_confirm_id = False
        flag = False
        for voucher in self:
            #v9: if voucher.voucher_type  in ('purchase','sale'):  super(account_voucher,self).compute_tax(cr, uid, [voucher.id], context=context)
            if voucher.journal_id.type == 'purchase':
                for voucher_line in voucher.line_ids:
                    #v9: TEST ME if voucher_line.account_id and voucher_line.account_id.user_type_id.analytic_wk:
                    if voucher_line.account_id:
                        total_amount=voucher.company_id.currency_id.with_context(date=voucher.date).compute(voucher_line.total_amount, voucher.currency_id)
                        amount=voucher.company_id.currency_id.with_context(date=voucher.date).compute(voucher_line.price_unit, voucher.currency_id)
                        val = {
                             'reference': voucher.number,
                             'partner_id': voucher.partner_id.id,
                             'account_id': voucher_line.account_id.id,
                             'date': voucher.date,
                             'analytic_account_id': voucher_line.account_analytic_id and voucher_line.account_analytic_id.id,
                             'amount': total_amount or amount,
                             'residual_amount': total_amount or amount,
                             'type':self._context.get('type','other'),
                             'note':voucher_line.name or '/',
                        }
                       
                        if voucher_line.tax_ids:
                            val_amount = val.get('amount',0)
                            net_amount = 0
                            total = 0
                            tax_amount = 0
                            tax_info = voucher_line.tax_ids.compute_all(voucher_line.price_unit, voucher.currency_id, voucher_line.quantity, voucher_line.product_id, voucher.partner_id)
                            total += tax_info.get('total_included', 0.0)
                            tax_amount += sum([t.get('amount',0.0) for t in tax_info.get('taxes', False)]) 
                            net_amount = tax_amount+val_amount
                            val.update({'amount':net_amount or amount,})
                        new_confirm_id = False

                        if voucher_line.budget_confirm_id:
                            flag = True
                            #confirmation_pool.write([voucher_line.budget_confirm_id.id], val)
                            #new_confirm_id = voucher_line.budget_confirm_id.id
                        elif not voucher_line.budget_confirm_id:
                            flag = True
                            confirm = confirmation_pool.create(val)
                            new_confirm_id = int(confirm)
                            voucher_line.write({'budget_confirm_id':new_confirm_id})
                        #v11 condition is worng ???
                        #if new_confirm_id and not voucher.company_id.auto_budget:#v9: test me
                        if new_confirm_id and voucher.company_id.auto_budget:
                            confirmation_pool.browse(new_confirm_id).action_cancel_draft()
                            confirmation_pool.browse(new_confirm_id).budget_complete()
                            confirmation_pool.browse(new_confirm_id).check_budget()
                            
        return flag

    @api.multi
    def approved_line(self):
        """
        This method return all voucher lines that have a budget confirmation.
        
        @return: list of all budget_confirm_ids for voucher lines 
        """
        return [voucher_line.budget_confirm_id.id for voucher in self for voucher_line in voucher.line_ids if voucher_line.budget_confirm_id]

    def cancel_voucher(self):
        """
        Object button method which canceling all  budget confirmation
        and change voucher state to "cancel"
        
        @return: super cancel_voucher
        """
        for confirmation_id in self.approved_line():
            self.env['account.budget.confirmation'].browse(confirmation_id).budget_cancel()
        return super(AccountVoucher, self).cancel_voucher()

    #v11 un needed funtions
    """def confirmation_get(self, cr, uid, ids, context=None):
                    '''
                    This method gets all budget confirmation ids of voucher.
            
                    @return: list of budget confirmation id
                    '''
                    res = []
                    for voucher in self.browse(cr, uid, ids, context=context):
                        for line in voucher.line_ids:
                            if line.budget_confirm_id:
                                res.append(line.budget_confirm_id.id)
                    return res
            
                def test_state(self, cr, uid, ids, mode, context=None):
                    '''
                    Check voucher line and budget_confirmation state 
                    and write state in voucher line (approved,not approved,cancelled)
                    depend on budget confirmation for this line
            
                    @param mode :tuple of flags
                    @return: Boolean True or False
                    '''
                    assert mode in ('finished', 'canceled' ,'no_approve'), _("invalid mode for test_state")
                    finished = True
                    canceled = False
                    notcanceled = False
                    no_approve=True
                    write_approve_ids = []
                    write_cancel_ids = []
                    write_no_approve_ids = []
                    no_approve_ids = []
                    ids = isinstance(ids, list) and ids[0] or ids
                    voucher = self.browse(cr, uid, ids, context=context)
                    #if voucher.type =='receipt': return True
                    for line in voucher.line_ids:
                        if (not line.budget_confirm_id) or (line.budget_confirm_id.state in ['valid','cancel']):
                            if (not line.budget_confirm_id) or (line.budget_confirm_id.state == 'valid' and line.state != 'approve'):
                                write_approve_ids.append(line.id)
                            elif line.budget_confirm_id.state == 'cancel' and line.state != 'cancel':
                                write_cancel_ids.append(line.id)
                        else:
                            finished = False
                        if line.budget_confirm_id:
                            if (line.budget_confirm_id.state == 'unvalid'):
                                if line.state != 'no_approve':
                                    write_no_approve_ids.append(line.id)
                                if line.state == 'no_approve':
                                    no_approve_ids.append(line.id)
                            else:
                                notcanceled = True
                        '''else:
                            write_approve_ids.append(line.id)'''
                    if write_approve_ids:
                        self.pool.get('account.voucher.line').write(cr, uid, write_approve_ids, {'state': 'approve'}, context=context)
                    if write_cancel_ids:
                        self.pool.get('account.voucher.line').write(cr, uid, write_cancel_ids, {'state': 'cancel'},context=context)
                    if write_no_approve_ids:
                        self.pool.get('account.voucher.line').write(cr, uid, write_no_approve_ids, {'state': 'no_approve'}, context=context)
                    if no_approve_ids == voucher.line_ids.ids:
                        if mode == 'no_approve':
                            return no_approve
                    '''v9: testme if not voucher.operation_type and voucher.type not in ('payment', 'receipt'):
                        res = self.onchange_price(cr, uid, [voucher.id], [(4,l.id) for l in voucher.line_ids], voucher.tax_id and [t.id for t in voucher.tax_id] or [], voucher.partner_id, context).get("value",{})
                        #Can't call orm write because of the recursion
                        # cr.execute("UPDATE account_voucher  \
                                    SET amount=%s, tax_amount=%s  WHERE id=%s ",
                                    (res.get("amount"),res.get("tax_amount"), voucher.id))'''
                    
                    canceled=self.test_cancel(cr, uid, [voucher.id],write_cancel_ids, context=context)
                    if mode == 'finished':
                        return finished
                    elif mode == 'canceled':
                        return canceled
                        if notcanceled:
                            return False
                        return canceled
            
                def test_cancel(self, cr, uid, ids,cancel_ids, context=None):
                    for voucher in self.browse(cr, uid, ids, context=context):
                        for line in voucher.line_ids:
                            if line.state != 'cancel' and line.id not in cancel_ids:
                                return False
                    return True"""

class AccountVoucherLine(models.Model):

    _inherit = 'account.voucher.line'

    @api.multi
    def unlink(self):
        """
        Inherit unlink method to delete budget confirmation that belong to the deleted voucher line.
        
        @return: Deleting selected records
        """
        confirmation_ids = [voucher_line.budget_confirm_id.id for voucher_line in self if voucher_line.budget_confirm_id]
        line = super(AccountVoucherLine, self).unlink()
        if confirmation_ids:
            self.env['account.budget.confirmation'].browse(confirmation_ids).unlink()
        return line

    
    name=fields.Char('Description', size=256, required=True,default='/')
    budget_confirm_id= fields.Many2one('account.budget.confirmation', 'Confirmation', select=2, ondelete="restrict")
    state=fields.Selection([('complete','Waiting for Approve'),('approve','Approved'),('no_approve','Budget Not Approved'),
                                  ('cancel','Canceled')], 'State', required=True, readonly=True,default='complete')
    total_amount= fields.Float('Total Amount')
    

    @api.model
    def create(self,vals):
        """
        Inherited - create method to be sure that account and voucher company
        are the same.

        @return: list creating voucher lines
        """
        vals.update({'budget_confirm_id':False})
        if vals.get('account_id',False) and vals.get('voucher_id',False):
            account_company = self.env['account.account'].browse(vals['account_id']).company_id.id
            voucher_company = self.env['account.voucher'].browse(vals['voucher_id']).company_id.id
            if account_company != voucher_company:
                raise orm.except_orm(_('Entry Error!'), _('The account company is not like the voucher company!'))
        return super(AccountVoucherLine, self).create(vals)


# ---------------------------------------------------------
# Budget Confirmation Inherit
# ---------------------------------------------------------
class AccountBudgetConfirmation(models.Model):
    """ Inherit to overwrite workflow mothods to reflect confirmation state in voucher line  """

    _inherit = "account.budget.confirmation" 

    #v11 link budget confirmation with voucher line to reflect workflow in voucher line
    voucher_line_ids=fields.One2many('account.voucher.line', 'budget_confirm_id', 'Voucher Lines')

    @api.multi
    def budget_valid(self):
        """
        overwrite to change vocher line state to approve
        """
        for conf in self:
            for line in conf.voucher_line_ids:
                line.write({'state': 'approve'})
        return super(AccountBudgetConfirmation, self).budget_valid()

    @api.multi
    def budget_unvalid(self):
        """
        overwrite to change vocher line state to no_approve
        """
        for conf in self:
            for line in conf.voucher_line_ids:
                line.write({'state': 'no_approve'})
        return super(AccountBudgetConfirmation, self).budget_unvalid()

    @api.multi
    def budget_cancel(self):
        """
        overwrite to change vocher line state to cancel
        """
        super(AccountBudgetConfirmation, self).budget_cancel()
        for conf in self:
            for line in conf.voucher_line_ids:
                line.write({'state': 'cancel'})
         


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
