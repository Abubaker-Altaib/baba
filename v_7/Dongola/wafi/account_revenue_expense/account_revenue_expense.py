# -*- coding: utf-8 -*-
##############################################################################
#
# NCTR, Nile Center for Technology Research
# Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################
import time
from openerp.osv import osv, fields, orm
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp
from account_voucher.account_voucher import resolve_o2m_operations

class account_voucher(osv.Model):

    _inherit = "account.voucher"

    _order = "scheduler, date desc, id desc"

    def _scheduler(self, cr, uid, ids, field_name, arg, context=None):
        """
        Functional field method that calculate each payment schedule according to it's priority, date & override level
        
        @return: dictionary of {record id: schedule}
        """
        res = {}.fromkeys(ids)
        cr.execute("""SELECT al.id ,row_number() over ()
                      FROM (SELECT
                                CASE WHEN vo.priority =1 THEN 0
                                ELSE sl.level
                                END AS new_override_level,
                                vo.id 
                           FROM 
                               account_voucher vo 
                               LEFT JOIN account_override_level sl ON (vo.override_level = sl.id) 
                           WHERE 
                               vo.state='schedule'
                           ORDER BY 
                               new_override_level  ,vo.priority,vo.scheduler_date ) AS al """)
        res.update(dict(cr.fetchall()))
        return res

    def _get_voucher(self, cr, uid, ids, context=None):
        """
        @return: list of all voucher waiting to schedule
        """
        return self.pool.get('account.voucher').search(cr, uid, [('state', '=', 'schedule')], context=context)


    def name_get(self, cr, uid, ids, context=None):
        """
        Overwrite name_get method to present voucher name as "number - amount'
        
        @return: list of tuple (voucher id, name)
        """
        if not ids:
            return []
        if context is None: context = {}
        return [(r['id'], (r['number'] or '')+'-'+str(r['amount'])) for r in self.read(cr, uid, ids, ['number','amount'], context, load='_classic_write')]

    _columns = {
        'priority': fields.related('journal_id', 'priority', type='integer', readonly=True, string='Payment Priority' , 
                                   store={'account.voucher': (_get_voucher, ['jornal_id'], 10),
                                          'account.journal': (_get_voucher, ['priority'], 10) },),
        'override_level':fields.many2one('account.override.level', 'Override Level',
                                readonly=True, states={'schedule':[('readonly', False)]}),
        'override_amount': fields.related('override_level', 'max_amount', type='integer', readonly=True, string='Override Amount'),
        'revenue_flow_id': fields.many2one('account.revenue.flow', 'Revenue'),
        'scheduler_date': fields.date('Scheduler Date'),
        'scheduler': fields.function(_scheduler, type='integer', string='Scheduler',
                            store={'account.voucher': (_get_voucher, ['state', 'override_level', 'jornal_id'], 10),
                                    'account.journal': (_get_voucher, ['priority'], 10) },),
        'state':fields.selection([('draft', 'Draft'), ('close', 'Waiting for Department Manager Behest'),
                                  ('confirm', 'Waiting for Payment Confirm'), ('review', 'Waiting for Internal Auditor Review'),
                                  ('schedule', 'Waiting for Schedule'),('pay', 'Waiting for Payment Pay'),
                                  ('receive', 'Waiting for Payment Deliver'), ('posted', 'Waiting for Financial Controller post'),
                                  ('done', 'Done'), ('cancel', 'Cancel'), ('reversed', 'Reversed'),
                                  ('no_approve', 'Budget doesn\'t Approve'), ], 'Status', readonly=True, size=32, track_visibility='onchange'),
    }


    def search(self, cr, uid, args, offset=0, limit=None, order=None, context=None, count=False):
        """
        @return: list of ids order by schedule field value
        """
        context = context or {}
        func_flds = []
        if order:
            order_part = order.split(',')[0]
            order_split = order_part.strip().split(' ')
            order_field = order_split[0].strip()
            order_direction = len(order_split) == 2 and order_split[1].strip() or ''
            if order_field == 'scheduler':
                    func_flds.append((order_field, order_direction))
        ids = super(account_voucher, self).search(cr, uid, args, offset, limit, order, context, count)
        if func_flds:
            for fld, order in func_flds:
                val = self.read(cr, uid, ids, [fld], context=context)
                sorted_val = sorted(val, key=lambda x: x[fld],
                        reverse=(order == 'DESC'))
            ids = map(lambda x: x['id'], sorted_val)
        return ids

    def _check_override_level(self, cr, uid, ids, context=None):
        """
        Constraint method that make sure override level doesn't use more than allowed times in period
        
        @return: boolean
        """
        for record in self.browse(cr, uid, ids, context=context):
            if record.override_level and record.override_level.no_of_override != 0:
                num = self.search(cr, uid, [('period_id', '=', record.period_id.id), ('override_level', '=', record.override_level.id)])
                if len(num) > record.override_level.no_of_override:
                    return False
        return True

    def _check_override_amount(self, cr, uid, ids, context=None):
        """
        Constraint method that make sure override level doesn't use in payment with amount 
        more than the maximum amount that allow to use override with 
        
        @return: boolean
        """
        for record in self.browse(cr, uid, ids, context=context):
            if record.override_level and record.override_amount > 0 and record.amount > record.override_amount:
                return False
        return True

    def schedule_voucher(self, cr, uid, ids, context=None):
        """
        Workflow function change record state to 'schedule' and scheduler_date.
        
        @return: boolean True
        """
        return self.write(cr, uid, ids, {'state': 'schedule', 'scheduler_date':time.strftime('%Y-%m-%d')}, context=context)
    

    def pay_voucher(self, cr, uid, ids, context=None):
        """
        Workflow function that  make budget confirmation affect cash budget
        
        @return: change state to 'pay'
        """
        for voucher in self.browse(cr, uid, ids, context=context):
            if voucher.state=='schedule' and voucher.company_id.restrict_scheduler and voucher.scheduler!=1:
                raise orm.except_orm(_('Error!'), _('Payments with less scheduler number must be schedule first, or disable \'Restrict Payment Scheduler\' option from accounting setting.'))
            if voucher.state=='schedule' and voucher.pay_type==False:
                raise orm.except_orm(_('Error!'), _('Kindly Choose Your Payment Type.'))
        return self.write(cr, uid, ids, {'state': 'pay'}, context=context)

    _constraints = [
        (_check_override_level, 'You can not override the maximum number of override level in the period ‬', ['override_level']),
        (_check_override_amount, 'Total amount is larger than override amount for this level ‬', ['override_amount'])
    ]

    def override_change(self, cr, uid, ids, override):
        """
        Method that prevent changing override level from higher to lower level
        
        @return: dictionary of override level value and warning
        """
        warning = {}
        override_obj = self.pool.get('account.override.level')
        if override:
            level = override_obj.browse(cr, uid, override).level
            for record in self.browse(cr, uid, ids):
                if record.override_level and record.override_level.level < level:
                    warning = {
                       'title': _('Invalid Action!'),
                       'message' : _('You cannot edit the General Manager Override Level')
                    }
                    override = record.override_level.id
        return {'value': {'override_level': override }, 'warning': warning}


