#coding: utf-8 
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

import re
import pooler
from osv import fields, osv
import time
from report import report_sxw
from tools.translate import _


class office_visit(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(office_visit, self).__init__(cr, uid, name, context)
        self.localcontext.update({
            'time': time,
        })
        self.context = context

    def set_context(self, objects, data, ids, report_type=None):
        for obj in self.pool.get('exchange.order').browse(self.cr, self.uid, ids, self.context):
            if obj.state !='category_manager':
		            raise osv.except_osv(_('Error!'), _('You can not print this notification, This request already been printed or not approved yet!'))
        return super(office_visit, self).set_context(objects, data, ids, report_type=report_type)


report_sxw.report_sxw('report.office_visit', 'exchange.order', 'addons/stock_exchange_NISS/report/office_visit.rml' ,parser=office_visit , header=True)
