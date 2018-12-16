# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution	
#    Copyright (C) 2004-2008 Tiny SPRL (<http://tiny.be>). All Rights Reserved
#    $Id$
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
import datetime
import time
from osv import osv, fields, orm
from openerp.tools.translate import _
from openerp import netsvc
import openerp.addons.decimal_precision as dp
from openerp.tools.amount_to_text_en import amount_to_text
from base_custom.amount_to_text_ar import amount_to_text as amount_to_text_ar

class account_move_type(osv.osv):

    _name = 'account.move.type'

    _columns = {
		'code' : fields.char('Code',size=32),
		'name' : fields.char('Name',size=32,required=True),
	 }

class account_voucher_line(osv.osv):

    _inherit = 'account.voucher.line'
    _order = 'id'
    def _get_voucher_id(self, cr, uid, ids, context=None):
        result = {}
        for voucher in self.browse(cr, uid, ids, context=context):
            for line in voucher.line_ids:
                result[line.id] = True
        return result.keys()

    _columns = {
                'date': fields.related('voucher_id', 'date', type='date', string='Date'),
		'res_partner_id' : fields.many2one('res.partner','Partner'),
		'dest_approve' : fields.many2one('account.analytic.account','Dest Approved'),
		'res_partner_id' : fields.many2one('res.partner','Partner'),
                 'move_type_id': fields.related('voucher_id', 'move_type_id', string='Move Type', type='many2one', relation='account.move.type', select=True,
                                store = {
                                    'account.voucher': (_get_voucher_id, ['move_type_id'], 20,),
                                    'account.voucher.line': (lambda self, cr, uid, ids, c={}: ids, [], 10),
                                },),
		'permission':fields.related('voucher_id', 'permission', type='char',store={
                        'account.voucher': (_get_voucher_id, ['permission'], 20),
                        'account.voucher.line': (lambda self, cr, uid, ids, c={}: ids, [], 10),
            }, string='permission',),
		'permission1' : fields.char('Permission',size=32,help="backup data fields"),
                'journal_id': fields.related('voucher_id', 'pay_journal_id', type='many2one', string='Journal', relation='account.journal'),
                'pay_journal_id': fields.related('voucher_id', 'pay_journal_id', type='many2one', string='Pay journal', relation='account.journal'),
                'voucher_type': fields.related('voucher_id', 'type', type='char', string='Type'),
                'number': fields.related('voucher_id', 'number', type='char', string='Number'),
                'chk_seq': fields.related('voucher_id', 'chk_seq', type='char', string='Receipt Ref'),
                'seq': fields.integer('Seq'),
                'custody':fields.boolean('custody',),
                'custody_state': fields.selection([('removed', 'Removed'),('not removed', 'Not Removed'),],'Custody State',),
                'removed_date':fields.date('Removed Date',),
                'validating_user_id': fields.many2one('res.users', 'Validate User', readonly=True),
                'last_partner_id': fields.many2one('res.partner', 'Last Partner'),
	   }
    _defaults = {
         'seq': 0,
         'custody_state': 'not removed',
    }

    def unlink(self, cr, uid, ids, context=None):
        """
        Delete the voucher line record if record in draft state,
        @return: super unlink method
        """
        for line in self.browse(cr, uid, ids, context):
            if line.voucher_id.state != 'draft':
                raise osv.except_osv(_('Invalid action !'), _("You can't delete record not in draft state"))
        return super(account_voucher_line, self).unlink(cr, uid, ids, context=context)
    

    def return_custody(self, cr, uid, ids, context=None):
        move_line_obj=self.pool.get('account.move.line')
        for line in self.browse(cr,uid,ids,context=context):
                line_ids=move_line_obj.search(cr, uid, [('voucher_line_id','=',line.id)], context=context)  
        for ml in move_line_obj.browse(cr,uid,line_ids,context=context):
            move_line_obj.write(cr, uid, [ml.id] ,{'custody_state':'not removed' },context=context) 
        self.write(cr, uid, ids, {'custody_state': 'not removed'}, context=context)
        return True

    def remove_custody(self, cr, uid, ids, context=None):
        move_line_obj=self.pool.get('account.move.line')
        for line in self.browse(cr,uid,ids,context=context):
                line_ids=move_line_obj.search(cr, uid, [('voucher_line_id','=',line.id)], context=context)  
        for ml in move_line_obj.browse(cr,uid,line_ids,context=context):
            move_line_obj.write(cr, uid, [ml.id] ,{'custody_state':'removed' },context=context) 
        self.write(cr, uid, ids, {'custody_state': 'removed','removed_date':datetime.datetime.now(),'validating_user_id':uid}, context=context)
        return True
    
class account_move_line(osv.osv):

    _inherit = 'account.move.line'
    def _get_move_type(self, cr, uid, ids, context=None):
        result = []
        for move in self.pool.get('account.move').browse(cr, uid, ids, context=context):
            for line in move.line_id:
                result.append(line.id)
        return result
    _columns = {
                'name': fields.char('Number', size=256, required=True),
		'permission' : fields.char('Permission',size=32),
		'voucher_id' : fields.many2one('account.voucher','voucher'),
		'voucher_line_id' : fields.many2one('account.voucher.line','voucher line'),
                'move_type_id': fields.related('move_id', 'move_type_id', string='Move Type', type='many2one', relation='account.move.type', select=True,
                                store = {
                                    'account.move': (_get_move_type, ['move_type_id'], 20),
                                    'account.move.line': (lambda self, cr, uid, ids, c={}: ids, [], 10),
                                }),
                'custody_state': fields.selection([('removed', 'Removed'),('not removed', 'not removed'),],'Custody State',),
                'custody':fields.related('voucher_line_id', 'custody', type='boolean', string='Custody',),
                'cancel_check':fields.related('move_id', 'canceled_chk', type='boolean', string='Cancel check',),
		'dest_approve' : fields.many2one('account.analytic.account','Dest Approved'),
                'is_changed': fields.boolean('Is changed',),
		#'currency_line_id' : fields.many2one('account.move.currency','currency line'),
	 }



    def unlink(self, cr, uid, ids, context=None):
        """
        Delete the move line record if record in draft state,
        @return: super unlink method
        """
        for line in self.browse(cr, uid, ids, context):
            if line.move_id.state != 'draft':
                raise osv.except_osv(_('Invalid action !'), _("You can't delete record not in draft state"))
        return super(account_move_line, self).unlink(cr, uid, ids, context=context)

    '''def write(self, cr, uid, ids, vals, context={},check=False):
        # overwrite write method to to make is_changed field = True when do any write in line
        if isinstance(ids, (long, int)):
            ids = [ids]
        for line in self.browse(cr, uid, ids, context=context):
            #This move already are posted befor and convert to fraft
            state=vals.get('state',False)
            if line.move_id.posted_before and not state:
                vals.update({'is_changed': True })
        return super(account_move_line, self).write(cr, uid, ids, vals, context=context)'''

