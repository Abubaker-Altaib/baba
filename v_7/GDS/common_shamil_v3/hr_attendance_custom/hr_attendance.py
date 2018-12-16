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

    _inherit = "hr.attendance"
    _columns = {
        'name': fields.datetime('Date', required=True, select=1,readonly=True),
        'action': fields.selection([('sign_in', 'Sign In'), ('sign_out', 'Sign Out'), ('action','Action')], 'Action', required=True,readonly=False),
        'employee_id': fields.many2one('hr.employee', "Employee's Name", required=True, select=True,readonly=True),
        'day': fields.function(_day_compute, method=True, type='char', string='Day', store=True, select=1, size=32),
    }


    def _altern_si_so(self, cr, uid, ids, context=None):
        for id in ids:
            sql = '''
            SELECT action, name
            FROM hr_attendance AS att
            WHERE employee_id = (SELECT employee_id FROM hr_attendance WHERE id=%s)
            AND action IN ('sign_in','sign_out')
            AND name <= (SELECT name FROM hr_attendance WHERE id=%s)
            ORDER BY name DESC
            LIMIT 2 '''
            cr.execute(sql,(id,id))
            atts = cr.fetchall()
            if not ((len(atts)==1 and atts[0][0] == 'sign_in') or (len(atts)==2 and atts[0][0] != atts[1][0] and atts[0][1] != atts[1][1])):
                return False
        return True

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