class budget_operation_history(osv.Model):
    """
    Inherit budget operation history to add revenue flow as reference option
    """
    _inherit = "account.budget.operation.history"

    _columns = {
        'reference': fields.reference('Event Ref', selection=[('account.budget.operation', 'account.budget.operation'),
                                                              ('account.revenue.flow', 'account.revenue.flow')], size=128),
    }


class account_revenue_flow(osv.Model):
    """
    Model to distribute revenues 
    """
    _name = "account.revenue.flow"

    _description = 'Revenue Flow'

    def _flow_line_subtotal(self, cr, uid, ids, name, args, context=None):
        """ 
        Functional field function Finds the total of revenue subtotal  .
        
        @return: Dictionary of revenue.flow.line total value
        """
        res = {}
        for record in self.browse(cr, uid, ids, context=context):
            res[record.id]=sum([line.sub_total for line in record.flow_line_ids])
        return res 

    def _revenu_total(self, cr, uid, ids, name, args, context=None):
        """ 
        Functional field function Finds the total of voucher amount  .
        
        @return: Dictionary of voucher total value
        """
        res = {}
        for record in self.browse(cr, uid, ids, context=context):
            res[record.id] = sum([line.amount for line in record.voucher_ids])
        return res

    def _check_amount(self, cr, uid, ids, context=None):
        """ 
        Check if amount equal to the revenue.
        
        @return: boolean true of false
        """
        for record in self.browse(cr, uid, ids, context=context):
            if record.amount != record.revenue_total:
                raise osv.except_osv(_('Invalid Action'), _('The SubTotal Of Revenue Must Be Equal To The Revenue Total!'))
        return True

    _columns = {
        'voucher_ids': fields.one2many('account.voucher', 'revenue_flow_id', 'Revenue'),
        'name': fields.char('Number', size=64, select=True, readonly=True),
        'period_id': fields.many2one('account.period', 'Period', required=True, readonly=True,
                                     states={'draft':[('readonly', False)]}),
        'amount': fields.function(_flow_line_subtotal, method=True, digits_compute=dp.get_precision('Account'), string='Amount'),
        'flow_line_ids': fields.one2many('account.revenue.flow.line', 'revenue_flow_id', 'Revenue Flow Lines',
                                        required=True, readonly=True, states={'draft':[('readonly', False)]}),
        'note': fields.text('Note'),
        'state': fields.selection([('draft', 'Draft'), ('confirm', 'Confirm'), ('done', 'Done'), ('cancel', 'Cancel')],
                                 'State', readonly=True, required=True),
        'revenue_total': fields.function(_revenu_total, method=True, digits_compute=dp.get_precision('Account'), string='Revenue Total'),
    }

    _defaults = {
        'state':'draft',
        'name': '/',
    }

    _constraints = [
        (_check_amount, '', ['']),
    ]

    def create(self, cr, user, vals, context=None):
        """
        Inherit create method to set the new record name
        
        @return: super create
        """
        if ('name' not in vals) or (vals.get('name') == '/'):
            seq_obj_name = self._name
            vals['name'] = self.pool.get('ir.sequence').get(cr, user, seq_obj_name)
        return super(account_revenue_flow, self).create(cr, user, vals, context)

    def unlink(self, cr, uid, ids, context=None):
        """
        Inherit unlink method to prevent deleting not draft or cancel records
        
        @return: super unlink
        """
        flow = self.read(cr, uid, ids, ['state'], context=context)
        for s in flow:
            if s['state'] not in ['draft', 'cancel']:
                raise osv.except_osv(_('Invalid Action!'), _('In order to delete a revenue flow, you must cancel it first.'))
        return super(account_revenue_flow, self).unlink(cr, uid, ids, context=context)

    def action_confirm(self, cr, uid, ids, context=None):
        """
        Method that make sure the total distribution amount is not grater than the revenue amount and
        the cash budget will not become more than the planned budget
        
        @return: change record state to 'confirm'
        """
        flow = self.browse(cr, uid, ids, context=context)[0]
        for l in flow.flow_line_ids:
            if l.line_id.cash_total_operation + l.sub_total > l.line_id.planned_amount + l.line_id.total_operation:
                raise orm.except_orm(_('Integrity Error!'), _("Cash budget can't be more than planned budget!!"))
        return self.write(cr, uid, ids, {'state': 'confirm'}, context=context)

    def action_done(self, cr, uid, ids, context=None):
        """
        Method that increase cash budget with the revenue distribution amount,
        change the record state to 'done' and prevent distribute more than the revenue amount
        
        @return: True
        """
        flow = self.browse(cr, uid, ids, context=context)[0]
        budget_line_pool = self.pool.get('account.budget.lines')
        for l in flow.flow_line_ids:
            to = {'analytic_account': l.line_id.analytic_account_id.id,
                  'account_id': l.line_id.general_account_id.id,
                  'period_id': l.line_id.period_id.id,
                  'company': l.line_id.company_id.id,
                  'amount': l.sub_total,
                  #'voucher_id': flow.voucher_id.id
                  }
            #TEST: test transfer
            budget_line_pool.transfer(cr, uid, {'type':'increase', 'budget_type':'cash', 'from_line':[],
                                                'to':to, 'reference':self._name + ',' + str(flow.id)}, context=context)
            self.write(cr, uid, ids, {'state': 'done'}, context=context)
        return True

    def action_cancel(self, cr, uid, ids, context=None):
        """
        @return: change record state to 'cancel'
        """
        return self.write(cr, uid, ids, {'state': 'cancel'}, context=context)

    def action_draft(self, cr, uid, ids, context=None):
        """
        @return: change record state to 'draft'
        """
        return self.write(cr, uid, ids, {'state':'draft'}, context=context)

    def calculate_flow(self, cr, uid, ids, context=None):
        """
        Method to calculate distribution percentage for each account according to 
        the account planned budget percentage from the total planned budget
        
        @return: dictionary of new flow lines details 
        """
        flow_line_pool = self.pool.get('account.revenue.flow.line')
        fy_budget_line_pool = self.pool.get('account.fiscalyear.budget.lines')
        budget_line_pool = self.pool.get('account.budget.lines')
        for flow in self.browse(cr, uid, ids, context=context):
            flow_line = []
            amount_dic = fy_budget_line_pool.read_group(cr, uid, [('fiscalyear_id','=',flow.period_id.fiscalyear_id.id)],
                                  ['fiscalyear_id', 'planned_amount'], ['fiscalyear_id'], context=context)
            amount = amount_dic and amount_dic[0]['planned_amount'] or 0
            if amount > 0:
                budget_line_ids = budget_line_pool.search(cr, uid, [('period_id','=',flow.period_id.id)], context=context)
                for line in budget_line_pool.browse(cr, uid, budget_line_ids, context=context):
                    fy_line_ids = fy_budget_line_pool.search(cr, uid, [('general_account_id','=',line.general_account_id.id), 
                                                                       ('analytic_account_id','=',line.analytic_account_id.id),
                                                                       ('fiscalyear_id','=',line.period_id.fiscalyear_id.id)], context=context)
                    fy_line = fy_line_ids and fy_budget_line_pool.browse(cr, uid, fy_line_ids[0], context=context)
                    percent = fy_line and fy_line.planned_amount*100/amount or 0
                    if percent > 0:
                        flow_line.append((0,0,{'line_id':line.id, 'value':'percent', 'amount': percent, 'sub_total': percent * flow.revenue_total / 100}))
                flow_line_ids = flow_line_pool.search(cr, uid, [('revenue_flow_id','=',flow.id)], context=context)
                self.write(cr, uid, flow.id, {'flow_line_ids':[(5,l) for l in flow_line_ids]+flow_line}, context=context)
        return True

