# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################
import time
import datetime
from datetime import datetime
from openerp.osv import osv, fields, orm
from openerp.tools.translate import _
import netsvc
import re

#----------------------------------------------------------
# Res Company (Inherit)
#----------------------------------------------------------
class res_company(osv.Model):
    """ inherit company model to add code field """
    _inherit = "res.company"

    _columns = {
        'code': fields.char('Code', size=6, required=True), 
    }

#----------------------------------------------------------
# Account Account Type (Inherit)
#----------------------------------------------------------
class account_account_type(osv.Model):
    """ Inherit account type model to add analytic_required field , add ('pl', 'profit and loss') in close_method field """

    _inherit =  "account.account.type"

    _columns = {
            'analytic_required': fields.boolean('Analytic Required', help="Check if this type of account has go through analytic check."), 
            'close_method': fields.selection([('none', 'None'), ('balance', 'Balance'), ('pl', 'profit and loss'), ('detail', 'Detail'), 
                                              ('unreconciled', 'Unreconciled')], 'Deferral Method', required=True, 
                                             help="""Set here the method that will be used to generate the end of year journal entries for all the accounts of this type.
            'None' means that nothing will be done.
            'Balance' will generally be used for cash accounts.
            'Detail' will copy each existing journal item of the previous year, even the reconciled ones.
            'Unreconciled' will copy only the journal items that were unreconciled on the first day of the new fiscal year."""), 
    }
    _sql_constraints = [
        ('name_uniq', 'unique (name)', 'The name of the account type must be unique !'),
    ]
    def copy(self, cr, uid, id, default=None, context=None):
        if context is None:
            context = {}
        if default is None:
            default = {}
        name = self.read(cr, uid, [id], ['name'], context)[0]['name']
        default.update({'name': _('%s (copy)') % name})
        data = self.copy_data(cr, uid, id, default, context)
        new_id = self.create(cr, uid, data, context)
        self.copy_translations(cr, uid,  new_id, new_id, context)
        return new_id
 
    def search(self, cr, uid, args, offset=0, limit=None, order=None, 
            context=None, count=False):
        """
        Search for records based on a search domain.

        @param args: list of tuples specifying the search domain [('field_name', 'operator', value), ...]. Pass an empty list to match all records.
        @param offset: optional number of results to skip in the returned values (default: 0)
        @param limit: optional max number of records to return (default: **None**)
        @param order: optional columns to sort by (default: self._order=id )
        @param count: optional (default: **False**), if **True**, returns only the number of records matching the criteria, not their ids
        @return: id or list of ids of records matching the criteria
        """
        if context is None:
            context = {}
        pos = 0
        obj_data = self.pool.get('ir.model.data')
        obj_financial_report = self.pool.get('account.financial.report') 
        financial_report_ref = {
            'asset': obj_financial_report.browse(cr, uid, obj_data.get_object_reference(cr, uid, 'account', 'account_financial_report_assets0')[1], context=context), 
            'liability': obj_financial_report.browse(cr, uid, obj_data.get_object_reference(cr, uid, 'account', 'account_financial_report_liability0')[1], context=context), 
            'income': obj_financial_report.browse(cr, uid, obj_data.get_object_reference(cr, uid, 'account', 'account_financial_report_income0')[1], context=context), 
            'expense': obj_financial_report.browse(cr, uid, obj_data.get_object_reference(cr, uid, 'account', 'account_financial_report_expense0')[1], context=context), 
        }
        while pos < len(args):
            if args[pos][0] == 'report_type':
                ids = financial_report_ref.get(args[pos][2]) and [type.id for type in financial_report_ref.get(args[pos][2]).account_type_ids] or []
                
                args[pos] = ('id', 'in', ids)
            pos += 1
        return super(account_account_type, self).search(cr, uid, args, offset, limit, order, context=context, count=count)


#----------------------------------------------------------
# Account Account (Inherit)
#----------------------------------------------------------
class account_account(osv.Model):

    _inherit = "account.account"

    """ Inherit to add domain in parent_id field """

    _columns = {
        'parent_id': fields.many2one('account.account', 'Parent', ondelete='cascade', 
                                     domain="[('type','=','view'),('company_id', '=', company_id)]"), 
    }

    def _code_check(self, cr, uid, ids, context=None):
        for acc in self.browse(cr, uid, ids, context=context):
            if not re.match(r'^[0-9_\*]*$', acc.code):
                return False
        return True

    _constraints = [
         (_code_check, "You have unsupported characters in your account code! available character \n [0-9 and _]", ['code']), 
    ]

