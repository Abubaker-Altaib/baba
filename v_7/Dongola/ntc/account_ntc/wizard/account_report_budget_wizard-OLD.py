#    Copyright (C) 2011-2017 NCTR (<http://www.nctr.sd>).
#
##############################################################################

import time
from openerp.osv import fields, osv

class AccountReportBudgetWizard(osv.osv_memory):
  
    _inherit = "account.report.budget"

    _columns = {
        'summary': fields.boolean('Summary'),
        'closure': fields.char('Closure', ),
        'unit_type':fields.selection([('ministry', 'ministry'), ('locality', 'locality'), ('other', 'other')], "Type"),
}

    def _get_analytic_account(self, cr, uid, context=None):
        """
        Method to return the root analytic account in logged in user     
        @return: int root analytic account id or False
        """
        analytic_obj = self.pool.get('account.analytic.account')
        company = self.pool.get('res.users').browse(cr, uid, uid, context=context).company_id.id
        analytic_account = self.pool.get('account.analytic.account').search(cr, uid, [('parent_id', '=', False), ('company_id','=', company)], 
                                                                            context=context, limit=1)
        #Use this code for none Accounting user       
        if not self.pool.get('res.users').has_group(cr, uid, 'account.group_account_user'):
            analytic_account = self.pool.get('account.analytic.account').search(cr, uid, [('type', '=', 'normal')], context=context)
            temp_analytic = []
            cr.execute("SELECT gid as group_id FROM res_groups_users_rel WHERE uid='%s'" % (str(uid),)) 
            #group_ids = list(cr.fetchall())
            user_group_ids = [x for x, in cr.fetchall()]
            for analytic in analytic_obj.browse(cr, uid, analytic_account, context=context ):
                if set([group.id for group in analytic.group_ids]) & set(user_group_ids):
                    temp_analytic.append(analytic.id)
            analytic_account = temp_analytic
        return analytic_account and analytic_account[0] or False

    _defaults = {
            'summary': 0,
            'report_type': '1',
            'date_from': time.strftime('%Y-01-01'), 
            'date_to': time.strftime('%Y-%m-%d'),
            'chart_analytic_account_id': _get_analytic_account,
    }
    
    def onchange_fiscalyear_id(self, cr, uid, ids, fiscalyear_id = False, context = None):
        """
        Inherit method to update date_from, date_to values

        @param fiscalyear_id: fiscalyear_id
        @return: dictionary of values 
        """
        fiscalyear = self.pool.get('account.fiscalyear').browse(cr, uid, fiscalyear_id, context=context)
        analytic_obj = self.pool.get('account.analytic.account')
        analytic_domain = [('type','in',('normal','view'))]
        #Use this code for none Accounting user       
        if not self.pool.get('res.users').has_group(cr, uid, 'account.group_account_user'):
            analytic_account = self.pool.get('account.analytic.account').search(cr, uid, [('type', '=',('normal','view'))], context=context)
            temp_analytic = []
            cr.execute("SELECT gid as group_id FROM res_groups_users_rel WHERE uid='%s'" % (str(uid),)) 
            #group_ids = list(cr.fetchall())
            user_group_ids = [x for x, in cr.fetchall()]
            for analytic in analytic_obj.browse(cr, uid, analytic_account, context=context ):
                if set([group.id for group in analytic.group_ids]) & set(user_group_ids):
                    temp_analytic.append(analytic.id)
            analytic_domain = [('id','in',temp_analytic)]

        res = {'domain':{'chart_analytic_account_id':analytic_domain}}
        if fiscalyear_id:
            res.update({'value': {'date_from': fiscalyear.date_start ,'date_to':  fiscalyear.date_stop, }})
        return res

    def print_report(self, cr, uid, ids, context=None):
        """
        Method to send wizards fields value to the report
        @return: dictionary call the report service 
        """

        res = super(AccountReportBudgetWizard, self).print_report(cr, uid, ids, context)


        #Mudathir : Get analytic_account From Wizard to set it in report
        anl_acc_name = self.pool.get('account.analytic.account').read(cr, uid,[self.read(cr, uid,ids,[], context)[0]['chart_analytic_account_id'][0]],['name'], context)[0]['name']
        res['datas']['form'].update({'chart_analytic_account_report':anl_acc_name})


        summary = res['datas']['form']['summary']
        if summary and res['datas']['form']['type_selection']=='detail':
            res['report_name'] = 'account.budget.summary'
        if summary and res['datas']['form']['type_selection']=='consol':
            res['report_name'] = 'account.budget.consol'
        if summary and res['datas']['form']['type_selection']=='dept':
            res['report_name'] = 'account.budget.dep'
        if summary and res['datas']['form']['type_selection']=='unit':
            res['report_name'] = 'account.budget.unit'
        return res
        '''

        data ={'ids':ids,'form': self.read(cr, uid, ids, [])[0]}
        data['form'].update({'chart_account_id': data['form']['chart_account_id'] and data['form']['chart_account_id'][0],
                             'fiscalyear_id': data['form']['fiscalyear_id'] and data['form']['fiscalyear_id'][0],
                             'period_from': data['form']['period_from'] and data['form']['period_from'][0],
                             'period_to': data['form']['period_to'] and data['form']['period_to'][0],
                             'chart_analytic_account_id': data['form']['chart_analytic_account_id'] and data['form']['chart_analytic_account_id'][0],
                             'accuracy':data['form']['accuracy']})
        if data['form']['report_type'] == '3':
            return {'type': 'ir.actions.report.xml', 'report_name': 'account.account.budget.company.report', 'datas': data}
        return {'type': 'ir.actions.report.xml', 'report_name': 'account.account.budget', 'datas': data}'''


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
