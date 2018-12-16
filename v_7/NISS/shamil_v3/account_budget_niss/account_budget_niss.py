# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################
import time
from osv import fields,osv
from datetime import datetime
import openerp.addons.decimal_precision as dp

class account_budget_niss(osv.osv): 
    _name = "account.budget.niss"

    _columns = {
            'number': fields.char('Number', size=156),
            'name': fields.char('Name', size=256),
            'date': fields.date('Date', select=True),
            'date_actual': fields.date('Actual Date', select=True),
            'type' : fields.selection([('main','Main Budget'),('detail','Detail Budget')], 'Type'),
            'fiscalyear_id': fields.many2one('account.fiscalyear.budget','Year'),
            'line_ids': fields.one2many('account.budget.niss.line', 'budget_niss_id', 'Budget lines'),
            'state': fields.selection([('draft','Draft'),('confirmed','Confirmed')], 'State', readonly=True, select=True),
    }

    def _get_type(self, cr, uid, context=None):
        """
        Get type of Budget
        @return : type or False 
        """
        if context is None:
            context = {}
        return context.get('type', False)

    _defaults = {
        'date': lambda *a: time.strftime('%Y-%m-%d'),
        'date_actual': lambda *a: time.strftime('%Y-%m-%d'),
        'state': 'draft',
        'number':'/',
        'type': _get_type,
    }
   
    def create(self, cr, user, vals, context=None):
        """
        Override to add constrain of sequance
        @param vals: Dictionary of values
        @return: super of exchange_order
        """
        if ('number' not in vals) or (vals.get('number') == '/'):
            seq = self.pool.get('ir.sequence').get(cr, user, 'account.budget.niss')
            vals['number'] = seq and seq or '/'
            if not seq:
                raise  osv.except_osv(_('Warning'), _('No sequence defined!\nPleas contact administartor to configue sequence with code \'account.budget.niss\'') )
        new_id = super(account_budget_niss, self).create(cr, user, vals, context)
        return new_id

    def get_actual_amount(self, cr, uid,ids, context=None):
        """
        return actual amount of budget line
        """
        budget_line_obj= self.pool.get('account.budget.niss.line')
        account_obj= self.pool.get('account.account')
        if context is None:
            context = {}
        ctx = context.copy()
        for record in self.browse(cr, uid, ids , context):
            year, month, date = record.date_actual.split('-')
            ctx['date_from'] =datetime(int(year),1, 1).strftime("%Y-%m-%d")
            ctx['date_to'] =  record.date_actual
            ctx['state'] = 'all'
  
            for line in record.line_ids:
                if line.account_id: 
                    result = account_obj.read(cr, uid, line.account_id.id, ['balance'], ctx)
                    budget_line_obj.write(cr, uid, [line.id], {'actual_amount':result.get('balance')}, context)


account_budget_niss()
 
class account_budget_niss_line(osv.osv): 
    _name = "account.budget.niss.line"

    _columns = {
            'name': fields.char('Name', size=256),
            'approved_department': fields.char('Approved Department', size=156),
            'Benefit_department': fields.char('Benefit Department', size=156),
	    'account_id' : fields.many2one('account.account','Account'),
	    #'currency_id' : fields.many2one('res.currency','Currency'),
	    'plannet_amount': fields.float('Plannet Amount', digits_compute=dp.get_precision('Account')),
            'actual_amount': fields.float('Actual Amount', digits_compute=dp.get_precision('Account')),
	    'budget_niss_id' : fields.many2one('account.budget.niss','Budget Niss'),
            #'balance': fields.float('Balance', digits_compute=dp.get_precision('Account')),
    }
   

account_budget_niss_line()

#----------------------------------------------------------
# Account Account(Inherit)
#----------------------------------------------------------
class account_account(osv.Model):

    """ Inherit account Model to add new boolean field used in budget department:
    """
    _inherit = "account.account"
    _columns = {
                'budget_account':fields.boolean('Appear to Budget Department'),
		}

    _defaults = {
		'budget_account':False,
		}




