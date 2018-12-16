import datetime
import time

from openerp.osv import fields, osv
from openerp.report.interface import report_rml
from openerp.report.interface import toxml

from openerp import pooler
import time
from openerp.report import report_sxw
from openerp.tools import ustr
from openerp.tools.translate import _
from openerp.tools import to_xml


class sickness_form(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(sickness_form, self).__init__(cr, uid, name, context)
        self.localcontext.update({
            'count':self._count,
                          
        })

    def _count(self):
        c = [{1:'1'},{2:'2'}]
        return c


report_sxw.report_sxw('report.sickness_form', 'hr.employee', 'hr_holidays_custom/report/sickness_form_2.rml' ,parser=sickness_form ,header=True)
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
