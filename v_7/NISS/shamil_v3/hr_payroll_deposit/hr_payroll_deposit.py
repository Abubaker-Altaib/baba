# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2014-2015 NCTR (<http://www.nctr.sd>).
#
##############################################################################

import time
from openerp.osv import fields, osv, orm
from openerp.tools.translate import _

class hr_payroll_deposit(osv.osv):

    _name = 'hr.payroll.deposit'

    def create(self, cr, uid, vals, context={}):
        """
        Inherit create method set name from sequence if exist
        @param default: dictionary of the values of record to be created,
        @return: super method of copy    
        """
        vals.update({'name': vals.get('name','/') == '/' and \
			self.pool.get('ir.sequence').get(cr, uid,'hr.payroll.deposit') or vals.get('name')})
        return super(hr_payroll_deposit, self).create(cr, uid, vals, context=context)

    def copy(self, cr, uid, id, default=None, context=None):
        if default is None:
            default = {}
        default = default.copy()
        default.update({'account_move_line_ids': []})
        return super(hr_payroll_deposit, self).copy(cr, uid, id, default, context=context)

    def confirm(self, cr, uid, ids, context={}):
        return self.write(cr, uid, ids, {'state': 'confirmed' })
    
    def cancel(self, cr, uid, ids, context={}):
        return self.write(cr, uid, ids, {'state': 'canceled' })
    
    def trans2treasury(self, cr, uid, ids, context={}):
	context.update({'account_type':'treasury'})
        self._create_account_move(cr, uid, ids, context)
	self.write(cr, uid, ids, {'state': 'treasury' })			
        return True

    def done(self, cr, uid, ids, context={}):
        context.update({'account_type':'refund'})
        self._create_account_move(cr, uid, ids, context)
	self.write(cr, uid, ids, {'state': 'done' })	
        return True

    def _employee_salary(self, cr, uid, ids, name, args, context=None):
        """
	       Method that returns the salary of employee in the given month and year.
           @return: employee salary
        """
        res = {}
        main_arch_obj = self.pool.get('hr.payroll.main.archive')
        for rec in self.browse(cr, uid, ids, context=context):
            main_arch_id = main_arch_obj.search(cr, uid, [('month','=',rec.month),
                                                          ('year','=',rec.year),
                                                          ('employee_id','=',rec.employee_id.id),
                                                          ('in_salary_sheet','=',True)])
            if not main_arch_id:
                raise osv.except_osv(_('Warning!'), 
                                     _('Sorry employee %s has no Salary in %sth month of the year %s!')\
					%(rec.employee_id.name, rec.month, rec.year))
            emp_salary = main_arch_obj.browse(cr, uid,main_arch_id)
            res[rec.id] = emp_salary and emp_salary[0].net or 0.0   
        return res

    _columns = {
		'name': fields.char('Name', size=64 , readonly=True),
		'date': fields.date('Date', readonly=True, required=True, states={'draft':[('readonly',False)]}),
    	        'employee_id' : fields.many2one('hr.employee','Employee', required=True,\
				  readonly=True, states={'draft':[('readonly',False)]}),
		'responsible_id' : fields.many2one('hr.employee','Responsible Employee', required=True, 
                                     readonly=True, states={'draft':[('readonly',False)]}),
		'amount' : fields.function(_employee_salary,  method=True, string="Employee Salary", type='float',
                                    store = { 'hr.payroll.deposit' : (lambda self,cr,uid,ids,ctx={}:\
					ids, ['employee_id','month','year'], 10),}),
		'state': fields.selection([('draft', 'Draft'),
                                   ('confirmed', 'Confirmed') ,
                                   ('treasury', 'In Treasury'), 
                                   ('done', 'Done'), 
                                   ('canceled', 'Canceled')],'State', select=True, required=True,readonly=True),
		'description': fields.text('Description', required=True, readonly=True, states={'draft':[('readonly',False)]}),
		'month' :fields.selection([(1, 1),(2, 2),(3, 3),(4, 4),(5, 5),\
					 (6, 6),(7, 7),(8, 8),(9, 9),(10, 10),\
					 (11, 11),(12, 12)], "Month", required=True,\
					readonly=True, states={'draft':[('readonly',False)]}),
                'year' :fields.integer("Year", required=True,readonly=True, states={'draft':[('readonly',False)]}),
    		'company_id' : fields.many2one('res.company','Company'),
                'account_move_line_ids': fields.one2many('account.move.line', 'payroll_deposit_id', 'Move lines', required=True, readonly=True,), 
               }

    _defaults = {
		'state' : 'draft',
		'name' : '/',
		'year': int(time.strftime('%Y')),
        'month': int(time.strftime('%m')),
		'date': time.strftime('%Y-%m-%d'),
		'company_id': lambda self, cr, uid, c: self.pool.get('res.company')._company_default_get(cr, uid, 'hr.payroll.deposit', context=c),
	}

    def _create_account_move_line(self, cr, uid, deposit, src_account_id, dest_account_id, reference_amount, context=None):
        """
        Generate the account.move.line values of transfer to deposit and get salary functions
        """
        partner_id = deposit.employee_id.user_id and deposit.employee_id.user_id.partner_id \
                     and deposit.employee_id.user_id.partner_id.id or False
        if not partner_id:
            raise osv.except_osv(_('Warning!'), _("This employee '%s' is not linked with user or partner") %deposit.employee_id.name)
        debit_line_vals = {
                    'name': deposit.name,
                    'ref': deposit.name,
                    'payroll_deposit_id': deposit.id,
                    'date': time.strftime('%Y-%m-%d'),
                    'partner_id': partner_id,
                    'debit': reference_amount,
                    'account_id': dest_account_id,
        }
        credit_line_vals = {
                    'name': deposit.name,
                    'ref': deposit.name,
                    'payroll_deposit_id': deposit.id,
                    'date': time.strftime('%Y-%m-%d'),
                    'partner_id': partner_id,
                    'credit': reference_amount,
                    'account_id': src_account_id,
        }      

        return [(0, 0, debit_line_vals), (0, 0, credit_line_vals)]

    def _create_account_move(self, cr, uid, ids, context={}):
        """
        Create account Journal Entries of transfer to treasury and refund         
        """
        account_move_obj = self.pool.get('account.move')
        for record in self.browse(cr, uid, ids, context=context):
            hr_journal_id = record.company_id.hr_journal_id and record.company_id.hr_journal_id.id or False
            if not hr_journal_id:
                raise osv.except_osv(_('Warning!'), _('Please add HR Journal in the HR setting'))
            deposit_acc_id = record.company_id.hr_deposit_account_id and record.company_id.hr_deposit_account_id.id or False
            if not deposit_acc_id:
                raise osv.except_osv(_('Warning!'), _('Please add HR Deposit Account in the company'))
            deposit_cash_acc_id = record.company_id.hr_deposit_cash_account_id and record.company_id.hr_deposit_cash_account_id.id or False
            if not deposit_cash_acc_id:
                raise osv.except_osv(_('Warning!'), _('Please add HR Deposit Cash Account in the company'))
	    account_type = context.get('account_type',False)
            if account_type == 'treasury':
            # when state= confirmed and context treasury
               move_lines = (self._create_account_move_line(cr, uid, record, deposit_acc_id,\
                                    deposit_cash_acc_id, record.amount, context))
            elif account_type == 'refund':
                if not record.account_move_line_ids:
                    raise osv.except_osv(_('Error!'), _('The treasury transfered journal entries is not found'))
                deposit_acc_id = [line.account_id.id for line in record.account_move_line_ids if line.credit >0][0]
                deposit_cash_acc_id = [line.account_id.id for line in record.account_move_line_ids if line.debit >0][0]
                move_lines = (self._create_account_move_line(cr, uid, record, deposit_cash_acc_id,\
                                    deposit_acc_id, record.amount, context))
            account_move_id = account_move_obj.create(cr, uid,
                        {
                         'journal_id': hr_journal_id,
                         'line_id': move_lines,
                         'ref': record.name}, context=context)
	   
            account_move_obj.completed(cr, uid, [account_move_id], context)
            account_move_obj.post(cr, uid, [account_move_id], context)

#----------------------------------------------------------
# Account Move Line(Inherit)
#----------------------------------------------------------
class account_move_line(osv.Model):

    """ Inherit model to add new feild """

    _inherit = 'account.move.line'

    _columns = {
        'payroll_deposit_id' : fields.many2one('hr.payroll.deposit', 'Payroll Deposit'),
   	    }


