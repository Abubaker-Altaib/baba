# -*- coding: utf-8 -*-
##############################################################################
#
# NCTR, Nile Center for Technology Research
# Copyright (C) 2016-2017 NCTR (<http://www.nctr.sd>).
#
##########################################################################

from openerp.osv import fields,osv
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp

class admin_affairs_payment_roof(osv.Model):
    """To manage admin affairs payment roof """
    def _check_roof_cost(self, cr, uid, ids, context=None):
        """
        Method checks that amount of roof's upper and lower limit are greater than zero or not 
        and whether the roof's upper limit is greater than the lower limit or not.
        
        @return: Boolean True Or False
        """
        for record in self.browse(cr, uid, ids):
            if record.cost_from < 0.0 or record.cost_to <0.0 or record.cost_to <= record.cost_from:
                raise osv.except_osv(_("ValidateError"),_('The Roof Cost Is Wrong\nPlease Enter The Right Cost!'))    	
        return True

    _name = "admin.affairs.payment.roof"

    _description = 'admin affairs payment roof'

    _columns = {
        'name': fields.selection([('affairs','Admin Affairs Manager'),('service','Service Section Manager')],'Name',required=True),
        'company_id': fields.many2one('res.company', 'Company', required=True, readonly=True),
        'model_id': fields.many2one('ir.model','Model',required=True),
        'cost_from': fields.float('Cost From', digits_compute=dp.get_precision('Account'),required=True),
        'cost_to': fields.float('Cost To', digits_compute=dp.get_precision('Account'),required=True),
    }

    _sql_constraints = [
        ('model_uniq', 'unique(name,model_id)', _('The Model Must Be Unique For Each Name!')),
    ]

    _defaults = {
        'company_id': lambda self, cr, uid, c: self.pool.get('res.company')._company_default_get(cr, uid, 'admin.affairs.payment.roof', context=c),
    }

    _constraints = [
        (_check_roof_cost, '',[''])
    ]

