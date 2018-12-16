# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

from openerp.osv import fields, osv

class res_company(osv.Model):

    _inherit = 'res.company'

    _columns = {
              'hq' :fields.boolean("HQ"),
               }


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
