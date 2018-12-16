# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################
import time
from tools.translate import _
from osv import fields,osv
from datetime import datetime
from openerp import netsvc


class asset_custody_line(osv.osv): 
    _inherit = "asset.custody.line"

    _columns = {
        'note': fields.char("Note"),
        'select': fields.boolean(string='Select'),
    }

 
class asset_custody(osv.osv):

    _inherit = "asset.custody"

    def _get_type(self, cr, uid,context=None):

        """ Determine the asset's type"""

        custody_type = 'request'
        if context:
            if context.has_key('type'): custody_type = context['type']
        return custody_type

    USERS_SELECTION = [
		('admin', 'Supply Department'),
		('tech', 'Techncial Services Department'),
		('arms', 'Arms Department'),
		('veichles', 'Veichles Department'),
		('medic', 'Medic Department'),
		('maintainance', 'Maintainance Department'),
					 ]

    STATE_SELECTION = [
        ('draft', 'Draft'),
        ('transfer', 'Transfer'),
        ('confirmed', 'Confirmed'),
        ('approved', 'Approved'),
        ('recived', 'Recived'),
        ('canceled', 'Canceled'),
       ]

    _columns = {
        'state': fields.selection(STATE_SELECTION, 'State', readonly=True, select=True),
        'stock_journal_id': fields.many2one('stock.journal', 'Journal',),
	    'type' : fields.selection([('request','Request'),('return','Return'),('released','Released')], string='Action Type', readonly=True ),
        'executing_agency': fields.selection(USERS_SELECTION, 'Executing Agency', readonly=True, select=True,help='Department Which this request will executed it'),
    }

    _defaults = {
	    'state' : 'draft',
	    'type' : _get_type,
        'executing_agency' : lambda self, cr, uid, c: self.pool.get('res.users').browse(cr, uid, uid, context=c).belong_to ,	
	}

    def transfer(self,cr,uid,ids,context=None):
        """
        Workflow function to change the custody state to transfer
        @return: True
        """
        self.changes_state(cr, uid, ids,{'state': 'transfer'},context=context)     
        return True

    def recived(self,cr,uid,ids,context=None):
        """
        Workflow function to change the custody state to recived
        @return: True
        """
        picking_obj = self.pool.get('stock.picking')
        asset_obj = self.pool.get('account.asset.asset')
        stock_move = self.pool.get('stock.move')
        wf_service = netsvc.LocalService("workflow")
        move_lines =[]
        super(asset_custody, self).recived(cr, uid, ids, context)
        for custody in self.browse(cr, uid, ids):
           if custody.type == 'return'  :
		pick=False
 
                pick_id=0
                for line in custody.asset_line:
                    if line.return_type.remove ==False:
		            pick=True
 
		if pick==True:
		    pick_id = picking_obj.create(cr, uid , {
		                     'type': 'in',
		                     'name': self.pool.get('ir.sequence').get(cr, uid, 'stock.picking.in'),
		                     'origin': custody.name,
		                     'date': custody.date,
		                     'executing_agency': custody.executing_agency,
		                     'partner_id': 1,
		                     'state': 'draft',
		                     #'stock_journal_id' : stock_journal,
		                     'move_lines' : [],
		                    }) 

	        for line in custody.asset_line:

		    move_id=0
		    if line.return_type.remove ==False:
	   	        move_id = stock_move.create(cr, uid, {
		            'name':'return',
		            'picking_id': pick_id,
		            'product_id': line.asset_id.product_id.id,
		            'product_qty': 1,
		            'product_uos_qty': 1,

		            'product_uos': line.asset_id.product_id.uom_id.id,
		            'product_uom': line.asset_id.product_id.uom_id.id,
		            'location_id': line.return_type.stock_journal.location_id.id,
		            'location_dest_id': line.return_type.location_id.id,
		            'picking_id': pick_id,
		            'price_unit': line.asset_id.product_id.standard_price,
		            'state': 'draft',
		            'type':'in',   
		                    }) 
	    	        move_lines.append(move_id)
		    asset_id= line.asset_id.id
		    asset_idd = asset_obj.write(cr, uid,asset_id, {
										 
							
			 'state_rm' : 'released',


 
							},context=context)
		    #asset_obj.unlink(cr,uid,[asset_id],context=None)
		    '''stock_move.action_confirm(cr, uid, move_lines)
		    stock_move.force_assign(cr, uid, move_lines)
		    wf_service.trg_validate(uid, 'stock.picking', pick_id, 'button_confirm', cr)
		    wf_service.trg_validate(uid, 'stock.picking', pick_id, 'button_done', cr)'''
                  
        	return pick_id

    def onchange_all(self, cr, uid, ids, context=None):
        """Onchange method to Set line with false when change in any field.

        @return: dictionary contain the false of the line
        """
        res = {'asset_line':False}
        return {'value': res}


    def release(self,cr,uid,ids,context=None):
        """
        Workflow function to change the custody state to recived
        @return: True
        """

        log_obj= self.pool.get("asset.log")
        picking_obj = self.pool.get('stock.picking')
        asset_obj = self.pool.get('account.asset.asset')
        stock_move = self.pool.get('stock.move')
        wf_service = netsvc.LocalService("workflow")
        move_lines =[]
        pick_id=0
        date = time.strftime('%Y-%m-%d')
        super(asset_custody, self).recived(cr, uid, ids, context)
        for custody in self.browse(cr, uid, ids):
            if custody.type == 'released':
                pick=False
                for line in custody.asset_line:
                    if line.return_type.remove == False and line.select == True:
                        pick=True
            if pick==True:
 
                pick_id = picking_obj.create(cr, uid , {
                             'type': 'in',
                             'name': self.pool.get('ir.sequence').get(cr, uid, 'stock.picking.in'),
                             'origin': custody.name,
                             'date': custody.date,
                             'executing_agency': custody.executing_agency,
                             'partner_id': 1,
                             'state': 'draft',
                             'stock_journal_id' : custody.stock_journal_id.id,
                             'move_lines' : [],
                            }) 


            for line in custody.asset_line:
                move_id=0
                if line.return_type.remove == False and line.select == True:
                    move_id = stock_move.create(cr, uid, {
                        'name':'return',
                        'picking_id': pick_id,
                        'product_id': line.asset_id.product_id.id,
                        'product_qty': 1,
                        'product_uos_qty': 1,
                        'product_uos': line.asset_id.product_id.uom_id.id,
                        'product_uom': line.asset_id.product_id.uom_id.id,
                        'location_id': line.return_type.stock_journal.location_id.id,
                        'location_dest_id': line.return_type.location_id.id,
                        'price_unit': line.asset_id.product_id.standard_price,
                        'state': 'draft',
                        'type':'in',   
                                }) 
                    move_lines.append(move_id)
 
                asset_id= line.asset_id.id
                if line.return_type.remove == False and line.select == True:
                    log_rec={
                    'date':custody.date,
                    'department_id':custody.department_id.id,
                    'employee_id':custody.employee_id.id,
                    'state':'released',
                    'picking_id':pick_id,
                    'office_id':line.asset_id.office_id.id,
                    'asset_id':line.asset_id.id,
                    }
                    log_id=log_obj.create(cr,uid,log_rec,context=context)

                    asset_idd = asset_obj.write(cr, uid,asset_id, {'state_rm' : 'released','picking_id':pick_id,'return_date':date},context=context)
                elif line.return_type.remove == True and line.select == True:
                    log_rec={
                    'date':custody.date,
                    'department_id':custody.department_id.id,
                    'employee_id':custody.employee_id.id,
                    'state':'damage',
                    'office_id':line.asset_id.office_id.id,
                    'asset_id':line.asset_id.id,
                    'picking_id':pick_id,
                    }
                    log_id=log_obj.create(cr,uid,log_rec,context=context)

                    asset_idd = asset_obj.write(cr, uid,asset_id, {'state_rm' : 'damage','return_date':date},context=context)
                  
            return pick_id


    def return_custody(self,cr,uid,ids,context=None):
        """
         Return all Custody that match the given data.
        """
        custody_ids_dept=[]
        custody_ids_office=[]
        custody_ids_pro=[]
        custody_ids_cat=[]
        custody_ids_emp=[]
        custody_ids=[]
        temp1=[]
        temp2=[]
        temp3=[]
        department_ids=[]
        product_ids=[]
        office_id=0
        employee_id=0
        custody_obj = self.pool.get('account.asset.asset')
        product_obj = self.pool.get('product.product')
        department_obj = self.pool.get('hr.department')

 
 
        for custody in self.browse(cr, uid, ids):
            if custody.department_id:
                department_id=0
                department_ids=[]
                department_id=custody.department_id.id
                department_ids= department_obj.search(cr, uid, [('id', 'child_of', department_id)])
                custody_ids_dept=custody_obj.search(cr,uid,[('department_id','in',department_ids),('asset_type','=','custody'),('state_rm','not in',('draft','released','damage'))])

            if custody.office:
                  office_id=0
                  office_id=custody.office.id
                  custody_ids_office=custody_obj.search(cr,uid,[('office_id','=',office_id),('asset_type','=','custody'),('state_rm','not in',('draft','released','damage'))])



            if custody.employee_id:
               employee_id=0
               employee_id=custody.employee_id.id
               custody_ids_emp=custody_obj.search(cr,uid,[('employee_id','=',employee_id),('asset_type','=','custody'),('state_rm','not in',('draft','released','damage'))])


           
            if custody.product_id:
                product_ids.append(custody.product_id)
                custody_ids_pro=custody_obj.search(cr,uid,[('product_id','=',custody.product_id.id),('asset_type','=','custody'),('state_rm','not in',('draft','released','damage'))])


            if custody.cat_id and not custody.product_id:
                product_ids += product_obj.search(cr,uid,[('categ_id','=',custody.cat_id.id) ]) 


                custody_ids_pro=custody_obj.search(cr,uid,[('product_id','in',product_ids),('asset_type','=','custody'),('state_rm','not in',('draft','released','damage'))])
            if custody_ids_dept and custody_ids_office:
                temp1 = list(set(custody_ids_dept).intersection(set(custody_ids_office)))
            elif custody_ids_dept and not custody_ids_office:
                temp1 = list(set(custody_ids_dept))
            elif custody_ids_office and not custody_ids_dept:
                temp1 = list(set(custody_ids_office))
            if custody_ids_pro and custody_ids_emp:
                temp2 = list(set(custody_ids_pro).intersection(set(custody_ids_emp)))
            elif custody_ids_pro and not custody_ids_emp:
                temp2 = list(set(custody_ids_pro))
            elif custody_ids_emp and not custody_ids_pro:
                temp2 = list(set(custody_ids_emp))
            if temp1 and temp2:
                custody_ids=list(set(temp1).intersection(set(temp2)))
            elif temp1 and not temp2:
                custody_ids=list(set(temp1))
            elif temp2 and not temp1:
                custody_ids=list(set(temp2))
 


        return custody_ids

    def create_return_line(self, cr, uid, ids, context=None):
            custody_obj = self.pool.get('account.asset.asset')
            for order in self.browse(cr, uid, ids, context=context):
                custody_ids=order.return_custody()
                if order.asset_line:
                    line_ids=[]
                    for asset in  order.asset_line:
                        line_ids.append(asset.id)
                        self.pool.get('asset.custody.line').unlink(cr,uid,line_ids)
                for custody in custody_obj.browse(cr,uid,custody_ids,context=context):
                    line_ids = self.pool.get('asset.custody.line').search(cr,uid,[('asset_id','=',custody.id),('custody_id','=',order.id)],context=context)
                    
                    if not line_ids:
                        line_id = self.pool.get('asset.custody.line').create(cr, uid ,{
                                 'custody_id': order.id,
                                 'product_id':custody.product_id.id,
                                 'serial_no':custody.serial,
                                 'asset_id':custody.id,
                                 'office_id': custody.office_id and custody.office_id.id,
                                 'department_to': custody.department_id and custody.department_id.id,
                                 'employee_to': custody.employee_id and custody.employee_id.id ,
                                 'custody_type': custody.custody_type , 
                                 'return_date':order.date,
                                 'executing_agency': order.executing_agency , 
                                 'time_scale': 'constant' , 
                                 'qty': 1, 
     
                    },context=context) 
                    else:
						
            			return True


#----------------------------------------------------------
# Custody Return Type inherit
#----------------------------------------------------------
class custody_return_type(osv.osv):
    _inherit = "custody.return.type"

    USERS_SELECTION = [
        ('admin', 'Supply Department'),
        ('tech', 'Techncial Services Department'),
        ('arms', 'Arms Department'),
]
    _columns = {
	'location_id':fields.many2one('stock.location', required=True,string='Location'),
        'stock_journal': fields.many2one('stock.journal', 'Journal',required=True,),
        'remove': fields.boolean('Remove'),
	'executing_agency':fields.selection(USERS_SELECTION, 'Executing Agency', required=True, select=True,help='Department Which this request will executed it'),
    }

custody_return_type()


	

