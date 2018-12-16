# -*- coding: utf-8 -*-
##############################################################################
#    
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.     
#
##############################################################################

import time
from report import report_sxw
from osv import osv
import pooler
from tools.translate import _

class order(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(order, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            'inv': self.invoice,
            'get_stock': self._get_stock,
            'get_discount': self._get_discount,
            'copy':self.make_copy,
            'delivery':self._get_method_of_dispatch,
            'payment':self._get_payment_method,
            'invoice':self._get_final_invoice,
            'incoterm':self._get_incoterm,

        })
        self.context = context

    def set_context(self, objects, data, ids, report_type=None):
        for obj in self.pool.get('purchase.order').browse(self.cr, self.uid, ids, self.context):
            if obj.purchase_type != 'foreign':
		            raise osv.except_osv(_('Error!'), _('You can not print this report, because this is internal purchase')) 

        return super(order, self).set_context(objects, data, ids, report_type=report_type) 

    def make_copy(self,para):
        res1 = {}
        res = {}
        hi_list = []
        res = {'no': 1,
               'text': 'ORIGINAL',
              }
        res1 = {'no': 2,
               'text': 'COPY',
              }
        hi_list.append(res)
        hi_list.append(res1)
        return hi_list


    def invoice(self, order_obj):
        res = {}
        if order_obj.ir_id.id :
            self.cr.execute("SELECT name FROM pur_quote WHERE pq_ir_ref=%s and state='done'", (order_obj.ir_id.id,))
            res = self.cr.dictfetchall()
            return res[0]['name']
        return res


    def _get_stock(self,stock_id):
        self.cr.execute("""select name  as stock_name from stock_location where id =%s"""%(stock_id))
        res = self.cr.dictfetchall()
        return res 

    def _get_discount(self,order):
        if order.ir_id:
            self.cr.execute("""select discount  as dis from pur_quote where pq_ir_ref =%s and state='done'"""%(order.ir_id.id))
        else:
            if order.contract_id.contract_type == 'direct':
                self.cr.execute("""select discount  as dis from purchase_contract where id =%s """%(order.contract_id.id))
            else :
                self.cr.execute("""select discount  as dis from contract_shipment where contract_id =%s and name = '%s' """%(order.contract_id.id,order.origin))
        res = self.cr.dictfetchall()
        return res 
     
    def _get_method_of_dispatch(self,order):
        if order.ir_id:
            self.cr.execute("""select delivery_method as delivery from pur_quote where pq_ir_ref =%s and state='done'"""%(order.ir_id.id))
        else:
            if order.contract_id.contract_type == 'direct':
                self.cr.execute("""select delivery_method as delivery from purchase_contract where id =%s """%(order.contract_id.id))
            else :
                self.cr.execute("""select delivery_method as delivery from contract_shipment where contract_id =%s and name = '%s' """%(order.contract_id.id,order.origin))
        res = self.cr.dictfetchall()
        return res

    def _get_payment_method(self,order):
        res = {}
        if order.ir_id :
            self.cr.execute("""select payment_method as payment from pur_quote where pq_ir_ref =%s and state='done'"""%(order.ir_id.id))
            res = self.cr.dictfetchall()
        return res


    def _get_final_invoice(self,order):
        if order.ir_id :
            self.cr.execute("""select q_no as no from pur_quote where pq_ir_ref =%s and state='done'"""%(order.ir_id.id))
        else:
            if order.contract_type == 'open':
                self.cr.execute("""select final_invoice_no as no from contract_shipment where contract_id =%s and name = '%s' """%(order.contract_id.id,order.origin))
        res = self.cr.dictfetchall()
        return res

    def _get_incoterm(self,order):
        res ={'na':''}
        if order.ir_id :
            self.cr.execute("""select name as na from stock_incoterms where id =(select incoterm as inco from pur_quote where pq_ir_ref =%s and state='done')"""%(order.ir_id.id))
            res = self.cr.dictfetchall()
        return res


report_sxw.report_sxw('report.purchase_order_foregin_order','purchase.order','purchase_foreign/report/order.rml',parser=order,header=False)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