class account_move(osv.osv):

    _inherit = 'account.move'

    def compute(self, cr, uid,ids, move_id, context={}):
        """ 
        This function used to write currency line in journal_items
        @return: the copied voucher line
        """
        context_multi_currency = context.copy()
        currency_pool = self.pool.get('res.currency')
        move_line_pool = self.pool.get('account.move.line')
        for mv in self.browse(cr,uid,ids,context):
            if mv.line_id:
               for line in mv.line_id:
                   if line.currency_line_id:
                      move_line_pool.unlink(cr, uid, [line.id], context=context)
        for mv in self.browse(cr,uid,ids,context):
            context_multi_currency.update({'date': mv.date})
            for rec in mv.currency_line_id:
		    company_currency = rec.move_id.company_id.currency_id.id
		    current_currency = rec.currency_id.id
                    if rec.currency_debit > 0.0 :
                       amount_currency = rec.currency_debit
                    if rec.currency_credit > 0.0:
                       amount_currency = -rec.currency_credit
                    if rec.currency_id.id != company_currency:
                       debit_amount =  currency_pool.compute(cr, uid, current_currency, company_currency, rec.currency_debit,context=context_multi_currency)
                       credit_amount = currency_pool.compute(cr, uid, current_currency, company_currency, rec.currency_credit,context=context_multi_currency)
                       currency_id = rec.currency_id.id
                    if rec.currency_id.id == company_currency or not rec.currency_id.id:
                       debit_amount =rec.currency_debit
                       credit_amount = rec.currency_credit
                       amount_currency =0.0
                       currency_id = False
                    dic = {'date':rec.move_id.date,'move_id':rec.move_id.id,'partner_id': rec.partner_id.id or False,'name':rec.name,'account_id':rec.account_id.id,
		                            'debit':debit_amount,
		                            'credit':credit_amount,
		                            'analytic_account_id':rec.analytic_account_id.id or False,
		                            'amount_currency':amount_currency or 0.0,
                                            'currency_id':currency_id or False,
                                            'currency_line_id':rec.id ,
                                            'dest_approve':rec.dest_approve.id or False,
					    'period_id':rec.move_id.period_id.id,
					    'journal_id':rec.move_id.journal_id.id}
		    move_line_pool.create(cr,uid,dic,context=context)

        return True
    def update(self, cr, uid,ids, context={}):
        """ 
        This function used to write currency line in journal_items
        @return: the copied voucher line
        """
        context_multi_currency = context.copy()
        currency_pool = self.pool.get('res.currency')
        move_line_pool = self.pool.get('account.move.line')
        for mv in self.browse(cr,uid,ids,context):
            company_currency = mv.company_id.currency_id.id

            if mv.line_id:
               for line in mv.line_id:
                   current_currency = line.currency_id.id
                   if line.currency_id.id != company_currency: 
                      if line.amount_currency > 0:
                         line.write({'debit':0.0,'credit':0.0})
                         debit_amount = currency_pool.compute(cr, uid, current_currency, company_currency, line.amount_currency,context=context_multi_currency)
                         line.write({'debit':debit_amount,'credit':0.0})
                      if line.amount_currency < 0:
                         line.write({'debit':0.0,'credit':0.0})
                         credit_amount = currency_pool.compute(cr, uid, current_currency, company_currency, line.amount_currency,context=context_multi_currency)
                         line.write({'credit':-credit_amount,'debit':0.0})

        return True

    def reverse(self, cr, uid, ids, context=None):
        """ 
        inherit method to add some constrains 
        @return: dictionary of values
        """
        if context is None:
            context = {}
        for move in self.browse(cr, uid, ids, context=context):
            if move.reversed_move_id:
                raise orm.except_orm(_('Warning !'), _("This move already reversed"))

        return super(account_move , self).reverse(cr, uid, ids, context)

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
            self.write(cr, uid, [copy_id], {'ref':move.ref, 'journal_id': journal}, context=context)
            #self.post(cr, uid, [copy_id], context=context)
            #self.write(cr, uid, [move.id, copy_id], {'state': 'reversed'}, context=context)
            self.write(cr, uid, [move.id, copy_id], {'reversed': True}, context=context)
            self.write(cr, uid, [move.id], {'reversed_move_id': copy_id}, context=context)
            self.write(cr, uid, [copy_id], {'reversed_move_id': move.id}, context=context)

            '''if reconcile:
                reconcile_lines = self.pool.get('account.move.line').search(cr, uid, [('account_id.reconcile', '=', 'True'), 
                                                                            ('move_id', 'in', [move.id, copy_id])], 
                                                                            context=context)
                self.pool.get('account.move.reconcile').create(cr, uid, {
                        'type': 'manual', 
                        'line_id': map(lambda x: (4, x, False), reconcile_lines), 
                        'line_partial_ids': map(lambda x: (3, x, False), reconcile_lines)}, context=context)'''
            return copy_id

    def _get_move(self, cr, uid, ids, context=None):
        result = {}
        for line in self.pool.get('account.move.line').browse(cr, uid, ids, context=context):
            result[line.move_id.id] = True
        return result.keys()

    def _get_line_name(self, cr, uid, ids, field_name, arg, context=None):
        """
        Functional field function to calculate the name from the account lines.
        @return: Dictionary of fields value
        """
        res = {}
        for order in self.browse(cr, uid, ids, context=context):
            res[order.id]=  order.line_id and (order.line_id[0].permission or ' ') + ' ' +  order.line_id[0].name 
        return res

    _columns = {
        'filter_account': fields.boolean('Filter Account',),
	'move_type_id' : fields.many2one('account.move.type','Move Type'),
	'voucher_id' : fields.many2one('account.voucher', 'Voucher'),
        #'currency_line_id': fields.one2many('account.move.currency', 'move_id', 'currency Entry Lines'),
	'second_voucher_id' : fields.many2one('account.voucher', 'Voucher'),
        'voucher_type': fields.related('voucher_id', 'type', type='char', size=32, store=True, string='Voucher type'),
        'posted_before' :fields.boolean('Posted Before'),
        'reversed' :fields.boolean('Reversed'),
	'reversed_move_id' : fields.many2one('account.move', 'Reversed Move'),
        'line_describtion': fields.function(_get_line_name, method=True, string='Describtion', type='char', size=256 ,
            store={
                'account.move': (lambda self, cr, uid, ids, c={}: ids, ['line_id'], 10),
                'account.move.line': (_get_move, None, 10),
            },),
	 }
    _defaults= {
              'posted_before': False,
               }

    def unlink(self, cr, uid, ids, context=None, check=True):
        """ inherit method to add constrain when delete move line 
        @param check: if true, to check
        @return: super unlink method of object
        """
        
        toremove = []
        move_line_pool = self.pool.get('account.move.line')
        if context == None :
           context = {}
        for move in self.browse(cr, uid, ids, context=context):
            
            if move.state != 'draft':
                raise orm.except_orm(_('UserError'), _('You can not delete movement: "%s"!') % move.name)
            if move.voucher_id :
               return False
            line_ids = map(lambda x: x.id, move.line_id)
            context.update({'journal_id': move.journal_id.id, 'period_id': move.period_id.id})
            move_line_pool._update_check(cr, uid, line_ids, context=context)
            move_line_pool.unlink(cr, uid, line_ids, context=context)
            toremove.append(move.id)
        return super(account_move, self).unlink(cr, uid, toremove, context=context)

    def copy(self, cr, uid, id, default=None, context=None):
        """
        Override copy function to edit default value.
        @param default : default vals dict 
        @return: id of the newly created record  
        """
        if default is None:
            default = {}
        if context is None:
            context = {}
        default.update({
            'voucher_id': False,
            'second_voucher_id': False,
        })
        return super(account_move, self).copy(cr, uid, id, default, context)

    def create_log(self, cr, uid, ids, previous_state, new_state, transaction_type ,context):
        """This method create new record in audittrial.log file, 
           use it if you call workflow from function """
        obj_audittrial = self.pool.get('audittrail.log')
        obj_audittrial_line = self.pool.get('audittrail.log.line')
        obj_model = self.pool.get('ir.model')
        obj_model_fields = self.pool.get('ir.model.fields')
        obj_ids = obj_model.search(cr, uid, [('model','=','account.move')],context=context)
        field_ids = obj_model_fields.search(cr, uid, [('model_id','=',obj_ids[0]),('name','=','state')],context=context)
        for move in self.browse(cr, uid, ids , context=context):
            log_dict = { 'timestamp': time.strftime("%Y-%m-%d %H:%M:%S"),
                         'name': move.name,
                         'object_id': obj_ids[0],
                         'user_id': uid,
                         'method': new_state,
                         'res_id': move.id,
                       }
            log_id = obj_audittrial.create(cr, uid, log_dict, context=context)

            log_line_dict_list =[{ 'old_value':previous_state,
                             'old_value_text':previous_state,
                             'new_value':new_state,
                             'new_value_text':new_state,
                             'field_description':'state',
                             'field_id':field_ids[0],
                             'log_id': log_id,
                           } ,
                           {'old_value':'transaction_type',
                             'old_value_text':'transaction_type',
                             'new_value':transaction_type,
                             'new_value_text':transaction_type,
                             'field_description':'state',
                             'field_id':field_ids[0],
                             'log_id': log_id,
                           }]
            for log_line_dict in log_line_dict_list:
                obj_audittrial_line.create(cr, uid, log_line_dict, context=context)

        return True

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
        for rec in self.browse(cr,uid,ids,context):
           if rec.voucher_id :
              self.pool.get('account.voucher').cancel_voucher_niss(cr, uid, [rec.voucher_id.id], context=context)
              self.pool.get('account.voucher').action_cancel_draft(cr, uid, [rec.voucher_id.id], context=context)
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
        voucher_line_obj=self.pool.get('account.voucher.line')
        voucher_obj=self.pool.get('account.voucher')
        context = context and context or {}     
        if not (self.validate(cr, uid, ids, context=context) and len(ids)):
            raise orm.except_orm(_('Integrity Error !'), _('You can not Complete a non-balanced entry !\nMake sure you have configured Payment Term properly !\nIt should contain atleast one Payment Term Line with type "Balance" !'))
        list_account_ids=[]
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
            #Add this check if this first compltete for this move do no update in voucher
            if not move.posted_before:
                self.write(cr, uid, ids, {'posted_before':True,}, context=context)
                return super(account_move, self).completed(cr, uid, ids, context)  
     
            count=0
            for line in move.line_id:
                list_account_ids.append(line.account_id.id)
                if not line.is_changed or line.move_id.filter_account:
                    continue
                count+=1
                if line.account_id.user_type.analytic_required and not line.analytic_account_id and line.debit:
                    raise orm.except_orm(_('Error!'), _('You must add analytic account for %s accounts!')%(line.account_id.user_type.name,))
                #update purchase voucher 
                if line.voucher_id and line.voucher_id.type=='purchase' and not line.currency_id.id:
                       voucher_obj.write(cr, uid, [line.voucher_id.id],{'partner_id':line.partner_id.id,'account_id':line.account_id.id,'amount': line.credit ,'name': line.name})
                if line.voucher_id and line.voucher_id.type=='purchase' and line.currency_id.id:
                       voucher_dict = {'partner_id':line.partner_id.id,'account_id':line.account_id.id,'name': line.name}
                       #If Voucher With forign currency
                       if not line.voucher_id.currency_id.base:
                           voucher_dict.update({'amount': -line.amount_currency ,})
                       voucher_obj.write(cr, uid, [line.voucher_id.id], voucher_dict)
                #update sale voucher 
                if line.voucher_id and line.voucher_id.type=='sale' and not line.currency_id.id:
                       voucher_obj.write(cr, uid, [line.voucher_id.id],{'partner_id':line.partner_id.id,'account_id':line.account_id.id,'amount': line.debit ,'name': line.name})
                if line.voucher_id and line.voucher_id.type=='sale' and line.currency_id.id:
                       voucher_obj.write(cr, uid, [line.voucher_id.id],{'partner_id':line.partner_id.id,'account_id':line.account_id.id,'amount': line.amount_currency ,'name': line.name})
                #purchase line same currency
                if line.voucher_line_id and line.voucher_line_id.voucher_id.type=='purchase' and not line.currency_id:
                   if line.voucher_line_id.amount <=0:
      
                           voucher_line_obj.write(cr, uid, [line.voucher_line_id.id] ,{'account_id':line.account_id.id,'amount': -line.credit ,'name':line.name,'permission':line.permission , 'analytic_account_id':line.analytic_account_id.id or False,'res_partner_id':line.partner_id.id})
                   else:
                        voucher_line_obj.write(cr, uid, [line.voucher_line_id.id] ,{'account_id':line.account_id.id,'amount': line.debit ,'name':line.name,'permission':line.permission, 'analytic_account_id':line.analytic_account_id.id or False,'res_partner_id':line.partner_id.id})
                        
                #sale line same other currency
                if line.voucher_line_id and line.voucher_line_id.voucher_id.type=='sale' and not line.currency_id:
                   if line.voucher_line_id.amount <=0:
                           voucher_line_obj.write(cr, uid, [line.voucher_line_id.id] ,{'account_id':line.account_id.id,'amount': -line.debit ,'name':line.name,'permission':line.permission , 'analytic_account_id':line.analytic_account_id.id or False,'res_partner_id':line.partner_id.id})
                   else:
                        voucher_line_obj.write(cr, uid, [line.voucher_line_id.id] ,{'account_id':line.account_id.id,'amount': line.credit ,'name':line.name,'permission':line.permission , 'analytic_account_id':line.analytic_account_id.id or False,'res_partner_id':line.partner_id.id})
                        
                #purchase line other currency
                if line.voucher_line_id and line.voucher_line_id.voucher_id.type=='purchase' and line.currency_id:
                        voucher_dict = {'account_id':line.account_id.id,'name':line.name,'permission':line.permission, 'analytic_account_id':line.analytic_account_id.id or False,'res_partner_id':line.partner_id.id}
                        #If Voucher in forign currency
                        if not line.voucher_line_id.voucher_id.currency_id.base:
                            voucher_dict.update({'amount': line.amount_currency })
                        voucher_line_obj.write(cr, uid, [line.voucher_line_id.id] ,voucher_dict)
                #sale line other currency
                if line.voucher_line_id and line.voucher_line_id.voucher_id.type=='sale' and line.currency_id:
                        voucher_line_obj.write(cr, uid, [line.voucher_line_id.id] ,{'account_id':line.account_id.id,'amount': -line.amount_currency ,'name':line.name,'permission':line.permission , 'analytic_account_id':line.analytic_account_id.id or False,'res_partner_id':line.partner_id.id})
                voucher_ids = voucher_obj.search(cr, uid, [('move_id','=',move.id)], context=context)   
                voucher_obj.compute_tax(cr, uid, voucher_ids, context=context)    
                voucher_obj.amount_to_word(cr, uid, voucher_ids, context=context)

            if move.voucher_id :
                     voucher_obj.write(cr, uid, [move.voucher_id.id], {'state':'posted','date':move.date,'period_id':move.period_id.id}, context=context) 
            if move.journal_id.default_debit_account_id.id not in list_account_ids and move.journal_id.type in ['cash','bank']:
               raise orm.except_orm(_('Error!'), _('You must add  account related by journal'))

        return self.write(cr, uid, ids, {'state':'completed',}, context=context)