#----------------------------------------------------------
# Account Journal(Inherit)
#----------------------------------------------------------
class account_journal(osv.Model):

    """ Inherit account journal to :
                       add special field 
                       change propertiy of user_id field from many2one to many2many
                       add new journal type
    """
    _inherit = "account.journal"

    _columns = {
        'special': fields.boolean("Special", help="Check it if your journal is Special Expense/Revenue/ voucher Journal or a Petty Cash Journal."), 
        'user_id': fields.many2many('res.users', 'account_journal_tax_user', 'journal_id', 'user_id', 'User'), 
        'type': fields.selection([('sale', 'Sale'), ('sale_refund', 'Sale Refund'), ('purchase', 'Purchase'), 
                            ('purchase_refund', 'Purchase Refund'), ('cash', 'Cash'), ('bank', 'Bank and Checks'), 
                            ('general', 'General'), ('situation', 'Opening/Closing Situation'), ('profit_loss', 'Profit & Loss')], 
                            'Type', size=32, required=True, 
                                 help="Select 'Sale' for customer invoices journals."\
                                 " Select 'Purchase' for supplier invoices journals."\
                                 " Select 'Cash' or 'Bank' for journals that are used in customer or supplier payments."\
                                 " Select 'General' for miscellaneous operations journals."\
                                 " Select 'Opening/Closing Situation' for entries generated for new fiscal years."\
                                 " Select 'Profit & Loss' for entries generated for closing fiscal year revenue & expense."), 
    }

    _defaults = {
        'user_id': lambda self, cr, uid, context:[], 
    }

    def onchange_type(self, cr, uid, ids, ttype, context=None):
        """
        Change in special field depend on journal type
        @param ttype: type of journal
        @return: Dictinory of value
        """
        return {'value':{'special': False,'cash_control': ttype=='cash', 'with_last_closing_balance': ttype=='cash'}}

    def create_sequence(self, cr, uid, vals, context=None):
        """ 
        Create new entry sequence for every new Journal
        @param vals: Dictinory of record values 
        @return: created sequence
        """
        seq_pool = self.pool.get('ir.sequence')
        seq_typ_pool = self.pool.get('ir.sequence.type')
        name = vals['name']
        code = vals['code'].lower()
        types = {
            'name': name, 
            'code': code
        }
        seq_typ_pool.create(cr, uid, types)
        seq = {
            'name': name, 
            'code': code, 
            'active': True, 
            'prefix': code + "/%(year)s/", 
            'padding': 4, 
            'number_increment': 1
        }
        if 'company_id' in vals:
            seq['company_id'] = vals['company_id']
            seq['prefix'] = self.pool.get('res.company').browse(cr, uid, [vals['company_id']])[0].code or ' ' + "/" + seq['prefix'] or ' '
        return seq_pool.create(cr, uid, seq)


    def create(self, cr, uid, vals, context=None):
        user = vals.get('user_id')
        if isinstance(user,int):
            vals.update({'user_id':[(6,0,[user])]})
        return super(account_journal,self).create(cr, uid, vals,context=context)

