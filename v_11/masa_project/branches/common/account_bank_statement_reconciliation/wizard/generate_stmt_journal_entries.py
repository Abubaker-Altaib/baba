# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2018-2019 NCTR (<http://www.nctr.sd>).
#
##############################################################################


from odoo import api, fields, models,_
from odoo.exceptions import ValidationError


class GenerateStmtJournalEntries(models.TransientModel):

	_name = "generate.stmt.journal.entries"


	analytic_account_id = fields.Many2one('account.analytic.account', string="Analytic account", required=True, domain=[('type', '=', 'normal')])
	account_id = fields.Many2one('account.account', string="Account", required=True, domain=[('deprecated', '=', False)])
	stmt_line_ids = fields.Many2many('account.bank.statement.line',string='Stmt Lines')

	@api.multi
	def generate_journal_entries(self):
	    move_obj=self.env["account.move"]
	    aml_obj=self.env["account.move.line"]
	    res = []
	    bnk_stmt_id = self.env.context.get('active_id', False)
	    if bnk_stmt_id:
	        bnk_stmt=self.env['account.bank.statement'].browse(bnk_stmt_id)
	        data = {
	            'journal_id': bnk_stmt.journal_id.id,
	            'date': bnk_stmt.date,
	            'ref': bnk_stmt.name,
	        }
	        for line in self.stmt_line_ids:
	            move=move_obj.create(data)
	            res.append(move.id)
	            aml_debit_dict={
	            'name': line.name,
	            'move_id': move.id,
	            'partner_id': line.partner_id and line.partner_id.id or False,
	            'account_id': self.account_id.id,
	            'credit':line.amount > 0 and line.amount or 0.0 ,
	            'debit': line.amount < 0 and -line.amount or 0.0 ,
	            'statement_line_id': line.id,
	            'analytic_account_id':self.analytic_account_id.id,
	            }
	            aml_obj.with_context(check_move_validity=False).create(aml_debit_dict)

	            aml_credit_dict={
	            'name': line.name,
	            'move_id': move.id,
	            'partner_id': line.partner_id and line.partner_id.id or False,
	            'account_id': line.amount >= 0 \
                and line.statement_id.journal_id.default_credit_account_id.id \
                or line.statement_id.journal_id.default_debit_account_id.id,
	            'credit': line.amount < 0 and -line.amount or 0.0,
	            'debit': line.amount > 0 and line.amount or 0.0,
	            'statement_line_id': line.id,
	            }
	            aml_obj.with_context(check_move_validity=False).create(aml_credit_dict)
	            line.write({'move_name': move.name})
	            move.post()
	        if res:
	            return {
	                'name': _('Generate Stmt Journal Entries'),
	                'type': 'ir.actions.act_window',
	                'view_type': 'form',
	                'view_mode': 'tree,form',
	                'res_model': 'account.move',
	                'domain': [('id', 'in', res)],
	            }
	    return {'type': 'ir.actions.act_window_close'}

