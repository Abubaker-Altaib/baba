# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

import time
from report import report_sxw
from datetime import datetime


class clearance_finance_report(report_sxw.rml_parse):
      def __init__(self, cr, uid, name, context):
        super(clearance_finance_report, self).__init__(cr, uid, name, context)
        self.localcontext.update({
            'time' : time,
            'function' : self.get_clearance_data,


        })
      


      def get_clearance_data(self,data):

           date1 = data['form']['from_date'] 
           date2 = data['form']['to_date'] 
           company_id = data['form']['company_id']
           department_id = data['form']['department_id']
           ship_method = data['form']['ship_method']

           res_data = {}
           conditions = ""     
           if company_id :
              conditions = conditions + " and cl.company_id=(%s)"%company_id[0] 
           
           if department_id :
              conditions = conditions + " and cl.department_id=(%s)"%department_id[0] 
           if ship_method :
              conditions = conditions + " and cl.ship_method='%s'"%ship_method
           self.cr.execute( """
                    select                        
                                    distinct cl.name as name,
                                    cl.bill_of_lading as bill_of_lading ,
                                    cl.date as date,
                                    cl.message_content as message_content,
                                    cl.bills_amoun_total as bills_amoun_total,
                                    cl.ship_method as ship_method ,
                                    dept.name as department,
                                    part.name as partner_name
                                    
                                    From purchase_clearance cl 

                                        left join res_company comp on (cl.company_id=comp.id)
                                        left join res_partner part on (cl.partner_id=part.id)
                                        left join hr_department dept on (cl.department_id=dept.id)
                                        
    
                                    
                                where (to_char(cl.date,'YYYY-mm-dd')>=%s and to_char(cl.date,'YYYY-mm-dd')<=%s) and cl.state not in ('cancel') 
                    """ + conditions + """ order by cl.ship_method """  ,(date1,date2,))



           res_data['data'] = self.cr.dictfetchall()
           self.cr.execute( """
                    select                        
                                    distinct cl.ship_method as ship_method ,
                                    sum(cl.bills_amoun_total) as bills_amoun_total,
                                    part.name as partner_name
                                    

                                    From purchase_clearance cl 

                                        left join res_company comp on (cl.company_id=comp.id)
                                        left join res_partner part on (cl.partner_id=part.id)
                                        left join hr_department dept on (cl.department_id=dept.id)
                                        
    
                                    
                                where (to_char(cl.date,'YYYY-mm-dd')>=%s and to_char(cl.date,'YYYY-mm-dd')<=%s) and cl.state not in ('cancel') 
                    """ + conditions + """group by cl.ship_method,part.name order by cl.ship_method desc """  ,(date1,date2,))
               
           res_data['data_as_total'] = self.cr.dictfetchall()
           return res_data




     






report_sxw.report_sxw('report.clearance_finance_report', 'purchase.clearance', 'addons/purchase_clearance_niss/report/clearance_finance_report.rml' ,parser=clearance_finance_report,header=False)
