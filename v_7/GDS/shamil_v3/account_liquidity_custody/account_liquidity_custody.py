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

from osv import osv, fields
from openerp import tools
from openerp.tools.translate import _



class account_liquidity_custody(osv.osv):

    _name = 'account.liquidity.custody'

    def create(self, cr, uid, vals, context={}):
        """
        Inherit create method set name from sequence if exist
        @param default: dictionary of the values of record to be created,
        @return: super method of copy    
        """
        vals.update({'name': vals.get('name','/') == '/' and self.pool.get('ir.sequence').get(cr, uid,'account.liquidity.custody') or vals.get('name')})
        res = super(account_liquidity_custody, self).create(cr, uid, vals, context=context)
        return res

    def confirm(self, cr, uid, ids, context={}):
	self.write(cr, uid, ids, {'state': 'confirmed' })
        return True
    
    def reset(self, cr, uid, ids, context={}):
	self.write(cr, uid, ids, {'state': 'draft' })
        return True
    
    def release(self, cr, uid, ids, context={}):
	self.write(cr, uid, ids, {'state': 'released' })
        return True

    def unlink(self, cr, uid, ids, context=None):
        for rec in self.browse(cr, uid, ids, context=context):
            if rec.state != 'draft':
                raise osv.except_osv(_('Warning!'),_('You cannot delete a Custody Liquidity in %s state.')%(rec.state))
        return super(account_liquidity_custody, self).unlink(cr, uid, ids, context)
    
    _columns = {

		'name': fields.char('Referance', size=32 ),#TODO: sequence
        'partner_id' : fields.many2one('res.partner','Current Employee'),
		'voucher_id' : fields.many2one('account.voucher','Voucher'),
		'amount' : fields.related('voucher_id', 'amount', type='float', readonly=True, store=True, string='Amount'),
		'state': fields.selection([('draft', 'Draft'), ('confirmed', 'Confirmed'), ('released', 'Released')],'State', select=True),
		'description': fields.text('Description'),
	}

    _sql_constraints = [
        
        ('voucher_id_uniq', 'unique(voucher_id)', 'Voucher must be unique !'),
        ]

    _defaults = {
		'state' : 'draft',
		'name' : '/',
	}




