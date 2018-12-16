# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2016-2017 NCTR (<http://www.nctr.sd>).
#
##############################################################################
import time
from openerp.osv import fields, osv, orm
from tools.translate import _
from base_custom.amount_to_text_ar import amount_to_text as amount_to_text_ar
import re

class account_period(osv.osv):

    _inherit = "account.period"

    _columns = {
        'sequence_id': fields.many2one('ir.sequence', string='Entry Sequence', ondelete='cascade'),
    }

    def create(self,cr,uid,vals,context=None):
        sequence_id = {'name':vals['name'],'prefix':vals['name']+"/",
                       'padding':3,'implementation':'no_gap'}
        vals['sequence_id'] = self.pool.get('ir.sequence').create(cr,uid,sequence_id,context=context)
        return super(account_period,self,).create(cr,uid,vals,context=context)
        

class account_move(osv.osv):

    _inherit = "account.move"

    _columns = {
        'ref': fields.char('Reference', size=64, required=True),
        'internal_sequence_number': fields.char(string='Internal Number', size=64, readonly=True),
        'active':fields.boolean('Active'),
    }

    _defaults = {
        'active':True,
    }

    def draft(self, cr, uid, ids, context=None):
        for move in self.browse(cr, uid, ids,context):
            #Used this condition if the state change and user not refresh the page
            if move.state not in ['completed','analytic','to_rev_manager','to_review_closer','review_analytic']:
                raise orm.except_orm(_('UserError'), _('You cann\'t edit this jouranl, it\'s in "%s" state, Please refresh your page') % move.state)	  
        return super(account_move, self).draft(cr, uid, ids, context=context)

    def check_completed(self, cr, uid, ids, context=None):
        for move in self.browse(cr, uid, ids,context):
            #Used this condition if the state change and user not refresh the page
            if move.state not in ['completed']:
                raise orm.except_orm(_('UserError'), _('You cann\'t edit this jouranl, it\'s in "%s" state, Please refresh your page') % move.state)	  
        return super(account_move, self).check_completed(cr, uid, ids, context=context)


    def copy(self, cr, uid, ids, default={}, context={}):
        """
        Inherit copy method resetinternal_sequence_number
        
        @param default: dictionary of the values of record to be created,
        @return: super method of copy
        """
        default.update({'internal_sequence_number': False })
        return super(account_move, self).copy(cr, uid, ids, default=default, context=context)

    def test_analytic(self, cr, uid, ids, context=None):
        """
        Workflow condition method to determine whether to go throw analytic workflow
        or not in move object. 
        It return True if user set analytic_wk field  in account type to False.
        and it return False if the user set analytic_wk field in account type to False.
                    
        @return: Boolean True or False
        """
        """if not(self.validate(cr, uid, ids, context) and len(ids)):
            raise orm.except_orm(_('Integrity Error !'), _('You can not Complete a non-balanced entry !\nMake sure you have configured Payment Term properly !\nIt should contain atleast one Payment Term Line with type "Balance" !'))"""
        for mv in self.browse(cr, uid, ids):
            for line in mv.line_id:
                if line.account_id.user_type.analytic_wk and not line.analytic_account_id and line.debit:
                    raise orm.except_orm(_('Error!'), _('You must add analytic account for %s accounts!' % (line.account_id.user_type.name,)))
                if line.account_id.user_type.analytic_wk:
                    return True
        return False

    def completed(self, cr, uid, ids, context=None):
        """
        Inherit from completed function 
        
        @return: write method of object
        """
        voucher_obj = self.pool.get('account.voucher')
        check_obj = self.pool.get('check.log')
        self.test_analytic(cr, uid, ids, context=context)
        super(account_move, self).completed(cr, uid, ids, context=context)
        move_line_obj = self.pool.get('account.move.line')
        move_obj =self.browse(cr, uid, ids)[0]

        sequence = move_obj.period_id.sequence_id.id
        if not move_obj.internal_sequence_number:
            seq_no = self.pool.get('ir.sequence').get(cr, uid, 'internal.sequance', context=context)
            self.write(cr, uid, ids,{'internal_sequence_number': seq_no, }, context=context)

        if move_obj.line_id:
            for line in move_obj.line_id:
                if line.ref == False :
                    move_line_obj.write(cr, uid, [line.id], {'ref':move_obj.ref })
        #This code used to Unlink account voucher if already there
        voucher_ids = voucher_obj.search(cr, uid, [('move_id', '=' , ids[0])] , context=context)
        for voucher_id in voucher_ids:
            voucher = voucher_obj.browse(cr, uid, voucher_id, context)
            if voucher.journal_id.type == 'bank'and voucher.chk_status == True:
                cr.execute("SELECT COALESCE(sum(credit),0) amount,ml.partner_id,ml.id id " \
                   "FROM account_move_line ml INNER JOIN account_move m ON m.id = ml.move_id " \
                   "INNER JOIN account_account acc ON acc.id = ml.account_id INNER JOIN account_account_type acc_type ON acc_type.id = user_type " \
                   "WHERE m.id = %s AND ml.credit > 0 AND type = 'liquidity' GROUP BY ml.partner_id,date_maturity,ml.id",(str(ids[0]),))
                suppliers = cr.dictfetchall()
                #First supplier
                supplier = suppliers[0]
                voucher_obj.write(cr, uid, [voucher_id],{'amount':supplier['amount'],
                                                        'amount_in_word':amount_to_text_ar(supplier['amount'], 'ar'),
                                                        'partner_id':supplier['partner_id'],
                                                          }, context)
                check_ids = check_obj.search(cr, uid, [('name', '=' , voucher_id),('status','=','active')] , context=context)
                check_obj.write(cr, uid, check_ids, {'partner_id':supplier['partner_id'],'amount': supplier['amount'] } ,context=context)
                #voucher_obj.unlink(cr, uid, voucher_ids, context)
        return True

    def reverse(self, cr, uid, ids, context=None):
        """ 
        inherit method to add some constrains to make reverse in close and posted state
        @return: dictionary of values
        """
        if context is None:
            context = {}
        for move in self.browse(cr, uid, ids, context=context):
            if move.state not in ['posted', 'closed'] :
                raise orm.except_orm(_('Error !'), _('You can\'t reverse unposted or unclosed move! '))
            context.update({'company_id':move.company_id.id})
            if self.pool.get('account.move.line').search(cr, uid, [('move_id', '=', move.id), ('statement_id', '!=', False)], context=context):
                raise orm.except_orm(_('Warning !'), _("This move has bank reconcilation")) 
        return {
            'name':_("Move Reverse"), 
            'view_mode': 'form', 
            'view_id': False, 
            'view_type': 'form', 
            'res_model': 'account.move.reverse', 
            'type': 'ir.actions.act_window', 
            'nodestroy': True, 
            'target': 'new', 
            'domain': '[]', 
            'context': dict(context, active_ids=ids, active_model=self._name),
        }

    def create_log(self, cr, uid, ids, previous_state, new_state, transaction_type ,context):
        """This method create new record in audittrial.log file, 
           use it if you call workflow from function """
        obj_audittrial = self.pool.get('audittrail.log')
        obj_audittrial_line = self.pool.get('audittrail.log.line')
        obj_model = self.pool.get('ir.model')
        obj_model_fields = self.pool.get('ir.model.fields')
        obj_ids = obj_model.search(cr, uid, [('model','=','account.move')],context=context)
        field_ids = obj_model_fields.search(cr, uid, [('model_id','=',obj_ids[0]),('name','=','state')],context=context)
        for move in self.browse(cr, uid, ids , context=context):
            log_dict = { 'timestamp': time.strftime("%Y-%m-%d %H:%M:%S"),
                         'name': move.name,
                         'object_id': obj_ids[0],
                         'user_id': uid,
                         'method': new_state,
                         'res_id': move.id,
                       }
            log_id = obj_audittrial.create(cr, uid, log_dict, context=context)

            log_line_dict_list =[{ 'old_value':previous_state,
                             'old_value_text':previous_state,
                             'new_value':new_state,
                             'new_value_text':new_state,
                             'field_description':'state',
                             'field_id':field_ids[0],
                             'log_id': log_id,
                           } ,
                           {'old_value':'transaction_type',
                             'old_value_text':'transaction_type',
                             'new_value':transaction_type,
                             'new_value_text':transaction_type,
                             'field_description':'state',
                             'field_id':field_ids[0],
                             'log_id': log_id,
                           }]
            for log_line_dict in log_line_dict_list:
                obj_audittrial_line.create(cr, uid, log_line_dict, context=context)

        return True
       
