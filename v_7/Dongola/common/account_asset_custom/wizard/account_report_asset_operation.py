# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

import time
from lxml import etree
from openerp.osv import fields, osv,orm
from openerp.tools.translate import _
class account_report_asset_list(osv.osv_memory):
    _name = "account.report.asset.operation"
    _description = "General Ledger Report"

    _columns = {
              
        'filter': fields.selection([('filter_no', 'No Filters'), ('filter_by_date', 'Filter By Date')], "Filter by", required=True),
        'company_id':fields.many2one('res.company','Company'),
        'date_from': fields.date( 'Start Date'),
        'date_to': fields.date( 'End Date'),
        'category_id': fields.many2many('account.asset.category', 'account_category_rel', 'asset_id', 'category_id', 'Asset Category', required=False),
        'asset_lists': fields.selection([
                                            ('list', 'Asset List'),
                                            ('initial', 'Initial Value'),
                                            ('revalue', 'Revalue Asset'),
                                            ('abandon', 'Abandon Asset'),
                                            ('sale', 'Asset Sale'),
                                            ('depreciation', 'Asset Depreciation Value'),
                                            ('details', 'Assets Detials'),
                                            ('end_of_year', 'End Of Year Sammary'),
                                            ], 'Asset Lists', required=True),
        'date': fields.date( 'Date'),
             }
    

    def _get_all_category(self, cr, uid, context=None):
        return self.pool.get('account.asset.category').search(cr, uid , [])
        
    _defaults = {
        'filter' :'filter_no',
                }    


    def check_report(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        data = {}
        data['ids'] = context.get('active_ids', [])
        data['model'] = context.get('active_model', 'ir.ui.menu')
        data['form'] = self.read(cr, uid, ids, ['company_id','category_id','filter','date_from', 'date_to','asset_lists', 'revalue_asset','depreciation_value','sale_value','addition_value','abandon_asset','filter_by_date','date'])[0]        
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
        return { 'type': 'ir.actions.report.xml', 'report_name': 'account.asset.operation', 'datas': data}
        
        
account_report_asset_list()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
