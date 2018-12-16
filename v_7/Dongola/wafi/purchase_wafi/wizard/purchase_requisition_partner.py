# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
############################################################################

from openerp.osv import osv
from openerp.tools.translate import _

class purchase_requisition_partner(osv.osv_memory):

    _inherit = "purchase.requisition.partner"
   
    def fields_view_get(self, cr, uid, view_id=None, view_type='form', context=None, toolbar=False, submenu=False):
        if context is None: context = {}
        fvg = super(purchase_requisition_partner, self).fields_view_get(cr, uid, view_id, view_type, context, toolbar, submenu)
        record_id = context and context.get('active_id', False) or False
        if view_type == 'form' and (context.get('active_model') == 'purchase.requisition') and record_id:
            preq_obj = self.pool.get('purchase.requisition').browse(cr, uid, record_id, context=context)
            if  preq_obj.supplier_ids:
                fvg['fields']['partner_id']['domain'].append(('id','in',[r.id for r in preq_obj.supplier_ids])) 
        return fvg

purchase_requisition_partner()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
