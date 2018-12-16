 # -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

from openerp.osv import fields, osv

class hr_config_settings_inherit(osv.Model):

    _inherit = 'res.company'

    _columns = {
              'process_employee' : fields.boolean('Process for Employee'),
              'process_contractors' : fields.boolean('Process for Contractors'),
              'process_recruit' : fields.boolean('Process for Recruit'),
              'process_trainee' : fields.boolean('Process for Trainee'),
              'age_pension' :fields.integer("Age Pension", required= True),
               }

    _defaults = {
         'age_pension':0,
         'process_employee':True,
        }