class check_log(osv.Model):
    """
    This class for storing some data for each printed check as a 
    summary log display check info and it's state.
    """
    _inherit = 'check.log'
    _order = 'id desc'

    _columns = {
        'check_delivered':fields.boolean('Delivered'),
        'amount':fields.float('Payment Amount'),        
    }

    def create(self, cr, uid, vals, context=None):
        """
        create operation
        @return: super create() method
        """
        voucher_id = vals.get('name',False)
        voucher_amount = self.pool.get('account.voucher').browse(cr, uid, voucher_id, context).amount
        vals.update({'amount': voucher_amount})
        return super(check_log, self).create(cr, uid, vals, context)

class account_check_print_wizard(osv.osv_memory):

    _inherit = "account.check.print.wizard"

    def check_payment(self, cr, uid, ids, context=None):
        #Change due date of voucher by current date
        data = self.browse(cr, uid, ids, context=context)[0]
        voucher_pool = self.pool.get('account.voucher')
        voucher_id = (data.payment_id and data.payment_id.id) or (context['active_model'] == 'account.move' and self.check_move_data(cr, uid, ids, context=context))
        if voucher_id :
            voucher_pool.write(cr, uid,[voucher_id],{'date_due': time.strftime('%Y-%m-%d')},  context=context)
        return super(account_check_print_wizard, self).check_payment(cr, uid, ids, context)

    def _get_state(self, cr, uid, context=None):
        """ 
        @return: char default value of wizard state.
        """
        ids = self._get_voucher_ids(cr, uid, context=context)
        voucher = self.pool.get('account.voucher').browse(cr, uid, ids, context=context)
        move = self.pool.get('account.move').browse(cr, uid, context.get('active_id',False) , context=context)
        return voucher and ((context['active_model'] == 'account.move' and voucher.move_id.state != 'closed' and not voucher.chk_seq and 'nothing') or 
                            (context['active_model'] == 'account.voucher' and voucher.state != 'receive' and 'unpost') or (voucher.chk_seq and 'printed' or 'draft')) or \
                (context['active_model'] == 'account.move' and move.state != 'closed' and 'unpost' or 'draft')


    def _get_msg(self, cr, uid, context=None): 
        """
        @return: char default value of wizard displaying message.
        """
        voucher_pool = self.pool.get('account.voucher')
        ids = self._get_voucher_ids(cr, uid, context=context)
        chk_no = ids and voucher_pool.browse(cr, uid, ids, context=context).chk_seq or False
        if context['active_model'] == 'account.move' and self.pool.get('account.move').browse(cr, uid, context.get('active_id',False) , context=context).state != 'closed':
            return _("Your payment's move is not Closed!")
        elif context['active_model'] == 'account.voucher' and voucher_pool.browse(cr, uid, ids, context=context).state != 'receive':
            return _("Your payment's is not paid!")
        elif chk_no:
            return _("This Payment has already been paid with check:%s")%(chk_no)
        else:
            return _("Please verify this check number matches the starting preprinted number of the check in the printer! If not, enter new check number below.")

    def cancel_check(self,  cr, uid, ids, context=None):
        """
        Cancel Check and change wizard state to "update".
        @return: boolean True
        """
        data = self.browse(cr, uid, ids, context=context)[0]
        voucher_pool = self.pool.get('account.voucher')
        check_log_pool = self.pool.get('check.log')
        voucher = voucher_pool.browse(cr, uid, data.payment_id.id, context=context)
        chk_log_ids = check_log_pool.search(cr,uid,[('name','=',voucher.id),('status','=','active')], context=context)
        voucher_pool.write(cr, uid,[voucher.id],{'chk_seq':'','chk_status':True}, context=context)
        if chk_log_ids:
            check_log_pool.write(cr, uid, chk_log_ids, {'status':'voided'},context=context)
        return {'type':'ir.actions.act_window_close'}


    _defaults = {
           'state': _get_state,
           'msg': _get_msg,
    }


