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


class purchases_suppliers_report(report_sxw.rml_parse):
      def __init__(self, cr, uid, name, context):
        super(purchases_suppliers_report, self).__init__(cr, uid, name, context)
        self.localcontext.update({
            'time' : time,
            'function' : self.get_move_data,


        })
      


      def get_move_data(self,data):


           date1 = data['form']['from_date'] 
           date2 = data['form']['to_date'] 
           company_id = data['form']['company_id']
           department_id = data['form']['department_id']
           category_id = data['form']['category_id']
           product_id = data['form']['product_id']
           supplier_id = data['form']['supplier_id']
           executing_agency = data['form']['executing_agency']


           conditions = ""         
           if company_id :
              conditions = conditions + " and po.company_id=(%s)"%company_id[0] 
           if category_id :
              conditions = conditions + " and p_temp.categ_id=(%s)"%category_id[0] 
           
           if department_id :
              conditions = conditions + " and po.department_id=(%s)"%department_id[0] 
           if product_id :
              conditions = conditions + " and pdc.id=(%s)"%product_id[0]
           
           if executing_agency :
              conditions = conditions + " and po.executing_agency=('%s')"%executing_agency

           if supplier_id :
              conditions = conditions + " and po.partner_id=(%s)"%supplier_id[0] 
            

             
           self.cr.execute( """
				select                        
		                                            distinct part.id as id,
                                                                     part.name as parter_name ,
                                                                     sum(po.amount_total) as po_sum_amount,
							             count(po.id) as po_counter
							    From purchase_order po 

                                                            left join res_company comp on (po.company_id=comp.id)
                                                            left join purchase_order_line line on (line.order_id = po.id)
                                                            left join res_partner part on (po.partner_id=part.id) 
							    left join hr_department dep on (po.department_id=dep.id)
							    left join product_product pdc on (line.product_id=pdc.id)
                                                            left join product_template p_temp on (pdc.product_tmpl_id = p_temp.id)
							    left join product_category catg on (p_temp.categ_id=catg.id)

							    
							where (to_char(po.date_order,'YYYY-mm-dd')>=%s and to_char(po.date_order,'YYYY-mm-dd')<=%s) and po.state not in ('cancel') 
		        """ + conditions + """group by part.id order by count(po.id) desc """  ,(date1,date2,)) 
           res = {}
           res['orders'] = self.cr.dictfetchall()
           orders_amount_sum = 0
           orders_counter_sum = 0
           for rec in res['orders'] :
               orders_amount_sum+= rec['po_sum_amount']
               orders_counter_sum+= rec['po_counter']

           res['orders_amount_sum'] = orders_amount_sum
           res['orders_counter_sum'] = orders_counter_sum

           return res




     






report_sxw.report_sxw('report.purchases_suppliers_report', 'purchase.order', 'addons/purchase_customization/report/purchases_suppliers_report.rml' ,parser=purchases_suppliers_report,header=False)
