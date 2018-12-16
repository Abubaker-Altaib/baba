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
    Inherits res.company to add feilds that spesify the employee types that can
    undergone training's process.
    """
    _inherit = 'res.company'

    _columns = {

              'training_employee' : fields.boolean('Training for Employee'),
              'training_contractors' : fields.boolean('Training for Contractors'),
              'training_recruit' : fields.boolean('Training for Recruit'),
              'training_trainee' : fields.boolean('Training for Trainee'),
               }


    _defaults = {

         'training_employee':True,

                }
