# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

from osv import fields,osv

class res_partner_year(osv.osv):
    """
    To add the abblitiy to mange the supplier of the specific year """

    _description='Partner Year'
    _name = 'res.partner.year'
    _columns = {
        'name': fields.char('Year Name', required=True, size=64, translate=True),
        'active' : fields.boolean('Active', help="The active field allows you to hide the category without removing it."),
        'partner_ids': fields.many2many('res.partner', 'res_partner_year_rel', 'year_id', 'partner_id', 'Partners'),
    }


class res_partner(osv.osv):
    """
    To add year id to res partner """

    _inherit = "res.partner"
    _columns = {
        'year_id': fields.many2many('res.partner.year', 'res_partner_year_rel', 'partner_id', 'year_id', 'Years'),
    }
#
# Model definition
#

class custom_res_partner_category(osv.osv):
    """
    Add parent and child relation to partner category"""

    _inherit = 'res.partner.category'
    _columns = {
                'type': fields.selection([('supplier', 'Supplier'),('accountant', 'Accountant'),('project', 'project')],'Type' ),
                'parent_id': fields.many2one('res.partner.category', 'Parent Category', select=True),
		}
        
    def onchange_parent_id(self, cr, uid, ids,parent_id=False):
        """ 
        Read type of parent of category to set it when changing a partner.
 
        @param parent_id: Changed parent id
        @return: Dictionary of values of parent type 
        """
        res = {}
        if parent_id:
            parent_type = self.pool.get('res.partner.category').browse(cr, uid, parent_id)
            result={'type': parent_type.type}
            res = {'value': result}
        return res

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
