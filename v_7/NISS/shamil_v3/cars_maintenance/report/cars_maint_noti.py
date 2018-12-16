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
from openerp.tools.translate import _


class cars_maint_noti(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(cars_maint_noti, self).__init__(cr, uid, name, context)
        self.localcontext.update({
            'time': time,
        })
        self.context = context

    """    def set_context(self, objects, data, ids, report_type=None):
        for obj in self.pool.get('car.maintenance.request').browse(self.cr, self.uid, ids, self.context):
            if obj.state != 'check':
		            raise osv.except_osv(_('Error!'), _('You can not print this notification, This request already been printed or not approved yet!')) 
        return super(cars_maint_noti, self).set_context(objects, data, ids, report_type=report_type)"""


report_sxw.report_sxw('report.cars_maint_noti', 'car.maintenance.request', 'addons/cars_maintenance/report/cars_maint_noti.rml' ,parser=cars_maint_noti , header=False)
