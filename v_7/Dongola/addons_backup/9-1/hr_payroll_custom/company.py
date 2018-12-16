# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
###############################################################################

from openerp.osv import fields, osv

class res_company(osv.osv):
    _inherit = "res.company"
    """Inherits res.company to add feilds for accounting configuration and to spesify the employee types that can undergone the payroll process.
    """
    _columns = {
              'hr_journal_id':fields.many2one('account.journal','HR Journal'),
              'hr_rev_journal_id':fields.many2one('account.journal','HR Revenue Journal'),
              'stamp_account_id': fields.many2one('account.account',"Stamp Account",domain="[('user_type.report_type','=','expense'),('type','!=','view')]"),
              'allowance_deduction_employee' : fields.boolean('Allowance Deduction for Employee'),
              'allowance_deduction_contractors' : fields.boolean('Allowance Deduction for Contractors'),
              'allowance_deduction_recruit' : fields.boolean('Allowance Deduction for Recruit'),
              'allowance_deduction_trainee' : fields.boolean('Allowance Deduction for Trainee'),
    }
    _defaults = {

         'allowance_deduction_employee':True,

                }




# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
