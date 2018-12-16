# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

import time
from datetime import datetime
from openerp.report import report_sxw
import math


class assets_details(report_sxw.rml_parse):
    """
    assets details report
    """
    _name = 'report.account.assets.detials'

    def __init__(self, cr, uid, name, context=None):
        """
        initiation method
        """
        self.counter = 0
        super(assets_details, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'lines': self.lines,
            'category':self.get_name,
            'depreciation':self.get_depreciation,
        })
        self.context = context
    def get_name(self):
        """
        print category name
        """
        name = self.categories_names[self.counter]
        #cuse this method will be called after get_depreciation
        self.counter+=1
        return name
    
    def get_depreciation(self):
        """
        print category depreciation percent
        """
        percent = self.depreciation_percent[self.counter]
        return percent
    def to_date(self, date):
        """
        convert string to date 
        """
        return datetime.strptime(str(date), "%Y-%m-%d")

    def compute_assets(self, company_id, category_ids, date):
        """
        compute details of assets
        category_ids:list of categories ids
        """
        #wanted date
        wanted_date = datetime.strptime(str(date), "%Y-%m-%d")
        #wanted year
        year = wanted_date.year
        start_or_year = str(year)+"-1-1"
        start_date = datetime.strptime(str(start_or_year), "%Y-%m-%d")
        self.assets = {x:{} for x in category_ids}
        self.categories = {x:{} for x in category_ids}
        asset_obj = self.pool.get('account.asset.asset')
        search_ids = asset_obj.search(self.cr, self.uid, [('category_id','in',category_ids),\
                                                          ('company_id','=',company_id),\
                                                          ('purchase_date','>=',start_or_year),\
                                                          ('purchase_date','<=',date),\
                                                          ('state','!=','draft'),],context=self.context)
        for asset in asset_obj.browse(self.cr, self.uid, search_ids):
            self.categories[asset.category_id.id] = asset.category_id.name
            self.assets[asset.category_id.id][asset.name] = self.assets[asset.category_id.id].get(asset.name,{})
            self.assets[asset.category_id.id][asset.name]['name'] = asset.name
            self.assets[asset.category_id.id][asset.name]['date'] = asset.purchase_date
            #to get the current count if exist or set to zero
            self.assets[asset.category_id.id][asset.name]['count'] = self.assets[asset.category_id.id][asset.name].get('count',0)
            self.assets[asset.category_id.id][asset.name]['count'] += 1
            
            #get the current value of the asset
            value = sum(x.amount for x in asset.history_ids\
             if (x.type in ['initial']\
                and self.to_date(x.date) >= start_date\
                and self.to_date(x.date) <= wanted_date))
            
            self.assets[asset.category_id.id][asset.name]['value'] = value
            #to get the current count if exist or set to zero
            self.assets[asset.category_id.id][asset.name]['sum_value'] = self.assets[asset.category_id.id][asset.name].get('sum_value',0.0)
            
            self.assets[asset.category_id.id][asset.name]['sum_value'] += value

            #get the current depreciation of the asset
            depreciation = sum(x.amount for x in asset.depreciation_line_ids\
             if x.depreciation_date and\
                (self.to_date(x.depreciation_date) >= start_date\
                and self.to_date(x.depreciation_date) <= wanted_date))
            
            #to get the current count if exist or set to zero
            self.assets[asset.category_id.id][asset.name]['depreciation'] = self.assets[asset.category_id.id][asset.name].get('depreciation',0.0)
            self.assets[asset.category_id.id][asset.name]['depreciation'] += math.fabs(depreciation)

            current_sum = self.assets[asset.category_id.id][asset.name]['sum_value']
            current_depreciation = self.assets[asset.category_id.id][asset.name]['depreciation']
            self.assets[asset.category_id.id][asset.name]['rest_value'] = current_sum - current_depreciation
        
        self.assets_to_print = []
        #hold categories name to print operation
        
        
        self.categories_names = {}
        self.depreciation_percent = {}
        counter = 0
        for key in self.assets.keys():
            category_list = []
            name = self.categories[key]
            self.categories_names[counter] = name
            dic = self.assets[key]
            
            last_line = {'name':'اﻹجمالي', 'date':' ', 'count':' ',\
            'value':0,  'sum_value':0, 'depreciation':0, 'rest_value':0}
            for record in dic:
                last_line['value'] += self.assets[key][record]['value']
                last_line['sum_value'] += self.assets[key][record]['sum_value']
                last_line['depreciation'] += self.assets[key][record]['depreciation']
                last_line['rest_value'] += self.assets[key][record]['rest_value']
                category_list.append(self.assets[key][record])
            
            
            
            #to add the sumation line
            category_list.append(last_line)
            
            #to round the percent to 2 digits
            if last_line['depreciation'] and last_line['sum_value']:
                self.depreciation_percent[counter] = round(last_line['depreciation']/last_line['sum_value'], 2)
            
            self.assets_to_print.append(category_list)
            counter += 1


    def lines(self, data):
        """
        return report lines
        """
        company_id = data['form']['company_id']
        category_ids = data['form']['category_id']
        date = str(data['form']['date'])
        #get entered company_id or the defualt user company_id
        company_id = company_id and company_id[0] or\
         self.pool.get('res.company')._company_default_get(self.cr, self.uid, 'account.asset.asset', context=self.context)

        self.compute_assets(company_id, category_ids, date)

        return self.assets_to_print

report_sxw.report_sxw('report.account.assets.details.report',
                      'account.asset.asset',
                      'addons/account_asset_custom/report/account_asset_details.rml',
                      parser=assets_details,
                      header='internal landscape')
