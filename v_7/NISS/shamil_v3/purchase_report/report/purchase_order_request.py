# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

import time
from report import report_sxw



class purchase_order_request(report_sxw.rml_parse):
      def __init__(self, cr, uid, name, context):
        super(purchase_order_request, self).__init__(cr, uid, name, context)
        self.localcontext.update({
            'time' : time,
            'line' : self._getdata,


        })
      

      
      def _getdata(self,data):
           date1 = data['form']['Date_from'] 
           date2 = data['form']['Date_to'] 
           purchase_type = data['form']['purchase_type']
           purchase_kind = data['form']['purchase_kind']
           request_state = data['form']['request_state']
           order_state = data['form']['order_state']
           department_id = data['form']['department_id']
           if purchase_kind == 'order' :
              if not order_state :
		       if not department_id :
			   	self.cr.execute( """
					   select

						    min(s.name) as name,
						    min(s.state) as state,
						    min(p_cat.name) as catg,
						    min(s.date_order) as order_date,
						    min(rp.name) as partner_name,
						    min(s.amount_total) as Amount,
                                                    min(curr.name) as currency_name
						    
						    From purchase_order s 
						    left join ireq_m ir on (s.ir_id=ir.id) 
						    left join res_partner rp on (s.partner_id=rp.id)
						    left join purchase_order_line l on (s.id=l.order_id)
                                                    left join res_currency curr on (s.currency_id=curr.id)
						    left join product_category p_cat on (s.cat_id=p_cat.id)


						where (to_char(s.date_order,'YYYY-mm-dd')>=%s and to_char(s.date_order,'YYYY-mm-dd')<=%s) and (s.state NOT IN ('cancel')) and s.purchase_type=%s
						group by
						    s.id , s.amount_total 
				
					""",(date1,date2,purchase_type)) 
				res = self.cr.dictfetchall()
                       else :
		            self.cr.execute( """
					   select
						    min(d.name) as department,
						    min(s.name) as name,
						    min(s.state) as state,
						    min(p_cat.name) as catg,
						    min(s.date_order) as order_date,
						    min(rp.name) as partner_name,
						    min(s.amount_total) as Amount,
                                                    min(curr.name) as currency_name

						    
						    From purchase_order s 
						    left join ireq_m ir on (s.ir_id=ir.id) 
						    left join res_partner rp on (s.partner_id=rp.id)
						    left join purchase_order_line l on (s.id=l.order_id)
						    left join hr_department d on (s.department_id=d.id)
						    left join product_category p_cat on (s.cat_id=p_cat.id)
                                                    left join res_currency curr on (s.currency_id=curr.id)

						where (to_char(s.date_order,'YYYY-mm-dd')>=%s and to_char(s.date_order,'YYYY-mm-dd')<=%s) and (s.state NOT IN ('cancel')) and s.purchase_type=%s and s.department_id=%s
						group by
						    s.id , s.amount_total 
				
					""",(date1,date2,purchase_type,department_id[0])) 
		            res = self.cr.dictfetchall()
              else : 
                 if not department_id :
		    self.cr.execute( """			   select
				    min(d.name) as department,
				    min(s.name) as name,
				    min(s.state) as state,
				    min(p_cat.name) as catg,
				    min(s.date_order) as order_date,
				    min(rp.name) as partner_name,
                                    min(s.amount_total) as Amount,
                                    min(curr.name) as currency_name

				    
				    From purchase_order s 
				    left join ireq_m ir on (s.ir_id=ir.id) 
				    left join res_partner rp on (s.partner_id=rp.id)
				    left join purchase_order_line l on (s.id=l.order_id)
				    left join hr_department d on (s.department_id=d.id)
				    left join product_category p_cat on (s.cat_id=p_cat.id)
                                    left join res_currency curr on (s.currency_id=curr.id)
				where (to_char(s.date_order,'YYYY-mm-dd')>=%s and to_char(s.date_order,'YYYY-mm-dd')<=%s) and s.state=%s and s.purchase_type=%s
				group by
				    s.id , s.amount_total 
				
			""",(date1,date2,order_state,purchase_type)) 
		    res = self.cr.dictfetchall()
                 else :


		    self.cr.execute( """			   select
				    min(d.name) as department,
				    min(s.name) as name,
				    min(s.state) as state,
				    min(p_cat.name) as catg,
				    min(s.date_order) as order_date,
				    min(rp.name) as partner_name,
		                    min(s.amount_total) as amount,
                                    min(curr.name) as currency_name

				    
				    From purchase_order s 
				    left join ireq_m ir on (s.ir_id=ir.id) 
				    left join res_partner rp on (s.partner_id=rp.id)
				    left join purchase_order_line l on (s.id=l.order_id)
				    left join hr_department d on (s.department_id=d.id)
				    left join product_category p_cat on (s.cat_id=p_cat.id)
                                    left join res_currency curr on (s.currency_id=curr.id)
				where (to_char(s.date_order,'YYYY-mm-dd')>=%s and to_char(s.date_order,'YYYY-mm-dd')<=%s) and s.state=%s and s.purchase_type=%s and s.department_id=%s
				group by
				    s.id , s.amount_total 
				
			""",(date1,date2,order_state,purchase_type,department_id[0])) 
		    res = self.cr.dictfetchall()



           else :
              if not request_state :
                if not department_id :
		        self.cr.execute( """
			   select
				    min(d.name) as department,
				    min(ir.name) as name,
				    min(ir.state) as state,
				    min(p_cat.name) as catg,
				    min(ir.ir_date) as order_date,
				    min(rp.name) as partner_name

				    
				    From ireq_m ir 
		                    left join pur_quote quote on (ir.id = quote.pq_ir_ref )
				    left join res_partner rp on (quote.supplier_id=rp.id )
				    left join ireq_products l on (ir.id=l.pr_rq_id)
				    left join hr_department d on (ir.department_id=d.id)
				    left join product_category p_cat on (ir.cat_id=p_cat.id)
				where (to_char(ir.ir_date,'YYYY-mm-dd')>=%s and to_char(ir.ir_date,'YYYY-mm-dd')<=%s)  and (ir.state NOT IN ('cancel')) and ir.purchase_type=%s
				group by
				    ir.id , quote.amount_total
			      
			""",(date1,date2,purchase_type)) 


                        res = self.cr.dictfetchall()
                else :


                    self.cr.execute( """
			   select
				    min(d.name) as department,
				    min(ir.name) as name,
				    min(ir.state) as state,
				    min(p_cat.name) as catg,
				    min(ir.ir_date) as order_date,
				    min(rp.name) as partner_name

				    
				    From ireq_m ir 
		                    left join pur_quote quote on (ir.id = quote.pq_ir_ref )
				    left join res_partner rp on (quote.supplier_id=rp.id )
				    left join ireq_products l on (ir.id=l.pr_rq_id)
				    left join hr_department d on (ir.department_id=d.id)
				    left join product_category p_cat on (ir.cat_id=p_cat.id)
				where (to_char(ir.ir_date,'YYYY-mm-dd')>=%s and to_char(ir.ir_date,'YYYY-mm-dd')<=%s)  and (ir.state NOT IN ('cancel')) and ir.purchase_type=%s and ir.department_id=%s
				group by
				    ir.id , quote.amount_total
			      
			""",(date1,date2,purchase_type,department_id[0])) 


                    res = self.cr.dictfetchall()







              else :
 
                  if not department_id :
		        self.cr.execute( """
			   select
				    min(d.name) as department,
				    min(ir.name) as name,
				    min(ir.state) as state,
				    min(p_cat.name) as catg,
				    min(ir.ir_date) as order_date,
				    min(rp.name) as partner_name

				    From ireq_m ir 
		                    left join pur_quote quote on (ir.id = quote.pq_ir_ref )
				    left join res_partner rp on (quote.supplier_id=rp.id )
				    left join ireq_products l on (ir.id=l.pr_rq_id)
				    left join hr_department d on (ir.department_id=d.id)
				    left join product_category p_cat on (ir.cat_id=p_cat.id)
				where (to_char(ir.ir_date,'YYYY-mm-dd')>=%s and to_char(ir.ir_date,'YYYY-mm-dd')<=%s)  and ir.state=%s and ir.purchase_type=%s
				group by
				    ir.id , quote.amount_total
			      
			""",(date1,date2,request_state,purchase_type)) 


		        res = self.cr.dictfetchall()
                  else :

		           self.cr.execute( """
				   select
					    min(d.name) as department,
					    min(ir.name) as name,
					    min(ir.state) as state,
					    min(p_cat.name) as catg,
					    min(ir.ir_date) as order_date,
					    min(rp.name) as partner_name

					    From ireq_m ir 
				            left join pur_quote quote on (ir.id = quote.pq_ir_ref )
					    left join res_partner rp on (quote.supplier_id=rp.id )
					    left join ireq_products l on (ir.id=l.pr_rq_id)
					    left join hr_department d on (ir.department_id=d.id)
					    left join product_category p_cat on (ir.cat_id=p_cat.id)
					where (to_char(ir.ir_date,'YYYY-mm-dd')>=%s and to_char(ir.ir_date,'YYYY-mm-dd')<=%s)  and ir.state=%s and ir.purchase_type=%s and ir.department_id=%s
					group by
					    ir.id , quote.amount_total
				      
				""",(date1,date2,request_state,purchase_type,department_id[0])) 


		           res = self.cr.dictfetchall()
           return res
report_sxw.report_sxw('report.purchase_order_request_report', 'purchase.order', 'addons/purchase_report/report/purchase_order_request.rml' ,parser=purchase_order_request,header='internal landscape')
