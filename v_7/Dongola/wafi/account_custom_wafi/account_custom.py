# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

from openerp.osv import osv, fields, orm
from datetime import datetime  
from datetime import timedelta  
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, DATETIME_FORMATS_MAP, float_compare
from openerp.tools.translate import _

#----------------------------------------------------------
# Account Account (Inherit)
#----------------------------------------------------------
class account_account(osv.Model):

    _inherit = "account.account"

    _columns = {
        'ceiling': fields.float('Ceiling'),
        'min_ceiling': fields.float('Minimum Ceiling'),
        'payment_ceiling': fields.float('Payment Ceiling'),
    }

class account_journal(osv.Model):

    _inherit = 'account.journal'

    def check_ceiling(self, cr, uid, ids, context=None):
           
            journal = self.browse(cr, uid, ids, context=context)[0]
           
            recipient_partners = []
            for user in journal.user_id:
                
                recipient_partners.append(
                    (4, user.partner_id.id)
                )       
            ceil_msg = []
            msg = ""
            flag= False
            if journal.default_debit_account_id.balance >= journal.default_debit_account_id.ceiling :
                ceil_msg.append(_(" Maximum ceiling %s for %s ' %s '  has been exceed") % (journal.default_debit_account_id.ceiling,journal.default_debit_account_id.name,journal.default_debit_account_id.balance))
                flag = True

            if journal.default_credit_account_id.balance >= journal.default_credit_account_id.ceiling:
               ceil_msg.append(_("\nMaximum ceiling %s for %s ' %s '  has been exceed") % (journal.default_credit_account_id.ceiling,journal.default_credit_account_id.name,journal.default_credit_account_id.balance))
               flag = True

                #raise orm.except_orm(_('Warning !'), _('(Maximum ceiling %s for %s " %s " has been exceed')%(account.ceiling,account.name,account.balance))
            if journal.default_debit_account_id.balance <= journal.default_debit_account_id.min_ceiling:
                ceil_msg.append(_("\nMinimum ceiling %s for %s ' %s ' has been exceed") %  (journal.default_debit_account_id.min_ceiling,journal.default_debit_account_id.name,journal.default_debit_account_id.balance))
                flag = True


            if journal.default_credit_account_id.balance <= journal.default_credit_account_id.min_ceiling:
                ceil_msg.append(_("\nMinimum ceiling %s for %s ' %s ' has been exceed") % (journal.default_credit_account_id.min_ceiling,journal.default_credit_account_id.name,journal.default_credit_account_id.balance))
                flag = True
 
            if flag == True:
                for msg_rec in ceil_msg:
                    msg = min_msg +','+ msg
                post_vars = {'subject': "notification about ceiling",
                             'body': msg,
                             'partner_ids': recipient_partners,} # Where "4" adds the ID to the list 
                                       # of followers and "3" is the partner ID 
                thread_pool = self.pool.get('mail.thread')
                thread_pool.message_post(
                    cr, uid, False,
                    type="notification",
                    subtype="mt_comment",
                    context=context,
                    **post_vars)

            raise orm.except_orm(_('Warning !'), _('Minimum ceiling %s for %s " %s " has been exceed')%(account.min_ceiling,account.name,account.balance))
            return True

    
        

class account_period(osv.Model):

    _inherit = "account.period"

    def name_search(self, cr, uid, name, args=None, operator='ilike', context=None, limit=100):
        """
        Inherit name_search method to display only open period 
        unless order close period by sending closed=True in context
        
        @return: super name_search
        """
        if args is None:
            args = []
        if context is None:
            context = {}
        if not context.get('closed',False):
            args.append(('state', '=', 'draft'))
        return super(account_period, self).name_search(cr, uid, name, args=args, operator='ilike', context=context, limit=limit)

    def action_draft(self, cr, uid, ids, context=None):
        """
        Inherit action_draft method to prevent reopening statement
        
        @return: super action_draft
        """
        if self.search(cr, uid, [('id', 'in', ids), ('fiscalyear_id.state', '!=', 'draft')], context=context):
                raise osv.except_osv(_('Warning!'), _('You can not re-open a period which belongs to closed fiscal year'))
        return super(account_period, self).action_draft(cr, uid, ids, context)

