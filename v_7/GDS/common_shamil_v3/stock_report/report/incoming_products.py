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


class incoming_products_report(report_sxw.rml_parse):
      def __init__(self, cr, uid, name, context):
        super(incoming_products_report, self).__init__(cr, uid, name, context)
        self.localcontext.update({
            'time' : time,
            'function' : self.get_move_data,


        })
      


      def get_move_data(self,data):


           date1 = data['form']['from_date'] 
           date2 = data['form']['to_date'] 
           company_id = data['form']['company_id']
           department_id = data['form']['department_id']
           #category_id = data['form']['category_id']
           product_id = data['form']['product_id']
           location_id = data['form']['location_id']
           supplier_id = data['form']['supplier_id']
           report_type = data['form']['report_type']
           conditions = " and pick.type = 'in'"
                      
           if company_id :
              conditions = conditions + " and pick.company_id=(%s)"%company_id[0] 
           #if category_id :
           #   conditions = conditions + " and p_temp.categ_id=(%s)"%category_id[0] 
           if location_id :
              conditions = conditions + " and pick.location_dest_id=(%s)"%location_id[0] 
           if department_id :
              conditions = conditions + " and po.department_id=(%s)"%department_id[0] 
           if product_id :
              conditions = conditions + " and pdc.id=(%s)"%product_id[0]
           if supplier_id :
              conditions = conditions + " and pick.partner_id=(%s)"%supplier_id[0]

           self.cr.execute( """
				select                        
		                                            distinct move.name as name ,
                                                            min(pdc.default_code) as no,
							    sum(move.product_qty) as qty,
							    sum(move.price_unit) / count(move.product_qty)  as price_unit
							    From stock_move move 
						            left join stock_picking pick on (pick.id=move.picking_id)
                                                            left join res_company comp on (pick.company_id=comp.id)
							    left join purchase_order po on (pick.purchase_id=po.id)
                                                            left join res_partner part on (pick.partner_id=part.id and po.partner_id = part.id) 
							    left join hr_department dep on (po.department_id=dep.id)
							    left join stock_location loc on (loc.id=pick.location_dest_id)
							    left join product_product pdc on (move.product_id=pdc.id)
                                                            left join product_template p_temp on (pdc.product_tmpl_id = p_temp.id)


							    
							where (to_char(pick.date,'YYYY-mm-dd')>=%s and to_char(pick.date,'YYYY-mm-dd')<=%s) and pick.state not in ('cancel') 
		        """ + conditions + """group by move.name order by min(pdc.default_code) """  ,(date1,date2,)) 
           res = {}
           res['move'] = self.cr.dictfetchall()
           sum = 0
           for rec in res['move'] :
               sum += rec['price_unit'] * rec['qty']
               
           res['total'] = sum
           return res




     






report_sxw.report_sxw('report.incoming_products_report', 'stock.picking', 'addons/stock_report/report/incoming_products.rml' ,parser=incoming_products_report,header='internal landscape')
