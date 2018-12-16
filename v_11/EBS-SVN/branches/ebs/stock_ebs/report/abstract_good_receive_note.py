from datetime import timedelta
from odoo import api, fields, models, _
from datetime import datetime
from decimal import Decimal

class GoodReceiveNote(models.AbstractModel):
  _name = 'report.stock_ebs.good_receive_note_report'
  @api.model
  def get_report_values(self, docids, data):

    current_id = data['context']['active_id']
    current_stock_pcking=self.env['stock.picking'].search([('id','=',current_id)])
    purchase_order = self.env['purchase.order'].search([('name','=',current_stock_pcking.origin)])

    purchase_lines = purchase_order.order_line
    prices=[]
    for line in purchase_lines :
      prices.append(line.price_unit)

    products_prices=prices[::-1]

    docargs = {
            'doc_ids': self.ids,
            'purchase_order':purchase_order,
            'stock_pcking':current_stock_pcking,
            'prices':products_prices
           }   
    return  docargs
    

    