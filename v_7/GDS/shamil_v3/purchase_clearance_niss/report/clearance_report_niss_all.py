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


class clearance_report_niss_all(report_sxw.rml_parse):
      def __init__(self, cr, uid, name, context):
        super(clearance_report_niss_all, self).__init__(cr, uid, name, context)
        self.localcontext.update({
            'time' : time,
            'function' : self.get_clearance_data,


        })
      


      def get_clearance_data(self,data):

           date1 = data['form']['from_date'] 
           date2 = data['form']['to_date'] 
           company_id = data['form']['company_id']
           department_id = data['form']['department_id']
           category_id = data['form']['category_id']
           ship_method = data['form']['ship_method']
           #transporter_id = data['form']['transporter_id']
           
           conditions = ""   
           res = {}  
           if company_id :
              conditions = conditions + " and cl.company_id=(%s)"%company_id[0] 
           if category_id :
              conditions = conditions + " and cat.id=(%s)"%category_id[0] 
           if department_id :
              conditions = conditions + " and cl.department_id=(%s)"%department_id[0] 
           #if transporter_id :
           #   conditions = conditions + " and cl.transporter_company_id=(%s)"%transporter_id[0]


           conditions = conditions + " and cl.ship_method='%s'"%ship_method
           self.cr.execute( """
                    select                        
                                    distinct cl.name as name,
                                    cl.bill_of_lading as bill_of_lading ,
                                    cl.date as date,
                                    cl.message_content as message_content,
                                    dept.name as department,
                                    cl.initial_bills_amount as initial_bills_amount,
                                    cl.final_invoice_amount as final_invoice_amount,
                                    cl.final_customs_amount as final_customs_amount,
                                    cl.initial_customs_amount as initial_customs_amount
                                    
                                    
                                    
                                    From purchase_clearance cl 
                                        left join transporter_companies trans on (trans.id=cl.transporter_company_id)
                                        left join res_company comp on (cl.company_id=comp.id)
                                        left join clearance_items_category cl_cat on (cl_cat.clearance_id=cl.id)
                                        left join items_category cat on (cat.id=cl_cat.category_id)
                                        left join hr_department dept on (cl.department_id=dept.id)
                                        
    
                                    
                                where (to_char(cl.date,'YYYY-mm-dd')>=%s and to_char(cl.date,'YYYY-mm-dd')<=%s) and cl.state not in ('cancel') 
                    """ + conditions + """ order by cl.name """  ,(date1,date2,)) 
           
           res['data'] = self.cr.dictfetchall()
           
           sum_initial_customs_amount = 0.0
           sum_final_customs_amount = 0.0
           for rec in res['data']:
               sum_initial_customs_amount += rec['initial_customs_amount']
               sum_final_customs_amount += rec['final_customs_amount']
           res['sum_initial'] = sum_initial_customs_amount
           res['sum_final'] = sum_final_customs_amount
           res['min_amount'] = sum_initial_customs_amount - sum_final_customs_amount
           return res




     






report_sxw.report_sxw('report.clearance_report_niss_all', 'purchase.clearance', 'addons/purchase_clearance_niss/report/clearance_report_niss_all.rml' ,parser=clearance_report_niss_all,header='internal landscape')