#----------------------------------------------------------
# Account Move Line(Inherit)
#----------------------------------------------------------
class account_move_line(osv.Model):

    _inherit = 'account.move.line'
    def _partner_balnce_fun(self, cr, uid, ids, field_name, arg, context=None):
        """
        Compute the partner balance amount.

        @param field_name: list contains name of fields that call this method
        @param arg: extra arguments
        @return: Dictionary of the partner balance amount
        """
        res = {}
        for record in self.browse(cr,uid,ids,context=context):
            res[record.id] = 0
            if record.partner_id:
                res[record.id] = record.partner_id.debit- record.partner_id.credit
        return res

    _columns = {
    'partner_balance': fields.function(_partner_balnce_fun,string="Partner Balance"),
    'active':fields.boolean('Active'),
    }

    _defaults={
        'active':True,
    }

    def change_account(self, cr, uid, ids, account_id, period_id, context=None):
        budget_line_obj = self.pool.get('account.budget.lines')

        budget_line_id = budget_line_obj.search(cr, uid, [('period_id', '=', period_id),('general_account_id','=',account_id)],
                                                                   context=context)

        if budget_line_id:
            budget = budget_line_obj.browse(cr, uid, budget_line_id[0],context=context)
                        
            analytic_account_id = budget.account_budget_id.analytic_account_id.id

            return {
                'value': {
                    'analytic_account_id':analytic_account_id,
                    }
            }
        
        return {}

#----------------------------------------------------------
# Change the filter default to Date in Accounting reports
#----------------------------------------------------------
class account_report_general_ledger(osv.Model):
    _inherit = "account.report.general.ledger"

    _columns = {
    'filter': fields.selection([('filter_no', 'No Filters'), ('filter_date', 'Date'), ('filter_period', 'Periods')], "Filter by", required=True),
        }
    _defaults = {
            'filter': 'filter_date',
    }

class account_balance_report(osv.Model):
    _inherit = "account.balance.report"

    _columns = {
    'filter': fields.selection([('filter_no', 'No Filters'), ('filter_date', 'Date'), ('filter_period', 'Periods')], "Filter by", required=True),
        }
    _defaults = {
            'filter': 'filter_date',
    }

class accounting_report(osv.Model):
    _inherit = "accounting.report"

    _columns = {
    'filter': fields.selection([('filter_no', 'No Filters'), ('filter_date', 'Date'), ('filter_period', 'Periods')], "Filter by", required=True),
        }
    _defaults = {
            'filter': 'filter_date',
    }

class account_account_statement_arabic(osv.Model):
    _inherit = "account.account.statement.arabic"

    _columns = {
    'filter': fields.selection([('filter_no', 'No Filters'), ('filter_date', 'Date'), ('filter_period', 'Periods')], "Filter by", required=True),
        }
    _defaults = {
            'filter': 'filter_date',
    }