class account_fiscalyear(osv.Model):
    """
    Inherit fiscal year model to modify it's states according to government requirements
    """
    _inherit = "account.fiscalyear"

    _columns = {
        'state': fields.selection([('draft', 'Open'), ('locked_temp', 'Locked Temporarily'),
                           ('open_ext_period' , 'Open Extension Period'),
                           ('close_ext_period', 'Close Extension Period'),
                           ('first_lock', 'First Lock'), ('done', 'Final Lock')],
                          'State',size=64, readonly=True),
    }

    def action_locked_temporarily(self, cr, uid, ids, context=None):
        """
        Method to check that all fiscal year's periods closed or not.
        
        @return: change record state to 'locked temporarily' or raise exception
        """
        if self.pool.get('account.period').search(cr, uid, [('state','=','draft'),('fiscalyear_id','in',ids)], context=context):
            raise orm.except_orm(_('Error'), _('You Must Close Open Periods First'))
        return self.write(cr, uid, ids, {'state': 'locked_temp'}, context=context)

    def action_close_extension_period(self, cr, uid, ids, context=None):
        """
        @return Change record state to 'Close Extension Period'.
        """
        return self.write(cr, uid, ids, {'state': 'close_ext_period'}, context=context)

    def action_first_lock(self, cr, uid, ids, context=None):
        """
        @return: Change record state to 'First Lock'.
        """
        self.write(cr, uid, ids, {'state': 'first_lock'}, context=context)
        return {
            'id': 'account_custom.action_account_pl_close',
            'context': {'default_fiscalyear_id': ids}
        }

