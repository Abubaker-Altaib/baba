from openerp.osv import osv

class account_bank_statement(osv.Model):
	_inherit='account.bank.statement'
	def _start_balance(self, cr, uid,ids, journal_id, statement_date, context=None):
		sum = 0
		account_voucher = self.pool.get('account.voucher')
		search_ids = account_voucher.search(cr,uid,[('move_id','!=',False),('date','<=',statement_date),
												('pay_journal_id','=',journal_id),('state','=','receive'),],context=context)
		for voucher in account_voucher.browse(cr,uid,search_ids,context=context):
				sum += voucher.amount
		return super(account_bank_statement,self)._start_balance(cr, uid,ids,journal_id = journal_id, statement_date = statement_date) + sum
		

		