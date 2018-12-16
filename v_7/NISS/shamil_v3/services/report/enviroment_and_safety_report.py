#coding: utf-8 
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

import time
from report import report_sxw

# Report to print information of environment and safety contractors for a specific period of time
#----------------------------------------
# Class Enviroment and safety  report
#----------------------------------------
class enviroment_safety_report(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(enviroment_safety_report, self).__init__(cr, uid, name, context)
        self.localcontext.update({
            'time': time,
            'line':self._getdata,
            #'line2':self._getdata2,
        })

    """def _getdata2(self,data):
        date_from= data['form']['Date_from']
        date_to= str(data['form']['Date_to'])
        data_partner = data['form']['partner_id'] 
        #date of rent in the period of wizard
        where_string = "((to_char(e.date_of_rent,'YYYY-mm-dd')>=%s and to_char(e.date_of_rent,'YYYY-mm-dd')<=%s)"
        #date of return in the period of wizard
        where_string += " or (to_char(e.date_of_return,'YYYY-mm-dd')>=%s and to_char(e.date_of_return,'YYYY-mm-dd')<=%s)"
        #period of contract bigger than period of wizard
        where_string += " or (to_char(e.date_of_rent,'YYYY-mm-dd')<=%s and to_char(e.date_of_return,'YYYY-mm-dd')>=%s))"
        if data_partner:
            partner_id = data_partner[0]
            where_string += " and r.id =%s"%partner_id
        self.cr.execute(
                SELECT distinct
                    r.id as id ,
                    r.name as partner_name
                FROM 
                    environment_and_safety e
                    LEFT JOIN res_partner r on (e.partner_id = r.id )
                where
                     + where_string,(date_from,date_to,date_from,date_to,date_from,date_to))
        res = self.cr.dictfetchall()
        for r in res:
            r['where_string'] = where_string
        return res"""

    def _getdata(self,data):
        date_from= data['form']['Date_from']
        date_to= data['form']['Date_to']
        partner_id= data['form']['partner_id']
        where_condition = ""
        where_condition += partner_id and " and e.partner_id=%s"%partner_id[0] or ""
        self.cr.execute("""
                SELECT
                e.name as cotract_no,
                e.date_of_rent as rent_date , 
                e.date_of_return as return_date , 
                e.cost_of_contract as contract_cost ,
		r.name as partner_name ,  
                e.fees_total_amount as amount_total
                FROM 
                    environment_and_safety e 
                    LEFT JOIN res_partner r on (e.partner_id = r.id )
                where (to_char(e.date_of_rent,'YYYY-mm-dd')>=%s and to_char(e.date_of_return,'YYYY-mm-dd')<=%s)
                     """+ where_condition,(date_from,date_to)) 
        res = self.cr.dictfetchall()
        return res

report_sxw.report_sxw('report.enviroment_safety.report', 'environment.and.safety', 'addons/services/report/enviroment_and_safety_report.rml' ,parser=enviroment_safety_report , header=False)
