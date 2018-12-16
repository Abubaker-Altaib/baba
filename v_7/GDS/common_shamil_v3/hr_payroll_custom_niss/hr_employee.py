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
        'employee_type': fields.selection([('employee', 'Employee'), ('trainee', 'Trainee'),
                                                ('contractor', 'Contractor'),('from_out','From Out'), ('recruit', 'Recruit')],'Employee Type' ),
        'external_transfer':fields.selection([('mandate','Mandate'),('loaning', 'Loaning'),('transfer', 'Transfer')], 'External Transfer',readonly=True,states={'draft':[('readonly', False)]}),
        'previous_institute' : fields.many2one("process.destin","Previous Institute"),
        'payroll_type':fields.selection([('paied', 'Paied'), ('unpaied', 'Unpaied')], 'Payroll',readonly=True, states={'draft':[('readonly',False)]}),
        'decion_number':fields.char('Decion Number')

    }

    def onchange_payroll_type(self, cr, uid, ids, payroll_type,context=None):
		if payroll_type == 'paied':
		   return {'value': {'salary_suspend':False}}
		elif payroll_type == 'unpaied' :
		   return {'value': {'salary_suspend':True}}
#----------------------------------------
#hr process(inherit)
#----------------------------------------
class hr_process_archive(osv.Model):
    """
    Inherits hr.process.archive and add promotion_date.
    """

    _inherit = "hr.process.archive"


    def create_new(self, cr, uid, ids, context=None):
        """
        Workflow function that changes the state to 'approved' and updates employee record degree or bonus based on the reference.
        @return: Boolean True
        """
        employee_obj = self.pool.get('hr.employee')
        super(hr_process_archive, self).create_new(cr, uid, ids, context=context)
        for row in self.read(cr, uid, ids, context=context):
            if model_name == 'hr.salary.degree':
                employee_obj.write(cr, uid, [row['employee_id'][0]], {'degree_id':id,  'promotion_date': row['approve_date']})
        return self.write(cr, uid, ids, {'state':'approved'})

class destination(osv.Model):
      _name='process.destin'

      _columns = {
        'name' : fields.char("Name",required=True),

    }
