# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2016 NCTR (<http://www.nctr.sd>).
#
##############################################################################

from datetime import datetime
import time
from openerp.osv import fields, osv
from openerp.tools.translate import _

class account_custody_change_partner(osv.osv_memory):

    _name = "custody.change.end_date"
    
    _description = "Custody Change End Date"

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
      
        res.update({'last_end_date': voucher_line.custody_end_date,'new_end_date':voucher_line.custody_end_date})
        print"SSSSSSSSS",res
        return res

    _columns = {
        'last_end_date': fields.date('Last End Date'),
        'new_end_date': fields.date('New End Date'),
      }

    def change_custody_end_date(self, cr, uid, ids, context={}):
        voucher_line_obj = self.pool.get('account.voucher.line')
        change_end_date_record = self.browse(cr, uid, ids[0], context )
        voucher_id = context.get('active_id',False)
        if not voucher_id:
            raise osv.except_osv(_('Error!'), _('Sorry , There are Error, First select record'))
        voucher_line = voucher_line_obj.browse(cr, uid, voucher_id, context=context)
        if not voucher_line.custody:
            raise osv.except_osv(_('Error!'), _('Sorry , This is not custody'))

        if voucher_line.custody_state == 'removed':
            raise osv.except_osv(_('Error!'), _('Sorry , This custody is removed'))
        if change_end_date_record.new_end_date < voucher_line.date :
            raise osv.except_osv(_('Error!'), _('Sorry , New date less than voucher date'))

        voucher_line_obj.write(cr, uid , [voucher_id], {'custody_end_date' :change_end_date_record.new_end_date }, context)
        










