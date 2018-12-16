# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

import time
from report import report_sxw
from osv import osv
import pooler
from openerp.tools.amount_to_text_en import amount_to_text
from base_custom.amount_to_text_ar import amount_to_text as amount_to_text_ar

class request_financial_ratification(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(request_financial_ratification, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            'function' : self.get_data,
            'get_data_detail' : self.get_data_detail,
            'get_sum' : self.get_sum_of_amounts,
            'get_amount_written' : self.get_amount_written,
            'get_department' : self.get_department,
            'get_quote_info' : self.get_quote_info,
            'convert_to_int' : self.convert_to_int,
        })
    def get_department(self,data):
        ireq_m_obj = self.pool.get(data['model'])
        
        result = { 'department' : '' }
        request_financial_ids = data['form']['request_financial_ids']
        if len(request_financial_ids) == 1:
           condition = " where ir.id in (%s)"%request_financial_ids[0]
           self.cr.execute(""" select dept.name as dept_name ,ir.purchase_purposes as purchase_purposes from hr_department dept
                                left join ireq_m ir on (ir.department_id = dept.id)  
                                """ + condition )
           res = self.cr.dictfetchall()

           result = { 'department' : res[0]['dept_name'] ,
                        'purpose' : res[0]['purchase_purposes'] , } 
        else:
            
           first_rec_department_id = ireq_m_obj.browse(self.cr ,self.uid ,data['form']['request_financial_ids'])[0].department_id.id
           department = ireq_m_obj.browse(self.cr ,self.uid ,data['form']['request_financial_ids'])[0].department_id.name
           for record in ireq_m_obj.browse(self.cr ,self.uid ,data['form']['request_financial_ids']):
                if first_rec_department_id != record.department_id.id :
                   department = 'جهات مختلفه' 
      
           request_financial_ids = tuple(request_financial_ids)
           condition = " where ir.id in (%s)"%str(request_financial_ids[0])
           self.cr.execute(""" select string_agg(ir.purchase_purposes , '+') as purchase_purposes  from ireq_m ir
                                left join hr_department dept on (ir.department_id = dept.id)  
                                """ + condition )
           res = self.cr.dictfetchall()
           
           result = { 'department' : department ,
                      'purpose' : res[0]['purchase_purposes'] ,}  
        return result



    def get_amount_written(self, amount_total):
        return amount_to_text_ar(amount_total)

    def get_sum_of_amounts(self,data):
        request_financial_ids = data['form']['request_financial_ids']
        if len(request_financial_ids) == 1:
                condition = " and ir.id in (%s)"%request_financial_ids[0]
        else:
                request_financial_ids = tuple(request_financial_ids)
                condition = " and ir.id in %s"%str(request_financial_ids)
        self.cr.execute( """
				select          sum (pq.price_subtotal) as sum_amount
  
							    From ireq_m ir 
						        left join pur_quote quote on (quote.pq_ir_ref=ir.id)
                                left join pq_products pq on ( (pq.pr_pq_id=quote.id and pq.chosen=True and ir.multi='multiple') or (pq.pr_pq_id=quote.id and ir.multi='exclusive') )
							    left join res_partner part on ( (quote.supplier_id=part.id and pq.chosen=True and ir.multi='multiple') or (quote.supplier_id=part.id and ir.multi='exclusive') ) 
							    left join res_currency curr on (quote.currency_id=curr.id)
							    left join product_product pdc on (pq.product_id=pdc.id) where quote.state in ('done') """ + condition )
         
        res = self.cr.dictfetchall()
        return res


    def get_data(self,data):
           
           request_financial_ids = data['form']['request_financial_ids']
           report_type = data['form']['report_type']

           if len(request_financial_ids) == 1:
                condition = " and ir.id in (%s)"%request_financial_ids[0]
           else:
                request_financial_ids = tuple(request_financial_ids)
                condition = " and ir.id in %s"%str(request_financial_ids) 
           if report_type not in ["with_items","without_items","suppliers_only"] :
               self.cr.execute( """
				                        select                        
		                                                distinct ir.name as name ,
                                                        quote.id as quote_id ,
                                                        sum (pq.price_subtotal) as total,
                                                        part.name as partner,
                                                        curr.name as currency
                          
							                            From ireq_m ir 
						                                left join pur_quote quote on (quote.pq_ir_ref=ir.id)
                                                        left join pq_products pq on ( (pq.pr_pq_id=quote.id and pq.chosen=True and ir.multi='multiple') or (pq.pr_pq_id=quote.id and ir.multi='exclusive') )
							                            left join res_partner part on ( (quote.supplier_id=part.id and pq.chosen=True and ir.multi='multiple') or (quote.supplier_id=part.id and ir.multi='exclusive') ) 
							                            left join res_currency curr on (quote.currency_id=curr.id)
							                            left join product_product pdc on (pq.product_id=pdc.id)

							                            
							                        where quote.state in ('done') """ + condition  + """ group by quote.id,part.name,curr.name,ir.name  order by part.name,ir.name """)
           

           else :
             self.cr.execute( """
				                        select                        
		                                                
                                                        sum (pq.price_subtotal) as total,
                                                        part.name as partner,
                                                        curr.name as currency
                          
							                            From ireq_m ir 
						                                left join pur_quote quote on (quote.pq_ir_ref=ir.id)
                                                        left join pq_products pq on ( (pq.pr_pq_id=quote.id and pq.chosen=True and ir.multi='multiple') or (pq.pr_pq_id=quote.id and ir.multi='exclusive') )
							                            left join res_partner part on ( (quote.supplier_id=part.id and pq.chosen=True and ir.multi='multiple') or (quote.supplier_id=part.id and ir.multi='exclusive') ) 
							                            left join res_currency curr on (quote.currency_id=curr.id)
							                            left join product_product pdc on (pq.product_id=pdc.id)

							                            
							                        where quote.state in ('done') """ + condition  + """ group by part.name,curr.name  order by part.name""")
           res = self.cr.dictfetchall()

           return res




     
    
    def convert_to_int(self,num ):
       return int(num)

    def get_data_detail(self,data):
           
           request_financial_ids = data['form']['request_financial_ids']
           report_type = data['form']['report_type']

           if len(request_financial_ids) == 1:
                condition = " and ir.id in (%s)"%request_financial_ids[0]
           else:
                request_financial_ids = tuple(request_financial_ids)
                condition = " and ir.id in %s"%str(request_financial_ids) 

           self.cr.execute( """
				                    select                        
		                                            distinct quote.supplier_id as supplier_id,
                                                    part.name as partner
                                                    
                                                    
                      
							                        From ireq_m ir 
						                            left join pur_quote quote on (quote.pq_ir_ref=ir.id)
                                                    left join pq_products pq on ( (pq.pr_pq_id=quote.id and pq.chosen=True and ir.multi='multiple') or (pq.pr_pq_id=quote.id and ir.multi='exclusive') )
							                        left join res_partner part on ( (quote.supplier_id=part.id and pq.chosen=True and ir.multi='multiple') or (quote.supplier_id=part.id and ir.multi='exclusive') ) 
							                        left join res_currency curr on (quote.currency_id=curr.id)
							                        left join product_product pdc on (pq.product_id=pdc.id)

							                        
							                    where quote.state in ('done') """ + condition  + """ group by quote.supplier_id,part.name,curr.name,ir.name  order by quote.supplier_id""")
             
           res = self.cr.dictfetchall()

           return res




     
    def get_quote_info(self,data,supplier_id):
        request_financial_ids = data['form']['request_financial_ids']
        report_type = data['form']['report_type']

        if len(request_financial_ids) == 1:
                condition = " and ir.id in (%s)"%request_financial_ids[0]
        else:
                request_financial_ids = tuple(request_financial_ids)
                condition = " and ir.id in %s"%str(request_financial_ids)    
        self.cr.execute( """
				    select                        
                                    distinct pdc.id as product,
                                    pq.name as product_name,
                                    cast(sum(pq.product_qty)  as integer) as qty,
                                    sum(pq.price_unit)/count(pq.product_qty) as price_unit



      
							        From pur_quote quote 
						                            left join ireq_m ir on (quote.pq_ir_ref=ir.id)
                                                    left join pq_products pq on ( (pq.pr_pq_id=quote.id and pq.chosen=True and ir.multi='multiple') or (pq.pr_pq_id=quote.id and ir.multi='exclusive') )
							                        left join res_partner part on ( (quote.supplier_id=part.id and pq.chosen=True and ir.multi='multiple') or (quote.supplier_id=part.id and ir.multi='exclusive') ) 
							                        left join product_product pdc on (pq.product_id=pdc.id)

							        
							    where quote.supplier_id=%s and quote.state ='done'""" + condition  + """ group by pdc.id,pq.name order by pdc.id""",(supplier_id,)) 

        res = self.cr.dictfetchall()

        return res
report_sxw.report_sxw('report.request_financial_ratification','ireq.m','purchase_customization/report/request_financial_ratification.rml',parser=request_financial_ratification,header=False)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
