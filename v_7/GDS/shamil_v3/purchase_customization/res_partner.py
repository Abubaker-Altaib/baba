# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
#############################################################################
#############################################################################



from osv import osv, fields

class res_partner(osv.Model):

    _inherit = 'res.partner'

    _columns = {
            'partner_type':fields.selection([('purchase','Purchase'),('clearance','Clearance')] , "Partner Type"),
            
     }