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

from osv import osv, fields, orm
from tools.translate import _
import mx
import mx.DateTime
import time
from datetime import datetime
import netsvc
from openerp.addons.account_voucher.account_voucher import resolve_o2m_operations


class luggage_transfer(osv.osv):

    _name = 'luggage.transfer'

    _columns = {
        'company_id': fields.many2one('res.company', 'Company', required=True),
        'department_id': fields.many2one('hr.department', 'Department', required=True),
        'allowance_id': fields.many2one('hr.allowance.deduction', 'Allowance', required=True),
        'destination_id': fields.many2one('luggage.destination.map', 'Destination', required=True),
        'additional_allowance_id': fields.many2one('hr.additional.allowance', 'Additional Allowance'),
        'date': fields.date('Date', required=True),
        'emp_hours': fields.one2many('emp.luggage_transfer.hours', 'parent_id', 'Employee luggage_transfer hours'),
        'purpose': fields.text('purpose'),
        'descirption': fields.text('Descirption'),
    }

    def _default_company(self,cr,uid,context=None):
        List = []
        user_obj = self.pool.get('res.users')
        user = user_obj.browse(cr ,uid, uid)
        company = False
        if user.company_id:
            company = user.company_id.id
        return company

    _defaults = {
        'company_id' : _default_company,
        'date': lambda *a: time.strftime('%Y-%m-%d'),
    }

    def luggage_transfer(self, cr, uid, ids, data, context=None):
        wiz_data = self.read(cr, uid, ids[0], context={})
        destination_amount = self.pool.get('luggage.destination.map').browse(
            cr, uid, wiz_data['destination_id'][0]).amount
        if not destination_amount:
            raise osv.except_osv(_('warning'), _(
                "Sorry please check  luggage destination map configuration  !"))

        date = mx.DateTime.Parser.DateTimeFromString(wiz_data['date'])

        if wiz_data['emp_hours']:
            allowance_lines = []
            luggage_transfer_hours = self.pool.get(
                'emp.luggage_transfer.hours').read(cr, uid, wiz_data['emp_hours'], [])
            for emp in luggage_transfer_hours:
                allowance_lines.append((0, 0, {
                    'employee_id': emp['employee'][0],
                    'week_hours': emp['hours'],
                    'type_amount': destination_amount,
                    'type' : 'luggage_transfer',
                }))

            dic = {
                'company_id': wiz_data['company_id'][0],
                'department_id': wiz_data['department_id'][0],
                'allowance_id': wiz_data['allowance_id'][0],
                'state': 'draft',
                'line_ids': allowance_lines
            }
            try:
                new_id = self.pool.get(
                'hr.additional.allowance').create(cr, uid, dic)
                self.write(cr, uid, ids, {'additional_allowance_id':new_id})
            except:
                raise orm.except_orm(_('ERROR'), _('The employee degree has no allowances amount'))
            

        else:
            raise osv.except_osv(_('Error'), _(
                "Sorry There is No Employees !"))

        return True


luggage_transfer()


class emp_luggage_transfer_hours(osv.osv):
    _name = 'emp.luggage_transfer.hours'
    _columns = {
        'parent_id': fields.many2one('luggage.transfer', 'luggage_transfer', required=True),
        'employee': fields.many2one('hr.employee', "Employee", required=True,),
        'otherid': fields.char('Code', size=64),
        'hours': fields.integer("Hours ", required=True),
    }

    def onchange_name_code(self, cr, uid, ids, emp, code=True):
        result = {}
        employee_tab = self.pool.get('hr.employee')
        if code:
            emp_id = employee_tab.search(cr, uid, [('otherid', '=', emp)])
            if emp_id:
                result['value'] = {'employee': employee_tab.browse(cr, uid, emp_id)[
                    0].id, }
            else:
                raise osv.except_osv('ERROR', 'Sorry this code is not exist')
        else:
            result['value'] = {'otherid': employee_tab.browse(cr, uid, [emp])[
                0].otherid, }
        return result


emp_luggage_transfer_hours()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