class account_revenue_flow_line(osv.Model):

    _name = "account.revenue.flow.line"

    _description = 'Revenue Flow Line'

    _columns = {
        'line_id': fields.many2one('account.budget.lines', 'Budget Line', required=True, ondelete='cascade'),
        'amount':fields.float('Amount', digits_compute=dp.get_precision('Account'), required=True),
        'value' : fields.selection([('fix', 'Fix Amount'), ('percent', 'Percentage')], 'Valuation', required=True),
        'sub_total': fields.float('Sub Total Amount', digits_compute=dp.get_precision('Account'), required=True),
        'revenue_flow_id': fields.many2one('account.revenue.flow', 'Revenue'),
    }

    _defaults = {
        'value': 'fix',
        'sub_total': 1.0,
        'amount':1.0,
    }

    _sql_constraints = [
        ('amount_check', "CHECK ( sub_total > 0 )", _("Wrong amount, they must be positive")),
    ]

    def onchange_line(self, cr, uid, ids, value, amount, context=None):
        """
        Method to calculate the sub_total according to the selected valuation & amount
        
        @return: dictionary if new sub_total value
        """
        return {'value': {'sub_total': (value == 'fix' and amount) or (value == 'percent' and amount * revenue_flow_id.revenue_total / 100) or 0.0}}


