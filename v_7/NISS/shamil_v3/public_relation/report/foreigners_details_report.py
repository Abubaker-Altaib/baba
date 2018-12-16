#coding: utf-8 
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

import time
from report import report_sxw


class foreigners_details_report(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(foreigners_details_report, self).__init__(cr, uid, name, context)
        self.localcontext.update({
            'time': time,
            'line':self._getdata,
            'line2':self._getdata2,


        })

    def _getdata2(self,data):


        date_from= data['form']['Date_from']
        date_to= data['form']['Date_to']
        data_company = data['form']['company_id']	

	if data_company !=0:

           self.cr.execute("""
                SELECT 
                                  distinct r.id as id ,
				  r.name as company 

  
                FROM public_relation_foreigners p 

		left join res_partner r on (p.company = r.id)

                where r.id =%s """%(data['form']['company_id'][0]))
	else  :

           self.cr.execute("""
                SELECT 
                                  distinct r.id as id ,
				  r.name as company 

  
                FROM public_relation_foreigners p 

		left join res_partner r on (p.company = r.id)

                where (to_char(p.date_of_entry,'YYYY-mm-dd')>=%s and to_char(p.date_of_entry,'YYYY-mm-dd')<=%s)""",(date_from,date_to))

 
        res = self.cr.dictfetchall()
        return res

    def _getdata(self,data,num):

           date_from= data['form']['Date_from']
           date_to= data['form']['Date_to']
           data_company = num
           self.cr.execute("""
                 SELECT  
			p.name as name , 
    			p.foreigner_name as foreigner_name , 
    			p.date_of_entry as date_of_entry , 
    			p.type_of_stay as type_of_stay , 
     			p.passport_number as passport_number ,
    			p.profession as profession , 
    			p.date_of_first_residence as date_of_first_residence , 
    			p.date_of_end_of_stay as date_of_end_of_stay , 
    			p.place_of_residence as place_of_residence,
			t.name as type_of_stay, 	
			n.name as nationality 

                FROM public_relation_foreigners p 
		left join res_country n on (p.nationality_id=n.id)
		left join type_of_stay t on (p.type_of_stay = t.id)

                where p.company =%s"""%data_company) 
           res = self.cr.dictfetchall()
           return res




report_sxw.report_sxw('report.foreigner_details.report', 'public.relation.foreigners', 'addons/public_relation/report/foreigners_details_report.rml' ,parser=foreigners_details_report , header=False)
