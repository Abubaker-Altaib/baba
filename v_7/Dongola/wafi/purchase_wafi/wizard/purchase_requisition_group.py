# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
############################################################################
import time

from openerp.osv import fields, osv
from openerp import netsvc
from openerp import pooler
from openerp.osv.orm import browse_record, browse_null
from openerp.tools.translate import _

class purchase_requisition_group(osv.osv_memory):
    _name = "purchase.requisition.group"
    _description = "Purchase Requisition Merge"

    def fields_view_get(self, cr, uid, view_id=None, view_type='form',
                        context=None, toolbar=False, submenu=False):
        """
         Changes the view dynamically
         @param self: The object pointer.
         @param cr: A database cursor
         @param uid: ID of the user currently logged in
         @param context: A standard dictionary
         @return: New arch of view.
        """
        if context is None:
            context={}
        res = super(purchase_requisition_group, self).fields_view_get(cr, uid, view_id=view_id, view_type=view_type, context=context, toolbar=toolbar,submenu=False)
        if context.get('active_model','') == 'purchase.requisition' and len(context['active_ids']) < 2:
            raise osv.except_osv(_('Warning!'),
            _('Please select multiple requisition to merge in the list view.'))
        return res
    def merge_requisitions(self, cr, uid, ids, context=None):
        """
             To merge similar type of purchase requisitions.

             @param self: The object pointer.
             @param cr: A database cursor
             @param uid: ID of the user currently logged in
             @param ids: the ID or list of IDs
             @param context: A standard dictionary

             @return: purchase requisition view

        """
        requisition_obj = self.pool.get('purchase.requisition')
        proc_obj = self.pool.get('procurement.order')
        mod_obj =self.pool.get('ir.model.data')
        wf_service = netsvc.LocalService("workflow")
        if context is None:
            context = {}
        result = mod_obj._get_id(cr, uid, 'purchase_requisition', 'view_purchase_requisition_filter')
        id = mod_obj.read(cr, uid, result, ['res_id'])

        allrequisitions = requisition_obj.do_merge(cr, uid, context.get('active_ids',[]), context)
        for new_requisition in allrequisitions:
            wf_service.trg_validate(uid, 'purchase.requisition', new_requisition, 'action_confirm', cr)
            wf_service.trg_validate(uid, 'purchase.requisition', new_requisition, 'action_confirm_dept', cr)
            wf_service.trg_validate(uid, 'purchase.requisition', new_requisition, 'action_confirm_supp', cr)
            wf_service.trg_validate(uid, 'purchase.requisition', new_requisition, 'action_approve', cr)
            proc_ids = proc_obj.search(cr, uid, [('requisition_id', 'in', allrequisitions[new_requisition])], context=context)
            for proc in proc_obj.browse(cr, uid, proc_ids, context=context):
                if proc.requisition_id:
                    proc_obj.write(cr, uid, [proc.id], {'requisition_id': new_requisition}, context)

        return {
            'domain': "[('id','in', [" + ','.join(map(str, allrequisitions.keys())) + "])]",
            'name': _('Purchase Requisitions'),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'purchase.requisition',
            'view_id': False,
            'type': 'ir.actions.act_window',
            'search_view_id': id['res_id']
        }

purchase_requisition_group()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