#----------------------------------------------------------
# Account Move Line(Inherit)
#----------------------------------------------------------
class account_move_line(osv.Model):

    _inherit = 'account.move.line'

    def _query_get(self, cr, uid, obj='l', context=None):
        """
        use in account arabic reports and chart of account to balance the credit and debit
        
        @return: string of the where statement
        """
 
        fiscalyear_obj = self.pool.get('account.fiscalyear')
        company_obj = self.pool.get('res.company')
        fiscalperiod_obj = self.pool.get('account.period')
        account_obj = self.pool.get('account.account')
        journal_obj = self.pool.get('account.journal')
        initial_bal = context.get('initial_bal', False)

        fiscalyear_ids = []
        if context is None:
            context = {}
        #Only Valid Move Lines (BALANCE MOVES)
        query = obj+".state <> 'draft' "
        #Filter by Company
        if context.get('company_id', False):
            query += " AND " +obj+".company_id = %s" % context['company_id']
        

        if context.get('unit_type', False):
            if context.get('unit_type', False) == 'ministry':
                company_ids = company_obj.search(cr,uid, [ ('type', '=', 'other')])
            elif context.get('unit_type', False) == 'locality':
                company_ids = company_obj.search(cr,uid, [ ('type', '=', 'loc_sub')])
        else:
            types=('other','loc_sub')
            company_ids = company_obj.search(cr,uid, [ ('type', 'in', types)])
        company_ids2 = ','.join(map(str, company_ids))
        query += " AND " +obj+".company_id in (%s)" % company_ids2

        #Filter by Move State
        if context.get('state', False):
            if type(context['state']) in (list,tuple) :
                query += " AND "+obj+".move_id IN (SELECT id FROM account_move WHERE state !='reversed') " 
               # query += " AND "+obj+".move_id IN (SELECT id FROM account_move WHERE state IN ("+st+")) "
            elif context['state'].lower() != 'all':
                query += " AND "+obj+".move_id IN (SELECT id FROM account_move WHERE account_move.state != '"+context['state']+"') "
        #Get Selected FiscalYear
        if not context.get('fiscalyear', False):
            if context.get('all_fiscalyear', False):
                fiscalyear_ids = fiscalyear_obj.search(cr, uid, [('company_id', 'in', company_ids)])
            else:
                if context.get('date_from', False):
                    #fiscalyear_ids = fiscalyear_obj.search(cr, uid, [])
                    date_from=context.get('date_from', False)
                    date_from2 = datetime.strptime( date_from, '%Y-%m-%d')
                    f_code=date_from2.year  
                    fiscalyear_ids = fiscalyear_obj.search(cr,uid, [('company_id', 'in', company_ids), ('code', '=', f_code)])
                else:
                    fiscalyear_ids = fiscalyear_obj.search(cr, uid, [('company_id', 'in', company_ids)])
                    
        else:
            #make the context['fiscalyear'] in one dimention list or ids
            fiscalyear_ids = type(context['fiscalyear']) is list and context['fiscalyear'] or [context['fiscalyear']]
        fiscalyear_clause = (','.join(map(str, fiscalyear_ids)))
        #Duration Filters

        if context.get('date_from', False) and context.get('date_to', False):
 
            if initial_bal:
 
                init_period = fiscalperiod_obj.search(cr, uid, [('special', '=', True), ('fiscalyear_id', 'in', fiscalyear_ids)])
                date_start = fiscalperiod_obj.browse(cr, uid, init_period[0], context=context).date_start
                
                query += " AND "+obj+".period_id IN (SELECT id FROM account_period WHERE fiscalyear_id IN (%s) ) " % (fiscalyear_clause,)

                date_from=context['date_from']
                if context.get('date_from', False)==date_start:
                    date_1 = datetime.strptime(date_from, DEFAULT_SERVER_DATE_FORMAT)
                    date_from= date_1+timedelta(days=1)
                    query += " AND " +obj+".move_id IN (SELECT id FROM account_move WHERE date <='%s') " %(context['date_from'],)
                query += " AND " +obj+".move_id IN (SELECT id FROM account_move WHERE date <'%s') " %(date_from,)

            else:
                if context['type']=='statement':
   
                    query += " AND " +obj+".move_id IN (SELECT id FROM account_move WHERE date >= '%s' AND date <= '%s') "%(context['date_from'],context['date_to']) 
                elif   context['type']=='balance':
                    init_period = fiscalperiod_obj.search(cr, uid, [('special', '=', True), ('fiscalyear_id', 'in', fiscalyear_ids)])

                    date_start = fiscalperiod_obj.browse(cr, uid, init_period[0], context=context).date_start
                    date_from=context['date_from']
                    if context.get('date_from', False)==date_start:
                        date_1 = datetime.strptime(date_from, DEFAULT_SERVER_DATE_FORMAT)
                        date_from= date_1+timedelta(days=1)
                        query += " AND " +obj+".move_id IN (SELECT id FROM account_move WHERE date > '%s' AND date <= '%s') "%(date_from,context['date_to']) 
                    query += " AND " +obj+".move_id IN (SELECT id FROM account_move WHERE date >= '%s' AND date <= '%s') "%(context['date_from'],context['date_to']) 
        if context.get('period_from', False) and context.get('period_to', False) and not context.get('periods', False) and context.get('type', False)!='statement':
            if initial_bal:
                period_company_id = fiscalperiod_obj.browse(cr, uid, context['period_from'], context=context).company_id.id
                first_period = fiscalperiod_obj.search(cr, uid, [('company_id', '=', period_company_id), ('fiscalyear_id', 'in', fiscalyear_ids)], order='date_start')
                context['periods'] = fiscalperiod_obj.build_ctx_periods(cr, uid, first_period[0], first_period[first_period.index(context['period_from'])-1])
            else:
                context['periods'] = fiscalperiod_obj.build_ctx_periods(cr, uid, context['period_from'], context['period_to'])

        if context.get('periods', False) and context.get('type', False)!='statement':
            period_ids = ','.join(map(str, context['periods']))
            query += " AND "+obj+".period_id IN (SELECT id FROM account_period WHERE fiscalyear_id IN (%s) AND id IN (%s)) " % (fiscalyear_clause, period_ids)
        else:
            sub_query = ""
            if not context.get('date_from', False) or context.get('period_from', False):
                special = initial_bal and (not context.get('date_from', False))
                sub_query = "AND special = %s"%(special,)
            query += " AND "+obj+".period_id IN (SELECT id FROM account_period WHERE fiscalyear_id IN (%s) %s) " % (fiscalyear_clause, sub_query)

        #Filter by Journal
        #situation_journal = set(journal_obj.search(cr, uid, [('type', '=', 'situation')], context=context))
        #selected_journals = set(context.get('journal_ids', False) or journal_obj.search(cr, uid, [], context=context))
        #TEST: situation journal when opening balance & not
        #journal_ids = context.get('selected_journals', False) and selected_journals or \
          #  (initial_bal and list(selected_journals | situation_journal) or list(selected_journals-situation_journal))
       # if journal_ids:
           # query += ' AND '+obj+'.journal_id IN (%s) ' % ','.join(map(str, journal_ids))
        #if not context.get('selected_journals', False) and not initial_bal and situation_journal:
                #query += ' AND '+obj+'.journal_id NOT IN (%s) ' % ','.join(map(str, situation_journal))
        #Filter by chart of Account
        if context.get('chart_account_id', False):
            child_ids = account_obj._get_children_and_consol(cr, uid, [context['chart_account_id']], context=context)
            query += ' AND '+obj+'.account_id IN (%s) ' % ','.join(map(str, child_ids))
        #Filter by Move Line Statement
        if 'statement_id' in context:
            if context.get('statement_id', False):
                query += ' AND '+obj+'.statement_id IN (%s) ' % ','.join(map(str, context['statement_id']))
            else:
                query += ' AND '+obj+'.statement_id IS NULL '
        #Filter by Move Line
        if context.get('move_line_ids', False):
            query += ' AND '+obj+'.id IN (%s) ' % ','.join(map(str, context['move_line_ids']))
        #Filter by Analytic Account Type
        if context.get('analytic_display', False):
            query += ' AND '+obj+".analytic_account_id IN (SELECT id FROM account_analytic_account WHERE analytic_type=%s) " % (context.get('analytic_display', False).id,)
 
        return query

