# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

from openerp.osv import fields, osv
from openerp.tools.translate import _


class asset_custody_line(osv.osv):
    _inherit = "asset.custody.line"
    _columns = {
	'location_id': fields.related('asset_id','stock_location_id',type='many2one',relation='stock.location',string='Stock Location', store=True, readonly=True),
    }
asset_custody_line()

	
