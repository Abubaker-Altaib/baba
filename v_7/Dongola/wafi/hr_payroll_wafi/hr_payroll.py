# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
############################################################################

from openerp.osv import fields, osv

class hr_employee_substitution(osv.osv):

    _inherit="hr.employee.substitution"

    _columns = {
        'create_uid':  fields.many2one('res.users', 'Responsible',readonly=True),
        'job_id': fields.many2one('hr.job', 'Job',readonly=True,states={'draft':[('readonly', False)]}),
        'state': fields.selection([('draft', 'Draft'), ('complete', 'Complete'),
                                   ('confirm', 'Confirm'),('approve', 'Approve'),
                                   ('cancel', 'Cancel'),('done', 'Done')],'State', readonly=True),
    }

    def is_manger(self, cr, uid, ids, context={}):
        is_manger=False
        for rec in self.browse(cr, uid, ids):
            if rec.employee_id.parent_id \
                and rec.employee_id.parent_id.user_id and rec.employee_id.parent_id.user_id.id==rec.create_uid.id:
                is_manger=True
        return is_manger


class hr_employee_exempt_tax(osv.osv):

    _inherit="hr.employee.exempt.tax"

    _columns = {
        'state': fields.selection([('draft', 'Draft'), ('complete', 'Complete'),
                                   ('confirm', 'Confirm'),('validate', 'validate'),
                                   ('approved', 'Approve'),('reject', 'reject')],'State', readonly=True),
    }

    def action_complete(self, cr, uid, ids, context=None):
        """
        Workflow function
        
        @return: change record state to 'complete'
        """
        return self.write(cr, uid, ids, {'state': 'complete'}, context=context)

    def action_confirm(self, cr, uid, ids, context=None):
        """
        Workflow function
        
        @return: change record state to 'confirm'
        """
        return self.write(cr, uid, ids, {'state': 'confirm'}, context=context)

    def action_validate(self, cr, uid, ids, context=None):
        """
        Workflow function
        
        @return: change record state to 'validate'
        """
        return self.write(cr, uid, ids, {'state': 'validate'}, context=context)

    def action_reject(self, cr, uid, ids, context=None):
        """
        Workflow function
        
        @return: change record state to 'reject'
        """
        return self.write(cr, uid, ids, {'state': 'reject'}, context=context)

