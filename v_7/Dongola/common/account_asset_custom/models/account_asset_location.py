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

from openerp.tools.translate import _
from openerp.osv import fields,osv

class account_asset_location(osv.osv):
    """
    Model of to configure location to be used by the asset model
    """
    _name = "account.asset.location"

    _parent_name = "asset_location_id"

    _order = "code"

    def _asset_complete_name(self, cr, uid, ids, name, args, context=None):
        """ 
        Forms complete name of location from parent location to child location.

        @param char name: the name of the functional field complete_name,
        @param list arg: other arguments,
        @return: Dictionary of asset name to be display
        """
        def _get_one_full_name(location, level=4):
            if location.asset_location_id:
                parent_path = _get_one_full_name(location.asset_location_id, level-1) + "/"
            else:
                parent_path = ''
            return parent_path + location.name
        res = {}
        for m in self.browse(cr, uid, ids, context=context):
            res[m.id] = _get_one_full_name(m)
        return res
     
    _columns = {
        'name': fields.char('Location Name',  size=128, required=True ),
        'asset_usage': fields.selection([('view', 'View'), ('regular', 'Regular')], 'Location Type', required=True, select = True),
        'complete_name': fields.function(_asset_complete_name, method=True, type='char', size=128, string="Location Name"),
        'asset_location_id': fields.many2one('account.asset.location', 'Parent Location', select=True, ondelete='cascade'),
        'child_idss': fields.one2many('account.asset.location', 'asset_location_id', 'Children Locations'),
        'code': fields.char('Location Code', size=24),
        'company_id': fields.many2one('res.company', 'Company', required=False), 
        'comment': fields.text('Additional Information'),
    }

    def _default_company(self, cr, uid, context=None):
        """
        Function return the company id based on the user company if exist or asset location company.
       
        @return: ID of the company
        """
        user = self.pool.get('res.users').browse(cr, uid, uid, context=context)
        if user.company_id:
            return user.company_id.id
        return self.pool.get('res.company').search(cr, uid, [('asset_location_id', '=', False)])[0]

    _defaults = {
        'asset_usage': 'regular',
        'company_id': _default_company,
    }

    def copy(self, cr, uid, id, default=None, context=None):
        category = self.browse(cr, uid, id, context=context)
        if category.code:
            default.update({'code':"%s (copy)"% (category.code or '')})
        if category.name:
            default.update({'name':"%s (copy)"% (category.name or '')})
        return super(account_asset_location, self).copy(cr, uid, id, default=default, context=context)

    def _check_recursion(self, cr, uid, ids):
        """Constrain function to prohibit the recursion of the location up to 30.

        @return: Boolean True or False
        """
        level = 30
        while len(ids):
            sql = "select distinct asset_location_id from account_asset_location where id in (%s)" % ','.join(map(str,ids))
            cr.execute(sql)
            ids = filter(None, map(lambda x:x[0], cr.fetchall()))
            if not level:
                return False
            level -= 1
        return True

    _constraints = [
        (_check_recursion, _('Error ! You can not create recursive location.'), ['asset_location_id'])
    ]

    _sql_constraints = [
        ('code_company_uniq', 'unique (code,company_id)', 'Location code must be unique per company.'),
        ('name_company_uniq', 'unique (name, company_id)', 'Location name must be unique per company.'),
    ]
    def unlink(self, cr, uid, ids, context=None):
        """
        This method to prevent record deletion
        """
        asset_obj=self.pool.get('account.asset.asset')
        
        for asset in asset_obj.browse(cr, uid, ids, context):
            if asset.location_id.id:
                raise osv.except_osv(_('Warning!'),_('You cannot delete this location there is an asset assign to it '))
        return super(account_asset_location, self).unlink(cr, uid, ids, context)
    


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
