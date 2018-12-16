# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

import time
from report import report_sxw
from openerp.tools.amount_to_text_en import amount_to_text
from openerp.osv import fields, osv
from openerp.tools.translate import _

class treatment_notifi(report_sxw.rml_parse):

      def __init__(self, cr, uid, name, context):
            super(treatment_notifi, self).__init__(cr, uid, name, context=context)
            self.localcontext.update({
            'time': time,
            'pars':self._pars,
           })
    
      def set_context(self, objects, data, ids, report_type=None,context={}):
          x=0
          for obj in self.pool.get('hr.injury').browse(self.cr, self.uid, ids,context=context):
              x=obj.acc_number 
              if (x==False ):          
		         raise osv.except_osv(_('Error!'), _('You can not print notification. This treatment invoice is not transferred yet!')) 

          return super(treatment_notifi, self).set_context(objects, data, ids, report_type=report_type)

      def _pars(self,u):
 
         res = amount_to_text_ar(u)
         return res
 
report_sxw.report_sxw('report.treatment.notifi', 'hr.injury', 'addons/hr_injury/report/treatment_notifi.rml' ,parser=treatment_notifi ,header=True)
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
