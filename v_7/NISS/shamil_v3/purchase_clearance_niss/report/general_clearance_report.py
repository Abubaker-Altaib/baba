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


class general_clearance_report(report_sxw.rml_parse):
      def __init__(self, cr, uid, name, context):
        super(general_clearance_report, self).__init__(cr, uid, name, context)
        self.localcontext.update({
            'time' : time,
            'function' : self.get_clearance_data,


        })
      


      def get_clearance_data(self,data):
           state = []
           date1 = data['form']['from_date'] 
           date2 = data['form']['to_date'] 
           company_id = data['form']['company_id']
           department_id = data['form']['department_id']
           ship_method = data['form']['ship_method']

           if data['form']['draft_state']:
              state.append('draft')
           if data['form']['recieve_document_state']:
              state.append('recieve_document')
           if data['form']['exemption_state']:
              state.append('exemption')
           if data['form']['confirmed_state']:
              state.append('confirmed')
           if data['form']['approved_state']:
              state.append('approved')
           if data['form']['done_state']:
              state.append('done')




           res_data = {}
           conditions = ""
           if state :
              if len(state) == 1:
                 conditions = conditions + " and cl.state = '%s'"%state[0]
              else :
                 states = tuple(state) 
                 conditions = conditions + " and cl.state in %s"%str(states)


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
                                    cl.packing_type_count as packing_count,
                                    cl.message_content as message_content,
                                    cl.state as state,
                                    cl.ship_method as ship_method ,
                                    dept.name as department

                                    
                                    From purchase_clearance cl 

                                        left join res_company comp on (cl.company_id=comp.id)
                                        left join hr_department dept on (cl.department_id=dept.id)
                                        
    
                                    
                                where (to_char(cl.date,'YYYY-mm-dd')>=%s and to_char(cl.date,'YYYY-mm-dd')<=%s)  and cl.state not in ('cancel')
                    """ + conditions + """ order by cl.date,cl.state desc """  ,(date1,date2,))




           res_data = self.cr.dictfetchall()

           return res_data




     






report_sxw.report_sxw('report.general_clearance_report', 'purchase.clearance', 'addons/purchase_clearance_niss/report/general_clearance_report.rml' ,parser=general_clearance_report,header=False)