class account_partner_balance(osv.Model):
    _inherit = "account.partner.balance"

    _columns = {
    'filter': fields.selection([('filter_no', 'No Filters'), ('filter_date', 'Date'), ('filter_period', 'Periods')], "Filter by", required=True),
        }
    _defaults = {
            'filter': 'filter_date',
    }

    def onchange_chart_id(self, cr, uid, ids, chart_account_id= -1, context=None):
        res = super(account_partner_balance, self).onchange_chart_id(cr, uid, ids, chart_account_id, context)
        res['value']['acc_ids'] =False
        return res 

class account_partner_ledger(osv.Model):
    _inherit = "account.partner.ledger"

    _columns = {
    'filter': fields.selection([('filter_no', 'No Filters'), ('filter_date', 'Date'), ('filter_period', 'Periods')], "Filter by", required=True),
        }
    _defaults = {
            'filter': 'filter_date',
    }

class account_report_compare_budget_custom(osv.Model):
    _inherit = "account.report.compare.budget.custom"

    _columns = {
    'filter': fields.selection([('filter_no', 'No Filters'), ('filter_date', 'Date'), ('filter_period', 'Periods')], "Filter by", required=True),
        }
    _defaults = {
            'filter': 'filter_date',
    }


class account_voucher(osv.Model):
    _inherit = 'account.voucher'

    _columns = {
	 'state':fields.selection([('draft', 'Draft'), ('close', 'Waiting for Payment Pay'),
                                  ('confirm', 'Waiting for Payment Confirm'), ('review', 'Waiting for Internal Auditor Review'),
                                  ('pay', 'Waiting for Payment Pay'),
                                  ('receive', 'Waiting for Payment Deliver'), ('posted', 'Posted'),
                                  ('done', 'Done'), ('cancel', 'Cancel'), ('reversed', 'Reversed')]),

         }

    def onchange_journal_id(self, cr, uid, ids, journal, pay_journal, line_ids, tax_id, partner_id, date, amount, ttype, company_id, pay_now, context={}):
        """
        Inherited to delete value of voucher lines
        @return: dictionary of values of fields to be updated"""
        res = super(account_voucher, self).onchange_journal_id(cr, uid, ids, journal, pay_journal, line_ids, tax_id, partner_id, date, amount, ttype, company_id, pay_now, context)
        if res and res['value'] and res['value'].get('line_cr_ids',False):
            del res['value']['line_cr_ids'] 
        if res and res['value'] and res['value'].get('line_ids',False):
            del res['value']['line_ids'] 
        return res

    def action_move_line_create(self, cr, uid, ids, vals={}, context=None):
        print "MOve Create>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>"
        """
        Method creating Journal Entry for account voucher.
        
        @param vals: dict of values (period, journal and date)
        @return: boolean True
        """
        if context is None:
            context = {}
        move_id = True
        move_pool = self.pool.get('account.move')
        move_line_pool = self.pool.get('account.move.line')
        voucher_line_pool = self.pool.get('account.voucher.line')
        currency_pool = self.pool.get('res.currency')
        tax_pool = self.pool.get('account.tax')
        sequence_pool = self.pool.get('ir.sequence')
        period_pool = self.pool.get('account.period')
        ml_id=[]
        self.compute_tax(cr, uid, ids, context=context)
        self.write(cr, uid, ids, {'state': 'posted'}, context=context)

        for voucher in self.browse(cr, uid, ids, context=context):
            if voucher.move_id:
                continue
            period_id = vals.get('period') or voucher.period_id
            date = vals.get('date') or voucher.date
            journal_id = vals.get('journal') or voucher.pay_journal_id or voucher.journal_id
            #account_id = vals.get('account') or (voucher.account_id and voucher.account_id.id) or \
            #                   (voucher.type in ('purchase', 'payment') and journal_id.default_credit_account_id.id) or \
            #                    (voucher.type in ('sale', 'receipt') and journal_id.default_debit_account_id.id)
            account_id = voucher.pay_journal_id.default_credit_account_id.id
            context_multi_currency = context.copy()
            context_multi_currency.update({'date': date})
            ctx = context.copy()
            ctx['fiscalyear_id'] = period_pool.browse(cr, uid, period_id.id).fiscalyear_id.id
            if journal_id.sequence_id:
                name = sequence_pool.get_id(cr, uid, journal_id.sequence_id.id)
            else:
                raise orm.except_orm(_('Error !'), _('Please define a sequence on the journal %s!')%(journal_id.name,))

            move_id = move_pool.create(cr, uid, {
                            'name': name,
                            'journal_id': journal_id.id,
                            'narration': voucher.narration,
                            'date': date,
                            'ref': voucher.number,
                            'period_id': period_id.id,
                        }, context=context)

            #create the first line manually
            company_currency = voucher.journal_id.company_id.currency_id.id
            current_currency = voucher.currency_id.id
            debit = 0.0
            credit = 0.0
            if voucher.type in ('purchase', 'payment'):
                credit = currency_pool.compute(cr, uid, current_currency, company_currency, voucher.amount, context=context_multi_currency)
            elif voucher.type in ('sale', 'receipt'):
                debit = currency_pool.compute(cr, uid, current_currency, company_currency, voucher.amount, context=context_multi_currency)
            if debit < 0:
                credit = -debit
                debit = 0.0
            if credit < 0:
                debit = -credit
                credit = 0.0
            sign = debit - credit < 0 and -1 or 1
            company_currency = voucher.company_id.currency_id.id
            move_lines = []
            line_total = debit - credit
            if voucher.type == 'sale':
                line_total = line_total - currency_pool.compute(cr, uid, voucher.currency_id.id, company_currency, voucher.tax_amount, context=context_multi_currency)
            elif voucher.type == 'purchase':
                line_total = line_total + currency_pool.compute(cr, uid, voucher.currency_id.id, company_currency, voucher.tax_amount, context=context_multi_currency)
            # Create Payment Terms move lines
            """if voucher.payment_term:
                move_lines=self.action_payment_term_create(cr,uid,voucher,context=context) 
            # Create Move Line for each voucher line'''"""
            if account_id:
                ml_id = move_line_pool.create(cr, uid,{
                    'name': voucher.name or '/',
                    'debit': debit,
                    'credit': credit,
                    'account_id': account_id ,
                    'move_id': move_id,
                    'journal_id': journal_id.id,
                    'period_id': period_id.id,
                    'partner_id': voucher.partner_id.id,
                    'currency_id': company_currency != current_currency and  current_currency or False,
                    'amount_currency': company_currency != current_currency and sign * voucher.amount or 0.0,
                    'date': date,
                    'date_maturity': voucher.date_due,
                    'ref': voucher.number,
                },context=context)
            rec_list_ids=[]
            for line in voucher.line_ids:
                #if voucher.type == 'purchase' and 'state' in voucher_line_pool._columns and line.state != 'approve':
                    #continue
                if not line.account_id:
                    raise orm.except_orm(_('Entry Error!'),_("Please make sure you enter an account for each voucher line!"))
                if not line.amount:
                    continue
                if line.amount == line.amount_unreconciled or (voucher.payment_option == 'with_writeoff' and line.amount < line.amount_unreconciled):
                    amount = line.move_line_id.amount_residual
                else :
                    amount = currency_pool.compute(cr, uid, current_currency, company_currency, line.amount, context=context_multi_currency)
                move_line = {
                    'journal_id': journal_id.id,
                    'period_id': period_id.id,
                    'name': line.name and line.name or '/',
                    'account_id': line.account_id.id,
                    'move_id': move_id,
                    'partner_id': voucher.partner_id.id,
                    'currency_id': company_currency != current_currency and current_currency or False,
                    'analytic_account_id': line.account_analytic_id and line.account_analytic_id.id or False,
                    'quantity': 1,
                    'credit': 0.0,
                    'debit': 0.0,
                    'date': date,
                    'ref': voucher.number,
                    'budget_confirm_id': 'budget_confirm_id' in voucher_line_pool._columns and line.budget_confirm_id and line.budget_confirm_id.id,
                    'budget_line_id': 'budget_confirm_id' in voucher_line_pool._columns and line.budget_confirm_id.budget_line_id and line.budget_confirm_id.budget_line_id.id
                }
                print "PPPP##",period_id
                if amount < 0:
                    amount = -amount
                    if line.type == 'dr':
                        line.type = 'cr'
                    else:
                        line.type = 'dr'

                if (line.type=='dr'):
                    line_total += amount
                    move_line['debit'] = amount
                    move_line['amount_currency'] = company_currency != current_currency and line.amount or 0.0
                else:
                    line_total -= amount
                    move_line['credit'] = amount
                    move_line['amount_currency'] = company_currency != current_currency and -line.amount or 0.0
                # Create Taxs Move Lines
                tax_line = move_line.copy()
                taxs = voucher.tax_id and (isinstance(voucher.tax_id,list)and voucher.tax_id or [voucher.tax_id]) or []
                
                for tax in tax_pool.compute_all(cr, uid, taxs, line.untax_amount, 1.00).get('taxes'):
                    tax_amount= currency_pool.compute(cr, uid, voucher.currency_id.id, company_currency, tax['amount'], context={'date': date or time.strftime('%Y-%m-%d')}, round=False)
                    tax_line.update({
                        'account_tax_id': False,
                        'account_id': tax['account_collected_id'] and tax['account_collected_id'] or move_line['account_id'],
                        'credit':  (voucher.type == 'purchase' and tax_amount<0 and -tax_amount) or (voucher.type == 'sale' and tax['amount']>0 and tax['amount']) or 0.0,
                        'debit': (voucher.type == 'purchase' and tax_amount>0 and tax_amount) or (voucher.type == 'sale' and tax['amount']<0 and -tax['amount']) or 0.0,
                        'amount_currency': company_currency != current_currency and tax['amount'] or 0.0,
                        'budget_confirm_id': 'budget_confirm_id' in voucher_line_pool._columns and 
                                            (not tax['account_collected_id'] or tax['account_collected_id'] == move_line['account_id']) and line.budget_confirm_id.id,
                        'budget_line_id': 'budget_confirm_id' in voucher_line_pool._columns and (not tax['account_collected_id'] or tax['account_collected_id'] == move_line['account_id']) and 
                                            line.budget_confirm_id.budget_line_id and line.budget_confirm_id.budget_line_id.id
                    })

                    move_line_pool.create(cr, uid, tax_line, context=context)
                print "%%%%%%%",move_line    
                voucher_line=move_line_pool.create(cr, uid, move_line, context=context)
                print "Aftr END&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&"
                if line.move_line_id.id:
                    #voucher_line = move_line_pool.create(cr, uid, move_line)
                    rec_ids = [voucher_line, line.move_line_id.id]
                    rec_list_ids.append(rec_ids)

            ml_writeoff = self.writeoff_move_line_get(cr, uid, voucher.id, line_total, move_id, name, company_currency, current_currency, context)
            if ml_writeoff:
                move_line_pool.create(cr, uid, ml_writeoff, context)

            self.write(cr, uid, [voucher.id], {
                'move_id': move_id,
            }, context=context)
            print "11111111111111111111111111111111111111111111111111111"
            #move_pool.write(cr, uid, [move_id],{'line_id': move_lines and move_lines,},context={'check':True})
            print "222222222222222222222222222222222222222222222222222222"
            #move_pool.completed(cr, uid, [move_id], context=context)
            #move_pool.create_log(cr, uid, [move_id], 'draft', 'completed', 'from_voucher', context)
            #move_pool.closed(cr, uid, [move_id], context=context) 
            #move_pool.create_log(cr, uid, [move_id], 'completed', 'closed', 'from_voucher', context)           
            #move_pool.post(cr, uid, [move_id], context=context)
            #reconcile = False
            #for rec_ids in rec_list_ids:
                #if len(rec_ids) >= 2:
                #    reconcile = move_line_pool.reconcile_partial(cr, uid, rec_ids, writeoff_acc_id=voucher.writeoff_acc_id.id, writeoff_period_id=voucher.period_id.id, writeoff_journal_id=voucher.journal_id.id)
        return ml_id 

    def name_get(self, cr, uid, ids, context=None):
        """Append the employee code to the name"""
        if not ids:
            return []
        if isinstance(ids, (int, long)):
            ids = [ids]
        res = [ (r['id'], r['number'] and '%s' % (r['number']) )
                for r in self.read(cr, uid, ids, ['number'],
                                   context=context) ]
        return res


