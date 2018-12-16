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
from openerp.osv import fields, osv, orm
from openerp.tools.translate import _
from openerp.tools import mute_logger

class group_voucher_partner(osv.osv_memory):
    _name = "group.voucher.partner"
    _description = "Create group voucher"

    def create_group_voucher(self, cr, uid, ids, context=None):
        """ Fill Group many voucher in one voucher.
        @param self: The object pointer.
        @param cr: A database cursor
        @param uid: ID of the user currently logged in
        @param ids: the ID or list of IDs if we want more than one
        @param context: A standard dictionary
        @return:
        """
        if context is None:
            context = {}

        account_voucher_obj = self.pool.get('account.voucher')
        account_voucher_line_obj = self.pool.get('account.voucher.line')
        clearance_obj = self.pool.get('purchase.clearance')
        voucher_ids = context.get('active_ids',False)
        count= 0
        voucher_records = account_voucher_obj.browse(cr, uid, voucher_ids, context=context)
        if voucher_records[0].type <>  'purchase' : 
            raise orm.except_orm(_('Entry Error!'),_("Sorry, You can use this wizard just in payment!"))

        if len(voucher_records) < 2 : 
            raise orm.except_orm(_('Entry Error!'),_("Please select more than one voucher!"))

        if len(voucher_records) < 2 : 
            raise orm.except_orm(_('Entry Error!'),_("Please select more than one voucher!"))

        partner_ids = [voucher.partner_id.id for voucher in voucher_records]
        if len(set(partner_ids)) > 1 : 
            raise orm.except_orm(_('Entry Error!'),_("Please make sure all vouchers has same partner!"))

        states = [voucher.state for voucher in voucher_records if voucher.state <> 'draft']
        if len(states) > 0 : 
            raise orm.except_orm(_('Entry Error!'),_("Please make sure all vouchers state are draft!"))
        voucher_id = account_voucher_obj.create(cr, uid, {
                    'type': 'purchase',
                    'date': time.strftime('%Y-%m-%d'),
                    'partner_id':voucher.partner_id.id,
                    'currency_id': voucher_records[0].currency_id.id,
                    'journal_id': voucher_records[0].journal_id.id,
                                            }, context)
        for voucher in voucher_records:
            account_voucher_line_obj.create(cr, uid, {
                    'res_partner_id':voucher.partner_id.id,
                    'name': voucher.name,
                    'amount': voucher.amount,
                    'type': 'dr',
                    'voucher_id':voucher_id,
                                            }, context)

            cr.execute('SELECT clearance_id from purchase_clearance_voucher \
                        WHERE voucher_id = (%s)'%voucher.id)
            for clearance_id in cr.fetchall():
                clearance_obj.write(cr, uid, [clearance_id], {'account_voucher_ids':[(4,voucher_id)]})  
            account_voucher_obj.write(cr, uid, [voucher.id], {'state':'cancel'}, context)
                
        account_voucher_obj.compute_tax(cr, uid, [voucher_id], context=context)
        return {'type': 'ir.actions.act_window_close'}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
