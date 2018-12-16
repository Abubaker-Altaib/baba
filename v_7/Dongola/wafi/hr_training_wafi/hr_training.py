# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
############################################################################
from openerp.osv import fields, osv
from openerp.tools.translate import _
import netsvc

#----------------------------------------
# Training Plan
#----------------------------------------
class hr_training_plan(osv.Model):

    _inherit = "hr.training.plan"

    _columns = {
        'suggested_course_ids' :fields.one2many('hr.employee.training.suggested', 'plan_id', 'Suggested Courses', readonly=True,
                                                domain=[('type','=','hr.suggested.course'),('state','in',('approved','approved_gen','approved2','rejected'))]),
        'state': fields.selection([('draft', 'Draft'),('approved', 'First Confirmation'),
                                    ('rejected', 'Reject from General Manager'),
                                    ('confirmed', 'Second Confirmation')], 'State', readonly=True),
        'type': fields.selection([('internal', 'Internal Courses'),('external', 'External Courses')],'Type',required=True),
    }

    _defaults = {
        'state': 'draft',
       }

    def approve(self, cr, uid, ids, context=None):
        for line in self.browse(cr, uid, ids, context=context):
            if line.type == 'internal': 
                self.confirm(cr, uid, [line.id], context=context)
            else:
                for line2 in line.suggested_course_ids:
                    if line2.state in ('approved'): 
                        raise osv.except_osv(_('Error'), _('Some Suggested Courses Are Not Approved By General Manager!'))
                self.write(cr, uid, line.id, {'state':'approved'}, context=context)
        return True

    def confirm(self, cr, uid, ids, context=None):
        obj_attachment = self.pool.get('ir.attachment')
        training = self.pool.get('hr.employee.training.suggested')
        flag = False
        for line in self.browse(cr, uid, ids[0], context=context).suggested_course_ids:
            flag = True
            if line.state not in ('approved2','done'): raise osv.except_osv(_('Error'), _('Some Suggested Courses Are Not Approved'))
        if flag == False: 
            raise osv.except_osv(_('Error'), _('Plan Must Have Some Suggested Courses Before Approve!'))
        training_plan_ids = self.browse(cr, uid, ids, context=context)[0].id
        attachment_ids = obj_attachment.search(cr, uid, [('res_model','=','hr.training.plan'),('res_id','=',training_plan_ids)], context=context)
        if attachment_ids:
            self.write(cr, uid, ids, {'state':'confirmed'}, context=context)
        else:
            raise osv.except_osv(_('Warning!'), _('Their Is No Attachments To Approved'))
        return True

    def reject(self, cr, uid, ids, context=None):
        for line in self.browse(cr, uid, ids, context=context):
            for l in line.suggested_course_ids:
                wf_service = netsvc.LocalService("workflow")
                wf_service.trg_validate(uid, 'hr.employee.training',l.id ,'rejected', cr)
        return self.write(cr, uid, line.id, {'state':'rejected'}, context=context)

    def unlink(self, cr, uid, ids, context=None):
        for rec in self.browse(cr, uid, ids, context=context):
            if rec.state != 'draft':
                raise osv.except_osv(_('Warning!'),_('You cannot delete a Training Plan which is in %s state.')%(rec.state))
        return super(hr_training_plan, self).unlink(cr, uid, ids, context)

    '''def count_attachments(self, cr, uid, ids, fields, arg, context=None):
        obj_attachment = self.pool.get('ir.attachment')
        res = {}
        for record in self:
            res[record.id] = 0
            _logger.info("record now in tree view:"+record)
            attachment_ids = obj_attachment.search([('res_model','=','stock.picking.in'),('res_id','=',record.id)]).ids
            if attachment_ids:
                res[record.id] = len(attachment_ids)
        return res'''
    
    def set_to_draft(self, cr, uid, ids, context=None):
        """
    	Method that resets the workflow (delets the old and creates a new one) and
        changes the state to 'draft'.

        @return: Boolean True
        """
        self.write(cr, uid, ids, {'state': 'draft'}, context=context)
        wf_service = netsvc.LocalService("workflow")
        for id in ids:
            wf_service.trg_delete(uid, 'hr.training.plan', id, cr)
            wf_service.trg_create(uid, 'hr.training.plan', id, cr)
        return True
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

