# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>).
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


from openerp.tools.config import config
from openerp.osv import osv,fields


class custom_config_settings(osv.osv):
    """
    To Add Boolean field to skip upgrade of workflow and security
    """
    _inherit = 'base.config.settings'

    _columns = {
      'module_base_custom_extra': fields.boolean('Skip Upgrade Models',
            help="""if this box is true the system will be skip workflow and security and csv files in particular module when upgrade it."""),
    }

    _defaults = {
        'module_base_custom_extra': False,
    }

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
