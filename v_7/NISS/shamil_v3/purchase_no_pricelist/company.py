# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

# adding currency format to the company 
from openerp.osv import osv, fields, orm

class company(osv.Model):
    """ 
    Add currency format to company"""

    _inherit = 'res.company'
    _columns = {
        'currency_format': fields.selection([ ('euro','Europian Format'),
                                              ('ar','Arabic Format')],
                                            'Check Printing Format',
                                            help="Check the format of the currency."),
    }
    _defaults = {
        'currency_format':'ar',
    }


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
