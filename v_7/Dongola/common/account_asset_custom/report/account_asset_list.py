# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

import time
from datetime import datetime
from report import report_sxw
import pooler
from openerp.tools.translate import _
from account_custom.common_report_header import common_report_header


class asset_list(report_sxw.rml_parse, common_report_header):
    _name = 'report.account.asset.list'

    def set_context(self, objects, data, ids, report_type=None):
        self.company_id = data['form']['company_id']   
        self.category_id = data['form']['category_id']           
        self.date_from = data['form']['date_from']        
        self.date_to = data['form']['date_to']  
        self.filter = data['form']['filter']
        self.type = data['form']['asset_lists']
        self.sum_purchase = 0
        self.sum_residual = 0
        self.where_clause = " "

        if self.company_id:
           company_ids =  self.pool.get('account.account')._get_children_and_consol(self.cr, self.uid, self.company_id[0])
           self.where_clause += " and a.company_id in (%s) "  % ','.join(map(str, company_ids)) 
        if self.category_id:
           if isinstance(ids, (int, long)): self.category_id = [self.category_id]
           self.where_clause += " and a.category_id in (%s) "  % ','.join(map(str, self.category_id)) 
        if self.filter == 'filter_by_date':
            if self.date_from:
               self.where_clause += " and a.purchase_date >= '" + self.date_from + "'"
            if self.date_to:
               self.where_clause += " and a.purchase_date <= '" + self.date_to + "'"
        return super(asset_list, self).set_context(objects, data, ids, report_type=report_type)
    
    def __init__(self, cr, uid, name, context=None):
        if context is None:
            context = {}
        super(asset_list, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            'lines': self.lines,            
            'lines_depre': self.lines_depre,  
            'asset_list': self.asset_list,  
            'sum_purchase': self._sum_purchase,            
            'sum_residual': self._sum_residual,              
            })
        self.context = context
   
    def lines_depre(self):
        dic={}
        self.cr.execute("select max(depreciation_date) as last_depr_date,a.name as name,a.purchase_date as purchase_date,\
                        a.purchase_value as purchase_value,cat.name as cat_name,a.value_residual as value_residual, \
                       (a.purchase_value - a.value_residual) as depr_amount,a.code as code ,\
                        CASE WHEN a.method_time='end' THEN\
                             cast(to_char(a.method_end,'YYYY') as int)-cast(to_char(a.purchase_date,'YYYY') as int) \
                        ELSE (a.method_period*a.method_number/12) END AS age \
                        from account_asset_depreciation_line depr\
                        LEFT JOIN account_asset_asset a on (a.id= depr.asset_id) \
                        LEFT JOIN account_asset_category cat on (cat.id= a.category_id) \
                       WHERE a.state='open' and move_check=True "+self.where_clause+" \
                       GROUP BY a.name,a.code,a.purchase_date,a.purchase_value,a.value_residual,a.purchase_value,\
                                    cat.name,a.method_time,a.method_end,a.method_period,a.method_number\
                           ")
        res = self.cr.dictfetchall()
        for r in res:
            self.sum_purchase += r['purchase_value'] or 0
            self.sum_residual += r['value_residual'] or 0
        return res

    def _sum_purchase(self):
        return self.sum_purchase

    def _sum_residual(self):
        return self.sum_residual

    def lines(self):
        if self.type == 'revalue':
            self.where_clause += " and h.type ='reval'"
        elif self.type == 'sale':
            self.where_clause += " and h.type ='sale'"
        elif self.type == 'abandon':
            self.where_clause += " and h.type ='abandon'"
        elif self.type == 'initial':
            self.where_clause += " and h.type ='initial'"


        self.cr.execute("SELECT  a.name, a.code, h.date as history_date, a.purchase_date,  min(cat.name) as cat_name,\
                        a.purchase_value,SUM(COALESCE(h.amount,0)) as amount,  SUM(COALESCE(current_value,0)) as current_value\
                        from account_asset_history h \
                        LEFT JOIN account_asset_asset a on (h.asset_id=a.id)\
                        LEFT JOIN account_asset_category cat on (cat.id= a.category_id) \
                        where  h.state= 'posted' " +self.where_clause+ "\
                        group by   a.name, a.code, a.purchase_value, a.value_residual,h.date, a.purchase_date ") 
        res = self.cr.dictfetchall()
        for r in res:
            self.sum_residual += r['current_value'] or 0
        return res

    def asset_list(self):
        dic={}
        self.cr.execute("select   a.name, a.code, a.purchase_date ,a.purchase_value ,\
                        cat.name as cat_name,a.value_residual, state \
                        from account_asset_asset a\
                        LEFT JOIN account_asset_category cat on (cat.id= a.category_id) \
                       WHERE a.state is not null "+ self.where_clause)
        res = self.cr.dictfetchall()
        for r in res:
            self.sum_purchase += r['purchase_value'] or 0
            self.sum_residual += r['value_residual'] or 0
        return res


report_sxw.report_sxw('report.account.asset.operation', 'account.asset.category', 'addons/account_asset_custom/report/account_asset_operation.rml', parser=asset_list, header=False)

report_sxw.report_sxw('report.account.asset.Depr', 'account.asset.category', 'addons/account_asset_custom/report/account_asset_depre.rml', parser=asset_list, header=False)
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: