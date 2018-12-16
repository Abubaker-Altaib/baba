# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

from openerp.osv import fields, osv

class account_balance_report(osv.osv_memory):
    """
    Inherit balance report wizard to add some displaying options:
        *  Assisstant Report
    """
    _inherit = "account.balance.report"

    _columns = {
        'assistant_report':fields.boolean('Assistant Report'),
        'unit_type':fields.selection([('ministry', 'ministry'), ('locality', 'locality'), ('other', 'other')], "Type"),

    }


    _defaults = {
        'assistant_report': False,
        'unit': 'assist',
        
    }

    def _print_report(self, cr, uid, ids, data, context=None):
        if context is None:
            context = {}
        data = self.pre_print_report(cr, uid, ids, data, context=context)

        data['form'].update(self.read(cr, uid, ids, ['assistant_report', 'moves', 'unit','unit_type','initial_balance', 'account_ids', 'acc_balances', 'landscape'])[0])
        data['form'].update(self.read(cr, uid, ids, ['assistant_report'])[0])

        # ASSISTANT REPORT WITH FIXED TEMPALTE : DESIGED TO MEET DESIGN OF DONGLA
        if data['form']['assistant_report'] and  data['form']['unit']=='assist':
            return {'type': 'ir.actions.report.xml', 'report_name': 'account.assistant.report', 'datas': data}
        # BALANCE REPORT WITH FIXED TEMPALTE:: DESIGED TO MEET DESIGN OF DONGLA(LESS IN PERFORMANCE)
        if not data['form']['assistant_report'] and  data['form']['unit']=='balance':
            return {'type': 'ir.actions.report.xml', 'report_name': 'account.account.unit.balance.arabic', 'datas': data}
        # BALANCE REPORT WITH FIXED TEMPALTE:SHOW ACCOUNTS DEPENDS ON CHOOSEN FIELD IN ACCOUNT VIEW
        if not data['form']['assistant_report'] and  data['form']['unit']=='normal':
            return {'type': 'ir.actions.report.xml', 'report_name': 'account.account.balance.arabic', 'datas': data}
        # BALANCE REPORT WITH FIXED TEMPALTE:CAN RETURN FULL ACCOUTS WITHOUT CHOOSEN FILED IN NORMAL REPORT
        if not data['form']['assistant_report'] and  data['form']['unit']=='common':
            return {'type': 'ir.actions.report.xml', 'report_name': 'account.account.balance.all.arabic', 'datas': data}
        if  data['form']['unit']=='consol':
            return {'type': 'ir.actions.report.xml', 'report_name': 'account.account.balance.consol.arabic', 'datas': data}
        # DEFAULT 
        #return {'type': 'ir.actions.report.xml', 'report_name': 'account.account.balance.all.arabic', 'datas': data}


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
