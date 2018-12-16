# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################
from mx import DateTime
import time
from datetime import datetime
from openerp.osv import osv, fields, orm
from openerp.tools.translate import _
import netsvc
import openerp.addons.decimal_precision as dp
from openerp import SUPERUSER_ID
from lxml import etree

#----------------------------------------
#HR Transfer Wishes
#----------------------------------------

class hr_transfer_wishes(osv.Model):
    _name = "hr.transfer.wishes"
    _description = "transfer wishes "

    _columns = {
        'reference': fields.char('Reference',size=64,readonly=True),
        'employee_id': fields.many2one('hr.employee', "Employee", domain="[('state','!=','refuse')]",readonly=True, states={'draft': [('readonly', False)]}),
        'department_id': fields.related('employee_id', 'department_id', store=True,string="Department", type="many2one", relation="hr.department",readonly=True),
        'company_id': fields.related('employee_id', 'company_id', string="Company", type="many2one", relation="res.company",readonly=True),

        'reason_id': fields.many2one('hr.transfer.reason', string='Reason',readonly=True, states={'draft': [('readonly', False)]}),
        'date': fields.date("Date",readonly=True, states={'draft': [('readonly', False)]}),
        'medical_date': fields.date("Medical Date",readonly=True, states={'draft': [('readonly', False)]}),
        'description': fields.text('Description',readonly=True, states={'draft': [('readonly', False)]}),
        'state':fields.selection([('draft','Draft'), ('confirm', 'Confirm')] ,'Status',readonly=True,),  

    	}
    def _default_company(self, cr, uid, context=None):
        List = []
        user_obj = self.pool.get('res.users')
        user = user_obj.browse(cr, uid, uid)
        company = False
        if user.company_id:
            company = user.company_id.id

        return company

    _defaults = {
        'reference':'/',
        'date': lambda * a: time.strftime('%Y-%m-%d'),
        'company_id': _default_company,
        'state': 'draft',
    }

    def set_to_draft(self,cr,uid,ids,context=None):
        """
        Mehtod that sets the state to draft.

        @return: Boolean True
        """
        self.write(cr, uid, ids, {'state': 'draft'}, context=context)
        return True

    def confirm(self,cr,uid,ids,context=None):
        """
        Mehtod that sets the state to confirm.

        @return: Boolean True
        """
        self.write(cr, uid, ids, {'state': 'confirm'}, context=context)
        return True

    def unlink(self, cr, uid, ids, context=None):
        for rec in self.browse(cr, uid, ids, context):
            if rec.state != 'draft':
                raise osv.except_osv(_('ValidateError'), _("this record is must be in draft state"))
        super(hr_transfer_wishes, self).unlink(cr, uid, ids, context=context)


    def create(self, cr, user, vals, context=None):
        """
        Override to add constrain of sequance
        @param vals: Dictionary of values
        @return: super of hr_additional_service
        """
        if ('reference' not in vals) or (vals.get('reference') == '/'):
            seq = self.pool.get('ir.sequence').get(cr, user, 'hr.transfer.wishes')
            vals['reference'] = seq and seq or '/'
            if not seq:
                raise  osv.except_osv(_('Warning'), _('No sequence defined!\nPleas contact administartor to configue sequence with code \'hr.transfer.wishes\'') )
        new_id = super(hr_transfer_wishes, self).create(cr, user, vals, context)
        return new_id



#----------------------------------------
#HR Transfer Reason
#----------------------------------------
class hr_transfer_reason(osv.osv):
    _name = "hr.transfer.reason"
    _description = "HR Transfer Reason"

    _columns = {
        'name': fields.char('Reason name', size=256,required=True),
        'company_id': fields.many2one('res.company','company',readonly=True),
    }
    def _default_company(self,cr,uid,context=None):
        List = []
        user_obj = self.pool.get('res.users')
        user = user_obj.browse(cr ,uid, uid)
        company = False
        if user.company_id:
            company = user.company_id.id
        return company

    _defaults = {
        'company_id' : _default_company,
    }



