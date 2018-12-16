# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################
from openerp import tools
from openerp.osv import fields, osv
from openerp.tools.translate import _

class custom_user(osv.osv):
    _inherit = "res.users"
    def preference_change_password(self, cr, uid, ids, context=None):
        raise osv.except_osv(_("Password can not change, This feature is temporary disabled"),_(''),) 
        return {
            'type': 'ir.actions.client',
            'tag': 'change_password',
            'target': 'new',
        }

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
