# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

from openerp.osv import fields, osv,orm
import netsvc
import time
from datetime import datetime,date,timedelta
from openerp.tools.translate import _
import decimal_precision as dp

#
# Model definition
#
class enrich_category(osv.osv):
    """
    To manage enrich category """

    _name = "enrich.category"
    _description = 'enrich category'
    _columns = {
                'name': fields.char('Name', size=64,required=True ),
                'company_id': fields.many2one('res.company', 'Company', required=True, readonly=True),
	        'department_id':fields.many2one('hr.department', 'Department',required=True, ),
               }
    _defaults = {
               'company_id': lambda self, cr, uid, c: self.pool.get('res.company')._company_default_get(cr, uid, 'enrich.category', context=c),
		}
       
  
class  payment_enrich(osv.osv):
    """
    To manage enrich operations """

    def create(self, cr, user, vals, context=None):
        """
        Create new entry sequence for every payment enrich

        @param vals: list of record to be approved
        @param context: context arguments, like lang, time zone
        @return: super create() method 
        """
        if ('name' not in vals) or (vals.get('name')=='/'):  
            vals['name'] = self.pool.get('ir.sequence').get(cr, user, 'payment.enrich')
        return super(payment_enrich, self).create(cr, user, vals, context)
    
    def copy(self, cr, uid, id, default=None, context=None):
        """
        Override copy function to edit default value.

        @param default : default vals dict 
        @return: super copy() method  
        """
        if default is None:
            default = {}
        if context is None:
            context = {}
        default.update({
            'name': self.pool.get('ir.sequence').get(cr, uid, 'payment.enrich'),
            
        })
        return super(payment_enrich, self).copy(cr, uid, id, default, context)

    def _amount_all(self, cr, uid, ids,field_name, arg, context={}):
        """ 
        Functional field function to finds the value of total paid of enrich.

        @param field_name: list contains name of fields that call this method
        @param arg: extra arguement
        @return: Dictionary of values
        """
        res={}
        for record in self.browse(cr, uid, ids, context=context):
            val = 0.0
            for line in record.enrich_lines:
		if line.state == 'done' :
                	val += line.cost
            res[record.id] = val 
        return res

    def _amount_all_residual(self, cr, uid, ids,field_name, arg, context={}):
        """ 
        Functional field function to finds the value of total residual of enrich.

        @param field_name: list contains name of fields that call this method
        @param arg: extra arguement
        @return: Dictionary of values
        """
        res={}
        val = 0.0
        for record in self.browse(cr, uid, ids, context=context):
                val = record.amount - record.paid_amount
        res[record.id] = val 
        return res    
    
    def unlink(self, cr, uid, ids, context=None):
        """
        delete the enrich payment record if record in draft or cancel state,
        and create log message to the deleted record.
    
        @return: super unlink() method
        """
        payment_enrich = self.read(cr, uid, ids, ['state'], context=context)
        unlink_ids = []
        for s in payment_enrich:
            if s['state'] in ['draft', 'cancel']:
                unlink_ids.append(s['id'])
            else:
                raise osv.except_osv(_('Invalid action !'), _('In order to delete a service request order(s), it must be cancelled first!'))
        wf_service = netsvc.LocalService("workflow")
        for id in unlink_ids:
            wf_service.trg_validate(uid, 'payment.enrich', id, 'cancel', cr)
            payment_enrich_name = self.browse(cr, uid, id, context=context).name
            message = _("Enrich Payment '%s' has been deleted.") % payment_enrich_name
            self.log(cr, uid, id, message)
        return super(payment_enrich, self).unlink(cr, uid, unlink_ids, context=context)

    def _get_months(sel, cr, uid, context):
       """
       Functional field function to read and returns monthes as list of tuple.

       @return: List of tuple
       """
       months=[(str(n),str(n)) for n in range(1,13)]
       return months

    def name_get(self, cr, uid, ids, context=None):
        """
        Making Analytic Account name appeare like "code name"
        @return: dictionary,name of all analytic account
        """
        return [(r.id, (r.month and r.month+'-' or '')+"Month" +'-'+ (r.desc and r.desc+' ' or '') +'-'+ r.name) for r in self.browse(cr, uid, ids, context=context)]

    STATE_SELECTION = [
    		('draft', 'Draft'),
    		('first_confirmed', 'Waiting for section / officer  / finical & admin affaris manager To confirm'),
    		('second_confirmed', 'Waiting for Department manager / PRM manager To Approve'),
    		('confirmed', 'Waiting for closing the Enrich'),
    		('done', 'Done'),
    		('cancel', 'Cancel'), 
    			]
    
    _name = "payment.enrich"
    _description = 'Payment Enrich'
    _order = "name desc"
    
    _columns = {
	    'name':fields.char('Reference', size=64, required=False, select=True, readonly=True  , help="unique number of the Payment Enrich"),
	    'date' :fields.date('Date',required=True),
            'month': fields.selection(_get_months,'Month', required=True),
            'year': fields.integer('Year',size=32, required=True),
	    'amount':fields.float('Total amount', digits=(16,2),required=True),
	    'residual_amount':fields.function(_amount_all_residual, method=True, digits=(16,2), string='Residual Amount' , store = True , readonly=True),
	    'paid_amount':fields.function(_amount_all, method=True, digits=(16,2), string='Paid Amount' , store = True , readonly=True),
	    'state': fields.selection(STATE_SELECTION,'State', readonly=True, select=True),
	    'user_id':  fields.many2one('res.users', 'Responsible', readonly=True , ),
	    'notes': fields.text('Notes', size=256 ,states={'done':[('readonly',True)]}),
	    'company_id': fields.many2one('res.company','Company',required=True,readonly=True),
	    'enrich_category':fields.many2one('enrich.category','Enrich category',readonly=True,states={'draft':[('readonly',False)]}),
	    'department_id': fields.related('enrich_category','department_id', type='many2one',relation='hr.department',string ='Department',readonly=True, ),
	    'enrich_lines': fields.one2many('payment.enrich.lines', 'enrich_id' , 'Enrich line',states={'done':[('readonly',True)]}),
            'desc': fields.char('Description', size=256,required=True,readonly=True,states={'draft':[('readonly',False)]},),
    }
    _sql_constraints = [
        ('name_uniq', 'unique(name)', 'Enrich Payment Reference must be unique !'), 
                        
        ]
    _defaults = {
                'name': lambda self, cr, uid, context: '/',
                'user_id': lambda self, cr, uid, context: uid,
                'date': time.strftime('%Y-%m-%d'),
                'state': 'draft',
                'year': int(time.strftime('%Y')),
                'company_id': lambda self, cr, uid, c: self.pool.get('res.company')._company_default_get(cr, uid, 'payment.enrich', context=c),

                }


    def first_confirmed(self, cr, uid, ids,context=None):
        """ 
        Workflow function changes state first_confirmed and check record amount .

        @return: Boolean True
        """
        for record in self.browse(cr, uid, ids, context=context):
		if record.amount < 1 :
                	raise osv.except_osv(_('Invalid action !'), _('Please Insert the right cost!'))  
        self.write(cr, uid, ids, {'state':'first_confirmed'})
        return True

    def second_confirmed(self, cr, uid, ids,context=None): 
        """ 
        Workflow function changes state second_confirmed .

        @return: Boolean True
        """
        self.write(cr, uid, ids, {'state':'second_confirmed'})
        return True

    def confirmed(self, cr, uid, ids,context=None):
        """ 
        Workflow function changes state confirmed and check record amount .

        @return: Boolean True
        """
        for record in self.browse(cr, uid, ids, context=context):
		if record.amount < 1 :
                	raise osv.except_osv(_('Invalid action !'), _('Please Insert the right cost!'))  
        self.write(cr, uid, ids, {'state':'confirmed'})
        return True 


    def done(self,cr,uid,ids,context=None):
       """ 
        Workflow function changes state done and check lines state .

        @return: Boolean True
       """
       for record in self.browse(cr, uid, ids, context=context):
            for line in record.enrich_lines:
		if line.state == 'draft':
                	raise osv.except_osv(_('Invalid action !'), _('Please close All the Lines First Then you can close the Enrich Payment!'))  
       self.write(cr, uid, ids, {'state':'done'},context=context)
       return True

    def modify_enrich(self,cr,uid,ids,context=None):
        """ 
         Reset the workflow and changes state to confirmed.

        @return: True 
        """
        if not len(ids):
            return False
        wf_service = netsvc.LocalService("workflow")
        for s_id in ids:
            wf_service.trg_delete(uid, 'payment.enrich', s_id, cr)            
            wf_service.trg_create(uid, 'payment.enrich', s_id, cr)
            res = wf_service.trg_validate(uid, 'payment.enrich',s_id, 'draft', cr) 
            res = wf_service.trg_validate(uid, 'payment.enrich',s_id, 'confirmed', cr)
        return True

    
    def cancel(self, cr, uid, ids, notes='', context=None):
        """ 
        Workflow function changes state to cancel and writes note.

	    @param notes: contains information of cancelling.
        @return: Boolean True
        """
        # Cancel the payment enrich 
        #if not notes:
        #notes = ""      
        #u = self.pool.get('res.users').browse(cr, uid,uid).name
        #notes = notes +'\n'+'Hospitality services Cancelled at : '+time.strftime('%Y-%m-%d') + ' by '+ u
        #self.write(cr, uid, ids, {'state':'cancel','notes':notes})
        self.write(cr, uid, ids, {'state':'cancel'})
        return True

    def ir_action_cancel_draft(self, cr, uid, ids, context=None):
        """ 
        Changes state to Draft and reset the workflow.

        @return: True 
        """
        if not len(ids):
            return False
        wf_service = netsvc.LocalService("workflow")
        for s_id in ids:
            self.write(cr, uid, s_id, {'state':'draft'})
            wf_service.trg_delete(uid, 'payment.enrich', s_id, cr)            
            wf_service.trg_create(uid, 'payment.enrich', s_id, cr)
        return True


