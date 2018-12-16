# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

import time
from report import report_sxw

class contracts_info_report(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(contracts_info_report, self).__init__(cr, uid, name, context)
        self.localcontext.update({
            'time' : time,
            'main' : self._main,
        })
      

    def _main(self,data) :
        result =[]
        clause =" "
        cls =" "
        if data['supplier_ids']: clause += " and c.partner_id in (%s) " % ','.join(map(str, data['supplier_ids']))
        if data['company_ids']: clause += " and c.company_id in (%s) " % ','.join(map(str, data['company_ids']))
        if data['contract_ids']: clause += " and c.id in (%s) " % ','.join(map(str, data['contract_ids']))
        if data['state']: clause += " and c.state = '%s' " % str(data.get('state'))
        if data['picking_policy']: clause += " and c.picking_policy = '%s' " % str(data.get('picking_policy'))
        if data['delivery_method']: clause += " and c.delivery_method = '%s' " % str(data.get('delivery_method'))
        if data['fees_state']: 
            clause += " and fs.state = '%s' " % str(data.get('fees_state'))
            cls  += " and contract_fees.state = '%s' " % str(data.get('fees_state')) 
        self.cr.execute('''SELECT 
			  c.co_operative_type AS type, 
			  c.company_id AS company_id, 
			  c.contract_amount AS amount, 
			  c.end_date AS end_date, 
			  c.start_date AS start_date, 
			  c.contract_title AS title, 
			  c.name AS name, 
			  c.partner_id AS suplier_id, 
			  c.contract_no AS code, 
			  c.id AS contract_id, 
			  ptnr.name AS suplier, 
			  cmpny.name AS company, 
			  c.co_operative_type AS co_oprtv_typ
			FROM 
			  public.purchase_contract c left join public.contract_fees fs on (fs.contract_id = c.id), 
			  public.res_partner ptnr, 
			  public.res_company cmpny
			WHERE 
			  c.company_id = cmpny.id AND
			  ptnr.id = c.partner_id AND
                          c.start_date >= %s AND
                          c.start_date <= %s AND
                          c.contract_purpose = 'co_operative' '''+clause,(data['from_date'],data['to_date']) ) 
        res = self.cr.dictfetchall() 
        if len(res) > 0 :
           for dic in res:
              row={'code': dic['code'] ,
                   'type': dic['type'] ,
                   'name': dic['name'] ,
                   'co_oprtv_typ': dic['co_oprtv_typ'] ,
                   'amount': dic['amount'] ,
                   'title': dic['title'] ,
                   'suplier': dic['suplier'] ,
                   'company': dic['company'] ,
                   'end_date': dic['end_date'] ,
                   'start_date': dic['start_date'] ,}
              self.cr.execute('''SELECT  fees_amount, contract_fees.state, fees_amount_in_euro, fees_date,contract_fees.name, discount_amount
				 FROM contract_fees,purchase_contract
				 WHERE contract_id = purchase_contract.id and contract_id = %s'''%dic['contract_id']+cls ) 
              fees = self.cr.dictfetchall()
              l_fees = []
              if len(fees) > 0 :
                  for fs in fees:
                      l_fees.append({'fees_amount': fs['fees_amount'],'euro': fs['fees_amount_in_euro'],'fees_date': fs['fees_date'],
                                     'state': fs['state'],'discount_amount': fs['discount_amount'],'name': fs['name'],  })
              row['fees']=l_fees
              self.cr.execute('''SELECT contract_shipment.delivery_date,contract_shipment.delivery_method,contract_shipment.id as shipment_id,
                                 total_amount,contract_shipment.name,contract_shipment.state,final_invoice_no as no , product_type
                                 FROM public.purchase_contract,public.contract_shipment 
                                 WHERE purchase_contract.id = contract_id and contract_id = %s'''%dic['contract_id']) 
              shpmnt = self.cr.dictfetchall()
              l_shpmnt = []
              if len(shpmnt) > 0 :
                  for fs in shpmnt:
                      items=[{'item':'','product_qty':'','price_unit':'','uom':'','total':''}]
                      self.cr.execute('''SELECT product_qty,price_unit,name_template, product_uom.name as uom
                                         FROM contract_shipment_line,product_uom, product_product
                                         WHERE product_product.id = contract_shipment_line.product_id AND 
                                         product_uom = product_uom.id AND contract_shipment_id= %s'''%fs['shipment_id']) 
                      itmes_res = self.cr.dictfetchall()
                      if len(itmes_res) >0:
                          items=[]
                          for itm in itmes_res:
                              items.append({'item':itm['name_template'],'product_qty':itm['product_qty'], 'price_unit':itm['price_unit'],
                                            'uom':  itm['uom'],'total':itm['product_qty']*itm['price_unit'],})
                      l_shpmnt.append({'name': fs['name'],'delivery_date': fs['delivery_date'],'delivery_method': fs['delivery_method'],
                                       'total_amount': fs['total_amount'],'state': fs['state'],'no': fs['no'],'product_type': fs['product_type'],
                                        'item':items,})
              row['shpmnt']=l_shpmnt
              result.append(row)
        return result
report_sxw.report_sxw('report.contracts.info', 'purchase.contract','addons/cooperative_purchase/report/contracts_info.rml' ,parser=contracts_info_report,header='internal landscape')
