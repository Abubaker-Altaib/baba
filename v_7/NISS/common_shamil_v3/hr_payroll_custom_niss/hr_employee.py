# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################
import time
from datetime import datetime
from openerp import netsvc
from dateutil.relativedelta import relativedelta
from openerp.osv import fields, osv, orm
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp
from datetime import timedelta
import mx
#----------------------------------------
#Employee(inherit)
#----------------------------------------
class hr_employee(osv.osv):

        
    _inherit = "hr.employee"
    _columns = {

        'promotion_date' : fields.date('Promotion Date'),

    }

#----------------------------------------
#hr process(inherit)
#----------------------------------------
class hr_process_archive(osv.Model):
    """
    Inherits hr.process.archive and add promotion_date.
    """

    _inherit = "hr.process.archive"

    '''def create_new(self, cr, uid, ids, context=None):
        employee_obj = self.pool.get('hr.employee')
        for row in self.read(cr, uid, ids, context=context):
            (model_name, id) = row['reference'].split(',')
            if model_name == 'hr.salary.degree.isolate':
                employee_obj.write(cr, uid, [row['employee_id'][0]], {
                                   'promotion_date': row['approve_date']})
                return self.write(cr, uid, ids, {'state': 'approved'})
            elif model_name == 'hr.salary.degree':
                employee_obj.write(cr, uid, [row['employee_id'][0]], {
                                   'promotion_date': row['approve_date']})
            return super(hr_process_archive, self).create_new(cr, uid, ids, context=context)'''