class account_fiscalyear_budget(osv.Model):
    """
    Account fiscalyear's Budget.
    It identifies the cost center and the fiscalyear which the budget belongs to,
    and the linked lines of detail with the accounts planned amount.
    """
    _name = "account.fiscalyear.budget"

    _inherit = "account.fiscalyear.budget"

    _description = "Fiscal Year Budget"

    _columns = {

        'budget_classification': fields.many2one('account.budget.classification', 'Classification'),
    }

    def change_class(self, cr, uid, ids, budget_classification,lines, context=None):
        
        account_obj = self.pool.get('account.account')

        accounts = account_obj.search(cr, uid, [('budget_classification', '=', budget_classification)], context=context)
        
        accounts = [{'general_account_id': acc, 'planned_amount': 0.0} for acc in accounts]

        return {
    	'value': {
                'account_fiscalyear_budget_line':accounts,
                }
                }

#----------------------------------------------------------
# Change the Order by code 
#----------------------------------------------------------
class account_analytic_account(osv.Model):
    _inherit = 'account.analytic.account'
    _order = 'code'

    _columns = {
        'group_ids': fields.many2many('res.groups', 'account_analytic_groups_rel', 'analytic_id', 'group_id', 'Groups'),
        'revenue': fields.boolean('Revenue', help="Used if this a revenue analytic account"),
    }

