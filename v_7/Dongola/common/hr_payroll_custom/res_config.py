# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
###############################################################################

from openerp.osv import fields, osv

class hr_config_settings_inherit(osv.osv_memory):

    _inherit = 'hr.config.settings'
    """Inherits hr.config.settings to add feilds for the configuration of account and tax.
    """
    _columns = {
          'company_id': fields.many2one('res.company', 'Company', required=True),
          'hr_journal_id':fields.related('company_id','hr_journal_id',type='many2one', relation='account.journal',string='HR Journal' ,domain="[('type','=','purchase')]"),
		  'hr_rev_journal_id':fields.related('company_id','hr_rev_journal_id',type='many2one', relation='account.journal',string='HR Revenue Journal' ,domain="[('type','=','sale')]"),
          'stamp_account_id':fields.related('company_id','stamp_account_id',type='many2one', relation='account.account',string='Stamp Account',domain="[('user_type.report_type','=','expense'),('type','!=','view')]"),
          'group_tax': fields.boolean("Use Taxes",
                      implied_group='hr_payroll_custom.group_tax',
                      help="""Allows you to use taxes."""),
    }



    def _default_company(self, cr, uid, context=None):
        """Method that returns the defualt company of user.
           @return: Id of user's company
        """
        user = self.pool.get('res.users').browse(cr, uid, uid, context=context)
        return user.company_id.id

 
    _defaults = {
        'company_id': _default_company,
    }

    def create(self, cr, uid, values, context=None):
        """Method that explicitly writes related fields to avoid bugs .
          @param values: Dictionary of values
          @return: Id of the created record
        """
        id = super(hr_config_settings_inherit, self).create(cr, uid, values, context)
        # Hack: to avoid some nasty bug, related fields are not written upon record creation.
        # Hence we write on those fields here.
        vals = {}
        for fname, field in self._columns.iteritems():
            if isinstance(field, fields.related) and fname in values:
                vals[fname] = values[fname]
        self.write(cr, uid, [id], vals, context)
        return id

    def onchange_company_id(self, cr, uid, ids, company_id, context=None):
        """Method that updates related fields of the company.
           @param company_id: Id of company
           @return: Dictionary of values 
        """

        values = {}
        if company_id:
            company = self.pool.get('res.company').browse(cr, uid, company_id, context=context)
            values = {
                'hr_journal_id': company.hr_journal_id.id,
                'hr_rev_journal_id':company.hr_rev_journal_id.id,
                'stamp_account_id': company.stamp_account_id.id,
            }
           
        return {'value': values}
