# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

from openerp.osv import fields, osv

class hr_config_settings_inherit(osv.Model):
    """
    Inherits res.company to add fields that specify the employee types that can undergone mission process.
    """
    _inherit = 'res.company'

    _columns = {
              'mission_employee' : fields.boolean('Mission for Employee'),
              'mission_contractors' : fields.boolean('Mission for Contractors'),
              'mission_recruit' : fields.boolean('Mission for Recruit'),
              'mission_trainee' : fields.boolean('Mission for Trainee'),
    }

    _defaults = {
         'mission_employee':True,
    }
