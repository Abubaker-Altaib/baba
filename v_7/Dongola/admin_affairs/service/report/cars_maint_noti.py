#coding: utf-8 
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2016-2017 NCTR (<http://www.nctr.sd>).
#
##############################################################################

import re
import pooler
from osv import fields, osv
import time
from report import report_sxw
from openerp.tools.translate import _


class cars_maint_noti(report_sxw.rml_parse):
    """ To manage cars maintenance notification report """

    def __init__(self, cr, uid, name, context):
        self.uid = uid
        self.cr = cr
        super(cars_maint_noti, self).__init__(cr, uid, name, context)
        self.localcontext.update({
            'time': time,
            'get_user': self.get_user,
        })
        self.context = context
    
    def get_user(self):
        name = self.pool.get('res.users').read(self.cr, self.uid, self.uid, ['name'])
        return name['name']

report_sxw.report_sxw('report.maint_noti', 'fleet.vehicle.log.contract', 'addons/service/report/cars_maint_noti.rml' ,parser=cars_maint_noti , header=False)
