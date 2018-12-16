# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

from report import report_sxw

class report_print_check(report_sxw.rml_parse):
    
    def __init__(self, cr, uid, name, context):
        self.context = context
        super(report_print_check, self).__init__(cr, uid, name, context=context)

    def set_context(self, objects, data, ids, report_type=None):
        objects = [o.payment_id for o in objects]
        return super(report_print_check, self).set_context(objects, data, ids, report_type=report_type)
  
report_sxw.report_sxw('report.account.print.check', 'account.check.print.wizard', 
                      'addons/account_check_writing_custom/report/check_print.rml',
                      parser=report_print_check,header=False)


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