class account_voucher(osv.osv):
    """
    Customize account voucher. 
    """
    _inherit='account.voucher'

    _columns = {
        'invoice_id': fields.many2one('account.invoice','Invoice'),
    }

class res_company(osv.Model):
    """
    Inherit company model to add restricted payment scheduler as configurable option
    """
    _inherit = "res.company"
    
    _columns = {
        'interval_number': fields.integer('Interval Number'),
    }
    
    _defaults = {
        'interval_number': 2,
    }

#----------------------------------------------------------
#  Account Config (Inherit)
#----------------------------------------------------------
class account_config_settings(osv.osv_memory):
    """
    Inherit account configuration setting model to define and display 
    the restricted payment scheduler' field value
    """
    _inherit = 'account.config.settings'

    _columns = {
        'interval_number': fields.related('company_id', 'interval_number', type='integer', string='Interval Number'),
    }

    def onchange_company_id(self, cr, uid, ids, company_id, context=None):
        """
        Update dict. of values to set interval_number depend on company_id
        @param company_id: user company_id
        @return: dict. of new values
        """
        # update related fields
        values =super(account_config_settings,self).onchange_company_id(cr, uid, ids, company_id, context=context).get('value',{})
        
        if company_id:
            company = self.pool.get('res.company').browse(cr, uid, company_id, context=context)
            values.update({
                'interval_number': company.interval_number
            })
           
        return {'value': values}


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