class account_voucher(osv.osv):

    _name = 'account.voucher'
    _inherit = 'account.voucher'

    def action_cancel_draft(self, cr, uid, ids, context=None):
        wf_service = netsvc.LocalService("workflow")
        for voucher_id in ids:
            wf_service.trg_create(uid, 'account.voucher', voucher_id, cr)
        self.write(cr, uid, ids, {'state':'draft'})
        return True

    def cancel_voucher_niss(self, cr, uid, ids, context=None):
        reconcile_pool = self.pool.get('account.move.reconcile')
        move_pool = self.pool.get('account.move')
        move_line_pool = self.pool.get('account.move.line')
        for voucher in self.browse(cr, uid, ids, context=context):
            # refresh to make sure you don't unlink an already removed move
            voucher.refresh()
            for line in voucher.move_ids:
                if line.reconcile_id:
                    move_lines = [move_line.id for move_line in line.reconcile_id.line_id]
                    move_lines.remove(line.id)
                    reconcile_pool.unlink(cr, uid, [line.reconcile_id.id])
                    if len(move_lines) >= 2:
                        move_line_pool.reconcile_partial(cr, uid, move_lines, 'auto',context=context)
            #if voucher.move_id:
                #move_pool.button_cancel(cr, uid, [voucher.move_id.id])
                #move_pool.unlink(cr, uid, [voucher.move_id.id])
        res = {
            'state':'cancel',
            
            #'move_id':False,
        }
        self.write(cr, uid, ids, res)
        return True


    def _lines_counter(self, cr, uid, ids, field_name, arg, context=None):
        """
        Calculate the number of voucher lines in the voucher.
        @param field_name: Name of the field
        @param arg: User defined argument
        @return:  Dictionary of values
        """
        res = {}
        for voucher in self.browse(cr, uid, ids, context=context):
            res[voucher.id] = {'line_cr_counter': len(voucher.line_cr_ids),
                               'line_dr_counter': len(voucher.line_dr_ids)}
            #res[voucher.id]['line_cr_counter'] = len(voucher.line_cr_ids) 
            #res[voucher.id]['line_dr_counter'] = len(voucher.line_dr_ids) 
        return res

    def _get_perm_chk_seq(self, cr, uid, ids, field_name, arg, context=None):
        """
        get the number of Check No or Permission.
        @param field_name: Name of the field
        @param arg: User defined argument
        @return:  Dictionary of values
        """
        res = {}
        for voucher in self.browse(cr, uid, ids, context=context):
            res[voucher.id] = voucher.chk_seq or voucher.permission
        return res

    _columns = {
	'permission' : fields.char('Permission',size=32),
	'move_type_id' : fields.many2one('account.move.type','Move Type'),
        'custody':fields.boolean('custody',),
        'line_cr_counter': fields.function(_lines_counter, method=True, string='Lines counter',  multi='sums'),
        'line_dr_counter': fields.function(_lines_counter, method=True, string='Lines counter',multi='sums'),
        'create_uid':  fields.many2one('res.users', 'Responsible'),
        'perm_chk_seq': fields.function(_get_perm_chk_seq, type='char', method=True,store={
                        'account.voucher': (lambda self, cr, uid, ids, c={}: ids, ['chk_seq','permission'], 20),
            }, string='Permission, Check No', ),
    }

    def _check_permission_uniq(self, cr, uid, ids, context=None):
        for voucher in self.browse(cr, uid, ids, context=context):
            if not voucher.permission:
                return True
            voucher_ids = self.search(cr, uid, [('permission','=',voucher.permission)] )
            if len(voucher_ids)>1:
                return False
        return True

    def _check_chk_seq_uniq(self, cr, uid, ids, context=None):
        for voucher in self.browse(cr, uid, ids, context=context): 
            if not voucher.chk_seq:
                return True
            voucher_ids = self.search(cr, uid, [('chk_seq','=',voucher.chk_seq),('journal_id','=',voucher.journal_id.id)\
                                      ,('pay_journal_id','=',voucher.pay_journal_id.id)] )
            if len(voucher_ids)>1: return False
        return True

    _constraints = [(_check_permission_uniq, 'Permission must be unique!', ['permission']),
                    (_check_chk_seq_uniq, 'Chk No must be unique!', ['chk_seq']),
                    ]

    def copy_cr_line(self, cr, uid, ids, context=None):
        """ 
        This function used to copy last cr voucher line
        @return: the copied voucher line
        """
        voucher_line_obj = self.pool.get('account.voucher.line')
        default = {'res_partner_id':False, 'amount':0.0, 'untax_amount':0.0}
        line_ids  = [voucher.id for voucher in self.browse(cr, uid, ids[0] ,context).line_cr_ids]
        if line_ids:
            voucher_line_obj.copy(cr, uid, line_ids[-1], default, context)

        return True

    def copy_dr_line(self, cr, uid, ids, context=None):
        """ 
        This function used to copy last dr voucher line
        @return: the copied voucher line
        """
        voucher_line_obj = self.pool.get('account.voucher.line')
        default = {'amount':0.0, 'custody':False,'res_partner_id':False,'untax_amount':0.0}
        line_ids  = [voucher.id for voucher in self.browse(cr, uid, ids[0] ,context).line_dr_ids]
        if line_ids:
            voucher_line_obj.copy(cr, uid, line_ids[-1], default, context)

        return True

    def copy(self, cr, uid, id, default={}, context=None, done_list=[], local=False):
        """ 
        Inherit to update value of ref field
        @return: super copy method of object
        """
        periods = self.pool.get('account.period').find(cr, uid,datetime.datetime.now(), context=context)
        if periods:
           default.update({'date':datetime.datetime.now(),'period_id':periods[0]})
        default.update({'permission':None})
        return super(account_voucher, self).copy(cr, uid, id, default=default, context=context)

    def amount_to_word(self, cr, uid, ids, context=None):
        """
        Inherit method to update the text value of the check amount in the field 
        amount_in_word based on the language format of the currency.
        @return: dictionary of values of fields to be updated 
        """
        for voucher in self.browse(cr, uid ,ids, context):
            amount = voucher.amount
            currency_format = self.pool.get('res.users').browse(cr, uid, uid).company_id.currency_format
            if currency_format == 'ar':
                currency_id = ids and self.browse(cr, uid, ids,context=context)[0].currency_id.id
                if currency_id:
                    currency = self.pool.get('res.currency').read(cr, uid, currency_id, ['units_name', 'cents_name'], context=context)
                    amount_in_word = amount_to_text_ar(amount, currency_format, currency.get('units_name',''), currency.get('cents_name',''))
                else:
                    amount_in_word = amount_to_text_ar(amount, currency_format)
            else: 
                amount_in_word = amount_to_text(amount)
            self.write(cr, uid, [voucher.id],{'amount_in_word':amount_in_word})
        return True

    def open_voucher(self, cr, uid, ids, context=None):
        self.compute_tax(cr, uid, ids, context=context)
        self.write(cr, uid, ids, {'state': 'complete'}, context=context)
        return True

    def cancel_voucher(self, cr, uid, ids, context={}):
        #Inherit this function to remove Active = False from it
        """
        Workflow function change record state to 'cancel', delete its move if any.

        @return: boolean True
        """
        #super(account_voucher,self).cancel_voucher(cr, uid, ids, context=context)
        self.cancel_voucher_niss(cr, uid, ids, context=context)
        for voucher in self.browse(cr,uid,ids,context):
	    if voucher.move_id:
                self.pool.get('account.move').draft(cr, uid, [voucher.move_id.id])
        #self.write(cr, uid, ids, {'active':1}, context=context)
        return True

    def compute_tax(self, cr, uid, ids, context=None):
        '''
        Calculate Voucher Amount before taxs, Tax Amount and Total Voucher Amoun t with Taxs,
        and update voucher record by new values.

        @return: boolean True
        '''
        context = context or {}
        tax_pool = self.pool.get('account.tax')
        for voucher in self.pool.get('account.voucher').browse(cr, uid, ids, context=context):
            voucher_amount = total_included = total = 0.0
            taxs = voucher.tax_id and (isinstance(voucher.tax_id,list)and voucher.tax_id or [voucher.tax_id]) or []
            for line in voucher.line_ids:
                voucher_amount += line.amount
                amount = line.untax_amount or line.amount
                computed_tax = tax_pool.compute_all(cr, uid, taxs, amount, 1)
                total_included += computed_tax.get('total_included', 0.0)
                total += computed_tax.get('total', 0.0)
                total_with_tax = [tax for tax in taxs if not tax.account_collected_id and tax.amount > 0.0]
                line_with_tax = tax_pool.compute_all(cr, uid, total_with_tax, amount, 1).get('total_included', 0.0)
                self.pool.get('account.voucher.line').write(cr, uid, [line.id], {
							    #'amount':computed_tax.get('total', 0.0),
                                                             #'total_amount':line_with_tax,
                                                             'untax_amount':line.amount}, context=context)
            self.write(cr, uid, [voucher.id], {'amount': not taxs and voucher_amount or total_included,
                                               'tax_amount': total_included-total or 0.0})
        return True
    def action_move_line_create(self, cr, uid, ids, vals={}, context=None):
        """
        Method creating Journal Entry for account voucher.
    
        @param vals: dict of values (period, journal and date)
        @return: boolean True
        """
        if context is None:
            context = {}

        move_id = True
        move_pool = self.pool.get('account.move')
        move_line_pool = self.pool.get('account.move.line')
        voucher_line_pool = self.pool.get('account.voucher.line')
        currency_pool = self.pool.get('res.currency')
        tax_pool = self.pool.get('account.tax')
        sequence_pool = self.pool.get('ir.sequence')
        period_pool = self.pool.get('account.period')
        ml_id=[]
        self.compute_tax(cr, uid, ids, context=context)
        for voucher in self.browse(cr, uid, ids, context=context):
            #if voucher.pay_type=='cash' and voucher.pay_journal_id.type not in ('cash',''):
                #raise osv.except_osv(_('Entry Error!'), _('journal type is not cash!'))
            #if voucher.pay_type in ('chk','letter') and voucher.pay_journal_id.type !='bank':
                #raise osv.except_osv(_('Entry Error!'), _('journal type is not bank!'))
            if voucher.move_id:
                #continue
                cr.execute("delete from account_move_line where move_id = %s",(voucher.move_id.id,))
            period_id = vals.get('period') or voucher.period_id
            date = vals.get('date') or voucher.date
            journal_id = vals.get('journal') or voucher.pay_journal_id or voucher.journal_id
            account_id = vals.get('account') or (voucher.account_id and voucher.account_id.id) or \
                                (voucher.type in ('purchase', 'payment') and journal_id.default_credit_account_id.id) or \
                                (voucher.type in ('sale', 'receipt') and journal_id.default_debit_account_id.id)
            if not account_id and voucher.pay_now != 'pay_now':
                account_id = (voucher.journal_id.type in ('sale', 'sale_refund') and \
			    voucher.partner_id.property_account_receivable and voucher.partner_id.property_account_receivable.id) \
			    or (voucher.journal_id.type in ('purchase', 'purchase_refund') and \
			    voucher.partner_id.property_account_payable and voucher.partner_id.property_account_payable.id) or False
                self.write(cr, uid, [voucher.id],{'account_id': account_id})
            if not account_id:
                raise osv.except_osv(_('Entry Error!'), _('Voucher Account must be added!'))


            context_multi_currency = context.copy()
            context_multi_currency.update({'date': date})
            ctx = context.copy()
            ctx['fiscalyear_id'] = period_pool.browse(cr, uid, period_id.id).fiscalyear_id.id
            if journal_id.sequence_id:
                name = sequence_pool.get_id(cr, uid, journal_id.sequence_id.id)
            else:
                raise orm.except_orm(_('Error !'), _('Please define a sequence on the journal %s!')%(journal_id.name,))
            if voucher.move_id:
               move_id = voucher.move_id.id
            if not voucher.move_id:
               move_id = move_pool.create(cr, uid, {
                            'name': name,
                            'journal_id': journal_id.id,
                            'narration': voucher.narration,
                            'date': date,
                            'ref': voucher.number,
                            'period_id': period_id.id,
                            'dest_approve':voucher.department_id.id,
                            'voucher_id': voucher.id,
                            'second_voucher_id': voucher.id,
                        }, context=context)
            
            #create the first line manually
            company_currency = voucher.journal_id.company_id.currency_id.id
            current_currency = voucher.currency_id.id
            debit = 0.0
            credit = 0.0
            if voucher.type in ('purchase', 'payment'):
                credit = currency_pool.compute(cr, uid, current_currency, company_currency, voucher.amount, context=context_multi_currency)
            elif voucher.type in ('sale', 'receipt'):
                debit = currency_pool.compute(cr, uid, current_currency, company_currency, voucher.amount, context=context_multi_currency)
            if debit < 0:
                credit = -debit
                debit = 0.0
            if credit < 0:
                debit = -credit
                credit = 0.0
            sign = debit - credit < 0 and -1 or 1
            company_currency = voucher.company_id.currency_id.id
            move_lines = []
            totlines = False
            total_currency = 0
            line_total = debit - credit
            if voucher.type == 'sale':
                line_total = line_total - currency_pool.compute(cr, uid, voucher.currency_id.id, company_currency, voucher.tax_amount, context=context_multi_currency)
            elif voucher.type == 'purchase':
                line_total = line_total + currency_pool.compute(cr, uid, voucher.currency_id.id, company_currency, voucher.tax_amount, context=context_multi_currency)
            # Create Payment Terms move lines

            if voucher.pay_now=='pay_now':
               account_id=voucher.pay_journal_id.default_credit_account_id.id
            if voucher.payment_term:
                move_lines=self.action_payment_term_create(cr,uid,voucher,context=context) 
            # Create Move Line for each voucher line'''

            else :
                ml_id = move_line_pool.create(cr, uid,{
                    'move_type_id':voucher.move_type_id.id,
                    'name': voucher.name or '/',
                    'debit': debit,
                    'credit': credit,
                    'account_id': account_id ,
                    'move_id': move_id,
                    'journal_id': journal_id.id,
                    'period_id': period_id.id,
                    'partner_id': voucher.partner_id.id,
                    'currency_id': company_currency != current_currency and  current_currency or False,
                    'amount_currency': company_currency != current_currency and sign * voucher.amount or 0.0,
                    'date': date,
                    'date_maturity': voucher.date_due,
                    'ref': voucher.number,
                    'voucher_id':voucher.id,
                    'custody':voucher.custody,
                    'permission':voucher.permission,
                },context=context)
            acc=[]
            vo_l=[]
            rec_list_ids=[]
            account_obj = self.pool.get('account.account')
            voucher_line_obj = self.pool.get('account.voucher.line')
            for line in voucher.line_ids:
                #if voucher.type == 'purchase' and 'state' in voucher_line_pool._columns and line.state != 'approve':
                    #continue
                if not line.account_id:
                    raise orm.except_orm(_('Entry Error!'),_("Please make sure you enter an account for each voucher line!"))
                if not line.amount:
                    raise orm.except_orm(_('Entry Error!'),_("Please make sure you enter an amount not zero for each voucher line!"))
                if line.res_partner_id:
                    context.update({'partner_ids':[line.res_partner_id.id]})
                partner_balance = account_obj.read(cr, uid, [line.account_id.id], ['balance'], context)[0]['balance']
                if line.type=='dr' and line.account_id.check_type == 'debit':
                    if line.amount > -partner_balance:
                        raise orm.except_orm(_('Warning!'), _('There is no sufficient balance for the partner %s, his balance is %s ') %(line.res_partner_id.name, -partner_balance) )
                    partner_lines = voucher_line_obj.search(cr, uid, [('account_id','=',line.account_id.id), ('res_partner_id', '=', line.res_partner_id.id), ('voucher_id', '=', line.voucher_id.id)])
                    if len(partner_lines) > 1:
                       raise orm.except_orm(_('Warning!'), _('The partner %s has more than one line') %(line.res_partner_id.name,) )
                                                         
                if line.amount == line.amount_unreconciled or (voucher.payment_option == 'with_writeoff' and line.amount < line.amount_unreconciled):
                    amount = line.move_line_id.amount_residual
                else :
                    amount = currency_pool.compute(cr, uid, current_currency, company_currency, line.amount, context=context_multi_currency)
                move_line = {
                    'voucher_line_id':line.id,
                    'journal_id': journal_id.id,
                    'period_id': period_id.id,
                    'name': line.name and line.name or '/',
                    'account_id': line.account_id.id,
                    'move_id': move_id,
                    'permission':line.permission or 0.0,
                    'dest_approve':line.dest_approve and line.dest_approve.id or False,
                    'partner_id': line.res_partner_id.id or voucher.partner_id.id,
                    'currency_id': company_currency != current_currency and current_currency or False,
                    'analytic_account_id': line.account_analytic_id and line.account_analytic_id.id or False,
                    'quantity': 1,
                    'credit': 0.0,
                    'debit': 0.0,
                    'date': date,
                    'ref': voucher.number,
                    'budget_confirm_id': 'budget_confirm_id' in voucher_line_pool._columns and line.budget_confirm_id and line.budget_confirm_id.id,
                    'budget_line_id': 'budget_confirm_id' in voucher_line_pool._columns and line.budget_confirm_id.budget_line_id and line.budget_confirm_id.budget_line_id.id,
                    'custody_state':line.custody_state,
                    'custody':line.custody,
                }
                acc=line.account_id.id
              
                if amount < 0:
                    amount = -amount
                    if line.type == 'dr':
                        line.type = 'cr'
                    else:
                        line.type = 'dr'

                if (line.type=='dr'):
                    line_total += amount
                    move_line['debit'] = amount
                    if line.voucher_id.type=='purchase':
                        move_line['amount_currency'] = company_currency != current_currency and line.amount or 0.0
                    else:
                        move_line['amount_currency'] = company_currency != current_currency and -line.amount or 0.0
                else:
                    line_total -= amount
                    move_line['credit'] = amount
                    if line.voucher_id.type=='purchase':
                       move_line['amount_currency'] = company_currency != current_currency and line.amount or 0.0
                    else:
                      move_line['amount_currency'] = company_currency != current_currency and -line.amount or 0.0
                # Create Taxs Move Lines
                tax_line = move_line.copy()
                taxs = voucher.tax_id and (isinstance(voucher.tax_id,list)and voucher.tax_id or [voucher.tax_id]) or []
                for tax in tax_pool.compute_all(cr, uid, taxs, line.untax_amount, 1.00).get('taxes'):
                    tax_amount= currency_pool.compute(cr, uid, voucher.currency_id.id, company_currency, tax['amount'], context={'date': date or time.strftime('%Y-%m-%d')}, round=False)
                    tax_line.update({
                        'voucher_line_id':False,
                        'account_tax_id': False,
                        'account_id': tax['account_collected_id'] and tax['account_collected_id'] or move_line['account_id'],
                        'credit':  (voucher.type == 'purchase' and tax_amount<0 and -tax_amount) or (voucher.type == 'sale' and tax['amount']>0 and tax['amount']) or 0.0,
                        'debit': (voucher.type == 'purchase' and tax_amount>0 and tax_amount) or (voucher.type == 'sale' and tax['amount']<0 and -tax['amount']) or 0.0,
                        'amount_currency': company_currency != current_currency and tax['amount'] or 0.0,
                        'budget_confirm_id': 'budget_confirm_id' in voucher_line_pool._columns and 
                                            (not tax['account_collected_id'] or tax['account_collected_id'] == move_line['account_id']) and line.budget_confirm_id.id,
                        'budget_line_id': 'budget_confirm_id' in voucher_line_pool._columns and (not tax['account_collected_id'] or tax['account_collected_id'] == move_line['account_id']) and 
                                            line.budget_confirm_id.budget_line_id and line.budget_confirm_id.budget_line_id.id
                    })
                    move_line_pool.create(cr, uid, tax_line, context=context)
                voucher_line=move_line_pool.create(cr, uid, move_line, context=context)
                vo_l=voucher_line
                if line.move_line_id.id:
                    #voucher_line = move_line_pool.create(cr, uid, move_line)
                    rec_ids = [voucher_line, line.move_line_id.id]
                    rec_list_ids.append(rec_ids)

            ml_writeoff = self.writeoff_move_line_get(cr, uid, voucher.id, line_total, move_id, name, company_currency, current_currency, context)
            if ml_writeoff:
               if ml_writeoff['credit'] > 0.0:
                  ml_writeoff['account_id']=voucher.pay_journal_id.default_credit_account_id.id
               
                  ml_writeoff['amount_currency']=0.0
                  ml=move_line_pool.browse(cr,uid,ml_id,context)
                  move_line_pool.write(cr,uid,ml_id,{'debit':ml.debit +ml_writeoff['debit'],'credit':ml.credit +ml_writeoff['credit']}) 
               else:
                  ml_writeoff['amount_currency']=0.0
                  ml_writeoff['account_id']=acc
                  move_line_pool.create(cr, uid, ml_writeoff, context)

            self.write(cr, uid, [voucher.id], {
                'move_id': move_id,
                'state': 'posted',
            }, context=context)
            wf_service = netsvc.LocalService("workflow")
            move_pool.write(cr, uid, [move_id],{'line_id': move_lines and move_lines,},context={'check':False})
            #move_pool.post(cr, uid, [move_id], context=context)
            wf_service.trg_validate(uid, 'account.move', move_id, 'completed', cr)
            move_pool.create_log(cr, uid, [move_id], 'draft', 'completed', 'from_voucher', context)
            wf_service.trg_validate(uid, 'account.move', move_id, 'analytic_completed', cr)
            move_pool.create_log(cr, uid, [move_id], 'draft', 'analytic_completed', 'from_voucher', context)
            #move_pool.completed(cr, uid, [move_id], context=context)
            reconcile = False

            print"lllllllllllllllllllllllllllllllllllllllllll"    
            for rec_ids in rec_list_ids:
                if len(rec_ids) >= 2:
                    reconcile = move_line_pool.reconcile_partial(cr, uid, rec_ids, writeoff_acc_id=voucher.writeoff_acc_id.id, writeoff_period_id=voucher.period_id.id, writeoff_journal_id=voucher.journal_id.id)
        return ml_id


