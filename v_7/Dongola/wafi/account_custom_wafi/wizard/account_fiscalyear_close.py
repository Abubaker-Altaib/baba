# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################
from openerp.osv import osv

class account_fiscalyear_close(osv.osv_memory):

    _inherit = "account.fiscalyear.close"

    def data_save(self, cr, uid, ids, context=None):
        """
        Inherit data_save method to open closed period which opening move will create in before creation,
        then close the period & fiscal year
        
        @return: super data_save
        """
        data =  self.read(cr, uid, ids, [],context=context)[0]
        self.pool.get('account.period').write(cr, uid, data['period_id'][0],{'state': 'draft'}, context=context)
        res = super(account_fiscalyear_close, self).data_save(cr, uid, ids, context=context)
        self.pool.get('account.period').write(cr, uid, data['period_id'][0],{'state': 'done'}, context=context)
        self.pool.get('account.fiscalyear').write(cr, uid, data['fy_id'][0], {'state': 'done'}, context=context)
        return res


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
