# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution	
#    Copyright (C) 2004-2008 Tiny SPRL (<http://tiny.be>). All Rights Reserved
#    $Id$
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

import time
import tools
from osv import osv, fields, orm
import decimal_precision as dp
from tools.translate import _



class account_asset_asset(osv.osv):


    _inherit = 'account.asset.asset'


    def _get_type(self, cr, uid,context=None):

        """ Determine the asset's type"""

        asset_type = 'asset'
        if context:
            if context.has_key('asset_type'): asset_type = context['asset_type']
        return asset_type


    def validate(self, cr, uid, ids, context={}):
        """
        check the asset depreiciation data in order to change it's state to open   

        @return: Returns asset state
        """        
        for asset in self.browse(cr, uid, ids, context):
            if asset.state == 'draft' :

                self.seq(cr, uid, ids, context)
                res = self.pool.get('account.asset.asset').write(cr, uid, [asset.id], {'state':'confirmed' }, context)
                return res
            

    def seq(self, cr, uid, ids, context=None):
        c = {}
        obj_sequence = self.pool.get('ir.sequence')
        seq_no = False
        for move in self.browse(cr, uid, ids, context=context):             
            if not move.category_id.sequence_id:
                raise osv.except_osv(_('Error'), _('No sequence defined on the category !')) 
            if not move.serial_no:
                seq_no = obj_sequence.get_id(cr, uid, move.category_id.sequence_id.id, context=c)
                self.write(cr, uid, [move.id], {'serial_no': seq_no})
                return seq_no




    _columns = {

        'employee_id' : fields.many2one('hr.employee','Current Employee'),

	'department_id' : fields.many2one('hr.department','Department'),

	'serial_no': fields.char('Asset S/N', size=32, readonly=True),

	'in_stock' : fields.boolean('In Stock'),

	'custody_specification' : fields.selection([('admin','Administrative'),('techn' , 'Techincal')], 'Custody Specification'),

	'active' : fields.boolean('Useable'),

        'custody' : fields.boolean('Custody'),

	#'custody_ids' : fields.one2many('asset.custody','asset_id','Log ID'),

	'asset_type': fields.selection([('asset','Asset'),('custody','Custody')], 'Asset Type', readonly=True, select=True),
	
	'state': fields.selection([('draft', 'Draft'), ('confirmed', 'Confirmed'), ('close', 'Closed')],'State', select=True),

	#'custody_asset_id': fields.many2many('asset.custody','asset_id','custody_asset_id',string='Asset Custody'),
	
	'delivery_date': fields.date(string='Delivery Date'),

		}



    _defaults = {

	'in_stock' : False,

	'active' : True,

	'asset_type': _get_type,

		 }




class product_product(osv.osv):


    _inherit = 'product.product'

    _columns = {

	    'custody' : fields.boolean('Custody'),

	    'custody_product_id' : fields.many2many('asset.custody','product_id','custody_product_id',string='Asset Custody'),

 	    'approved_qty' :  fields.integer('Approved Quantity'),

	    

		}



class account_asset_location(osv.osv):


    _inherit = 'account.asset.location'

    _columns = {

	    'custody' : fields.boolean('Custody'),

		}

class account_asset_category(osv.osv):

    _inherit = 'account.asset.category'

    """
    this class contain function define main view categories and regular
    categories  and function to control all asset's account operation 
    """

    _columns = {
        
        'sequence_id': fields.many2one('ir.sequence', 'Entry Sequence', domain="[('company_id', '=', company_id)]" , readonly=True, help="This field contains the informatin related to the numbering of this asset categories."),

   	 }

 

    def create(self, cr, uid, vals, context=None):
        if not 'sequence_id' in vals or not vals['sequence_id']:
            vals.update({'sequence_id': self.create_sequence(cr, uid, vals, context)})
        return super(account_asset_category, self).create(cr, uid, vals, context)




    def create_sequence(self, cr, uid, vals, context=None):
        """
        this Function create sequence for each asset by using 
        category code and counter for asset one by one 
        """    
        seq_pool = self.pool.get('ir.sequence')
        seq_typ_pool = self.pool.get('ir.sequence.type')
        name = vals['name']
        code = vals['code']

        types = {
            'name': name,
            'code': code
        }

        seq_typ_pool.create(cr, uid, types)

        seq = {
            'name': name,
            'code': code,
            'active': True,
            'prefix': code + "/",
            'padding': 0,
            'number_increment': 1
        }

        return seq_pool.create(cr, uid, seq)
    
    


