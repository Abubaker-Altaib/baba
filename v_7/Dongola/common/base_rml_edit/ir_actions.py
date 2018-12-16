# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2011 Cubic ERP - Teradata SAC (<http://cubicerp.com>).
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
import binascii
import netsvc

class report_xml(osv.osv):
 
    def _report_content_txt(self, cr, uid, ids, name, arg, context=None):
        if context is None: context = {}
        res = {}
        context['bin_size'] = False
        for report in self.browse(cr, uid, ids, context=context):
            if not report.modify:
               self.reset_rml(cr, uid, [report.id], context=context)
            data = report.report_rml_content
            res[report.id] = data
        return res

    def _report_content_txt_inv(self, cr, uid, id, name, value, arg, context=None):
        self.write(cr,uid,id,{'report_rml_content':value.encode('utf-8')},context=context)

    def reset_rml(self, cr, uid, ids, context=None):
        self.write(cr,uid,ids,{'report_rml_content': None},context=context)
        res=self._report_content(cr, uid, ids, name='report_rml_content', arg=None, context=context)
        for id in ids:
            self.write(cr,uid,id,{'report_rml_content':res.get(id, None)},context=context)
        return True
    
    _name = 'ir.actions.report.xml'
    _inherit = 'ir.actions.report.xml'
    _columns = {
        'modify': fields.boolean('Modify', help="Allow to modify the RML report directly from OpenERP"),
	    'report_rml_content_txt': fields.function(_report_content_txt, fnct_inv=_report_content_txt_inv, method=True, type='text', string='RML text content'),
	    
	}
	
    _defaults = {
        'modify': False,
   }      
report_xml()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
