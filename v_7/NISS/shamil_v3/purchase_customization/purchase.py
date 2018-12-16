# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

from openerp.osv import osv, fields, orm
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp
import logging
_logger = logging.getLogger(__name__)

class purchase_order(osv.Model):
    """ 
    To change state values"""

    _inherit = 'purchase.order'
    USERS_SELECTION = [
        ('admin', 'Supply Department'),
        ('tech', 'Techncial Services Department'),
        ('arms', 'Arms Department'),
                     ]
    def next_by_id(self, cr, uid, sequence_id, context=None):
        """
        Override to edit Sequences to read company from res_user.
 
        @param sequence_id: sequence id 
        @return: object _next method
        """
        seq_obj = self.pool.get('ir.sequence')
        user_obj = self.pool.get('res.users')
        self.check_access_rights(cr, uid, 'read')
        company_id = user_obj.browse(cr, uid, uid).company_id.id 
        ids = seq_obj.search(cr, uid, ['&',('id','=',
sequence_id),('company_id','in',[company_id, False])])
        return seq_obj._next(cr, uid, ids, context)
 
    def next_by_code(self, cr, uid, sequence_code,executing_agency, context=None):
        """
        Gets the sequence by code.
 
        @param sequence_code: Code of the sequence by which we'll fetch the sequence
        @param context: standard dictionary
        @return: object _next method
        """
        seq_obj = self.pool.get('ir.sequence')
        user_obj = self.pool.get('res.users')
        self.check_access_rights(cr, uid, 'read')
        #Get the company only from user
        company_id = user_obj.browse(cr, uid, uid).company_id.id 
        ids = seq_obj.search(cr, uid, ['&',('code','=',
sequence_code),('company_id','in',[company_id,False]),('executing_agency','=', executing_agency)])
        return seq_obj._next(cr, uid, ids, context)
     
 
    def get_id(self, cr, uid, executing_agency,  sequence_code_or_id,code_or_id='id', context=None):
        """ 
        Draw an interpolated string using the specified sequence.
        The sequence to use is specified by the ``sequence_code_or_id``
        argument, which can be a code or an id (as controlled by the
        ``code_or_id`` argument. This method is deprecated.
              
        @param sequence_code_or_id: code or id of the sequence
        @param code_or_id: type of the sequence
        @return: object next_by_code or next_by_id method
        """
        _logger.debug("ir_sequence.get() and ir_sequence.get_id() are deprecated. "
            "Please use ir_sequence.next_by_code() or ir_sequence.next_by_id().")
        if code_or_id == 'id':
            return self.next_by_id(cr, uid, sequence_code_or_id, executing_agency,context)
        else:
            return self.next_by_code(cr, uid, sequence_code_or_id, executing_agency,context)
 
    def get(self, cr, uid, code,executing_agency, context=None):
        """ 
        Draw an interpolated string using the specified sequence.
        The sequence to use is specified by its code. This method is
        deprecated.
 
        @param code: code of the sequence
        @return: object get_id method   
        """
        return self.get_id(cr, uid, executing_agency,  code, 'code', context)
 
    def create(self, cr, user, vals, context=None):
        """ 
        Override to edit the name field by a new sequence. 
 
        @return: new object id 
        """
        if ('name' not in vals) or (vals.get('name')=='/'):
            seq_obj_name =  'purchase.order'
            ir_id = self.pool.get('ireq.m').search(cr , user , [('id' , '=' , vals['ir_id'])])
            if ir_id:
               for rec in self.pool.get('ireq.m').browse(cr ,user , ir_id ):
                    executing_agency = rec.executing_agency
                    vals['name'] = self.pool.get('purchase.order').get(cr, user, seq_obj_name , executing_agency)
        new_id = super(purchase_order, self).create(cr, user, vals, context)
        return new_id


    STATE_SELECTION = [
        ('draft', 'Draft'),
        ('sign', 'In progress'),
        ('confirmed', 'Complete'),
        ('approved', 'Closed'),
        ('done', 'Done'),
        ('cancel', 'Cancelled'),
        ('wait', 'Waiting'),
        ('except_picking', 'Shipping Exception'),
        ('except_invoice', 'Invoice Exception'),
    ]
    
    _columns = {
        'state': fields.selection(STATE_SELECTION, 'State', readonly=True, help="The state of the purchase order or the quotation request. A quotation is a purchase order in a 'Draft' state. Then the order has to be confirmed by the user, the state switch to 'Confirmed'. Then the supplier must confirm the order to change the state to 'Approved'. When the purchase order is paid and received, the state becomes 'Done'. If a cancel action occurs in the invoice or in the reception of goods, the state becomes in exception.", select=True),
        'executing_agency':fields.selection(USERS_SELECTION, 'Executing Agency',select=True ,help='Department Which this request will executed it'),
                }
    
    
    _defaults = {
                 
          'executing_agency' : lambda self, cr, uid, c: self.pool.get('res.users').browse(cr, uid, uid, context=c).belong_to ,

                }

    
class purchase_order_line(osv.osv):
    """
    To add fields to manage partial picking """

    _inherit = 'purchase.order.line'  
    _columns = {
                'all_quantity_picking': fields.boolean('All Quantity Picking',),
                'picking_quantity': fields.float('Picking Quantity',digits=(16,4)),
                }
    _defaults = {
                 'picking_quantity': 0.0,
                 'all_quantity_picking': False,
                 }    

    
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
