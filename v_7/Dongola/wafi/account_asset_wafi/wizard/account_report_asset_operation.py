# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

from openerp.osv import fields, osv,orm
from openerp.tools.translate import _

class account_report_asset_list(osv.osv_memory):

    _inherit = "account.report.asset.operation"

    _columns = {
        'asset_lists': fields.selection([('list', 'Asset List'),
                                        ('initial', 'Initial Value'),
                                        ('revalue', 'Revalue Asset'),
                                        ('abandon', 'Abandon Asset'),
                                        ('sale', 'Asset Sale'),
                                        ('depreciation', 'Asset Depreciation Value'),
                                        ('before_revalue', 'Before Revaluation'),
                                        ('after_revalue', 'After Revaluation'),
                                        ('before_rehab', 'Before Rehabilitation'),
                                        ('after_rehab', 'After Rehabilitation'),
                                        ('details', 'Assets Detials'),
                                        ('end_of_year', 'End Of Year Sammary'),
                                        ], 'Asset Lists', required=True),
    }

    def _get_all_category(self, cr, uid, context=None):
        return self.pool.get('account.asset.category').search(cr, uid , [], context=context)

    _defaults = {
        'filter' :'filter_no',
    }

    def check_report(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        data = {'ids': context.get('active_ids', []),
                'model': context.get('active_model', 'ir.ui.menu'),
                'form': self.read(cr, uid, ids, [])[0]}
        if data['form']['asset_lists'] == 'details':
            return {'type': 'ir.actions.report.xml',\
                    'report_name': 'account.assets.details.report',\
                    'datas': data}
        if data['form']['asset_lists'] == 'end_of_year':
            return {'type': 'ir.actions.report.xml',\
                    'report_name': 'account.assets.end_of_year.report',\
                    'datas': data}
        if data['form']['asset_lists'] == 'depreciation':
            return { 'type': 'ir.actions.report.xml', 'report_name': 'account.asset.Depr', 'datas': data}
        if data['form']['asset_lists'] == 'revalue' or data['form']['asset_lists'] == 'initial' or data['form']['asset_lists'] == 'abandon' or data['form']['asset_lists'] == 'sale' or data['form']['asset_lists'] == 'list':
             return { 'type': 'ir.actions.report.xml', 'report_name': 'account.asset.operation', 'datas': data}        
        return {'type': 'ir.actions.report.xml', 'report_name': 'account.asset.operation2', 'datas': data}


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
