# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

import time
from report import report_sxw



class stock_cooperative_delivery_orders_report(report_sxw.rml_parse):
      def __init__(self, cr, uid, name, context):
        super(stock_cooperative_delivery_orders_report, self).__init__(cr, uid, name, context)
        self.localcontext.update({
            'time' : time,
            
            'function' : self.get_pick_data,
            'function2' : self.get_move_data,
	    'total':self._gettotal,

        })
      

      def get_pick_data(self,data):
           date1 = data['form']['from_date'] 
           date2 = data['form']['to_date'] 
           company_id = data['form']['company_id']
           location_id = data['form']['location_id']
           location_dest_id = data['form']['location_dest_id']
           supplier_id = data['form']['supplier_id']
           product_id = data['form']['product_id']
           state = data['form']['state']

           conditions = " and pick.type = 'out'"
           picking = []
           if state :
              conditions = conditions + " and pick.state = '%s' "%state
           else :
              conditions = conditions + " and pick.state NOT IN ('cancel') "
           if company_id :
              conditions = conditions + " and pick.company_id=%s"%company_id[0] 
           if location_id :
              conditions = conditions + " and move.location_id=%s"%location_id[0] 
           if location_dest_id :
              conditions = conditions + " and pick.location_dest_id=%s"%location_dest_id[0] 
           if supplier_id :
              conditions = conditions + " and pick.partner_id=%s"%supplier_id[0] 
           if product_id :
              conditions = conditions + " and move.product_id=%s"%product_id[0]
           self.cr.execute( """
					   select
                                                    distinct pick.id as pick_id,
						    pick.name as name,
						    pick.date as date,
						    s.name as partner
						    From stock_picking pick 
						    left join res_company comp on (pick.company_id=comp.id) 
						    left join res_partner sup on (pick.partner_id=sup.id)
						    left join stock_location loc on (loc.id=pick.location_id)
						    left join stock_move move on (pick.id=move.picking_id)
						    left join product_product pdc on (move.product_id=pdc.id)
						    left join sale_order s on (pick.sale_id=s.id)
						where (to_char(pick.date,'YYYY-mm-dd')>=%s and to_char(pick.date,'YYYY-mm-dd')<=%s) """ + conditions + """
						order by
						    pick.name ,s.name
					""",(date1,date2,)) 
				
           picking = self.cr.dictfetchall()

           return picking

      def get_move_data(self,data,picking_id):
           company_id = data['form']['company_id']
           location_id = data['form']['location_id']
           location_dest_id = data['form']['location_dest_id']
           supplier_id = data['form']['supplier_id']
           product_id = data['form']['product_id']
           state = data['form']['state']
           conditions = " and pick.type = 'out'"
           picking = []
           if state :
              conditions = conditions + " and pick.state in ('%s')"%state
           else :
              conditions = conditions + " and pick.state NOT IN ('cancel') "
           if company_id :
              conditions = conditions + " and pick.company_id=(%s)"%company_id[0] 
           if location_id :
              conditions = conditions + " and pick.location_id=(%s)"%location_id[0] 
           if location_dest_id :
              conditions = conditions + " and pick.location_dest_id=(%s)"%location_dest_id[0] 
           if supplier_id :
              conditions = conditions + " and pick.partner_id=(%s)"%supplier_id[0] 
           if product_id :
              conditions = conditions + " and pdc.id=(%s)"%product_id[0]

           self.cr.execute( """
				select
		                                            pdc.name_template as name ,
							    move.product_qty as qty,
							    move.price_unit as price_unit
							    From stock_move move 
						            left join stock_picking pick on (pick.id=move.picking_id)
						            left join product_product pdc on (pdc.id=move.product_id)
						    	    left join sale_order s on (pick.sale_id=s.id)
							    
							where move.picking_id =%s 
				order by move.name """%picking_id) 
           move = self.cr.dictfetchall()
           return move

      def _gettotal(self,data):
           date1 = data['form']['from_date'] 
           date2 = data['form']['to_date'] 
           company_id = data['form']['company_id']
           location_id = data['form']['location_id']
           location_dest_id = data['form']['location_dest_id']
           supplier_id = data['form']['supplier_id']
           product_id = data['form']['product_id']
           state = data['form']['state']

           conditions = " and pick.type = 'out'"
           picking = []
           if state :
              conditions = conditions + " and pick.state in ('%s')"%state
           else :
              conditions = conditions + " and pick.state NOT IN ('cancel') "
           if company_id :
              conditions = conditions + " and pick.company_id=(%s)"%company_id[0] 
           if location_id :
              conditions = conditions + " and move.location_id=(%s)"%location_id[0] 
           if location_dest_id :
              conditions = conditions + " and pick.location_dest_id=(%s)"%location_dest_id[0] 
           if supplier_id :
              conditions = conditions + " and pick.partner_id=(%s)"%supplier_id[0] 
           if product_id :
              conditions = conditions + " and pdc.id=(%s)"%product_id[0]
           self.cr.execute( """
					   select
                                		    distinct sum (move.product_qty * move.price_unit) as total_price ,
                                 		    sum (move.product_qty) as total_qty 
						    From stock_picking pick 
						    left join res_company comp on (pick.company_id=comp.id) 
						    left join res_partner sup on (pick.partner_id=sup.id)
						    left join stock_location loc on (loc.id=pick.location_id)
						    left join stock_move move on (pick.id=move.picking_id)
						    left join product_product pdc on (move.product_id=pdc.id)
						    left join sale_order s on (pick.sale_id=s.id)
						where (to_char(pick.date,'YYYY-mm-dd')>=%s and to_char(pick.date,'YYYY-mm-dd')<=%s) """ + conditions + """ """,(date1,date2,)) 
				
           res = self.cr.dictfetchall()

           return res
report_sxw.report_sxw('report.cooperative_stock_delivery_orders_report', 'stock.picking', 'addons/stock_co_operative/report/co_operative_delivery_orders.rml' ,parser=stock_cooperative_delivery_orders_report,header=False)
