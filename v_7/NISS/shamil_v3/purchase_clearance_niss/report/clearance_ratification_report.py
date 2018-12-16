# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################
import time
from report import report_sxw
from osv import osv
import pooler
from tools.translate import _
from openerp.tools.amount_to_text_en import amount_to_text
from base_custom.amount_to_text_ar import amount_to_text as amount_to_text_ar


class clearance_ratification_report(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(clearance_ratification_report, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            'get_amount_written' : self.convert,
            
        })

    def set_context(self, objects, data, ids, report_type=None):
        for obj in self.pool.get('purchase.clearance').browse(self.cr, self.uid, ids):
            if obj.state != 'confirmed' :
                raise osv.except_osv(_('Error!'), _('You can only print the order in confirmed state')) 
            if not obj.account_voucher_ids :
                raise osv.except_osv(_('Bad Action!'), _('Sorry Account Voucher doesnt created yet'))

        return super(clearance_ratification_report, self).set_context(objects, data, ids, report_type=report_type) 
   

    def convert(self, amount_total):
        return amount_to_text_ar(amount_total)
    
    
    


report_sxw.report_sxw('report.clearance_ratification_report', 'purchase.clearance', 'purchase_clearance_niss/report/clearance_ratification_report.rml', parser=clearance_ratification_report,header=False)