#----------------------------------------------------------
# Create Invoice Sequence ID 
#----------------------------------------------------------
class account_journal(osv.osv):
    _inherit = "account.journal"

    _columns = {
        'invoice_sequence_id': fields.many2one('ir.sequence', 'Invoice Sequence', help="This sequence will be used to maintain the invoice number for the account invoice related to this journal."),
    }

#----------------------------------------------------------
# Create Invoice Sequence ID In complete Taska
#----------------------------------------------------------
class account_invoice(osv.osv):
    _inherit = "account.invoice"

    _columns = {
    'internal_sequence': fields.char('Internal Number', size=32, help="Unique number of the invoice, computed automatically when the invoice is completed."),
    'partner_name': fields.char('Customer Name', size=64, help="Write customer name here if not created in the system"),
    'partner_id': fields.many2one('res.partner', required=False),
    }

    def create(self, cr, uid, vals, context=None):
        """
        Override to add Internal sequance
        @param vals: Dictionary of values
        """
        if ('internal_sequence' not in vals) or (vals.get('internal_sequence') == '/'):
                journal_id = vals.get('journal_id', False)
                journal = self.pool.get('account.journal').browse(cr, uid, journal_id, context )
                if journal.invoice_sequence_id:
                    invoice_sequence = self.pool.get('ir.sequence').get_id(cr, uid, journal.invoice_sequence_id.id)
                    vals.update({'internal_sequence': invoice_sequence, })
        return super(account_invoice, self).create(cr, uid, vals, context)
        
    def to_complete(self, cr, uid, ids, context=None):
        """
        @return: change records state to 'complete' and create invoice sequence
        """
        for record in self.browse(cr, uid, ids, context=context):
            vals = {'state':'complete', 'check_total': record.amount_total}
            if not record.internal_sequence:
                journal = record.journal_id
                if not journal.invoice_sequence_id:
                    raise orm.except_orm(_('Error!'), _('Journal %s has no sequence defined for Invoice.') % journal.name)
                invoice_sequence = self.pool.get('ir.sequence').get_id(cr, uid, journal.invoice_sequence_id.id)
                vals.update({'internal_sequence': invoice_sequence, })
            self.write(cr, uid, record.id, vals, context)
        return True

    def action_number(self, cr, uid, ids, context=None):
        """
        update account move ref with invoice internal sequence
        """
        super(account_invoice, self).action_number(cr, uid, ids, context=context)
        for record in self.browse(cr, uid, ids, context=context):
            if record.move_id and record.internal_sequence:
                move_id = record.move_id.id
                ref = record.internal_sequence
                cr.execute('UPDATE account_move SET ref=%s WHERE id=%s',(ref, move_id))

                cr.execute('UPDATE account_move_line SET ref=%s WHERE move_id=%s', (ref, move_id))

                cr.execute('UPDATE account_analytic_line SET ref=%s ' \
                    'FROM account_move_line ' \
                    'WHERE account_move_line.move_id = %s ' \
                        'AND account_analytic_line.move_id = account_move_line.id', (ref, move_id))
        return True

    def onchange_partner_id(self, cr, uid, ids, type, partner_id,\
            date_invoice=False, payment_term=False, partner_bank_id=False, company_id=False):
        """
        Inherit to fill Partner Name field
        """
        res = super(account_invoice, self).onchange_partner_id(
                                                                cr,
                                                                 uid,
                                                                 ids,
                                                                 type,
                                                                 partner_id,
                                                                 date_invoice,
                                                                 payment_term
                                                            )
        #This case used to changr partner name field in draft state and out invoice
        partner_name = self.pool.get('res.partner').browse(cr, uid, partner_id).name
        invoice_state = ids and self.browse(cr, uid, ids[0]).state or 'draft'
        if type == 'out_invoice' and invoice_state == 'draft':
            res['value'].update({'partner_name': partner_name})
        return res

    def action_move_create(self, cr, uid, ids, context=None):
        """Inherited to write account move in completed state"""
        if context is None:
            context = {}
        move_pool = self.pool.get('account.move')
        res = super(account_invoice,self).action_move_create(cr, uid, ids, context=context)
        move_ids = [invoice.move_id.id for invoice in self.browse(cr, uid, ids, context)]
        #self.pool.get('account.move').write(cr, uid, account_ids, {'state':'completed'}, context)
        move_pool.completed(cr, uid, move_ids, context)
        move_pool.create_log(cr, uid, move_ids, 'draft', 'completed', 'from_invoice', context)
        return res

