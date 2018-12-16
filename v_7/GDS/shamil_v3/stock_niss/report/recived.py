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
from tools.translate import _
  
class recived(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(recived, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            'inv': self.invoice,
            'line2':self._getdata
            #'copy':self.make_copy,
        })
# generate the text of origin and copy
    """def make_copy(self,para):
        return [{'no': 1,'text': 'ORIGINAL'},{'no': 2,'text': 'COPY',}]"""
    def _getdata(self,pick):
        self.cr.execute("""
               select
                    (pr.name_template) as product_name,
                    (pr.default_code) as default_code,
                    (sm.product_qty) as quantity,
                    (u.name) as product_uom,
                    (ol.price_unit) as price_unit,
                    (pa.lang) as lang,
                    (pa.name) as partner_name

                    from stock_move sm
                    left join stock_picking sp on (sm.picking_id=sp.id and sm.state='done')
                    left join purchase_order po on (sp.purchase_id=po.id)
                    left join purchase_order_line ol on (po.id = ol.order_id and sm.product_id =ol.product_id)
                    left join product_uom u on (u.id = ol.product_uom)
                    left join product_product pr on (sm.product_id =pr.id)
                    left join res_partner pa on (po.partner_id =pa.id)
                   
                     where sp.id =%s
                  order by sm.id
        """%(pick,)) 

        res = self.cr.dictfetchall()
        return res
    def invoice(self, order_obj):
        self.pool.get('stock.picking').write(self.cr, self.uid,order_obj.id,{'test_report_print':'printed'})
        pur_inv = [x.id for x in order_obj.invoice_ids]
        invoices=''
        for inv_id in pur_inv:
            inv_ref = self.pool.get('account.invoice').browse(self.cr, self.uid, inv_id).number
            invoices = invoices + '\n' +inv_ref
        return invoices
    
report_sxw.report_sxw('report.recived','stock.picking','addons/stock_niss/report/recived.rml',parser=recived,header=False)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
