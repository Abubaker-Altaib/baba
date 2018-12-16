# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

#--------------------------------------------------------------
# class to customising purchase order report 
#--------------------------------------------------------------
import time
from report import report_sxw
import pooler
  
class partial_picking_report(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(partial_picking_report, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            'inv': self.invoice,
            'function' : self.get_move_data,
            'convert_to_int' : self.convert_to_int,

        })

     
    def invoice(self, order_obj):
        self.pool.get('purchase.order').write(self.cr, self.uid,order_obj.id,{'test_report_print':'printed'})
        pur_inv = [x.id for x in order_obj.invoice_ids]
        invoices=''
        for inv_id in pur_inv:
            inv_ref = self.pool.get('account.invoice').browse(self.cr, self.uid, inv_id).number
            invoices = invoices + '\n' +inv_ref
        return invoices


    def get_move_data(self,data):


           conditions = " pick.type = 'in'"           
           picking_id = data['form']['picking_id']
           if picking_id :
              conditions = conditions + " and pick.id=(%s)"%picking_id[0]
          
           self.cr.execute( """
				select                        
		                        move.name as name ,
                                pdc.default_code as no,
                                uom.name as product_uom,
							    move.product_qty as qty,
							    move.price_unit as price_unit
							    From stock_move move 
						        left join stock_picking pick on (pick.id=move.picking_id)
                                left join res_company comp on (pick.company_id=comp.id)
							    left join purchase_order po on (pick.purchase_id=po.id) 
							    left join hr_department dep on (po.department_id=dep.id)
							    left join stock_location loc on (loc.id=pick.location_dest_id)
							    left join product_product pdc on (move.product_id=pdc.id)
                                left join product_template p_temp on (pdc.product_tmpl_id = p_temp.id)
                                left join product_uom uom on (uom.id = p_temp.uom_id)
							    left join product_category catg on (p_temp.categ_id=catg.id)

							     where    
							
		        """ + conditions ) 
           move = self.cr.dictfetchall()
           return move

    def convert_to_int(self,num ):
       return int(num)

report_sxw.report_sxw('report.create_partial_picking_report','purchase.order','addons/purchase_customization/report/partial_purchase_order_report.rml',parser=partial_picking_report,header=False)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
