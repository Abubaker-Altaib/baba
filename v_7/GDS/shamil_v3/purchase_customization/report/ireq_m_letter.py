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
from openerp.tools.translate import _

class ireq_m_letter(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(ireq_m_letter, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            'convert_to_int' : self.convert_to_int,
            'get_amount' : self.get_partner_total_amount,
            'get_data' :  self.get_partner_invoice_detial,

        })
        self.context = context
    def set_context(self, objects, data, ids, report_type=None):
        for record in self.pool.get('ireq.m').browse(self.cr, self.uid, ids, self.context):
		if not record.q_ids :
			raise osv.except_osv(_('Error!'), _('You can not print this report, Unitl You insert and confirmed Quote!'))  
        	#for record_quote in record.q_ids:
            		#if record_quote.state != 'done':
		            #raise osv.except_osv(_('Error!'), _('You can not print this report,because quotation is not confirmed yet!')) 
        return super(ireq_m_letter, self).set_context(objects, data, ids, report_type=report_type)
    
    
    
    def get_partner_total_amount(self,quotes):
        res = {}
        quote_ids = []
        if quotes :
            for rec in quotes:
                quote_ids.append(rec.id)
            condition = ""
            if len(quotes) == 1:
               condition += " and quote.id in (%s)"%quote_ids[0]
            else :    
               request_quote_ids = tuple(quote_ids)
               condition += "and quote.id in %s"%str(request_quote_ids)

            self.cr.execute( """ select part.name as partner,
                                            curr.name as currency,
                                            quote.amount_total as total
                                            
                                           from pur_quote quote 
                                           left join res_partner part on (quote.supplier_id = part.id)
                                           left join res_currency curr on (quote.currency_id = curr.id)
                                           
                                           where quote.state = 'done' """ + condition ) 
            res = self.cr.dictfetchall()
            amount = 0.0
            for rec in res:
                amount += rec['total']
            res.append({'total_amount' : amount })
           

        return res
    
        
        
        
        
    def get_partner_invoice_detial(self,quotes,product):
        res = {}
        quote_ids = []
        if quotes :
            for rec in quotes:
                quote_ids.append(rec.id)
            condition = ""
            condition += "and line.product_id = %s"%str(product)
            if len(quotes) == 1:
               condition += " and quote.id in (%s)"%quote_ids[0]
            else :    
               request_quote_ids = tuple(quote_ids)
               condition += "and quote.id in %s"%str(request_quote_ids)
        self.cr.execute( """ select distinct quote.id,
                                    part.name as partner,
                                    line.product_qty as qty,
                                    line.price_unit as price_unit,
                                    line.price_subtotal as price_subtotal,
                                    uom.name as uom ,
                                    curr.name as currency,
                                    line.chosen as chosen
                                    
                                    from pq_products line
                                    left join pur_quote quote on (quote.id = line.pr_pq_id)
                                    left join ireq_m ir on ( ir.id = quote.pq_ir_ref)
                                    left join ireq_products ir_p on (ir.id = ir_p.pr_rq_id)
                                    left join product_template prod on (prod.id = line.product_id)
                                    left join product_uom uom on (prod.uom_id = uom.id)
                                    left join res_partner part on (quote.supplier_id = part.id)
                                    left join res_currency curr on (quote.currency_id = curr.id)
                                   
                                   where line.price_unit > 0""" + condition ) 
        res = self.cr.dictfetchall()
        return res
        
        
        
                                     
    def convert_to_int(self,num ):
        return int(num)

report_sxw.report_sxw('report.ireq_m_letter_custom','ireq.m','../purchase_customization/report/ireq_m_letter.rml',parser=ireq_m_letter,header=False)

