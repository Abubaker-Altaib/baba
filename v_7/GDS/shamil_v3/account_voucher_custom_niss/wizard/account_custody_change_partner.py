# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2016 NCTR (<http://www.nctr.sd>).
#
##############################################################################

from openerp.osv import fields, osv
from openerp.tools.translate import _

class account_custody_change_partner(osv.osv_memory):

    _name = "custody.change.partner"
    
    _description = "Custody Change Partner"

    def default_get(self, cr, uid, fields, context=None):
        """ Get default values
        @param self: The object pointer.
        @param cr: A database cursor
        @param uid: ID of the user currently logged in
        @param fields: List of fields for default value
        @param context: A standard dictionary
        @return: default values of fields
        """
        if context is None:
            context = {}
        if len(context.get('active_ids',[])) > 1:
            raise osv.except_osv(_('Error!'), _('You cannot perform this operation on more than one custody.'))
        res = super(account_custody_change_partner, self).default_get(cr, uid, fields, context=context)
        voucher_line = self.pool.get('account.voucher.line').browse(cr, uid, context['active_id'], context=context)
        if 'last_partner_id' in fields:
            res.update({'last_partner_id': voucher_line.res_partner_id.id})

        return res

    _columns = {
        'last_partner_id': fields.many2one('res.partner', 'Last Partner'),
        'new_partner_id': fields.many2one('res.partner', 'New Partner'),
      }

    def change_custody_partner(self, cr, uid, ids, context={}):
        voucher_line_obj = self.pool.get('account.voucher.line')
        change_partner_record = self.browse(cr, uid, ids[0], context )
        voucher_id = context.get('active_id',False)
        if not voucher_id:
            raise osv.except_osv(_('Error!'), _('Sorry , There are Error'))
        voucher_line = voucher_line_obj.browse(cr, uid, voucher_id, context=context)
        if not voucher_line.custody:
            raise osv.except_osv(_('Error!'), _('Sorry , This is not custody'))

        if voucher_line.custody_state == 'removed':
            raise osv.except_osv(_('Error!'), _('Sorry , This custody is removed'))

        voucher_line_obj.write(cr, uid , [voucher_id], {'last_partner_id' :change_partner_record.last_partner_id.id,
                                                        'res_partner_id': change_partner_record.new_partner_id.id,}, context)
        










