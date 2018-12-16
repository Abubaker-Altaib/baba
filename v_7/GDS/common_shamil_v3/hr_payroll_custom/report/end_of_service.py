# -*- coding: utf-8 -*-
##############################################################################
#    
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.     
#
##############################################################################

import time
from openerp.report import report_sxw
from osv import orm
from openerp import pooler
from tools.translate import _

class end_of_service(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context=None):          
        if context is None:
           context = {}
        super(end_of_service, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            'amount':self._amount,
        })
        self.context = context

    def set_context(self, objects, data, ids, report_type=None):
        '''for obj in objects:
            if not obj.dismissal_type.allowance_ids :
                raise orm.except_orm(_('Warning!'), _("You cannot print this report , %s doesn't have allowances")%(obj.dismissal_type.name))
            if obj.state not in ('calculate','transfer'):
                raise orm.except_orm(_('Warning!'), _("You cannot print this report allowances not calculated yet"))'''
        return super(end_of_service, self).set_context(objects, data, ids, report_type=report_type)
 
    def _amount(self,o):
        amount=0.0
        for allwo in o.allowance_ids:
            amount+=allwo.amount
        return amount
        
report_sxw.report_sxw('report.end_of_service','hr.employment.termination','addons/hr_payroll_custom/report/end_of_service.rml',parser=end_of_service)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

