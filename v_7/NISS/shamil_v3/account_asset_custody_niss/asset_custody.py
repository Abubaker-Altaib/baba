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
        'serials': fields.many2many('stock.partial.picking.line.serail', 'custody_lines_serials_rel2', 'line_id', 'serial_id', string='Serials', ondelete='CASCADE'),
        'is_serializable': fields.boolean('Serializable'),
    }

    def onchange_product_serial(self, cr, uid, ids, product_id, context={}):
        vals = {}
        vals['is_serializable'] = False
        if product_id:
            product = self.pool.get('product.product').browse(cr, uid, product_id, context)
            if product.custody:
                is_serializable = self.pool.get('product.product').browse(cr, uid, product_id, context).is_serializable
                vals['is_serializable'] = is_serializable

        return {'value': vals}

    def unlink(self, cr, uid, ids, context={}):
        """
        override unlink to unlink serials
        """
        for rec in self.browse(cr, uid, ids, context):
            serials = []
            if rec.serials:
                serials = [x.id for x in rec.serials]
            super(asset_custody_line, self).unlink(cr, uid, [rec.id], context)
            if serials:
                self.pool.get('stock.partial.picking.line.serail').unlink(cr, uid, serials, context)

        return True


 
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
        ('oc', 'Operation Corporation'),
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
	    'type' : fields.selection([('request','Request'),('return','Return'),('released','Released')], string='Action Type', readonly=True ),
        'executing_agency': fields.selection(USERS_SELECTION, 'Executing Agency', readonly=True, select=True,help='Department Which this request will executed it'),
        'company_id': fields.many2one('res.company', 'Company',readonly=True),
        'create_type': fields.selection([('stock','In Stock'),('custody','Out Stock')], 'Entry Type'),
    }

    _defaults = {
	    'state' : 'draft',
	    'type' : _get_type,
        'executing_agency' : lambda self, cr, uid, c: self.pool.get('res.users').browse(cr, uid, uid, context=c).belong_to ,	
	     'company_id': lambda s, cr, uid, c: s.pool.get('res.company')._company_default_get(cr, uid, 'asset.custody', context=c),
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
	asset_log_obj = self.pool.get('asset.log')
        stock_move = self.pool.get('stock.move')
        wf_service = netsvc.LocalService("workflow")
	custody_line_obj = self.pool.get('asset.custody.line')
        move_lines =[]
        super(asset_custody, self).recived(cr, uid, ids, context)
        for custody in self.browse(cr, uid, ids):
	   if custody.type == 'request' :
		if  not custody.stock:  # DATA MIGRATION
			for custody_line in custody.asset_line:
				serials = [x.name for x in custody_line.serials]
				if custody_line.product_id.is_serializable and not custody_line.serial_no:
					raise osv.except_osv(_('Error'),_('Please Enter all Serials') )
				#if len(custody_line.serial_no) != custody_line.qty:
				#        raise osv.except_osv(_('Sorry!'),
				#                             _('Please set the right Serials for the product %s ' % (custody_line.product_id.name,)))
				for new_asset in range(0, int(custody_line.qty)):
					if not custody_line.asset_id:
						# CREATE ASSET ITEM
						if custody.create_type == 'stock':
							asset_id = asset_obj.create(cr, uid , {
										 'name':custody_line.product_id.name,
										 'category_id':'1',
										 'asset_type':'custody',
										 'office_id': custody_line.office and custody_line.office.id or False,
										 'department_id': custody_line.department_to and custody_line.department_to.id or False,
										 'employee_id': custody_line.employee_to and custody_line.employee_to.id or False ,
										 'request_date': custody_line.custody_id.date,
										 'return_date': custody_line.return_date ,
										 'product_id':custody_line.product_id.id,
										 'main_type': custody_line.product_id.categ_id.id,
										 'time_scale': custody_line.time_scale,
										 'executing_agency': custody_line.executing_agency,
										 'custody_type' : custody_line.custody_type,
										 'state_rm' : 'draft',
										 'state': 'confirmed',
										 'serial': custody_line.serial_no,
										 #'serial': custody_line.product_id.is_serializable and serials[new_asset] or False,
							},context=context)
							log_dict = {
								'date': time.strftime('%Y-%m-%d'),
								'department_id': custody_line.department_to and custody_line.department_to.id or False,
								'employee_id': custody_line.employee_to and custody_line.employee_to.id or False,
								'asset_id': asset_id,
								'office_id': custody_line.office and custody_line.office.id or False,
								'state': 'added'
							 } 
							asset_log_obj.create(cr, uid, log_dict, context=context)
							custody_line_obj.write(cr, uid,custody_line.id , {'asset_id':asset_id}, context=context)
						if custody.create_type == 'custody':
							asset_id = asset_obj.create(cr, uid , {
										 'name':custody_line.product_id.name,
										 'category_id':'1',
										 'asset_type':'custody',
										 'office_id':  custody_line.office and custody_line.office.id or False,
										 'department_id': custody_line.department_to and custody_line.department_to.id or False,
										 'employee_id': custody_line.employee_to and custody_line.employee_to.id or False ,
										 'request_date': custody_line.custody_id.date,
										 'return_date': custody_line.return_date ,
										 'product_id': custody_line.product_id.id,
										 'main_type': custody_line.product_id.categ_id.id,
										 'time_scale': custody_line.time_scale,
										 'executing_agency': custody_line.executing_agency,
										 'custody_type' : custody_line.custody_type,
										 'state_rm' : 'assigned',
										 'state': 'confirmed',
										 'serial': custody_line.serial_no,
										 #'serial': custody_line.product_id.is_serializable and serials[new_asset] or False,
							},context=context) 
							log_dict = {
								'date': time.strftime('%Y-%m-%d'),
								'department_id': custody_line.department_to and custody_line.department_to.id or False,
								'employee_id': custody_line.employee_to and custody_line.employee_to.id or False,
								'asset_id': asset_id,
								'office_id': custody_line.office and custody_line.office.id or False,
								'state': 'recieved'
							}
							asset_log_obj.create(cr, uid, log_dict, context=context)
							custody_line_obj.write(cr, uid,custody_line.id , {'asset_id':asset_id}, context=context)
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

    def onchange_all(self, cr, uid, ids,field1,field2,field3,field4,field5,field6, context=None):
        """Onchange method to Set line with false when change in any field.

        @return: dictionary contain the false of the line
        """
        unlink_ids=[]
        res={}
        if not field1 or field2 or field3 or field4 or field5 or field6:
            return {'value': res}
        line_obj=self.pool.get('asset.custody.line')
        if ids:
            for custody in self.browse(cr, uid, ids):
                for line in custody.asset_line:
                    unlink_ids.append(line.id)
                line_obj.unlink(cr,uid,unlink_ids,context=None)
                #custody.create_return_line()
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
                             #'stock_journal_id' : stock_journal,
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
                    'date':time.strftime('%Y-%m-%d'),
                    'department_id':custody.department_id.id,
                    'employee_id':custody.employee_id.id,
                    'state':'released',
                    'asset_id':line.asset_id.id,
                    }
                    log_id=log_obj.create(cr,uid,log_rec,context=context)

                    asset_idd = asset_obj.write(cr, uid,asset_id, { 'state_rm' : 'released',
                                                                    'picking_id':pick_id,
 								    'return_date':date , 
                                              			    'department_id':False ,
								    'office_id' : False,
},context=context)
                elif line.return_type.remove == True and line.select == True:
                    log_rec={
                    'date':time.strftime('%Y-%m-%d'),
                    'department_id':custody.department_id.id,
                    'employee_id':custody.employee_id.id,
                    'state':'damage',
                    'asset_id':line.asset_id.id,
                    }
                    log_id=log_obj.create(cr,uid,log_rec,context=context)

                    asset_idd = asset_obj.write(cr, uid,asset_id, {'state_rm' : 'damage','return_date':date ,'department_id':False ,
								    'office_id' : False,},context=context)
                  
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
            if custody.employee_id:
               employee_id=0
               employee_id=custody.employee_id.id
               custody_ids=custody_obj.search(cr,uid,[('employee_id','=',employee_id),('asset_type','=','custody'),('state_rm','not in',('draft','released','damage'))])
               if not custody_ids:
                return custody_ids
               

            if custody.department_id:
                department_id=0
                department_ids=[]
                department_id=custody.department_id.id
                department_ids= department_obj.search(cr, uid, [('id', 'child_of', department_id)])
                if custody_ids:
                    custody_ids=custody_obj.search(cr,uid,[('id','in',custody_ids),('department_id','in',department_ids),('asset_type','=','custody'),('state_rm','not in',('draft','released','damage'))])
                else:
                    custody_ids=custody_obj.search(cr,uid,[('department_id','in',department_ids),('asset_type','=','custody'),('state_rm','not in',('draft','released','damage'))])

            if custody.office:
                  office_id=0
                  office_id=custody.office.id
                  if custody_ids:
                    custody_ids=custody_obj.search(cr,uid,[('id','in',custody_ids),('office_id','=',office_id),('asset_type','=','custody'),('state_rm','not in',('draft','released','damage'))])
                  else:
                    return custody_ids
                  
            if custody.product_id:
                product_ids.append(custody.product_id)
                if custody_ids:
                    custody_ids=custody_obj.search(cr,uid,[('id','in',custody_ids),('product_id','=',custody.product_id.id),('asset_type','=','custody'),('state_rm','not in',('draft','released','damage'))])
                else:
                    return custody_ids

            if custody.cat_id and not custody.product_id:
                product_ids += product_obj.search(cr,uid,[('categ_id','=',custody.cat_id.id) ]) 
                if custody_ids:
                    custody_ids=custody_obj.search(cr,uid,[('id','in',custody_ids),('product_id','in',product_ids),('asset_type','=','custody'),('state_rm','not in',('draft','released','damage'))])
                else:
                    return custody_ids

        return custody_ids

    def create_return_line(self, cr, uid, ids, context=None):
            custody_obj = self.pool.get('account.asset.asset')
            for order in self.browse(cr, uid, ids, context=context):
                custody_ids=order.return_custody()
                if not custody_ids:
                    raise osv.except_osv(_('Warring !'), _('There Is no Custody Found For specific data'))
                for custody in custody_obj.browse(cr,uid,custody_ids,context=context):
                    line_ids = self.pool.get('asset.custody.line').search(cr,uid,[('asset_id','=',custody.id),('custody_id','=',order.id)],context=context)
                    if not line_ids:
                        line_id = self.pool.get('asset.custody.line').create(cr, uid ,{
                                 'custody_id': order.id,
                                 'product_id':custody.product_id.id,
                                 'asset_id':custody.id,
                                 'office': custody.office_id and custody.office_id.id,
                                 'department_to': custody.department_id and custody.department_id.id,
                                 'employee_to': custody.employee_id and custody.employee_id.id ,
                                 'custody_type': custody.custody_type , 
                                 'return_date':order.date,
                                 'executing_agency': order.executing_agency , 
                                 'time_scale': 'constant' , 
                                 'qty': 1, 
     
                    },context=context) 
            return True

    def confirm(self,cr,uid,ids,context=None):
        """
        inherit confirm to check asset line        
        """
        for custody in self.browse(cr, uid, ids, context=context):
            select=False
            for line in custody.asset_line:
                if not line.custody_type:
                    raise osv.except_osv(_('Warring !'), _('custody type Is required and this custody has no custody type(%s)')%(line.asset_id.name))
                if line.select and custody.type == 'return' and not line.return_type:
                    raise osv.except_osv(_('Warring !'), _('you must Determination the return type for selected custody(%s)')%(line.asset_id.name))
                if line.select:
                    select=True
            if not select and custody.type == 'return':
                raise osv.except_osv(_('Warring !'), _('There Is no custody selected to be return!'))
        return super(asset_custody, self).confirm(cr, uid, ids, context)


    def unlink(self, cr, uid, ids, context={}):
        """
        override unlink to unlink lines
        """
        for rec in self.browse(cr, uid, ids, context):
            lines = []
            if rec.asset_line:
                lines = [x.id for x in rec.asset_line]
            super(asset_custody, self).unlink(cr, uid, [rec.id], context)
            if lines:
                self.pool.get('asset.custody.line').unlink(cr, uid, lines, context)

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


	

