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
    Inherits res.company to add fields that specify the employee types that can undergone the process.
    """
    _inherit = 'res.company'

    _columns = {
              'injury_employee' : fields.boolean('Injury for Employee'),
              'injury_contractors' : fields.boolean('Injury for Contractors'),
              'injury_recruit' : fields.boolean('Injury for Recruit'),
              'injury_trainee' : fields.boolean('Injury for Trainee'),
              'treatment_account_id':fields.many2one('account.account','Treatment Account'),
               }

    _defaults = {
         'injury_employee':True,
    }
