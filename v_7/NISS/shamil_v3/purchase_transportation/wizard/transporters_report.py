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

from osv import fields, osv

class transporters_report(osv.osv_memory):
    _name = "transporters.report"
    _description = "Transporters Report wizard"
    _columns = {
        'Date_from': fields.date('Date From',required=True), 
        'Date_to': fields.date('Date To',required=True), 
        'partner_name': fields.many2one('res.partner', 'Partner' ),
        'state' : fields.selection([('done','تم')] ,'State',select=True),

    }

    def print_report(self, cr, uid, ids, context=None):
        data = self.read(cr, uid, ids, [], context=context)[0]
        datas = {
             'ids': [],
             'model': 'transportation.order',
             'form': data
            }
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'transporters_report',
            'datas': datas,
            }
transporters_report()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: