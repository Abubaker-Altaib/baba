# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

import time
import datetime
from report import report_sxw
from account_custom.common_report_header import common_report_header


class asset_list(report_sxw.rml_parse, common_report_header):
    _name = 'report.account.asset.list'
    
    globals()['sum_amount'] = 0.0
    globals()['sum_amount_before'] = 0.0
    globals()['sum_residual'] = 0.0
    globals()['sum_amont_after'] = 0.0
    
    
    def __init__(self, cr, uid, name, context=None):
        super(asset_list, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            'lines_record': self.lines_record,
            'lines': self.lines,
            'sum_amount': self.sum_amount,
            'sum_residual': self.sum_residual,
            'sum_amount_before': self.sum_amount_before,
            'sum_amont_after': self.sum_amont_after,
            
        })
        self.context = context



    def sum_amount(self,data):
        return globals()['sum_amount']

    def sum_amount_before(self,data):
        return globals()['sum_amount_before']

    def sum_residual(self,data):
        return globals()['sum_residual']

    def sum_amont_after(self,data):
        return globals()['sum_amont_after']

    def lines_record(self,data):       
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
        
        if company_id:
            domain+=[('company_id','=',company_id[1])]           
        if category_id:
            domain+=[('category_id','in',category_id)]            
        if filters:
            if date_from:
                domain+=[('purchase_date','>=',date_from)]
            if date_to:
                domain+=[('purchase_date','<=',date_to)]                                     
        
        asset = asset_obj.search(self.cr, self.uid, domain)
        #asset_ids = asset_history_obj.search(self.cr, self.uid, domain_type)
        val = []
        operation = {}
        for asset in asset_obj.browse(self.cr, self.uid, asset):
            hist = []  
            history = []
            globals()['sum_amount'] = 0.0
            proft = 0.0
            los = 0.0
            his=[]
            for asse in asset.history_ids:
                hist.append((asse.id))
            domain_type=[('state','in',['posted']),('id', 'in', hist)]
            asset_ids = asset_history_obj.search(self.cr, self.uid, domain_type)
            
            for asse in asset_history_obj.browse(self.cr, self.uid, asset_ids):
                his.append((asse))
            his.sort(key=lambda x: datetime.datetime.strptime(x.date, '%Y-%m-%d'))

            for asse in his: 
                    if asse.type == 'initial':#dr
                        globals()['sum_amount'] = asse.amount
                        history.append({
                            'dr':asse.amount,
                            'cr':0.0,
                            'balance':globals()['sum_amount'],
                            'hist_date':asse.date,
                            'statement':asse.type,})
                    if asse.type == 'rehabilitation':#dr 
                            globals()['sum_amount'] += asse.amount
                            history.append({
                                'dr':asse.amount,
                                'cr':0.0,
                                'balance':globals()['sum_amount'],
                                'hist_date':asse.date,
                                'statement':asse.type,})
                            
                    if asse.type == 'reval':#dr/cr
                                if asse.amount > globals()['sum_amount']:
                                    globals()['sum_amount'] = asse.amount
                                    history.append({
                                        'dr':asse.amount,
                                        'cr':0.0,
                                        'balance':globals()['sum_amount'],
                                        'hist_date':asse.date,
                                        'statement':asse.type,})
                                else:
                                    globals()['sum_amount'] = asse.amount
                                    history.append({
                                        'dr':0.0,
                                        'cr':asse.amount,
                                'balance':globals()['sum_amount'],
                                'hist_date':asse.date,
                                'statement':asse.type,})

                    if asse.type == 'abandon':#cr 
                            globals()['sum_amount'] -= asse.amount
                            history.append({
                                'dr':0.0,
                                'cr':asse.amount ,
                                'balance':globals()['sum_amount'],
                                'hist_date':asse.date,
                                'statement':asse.type,})  

                    if asse.type == 'sale':#dr/cr
                            history.append({
                                    'dr':0.0,
                                    'cr':asse.amount,
                                    'balance':0.0,
                                    'hist_date':asse.date,
                                    'statement':asse.type,})
                            if asse.amount >= globals()['sum_amount']:
                                proft = asse.amount - globals()['sum_amount'] 
                            else:
                                los =  globals()['sum_amount'] - asse.amount 
                                
            if asset.depreciation_line_ids:        
                for asse in asset.depreciation_line_ids:
                    if asse.move_check :#cr 
                        globals()['sum_amount'] -= asse.amount
                        history.append({
                            'dr':0.0,
                            'cr':asse.amount ,
                            'balance':globals()['sum_amount'],
                            'hist_date':asse.depreciation_date,
                            'statement':u'إهلاك ' + asse.name,})
                    

            operation ={'type':asset.category_id.name,
                        'model':asset.name,
                        'specif':asset.code,
                        'purchase_date':asset.purchase_date,
                        'country':asset.location_id.name,
                        'purchase_value':asset.purchase_value,
                        'other':asset.note,
                        'depr_amount': " % " +str(asset.category_id.depreciation_rate*100)  ,
                        'operation':history,
                        'proft': proft,
                        'los': los,
                        }    
            val.append((operation))
        
        return val


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
        globals()['sum_amont_after'] = 0.0
               
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
            depr_rate = 0
            asse = asset.asset_id
            if asset.asset_id.depreciation_rate:
                depr_rate = 1/asset.asset_id.depreciation_rate
            rehabilitation = 0.0
            #amount_before =asset.amount #asse.purchase_value - asset.amount
            #if asset.type == 'rehabilitation':
            amount_before = asset.asset_value
            asset_amount = asset.amount
            for rehabil in asse.depreciation_line_ids:
                rehabilitation = rehabil.amount
            val.append({'note':asse.note,
                        'amont_after':amount_before + asset_amount,
                        'value_residual': asse.value_residual,
                        'history_date':int(depr_rate),
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
            globals()['sum_amont_after'] += sums['amont_after'] or 0
        return val

report_sxw.report_sxw('report.account.asset.operation.ntc', 'account.asset.category', 'addons/asset_ntc_custom/report/account_asset_operation_ntc.rml', parser=asset_list, header=False)  

report_sxw.report_sxw('report.account.asset.operation.ntc2', 'account.asset.category', 'addons/account_asset_wafi/report/account_asset_operation2.rml', parser=asset_list, header=False)


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: