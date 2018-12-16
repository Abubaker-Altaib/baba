# -*- coding: utf-8 -*-
##############################################################################
#
# NCTR, Nile Center for Technology Research
# Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

from openerp.osv import fields, osv,orm

from tools.translate import _

class stock_invoice_onshipping(osv.osv_memory):

    def _get_journal(self, cr, uid, context=None):
        """
        Return journal based on the journal type
        @return: id or False
        """
        res = self._get_journal_id(cr, uid, context=context)
        if res:
            return res[0][0]
        return False

    def _get_journal_id(self, cr, uid, context=None):
        """
         Inherit function to add picking quality type in option to get journal type
         @return: List of ids
        """
        if context is None:
            context = {}
        model = context.get('active_model')
        if not model or model not in ['stock.picking','stock.picking.out','stock.picking.in']:
            return []

        model_pool = self.pool.get(model)
        journal_obj = self.pool.get('account.journal')
        res_ids = context and context.get('active_ids', [])
        vals = []
        browse_picking = model_pool.browse(cr, uid, res_ids, context=context)
        for pick in browse_picking:
            if not pick.move_lines:
                continue
            src_usage = pick.move_lines[0].location_id.usage
            dest_usage = pick.move_lines[0].location_dest_id.usage
            type = pick.type
            if type == 'out' and dest_usage == 'supplier':
                journal_type = 'purchase_refund'
            elif type == 'out' and dest_usage == 'customer':
                journal_type = 'sale'
            elif type == 'in' and src_usage == 'supplier':
                journal_type = 'purchase'
            elif type == 'in' and src_usage == 'customer':
                journal_type = 'sale_refund'
            elif type == 'quality' and src_usage == 'supplier':
                journal_type = 'purchase'
            elif type == 'quality' and src_usage == 'customer':
                journal_type = 'sale_refund'
            else:
                journal_type = 'sale'
            company_id=self.pool.get('res.users').browse(cr, uid, uid).company_id.id
            value = journal_obj.search(cr, uid, [('type','=',journal_type ),('company_id','=',company_id ),('special','=',False)])
            for jr_type in journal_obj.browse(cr, uid, value, context=context):
                t1 = jr_type.id,jr_type.name
                if t1 not in vals:
                    vals.append(t1)
        return vals

    _inherit = "stock.invoice.onshipping"


    _columns = {
        'journal_id': fields.selection(_get_journal_id, 'Destination Journal',required=True),

    }

    _defaults = {
        'journal_id' : _get_journal,
    }


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
