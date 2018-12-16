# -*- coding: utf-8 -*-
##############################################################################
#
# NCTR, Nile Center for Technology Research
# Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##########################################################################

from openerp.osv import fields,osv
import time
import netsvc
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp


#----------------------------------------
# Class admin affaris payment roof
#----------------------------------------
class admin_affaris_payment_roof(osv.Model):

    def _check_roof_cost(self, cr, uid, ids, context=None): 
       """
           Method checks that amount of roof's upper and lower limit are greater than zero ro not 
           and wether the roof's upper limit is greater than the lower limit or not.
           @return: Boolean True Or False
       """         
       for record in self.browse(cr, uid, ids): 
        if record.cost_from <= 0.0 or record.cost_to <=0.0 or record.cost_to <= record.cost_from:
                        return False    	
        return True     

    ROOF_SELECTION = [
    ('affaris', 'Admin Affaris manager'),
    ('service', 'Service Section manager'),
 	]  
    _name = "admin.affaris.payment.roof"
    _description = 'admin affaris payment roof'
    _columns = {
    		'company_id': fields.many2one('res.company', 'Company', required=True, readonly=True),
		'model_id': fields.many2one('admin.affairs.model','Model',required=True),
                'name': fields.selection(ROOF_SELECTION, 'Name', required=True,),
                'cost_from': fields.float('Cost From', digits_compute=dp.get_precision('Account'),required=True),
                'cost_to': fields.float('Cost To', digits_compute=dp.get_precision('Account'),required=True),
               }

    _sql_constraints = [
        ('model_uniq', 'unique(name,model_id)', 'Model must be unique!'),
            ]
    _defaults = {
        'company_id': lambda self, cr, uid, c: self.pool.get('res.company')._company_default_get(cr, uid, 'admin.affaris.payment.roof', context=c),
                } 
    _constraints = [
        (_check_roof_cost, 
            'Your Roof Cost is WRONG ... please insert the right cost',
            ['Roof Cost ']),]