#----------------------------------------------------------
# Account Move(Inherit)
#----------------------------------------------------------
class account_move(osv.Model):
    """ Inherit account move to :
        add new state
        change in properties of some fields
    """
    _inherit = 'account.move'

    _columns = {
        'state': fields.selection([('draft', 'Draft'), ('completed', 'Completed'), 
                 ('posted', 'Posted'), ('closed', 'Closed'), ('analytic', 'Analytic Check'), 
                 ('reversed', 'Reverse'), ('to_review_closer', 'To Review(Closer)'), 
                 ('to_rev_manager', 'To Review(Manager)'), ('to_review_analytic', 'To Review(From Analytic)')], 
                 'State', select=True, readonly=True), 
        'period_id': fields.many2one('account.period', 'Period', required=True, readonly = True, 
                 states={'draft':[('readonly', False)]}), 
        'journal_id': fields.many2one('account.journal', 'Journal', required=True, readonly = True, 
                 states={'draft':[('readonly', False)]}), 
        'line_id': fields.one2many('account.move.line', 'move_id', 'Entries', readonly = True, required=True,
                 states={'draft':[('readonly', False)], 'analytic':[('readonly', False)]}), 
        'ref': fields.char('Reference', size=64, readonly = True), 
        'date': fields.date('Date', required=True, readonly = True, states={'draft':[('readonly', False)]}), 
    }

    def _required_line_id(self, cr, uid, ids, context=None):
        if self.search(cr, uid,[('id', 'in', ids),('line_id', '=', False),('state', '!=', 'draft')], context=context):
            return False
        return True

    def _debit_credit_check(self, cr, uid, ids, context=None):
        move_ids = self.search(cr, uid, [('state','!=','draft'),('id','in',ids)], context=context)
        if self.pool.get('account.move.line').search(cr, uid,[('debit','=',0),('credit','=',0),('move_id','in',move_ids)], context=context):
            return False
        return True

    _constraints = [
         (_required_line_id, "Operation is not completed, 'Journal Items' info is missing!", ['line_id']), 
         (_debit_credit_check, "Operation is not completed, Journal Items should have debit/credit values!", []), 
    ]

    def onchange_date(self, cr, uid, ids, date, context=None):
        """
        Change in period field depend on journal type
        @param date: date
        @return: Dictinory of value
        """
        if context is None:
            context ={}
        context.update({'account_period_prefer_normal': True})
        pids = date and self.pool.get('account.period').find(cr, uid, date, context=context) or False
        return {'value':{'period_id':pids and pids[0] or False}}

    def draft(self, cr, uid, ids, context={}):
        """
        Workflow function change record state to 'draft'.
        @return: boolean True
        """        
        cr.execute("SELECT part.name,timestamp,aud.method,aud.user_id \
                    FROM   res_users usr JOIN res_partner part ON part.id = usr.partner_id\
                           INNER JOIN audittrail_log aud ON aud.user_id = usr.id \
                    WHERE  aud.res_id = %s AND method = 'completed' AND  aud.object_id = \
                    (SELECT id FROM ir_model WHERE model='account.move' )  ORDER BY  timestamp desc", (ids[0],))
        res = cr.dictfetchone()
        #if res and res['user_id'] != uid:
            #raise orm.except_orm(_('UserError'), _('You cann\'t edit this jouranl, it\'s entered by "%s"') % res['name'])	  

        wf_service = netsvc.LocalService("workflow")
        for id in ids:
            wf_service.trg_delete(uid, 'account.move', id, cr)
            wf_service.trg_create(uid, 'account.move', id, cr)
        self.write(cr, uid, ids, {'state': 'draft'}, context=context)
        return True

    def completed(self, cr, uid, ids, context=None):
        """
        Workflow function change record state to 'completed'.
        @return: write method of object
        """        
        if not (self.validate(cr, uid, ids, context=context) and len(ids)):
            raise orm.except_orm(_('Integrity Error !'), _('You can not Complete a non-balanced entry !\nMake sure you have configured Payment Term properly !\nIt should contain atleast one Payment Term Line with type "Balance" !'))
        for mv in self.browse(cr, uid, ids, context=context):
            for line in mv.line_id:
                if line.account_id.user_type.analytic_required and not line.analytic_account_id and line.debit:
                    raise orm.except_orm(_('Error!'), _('You must add analytic account for %s accounts!')%(line.account_id.user_type.name,))
        return self.write(cr, uid, ids, {'state':'completed'}, context=context)

    def check_analytic(self, cr, uid, ids, context={}):
        """
        Workflow function change record state to 'to_review_analytic'.
        @return: write method of object
        """
        return self.write(cr, uid, ids, {'state': 'to_review_analytic'}, context=context)

    def reverse(self, cr, uid, ids, context=None):
        """ 
        inherit method to add some constrains 
        @return: dictionary of values
        """
        if context is None:
            context = {}
        for move in self.browse(cr, uid, ids, context=context):
            if move.state != 'posted':
                raise orm.except_orm(_('Error !'), _('You can\'t reverse unposted move! '))
            context.update({'company_id':move.company_id.id})
            if self.pool.get('account.move.line').search(cr, uid, [('journal_id.type', '=', 'bank'),('move_id', '=', move.id), ('statement_id', '!=', False)], context=context):
                raise orm.except_orm(_('Warning !'), _("This move has bank reconcilation")) 
        return {
            'name':_("Move Reverse"), 
            'view_mode': 'form', 
            'view_id': False, 
            'view_type': 'form', 
            'res_model': 'account.move.reverse', 
            'type': 'ir.actions.act_window', 
            'nodestroy': True, 
            'target': 'new', 
            'domain': '[]', 
            'context': dict(context, active_ids=ids, active_model=self._name), 
        }

    def post(self, cr, uid, ids, context=None):
        """
        Workflow function change record state to 'posted'.
        @return: write method of object
        """
        context = context and context or {}
        if not (self.validate(cr, uid, ids, context=context) and len(ids)):
            raise orm.except_orm(_('Integrity Error !'), _('You can not Complete a non-balanced entry !\nMake sure you have configured Payment Term properly !\nIt should contain atleast one Payment Term Line with type "Balance" !'))
        for move in self.browse(cr, uid, ids, context=context):
                if move.name =='/':
                    new_name = False
                    journal = move.journal_id
                    if journal.sequence_id:
                        c = context.copy()
                        c.update({'fiscalyear_id': move.period_id.fiscalyear_id.id})
                        new_name = self.pool.get('ir.sequence').get_id(cr, uid, journal.sequence_id.id, context=c)
                    else:
                        raise orm.except_orm(_('Error'), _('No sequence defined in the journal !'))
                    if new_name:
                        self.write(cr, uid, [move.id], {'name':new_name}, context=context)
        return self.write(cr, uid, ids, {'state': 'posted'}, context=context)

    def analytic_completed(self, cr, uid, ids, context=None):
        """
        Workflow function change record state to 'completed'.
        @return: write method of object
        """
        return self.write(cr, uid, ids, {'state': 'completed'}, context=context)

    def unlink(self, cr, uid, ids, context=None, check=True):
        """ inherit method to add constrain when delete move line 
        @param check: if true, to check
        @return: super unlink method of object
        """
        toremove = []
        move_line_pool = self.pool.get('account.move.line')
        for move in self.browse(cr, uid, ids, context=context):
            if move.state != 'draft':
                raise orm.except_orm(_('UserError'), _('You can not delete movement: "%s"!') % move.name)
            
            line_ids = map(lambda x: x.id, move.line_id)
            context.update({'journal_id': move.journal_id.id, 'period_id': move.period_id.id})
            move_line_pool._update_check(cr, uid, line_ids, context=context)
            move_line_pool.unlink(cr, uid, line_ids, context=context)
            toremove.append(move.id)
        return super(account_move, self).unlink(cr, uid, toremove, context=context)

    def copy(self, cr, uid, id, default={}, context=None, done_list=[], local=False):
        """ 
        Inherit to update value of ref field
        @return: super copy method of object
        """

        periods = self.pool.get('account.period').find(cr, uid,datetime.now(), context=context)
        default.update({'ref': False , 'date':datetime.now(),'period_id':periods[0]})
        return super(account_move, self).copy(cr, uid, id, default=default, context=context)

    def revert_move(self, cr, uid, ids, journal, period, date, reconcile=True, context=None):
        """ Function to reverse move by creating new reversing move by reversing debit/credit values.

        @param journal: ID of the move journal to be reversed
        @param journal: ID of the period of the reversing move 
        @param date: date of the reversing move 
        @param reconcile: boolean partner reconcilation
        @return: ID of the new reversing move

        """
        if context is None:
            context = {}
        for move in self.browse(cr, uid, ids, context=context):
            journal = journal and journal[0] or move.journal_id.id
            period = period and period[0] or move.period_id.id
            date = date or move.date
            ctx = context.copy()
            ctx.update({'period_id': period, 'date': date})
            copy_id = self.copy(cr, uid, move.id, context=ctx)
            self.write(cr, uid, [copy_id], {'ref': context.get('ref', '')+move.name, 'journal_id': journal}, context=context)
            self.post(cr, uid, [copy_id], context=context)
            self.write(cr, uid, [move.id, copy_id], {'state': 'reversed'}, context=context)
            if reconcile:
                reconcile_lines = self.pool.get('account.move.line').search(cr, uid, [('account_id.reconcile', '=', 'True'), 
                                                                            ('move_id', 'in', [move.id, copy_id])], 
                                                                            context=context)
                self.pool.get('account.move.reconcile').create(cr, uid, {
                        'type': 'manual', 
                        'line_id': map(lambda x: (4, x, False), reconcile_lines), 
                        'line_partial_ids': map(lambda x: (3, x, False), reconcile_lines)}, context=context)
            return copy_id


