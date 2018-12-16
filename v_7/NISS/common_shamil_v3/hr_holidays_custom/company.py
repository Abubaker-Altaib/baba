# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

from openerp.osv import fields, osv

class hr_config_settings_inherit(osv.Model):
    """Inherits res.company to add feilds to indicate if the process allowaed to the specific employee_type or not.
    """

    _inherit = 'res.company'

    _columns = {
        'holiday_employee' : fields.boolean('Holidays for Employee'),
        'holiday_contractors' : fields.boolean('Holidays for Contractors'),
        'holiday_recruit' : fields.boolean('Holidays for Recruit'),
        'holiday_trainee' : fields.boolean('Holidays for Trainee'),
    }

    _defaults = {
         'holiday_employee':True,
    }


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
