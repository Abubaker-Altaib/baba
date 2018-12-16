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

from osv import fields, osv
from tools.translate import _

class hr_action_reason(osv.osv):
    _inherit = "hr.action.reason"
    _columns = {
        'action_type': fields.selection([('sign_in', 'Sign in'), ('sign_out', 'Sign out')], "Action's type"),
}

class hr_attendance(osv.osv):

    def _day_compute(self, cr, uid, ids, fieldnames, args, context=None):
        res = super(hr_attendance, self)._day_compute(cr, uid, ids, fieldnames, args, context)
        return res
    def _get_emp(self, cr, uid, ids, fieldnames, args, context=None):
        res = {}
        emp_code = self.read(cr, uid, ids[0],['employee_id'], context=context )
        emp_code = emp_code['employee_id']
        emp_id = self.pool.get('hr.employee').search(cr, uid, [('emp_code','=',emp_code)], context=context )
        res[ids[0]] = emp_id and emp_id[0] or 0
        return res
        

    _inherit = "hr.attendance"
    _columns = {
        'name': fields.datetime('Date', required=True, select=1,readonly=True),
        'action': fields.selection([('sign_in', 'Sign In'), ('sign_out', 'Sign Out'), ('action','Action')], 'Action', required=True,readonly=False),
        'employee_id': fields.integer("Employee's Code", required=True, readonly=True),
        'day': fields.function(_day_compute, method=True, type='char', string='Day', store=True, select=1, size=32),
        'emp_id': fields.many2one('hr.employee', "Employee", select=True),
    }

    def fields_view_get(self, cr, uid, view_id=None, view_type='tree', context=None, toolbar=False, submenu=False):
        """ Returns views and fields for current model.
        @param cr: A database cursor
        @param user: ID of the user currently logged in
        @param view_id: list of fields, which required to read signatures
        @param view_type: defines a view type. it can be one of (form, tree, graph, calender, gantt, search, mdx)
        @param context: context arguments, like lang, time zone
        @param toolbar: contains a list of reports, wizards, and links related to current model

        @return: Returns a dictionary that contains definition for fields, views, and toolbars
        """
        if not context:
            context = {}

        emp_code_ids = self.search(cr, uid,[('emp_id','=',False)], context=context )
        if emp_code_ids:
            attendance = self.browse(cr, uid, emp_code_ids, context=context)

            emp_obj = self.pool.get('hr.employee')
            emp_ids = emp_obj.search(cr, uid, [], context=context )
            emp_basic = emp_obj.read(cr, uid, emp_ids,['emp_code'], context=context)
            
            emp_basic = {int(x['emp_code']):int(x['id']) for x in emp_basic}
            for x in attendance:
                new_id = x.employee_id in emp_basic and emp_basic[x.employee_id]
                if new_id:
                    x.write({'emp_id':new_id})
        




        res = super(hr_attendance, self).fields_view_get(cr, uid, view_id=view_id, view_type=view_type, context=context, toolbar=toolbar, submenu=submenu)

        return res


    def _altern_si_so(self, cr, uid, ids, context=None):
        for id in ids:
            sql = '''
            SELECT action, name
            FROM hr_attendance AS att
            WHERE emp_id = (SELECT emp_id FROM hr_attendance WHERE id=%s)
            AND action IN ('sign_in','sign_out')
            AND name <= (SELECT name FROM hr_attendance WHERE id=%s)
            ORDER BY name DESC
            LIMIT 2 '''
            cr.execute(sql,(id,id))
            atts = cr.fetchall()
            if not ((len(atts)==1 and atts[0][0] == 'sign_in') or (len(atts)==2 and atts[0][0] != atts[1][0] and atts[0][1] != atts[1][1])):
                #return False
                pass
        return True
    
    _constraints = [(_altern_si_so, 'Error ! Sign in (resp. Sign out) must follow Sign out (resp. Sign in)', ['action'])]

class hr_employee(osv.osv):
    def _state(self, cr, uid, ids, name, args, context=None):
        result = super(hr_employee, self)._state(cr, uid, ids, name, args, context)
        return result

    _inherit = "hr.employee"
    _columns = {
       'availability': fields.function(_state, method=True, type='selection', selection=[('absent', 'Absent'), ('present', 'Present')], string='Attendance'),
       'emp_attendance_no': fields.integer('Attendance No',readonly=True,states={'draft':[('readonly',False)]}),      
    }

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
