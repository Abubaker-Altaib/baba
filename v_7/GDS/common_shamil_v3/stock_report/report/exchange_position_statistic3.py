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


class exchange_position_statistic3(report_sxw.rml_parse):
      def __init__(self, cr, uid, name, context):
        super(exchange_position_statistic3, self).__init__(cr, uid, name, context)
        self.localcontext.update({
            'time' : time,
            'get_pick_data' : self.get_picking_data,
            'get_move_data' : self.get_move_data,
            'get_total' : self.get_total,
            'get_move_data2' : self.get_move_data2,


        })
      

      def get_picking_data(self,data):
           date1 = data['form']['from_date'] 
           date2 = data['form']['to_date'] 
           company_id = data['form']['company_id']
           department_id = data['form']['department_id']
           cat_id = data['form']['cat_id']
           product_id = data['form']['product_id']
           location_id = data['form']['location_id']
           with_childern = data['form']['with_childern']
           
           
           conditions = " and pick.type = 'out'"
           if company_id :
              conditions = conditions + " and pick.company_id=(%s)"%company_id[0] 
           
           if location_id :
              conditions = conditions + " and pick.location_dest_id=(%s)"%location_id[0] 
           if department_id :
              if with_childern == True:
                 department_ids = self.pool.get('hr.department').search(self.cr , self.uid , [('id' , 'child_of' , department_id[0] )])
                 if len(department_ids) == 1:
                     conditions = conditions + " and pick.department_id=(%s)"%department_ids[0]
                 else :
                     department_ids = tuple(department_ids)
                     conditions = conditions + " and pick.department_id in %s"%str(department_ids)
              else :   
                 conditions = conditions + " and pick.department_id=(%s)"%department_id[0]
           #if category_id :
           #   conditions = conditions + " and pick.category_id=(%s)"%category_id[0] 
              
           if product_id :
              conditions = conditions + " and pdc.id=(%s)"%product_id[0]

           
               
               
           self.cr.execute( """
                select                        
                                distinct pick.department_id as department_id,
                                         dep.name as department_name 
                                         
                                From stock_picking pick
                                    left join hr_department dep on (pick.department_id=dep.id)
                                    left join stock_move move on (move.picking_id = pick.id)
                                    left join stock_location loc on (loc.id=pick.location_dest_id)

                                    left join product_product pdc on (move.product_id=pdc.id)
                                    left join product_template p_temp on (pdc.product_tmpl_id = p_temp.id)

                                
                            where (to_char(pick.date,'YYYY-mm-dd')>=%s and to_char(pick.date,'YYYY-mm-dd')<=%s) and pick.state = 'done' 
                """ + conditions + """ order by pick.department_id """ ,(date1,date2,)) 

           res = self.cr.dictfetchall()
	   if cat_id :
	      cat_ids =  type_obj.search(self.cr, self.uid, [('id', 'child_of',cat_id[0])])		
              res=[x for x in res if x['cat_id'] in cat_ids]
           return res
          
          
      def get_move_data(self,data,department_id):
        
           date1 = data['form']['from_date'] 
           date2 = data['form']['to_date'] 
           company_id = data['form']['company_id']
 
           product_id = data['form']['product_id']
           cat_id = data['form']['cat_id']
           location_id = data['form']['location_id']
           with_childern = data['form']['with_childern']
           type_obj = self.pool.get('product.category') 
           cat_ids=[]
           conditions = " and pick.type = 'in' "
           if company_id :
              conditions = conditions + " and pick.company_id=(%s)"%company_id[0] 
           if location_id :
              conditions = conditions + " and pick.location_dest_id=(%s)"%location_id[0]
           
           if product_id :
              conditions = conditions + " and pdc.id=(%s)"%product_id[0]
	   
 
           if department_id:
              conditions = conditions + " and pick.department_id=(%s)"%department_id
           self.cr.execute( """
                select            distinct pick.department_id as dep_id,    
                                         p_temp.name as product_name,
                                         pdc.default_code as code,
                                         pdc.id as product_id,
                                         p_temp.categ_id as cat_id,
                                         cast(sum(move.product_qty) as integer) as qty
                                         
                                         
                                From stock_move move 
                                    left join stock_picking pick on (pick.id=move.picking_id)
                                    left join hr_department dep on (pick.department_id=dep.id)
                                    left join stock_location loc on (loc.id=pick.location_dest_id)
                                    left join product_product pdc on (move.product_id=pdc.id)
 
                                    left join product_template p_temp on (pdc.product_tmpl_id = p_temp.id)

                                
                            where (to_char(pick.date,'YYYY-mm-dd')>=%s and to_char(pick.date,'YYYY-mm-dd')<=%s)   and pick.state = ('done') 
                           """ + conditions + """ group by pick.department_id,pdc.id,p_temp.name ,p_temp.categ_id order by qty   """  ,(date1,date2)) 
           res = self.cr.dictfetchall()
	   if cat_id :
	      cat_ids =  type_obj.search(self.cr, self.uid, [('id', 'child_of',cat_id[0])])		
              res=[x for x in res if x['cat_id'] in cat_ids]
 
           return res


      def get_move_data2(self,data):
        
           date1 = data['form']['from_date'] 
           date2 = data['form']['to_date'] 
           company_id = data['form']['company_id']
           department_id = data['form']['department_id']
           product_id = data['form']['product_id']
           cat_id = data['form']['cat_id']
           location_id = data['form']['location_id']
           with_childern = data['form']['with_childern']
           type_obj = self.pool.get('product.category') 
           cat_ids=[]
           conditions = " and pick.type = 'in' "
           if company_id :
              conditions = conditions + " and pick.company_id=(%s)"%company_id[0] 
           if location_id :
              conditions = conditions + " and pick.location_dest_id=(%s)"%location_id[0]
           
           if product_id :
              conditions = conditions + " and pdc.id=(%s)"%product_id[0]
	   
 
           if department_id:
              conditions = conditions + " and pick.department_id=(%s)"%department_id
           self.cr.execute( """
                select                 
                                           p_temp.name as product_name,
                                           pdc.default_code as code,

                                         pdc.id as product_id,
                                         p_temp.categ_id as cat_id,
                                         cast(sum(move.product_qty) as integer) as qty
                                         
                                         
                                From stock_move move 
                                    left join stock_picking pick on (pick.id=move.picking_id)
                                    left join hr_department dep on (pick.department_id=dep.id)
                                    left join stock_location loc on (loc.id=pick.location_dest_id)
                                    left join product_product pdc on (move.product_id=pdc.id)
 
                                    left join product_template p_temp on (pdc.product_tmpl_id = p_temp.id)

                                
                            where (to_char(pick.date,'YYYY-mm-dd')>=%s and to_char(pick.date,'YYYY-mm-dd')<=%s)   and pick.state = ('done') 
                           """ + conditions + """ group by pdc.id, p_temp.name ,p_temp.categ_id order by qty   """  ,(date1,date2)) 
           res = self.cr.dictfetchall()
	   if cat_id :
	      cat_ids =  type_obj.search(self.cr, self.uid, [('id', 'child_of',cat_id[0])])		
              res=[x for x in res if x['cat_id'] in cat_ids]
 
           return res


      def get_total(self,data):
	   date1 = data['form']['from_date'] 
           date2 = data['form']['to_date'] 
           company_id = data['form']['company_id']
           department_id = data['form']['department_id']
 
           product_id = data['form']['product_id']
           cat_id = data['form']['cat_id']
           location_id = data['form']['location_id']
           with_childern = data['form']['with_childern']
           type_obj = self.pool.get('product.category') 
           cat_ids=[]
           conditions = " and pick.type = 'in' "
           if company_id :
              conditions = conditions + " and pick.company_id=(%s)"%company_id[0] 
           if location_id :
              conditions = conditions + " and pick.location_dest_id=(%s)"%location_id[0]
           
           if product_id :
              conditions = conditions + " and pdc.id=(%s)"%product_id[0]
           if cat_id :
              conditions = conditions + " and pdcc.id=(%s)"%cat_id[0]
	   
 
           if department_id:
              conditions = conditions + " and pick.department_id=(%s)"%department_id[0]
           self.cr.execute( """
 
 
 
select
 
 
                                         cast(sum(move.product_qty) as integer) as qty
                                         
                                         
                                From stock_move move 
                                    left join stock_picking pick on (pick.id=move.picking_id)
                                    left join hr_department dep on (pick.department_id=dep.id)
                                    left join stock_location loc on (loc.id=pick.location_dest_id)
                                    left join product_product pdc on (move.product_id=pdc.id)
                                    left join product_template p_temp on (pdc.product_tmpl_id = p_temp.id)
                                    left join product_category pdcc on (p_temp.categ_id=pdcc.id)

 


                                
                            where (to_char(pick.date,'YYYY-mm-dd')>=%s and to_char(pick.date,'YYYY-mm-dd')<=%s)   and pick.state = ('done') 
                           """ + conditions + """  order by qty   """  ,(date1,date2)) 
           res = self.cr.dictfetchall()
	    
            
           return res

     






report_sxw.report_sxw('report.exchange_position_statistic_report3', 'stock.picking', 'addons/stock_report/report/exchange_position_statistic3.rml' ,parser=exchange_position_statistic3,header='internal landscape')
