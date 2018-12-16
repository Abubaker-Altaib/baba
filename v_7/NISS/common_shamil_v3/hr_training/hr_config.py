# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
###############################################################################

from openerp.osv import fields, osv


#----------------------------------------
# Company (Inherit)
#----------------------------------------
class res_company(osv.Model):
    """
    Inherits res.company to add feilds for training accounting configurations 
    (Training journal, Training analytic Account and Training Account).
    """

    _inherit = "res.company"
    
    _columns = {
         'training_journal_id':fields.many2one('account.journal','Training Journal',domain="[('type','=','purchase')]"),
         
         'training_account_id': fields.many2one('account.account',"Training Account",domain="[('user_type.report_type','=','expense'),('type','!=','view')]"),
         
         'training_analytic_account_id': fields.many2one('account.analytic.account',"Training Analytic Account"),
    }

#----------------------------------------
# hr.configuration (Inherit)
#----------------------------------------
class hr_config_settings_inherit(osv.osv_memory):

    """Inherits hr.config.settings to add feilds for training accounting configurations 
        (Training journal, Training analytic Account and Training Account).
    """
    _inherit = 'hr.config.settings'

    _columns = {
          'training_journal_id':fields.related('company_id','training_journal_id',type='many2one', 
                                               relation='account.journal',string='Journal',domain="[('type','=','purchase')]"),
          
          'training_account_id':fields.related('company_id','training_account_id',type='many2one', 
                                               relation='account.account',string='Account',domain="[('user_type.report_type','=','expense'),('type','!=','view')]"),
          
          'training_analytic_account_id':fields.related('company_id','training_analytic_account_id',type='many2one', 
                                                        relation='account.analytic.account',string='Analytic Account'),
    }

    def onchange_company_id(self, cr, uid, ids, company_id, context=None):
        """Method that updates related fields of the company if it has been changed.
           @param company_id: Id of company
           @return: Dictionary of values 
        """
        # update related fields
        values = super(hr_config_settings_inherit,self).onchange_company_id(cr, uid, ids, company_id, context=context).get('value',{})
        
        if company_id:
            company = self.pool.get('res.company').browse(cr, uid, company_id, context=context)
            values.update({
                'training_journal_id': company.training_journal_id.id,
                'training_account_id': company.training_account_id.id,
                'training_analytic_account_id': company.training_analytic_account_id.id,
            })
           
        return {'value': values}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
