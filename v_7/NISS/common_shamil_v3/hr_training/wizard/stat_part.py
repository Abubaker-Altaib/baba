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

from osv import osv, fields
from tools.translate import _
import time
from datetime import datetime



class print_stat_part(osv.osv_memory):

    


    _name = 'stat.part'

    _columns = {
        'from':fields.date('From Date', required=True),
        'to':fields.date('To Date', required=True),
      
    }

    def check_dates(self, cr, uid, ids, context=None):
         exp = self.read(cr, uid, ids[0], ['from', 'to'])
         if exp['from'] and exp['to']:
             if exp['from'] > exp['to']:
                 return False
         return True

    _constraints = [
        (check_dates, _('The start date must be before the end date!'), []),
    ]

    def print_report(self, cr, uid, ids, context=None):
        datas = {}
        if context is None:
            context = {}
        data = self.read(cr, uid, ids)[0]
        datas = {
             'ids': context.get('active_ids', []),
             'model': 'hr.employee.training',
             'form': data
                }
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'stat_report',
            'datas': datas,
            }
        



# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
