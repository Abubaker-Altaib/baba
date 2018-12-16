# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

import time
from report import report_sxw
from account_custom.common_report_header import common_report_header


class asset_list(report_sxw.rml_parse, common_report_header):
    _name = 'report.account.asset.list'
    
    globals()['sum_amount'] = 0.0
    globals()['sum_amount_before'] = 0.0
    globals()['sum_residual'] = 0.0
    
    def __init__(self, cr, uid, name, context=None):
        super(asset_list, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            'lines': self.lines,
            'sum_amount': self.sum_amount,
            'sum_residual': self.sum_residual,
            'sum_amount_before': self.sum_amount_before,
        })
        self.context = context

    def sum_amount(self,data):
        return globals()['sum_amount']

    def sum_amount_before(self,data):
        return globals()['sum_amount_before']

    def sum_residual(self,data):
        return globals()['sum_residual']

    def lines(self,data):       
        asset_history_obj = self.pool.get('account.asset.history')
        asset_obj = self.pool.get('account.asset.asset')
        company_id = data['form']['company_id']
        category_id = data['form']['category_id']
        date_from = data['form']['date_from']
        date_to = data['form']['date_to']
        filters = data['form']['filter']
        types = data['form']['asset_lists']
        domain=[]
        domain_type=[]
        globals()['sum_amount'] = 0.0
        globals()['sum_amount_before'] = 0.0
        globals()['sum_residual'] = 0.0
               
        if company_id:
            domain+=[('company_id','=',company_id[1])]           
        if category_id:
            domain+=[('category_id','in',category_id)]            
        if filters:
            if date_from:
                domain+=[('purchase_date','>=',date_from)]
            if date_to:
                domain+=[('purchase_date','<=',date_to)]                                     
        if types == 'after_revalue':
            domain_type+=[('type','=','reval')]
        if types == 'before_revalue':
            domain_type+=[('type','=','initial')]
        if types == 'before_rehab':
            domain_type+=[('type','=','reval')]
        if types == 'after_rehab':
            domain_type+=[('type','=','rehabilitation')]
                       
        asset = asset_obj.search(self.cr, self.uid, domain)
        domain_type+=[('state','in',['posted']),('asset_id','in',asset)]
        asset_ids = asset_history_obj.search(self.cr, self.uid, domain_type)
        val = []
        asset_amount = 0.0
        for asset in asset_history_obj.browse(self.cr, self.uid, asset_ids):
            asse = asset.asset_id
            rehabilitation = 0.0
            amount_before = asse.purchase_value - asset.amount
            asset_amount += asset.amount
            for rehabil in asse.depreciation_line_ids:
                rehabilitation = rehabil.amount
            val.append({'note':asse.note,
                        'value_residual':asse.value_residual,
                        'history_date':asset.date,
                        'purchase_date':asse.purchase_date,
                        'code':asse.code,
                        'name':asse.name,
                        'serial_no':asse.serial_no,
                        'amount_before':amount_before,
                        'rehab':asset.rehab_type,
                        'depr_amount':rehabilitation,
                        'amount':asset_amount,
                        })
        
        for sums in val:
            globals()['sum_amount'] += sums['amount'] or 0
            globals()['sum_residual'] += sums['value_residual'] or 0
            globals()['sum_amount_before'] += sums['amount_before'] or 0
        return val

report_sxw.report_sxw('report.account.asset.operation2', 'account.asset.category', 'addons/account_asset_wafi/report/account_asset_operation2.rml', parser=asset_list, header=False)


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