#----------------------------------------------------------
# Account Move Line(Inherit)
#----------------------------------------------------------
class account_move_line(osv.Model):
    """ Inherit model to override and add method """
    _inherit = 'account.move.line'

    def create(self, cr, uid, vals, context=None, check=True):
        """ 
        Inherit create method to update dictionary of vals
        @param vals: dictionary of values
        @return: super create method
        """
        if context is None:
            context = {}
        move_obj = self.pool.get('account.move')
        if ('move_id' in vals) and vals['move_id']:
            m = move_obj.browse(cr, uid, vals['move_id'])
            context.update({'date': m.date})
            vals.update({'date': m.date})  
        if context.get('reverse_move', False):
            debit = vals.get('debit', 0)
            credit = vals.get('credit', 0)
            amount = vals.get('amount_currency',0) == 0 and 0 or -vals.get('amount_currency',0)
            vals.update({  'debit': credit, 'credit': debit, 'amount_currency': amount,
                             'period_id': context['period_id'], 'date': context['date'] })   
        return super(account_move_line, self).create(cr, uid, vals, context=context, check=check)

    def _query_get(self, cr, uid, obj='l', context=None):
        """
        used in account arabic reports and chart of account to balance the credit and debit
        @param obj: current object
        @return: string of the where statement
        """       
        fiscalyear_obj = self.pool.get('account.fiscalyear')
        fiscalperiod_obj = self.pool.get('account.period')
        account_obj = self.pool.get('account.account')
        fiscalyear_ids = []
        if context is None:
            context = {}
        initial_bal = context.get('initial_bal', False)
        company_clause = " "
        if context.get('company_id', False):
            company_clause = " AND " +obj+".company_id = %s" % context.get('company_id', False)
        if not context.get('fiscalyear', False):
            if context.get('all_fiscalyear', False):
                fiscalyear_ids = fiscalyear_obj.search(cr, uid, [])
            else:
                fiscalyear_ids = fiscalyear_obj.search(cr, uid, [('state', '!=', 'final_lock')])
        else:
            fiscalyear_ids = [context['fiscalyear']]
        company = ''
        fiscalyear_start_date = ''
        orderd_fiscalyears = []
        if context.get('chart_account_id', False):
            company = account_obj.browse(cr, uid, [context.get('chart_account_id', False)])[0].company_id.id
            fiscalyear_start_date = fiscalyear_obj.browse(cr, uid, fiscalyear_ids)[0].date_start
            orderd_fiscalyears = fiscalyear_obj.search(cr, uid, [('company_id', '=', company),('state', '=', 'draft')], order='date_start')
        fiscalyear_clause = initial_bal and (','.join(map(str,orderd_fiscalyears))) or (','.join(map(str,fiscalyear_ids)))
        state = context.get('state', False)
        where_move_state = ''
        where_move_lines_by_date = ''
        if context.get('date_from', False) and context.get('date_to', False):
            if initial_bal:
                where_move_lines_by_date = " AND " +obj+".move_id IN (SELECT id FROM account_move WHERE date < '" +context['date_from']+"')"
            else:
                where_move_lines_by_date = " AND " +obj+".move_id IN (SELECT id FROM account_move WHERE date >= '" +context['date_from']+"' AND date <= '"+context['date_to']+"')"
        if state:
            if isinstance(state,tuple):
                where_move_state= " AND "+obj+".move_id IN (SELECT id FROM account_move WHERE account_move.state in %s )"% (state,)
            else:
                if state.lower() not in ['all']:
                    where_move_state= " AND "+obj+".move_id IN (SELECT id FROM account_move WHERE account_move.state = '"+state+"')"
        if context.get('period_from', False) and context.get('period_to', False) and not context.get('periods', False):
            if initial_bal:
                period_company_id = fiscalperiod_obj.browse(cr, uid, context['period_from'], context=context).company_id.id
                first_period = fiscalperiod_obj.search(cr, uid, [('company_id', '=', period_company_id)], order='date_start')
                context['periods'] = fiscalperiod_obj.build_ctx_periods(cr, uid, first_period[0], first_period[first_period.index(context['period_from'])-1])
            else:
                context['periods'] = fiscalperiod_obj.build_ctx_periods(cr, uid, context['period_from'], context['period_to'])
        if context.get('periods', False):
            period_ids = ','.join(map(str,context['periods']))
            query = obj+".state <> 'draft' AND "+obj+".period_id IN (SELECT id FROM account_period WHERE fiscalyear_id IN (%s) AND id IN (%s)) %s %s" % (fiscalyear_clause, period_ids, where_move_state, where_move_lines_by_date)
        else:
            if initial_bal and (not context.get('date_from', False)):
                if context.get('fiscalyear',False) and context['fiscalyear'] in orderd_fiscalyears:
                    x= orderd_fiscalyears[0:orderd_fiscalyears.index(context['fiscalyear'])]
                    fiscalyear_clause = (','.join(map(str,x))) or -1
                else:
                    fiscalyear_clause = -1
            query = obj+".state <> 'draft' AND "+obj+".period_id IN (SELECT id FROM account_period WHERE fiscalyear_id IN (%s)) %s %s" % (fiscalyear_clause, where_move_state, where_move_lines_by_date)
        if context.get('journal_ids', False):
            query += ' AND '+obj+'.journal_id IN (%s)' % ','.join(map(str, context['journal_ids']))
        if context.get('chart_account_id', False):
            child_ids = account_obj._get_children_and_consol(cr, uid, [context['chart_account_id']], context=context)
            query += ' AND '+obj+'.account_id IN (%s)' % ','.join(map(str, child_ids))
        if 'statement_id' in context:
            if context.get('statement_id', False):
                query += ' AND '+obj+'.statement_id IN (%s)' % (tuple(context.get('statement_id', [])))
            else:
                query += ' AND '+obj+'.statement_id IS NULL '
        if context.get('move_line_ids', False):
            query += ' AND '+obj+'.id IN (%s)' % ','.join(map(str, context['move_line_ids']))
            
        if context.get('analytic_display', False):
            query += ' AND '+obj+".analytic_account_id IN (select id from account_analytic_account where analytic_type=%s) " % (context.get('analytic_display', False).id,) 


        if context.get('partner_ids', False):
            query += ' AND '+obj+'.partner_id IN (%s)' % ','.join(map(str, context['partner_ids']))

        query += company_clause
        return query

    def _update_check(self, cr, uid, ids, context={}):
        done = {}
        for line in self.browse(cr, uid, ids, context):
            if line.move_id.state in ('posted') or line.reconcile_id:
                raise orm.except_orm(_('Error !'), _('You can not do this modification on a posted entry ! Please note that you can just change some non important fields !\n  '))
            t = (line.journal_id.id, line.period_id.id)
            if t not in done:
                self._update_journal_check(cr, uid, line.journal_id.id, line.period_id.id, context=context)
                done[t] = True
        return True

    def _default_get(self, cr, uid, fields, context=None):
        """ 
        This Method get the 
        default value for move line 
        (debit or credit and name)  and return them in the balanced move line
        @return: data 
        """         
        data = super(account_move_line, self)._default_get(cr, uid, fields, context=context)
        if context.get('lines', []):
            total_new = 0.00
            for i in context['lines']:
                if i[2]:
                    total_new += (i[2]['debit'] or 0.00)- (i[2]['credit'] or 0.00)
                    s = -total_new
                    data['debit'] = s > 0 and s or 0.0
                    data['credit'] = s < 0 and -s or  0.0
                    data['name'] = i[2]['name']
        return data 

    def onchange_currency_id(self, cr, uid, ids, account_id, debit, credit, currency_id, date, journal=False, context=None):
        """ 
        convert move line amount to selected currency and put the converted amount in debit and credit fields
        put foreign amount to amount_currency
        @param char account_id: move line account ,
        @param char debit:move line debit  ,
        @param char credit: move line credit,
        @param char currency_id: current id of currency,
        @return: update the form values 
        """
        if context is None:
            context = {}
        account_obj = self.pool.get('account.account')
        currency_obj = self.pool.get('res.currency')
        if (not currency_id) or (not account_id):
            return {}
        result = {}
        acc = account_obj.browse(cr, uid, account_id, context=context)
        amount= credit > 0 and -credit or debit
        if currency_id == acc.company_id.currency_id.id:
            v = amount
        else:

            context.update({'date': date})
            v = currency_obj.compute(cr, uid, currency_id, acc.company_id.currency_id.id, amount, date, context=context)
        result['value'] = {
                'debit': v > 0 and v or 0.0, 
                'credit':v < 0 and -v or 0.0, 
                
                'amount_currency': 0.0
            }
        #change amount currency from amount to 0.0
        #'amount_currency': amount 
        return result

    def onchange_partner_id(self, cr, uid, ids, move_id, partner_id, account_id=None, debit=0, credit=0, date=False, journal=False):
        """ 
        put default account for selected partner

        @param char move_id: the current move  
        @param char partner_id:the selected partner 
        @param account_id: current account
        @param debit: debit amount
        @param credit: credit amount
        @param date: move date
        @param journal: journal_id
        @return: update the form values 
        """
        partner_obj = self.pool.get('res.partner')
        payment_term_obj = self.pool.get('account.payment.term')
        journal_obj = self.pool.get('account.journal')
        fiscal_pos_obj = self.pool.get('account.fiscal.position')
        val = {}
        val['date_maturity'] = False
        if not partner_id:
            return {'value':val}
        if not date:
            date = datetime.now().strftime('%Y-%m-%d')
        part = partner_obj.browse(cr, uid, partner_id)
        if part.property_payment_term:
            res = payment_term_obj.compute(cr, uid, part.property_payment_term.id, 100, date)
            if res:
                val['date_maturity'] = res[0][0]
        if not account_id:
            id1 = part.property_account_payable.id
            id2 =  part.property_account_receivable.id
            if journal:
                jt = journal_obj.browse(cr, uid, journal).type
                if part.customer and not part.supplier:
                    val['account_id'] = fiscal_pos_obj.map_account(cr, uid, part and part.property_account_position or False, id2)
                if part.supplier and not part.customer:
                    val['account_id'] = fiscal_pos_obj.map_account(cr, uid, part and part.property_account_position or False, id1)
                elif jt in ('sale', 'purchase_refund') :
                    val['account_id'] = fiscal_pos_obj.map_account(cr, uid, part and part.property_account_position or False, id2)
                elif jt in ('purchase', 'sale_refund', 'expense', 'bank', 'cash') :
                    val['account_id'] = fiscal_pos_obj.map_account(cr, uid, part and part.property_account_position or False, id1)
                if val.get('account_id', False):
                    d = self.onchange_account_id(cr, uid, ids, val['account_id'])
                    val.update(d['value'])
        return {'value':val}

    def _check_date(self, cr, uid, vals, context=None, check=True):
        """ 
        check the period in selected date
        @param char vals: all values of create form  ,
        @return:True
        """
        if context is None:
            context = {}
        move_obj = self.pool.get('account.move')
        journal_obj = self.pool.get('account.journal')
        period_obj = self.pool.get('account.period')
        journal_id = False
        date = False
        if 'journal_id' in vals and 'journal_id' not in context:
                journal_id = vals['journal_id']
        if 'period_id' in vals and 'period_id' not in context:
                period_id = vals['period_id']
        elif 'journal_id' not in context and 'move_id' in vals:
            if vals.get('move_id', False):
                m = move_obj.browse(cr, uid, vals['move_id'])
                journal_id = m.journal_id.id
                period_id = m.period_id.id
                date = m.date
        else:
            journal_id = context.get('journal_id', False)
            period_id = context.get('period_id', False)
        if journal_id and date:
            journal = journal_obj.browse(cr, uid, journal_id, context=context)
            if journal.allow_date and period_id:
                period = period_obj.browse(cr, uid, period_id, context=context)
                if not time.strptime(date[:10], '%Y-%m-%d') >= time.strptime(period.date_start, '%Y-%m-%d') or not time.strptime(date[:10], '%Y-%m-%d') <= time.strptime(period.date_stop, '%Y-%m-%d'):
                    raise orm.except_orm(_('Error'), _('The date of your Journal Entry is not in the defined period!'))
        else:
            return True

    def _check_balance(self, cr, uid, ids, context=None):
        """
        Check account_id in move line if account type is liquidity and credit or debit less than zero
        @return: boolean True or False 
        """
        obj = self.browse(cr, uid, ids[0], context=context)
        if obj.move_id:
            for l in obj.move_id.line_id:
                if l.account_id.type == 'liquidity' and l.credit and l.account_id.balance  < 0: 
                    return False
        return True

    _defaults = {
        'date': lambda self, cr, uid, c: c.get('date', False), 
    }

    _constraints = [
         (_check_balance, "You can not exceed the existing balance!", ['credit']), 
    ]


