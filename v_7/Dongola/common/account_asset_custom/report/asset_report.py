#coding: utf-8 
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2016-2017 NCTR (<http://www.nctr.sd>).
#
##############################################################################

from report import report_sxw
from datetime import datetime
import math

class asset_report(report_sxw.rml_parse):
    """ To manage assets report """

    def __init__(self, cr, uid, name, context):
        self.total = {'1':0.0,'2':0.0,'3':0.0,'4':0.0,'5':0.0,'6':0.0,'7':0.0,'8':0.0}
        super(asset_report, self).__init__(cr, uid, name, context)
        self.cr = cr
        self.uid = uid
        self.name = name
        self.context = context
        self.localcontext.update({
            'lines':self._getdata,
            'sub':self._getsum,
        })
    
    def _getdata(self,data):
        account_asset_asset            = self.pool.get("account.asset.asset")
        account_asset_history          = self.pool.get("account.asset.history")
        acount_asset_depreciation_line = self.pool.get("account.asset.depreciation.line")
        account_asset_category         = self.pool.get("account.asset.category")
        date_from= data['form']['date_from']
        date_to= data['form']['date_to']
        category_ids = data['form']['category_ids']
        company_id = data['form']['company_id']
        target_operation = data['form']['target_operation']
        date_from = datetime.strptime(date_from, "%Y-%m-%d")
        date_to = datetime.strptime(date_to, "%Y-%m-%d")
        lines=[]
        if not category_ids:
            return [{}]
        for category in account_asset_category.browse(self.cr,self.uid,category_ids,context=self.context):
            assets = account_asset_asset.search(self.cr,self.uid,[('category_id','=',category.id)],context=self.context)
            if not assets:
                continue
            depreciation_lines = acount_asset_depreciation_line.search(self.cr,self.uid,[('asset_id','in',assets),],context=self.context)
            if target_operation == "posted":
                depreciation_lines = acount_asset_depreciation_line.search(self.cr,self.uid,[('asset_id','in',assets),('move_check','=',True)],context=self.context)
            historyids = account_asset_history.search(self.cr,self.uid,[('asset_id','in',assets),],context=self.context)
            if target_operation == "posted":
                historyids = account_asset_history.search(self.cr,self.uid,[('asset_id','in',assets),('state','=','posted'),],context=self.context)

            initial_value = 0
            revalution_value = 0
            abandon_value = 0
            sale_value = 0
            rehabilitation_value = 0

            initial_asset_value = 0
            revalution_asset_value = 0
            abandon_asset_value = 0
            sale_asset_value = 0
            for history in account_asset_history.browse(self.cr,self.uid,historyids,context=self.context):
                if datetime.strptime(history.date, "%Y-%m-%d") >= date_from:
                    if history.type=='initial':
                        initial_value         +=history.amount
                        initial_asset_value   +=history.asset_value
                    elif history.type=='reval':
                        revalution_value      +=history.amount
                        revalution_asset_value+=history.asset_value
                    elif history.type=='abandon':
                        abandon_value         +=history.amount
                        abandon_asset_value   +=history.asset_value
                    elif history.type=='sale':
                        sale_value            +=history.amount
                        sale_asset_value      +=history.asset_value
                    elif history.type=='rehabilitation':
                            rehabilitation_value  +=history.amount
                    
            sum1 = initial_value + rehabilitation_value +(revalution_value - revalution_asset_value) - sale_asset_value - abandon_asset_value

            sum2 = 0
            sum3 = 0
            for item in assets:
                historyid  = account_asset_history.search(self.cr,self.uid,[('asset_id','=',int(item)),],context=self.context)
                if target_operation == "posted":
                    historyid = account_asset_history.search(self.cr,self.uid,[('asset_id','=',int(item)),('state','=','posted'),],context=self.context)
                initial_value = 0
                revalution_value = 0
                abandon_value = 0
                sale_value = 0
                rehabilitation_value = 0

                initial_asset_value = 0
                revalution_asset_value = 0
                abandon_asset_value = 0
                sale_asset_value = 0

                for history in account_asset_history.browse(self.cr,self.uid,historyid,context=self.context):
                    if datetime.strptime(history.date, "%Y-%m-%d") <= date_to and datetime.strptime(history.date, "%Y-%m-%d") >= date_from:
                        if history.type=='initial':
                            initial_value         +=history.amount
                            initial_asset_value   +=history.asset_value
                        elif history.type=='reval':
                            revalution_value      +=history.amount
                            revalution_asset_value+=history.asset_value
                        elif history.type=='abandon':
                            abandon_value         +=history.amount
                            abandon_asset_value   +=history.asset_value
                        elif history.type=='sale':
                            sale_value            +=history.amount
                            sale_asset_value      +=history.asset_value
                        elif history.type=='rehabilitation':
                            rehabilitation_value  +=history.amount
                sum2 += initial_value + rehabilitation_value
                sum3 += sale_asset_value + abandon_asset_value
                if revalution_asset_value - revalution_value > 0:
                    sum2 += revalution_asset_value - revalution_value
                    sum3 += revalution_asset_value - revalution_value


            sum4 = 0
            for dep in acount_asset_depreciation_line.browse(self.cr,self.uid,depreciation_lines,context=self.context):
                if datetime.strptime(dep.depreciation_date, "%Y-%m-%d") <= date_to and datetime.strptime(dep.depreciation_date, "%Y-%m-%d") >= date_from:
                    sum4 += math.fabs(dep.amount)

            sum5 = 0
            for dep in acount_asset_depreciation_line.browse(self.cr,self.uid,depreciation_lines,context=self.context):
                if datetime.strptime(dep.depreciation_date, "%Y-%m-%d") >= date_from:
                    sum5 += math.fabs(dep.amount)

            sum_dep_to = 0
            for dep in acount_asset_depreciation_line.browse(self.cr,self.uid,depreciation_lines,context=self.context):
                if datetime.strptime(dep.depreciation_date, "%Y-%m-%d") <= date_to:
                    sum_dep_to += math.fabs(dep.amount)

            collect1 = sum1 + sum2 + sum3
            collect2 = sum4 + sum_dep_to
            collect3 = collect1 - collect2
            self.total['1'] += sum1
            self.total['2'] += sum2
            self.total['3'] += sum3
            self.total['4'] += collect1
            self.total['5'] += sum4
            self.total['6'] += sum5
            self.total['7'] += collect2
            self.total['8'] += collect3
            lines.append({  'category':category.name,
                            'sum1':sum1,
                            'sum2':sum2,
                            'sum3':sum3,
                            'sum4':sum4,
                            'sum5':sum5,
                            'collect1':collect1,
                            'collect2':collect2,
                            'collect3':collect3,
                            })

        return lines

    def _getsum(self,st):
        return [{'count': self.total[str(st)]}]
           




report_sxw.report_sxw('report.asset.report', 'account.asset.history', 'addons/account_asset_custom/report/asset_report.rml' ,parser=asset_report,header='internal landscape')

