# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################
from datetime import datetime
import time
from openerp.osv import fields, osv, orm
from openerp.tools.translate import _
from openerp import netsvc

class hr_salary_scale(osv.Model):
    _inherit = "hr.salary.scale"
    _columns = {
        'military_type' : fields.selection([ ('officer' , 'Officers'),('soldier' , 'Soldiers')], string='Military Type'),
    }