#----------------------------------------------------------
# Account Analytic Line(Inherit)
#----------------------------------------------------------
class account_analytic_line(osv.Model):

    """Inherit model to add move_id field """

    _inherit = 'account.analytic.line'

    _columns = {
        'move_id': fields.many2one('account.move.line', 'Move Line', ondelete='cascade', select=True), 
    }


#----------------------------------------------------------
# Account Payment Term Line (Inherit)
#----------------------------------------------------------
class account_payment_term_line(osv.Model):

    """Inherit to change compute digit of value_amount field """

    _inherit = "account.payment.term.line"

    _columns = {
        'value_amount': fields.float('Value Amount', digits=(14, 6), help="For Value percent enter % ratio between 0-1."), 
    }


#----------------------------------------------------------
# Account Analytic (Inherit)
#----------------------------------------------------------
class account_analytic(osv.Model):

    _inherit = "account.analytic.account"

    def _child_compute(self, cr, uid, ids, name, arg=None, context=None):
        """
        Get all childrens (child_ids & child_consol_ids)of Analytic Account.
        
        @param char name: functional field name,
        @param list arg: additional arguments,
        @return: dictionary each analytic account and its childrens 
        """
        result = {}
        for record in self.browse(cr, uid, ids, context=context):
            if record.child_ids:
                result[record.id] = [x.id for x in record.child_ids]
            else:
                result[record.id] = []

            if record.child_consol_ids:
                for acc in record.child_consol_ids:
                    if acc.id not in result[record.id]:
                        result[record.id].append(acc.id)
        return result
    
    _columns = {
        'type': fields.selection([('view', 'View'), ('normal', 'Normal'), ('consolidation', 'Consolidation'), ], 'Account Type', 
                                 help='If you select the View Type, it means you won\'t allow to create journal entries using that account.'), 
        'child_consol_ids': fields.many2many('account.analytic.account', 'account_analytic_account_consol_rel', 'child_id', 'parent_id', 'Consolidated Children'), 
        'child_complete_ids': fields.function(_child_compute, relation='account.analytic.account', string="Account Hierarchy", type='many2many'), 
    }

    def name_get(self, cr, uid, ids, context=None):
        """
        Making Analytic Account name appeare like "code name"
        @return: dictionary,name of all analytic account
        """
        return [(r.id, (r.company_id.code and r.company_id.code+'-' or '') + (r.code and r.code+' ' or '') + r.name) for r in self.browse(cr, uid, ids, context=context)if r.id!=0]