#----------------------------------------------------------
# Inherit Account Invoice Line Class
#----------------------------------------------------------
class account_invoice_line(osv.Model):
    """
    Inherit model to override and add method
    """
    _inherit = 'account.invoice.line'

    def onchange_account_id(self, cr, uid, ids, product_id, partner_id, inv_type, fposition_id, account_id):
        """
        Inherit to return value of analytic account if account is linked with budget
        """
        analytic_account_id = False
        budget_line_obj = self.pool.get('account.budget.lines')
        budget_line_id = budget_line_obj.search(cr, uid, [('general_account_id','=',account_id)])
        if budget_line_id:
            budget = budget_line_obj.browse(cr, uid, budget_line_id[0])
            analytic_account_id = budget.account_budget_id.analytic_account_id.id
        res = super(account_invoice_line, self).onchange_account_id(cr, uid, ids, product_id, partner_id, inv_type, fposition_id, account_id)
        if not res:
            res.update({'value':{'account_analytic_id':analytic_account_id}})
        else:
            res['value']['account_analytic_id'] = analytic_account_id
        return res

#----------------------------------------------------------
# Inherit Account_account_fiscalyear Class
#----------------------------------------------------------
class account_fiscalyear(osv.Model):
    """
    Inherit fiscal year model to make workflow so simple, Just two state open and close
    """
    _inherit = "account.fiscalyear"

    def action_locked_temporarily(self, cr, uid, ids, context=None):
        """
        Overloaded to change state directly to done
        """
        super(account_fiscalyear, self).action_locked_temporarily(cr, uid, ids, context=context)
        return self.write(cr, uid, ids, {'state': 'done'}, context=context)

    def action_open(self, cr, uid, ids, context=None):
        """
        Change state to draft
        """
        self.write(cr, uid, ids, {'state': 'draft'}, context=context)
        return True


