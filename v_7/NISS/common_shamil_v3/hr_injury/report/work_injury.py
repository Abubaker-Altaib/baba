# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

import time
from report import report_sxw
from openerp.osv import fields, osv
from openerp.tools.translate import _

class work_injury(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(work_injury, self).__init__(cr, uid, name, context)
        self.localcontext.update({
            'time': time,            
            
        })
    
report_sxw.report_sxw('report.work.injury', 'hr.injury', 'addons/hr_injury/report/work_injury.rml' ,parser=work_injury)
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

