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


class final_accomplishment(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(final_accomplishment, self).__init__(cr, uid, name, context)
        self.localcontext.update({
            'time': time,
        })
        self.context = context

    def set_context(self, objects, data, ids, report_type=None):
        for obj in self.pool.get('building.maintenance').browse(self.cr, self.uid, ids, self.context):
            if time.strftime('%Y-%m-%d') < obj.warranty_end_date or obj.state!='done':
		            raise osv.except_osv(_('Error!'), _('You can not print this notification, The Date To Warranty End Not Come yet!')) 


        return super(final_accomplishment, self).set_context(objects, data, ids, report_type=report_type) 


report_sxw.report_sxw('report.final_accomplishment', 'building.maintenance', 'addons/building_management/report/final_accomplishment.rml' ,parser=final_accomplishment , header=False)
