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


class sale_order_all_report(report_sxw.rml_parse):
      def __init__(self, cr, uid, name, context):
        super(sale_order_all_report, self).__init__(cr, uid, name, context)
        self.localcontext.update({
            'time' : time,
            'function' : self.get_sale_order_data,
	    'total':self._gettotal,
            'line2':self._getdetails,
        })
# Method to get data      
      def get_sale_order_data(self,data):
           date1 = data['form']['from_date'] 
           date2 = data['form']['to_date'] 
           company_id = data['form']['company_id']
           category_id = data['form']['category_id']
           location_id = data['form']['location_id']
           payroll_id = data['form']['scale_id']
           payment_type = data['form']['payment_type']
           receive_state = data['form']['receive_state']
           emp_id = data['form']['emp_id']
           report_type = data['form']['report_type']
           conditions = "and emp.payroll_id=%s"%payroll_id[0]
           if company_id :
              		conditions = conditions + " and so.company_id=(%s)"%company_id[0] 
           if category_id :
              		conditions = conditions + " and so.category_id=(%s)"%category_id[0] 
           if location_id :
              		conditions = conditions + " and so.shop_id=(%s)"%location_id[0]
	   #if payment_type :
			#conditions = conditions + " and so.payment_type='%s'"%payment_type
           if emp_id :
              		conditions = conditions + " and so.employee_id=(%s)"%emp_id[0]

	   if report_type == 'deduction' : 
		if  payment_type == 'installment' : 
           		self.cr.execute( """
                		select                        
                                	distinct so.name as name ,
					so.id as id ,
                                	so.date_order as date_order,
                                	emp.name_related as employee,
                                	emp.degree_id as degree,
                                	emp.emp_code as code,
					emp.otherid as other_id , 
					l.period as period ,
					so.state as state ,
                                	sum (l.installment_value * l.product_uom_qty) as total
                                
                                From sale_order so
                    
                                	left join res_company comp on (so.company_id=comp.id)
                                	left join hr_employee emp on (so.employee_id=emp.id)
                                	left join hr_salary_scale scale on (emp.payroll_id = scale.id)
                                	left join sale_shop shop on (shop.id= so.shop_id)
                                	left join sale_category cat on (so.category_id=cat.id)
					left join sale_order_line l on (so.id = l.order_id)
                            where (to_char(so.start_date,'YYYY-mm-dd')>=%s and to_char(so.start_date,'YYYY-mm-dd')<=%s) and so.payment_type in ('installment','up_cash') and so.state in ('done') and so.print_order = True
                """ + conditions + """group by l.period,so.id,so.name,emp.otherid,so.date_order,emp.name_related,emp.degree_id,emp.emp_code,so.state order by so.name  """  ,(date1,date2,)) 
           		move = self.cr.dictfetchall()
		if  payment_type == 'cash' : 
			conditions = conditions + " and so.payment_type='%s'"%payment_type
           		self.cr.execute( """
                		select                        
                                	distinct so.name as name ,
					so.id as id ,
                                	so.date_order as date_order,
                                	emp.name_related as employee,
                                	emp.degree_id as degree,
                                	emp.emp_code as code,
					emp.otherid as other_id , 
					so.state as state ,
                                	sum (l.price_unit * l.product_uom_qty) as total
                                
                                From sale_order so
                    
                                	left join res_company comp on (so.company_id=comp.id)
                                	left join hr_employee emp on (so.employee_id=emp.id)
                                	left join hr_salary_scale scale on (emp.payroll_id = scale.id)
                                	left join sale_shop shop on (shop.id= so.shop_id)
                                	left join sale_category cat on (so.category_id=cat.id)
					left join sale_order_line l on (so.id = l.order_id)
                            where (to_char(so.create_date,'YYYY-mm-dd')>=%s and to_char(so.create_date,'YYYY-mm-dd')<=%s) and so.state in ('done') and so.print_order = True
                """ + conditions + """group by so.id,so.name,emp.otherid,so.date_order,emp.name_related,emp.degree_id,emp.emp_code,so.state order by so.name  """  ,(date1,date2,)) 
           		move = self.cr.dictfetchall()
		if  payment_type == 'up_cash' :
			conditions = conditions + " and so.payment_type='%s'"%payment_type 
           		self.cr.execute( """
                		select                        
                                	distinct so.name as name ,
					so.id as id ,
                                	so.date_order as date_order,
                                	emp.name_related as employee,
                                	emp.degree_id as degree,
                                	emp.emp_code as code,
					emp.otherid as other_id , 
					so.state as state ,
                                	sum (l.up_front * l.product_uom_qty) as total
                                
                                From sale_order so
                    
                                	left join res_company comp on (so.company_id=comp.id)
                                	left join hr_employee emp on (so.employee_id=emp.id)
                                	left join hr_salary_scale scale on (emp.payroll_id = scale.id)
                                	left join sale_shop shop on (shop.id= so.shop_id)
                                	left join sale_category cat on (so.category_id=cat.id)
					left join sale_order_line l on (so.id = l.order_id)
                            where (to_char(so.start_date,'YYYY-mm-dd')>=%s and to_char(so.start_date,'YYYY-mm-dd')<=%s) and so.state in ('done') and so.print_order = True
                """ + conditions + """group by so.id,so.name,emp.otherid,so.date_order,emp.name_related,emp.degree_id,emp.emp_code,so.state order by so.name  """  ,(date1,date2,)) 
           		move = self.cr.dictfetchall()
	   else :
	   	if receive_state :
                	conditions += receive_state and (receive_state == 'done' and " and sp.state= 'done' " or " and sp.state != 'done' ") or ""

           	self.cr.execute( """
                	select                        
                                distinct so.name as name ,
				so.id as id ,
                                so.date_order as date_order,
                                emp.name_related as employee,
                                emp.degree_id as degree,
                                emp.emp_code as code,
				emp.otherid as other_id ,
				sum (l.up_front * l.product_uom_qty) as front, 
                                sum (l.installment_value * l.product_uom_qty) as total ,
				sp.state as state 
                                
                                From sale_order so
                    
                                left join res_company comp on (so.company_id=comp.id)
                                left join hr_employee emp on (so.employee_id=emp.id)
                                left join hr_salary_scale scale on (emp.payroll_id = scale.id)
                                left join sale_shop shop on (shop.id= so.shop_id)
                                left join sale_category cat on (so.category_id=cat.id)
				left join sale_order_line l on (so.id = l.order_id)
				left join stock_picking sp on (so.id = sp.sale_id)

                                
                            where so.deliver_order=False and (to_char(so.create_date,'YYYY-mm-dd')>=%s and to_char(so.create_date,'YYYY-mm-dd')<=%s) and so.state in ('done') 
                """ + conditions + """group by so.id,so.name,emp.otherid,so.date_order,emp.name_related,emp.degree_id,emp.emp_code,sp.state order by so.name  """  ,(date1,date2,))
           	move = self.cr.dictfetchall()
	   	for record in move : 
			update_id = self.cr.execute( """ update sale_order set deliver_order=True where id=%s"""%record['id'])
           return move
