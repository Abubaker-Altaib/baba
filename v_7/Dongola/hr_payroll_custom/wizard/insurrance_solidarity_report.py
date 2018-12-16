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

class insurrance_solidarity_report(osv.osv_memory):

    def _get_months(self, cr, uid, context):
        months=[(n, n) for n in range(1, 13)]
        return months   
   
    _name = 'insurrance.solidarity'
    _description = 'info about the paid amout of health insurannce or solidarity'
    _columns = {
       	        'scale_ids': fields.many2many('hr.salary.scale','soli_scale_rel','parent_id','child_id', 'Salary Scale',required=True),
       	        'company_ids': fields.many2many('res.company','soli_com_rel','soli_id','com_id', 'Company',required=True),		
        	    'year' :fields.integer("Year" ,required=True), 
                'month' :fields.selection(_get_months,"Month",required=True), 
                'soli_insu_id':fields.many2one('hr.allowance.deduction', 'Insurance / solidarity',required=True,domain="[('name_type','=','deduct')]"),
       	        'dept_ids': fields.many2many('hr.department','soli_dept_rel','soli_id','dept_id', 'Departmet',required=False),	
        	    'factor' :fields.float("Factor" ,required=True), 
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
             'model': 'hr.payroll.main.archive',
             'form': data
               }
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'insurrance.solidarity.webkit',
            'datas': datas,
              }

        return 


insurrance_solidarity_report()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
