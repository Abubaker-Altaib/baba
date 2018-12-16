# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################
from mx import DateTime
import time
from datetime import datetime
from openerp.osv import osv, fields, orm
from openerp.tools.translate import _
import netsvc
import openerp.addons.decimal_precision as dp

#----------------------------------------
#transfer accounts 
#----------------------------------------
class hr_transfer_account(osv.osv_memory):

    _name = 'hr.transfer.account'

    _columns = {
        'type':fields.selection([('treatment', 'Treatment'), ('compensation', 'Compensation'), ('all', 'All')], 'Type', required=True),
        'partner_id': fields.many2one('res.partner', "Beneficiary", domain="[('supplier','=',True)]", required=True),
    }

    def transfer(self, cr, uid, ids, context=None):
        """
        Method that transfers employee injury from injury form to accounting voucher.
        
        @return: dictionary of action to close wizard 
        """
        if context is None:
            context = {}
        emp_injury_id = context.get('active_id', False)
        injury = self.pool.get('hr.injury').browse(cr, uid, emp_injury_id, context=context)
        data = self.browse(cr, uid, ids[0], context=context)
        company = injury.employee_id.company_id
        analytic_account = injury.department_id.analytic_account_id or company.hr_analytic_account_id
        if not company.hr_journal_id or not analytic_account or not company.treatment_account_id:
            raise osv.except_osv(_('Error'), _('Please make sure that your HR journal, treatment account and analytic account has been configured'))
        amount = 0
        ttype = data.type
        if ttype in ('all', 'compensation'):
            if injury.inability_voucher_id:
                raise osv.except_osv(_('Error'), _('Compensation amount is already transfered to finance section.'))
            if injury.inability_amount <= 0:
                raise osv.except_osv(_('Error'), _('Compensation amount must be positive value.'))
            amount += injury.inability_amount
        if ttype in ('all','treatment'):
            treatment_pool = self.pool.get('hr.injury.treatment')
            treatment_ids = treatment_pool.search(cr, uid, [('injury_id','=',injury.id), ('voucher_id', '=', False)], context=context)
            treatment_amount = sum([r.treatment_amount for r in treatment_pool.browse(cr, uid, treatment_ids, context=context)])
            if treatment_amount <= 0:
                raise osv.except_osv(_('Error'), _('There is no treatment to transfer.'))
            amount += treatment_amount
        line = {'account_id': company.treatment_account_id.id, 'account_analytic_id': analytic_account.id, 'amount': amount}
        voucher = self.pool.get('payroll').create_payment(cr, uid, ids, {'partner_id': data.partner_id.id, 'lines':[line],
                                                                         'reference': 'HR/Employee Injury/'+injury.employee_id.name+' - '+str(injury.injury_date)}, context=context)
        if ttype in ('all', 'compensation'):
            injury.write({'inability_voucher_id': voucher})
        if ttype in ('all','treatment'):
            treatment_pool.write(cr, uid, treatment_ids, {'voucher_id': voucher}, context=context)
        return {'type': 'ir.actions.act_window_close'}

