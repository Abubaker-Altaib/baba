import time
from report import report_sxw
from datetime import timedelta,date
import re
import pooler
from report import report_sxw
#import wizard
from openerp.osv import fields, osv
from openerp.tools.translate import _

class ticket_booking_noti(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(ticket_booking_noti, self).__init__(cr, uid, name, context)
        self.localcontext.update({
           'time': time,
           'line':self._getdata,
        })
        self.context = context

    def set_context(self, objects, data, ids, report_type=None):
        for obj in self.pool.get('ticket.booking').browse(self.cr, self.uid, ids, self.context):
            if obj.state != 'cancel':
		            raise osv.except_osv(_('Error!'), _('You can not print this notification, the ticket is not cancelled!')) 

        return super(ticket_booking_noti, self).set_context(objects, data, ids, report_type=report_type) 

    def _getdata(self,request_id):
        self.cr.execute(''' select v.number as vou_number  from account_voucher v 
            left join ticket_voucher t on (t.voucher_id = v.id) where t.ticket_id= %s'''%request_id)
        res=self.cr.dictfetchall()
        return res
                
        
 
report_sxw.report_sxw('report.ticket_booking_noti', 'ticket.booking', 'addons/public_relation/report/ticket_booking_noti.rml' ,parser=ticket_booking_noti ,header=False)
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
