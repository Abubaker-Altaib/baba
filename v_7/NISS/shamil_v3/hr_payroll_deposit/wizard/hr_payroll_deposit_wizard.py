# # -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2014-2015 NCTR (<http://www.nctr.sd>).
#
##############################################################################

from openerp import netsvc
from openerp.osv import fields, osv, orm

class hr_payroll_deposit_wizard(osv.osv):

    _name = 'hr.payroll.deposit.wizard'
    _columns = {
           'deposit_type' :fields.selection([('treasury', 'Treasury'),('refund', 'Refund')], "Deposit Type"),
               }
    _defaults = {
		'deposit_type' : 'treasury'
		}

    def transfer_or_get_salary(self, cr, uid, ids, context={}):
        """
        This function can transfer deposit to treasuray or refund from treasury 
        depending on deposit type field on wizard and state of recorda
        """
        deposit_obj = self.pool.get('hr.payroll.deposit')
        wf_service = netsvc.LocalService("workflow")	
        deposit_ids = context.get('active_ids')	
        wizard_deposit_type = self.browse(cr, uid, ids[0]).deposit_type
        deposit_records=deposit_obj.browse(cr,uid,deposit_ids, context)
        for deposit in deposit_records:
            #To transfer deposit to treasury must first be in Confirmed state 
            if wizard_deposit_type=='treasury' and deposit.state == 'confirmed':
                wf_service.trg_validate(uid, 'hr.payroll.deposit', deposit.id, 'trans2treasury', cr)
            #To refund the deposit from treasury must first be in treasury state 
            if wizard_deposit_type=='refund' and deposit.state == 'treasury':
                wf_service.trg_validate(uid, 'hr.payroll.deposit', deposit.id, 'done', cr)
        return True



