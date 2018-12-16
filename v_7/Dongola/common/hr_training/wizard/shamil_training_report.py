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
class print_shamil_training_report(osv.osv_memory):

    _name = 'shamil.training.report'

    _columns = {
     'department_id': fields.many2many('hr.department','shamil_dep_rel','sh_dep_id','dep_id','Department',required=True), 
     'start_date': fields.date('Start Date',required=True),
     'end_date': fields.date('End Date',required=True),
     'percentage':fields.integer(string="Percentage" ,required=True),
       
    }
    _defaults = {
       
    }

    def positive_percentage(self, cr, uid, ids, context=None):
        for p in self.browse(cr, uid, ids, context=context):
          if p.percentage<0 or p.start_date > p.end_date :
               return False
        return True

    _constraints = [
        (positive_percentage, 'The Percentage  must be more than zero and Start Date must be before the End Date!', ['percentage','start_date']),
    ]

    def print_report(self, cr, uid, ids, data, context=None):
        wiz_data =self.read(cr, uid, ids[0], context={})
        datas = {
            'ids': [],
            'model':'training.approved.by.employee',
            'form':wiz_data
                }

        return {
                    'type': 'ir.actions.report.xml',
                    'report_name':'shamil.training.report',
                    'datas':datas
                     }

print_shamil_training_report()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
