# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

from osv import fields, osv

class purchase_order_request(osv.osv_memory):
    _name = "purchase.order.request"
    _description = "Purchase Order and Requistion"

    request_status = [
             ('draft', 'مبدئي'),
             ('confirmed_d','في انتظار تصديق قسم المشتريات '),
             ('confirmed','في انتظار  انشاء الفواتير'),
             ('approve1' , 'في انتظار تصديق المدير العام'),
             ('wait_confirmed','في انتظار تصديق ادارة الشئون الإداريه'),
             ('wait_budget','في انتظار الموازنه'),
             ('done','تم'),
             ('cancel', 'ملغي'),
             ('checked','في انتظار تصديق المدير الإداري/الفني'),
             ('approve3' , 'في انتظار انشاء امر الشراء') ,
             
         ]



    order_stauts = [  ('done' , 'تم') ,
                      ('approved' , 'في انتظار الاستلام في المخزن') ,
                      ('draft' , 'مبدئي') ,
                      ('sign' , 'موقع من المشتريات') ,
                      ('except_picking' , 'تم الغاء الاستلام من المخزن') ,
                      ('except_invoice' , 'تم الغاء الفاتورة') ,
                      ]
    _columns = {
        'Date_from': fields.date('Date From', required=True,), 
        'Date_to': fields.date('Date To', required=True),
        'purchase_type': fields.selection([('internal','Internal'),('foreign','foreign')], 'Type', select=True , required=True), 
        'purchase_kind': fields.selection([('request','Request'),('order','Order')], 'Kind', select=True, required=True), 
        'department_id' : fields.many2one('hr.department','Department' ),
        'request_state' : fields.selection(request_status ,'Request Status',select=True),
        'order_state' : fields.selection(order_stauts ,'Order Status',select=True),
    }

    def print_report(self, cr, uid, ids, context=None):
        data = self.read(cr, uid, ids, [], context=context)[0]
        datas = {
             'ids': [],
             'model': 'purchase.order',
             'form': data,
            }
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'purchase_order_request_report',
            'datas': datas,
            }
purchase_order_request()
    
