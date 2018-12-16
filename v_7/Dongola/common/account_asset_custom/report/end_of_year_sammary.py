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


class assets_end_of_year(report_sxw.rml_parse):
    """
    assets end of year sammary report
    """
    _name = 'report.account.assets.end_of_year'

    def __init__(self, cr, uid, name, context=None):
        """
        initiation method
        """
        self.counter = 0
        super(assets_end_of_year, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'lines': self.lines,
            'category':self.get_name,
            'depreciation':self.get_depreciation,
            'year':self.get_year,
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
        depreciation_compound_first = 0.0
        year = wanted_date.year
        start_or_year = str(year)+"-1-1"
        start_date = datetime.strptime(str(start_or_year), "%Y-%m-%d")
        asset_obj = self.pool.get('account.asset.asset')
        cat_obj = self.pool.get('account.asset.category')
        search_caat = []
        self.assets_to_print = []
        self.assets = {}
        domain = []
        
        if category_ids:
            domain+=[('id','in',category_ids)]
        search_caat = cat_obj.search(self.cr, self.uid, domain,context=self.context)
            
        for cat in cat_obj.browse(self.cr, self.uid, search_caat):
            abandon_rate = 0.0
            line_to_print = {'name':'',\
                 'value_at_start':0.0,\
                 'value_during_year':0.0,\
                 'cut_during_year':0.0,\
                 'value_end_year':0.0,\
                 'depreciation_at_start':0.0,\
                 'depreciation_during_year':0.0,\
                 'depreciation_compound_second':0.0,\
                 'cut_depreciation_sum_year_last':0.0}
            self.assets.update({x:line_to_print for x in [cat.id]})
            search_ids = asset_obj.search(self.cr, self.uid, [('category_id','=',cat.id),\
                                                  ('company_id','=',company_id),\
                                                  ('purchase_date','<=',date),\
                                                  ('state','!=','draft'),],context=self.context)
            #print search_ids,"search_idssearch_idssearch_idssearch_idssearch_idssearch_ids"
            for asset in asset_obj.browse(self.cr, self.uid, search_ids):
                self.assets[cat.id]['name'] = asset.category_id.name


                #get the asset in the start of the year 
                value_at_start = sum(x.amount for x in asset.history_ids\
                 if x.type == 'initial'\
                    and self.to_date(x.date) <= start_date)
                
                self.assets[cat.id]['value_at_start'] += value_at_start

                #get the asset during the year إضافات خلال العام
                value_during_year = sum(x.amount for x in asset.history_ids\
                 if x.type in ['reval','rehabilitation']\
                    and self.to_date(x.date) > start_date\
                    and self.to_date(x.date) <= wanted_date)

                self.assets[asset.category_id.id]['value_during_year'] += value_during_year

                #get the cuted value from asset during the year الإستبعاد
                cut_during_year = sum(x.amount for x in asset.history_ids\
                 if x.type in ['abandon','sale']\
                    and self.to_date(x.date) > start_date\
                    and self.to_date(x.date) <= wanted_date)

                self.assets[cat.id]['cut_during_year'] += cut_during_year


                self.assets[cat.id]['value_end_year'] += (value_at_start + value_during_year - cut_during_year)


                #get the depreciation at the start of the year for the asset السنة الفاتت الإضافية
                depreciation_at_start = sum(x.amount for x in asset.depreciation_line_ids\
                 if x.depreciation_date and\
                    (self.to_date(x.depreciation_date) <= start_date))
                
                self.assets[cat.id]['depreciation_at_start'] += math.fabs(depreciation_at_start)


                #get the depreciation during the year for the asset السنة الحالية إهلاكات العام
                depreciation_during_year = sum(x.amount for x in asset.depreciation_line_ids\
                 if x.depreciation_date and\
                    (self.to_date(x.depreciation_date) > start_date\
                    and self.to_date(x.depreciation_date) <= wanted_date))
                
                self.assets[asset.category_id.id]['depreciation_during_year'] += math.fabs(depreciation_during_year)

                #get the depreciation_compound for the asset السنة الحالية مجمع الإهلاك
                depreciation_compound = sum(x.depreciated_value for x in asset.depreciation_line_ids\
                 if x.depreciation_date and\
                    (self.to_date(x.depreciation_date) <= start_date))
                    
                depreciation_compound_first += math.fabs(depreciation_compound)
                
                #get the cut_depreciation_sum_year for the asset 
                cut_depreciation_sum_year = sum(x.amount for x in asset.history_ids\
                 if x.type in ['abandon']\
                    and (self.to_date(x.date) <= start_date))

                cut_depreciation_sum_year += math.fabs(cut_depreciation_sum_year)
                
                if self.assets[cat.id]['value_at_start']:
                
                    abandon_rate = (cut_depreciation_sum_year / self.assets[cat.id]['value_at_start'])*100
                
                self.assets[cat.id]['cut_depreciation_sum_year_last'] = round(depreciation_compound_first * abandon_rate,2)
                
                self.assets[cat.id]['depreciation_compound_second'] = round(depreciation_compound_first - self.assets[cat.id]['cut_depreciation_sum_year_last'],2)
            
            
            #get duration
            if self.assets[cat.id]['value_at_start']:
                self.assets[cat.id]['duration'] = round(self.assets[cat.id]['depreciation_compound_second'] / self.assets[cat.id]['value_at_start'] *100,2)
           
           
            #get depreciation_compound_last
            self.assets[cat.id]['depreciation_compound_last'] = round(self.assets[cat.id]['depreciation_during_year']+self.assets[cat.id]['depreciation_at_start']+self.assets[cat.id]['depreciation_compound_second'] - self.assets[cat.id]['cut_depreciation_sum_year_last'],2)
            #lines of the report
            
            #get book_value
            self.assets[cat.id]['book_value'] = round(self.assets[cat.id]['value_end_year'] - self.assets[cat.id]['depreciation_compound_last'],2)
            
        for key in self.assets.keys():
            self.assets_to_print.append(self.assets[key])
        #print self.assets_to_print,"self.assets_to_printself.assets_to_printself.assets_to_printself.assets_to_print"
            


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

    def get_year(self, data):
        date = data['form']['date']
        datesss = datetime.strptime(str(date), "%Y-%m-%d")
        return datesss.year
        
        
report_sxw.report_sxw('report.account.assets.end_of_year.report',
                      'account.asset.asset',
                      'addons/account_asset_custom/report/end_of_year_sammary.rml',
                      parser=assets_end_of_year,
                      header='internal landscape')
