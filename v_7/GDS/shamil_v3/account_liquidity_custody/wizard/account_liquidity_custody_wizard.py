# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

 
from openerp.osv import fields, osv



class account_liquidity_custody_add_vouher_wizard(osv.osv_memory):
    
    _name = 'account.liquidity.custody.add.vouher.wizard'
    _columns = {
                'partner_id': fields.many2one('res.partner', 'Partner'),
                
                             
                }
    
    def create_custody(self, cr, uid, ids, context=None):
	"""
        Override create method to create a new liquidity custody

	@return: super create method
	"""
     
        if context is None:
            context = {}
        data = self.read(cr, uid, ids)[0]
        account_liquidity_custody_obj = self.pool.get('account.liquidity.custody')
        for v in context.get('active_ids', []):
             account_liquidity_custody_id = account_liquidity_custody_obj.create(cr, uid,{
            'voucher_id': v,
            'partner_id': data['partner_id'][0]
             }, context=context)
        
        return True

