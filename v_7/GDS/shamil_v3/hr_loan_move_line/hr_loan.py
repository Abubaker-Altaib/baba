# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

from openerp.osv import fields, osv, orm
from openerp.tools.translate import _
import time

class hr_loan(osv.Model):
    _inherit = "hr.loan"
    _description = "Loan configuration"
    _columns = {
        'transfer_type' :fields.selection([('per_loan','Per Loan'),('per_partner','Per Partner')],'Transfer Type', required= True),
                }
    _defaults = {
        'transfer_type': 'per_loan',
                }

class hr_employee_salary_addendum(osv.osv):
    _inherit = 'hr.employee.salary.addendum'

    def transfer(self, cr, uid, ids, context = None):
	transfer = super(hr_employee_salary_addendum, self).transfer(cr, uid, ids, context)
        user = self.pool.get('res.users').browse(cr, uid, uid, context = context)
        journal_id = user.company_id.hr_journal_id and user.company_id.hr_journal_id.id or False
        ctx = context.copy()
        ctx.update({'company_id': user.company_id.id, 'account_period_prefer_normal': True})
	period_id = self.pool.get('account.period').find(cr, uid, time.strftime('%Y-%m-%d'), context=ctx)[0]
        data = self.get_data(cr, uid, ids, context = context)
	data_loan = self.get_loan( cr, uid , data,  context=None)
	res = {}
	move_lines = []
	loan_move={
		'journal_id':journal_id,
		'period_id': period_id,
		'date':time.strftime('%Y-%m-%d'),
	}
	move_id = self.pool.get('account.move').create(cr,uid,loan_move) 
	for archive in self.pool.get('hr.loan.archive').browse(cr, uid, data_loan['archive_ids'], context):
		if archive.loan_id.loan_id.transfer_type != 'per_partner': continue
		loan = archive.loan_id.loan_id
		voucher_line_loan={
			'journal_id':journal_id,
			'account_id':loan.loan_account_id.id,
			'date':time.strftime('%Y-%m-%d'),
			'name':archive.loan_id.name,
			'period_id':period_id,
			'debit':0,
			'credit':archive.loan_amount,
			'partner_id':archive.employee_id.user_id.partner_id.id,
			'move_id':move_id
			}
		move_lines = move_lines + [self.pool.get('account.move.line').create(cr,uid,voucher_line_loan)]
		if loan.id in res:
		    res[loan.id].update({'debit':res[loan.id]['debit']+archive.loan_amount})
		else:
		    res[loan.id] = voucher_line_loan.copy()
		    res[loan.id].update({'debit':archive.loan_amount, 'credit':0 })
	if move_lines:
	    for r in res:
		res[r].update({'partner_id':False})
	        move_lines = move_lines + [self.pool.get('account.move.line').create(cr,uid,res[r])]
	    #self.pool.get('account.move.line').write(cr, uid, move_lines, {'move_id':move_id}, context)
        return 	transfer

