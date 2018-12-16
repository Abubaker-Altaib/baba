# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2011-2013 Serpent Consulting Services (<http://www.serpentcs.com>)
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
############################################################################

import time
from datetime import datetime
from dateutil import relativedelta

from openerp.osv import fields, osv, orm

class payroll_taxes(osv.osv_memory):

    def _get_months(self, cr, uid, context):
        months=[(n, n) for n in range(1, 13)]
        return months  
     
    _name = 'payroll.taxes'
    _description = 'info about the taxes of employees'
    _columns = {
       	        'scale_ids': fields.many2many('hr.salary.scale','tax_scale_rel','parent_id','child_id', 'Salary Scale',required=True),
       	        'company_ids': fields.many2many('res.company','tax_com_rel','tax_id','com_id', 'Company',required=True),		
        	    'year' :fields.integer("Year" ,), 
                'month' :fields.selection(_get_months,"Month"), 
                'process':fields.selection([('monthly','Monthly Tax'),('candidate','Exemption Candidates'),('exempted','Tax Exempted           ')],"Process",required=True),
               }

   
    def _get_companies(self, cr, uid, context=None): 
   
        return [self.pool.get('res.users').browse(cr,uid,uid).company_id.id]

    _defaults ={
               'year': int(time.strftime('%Y')),
               'company_ids': _get_companies,
                }
    def print_report(self, cr, uid, ids, context={}):
        data = self.read(cr, uid, ids, [], context=context)[0]
        datas = {
             'ids': [],
             'model': 'hr.employee',
             'form': data
               }
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'payroll.taxes.webkit',
            'datas': datas,
              }

        return 


payroll_taxes()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
