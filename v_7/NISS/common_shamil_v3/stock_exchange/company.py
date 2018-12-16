# -*- coding: utf-8 -*-
##############################################################################
#
# NCTR, Nile Center for Technology Research
# Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

from openerp.osv import osv,fields

class company(osv.Model):

    """ inherit company model to determine direction of workflow """
    _inherit = 'res.company'
    _columns = {
        'rec_by_categ':fields.boolean('Rec By Category'), 
    }
    _defaults = {

        'rec_by_categ':0,
    }




# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
