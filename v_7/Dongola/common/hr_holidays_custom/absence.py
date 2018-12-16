# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

from openerp.osv import fields, osv

#----------------------------------------
#holiday status(inherit)
#----------------------------------------
class  hr_holidays_status_absence(osv.Model):
    """Inherits hr.holidays.status and add absence field 
    """
    _inherit = "hr.holidays.status"

    _columns = {
        'absence': fields.boolean('Absence', help="If True the configuration is for absence."),
        'permission': fields.boolean('Permission', help="If True the configuration is for permission."),
        'number_hour': fields.float('Number Of Hours'),
    }
    
    _defaults = {
        'number_hour': 3,
        'number_of_days': 3,
        'absence':0,
        'permission':0,
    }


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