class account_journal(osv.Model):

    _inherit = 'account.journal'

    _columns = {
        'priority': fields.integer('Payment Priority'),
    }

    _defaults = {
        'priority': 10,
    }

    _sql_constraints = [
        ('priority_check', "CHECK (NOT( (type='purchase') AND (priority <=0)))", "The Payment Priority must be greater than zero."),
    ]


class res_company(osv.Model):
    """
    Inherit company model to add restricted payment scheduler as configurable option
    """
    _inherit = "res.company"
    
    _columns = {
        'restrict_scheduler': fields.boolean('Restricted Payment Scheduler'),
    }
    
    _defaults = {
        'restrict_scheduler': True,
    }


class account_config_settings(osv.osv_memory):
    """
    Inherit account configuration setting model to define and display 
    the restricted payment scheduler' field value
    """
    _inherit = 'account.config.settings'

    _columns = {
        'restrict_scheduler':  fields.related('company_id', 'restrict_scheduler', type='boolean', string='Restricted Payment Scheduler'),
    }

    def onchange_company_id(self, cr, uid, ids, company_id, context=None):
        """
        Update dict. of values to set restrict_scheduler depend on company_id
        @param company_id: user company_id
        @return: dict. of new values
        """
        # update related fields
        values = super(account_config_settings,self).onchange_company_id(cr, uid, ids, company_id, context=context).get('value',{})
        
        if company_id:
            company = self.pool.get('res.company').browse(cr, uid, company_id, context=context)
            values.update({
                'restrict_scheduler': company.restrict_scheduler,
            })
           
        return {'value': values}




class account_override_level(osv.Model):

    _name = 'account.override.level'

    _description = 'Override Level'

    _columns = {
        'name': fields.char('Name', size=64, required=True),
        'level': fields.integer('Level.NO', required=True),
        'max_amount': fields.integer('Max Amount', required=True),
        'no_of_override': fields.integer('# OF Override'),
    }

    _sql_constraints = [
        ('level_uniq', 'unique (level)', 'The level of  the override level must be unique !'),
        ('name_uniq', 'unique (name)', 'The name of the override level must be unique per company !'),
    ]



