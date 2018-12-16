# -*- coding: utf-8 -*-
############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
############################################################################

import netsvc
from openerp.osv import fields, osv, orm
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp
from openerp.addons.account_voucher.account_voucher import resolve_o2m_operations

class hr_employee_training(osv.Model):

    _inherit = "hr.employee.training"

    _columns = {
        'state': fields.selection([('draft', 'Draft'), ('requested', 'Requested from section manager'),
                                    ('confirmed', 'Confirmed from department maneger'),
                                    ('validated', 'Validated from general department'),
                                    ('approved', 'Approved Training'),
                                    ('approved2', 'Approved from General Manager'),
                                    ('approved_na', 'Approved'),
                                    ('execute', 'Transferred to "Approved Courses"'), ('done', 'Done'),
                                    ('rejected', 'Reject from general manager'),
                                    ('edit', 'Edit')], 'State', readonly=True),
        'reject_reason' :fields.text("Reject Reason"),
      }

    def approve2(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {'state':'approved_na'}, context=context)


class hr_employee_training_suggested(osv.Model):

    _inherit = "hr.employee.training.suggested"

    _columns = {
        'state': fields.selection([('draft', 'Draft'), ('requested', 'Requested from section manager'),
                                    ('confirmed', 'Confirmed from department maneger'),
                                    ('validated', 'Validated from general department'),
                                    ('approved', 'Approved Training'),
                                    ('approved_gen', 'Approved from General Manager'),
                                    ('approved2', 'Approved'),
                                    ('execute', 'Transferred to "Approved Courses"'), ('done', 'Done'),
                                    ('rejected', 'Reject'),
                                    ('edit', 'Edit')], 'State', readonly=True),
      }
    '''
    def approve_line(self, cr, uid, ids, context=None):
        for line in self.browse(cr, uid, ids, context=context): 
            return self.write(cr, uid, line.id, {'state':'approved2'}, context=context) 

    def reject_line(self, cr, uid, ids, context=None):
        for line in self.browse(cr, uid, ids, context=context): 
            return self.write(cr, uid, line.id, {'state':'rejected'}, context=context)
    '''
    def approved_gen(self, cr, uid, ids, context=None):
        for cor in self.browse(cr, uid, ids, context=context):
            if cor.plan_id.type == 'internal':
                self.approved2(cr, uid, ids, context= context)
            else:
                self.write(cr, uid, ids, {'state':'approved_gen'}, context=context)
        return True
        
    def approved2(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {'state':'approved2'}, context=context)

class hr_employee_training_approved(osv.osv):

    _inherit = "hr.employee.training.approved"

    _columns = {
        'state': fields.selection([('draft', 'Draft'), ('requested', 'Requested from section manager'),
                                    ('confirmed', 'Confirmed from department maneger'),
                                    ('validated', 'Validated from general department'),
                                    ('approved2', 'Approved from General Manager'),
                                    ('approved', 'Approved from National Council'),
                                    ('execute', 'Transferred to "Approved Courses"'), ('done', 'Done'),
                                    ('rejected', 'Reject from general manager'),], 'State', readonly=True),
        'reject_reason' :fields.text("Reject Reason"),
      }


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