#----------------------------------------------------------
# Account Journal(Inherit)
#----------------------------------------------------------
class account_journal(osv.Model):

    """ Inherit account journal to :
                       add special field 
                       get name of journal without currency 
                       in state of company currency
    """
    _inherit = "account.journal"

    def name_get(self, cr, user, ids, context=None):
        """
        Returns a list of tupples containing id, name.
        result format: {[(id, name), (id, name), ...]}

        @param cr: A database cursor
        @param user: ID of the user currently logged in
        @param ids: list of ids for which name should be read
        @param context: context arguments, like lang, time zone

        @return: Returns a list of tupples containing id, name
        """
        if not ids:
            return []
        if isinstance(ids, (int, long)):
            ids = [ids]
        result = self.browse(cr, user, ids, context=context)
        res = []
        for rs in result:
            if rs.currency:
                currency = rs.currency.name
                name = "%s (%s)" % (rs.name, currency)
            else:
                name = name = "%s " % (rs.name)

            res += [(rs.id, name)]
        return res


'''class account_check_print_wizard(osv.osv_memory):
     
      _inherit="account.check.print.wizard"
     
      def _get_msg(self, cr, uid, context=None): 
        """ @return: char default value of wizard displaying message. """       
        voucher_pool = self.pool.get('account.voucher')
        ids = self._get_voucher_ids(cr, uid, context=context)
        chk_no = ids and voucher_pool.browse(cr, uid, ids, context=context).chk_seq or False
        ok = _("Please verify this check number matches the starting preprinted number of the check in the printer! If not, enter new check number below.")
        if not ids: return ok
        move = voucher_pool.browse(cr, uid, ids, context=context).move_id.state
        return (move == 'draft' and _("Your payment's move is not posted!")) or (chk_no and _("This Payment has already been paid with check:%s")%(chk_no) or \
            ok)'''
    



