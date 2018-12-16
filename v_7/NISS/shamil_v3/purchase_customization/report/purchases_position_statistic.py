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


class purchases_position_statistic(report_sxw.rml_parse):
      def __init__(self, cr, uid, name, context):
        super(purchases_position_statistic, self).__init__(cr, uid, name, context)
        self.localcontext.update({
            'time' : time,
            'get_pick_data' : self.get_picking_data,
            'get_move_data' : self.get_move_data,


        })
      

      def get_picking_data(self,data):
           date1 = data['form']['from_date'] 
           date2 = data['form']['to_date'] 
           company_id = data['form']['company_id']
           department_id = data['form']['department_id']
           category_id = data['form']['category_id']
           product_id = data['form']['product_id']
           location_id = data['form']['location_id']
           with_childern = data['form']['with_childern']
           executing_agency = data['form']['executing_agency']
           
           
           conditions = " and pick.type = 'in'"
           if company_id :
              conditions = conditions + " and po.company_id=(%s)"%company_id[0] 
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


           if category_id :
              cat_ids = self.pool.get('product.category').search(self.cr , self.uid , [('id' , 'child_of' , category_id[0]  )])
              category_ids = tuple(cat_ids)
              if len(category_ids) == 1:
                  conditions = conditions + " and p_temp.categ_id =(%s)"%category_ids[0]
              else :
                  conditions = conditions + " and p_temp.categ_id in %s"%str(category_ids)


           if product_id :
              conditions = conditions + " and pdc.id=(%s)"%product_id[0]
           if executing_agency :
               conditions = conditions + " and pick.executing_agency='%s'"%executing_agency
               
               
           self.cr.execute( """
                select                        
                                distinct po.department_id as department_id,
                                         dep.name as department_name 
                                         
                                From purchase_order po
                                    left join purchase_order_line po_line on (po_line.order_id = po.id)
                                    left join stock_picking pick on (pick.purchase_id = po.id)
                                    left join hr_department dep on (po.department_id=dep.id)
                                    left join stock_location loc on (loc.id=po.location_id)
                                    left join product_product pdc on (po_line.product_id=pdc.id)
                                    left join product_template p_temp on (pdc.product_tmpl_id = p_temp.id)

                                
                            where (to_char(po.date_order,'YYYY-mm-dd')>=%s and to_char(po.date_order,'YYYY-mm-dd')<=%s) and po.state = 'approved' 
                """ + conditions + """ order by po.department_id """ ,(date1,date2,)) 
           
           res = self.cr.dictfetchall()
           return res
          
          
      def get_move_data(self,data,department_id):

           date1 = data['form']['from_date'] 
           date2 = data['form']['to_date'] 
           company_id = data['form']['company_id']
           product_id = data['form']['product_id']
           location_id = data['form']['location_id']
           with_childern = data['form']['with_childern']
           executing_agency = data['form']['executing_agency']


           conditions = " and pick.type = 'in' "
           if company_id :
              conditions = conditions + " and pick.company_id=(%s)"%company_id[0] 
           if location_id :
              conditions = conditions + " and pick.location_dest_id=(%s)"%location_id[0]
           if product_id :
              conditions = conditions + " and pdc.id=(%s)"%product_id[0]
           if department_id :

              if with_childern == True:
                 department_ids = self.pool.get('hr.department').search(self.cr , self.uid , [('id' , 'child_of' , department_id )])
                 if len(department_ids) == 1:
                     conditions = conditions + " and pick.department_id=(%s)"%department_ids[0]
                 else :
                     department_ids = tuple(department_ids)
                     conditions = conditions + " and pick.department_id in %s"%str(department_ids)
              else :   
                 conditions = conditions + " and pick.department_id=(%s)"%department_id
           if executing_agency :
               conditions = conditions + " and pick.executing_agency='%s'"%executing_agency  
           self.cr.execute( """
                select                        
                                distinct move.name as product_name,
                                         cast(sum(move.product_qty) as integer) as qty,
                                         sum(move.price_unit) / count(move.product_qty)  as price_unit , 
                                         sum(move.price_unit * move.product_qty) as sub_total
                                         
                                From stock_move move 
                                    left join stock_picking pick on (pick.id=move.picking_id)
                                    left join purchase_order po on (pick.purchase_id = po.id)
                                    left join stock_location loc on (loc.id=pick.location_dest_id)
                                    left join product_product pdc on (move.product_id=pdc.id)
                                    left join product_template p_temp on (pdc.product_tmpl_id = p_temp.id)

                                
                            where (to_char(po.date_order,'YYYY-mm-dd')>=%s and to_char(po.date_order,'YYYY-mm-dd')<=%s) and pick.state not in ('cancel') 
                           """ + conditions + """ group by move.name order by move.name   """  ,(date1,date2)) 
           res = self.cr.dictfetchall()
           return res




     






report_sxw.report_sxw('report.purchases_position_statistic_report', 'stock.picking', 'addons/purchase_customization/report/purchases_position_statistic.rml' ,parser=purchases_position_statistic,header=False)
