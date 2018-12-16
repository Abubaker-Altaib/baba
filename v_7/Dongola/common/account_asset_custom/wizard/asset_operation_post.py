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
from tools.translate import _

class account_post_move(osv.osv_memory):
    """
    Account move line reconcile wizard, it checks for the write off the reconcile entry or directly reconcile.
    """

    _name = 'account.asset.post'

    def create_operation_move(self, cr, uid, ids, context=None):
        """
        Wizard method to call "create_operation_move" method for more than one asset to 
        to post Asset sale, revaluation, abandon and initial.

        @return: Action window of the created move
        """
        if context is None:
            context = {}
        move_id = False
        history_obj = self.pool.get('account.asset.history')

        if 'active_ids' in context and context['active_ids']:
            move_ids = history_obj.create_operation_move(cr, uid, context['active_ids'], context)

        return {                
                'domain': "[('id','in',%s)]" % move_ids,
                'name': 'Asset operation move',
                'view_type': 'form',
                'view_mode': 'tree,form',
                'view_id': False,
                'res_model': 'account.move',
                'type': 'ir.actions.act_window'}
account_post_move()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