#----------------------------------------------------------
# Inherit Account_account Class
#----------------------------------------------------------
class account_account(osv.osv):
    _inherit = "account.account"

    _columns = {
        'group_ids': fields.many2many('res.groups', 'account_groups_rel', 'account_id', 'group_id', 'Groups'),
        'no_code':fields.boolean('No Code'),
        'detialed':fields.boolean('detailed'),
        'bl_report':fields.boolean('BL Report'),
        'with_value':fields.boolean('With Value'),
        'reserve':fields.boolean('reserve'),
 
        #'special':fields.boolean('special'),
    }
    _defaults = {
        'no_code':False,
        'detialed':False,
    }





    def get_accounts(self, cr, uid, ids, vals,code,company_id ,context=None):
        """
        This functions  fill up  the gaps in accounts parents and also correct the wrong one by/
	check the accounts parents correctness accroding to model company accounts with id '1'
        """
 
	match=''
	match_id=0
	parent_match_code=''
 
 
        
        match_main=self.pool.get('account.account').search(cr, uid, [('code','=',code),('company_id','=',1)])

        if not match_main:
           raise orm.except_orm(_('Error!'), _('NO account.'))
       
        for m in self.pool.get('account.account').browse(cr, uid, match_main):
           parent_match_code=m.parent_id.code

        match_id=self.pool.get('account.account').search(cr, uid, [('code','=',parent_match_code),     
('company_id','=',company_id)])

        vals.update({
                'parent_id': match_id[0],

            })
	super(account_account, self).write(cr, uid, ids, vals, context=context)


    def check_accounts(self, cr, uid, ids, vals, context=None):
        """
        this functions aims to fill up  the gaps in accounts parents and also correct the wrong one by/
	check the accounts parents correctness accroding to model company accounts with id '1'
        """
     
 
        
        for record in self.browse(cr, uid, ids, context=context):
            if  record.no_code==True:
	       code='33032000'
            else:
	       code=record.code
            self.get_accounts(cr, uid,ids,vals,code, record.company_id.id,context=None)
	return True

    def check_accounts_all(self, cr, uid, ids, vals, context=None):
        """ 
	Return  conslidation accounts  accorrding to companies chart :TREE
        """ 
        for record in self.browse(cr, uid, ids, context=context):
            child_company_ids = self.pool.get('res.company').search(cr, uid, [('parent_id', '=', record.company_id.id)], context=context)
            if record.type!='consolidation' :
	        raise orm.except_orm(_('Error!'), _('Not a conslidation Account or Not allowed Company'))
            # GET ACCOUNT DEPEND ON PARENTS AND CHILDS 
	    accounts_all=self.pool.get('account.account').search(cr, uid, [('code','=',record.code),('company_id','in',child_company_ids)])
	    cr.execute("DELETE FROM account_account_consol_rel WHERE child_id=%s ", (record.id,)) 
	    for acc in accounts_all:                
	        cr.execute('INSERT INTO account_account_consol_rel\
		    (child_id,parent_id) values (%s,%s)', (record.id, acc))

            # GET ACCOUNTS DEPEND ON COMPANY TYPE
            '''type=record.company_id.type
            if type=='main_locs':
	        company_ids=self.pool.get('res.company').search(cr, uid, [('type','=','locality')])
	        accounts_all=self.pool.get('account.account').search(cr, uid, [('code','=',record.code),('company_id','in',company_ids)])
	        cr.execute("DELETE FROM account_account_consol_rel WHERE child_id=%s ", (record.id,)) 
	        for acc in accounts_all:                
		    cr.execute('INSERT INTO account_account_consol_rel\
		    (child_id,parent_id) values (%s,%s)', (record.id, acc))

            elif type=='main_mins':
	        company_ids=self.pool.get('res.company').search(cr, uid, [('type','=','ministry')])
	        accounts_all=self.pool.get('account.account').search(cr, uid, [('code','=',record.code),('company_id','in',company_ids)])
	        cr.execute("DELETE FROM account_account_consol_rel WHERE child_id=%s ", (record.id,)) 
	        for acc in accounts_all:                
		    cr.execute('INSERT INTO account_account_consol_rel\
		    (child_id,parent_id) values (%s,%s)', (record.id, acc))

	    elif type=='main_others':
	        company_ids=self.pool.get('res.company').search(cr, uid, [('type','=','other')])
	        accounts_all=self.pool.get('account.account').search(cr, uid, [('code','=',record.code),('company_id','in',company_ids)])
	        cr.execute("DELETE FROM account_account_consol_rel WHERE child_id=%s ", (record.id,)) 
	        for acc in accounts_all:                
		    cr.execute('INSERT INTO account_account_consol_rel\
		    (child_id,parent_id) values (%s,%s)', (record.id, acc))
            else:
		company_ids=self.pool.get('res.company').search(cr, uid, [('type','in',('main_locs','main_mins','main_others'))])
	        accounts_all=self.pool.get('account.account').search(cr, uid, [('code','=',record.code),('company_id','in',company_ids)])
	        cr.execute("DELETE FROM account_account_consol_rel WHERE child_id=%s ", (record.id,)) 
	        for acc in accounts_all:                
		    cr.execute('INSERT INTO account_account_consol_rel\
		    (child_id,parent_id) values (%s,%s)', (record.id, acc))  '''                        
	return True
#----------------------------------------------------------
# Inherit Res Company Class
#----------------------------------------------------------

class res_company(osv.osv):
    _inherit = "res.company"

    _columns = {
	'type': fields.selection([('main', 'main'),('main_locs', 'main_locs'),('main_mins', 'main_mins'),('main_others', 'main_others'),('ministry', 'ministry'), ('locality', 'locality'), ('other', 'other'),('loc_sub', 'loc_sub')], "Type"),
    'out_budget':fields.boolean('out_budget'),
    }
   

