# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################
import time
from report import report_sxw

class total_insurance_report(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(total_insurance_report, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            'line1':self._get_car,
            'line2':self._get_station,
            'line3':self._get_stock,
            'line4':self._get_sea,
            'line5':self._get_bank,
            'line6':self._get_accident,
        })
    def _get_car(self,data):
            date_company= data['form']['company_id']
            date_from= data['form']['Date_from']
            date_to= data['form']['Date_to']
            car = data['form']['car_insurance']
            res=[]
            result=[]
            dic = {}
            if car==True:
                self.cr.execute("""
                SELECT sum(s.total_cost) as total FROM car_operation s
            where s.company_id =%s and s.state='done' and s.operation_type = 'insurance' and (to_char(s.date,'YYYY-mm-dd')>=%s and to_char(s.date,'YYYY-mm-dd')<=%s)""",(date_company[0],date_from,date_to)) 
                result = self.cr.dictfetchall()
                if result :
                    for r in result :
                        dic = {'total':r['total']}
            else :
                dic = {'total':0.0}
            res.append(dic)
            return res
    def _get_station(self,data):
            date_company= data['form']['company_id']
            date_from= data['form']['Date_from']
            date_to= data['form']['Date_to']
            station = data['form']['station_insurance']
            res=[]
            result=[]
            dic = {}
            if station==True:
                self.cr.execute("""
                SELECT sum(b.cost) as total FROM building_insurance s
                       left join building_insurance_cost_line b on (b.line_id = s.id)
            where s.company_id =%s and s.state='gm' and (to_char(s.date,'YYYY-mm-dd')>=%s and to_char(s.date,'YYYY-mm-dd')<=%s)""",(date_company[0],date_from,date_to)) 
                result = self.cr.dictfetchall()
                if result :
                    for r in result :
                        dic = {'total':r['total']}
            else :
                dic = {'total':0.0}
            res.append(dic)
            return res
    def _get_stock(self,data):
            date_company= data['form']['company_id']
            date_from= data['form']['Date_from']
            date_to= data['form']['Date_to']
            stock = data['form']['stock_insurance']
            res=[]
            result=[]
            dic = {}
            if stock==True:
                self.cr.execute("""
                SELECT sum(s.total_insurance_cost) as total FROM stock_insurance s
            where s.company_id =%s and s.state='done' and (to_char(s.date,'YYYY-mm-dd')>=%s and to_char(s.date,'YYYY-mm-dd')<=%s)""",(date_company[0],date_from,date_to)) 
                result = self.cr.dictfetchall()
                if result :
                    for r in result :
                        dic = {'total':r['total']}
            else :
                dic = {'total':0.0}
            res.append(dic)
            return res

    def _get_sea(self,data):
            date_company= data['form']['company_id']
            date_from= data['form']['Date_from']
            date_to= data['form']['Date_to']
            sea = data['form']['sea_insurance']
            res=[]
            result=[]
            dic = {}
            if sea==True:
                self.cr.execute("""
                SELECT sum(s.total_insurance_cost) as total FROM sea_insurance s
            where s.company_id =%s and s.state='done' and (to_char(s.date,'YYYY-mm-dd')>=%s and to_char(s.date,'YYYY-mm-dd')<=%s)""",(date_company[0],date_from,date_to)) 
                result = self.cr.dictfetchall()
                if result :
                    for r in result :
                        dic = {'total':r['total']}
            else :
                dic = {'total':0.0}
            res.append(dic)
            return res

    def _get_bank(self,data):
            date_company= data['form']['company_id']
            date_from= data['form']['Date_from']
            date_to= data['form']['Date_to']
            bank = data['form']['bankers_insurance']
            res=[]
            result=[]
            dic = {}
            if bank==True:
                self.cr.execute("""
                SELECT sum(s.total_insurance_cost) as total FROM bankers_insurance s
            where s.company_id =%s and s.state='done' and (to_char(s.date,'YYYY-mm-dd')>=%s and to_char(s.date,'YYYY-mm-dd')<=%s)""",(date_company[0],date_from,date_to)) 
                result = self.cr.dictfetchall()
                if result :
                    for r in result :
                        dic = {'total':r['total']}
            else :
                dic = {'total':0.0}
            res.append(dic)
            return res

    def _get_accident(self,data):
            date_company= data['form']['company_id']
            date_from= data['form']['Date_from']
            date_to= data['form']['Date_to']
            accident = data['form']['accident_cost']
            res=[]
            result=[]
            dic = {}
            if accident==True:
                self.cr.execute("""
                SELECT sum(s.repayment_cost) as total FROM building_accident s
            where s.company_id =%s and s.state='done' and (to_char(s.date,'YYYY-mm-dd')>=%s and to_char(s.date,'YYYY-mm-dd')<=%s)""",(date_company[0],date_from,date_to)) 
                result = self.cr.dictfetchall()
                if result :
                    for r in result :
                        dic = {'total':r['total']}
            else :
                dic = {'total':0.0}
            res.append(dic)
            return res

report_sxw.report_sxw('report.total_insurance.report','bankers.insurance','addons/extra_insurance/report/total_insurance.rml',parser=total_insurance_report, header=False)
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
