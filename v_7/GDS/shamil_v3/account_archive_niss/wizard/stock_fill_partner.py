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

from openerp.osv import fields, osv, orm
from openerp.tools.translate import _
from openerp.tools import mute_logger

class archive_fill_partner(osv.osv_memory):
    _name = "archive.fill.partner"
    _description = "Fill partner"

    def fill_partner(self, cr, uid, ids, context=None):
        """ Fill field partner_id using field partner_code.
        @param self: The object pointer.
        @param cr: A database cursor
        @param uid: ID of the user currently logged in
        @param ids: the ID or list of IDs if we want more than one
        @param context: A standard dictionary
        @return:
        """
        if context is None:
            context = {}

        amanat_archive_obj = self.pool.get('account.amanat.archive')
        res_partner_obj = self.pool.get('res.partner')
        archive_ids = context.get('active_ids',False)
        print">>>>>>",archive_ids
        count= 0
        for archive in amanat_archive_obj.browse(cr, uid, archive_ids, context=context):
            partner_id = res_partner_obj.search(cr, uid, [('code','=',archive.partner_code)], context=context)
            if partner_id:
                print">>>>>>>>>>>",partner_id
                amanat_archive_obj.write(cr, uid, archive.id,{'partner_id':partner_id[0]}, context=context)
                count+=1
        print"SSSSSSSSSSSSS",count
        
        return {'type': 'ir.actions.act_window_close'}

archive_fill_partner()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
