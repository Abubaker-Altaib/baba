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
  
class purchase_order_stauts(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(purchase_order_stauts, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            'get_data': self.get_data,
            'convert_to_int' : self.convert_to_int,
            #'copy':self.make_copy,
        })
# generate the text of origin and copy
    """def make_copy(self,para):
        return [{'no': 1,'text': 'ORIGINAL'},{'no': 2,'text': 'COPY',}]"""
    def get_data(self,product_qty,line_id):
        condition = ""
        if line_id :
            condition +="where pick.state not in ('cancel') and move.purchase_line_id=%s"%str(line_id)
            
        self.cr.execute( """
             select                        
                                 
                    cast(sum(move.product_qty) as integer) as received_qty
                    
                From stock_move move 
                left join stock_picking pick on (pick.id=move.picking_id)
                                   
    
                                    
                                
                    """ + condition ) 
        res = {}
        res['received_qty'] = self.cr.dictfetchall()
        if res:
           if res['received_qty'][0]['received_qty'] == None:
              res['received_qty'][0]['received_qty'] = '0'
           res['remain_qty'] =  int(product_qty) - int(res['received_qty'][0]['received_qty'])
        return res
    
    
    def convert_to_int(self,num ):
       return int(num)
report_sxw.report_sxw('report.purchase_order_stauts','purchase.order','purchase_customization/report/purchase_order_stauts.rml',parser=purchase_order_stauts,header=False)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
