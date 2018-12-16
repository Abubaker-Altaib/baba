# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2013-2014 NCTR (<http://www.nctr.sd>).
#
##############################################################################

from openerp.osv import fields, osv, orm
from openerp.tools.translate import _

class account_voucher(osv.Model):
    """
    Inherit account voucher model to auto reconcile move line that created from voucher created from bank reconciliation
    """
    _inherit = "account.voucher"

    _columns = {
            'account_statement_line_ids': fields.one2many('account.bank.statement.line', 'voucher_id', 'Bank Statement Lines'),
    }

    def action_move_line_create(self, cr, uid, ids, vals={}, context=None):
        """
        Auto reconcile bank move line in the voucher which created from bank statement 
        @parm vals : dict that contains new values
        """
        if ids:
            ml_ids = super(account_voucher, self).action_move_line_create(cr, uid, ids, vals, context=context)
            ml_pool = self.pool.get('account.move.line')
            voucher = self.browse(cr, uid, ids, context=context)
            voucher = isinstance(voucher,list) and voucher[0] or voucher
            st = voucher.account_statement_line_ids and voucher.account_statement_line_ids[0].statement_id.id
            ml_pool.write(cr, uid, ml_ids,{'statement_id':st}, context=context)

class accouunt_bank_statement(osv.Model):
    """
    Inherit bank statement model to modify the calculation of total_entry_encoding by excluding statement lines which has voucher with moves 
    """
    _inherit = "account.bank.statement"

    def reconcile(self, cr, uid, ids, context=None):
        voucher_obj = self.pool.get('account.voucher')
        for statement in self.browse(cr, uid, ids, context=context):
            for line in statement.line_ids:
                if line.line_type == "out_line":
                    type=('payment','purchase')
                else:
                    type=('receipt','sale')
                
                voucher = voucher_obj.search(cr,uid,[( 'journal_id','=',statement.journal_id and statement.journal_id.id or False),
                    ( 'amount','=',line.amount ),('chk_seq','=',line.name),('type','in',type)])
                if voucher:
                    self.pool.get('account.bank.statement.line').write(cr, uid, line.id,{'voucher_id':voucher[0]}, context=context)

                    move_line_obj = self.pool.get('account.move.line')
                    move_ids = voucher_obj.browse(cr,uid,voucher[0]).move_ids
                    move_lins = move_line_obj.search(cr,uid,[( 'id','in',move_ids ),( 'account_id','=',statement.account_id.id )])
                    move_line_obj.write(cr, uid, move_lins,{'statement_id':statement.id}, context=context)


    
    def _get_statement(self, cr, uid, ids, context=None):
        """
        Get statement id from bank statement
        @return : list of statement_ids for bank statement line
        """
        return [line.statement_id.id for line in self.pool.get('account.bank.statement.line').browse(cr, uid, ids, context=context)]

    def _get_voucher_statement(self, cr, uid, ids, context=None):
        """
        To get statement ids from account voucher model
        return: list of statement ids from voucher_id
        """
        line_pool = self.pool.get('account.bank.statement.line')
        line_ids = line_pool.search(cr, uid, [('voucher_id','in',ids)], context=context)
        return [line.statement_id.id for line in line_pool.browse(cr, uid, line_ids, context=context)]

    def _get_sum_entry_encoding(self, cr, uid, ids, name, arg, context=None):
        """
        Find encoding total of statements as a sum of lines amount 
        which doesn't have voucher's move"
        @param name: Names of fields.
        @param arg: User defined arguments
        @return: Dictionary of values.
        """
        res = {}.fromkeys(ids,0)
        for statement in self.browse(cr, uid, ids, context=context):
            for line in statement.line_ids:
                if not (line.voucher_id and  line.voucher_id.move_id):
                    res[statement.id] += line.amount
        return res

    _columns = {
        'total_entry_encoding': fields.function(_get_sum_entry_encoding, string="Cash Transaction", help="Total cash transactions",
            store = {
                'account.bank.statement': (lambda self, cr, uid, ids, c={}: ids, ['line_ids','move_line_ids'], 10),
                'account.bank.statement.line': (_get_statement, ['amount'], 10),
                'account.voucher': (_get_voucher_statement, ['move_id'], 10),
            }),
    }


class accouunt_bank_statement_line(osv.Model):
    """
    Inherit bank statement lines to add the ability of creating voucher from each created line 
    """
    _inherit = "account.bank.statement.line"

    def create_voucher(self, cr, uid, ids, context=None):
        """
        This function allow accountant to create voucher from statement lines 
        which represent moves in bank & didn't appear in journal
        @return: dict an action open Payment/Receipt voucher with some default values to create voucher
        """
        if not ids: return []
        line = self.browse(cr, uid, ids[0], context=context)
        
        if line.voucher_id:
            raise orm.except_orm(_('Integrity Error!'), _('This line already has voucher before!'))
        domain = line.line_type == "out_line" and '%purchase%' or '%sale%'
        return {
            'name':_("Payment/Receipt"),
            'view_mode': 'form',
            'view_id': self.pool.get('ir.ui.view').search(cr, uid, [('model','=','account.voucher'),('type','=','form'),
                                                                    ('name','ilike',domain)], context=context),
            'view_type': 'form',
            'res_model': 'account.voucher',
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'target': 'current',
            'domain': '[]',
            'context': {
                'default_pay_journal_id': line.statement_id.journal_id.id,
                'default_account_id': line.line_type == "out_line" and line.statement_id.journal_id.default_credit_account_id.id or 
                                        line.statement_id.journal_id.default_debit_account_id.id,
                'default_partner_id': line.partner_id.id,
                'default_company_id': line.statement_id.company_id.id,
                'default_amount': abs(line.amount),
                'default_date': line.date,
                'default_name':line.ref,
                'default_account_statement_line_ids':[(4,line.id)],
                'default_chk_seq':line.name,
                'default_reference':line.statement_id.name,
                'close_after_process': True,
                'default_type': line.line_type == "out_line" and 'purchase' or 'sale',
                'type': line.line_type == "out_line" and 'purchase' or 'sale',
                'default_line_cr_ids':line.line_type == "in_line" and [{'name': line.ref, 'amount': abs(line.amount)}] or [],
                'default_line_dr_ids':line.line_type == "out_line" and [{'name': line.ref, 'amount': abs(line.amount)}] or []
                }
        }


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