#Method to calculate Total
      def _gettotal(self,data):
           date1 = data['form']['from_date'] 
           date2 = data['form']['to_date'] 
           company_id = data['form']['company_id']
           category_id = data['form']['category_id']
           location_id = data['form']['location_id']
           payroll_id = data['form']['scale_id']
           payment_type = data['form']['payment_type']
           receive_state = data['form']['receive_state']
           emp_id = data['form']['emp_id']
           report_type = data['form']['report_type']
           
           conditions = "and emp.payroll_id=%s"%payroll_id[0]
           if company_id :
              conditions = conditions + " and so.company_id=(%s)"%company_id[0] 
           if category_id :
              conditions = conditions + " and so.category_id=(%s)"%category_id[0] 
           if location_id :
              conditions = conditions + " and so.shop_id=(%s)"%location_id[0]
	   #if payment_type :
		#conditions = conditions + " and so.payment_type='%s'"%payment_type
	   """if receive_state :
                conditions += receive_state and (receive_state == 'done' and " and sp.state= 'done' " or " and sp.state not in ('done','cancel') ") or """""
           if emp_id :
              conditions = conditions + " and so.employee_id=(%s)"%emp_id[0]

	   if report_type == 'deduction' : 
		if  payment_type == 'installment' : 
              
           		self.cr.execute( """
                		select sum (l.installment_value * l.product_uom_qty * l.period) as total                
                                From sale_order so
                                left join res_company comp on (so.company_id=comp.id)
				left join sale_order_line l on (so.id = l.order_id)
                                left join hr_employee emp on (so.employee_id=emp.id)
                                left join hr_salary_scale scale on (emp.payroll_id = scale.id)
                                left join sale_shop shop on (shop.id= so.shop_id)
                                left join sale_category cat on (so.category_id=cat.id)
				left join stock_picking sp on (so.id = sp.sale_id)
                                where (to_char(so.start_date,'YYYY-mm-dd')>=%s and to_char(so.start_date,'YYYY-mm-dd')<=%s) and so.payment_type in ('installment','up_cash') and so.state in ('done') and so.print_order = True
                """ + conditions ,(date1,date2,)) 
           		res = self.cr.dictfetchall()
		if  payment_type == 'cash' : 
              		conditions = conditions + " and so.payment_type='%s'"%payment_type
           		self.cr.execute( """
                		select sum (l.price_unit * l.product_uom_qty ) as total                
                                From sale_order so
                                left join res_company comp on (so.company_id=comp.id)
				left join sale_order_line l on (so.id = l.order_id)
                                left join hr_employee emp on (so.employee_id=emp.id)
                                left join hr_salary_scale scale on (emp.payroll_id = scale.id)
                                left join sale_shop shop on (shop.id= so.shop_id)
                                left join sale_category cat on (so.category_id=cat.id)
				left join stock_picking sp on (so.id = sp.sale_id)
                                where (to_char(so.start_date,'YYYY-mm-dd')>=%s and to_char(so.start_date,'YYYY-mm-dd')<=%s) and so.state in ('done') and so.print_order = True
                """ + conditions ,(date1,date2,)) 
           		res = self.cr.dictfetchall()
		if  payment_type == 'up_cash' : 
              		conditions = conditions + " and so.payment_type='%s'"%payment_type
           		self.cr.execute( """
                		select sum (l.up_front * l.product_uom_qty) as total                
                                From sale_order so
                                left join res_company comp on (so.company_id=comp.id)
				left join sale_order_line l on (so.id = l.order_id)
                                left join hr_employee emp on (so.employee_id=emp.id)
                                left join hr_salary_scale scale on (emp.payroll_id = scale.id)
                                left join sale_shop shop on (shop.id= so.shop_id)
                                left join sale_category cat on (so.category_id=cat.id)
				left join stock_picking sp on (so.id = sp.sale_id)
                                where (to_char(so.start_date,'YYYY-mm-dd')>=%s and to_char(so.start_date,'YYYY-mm-dd')<=%s) and so.state in ('done') and so.print_order = True
                """ + conditions ,(date1,date2,)) 
           		res = self.cr.dictfetchall()
           return res

#Method to get items details for devlivery request
      def _getdetails(self,data,ref):
           #data_product= data['form']['product_id']
           #where_condition = ""
           #where_condition += data_product and "f.product_id=%s"%data_product[0] or ""
           #where_condition += ref and " and r.id=%s"%ref or ""
           date1 = data['form']['from_date'] 
           date2 = data['form']['to_date'] 
           self.cr.execute("""
                SELECT 
                                  p.name_template as detail_name ,
				  l.product_uos_qty as qty 

                FROM sale_order so 
		left join sale_order_line l on (l.order_id = so.id)
		left join product_product p on (l.product_id = p.id)
                where so.id=%s order by p.name_template"""%ref)
           res = self.cr.dictfetchall()
           return res

report_sxw.report_sxw('report.sale_order_all_report', 'sale.order', 'addons/cooperative_sale/report/sale_order_all.rml' ,parser=sale_order_all_report,header=False)
