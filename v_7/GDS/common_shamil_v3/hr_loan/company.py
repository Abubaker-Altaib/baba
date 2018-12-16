# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

from openerp.osv import fields, osv

class hr_config_settings_inherit(osv.Model):
    """Inherits res.company to add feilds that spesify the employee types that can undergone the process.
    """
    _inherit = 'res.company'

    _columns = {
              'loan_employee' : fields.boolean('Loan for Employee'),
              'loan_contractors' : fields.boolean('Loan for Contractors'),
              'loan_recruit' : fields.boolean('Loan for Recruit'),
              'loan_trainee' : fields.boolean('Loan for Trainee'),
               }


    _defaults = {

         'loan_employee':True,

                }
