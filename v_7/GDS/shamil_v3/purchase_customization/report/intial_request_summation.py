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

class intial_request_summation(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(intial_request_summation, self).__init__(cr, uid, name, context=context)
        
        self.localcontext.update({
            'time': time,
            'function' : self.get_data,
            'convert_to_int' : self.convert_to_int,
        })
    



    

    

    def get_data(self,data):
           res={}
           request_ids = data['form']['request_ids']
           condition = ""
           if len(request_ids) == 1:
                condition = " where ir.id in (%s)"%request_ids[0]
           else:
                request_ids = tuple(request_ids)
                condition = " where ir.id in %s"%str(request_ids) 
           self.cr.execute( """
                                    select                        
                                                             distinct pdc.name as product_name,
                                                             pd.default_code as default_code,
                                                             cast(sum(ir_prod.product_qty) as integer) as product_qty,
                                                             uom.name as uom
                                                     
                      
                                                    From ireq_m ir 
                                                    left join ireq_products ir_prod on (ir_prod.pr_rq_id=ir.id)
                                                    left join product_template pdc on (ir_prod.product_id=pdc.id)
                                                    left join product_product pd on (pd.id=pdc.id)
                                                    left join product_uom uom on (ir_prod.product_uom= uom.id)


                                                    
                                                 """ + condition  + """ group by pd.default_code ,pdc.name ,uom.name   """)
             
           res['items'] = self.cr.dictfetchall()
           self.cr.execute( """  
                               select distinct dept.id ,dept.name as department , string_agg(ir.name , ' - ' ) as orders, string_agg(ir.purchase_purposes , ' + ' ) as purposes
                                      from ireq_m ir
                                          left join hr_department dept on (ir.department_id = dept.id)
                                          """ + condition + """ group by dept.id   """ )
           res['other_info'] = self.cr.dictfetchall()
           return res




     
    
    def convert_to_int(self,num ):
       return int(num)

    
report_sxw.report_sxw('report.intial_request_summation','ireq.m','purchase_customization/report/intial_request_summation.rml',parser=intial_request_summation,header=False)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
