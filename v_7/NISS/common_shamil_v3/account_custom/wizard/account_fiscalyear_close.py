# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################
import time
from openerp.osv import fields, osv
from openerp.tools.translate import _

class account_fiscalyear_close(osv.osv_memory):
    """ inherit account fiscalyear_close add company id and update some methods"""

    _inherit = "account.fiscalyear.close"

    _columns = {
        'company_id': fields.many2one('res.company', 'Company', type='many2one'),
    }
    def _get_fiscalyear(self, cr, uid, context=None):
        """ Get fiscalyear_id
        @return: id of fiscal year
        """
        now = time.strftime('%Y-%m-%d')
        fiscalyears = self.pool.get('account.fiscalyear').search(cr, uid, [('date_start', '<', now), ('date_stop', '>', now)], limit=1 )
        return fiscalyears and fiscalyears[0] or False

    _defaults = {
        'fy_id': _get_fiscalyear,
        
    }
    def onchange_fiscalyear_id(self, cr, uid, ids, fiscalyear_id=False, company_id=False, context=None):
        """
        Inherit method to update report_name values (End of Fiscal Year Entry) 

        @param fiscalyear_id: fiscalyear_id
        @param company_id: company_id
        @return: dictionary of values
        """
        FY = self.pool.get('account.fiscalyear').browse(cr, uid, fiscalyear_id, context=context)
        return {'value': {'company_id': FY and FY.company_id.id or False, 'fy2_id': False, 
                          'journal_id': False, 'period_id': False, 'report_name': _('End of Fiscal Year Entry')}}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
