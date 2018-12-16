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


class search_and_inform_report(report_sxw.rml_parse):
      def __init__(self, cr, uid, name, context):
        super(search_and_inform_report, self).__init__(cr, uid, name, context)
        self.localcontext.update({
            'time' : time,
            'function' : self.get_data,


        })
      


      def get_data(self,data):


           date1 = data['form']['from_date'] 
           date2 = data['form']['to_date'] 
           company_id = data['form']['company_id']
           department_id = data['form']['department_id']
           with_childern = data['form']['with_childern']
           report_type = data['form']['report_type']
           state = data['form']['state']
           executing_agency = data['form']['executing_agency']


           conditions = ""
           if company_id and report_type == 'purchase_order'  :
              conditions = conditions + " and po.company_id=(%s)"%company_id[0]+ " and po.executing_agency='%s'"%executing_agency
           else :
              conditions = conditions + " and ir.company_id=(%s)"%company_id[0] + " and ir.executing_agency='%s'"%executing_agency

 
           if department_id and report_type == 'purchase_order' :

              if with_childern:
                 department_ids = self.pool.get('hr.department').search(self.cr , self.uid , [('id' , 'child_of' , department_id[0] )])


                 if len(department_ids) == 1:
                    conditions = conditions + " and po.department_id=(%s)"%department_id[0]
                 else:
                     department_ids = tuple(department_ids)
                     conditions = conditions + " and po.department_id in %s"%str(department_ids)
              else :
                   conditions = conditions + " and po.department_id=(%s)"%department_id[0]

           if department_id and report_type != 'purchase_order' :
               if with_childern:
                  department_ids = self.pool.get('hr.department').search(self.cr , self.uid , [('id' , 'child_of' , department_id[0] )])

                  if len(department_ids) == 1:
                     conditions = conditions + " and ir.department_id=(%s)"%department_id[0]
                  else:
                     department_ids = tuple(department_ids)
                     conditions = conditions + " and ir.department_id in %s"%str(department_ids)

               else:
                     conditions = conditions + " and ir.department_id=(%s)"%department_id[0]


           if report_type == 'init_request' :
               # "Filter By State"
              if state == 'in_progress' :
                 conditions = conditions + " and ir.state in ('in_progress')"
              if state == 'completed' :
                 conditions = conditions + " and ir.state in ('completed')" 
              if  state == 'closed' :
                  conditions = conditions + " and ir.state in ('closed')"
              if not state  :
                 conditions = conditions + " and ir.state in ('draft','in_progress','completed','closed')"

              self.cr.execute( """
					select                        
				                                    ir.name as name ,
                                                                    ir.ir_date as order_date,
		                                                    dep.name as department,
                                                                    ir.purchase_type as purchase_type,
                                                                    ir.state as state

								    From ireq_m ir 
								    
		                                                    left join res_company comp on (ir.company_id=comp.id)
								    left join hr_department dep on (ir.department_id=dep.id)

								    
								where (to_char(ir.ir_date,'YYYY-mm-dd')>=%s and to_char(ir.ir_date,'YYYY-mm-dd')<=%s) """ + conditions + """order by ir.name"""  ,(date1,date2,))
	      

           elif report_type == 'quotes' :
             # "Filter By State"   
                if state == 'in_progress' :
                   conditions = conditions + " and ir.state in ('in_progress_quote')"
                if state == 'completed' :
                   conditions = conditions + " and ir.state in ('completed_quote')" 
                if state == 'closed' :
                    conditions = conditions + " and ir.state in ('closed_quote')"
                if not state :
                   conditions = conditions + " and ir.state in ('in_progress_quote','completed_quote','closed_quote')"
                self.cr.execute( """
					select                        
				                                    ir.name as name ,
                                                                    quote.q_no as q_no ,
                                                                    quote.state as state ,
                                                                    quote.amount_total as amount_total ,
                                                                    part.name as supplier ,
                                                                    ir.ir_date as order_date,
		                                                    dep.name as department,
                                                                    ir.purchase_type as purchase_type 


								    From ireq_m ir 
								    
		                                                    left join res_company comp on (ir.company_id=comp.id)
								    left join hr_department dep on (ir.department_id=dep.id)
                                                                    left join pur_quote quote on (quote.pq_ir_ref=ir.id)
							            left join res_currency curr on (quote.currency_id=curr.id)
								    left join res_partner part on (quote.supplier_id=part.id )                                                               
								where (to_char(ir.ir_date,'YYYY-mm-dd')>=%s and to_char(ir.ir_date,'YYYY-mm-dd')<=%s) """ + conditions + """order by (ir.name,quote.name) """  ,(date1,date2,))
	        

           elif report_type == 'fin_ratif_request' :
             # "Filter By State"
                if state == 'in_progress' :
                   conditions = conditions + " and ir.state in ('in_progress_fin_request')"
                if state == 'completed' :
                   conditions = conditions + " and ir.state in ('completed_fin_request')" 
                if  state == 'closed' :
                    conditions = conditions + " and ir.state in ('closed_fin_request','done')"
                if not state :
                   conditions = conditions + " and ir.state in ('in_progress_fin_request','completed_fin_request','closed_fin_request','done')"
                self.cr.execute( """
					select                        
				                                    ir.name as name ,
                                                                    quote.q_no as q_no ,
                                                                    ir.state as state ,
                                                                    quote.amount_total as amount_total ,
                                                                    part.name as supplier ,
                                                                    ir.ir_date as order_date,
		                                                    dep.name as department,
                                                                    ir.purchase_type as purchase_type 


								    From ireq_m ir 
								    
		                                                    left join res_company comp on (ir.company_id=comp.id)
								    left join hr_department dep on (ir.department_id=dep.id)
                                                                    left join pur_quote quote on (quote.pq_ir_ref=ir.id and quote.state in ('done') )
                                
							            left join res_currency curr on (quote.currency_id=curr.id)
								    left join res_partner part on (quote.supplier_id=part.id )        where (to_char(ir.ir_date,'YYYY-mm-dd')>=%s and to_char(ir.ir_date,'YYYY-mm-dd')<=%s) """ + conditions + """order by (ir.name,quote.name) """  ,(date1,date2,))
	        


         
           else :
             # "Filter By State"   
                if state == 'in_progress' :
                    conditions = conditions + " and po.state in ('draft','sign')"
                if state == 'completed' :
                    conditions = conditions + " and po.state in ('confirmed')" 
                if  state == 'closed' :
                    conditions = conditions + " and po.state in ('approved','done')"
                if not state :
                   conditions = conditions + " and po.state in ('draft','sign','confirmed','approved','done')"
                self.cr.execute( """
					select                      distinct po.name as order_name,  
				                                         ir.name as ir_name ,
                                                         ir.ir_date as order_date,
                                                        part.name as supplier ,
                                                        po.date_order as date_order,
		                                               dep.name as department,
                                                       po.amount_total as amount_total,
                                                       po.state as state,
                                                       ir.purchase_type as purchase_type 


								    From purchase_order po 
								    left join ireq_m ir on (po.ir_id=ir.id)
		                            left join res_company comp on (po.company_id=comp.id)
								    left join hr_department dep on (po.department_id=dep.id)
							        left join res_currency curr on (po.currency_id=curr.id)
								    left join res_partner part on (po.partner_id=part.id)                                                                    
								where (to_char(po.date_order,'YYYY-mm-dd')>=%s and to_char(po.date_order,'YYYY-mm-dd')<=%s) """ + conditions + """order by ir.name"""  ,(date1,date2,))
	   res = self.cr.dictfetchall()
           return res




     






report_sxw.report_sxw('report.search_and_inform_report', 'purchase.order', 'addons/purchase_customization/report/search_and_inform.rml' ,parser=search_and_inform_report,header='internal landscape')
