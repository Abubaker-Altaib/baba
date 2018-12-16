# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################
from openerp.osv import osv

class account_fiscalyear_close(osv.osv_memory):
    """
    Closes Account fiscal year and generate closing entries for the selected fiscal year revenue & expense accounts
    """
    _inherit = "account.fiscalyear.pl.close"

    def data_save(self, cr, uid, ids, context=None):
        """
        This function close Profit & loss account of the selected fiscal year by create entries in the closing period
        
        @param cr: the current row, from the database cursor,
        @param uid: the current user’s ID for security checks,
        @param ids: List of Account fiscal year close state’s IDs
        """
        data =  self.read(cr, uid, ids, [],context=context)[0]
        self.pool.get('account.period').write(cr, uid, data['period_id'][0],{'state': 'draft'}, context=context)
        res = super(account_fiscalyear_close, self).data_save(cr, uid, ids, context=context)
        self.pool.get('account.period').write(cr, uid, data['period_id'][0],{'state': 'done'}, context=context)
        self.pool.get('account.fiscalyear').write(cr, uid, data['fiscalyear_id'][0], {'state': 'first_lock'}, context=context)
        return res


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

