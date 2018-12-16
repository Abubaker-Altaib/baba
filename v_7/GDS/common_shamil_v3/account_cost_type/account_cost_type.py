# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################
import netsvc
import pooler
from openerp.osv import osv, fields, orm
from openerp.tools.translate import _



class account_cost_type(osv.osv):
    _name = "account.cost.type"
    _description = "Account Cost Type"
    _columns = {
        'name': fields.char('Cost Type Name', size=64, required=True),
        'code': fields.char('Code', size=32),
        'note': fields.text('Description'),       
    }
    _defaults = {
       
    }
    _order = "code"


def _code_get(self, cr, uid, context=None):
    acc_type_obj = self.pool.get('account.cost.type')
    ids = acc_type_obj.search(cr, uid, [])
    res = acc_type_obj.read(cr, uid, ids, ['code', 'name'], context=context)
    return [(r['code'], r['name']) for r in res]

class account_account(osv.osv):
    _inherit = "account.account"
    _description = "Cost Type"
    

    _columns = {
        'cost_type_id':fields.many2one('account.cost.type', 'Cost Type'),
        'devolopment_projects': fields.boolean('Devolopment Projects'), 
    }
    _defaults = {
        'devolopment_projects': False,
        }


class account_voucher_line(osv.osv):
    _inherit = 'account.voucher.line'
            
    _columns = {
        'cost_type_id':fields.many2one('account.cost.type', 'Cost Type'),
    }


class account_move_line(osv.osv):
    _inherit = 'account.move.line'
            
    _columns = {
        'cost_type_id':fields.many2one('account.cost.type', 'Cost Type'),
    }




class account_voucher(osv.osv):

    _inherit = 'account.voucher'

    def open_voucher(self, cr, uid, ids, context={}):
	self.compute_tax(cr, uid, ids, context)
        for v in self.browse(cr, uid, ids, context=context):

	    if v.account_change and not v.account_id.reconcile:
                raise orm.except_orm(_('Error!'), _('The account is not defined to be reconciled !'))

	    if v.line_ids[0].account_id.devolopment_projects== True and v.line_ids[0].cost_type_id.id == False:
                raise orm.except_orm(_('Attension:'), _("The account %s '%s'  set to be Devolopment Project but the Cost Type is missing in the account move line ." % (v.line_ids[0].account_id.code, v.line_ids[0].account_id.name, )))

        self.write(cr, uid, ids, {'state': 'complete'})
        return True



    def action_move_line_create(self, cr, uid, ids, vals={}, context=None):
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
        for voucher in self.browse(cr, uid, ids, context=context):
            if voucher.move_id:
                continue
            period_id = vals.get('period') or voucher.period_id
            date = vals.get('date') or voucher.date
            journal_id = vals.get('journal') or voucher.pay_journal_id or voucher.journal_id
            account_id = vals.get('account') or (voucher.account_id and voucher.account_id.id) or \
                                (voucher.type in ('purchase', 'payment') and journal_id.default_credit_account_id.id) or \
                                (voucher.type in ('sale', 'receipt') and journal_id.default_debit_account_id.id)

	    if not account_id and voucher.pay_now != 'pay_now':
		account_id = (voucher.journal_id.type in ('sale', 'sale_refund') and \
			voucher.partner_id.property_account_receivable and voucher.partner_id.property_account_receivable.id) \
			or (voucher.journal_id.type in ('purchase', 'purchase_refund') and \
			voucher.partner_id.property_account_payable and voucher.partner_id.property_account_payable.id) or False
		self.write(cr, uid, [voucher.id],{'account_id': account_id})
            if not account_id:
                raise osv.except_osv(_('Entry Error!'), _('Voucher Account must be added!'))


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
            totlines = False
            total_currency = 0
            line_total = debit - credit
            if voucher.type == 'sale':
                line_total = line_total - currency_pool.compute(cr, uid, voucher.currency_id.id, company_currency, voucher.tax_amount, context=context_multi_currency)
            elif voucher.type == 'purchase':
                line_total = line_total + currency_pool.compute(cr, uid, voucher.currency_id.id, company_currency, voucher.tax_amount, context=context_multi_currency)
            # Create Payment Terms move lines
            if voucher.payment_term:
                move_lines=self.action_payment_term_create(cr,uid,voucher,context=context) 
            # Create Move Line for each voucher line'''
            else :
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
                if voucher.type == 'purchase' and 'state' in voucher_line_pool._columns and line.state != 'approve':
                    continue
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
                voucher_line=move_line_pool.create(cr, uid, move_line, context=context)

                if line.move_line_id.id:
                    #voucher_line = move_line_pool.create(cr, uid, move_line)
                    rec_ids = [voucher_line, line.move_line_id.id]
                    rec_list_ids.append(rec_ids)

            ml_writeoff = self.writeoff_move_line_get(cr, uid, voucher.id, line_total, move_id, name, company_currency, current_currency, context)
            if ml_writeoff:
                move_line_pool.create(cr, uid, ml_writeoff, context)

            self.write(cr, uid, [voucher.id], {
                'move_id': move_id,
                'state': 'posted',
            }, context=context)
            move_pool.write(cr, uid, [move_id],{'line_id': move_lines and move_lines,},context={'check':False})
            move_pool.post(cr, uid, [move_id], context=context)
            reconcile = False
            for rec_ids in rec_list_ids:
                if len(rec_ids) >= 2:
                    reconcile = move_line_pool.reconcile_partial(cr, uid, rec_ids, writeoff_acc_id=voucher.writeoff_acc_id.id, writeoff_period_id=voucher.period_id.id, writeoff_journal_id=voucher.journal_id.id)
        return ml_id


    


class account_move(osv.osv):

    _inherit = 'account.move'


    def completed(self, cr, uid, ids, context=None):
        if not(self.validate(cr, uid, ids, context) and len(ids)):
            raise orm.except_orm(_('Integrity Error !'), _('You can not Complete a non-balanced entry !\nMake sure you have configured Payment Term properly !\nIt should contain atleast one Payment Term Line with type "Balance" !'))      
        for move in self.browse(cr, uid, ids):
                if move.name =='/':
                    new_name = False
                    journal = move.journal_id
                    if journal.sequence_id:
                        c = {'fiscalyear_id': move.period_id.fiscalyear_id.id}
                        #new_name = self.pool.get('ir.sequence').get_id(cr, uid, journal.sequence_id.id, context=c)
                    else:
                        raise orm.except_orm(_('Error'), _('No sequence defined in the journal !'))
                    if new_name:
                        self.write(cr, uid, [move.id], {'name':new_name})

                    print' dev',move.line_id[0].account_id.devolopment_projects
                    print 'cost',move.line_id[0].cost_type_id.id

                    if move.line_id[0].account_id.devolopment_projects== True and move.line_id[0].cost_type_id.id == False:
                	raise orm.except_orm(_('Attension:'), _("The account %s '%s'  set to be Devolopment Project but the Cost Type is missing in the account move line ." % (move.line_id[0].account_id.code, move.line_id[0].account_id.name, )))

        
        self.write(cr, uid, [move.id], {'state':'completed'})
        return True


