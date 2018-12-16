# -*- coding: utf-8 -*-
##############################################################################
#
# NCTR, Nile Center for Technology Research
# Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

import time
import re
import pooler
from report import report_sxw
import calendar
import datetime
from osv import fields, osv
from tools.translate import _

class examine_and_receive_form2_reports(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(examine_and_receive_form2_reports, self).__init__(cr, uid, name, context)
        self.localcontext.update({
           'time': time,
           'line':self._getShop,
             
        })
 
    def set_context(self, objects, data, ids, report_type=None):         
        return super(examine_and_receive_form2_reports, self).set_context(objects, data, ids, report_type=report_type)

    def _getShop(self,ids):
        p = pooler.get_pool(self.cr.dbname).get('stock.picking')
        pick_id=p.browse(self.cr, self.uid,[ids['id']])[0]
        picking_id = pick_id.id

        pur = pick_id.purchase_id.id
        if not pur:
            raise osv.except_osv(_('Warning !'),_('No purchase order selected.'))
        return True
     
report_sxw.report_sxw('report.examine.and.receive.form.reports', 'stock.picking', 'addons/stock_quality/report/exminer.rml' ,parser=examine_and_receive_form2_reports )
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