'''class account_move_currency(osv.osv):

    _name = 'account.move.currency'
    _order = 'id'

    def _get_move_lines(self, cr, uid, ids, context=None):
        result = []
        for move in self.pool.get('account.move').browse(cr, uid, ids, context=context):
            for line in move.line_id:
                result.append(line.id)
        return result

    _columns = {
        'name': fields.char('Name', size=64, required=True),
        'dest_approve' : fields.many2one('account.analytic.account','Dest Approved'),
        'currency_debit': fields.float('Currency Debit', digits_compute=dp.get_precision('Account')),
        'currency_credit': fields.float('currency Credit', digits_compute=dp.get_precision('Account')),
        'account_id': fields.many2one('account.account', 'Account', required=True, ondelete="cascade", domain=[('type','<>','view'), ('type', '<>', 'closed')], select=2),
'analytic_account_id': fields.many2one('account.analytic.account', 'Analytic Account', ondelete="cascade", domain=[('type','<>','view'), ('type', '<>', 'closed')], select=2),
        'move_id': fields.many2one('account.move', 'Journal Entry', ondelete="cascade", help="The move of this entry line.", select=2, ),
        
        'narration': fields.related('move_id','narration', type='text', relation='account.move', string='Internal Note'),
        'ref': fields.related('move_id', 'ref', string='Reference', type='char', size=64, store=True),

        'currency_id': fields.many2one('res.currency', 'Currency', help="The optional other currency if it is a multi-currency entry."),
       

        'partner_id': fields.many2one('res.partner', 'Partner', select=1, ondelete='restrict'),
    }
    _defaults = {
       
    }

      
    def onchange_curr_id(self, cr, uid, ids, account_id, context=None):
        account_obj = self.pool.get('account.account')
        val = {}
        if account_id:
            res = account_obj.browse(cr, uid, account_id, context=context)
            currency_id = res.currency_id.id
            if currency_id:
                currency_id = currency_id
            val['currency_id'] = currency_id or False
        return {'value': val}'''






