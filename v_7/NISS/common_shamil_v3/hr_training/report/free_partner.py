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
from openerp import pooler
import copy
import pdb
import re
from openerp.tools.translate import _
from openerp.osv import fields, osv, orm


class free_partner(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(free_partner, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({'time': time})
        self.context = context

    def set_context(self, objects, data, ids, report_type=None):
        	for obj in self.pool.get('hr.employee.training.approved').browse(self.cr, self.uid, ids, self.context):
           		c=obj.state
        		if (c not in ['approved','done']):
        			raise osv.except_osv(_('Error!'), _('You can not print ..This report available only if state is done or approved!'))
        	return super(free_partner, self).set_context(objects, data, ids ,report_type=report_type)
report_sxw.report_sxw('report.free_partner','hr.employee.training.approved','addons/hr_training/report/free_partner.rml',parser=free_partner)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

