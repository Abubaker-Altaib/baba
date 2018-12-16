# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

from osv import osv, fields
from tools.translate import _
import time
import netsvc

#----------------------------------------
# Class fleet vehicles
#----------------------------------------

class fleet_vehicles(osv.osv):
    """
    To add admin affaire information """

    STATE_SELECTION = [
    ('draft', 'Draft'),
    ('confirmed', 'Confirmed'),
    ('cancel', 'Cancel'), 
    ]
       
    _inherit = "fleet.vehicle"
    _columns = {
                #'name': fields.function(_complete_name, type='char', size=256, string="Vehicle Name",store=True),
                'year':fields.many2one('manufacturing.year','Year',states={'confirmed':[('readonly',True)],'cancel':[('readonly',True)]}),
                'depracc':fields.many2one('account.account',string='Depreciation Account',required=False,states={'confirmed':[('readonly',True)],'cancel':[('readonly',True)]}),
                #'schedname':fields.many2one('fleet.service.templ','PM Schedule',help="Preventive maintainance schedule for this vehicle",required=False,states={'confirmed':[('readonly',True)],'cancel':[('readonly',True)]}), must be check with car maintenance module
                 'type': fields.selection([
                        ('truck','Truck'),
                        ('bus','Bus'),
                        ('car','Car'),('generator','Generator')], 'Class', required=True,states={'confirmed':[('readonly',True)],'cancel':[('readonly',True)]},),  
                'status': fields.selection([
                        ('active','Active'),
                        ('inactive','InActive'),
                        ('outofservice','Out of Service'),                        
                        ], 'status', required=True,states={'confirmed':[('readonly',True)],'cancel':[('readonly',True)]},),
                'ownership': fields.selection([
                        ('owned','Owned'),
                        ('rented','Rented'),('generator','Generator'),('mile','Instead mile'),                       
                        ], 'Ownership', required=True,states={'confirmed':[('readonly',True)],'cancel':[('readonly',True)]},), 
                'primarymeter':fields.selection([
                                                 ('odometer','Odometer'),
                                                 ('hourmeter','Hour Meter'),
                                                 ],'Primary Meter',required=True,states={'confirmed':[('readonly',True)],'cancel':[('readonly',True)]},),                                
                'company_id':fields.many2one('res.company','Company',required=True,states={'confirmed':[('readonly',True)],'cancel':[('readonly',True)]},),
               'startodometer':fields.integer('Start Odometer',required=True,states={'confirmed':[('readonly',True)],'cancel':[('readonly',True)]}),
                'cmil':fields.float('Current Mileage',digits = (16,3),states={'confirmed':[('readonly',True)],'cancel':[('readonly',True)]}),
                'bmil':fields.float('Base Mileage',digits=(16,3),help="The last recorded mileage",states={'confirmed':[('readonly',True)],'cancel':[('readonly',True)]}),
                'bdate':fields.date('Recorded Date',help="Date on which the mileage is recorded",states={'confirmed':[('readonly',True)],'cancel':[('readonly',True)]}),               
                          
                #'location':fields.many2one('stock.location','Stk Location',help="Select the stock location or create one for each vehicle(recommended) so that the spares, tyres etc are assossiated with the vehicle when issued",required=False,states={'confirmed':[('readonly',True)],'cancel':[('readonly',True)]}),
                'department_id':fields.many2one('hr.department','Department',states={'confirmed':[('readonly',True)],'cancel':[('readonly',True)]}),  
                'machine_no': fields.char('Machine No', size=64,states={'confirmed':[('readonly',True)],'cancel':[('readonly',True)]}), 
                'employee_id' :fields.many2one('hr.employee', 'Employee',states={'confirmed':[('readonly',True)],'cancel':[('readonly',True)]}),
           	
                'state': fields.selection(STATE_SELECTION,'State', readonly=True, select=True),  
                'user_id':  fields.many2one('res.users', 'Responsible', readonly=True,states={'confirmed':[('readonly',True)],'cancel':[('readonly',True)]} , ), 
                'notes': fields.text('Notes', size=256 ,states={'confirmed':[('readonly',True)],'cancel':[('readonly',True)]}),
                'serial':fields.char('productSerial #',size=50,states={'confirmed':[('readonly',True)],'cancel':[('readonly',True)]}),
		'machine_capacity':fields.char('Machine Capacity',size=50,states={'confirmed':[('readonly',True)],'cancel':[('readonly',True)]}),

               }
    _defaults={
                'state': 'draft', 
                'user_id': lambda self, cr, uid, context: uid,                
                             
              }

    
    def confirmed(self, cr, uid, ids, context=None):
        """
        Workflow function to change state to confirmed.

        @return: Boolean True
        """             
        self.write(cr, uid, ids, {'state':'confirmed'})
        return True
    
    def cancel(self, cr, uid, ids, notes='', context=None):
        """ 
        Workflow function changes order state to cancel and writes note
	    which contains Date and username who do cancellation.

	    @param notes: contains information of who & when cancelling order.
        @return: Boolean True
        """
        notes = ""
        u = self.browse(cr, uid, ids)[0].user_id.name
        notes = notes +'\n'+'vehicle Cancelled at : '+time.strftime('%Y-%m-%d') + ' by '+ u       
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
            wf_service.trg_delete(uid, 'fleet.vehicle', s_id, cr)
            wf_service.trg_create(uid, 'fleet.vehicle', s_id, cr)
        return True
 

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