class  payment_enrich_lines(osv.osv):
    """
    To manage admin affairs payment lines """

    STATE_SELECTION = [
    		('draft', 'Draft'),
    		('done', 'Done'),
    		('cancel', 'Cancel'), 
    			]
   	
    _name = "payment.enrich.lines"
    _description = 'Payment Enrich Lines'
    _columns = {
	'enrich_id':fields.many2one('payment.enrich', 'Payment Enrich',readonly=True),
	'department_id':fields.many2one('hr.department', 'Department',required=True,readonly=True ,states={'draft':[('readonly',False)]}),
	'date' :fields.date('Date',readonly=True ,required=True,states={'draft':[('readonly',False)]}),
	'state': fields.selection(STATE_SELECTION,'State', readonly=True, select=True),
        'cost':fields.float('Cost',digits=(18,2),readonly=True , required=True,states={'draft':[('readonly',False)]}),
	'name': fields.text('Name', size=256,required=True),
                    }
    _defaults = {
                'state': 'draft',
                }

    def done(self,cr,uid,ids,context=None):
       """ 
        Workflow function changes state to done and check , update cost.

        @return: Boolean True
       """
       residual = 0.0
       paid = 0.0 
       for record in self.browse(cr, uid, ids, context=context):
	        search_result = self.pool.get('payment.enrich').browse(cr, uid,record.enrich_id.id)
		if record.cost < 1 :
                	raise osv.except_osv(_('Invalid action !'), _('Please Insert the right cost!'))
		if record.cost > search_result.residual_amount :
                	raise osv.except_osv(_('Invalid action !'), _('Your Residual Balance is Less Than your cost!'))
		residual = search_result.residual_amount - record.cost
		paid = search_result.paid_amount + record.cost
		enrich_payment_id = cr.execute("""update payment_enrich set paid_amount=%s , residual_amount=%s where id =%s""",(paid,residual,record.enrich_id.id))
       self.write(cr, uid, ids, {'state':'done'},context=context)
       return True 
 
    def cancel(self, cr, uid, ids, notes='', context=None):
        """ 
        Workflow function changes state to cancel and writes note.

	    @param notes: contains information of cancelling 
        @return: Boolean True
        """
        # Cancel the payment enrich 
        #if not notes:
        #notes = ""      
        #u = self.pool.get('res.users').browse(cr, uid,uid).name
        #notes = notes +'\n'+'Hospitality services Cancelled at : '+time.strftime('%Y-%m-%d') + ' by '+ u
        #self.write(cr, uid, ids, {'state':'cancel','notes':notes})
        self.write(cr, uid, ids, {'state':'cancel'})
        return True

    def ir_action_cancel_draft(self, cr, uid, ids, context=None):
        """ 
        Changes state to Draft and reset the workflow.

        @return: True 
        """
        if not len(ids):
            return False
        wf_service = netsvc.LocalService("workflow")
        for s_id in ids:
            self.write(cr, uid, s_id, {'state':'draft'})
            wf_service.trg_delete(uid, 'payment.enrich.lines', s_id, cr)            
            wf_service.trg_create(uid, 'payment.enrich.lines', s_id, cr)
        return True

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
