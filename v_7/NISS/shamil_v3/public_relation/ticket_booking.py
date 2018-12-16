# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

from openerp.osv import fields, osv
import netsvc
import time
import datetime
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp
from admin_affairs.copy_attachments import copy_attachments as copy_attachments
from tools.amount_to_text_en import amount_to_text
from base_custom import amount_to_text_ar

class ticket_booking(osv.Model):
    """
    To manage ticket booking """
  
    def create(self, cr, user, vals, context=None):
        """
        Create new entry sequence for every Ticket Booking
        @param vals: record to be created
        @return: super create() method 
          """
        if ('name' not in vals) or (vals.get('name')=='/'):  
            vals['name'] = self.pool.get('ir.sequence').get(cr, user, 'ticket.booking')
        return super(ticket_booking, self).create(cr, user, vals, context)
    
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
            'name': self.pool.get('ir.sequence').get(cr, uid, 'ticket.booking'),
            
        })
        return super(ticket_booking, self).copy(cr, uid, id, default, context)    
    
    STATE_SELECTION = [
    ('draft', 'Draft'),
    ('dept_confirm','Waiting for General Department Manager To approve'),
    ('admin_affiars_confirm','Waiting for GM To approve'),
    ('confirmed', 'Waiting for PRM Section Manager To approve'),
    ('approved', 'Waiting for PRM office To process'),
    ('done', 'Done'),
    ('cancel', 'Cancel'), 
    ]

    TYPE_SELECTION = [
    ('internal', 'Internal'),
    ('external','External'),
    ]
      
    TRAVEL_PURPOSE_SELECTION = [
    ('training', 'Training'),
    ('mission', 'Mission'),
    ('treatment','Treatment'),
    ('other', 'Other'),
 ] 
    PROCEDURE_SELECTION = [
        ('sudanese', 'Sudanese'),
        ('foreigners', 'Foreigners'),]

    PAYMENT_SELECTION = [
    		('voucher', 'Voucher'),
    		('enrich', 'Enrich'), 
    			]
  

    _name = "ticket.booking"
    _description = 'Ticket Booking'
    _columns = {
    'name':fields.char('Reference', size=64, required=True, select=True, readonly=True  , help="unique number of the Ticket Booking"),
    'date' :fields.date('Date of request',readonly=True),
    'travel_agency':fields.many2one('res.partner', 'Travel Agency',readonly=True, states={'approved':[('readonly',False)]}),
    'cost_of_travel':fields.integer('Cost of Travel',digits_compute= dp.get_precision('Account'),readonly=True, states={'approved':[('readonly',False)]}),
    'travel_route':fields.many2one('res.company','Travel Route', size=64, states={'draft':[('readonly',False)]}),
    'country_route':fields.many2one('res.country','Travel Route', size=64,readonly=True, states={'draft':[('readonly',False)]}),
    'carrier':fields.char('Carrier', size=64,readonly=True, states={'approved':[('readonly',False)]}),
    'date_of_travel':fields.date('Date of Travel',required=True ,readonly=False, states={'done':[('readonly',True)],'approved':[('readonly',True)],'cancel':[('readonly',True)]}),
    'date_of_return':fields.date('Date of Return',required=True ,readonly=False, states={'done':[('readonly',True)],'approved':[('readonly',True)],'cancel':[('readonly',True)]}),
    'travel_purpose':fields.selection(TRAVEL_PURPOSE_SELECTION,'Travel Purpose', select=True,readonly=False, states={'done':[('readonly',True)],'approved':[('readonly',True)],'cancel':[('readonly',True)]}),
    'state': fields.selection(STATE_SELECTION,'State', readonly=True, select=True),
    'type': fields.selection(TYPE_SELECTION,'Ticket Type',required=True,select=True ,states={'done':[('readonly',True)],'cancel':[('readonly',True)]}),
    'user_id':  fields.many2one('res.users', 'Responsible', readonly=True , ),
    'info': fields.text('Mission or Training Information', size=256 ,states={'done':[('readonly',True)],'cancel':[('readonly',True)]}),
    'notes': fields.text('Notes', size=256 ,states={'done':[('readonly',True)]}),
    'company_id': fields.many2one('res.company','Company',required=True,readonly=True),
    'employee_ids': fields.many2many('hr.employee', 'employee_ticket_booking_rel', 'ticket_booking_id', 'emp_id', 'Employees',readonly=False, states={'done':[('readonly',True)],'approved':[('readonly',True)],'cancel':[('readonly',True)]}),
    'department_id':fields.many2one('hr.department', 'Department',readonly=True,states={'draft':[('readonly',False)],'confirmed':[('readonly',False)],}, ),
#    'voucher_no': fields.char('Voucher', size=64,readonly=True),
    'foreigners_lines_id':fields.one2many('foreigners.ticket.lines','request_id','Foreigners',readonly=True,states={'draft':[('readonly',False)]}),
    'procedure_for': fields.selection(PROCEDURE_SELECTION,'Procedure For',help="To decide The procedure is for sudanese of foreigner",required=True,readonly=True,states={'draft':[('readonly',False)]}),
    'account_voucher_ids': fields.many2many('account.voucher', 'ticket_voucher', 'ticket_id', 'voucher_id', 'Account voucher',readonly=True),
    'payment_selection': fields.selection(PAYMENT_SELECTION,'Payment',states={'done':[('readonly',True)]}, select=True),
    'enrich_category':fields.many2one('payment.enrich','Enrich',readonly=True,states={'approved':[('readonly',False)]}),
    }
    _sql_constraints = [
        ('name_uniq', 'unique(name)', 'Ticket booking Reference must be unique !'), 
                        
        ]
    _defaults = {
                'name': lambda self, cr, uid, context: '/',
                'user_id': lambda self, cr, uid, context: uid,
                'date': time.strftime('%Y-%m-%d'),
                'date_of_travel': time.strftime('%Y-%m-%d'),
                'date_of_return': time.strftime('%Y-%m-%d'),
                'state': 'draft',
#    		'voucher_no':'/',
                'travel_purpose':'other',
		'type':'internal',
		'procedure_for' : 'sudanese',
                'company_id': lambda self, cr, uid, c: self.pool.get('res.company')._company_default_get(cr, uid, 'ticket.booking', context=c),

                }

     
    def confirmed(self, cr, uid, ids, context=None): 
        """ 
        Workflow function to change the state to confirmed.

        @return: Boolean True 
        """ 
        self.write(cr, uid, ids, {'state':'confirmed'})
        return True

    def approved(self,cr,uid,ids,context=None):
        """ 
        Workflow function to change the state to approved.

        @return: Boolean True 
        """ 
        self.write(cr, uid, ids, {'state':'approved'},context=context)
        return True

    def dept_confirm(self, cr, uid, ids, context=None):
        """ 
        Workflow function to change the state to dept_confirm and check
        employee and foreigners.

        @return: Boolean True 
        """ 
        for record in self.browse(cr, uid, ids, context=context):
	  if record.procedure_for == 'sudanese':
		if not record.employee_ids : 
			raise osv.except_osv(_('Error'), _("Please enter the Employees"))
	  else:
		if not record.foreigners_lines_id : 
			raise osv.except_osv(_('Error'), _("Please enter the Foreigners"))                       
        self.write(cr, uid, ids, {'state':'dept_confirm'})
        return True

    def admin_affiars_confirm(self, cr, uid, ids, context=None):
        """ 
        Workflow function to change the state to admin_affiars_confirm.

        @return: Boolean True 
        """             
        self.write(cr, uid, ids, {'state':'admin_affiars_confirm'})
        return True

    
    def create_voucher(self,cr,uid,ids,context=None):
        """ 
        Function to create voucher and change the state to done

        @return: Id of created voucher 
        """
        ticket_booking_obj = self.pool.get('ticket.booking')
        account_journal_obj = self.pool.get('account.journal')   
        account_obj = self.pool.get('account.account')
        voucher_obj = self.pool.get('account.voucher')
        voucher_line_obj = self.pool.get('account.voucher.line')
        affairs_account_obj = self.pool.get('admin_affairs.account') 
        affairs_model_obj = self.pool.get('admin.affairs.model')
        payment_enrich_obj = self.pool.get('payment.enrich')
        payment_enrich_lines_obj = self.pool.get('payment.enrich.lines')
        notes =''
        for record in self.browse(cr, uid, ids, context=context):
            if record.cost_of_travel < 1 :
                raise osv.except_osv(_('No cost !'), _('You have to insert cost.'))
            else:
               	notes = '\n'+'This is Ticket Booking number: '+ record.name + ' for the purpose is :' + record.travel_purpose
            if record.payment_selection == 'enrich':
				#details = smart_str('Public Relation Request No:'+record.name+'\nProcedure For:'+record.procedure_for+'\nprocedure:'+record.procedure_id.name+'\nPurpose:'+record.purpose.name)
				#details = 'Public Relation Request No:'+record.name
				enrich_payment_lines_id = payment_enrich_lines_obj.create(cr, uid, {
					'enrich_id':record.enrich_category.id,
                        		'cost': record.cost_of_travel,
					'date':time.strftime('%Y-%m-%d'),
					'state':'draft',
                        		'name':notes,
					'department_id':record.department_id.id,

                            				}, context=context)
       	 			self.write(cr, uid, ids, {'state':'done'},context=context)
            elif record.payment_selection == 'voucher' : 
        	    affairs_model_ids = affairs_model_obj.search(cr, uid, [('model','=','ticket.booking')], context=context)
        	    affairs_account_ids = affairs_account_obj.search(cr, uid, [('model_id','=',affairs_model_ids[0])], context=context)
        	    if not affairs_account_ids:
                	raise osv.except_osv(_('Error'), _("Please enter the Ticket Booking accounting configuration"))
        	    affairs_account = affairs_account_obj.browse(cr, uid, affairs_account_ids[0], context=context)
        	    account_ids = account_obj.search(cr, uid, [('company_id','=',record.company_id.id),('code','=',str(affairs_account.code))], context=context)
        	    journal_ids =  account_journal_obj.search(cr, uid, [('company_id','=',record.company_id.id),('name','=',affairs_account.name_type.name)], context=context)
        	    journal_id = journal_ids and journal_ids[0] or affairs_account.journal_id.id
        	    account_id = account_ids and account_ids[0] or affairs_account.account_id.id
        	    analytic_id = affairs_account.analytic_id
        # Creating Voucher
        	    occasion_voucher=[]
                    voucher_id = voucher_obj.create(cr, uid, {
                        'amount': record.cost_of_travel,
                        'type': 'ratification',
                        'date': time.strftime('%Y-%m-%d'),
                        'partner_id': record.travel_agency.id, 
                        'department_id': record.department_id.id ,
                        'state': 'draft',
                        'journal_id':journal_id , 
                        'narration': notes,
                        #'amount_in_word':amount_to_text_ar(record.cost_of_travel),

                            }, context={})   
                #voucher_number = voucher_obj.browse(cr,uid,voucher_id,context=context)
            	    occasion_voucher.append(voucher_id) 
        #Creating voucher lines
                    voucher_line_dict={
                     'name': record.name,
                     'voucher_id':voucher_id,
                     'account_analytic_id':analytic_id and analytic_id.id,
                     'amount':record.cost_of_travel,
                     'type':'dr',
                               }
                    if account_id:
                        voucher_line_dict.update({'account_id':account_id })
                    voucher_line=voucher_line_obj.create(cr,uid,voucher_line_dict)
                    #################### update workflow state###############
                    voucher_state = 'draft'
                    if record.company_id.affairs_voucher_state : 
                        voucher_state = record.company_id.affairs_voucher_state 
                    if voucher_id:
                        wf_service = netsvc.LocalService("workflow")
                        wf_service.trg_validate(uid, 'account.voucher',voucher_id, voucher_state, cr)
                        voucher_obj.write(cr, uid, voucher_id, {'type':'ratification','ratification':True,'state':voucher_state}, context)        
                    cr.execute('insert into ticket_voucher (ticket_id,voucher_id) values(%s,%s)',(record.id,voucher_id))
                    self.write(cr, uid, ids, {'state':'done'})
                    return voucher_id
    
    def done(self,cr,uid,ids,context=None):
        """ 
        Workflow function to create voucher and calling copy_attachment() method

        @return: Boolean True 
        """
        voucher_id = self.create_voucher(cr, uid, ids, context)
        # Calling copy attachment method
        copy_attachments(self,cr,uid,ids,'ticket.booking',voucher_id,'account.voucher', context)
        return True

    def modify_ticket(self,cr,uid,ids,context=None):
        """ 
        Function to reset the modify ticket.

        @return: Boolean True 
        """
        if not len(ids):
            return False
        wf_service = netsvc.LocalService("workflow")
        for s_id in ids:
            wf_service.trg_delete(uid, 'ticket.booking', s_id, cr)            
            wf_service.trg_create(uid, 'ticket.booking', s_id, cr)
            res = wf_service.trg_validate(uid, 'ticket.booking',s_id, 'draft', cr) 
            res = wf_service.trg_validate(uid, 'ticket.booking',s_id, 'dept_confirm', cr)
            res = wf_service.trg_validate(uid, 'ticket.booking',s_id, 'admin_affiars_confirm', cr) 
            res = wf_service.trg_validate(uid, 'ticket.booking',s_id, 'confirmed', cr) 
            res = wf_service.trg_validate(uid, 'ticket.booking',s_id, 'approved', cr)  
            #self.write(cr, uid, s_id, {'state':'dept_confirm'})
        return True

    
    def cancel(self, cr, uid, ids, notes='', context=None):
        """ 
        Workflow function changes order state to cancel and writes note
	    which contains Date and username who do cancellation.

	    @param notes: contains information of who & when cancelling order.
        @return: Boolean True
        """
        notes = ""
        u = self.pool.get('res.users').browse(cr, uid,uid).name
        notes = notes +'\n'+'Ticket Booking Cancelled at : '+time.strftime('%Y-%m-%d') + ' by '+ u
        self.write(cr, uid, ids, {'state':'cancel','notes':notes})
        return True

    def ir_action_cancel_draft(self, cr, uid, ids, context=None):
        """ 
        Changes state to Draft and reset the workflow.

        @return: Boolean True 
        """
        if not len(ids):
            return False
        wf_service = netsvc.LocalService("workflow")
        for s_id in ids:
            self.write(cr, uid, s_id, {'state':'draft'})
            wf_service.trg_delete(uid, 'ticket.booking', s_id, cr)            
            wf_service.trg_create(uid, 'ticket.booking', s_id, cr)
        return True

    def unlink(self, cr, uid, ids, context=None):
        """
        Delete Ticket Booking record if record in draft or cancel state,
        and create log message to the deleted record.

        @return: super unlink() method
        """
        ticket_request = self.read(cr, uid, ids, ['state'], context=context)
        unlink_ids = []
        for s in ticket_request:
            if s['state'] in ['draft', 'cancel']:
                unlink_ids.append(s['id'])
            else:
                raise osv.except_osv(_('Invalid action !'), _('Sorry in order to delete a ticket request(s), it must be cancelled first!'))
        wf_service = netsvc.LocalService("workflow")
        for id in unlink_ids:
            wf_service.trg_validate(uid, 'ticket.booking', id, 'request_cancel', cr)
            record_name = self.browse(cr, uid, id, context=context).name
            message = _("Ticket Booking '%s' has been deleted.") % record_name
            self.log(cr, uid, id, message)
        return super(ticket_booking, self).unlink(cr, uid, unlink_ids, context=context)


class foreigners_ticket_lines(osv.Model):
    """
    To manage foreigner's ticket"""

    _name = "foreigners.ticket.lines"
    _columns = {
                'name': fields.text('Specification', size=256 ),
       		'request_id': fields.many2one('ticket.booking', 'Foreginer', ondelete='cascade'),
		'foreigner_id': fields.many2one('public.relation.foreigners', 'Foreginers',),
                'foreigner_name': fields.related('foreigner_id', 'foreigner_name', type='char', relation='public.relation.foreigners', string='Foreigner Name', readonly=True,store=True),
                'passport_num': fields.related('foreigner_id', 'passport_number', type='char', relation='public.relation.foreigners', string='Passport', readonly=True,store=True),
               }
       
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
