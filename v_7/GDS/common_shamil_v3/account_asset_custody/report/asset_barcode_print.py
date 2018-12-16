# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################


import time
import pooler
#import rml_parse
import copy
from report import report_sxw
import pdb
import re
from osv import fields, osv
from openerp.tools.translate import _

class report_print_barcode(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(report_print_barcode, self).__init__(cr, uid, name, context)
        self.localcontext.update({
            'time': time,
        })
        self.context = context

    def set_context(self, objects, data, ids, report_type=None):
        da = {}
        da = self.pool.get('account.asset.asset').browse(self.cr, self.uid, ids) #[o.payment_id for o in objects]
        for serial in da:
            if serial.serial_no == False :
	           raise osv.except_osv(_('Warning'),_('There is no serial for this asset ')) 
            
        return super(report_print_barcode, self).set_context(objects, data, ids, report_type=report_type)
  
report_sxw.report_sxw('report.asset.print.barcode', 'account.asset.asset', 
                      'account_asset_custody/report/asset_barcode_print.rml',
                      parser=report_print_barcode,header='internal')

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
