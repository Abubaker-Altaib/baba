#coding: utf-8 
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2016-2017 NCTR (<http://www.nctr.sd>).
#
##############################################################################

import time
from report import report_sxw
from datetime import datetime


class purchase_requisition_order_report(report_sxw.rml_parse):
    """ To manage purchase requisition report """
    globals()['total_amount']=0.0

    def __init__(self, cr, uid, name, context):
        super(purchase_requisition_order_report, self).__init__(cr, uid, name, context)
        self.localcontext.update({
            'time': time,
            'line':self._getdata,
            'total':self._gettotal,
        })

    def _getdata(self,data):
        """
        Function finds purchase requisition  report data.
 
        @return: List of dictionary to  purchase requisition report data
        """
        requis_obj = self.pool.get('purchase.requisition')
        partner_obj= self.pool.get('res.partner')
        date_from= data['form']['date_from']
        date_to= data['form']['date_to']
        category_id = data['form']['category_id']
        department_id = data['form']['department_id']
        partner_id = data['form']['partner_id']
        start_date = datetime.strptime(str(date_from), "%Y-%m-%d").date()
        end_date = datetime.strptime(str(date_to), "%Y-%m-%d").date()

        globals()['total_amount']=0.0
        
        insurer_id = []
        req_domain=[]
        order_state = ["approved", "done", "except_picking", "except_invoice"]
        if department_id:
            req_domain +=[('department_id','=',department_id[0])]
        if category_id :
            req_domain +=[('category_id','=',category_id)]
        part_ids = partner_obj.search(self.cr, self.uid, [])
        insurer_id = partner_id or [par.id for par in partner_obj.browse(self.cr, self.uid, part_ids)]
        requisition_ids = requis_obj.search(self.cr, self.uid, req_domain)
        requisition = []
 
        for req in requis_obj.browse(self.cr, self.uid, requisition_ids):
            req_order =[]
            start = datetime.strptime(str(req.date_start), "%Y-%m-%d %H:%M:%S").date()
            #end = datetime.strptime(str(req.date_end), "%Y-%m-%d %H:%M:%S").date()
            if ((start >= start_date) and (start <= end_date) ):
                for order in req.purchase_ids:
                    if (order.state in order_state) and (order.partner_id.id in insurer_id):
                        globals()['total_amount'] += order.amount_total
                        req_order.append({  
                            'order_date': order.date_order,
                            'partner': order.partner_id.name,
                            'amount': order.amount_total,
                            'state': order.state,
                            'req_id': req.id,
                            })
                if req_order :  
                    requisition.append({  
                                'req_no': req.name,
                                'desired': req.category_id.name,
                                'department': req.department_id.name,
                                'req_date': start,
                                'order_line': req_order,
                                'req_id': req.id,
                                })
        return requisition

    def _gettotal(self,data):
        """
        Function finds the total amount to requisition order .

        @return: value of total amount
        """
        return globals()['total_amount']
               
report_sxw.report_sxw('report.purchase.requisition.order', 'purchase.requisition', 'addons/purchase_wafi/report/purchase_requisition_order_report.rml' ,parser=purchase_requisition_order_report,header='internal landscape')