#----------------------------------------------------------
# Account move reconcile (Inherit)
#----------------------------------------------------------

class account_move_reconcile(osv.Model):

    _inherit = "account.move.reconcile"

    def _check_same_account(self, cr, uid, ids, context=None):
        """
        Override method to check that the accounts in move lines to be reconciled are same.
        @return: boolean True
        """
        for reconcile in self.browse(cr, uid, ids, context=context):
            move_lines = []
            if not reconcile.opening_reconciliation:
                if reconcile.line_id:
                    first_account = reconcile.line_id[0].account_id.id
                    move_lines = reconcile.line_id
                elif reconcile.line_partial_ids:
                    first_account = reconcile.line_partial_ids[0].account_id.id
                    move_lines = reconcile.line_partial_ids
                for line in move_lines:
                    if line.account_id.id != first_account: return False
        return True

    _constraints = [
        (_check_same_account, 'You can only reconcile journal items with the same account.', ['line_id']), 
    ]

#----------------------------------------------------------
# Partner (Inherit)
#----------------------------------------------------------

class res_partner(osv.Model):

    _inherit = 'res.partner'

    #_sql_constraints = [
    #    ('name_uniq', 'unique (name)', 'The name of the partner must be unique !'),
   #]

    def copy_data(self, cr, uid, id, default=None, context=None):
        if not default:
            default = {}
        name = self.read(cr, uid, [id], ['name'], context)[0]['name']
        default.update({'name': _('%s (copy)') % name})
        return super(res_partner, self).copy_data(cr, uid, id, default, context)

#----------------------------------------------------------
# Account FiscalYear (Inherit)
#----------------------------------------------------------

class account_fiscalyear(osv.Model):

    _inherit = "account.fiscalyear"

    def _periods_check(self, cr, uid, ids, context=None):
        if self.search(cr, uid,[('id', 'in', tuple(ids)),('period_ids', '=', False),\
                    ('state', '!=', 'draft')], context=context):
            return False
        return True

    _constraints = [
         (_periods_check, "Fiscalyear should has at least one period!", []), 
    ]

    def unlink(self, cr, uid, ids, context=None):
        if self.search(cr, uid,[('id', 'in', ids),('state', '!=', 'draft')], context=context):
            raise orm.except_orm(_('UserError'), _('You cann\'t delete not draft fiscalyear!'))
        return super(account_fiscalyear, self).unlink(cr, uid, ids, context=context)


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
