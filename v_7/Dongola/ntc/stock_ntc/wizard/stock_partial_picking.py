# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-TODAY OpenERP SA (<http://openerp.com>).
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
from lxml import etree
from openerp.osv import fields, osv
from openerp.tools.misc import DEFAULT_SERVER_DATETIME_FORMAT
from openerp.tools.float_utils import float_compare
import openerp.addons.decimal_precision as dp
from openerp.tools.translate import _
from openerp import netsvc


class stock_partial_picking(osv.osv_memory):
    _inherit = "stock.partial.picking"

    def fields_view_get(self, cr, uid, view_id=None, view_type='form', context=None, toolbar=False, submenu=False):
        #override of fields_view_get in order to change the label of the process button and the separator accordingly to the shipping type
        if context is None:
            context={}
        res = super(stock_partial_picking, self).fields_view_get(cr, uid, view_id=view_id, view_type=view_type, context=context, toolbar=toolbar, submenu=submenu)
        type = context.get('default_type', False)
        request = context.get('request', False)
        if type:
            doc = etree.XML(res['arch'])
            for node in doc.xpath("//button[@name='do_partial']"):
                if type == 'in':
                    node.set('string', _('_Receive'))
                elif type == 'out':
                    if request:
                        node.set('string', _('_Send Purchase Requisition'))
                    else:    
                        node.set('string', _('_Deliver'))
            for node in doc.xpath("//separator[@name='product_separator']"):
                if type == 'in':
                    node.set('string', _('Receive Products'))
                elif type == 'out':
                    if request:
                        node.set('string', _('Request Products'))
                    else:
                        node.set('string', _('Deliver Products'))
            res['arch'] = etree.tostring(doc)
        return res

    def do_partial(self, cr, uid, ids, context=None):
        returned = super(stock_partial_picking, self).do_partial(cr, uid, ids, context=context)
        req_ids = context.get('active_ids', [])
        wf_service = netsvc.LocalService("workflow")
        pick_obj = self.pool.get('stock.picking.out')
        x = pick_obj.browse(cr, uid, req_ids[0], context=context).state
        if x == 'approve_ghrm':
            pick_obj.write(cr, uid, req_ids[0], {'state': 'done'})
            wf_service.trg_validate(uid, 'stock.picking.out', req_ids[0], 'done', cr)


        return returned


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
