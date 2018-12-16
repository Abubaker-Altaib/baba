# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
###############################################################################

from openerp.osv import fields, osv
import netsvc

class res_company(osv.Model):
    _inherit = "res.company"
    """Inherits res.company to add feild for accounting configuration 
    """
    _columns = {
              
             'hr_voucher_state': fields.char("HR Voucher State", size=16),
    }
    def _check_state(self, cr, uid, ids, context=None):
        values = self.pool.get('account.voucher')._columns['state'].selection
        for company in self.browse(cr, uid, ids, context=context):
            if company.hr_voucher_state and company.hr_voucher_state not in dict(values).keys():
                return False
        return True

    _constraints = [
        (_check_state, 'Configuration error!\nThis state is not defined in voucher object', ['hr_voucher_state']),
    ]

class payroll(osv.Model):

    _inherit = "payroll"
    _description = "Payroll"

    def create_payment(self, cr, uid, ids, vals = {}, context = None):
        wf_service = netsvc.LocalService("workflow")

        vou_obj = self.pool.get('account.voucher')
        voucher_id = super(payroll, self).create_payment(cr, uid, ids, vals, context)
        voucher = vou_obj.browse(cr, uid, voucher_id, context)
        if voucher.company_id.hr_voucher_state:
            department_id=  vals.get('department_id',False) 

            res = wf_service.trg_validate(uid, 'account.voucher',voucher_id, voucher.company_id.hr_voucher_state, cr)
            vou_obj.write(cr, uid, voucher_id, {'type':'ratification','ratification':True,'department_id':department_id,
                                                'state':voucher.company_id.hr_voucher_state,}, context)
        return voucher_id





# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
