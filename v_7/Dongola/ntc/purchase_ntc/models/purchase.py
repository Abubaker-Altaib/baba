# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2016-2017 NCTR (<http://www.nctr.sd>).
#
############################################################################
from openerp.osv import fields, osv
from openerp import netsvc
from openerp.tools.translate import _
from lxml import etree
from openerp.osv.orm import setup_modifiers
from admin_affairs.model.email_serivce import send_mail

class product_template(osv.osv):
    _inherit = "product.template"
    
    _defaults = {
        'categ_id' : False,
    }


class purchase_requisition(osv.osv):
    _inherit = "purchase.requisition"
    _order = 'id desc'
      
    STATE_SELECTION =  [
         ('draft', 'Sign'),
         ('confirm', 'Department Manager Approve'),
         ('approve', 'General Department Manager Approve'),#confirm_dept
         ('HRM_approve1', 'HRM General Department Manager '),#*
         ('commite_confirm', 'Commite Manager Confirm'),#*
         ('GM_approve2', ' General Manager Approve'),#*
         ('in_progress', 'Tender'),
         ('done', 'Purchase Done'),
         ('cancel', 'Cancelled'),
         ('budget_approve', 'Budget Approve'),
         ('purchase_order', 'Purchase Order'),]

    _columns = {
        
        'user_ids': fields.one2many('purchase.tender.members.info', 'requisition_id' , string='Users'),
        'state': fields.selection(STATE_SELECTION, 'Status', required=True, readonly=True),
    }   



    message = "Dear Sir, You have Purchase Requisition Waiting for Your Signature"
    
    def get_manager_id(self, cr, uid,  ids, user, context=None):
        """ Getting Manager ID """
        
        if user:
            emp_obj = self.pool.get('hr.employee')
            dept_obj = self.pool.get('hr.department')
            
            
            emp_id = emp_obj.search( cr, uid, [('user_id' , '=' , user)])
            parent_id = emp_obj.browse( cr, uid, emp_id[0]).department_id.parent_id.id
            cr.execute('SELECT res_users.id as user_id, res_users.login as login, hr_department.manager_id as manager_id, res_partner.email as email ' \
            'FROM public.res_users, public.hr_employee, public.resource_resource, public.hr_department, public.res_partner ' \
            'WHERE hr_department.manager_id = hr_employee.id '\
            'AND hr_employee.resource_id = resource_resource.id '\
            'AND resource_resource.user_id = res_users.id '\
            'AND res_users.partner_id = res_partner.id '\
            'AND hr_department.id = %s', (parent_id,))
            res = cr.dictfetchall()
            return [res[0]['user_id']]
        
        
        
        return False
    
    
    
    
    def commite_confirm(self,cr,uid,ids,context=None):
        """ Function For Change Order State into commite_confirm """
        
        
        for rec in self.browse(cr,uid,ids):
            if rec.purchase_ids:
               for quote in rec.purchase_ids:
                      if quote.state == 'budget_approved':
                         self.pool.get('purchase.order').action_invoice_create(cr, uid, [quote.id], context=context)
                      
                      
                        
            self.write(cr,uid,ids,{'state':'commite_confirm'})
        send_mail(self, cr, uid, ids[0] , 'purchase_ntc.group_commite_members_manager', "New Purchase Requisition", self.message , user=False  , department=False,context=context)    
        return True  
    
    
    
    
    def tender_confirm(self, cr, uid, ids, context=None):
        super(purchase_requisition,self).tender_confirm(cr, uid, ids, context=context)
        send_mail(self, cr, uid, ids[0] , '', "New Purchase Requisition", self.message , user=self.get_manager_id( cr, uid, ids, uid)  , department=False,context=context)
        return True
    
    
    def tender_approve(self, cr, uid, ids, context=None):
        send_mail(self, cr, uid, ids[0] , '', "New Purchase Requisition", self.message , user=self.get_manager_id( cr, uid, ids, uid)  , department=False,context=context)
        self.write(cr,uid,ids,{'state' : 'approve'})
        return True
    
    
    def tender_HRM_approve1(self, cr, uid, ids, context=None):
        send_mail(self, cr, uid, ids[0] , 'base_custom.group_general_hr_manager' , "New Purchase Requisition", self.message , user=False  , department=False,context=context)
        self.write(cr,uid,ids,{'state' : 'HRM_approve1'})
        return True
        
        
    def tender_GM_approve2(self, cr, uid, ids, context=None):
        send_mail(self, cr, uid, ids[0] , 'base_custom.group_account_general_manager' , "New Purchase Requisition", self.message , user=False  , department=False,context=context)
        self.write(cr,uid,ids,{'state' : 'GM_approve2'})
        return True
      
             
        
        
         
    
    
    
    
    def back_to_quatations_entry(self, cr, uid, ids, context=None):
        
        """ Back To Quatations Entry """
        
        for rec in self.browse(cr,uid,ids):
            if not rec.purchase_ids:
               raise osv.except_osv(_('Error!'), _('The Order havent Quotations .... '))
            for quote in rec.purchase_ids:
                
                self.pool.get('purchase.order').action_cancel_draft(cr, uid, [quote.id], context=context)
            send_mail(self, cr, uid, ids[0] , 'purchase_ntc.group_commite_members_manager', "Purchase Requisition Returned from Internal Auditor For Correction", self.message , user=False  , department=False,context=context)    
            return True
        
        
        
        
    def tender_HRM_approve(self, cr, uid, ids, context=None):
        wf_service = netsvc.LocalService('workflow')
        for req in self.browse(cr, uid, ids, context=context):
            req.write({'state':'HRM_approve1'})
            wf_service.trg_validate(uid, 'purchase.requisition', req.id, 'tender_GM_approve1', cr)
            cr.execute("SELECT uid as User_id FROM res_groups_users_rel rel left join res_groups grp on (grp.id = rel.gid)   WHERE grp.name='%s' and uid <> 1" % ('Committee User'))
            res = cr.dictfetchall()
            user_ids = []
            "Write The Committe Members In Users Field"
            if res:
               for user in res:
                   #user_ids.append(user['user_id'])
                   line_id = self.pool.get('purchase.tender.members.info').create(cr,uid, {
                       
                       'user_id' : user['user_id'],
                       'requisition_id' : ids[0],
                       
                       
                       })
                   
               #self.write(cr ,uid ,ids ,{'user_ids' : [(6 ,False ,user_ids )] } )
        return True

    

    def tender_in_progress(self, cr, uid, ids, context=None):
        wf_service = netsvc.LocalService('workflow')
        purchase_order_pool = self.pool.get('purchase.order')
        for req in self.browse(cr, uid, ids, context=context):
            req.write({'state':'in_progress'})
            if not req.purchase_ids:
                wf_service.trg_validate(uid, 'purchase.requisition', req.id, 'tender_in_progress', cr)
                send_mail(self, cr, uid, ids[0] , 'purchase_wafi.group_committee_user', "New Purchase Requisition", self.message , user=False  , department=False,context=context)    

            else:
                for order in req.purchase_ids:
                    if order.state == 'budget_approved':
                       wf_service.trg_validate(uid, 'purchase.order', order.id, 'create_picking_in', cr)
            
                wf_service.trg_validate(uid, 'purchase.requisition', req.id, 'tender_done', cr)
        return True

    def test_roof(self, cr, uid, ids, context=None):
        wf_service = netsvc.LocalService('workflow')
        total = 0.0
        limite = self.pool.get('purchase.config.settings').get_limit_amount(cr, uid, ids)
        #requisition_pool = self.pool.get('purchase.requisition')
        for requisition in self.browse(cr, uid, ids, context={}):         
            
            for purchase in requisition.purchase_ids:
                total += purchase.amount_total


                if total < limite:
                    send_mail(self, cr, uid, ids[0] , 'base_custom.group_general_hr_manager', "Purchase Requisition After Entry The Quotations", self.message , user=False  , department=False,context=context)    
                    return False
                    #wf_service.trg_validate(uid, 'purchase.requisition', requisition_id.id, 'tender_HRM_approve2', cr)

        send_mail(self, cr, uid, ids[0] , 'base_custom.group_account_general_manager', "Purchase Requisition After Entry The Quotations", self.message , user=False  , department=False,context=context)                        
        return True


    def make_purchase_order(self, cr, uid, ids, partner_id, context=None):
        """
        Create New RFQ for Supplier
        """
        if context is None:
            context = {}
        assert partner_id, 'Supplier should be specified'
        purchase_order = self.pool.get('purchase.order')
        purchase_order_line = self.pool.get('purchase.order.line')
        picking_obj = self.pool.get('stock.picking')

        res_partner = self.pool.get('res.partner')
        fiscal_position = self.pool.get('account.fiscal.position')
        supplier = res_partner.browse(cr, uid, partner_id, context=context)

        supplier_pricelist = supplier.property_product_pricelist_purchase or False
        res = {}
        for requisition in self.browse(cr, uid, ids, context=context):
            location_id = False
            if supplier.id in filter(lambda x: x, [rfq.state <> 'cancel' and rfq.partner_id.id or None for rfq in requisition.purchase_ids]):
                raise osv.except_osv(_('Warning!'), _('You have already one %s purchase order for this partner, you must cancel this purchase order to create a new quotation.') % rfq.state)
            if  requisition.origin :
                pick_id = picking_obj.search(cr,uid,[('name' , '=' , requisition.origin ),('type' , '=' , 'out')])
                if pick_id :
                   location_id = picking_obj.browse(cr,uid,pick_id)[0].location_id.id
                   
            purchase_id = purchase_order.create(cr, uid, {
                        'origin': requisition.name,
                        'partner_id': supplier.id,
                        'pricelist_id': supplier_pricelist.id,
                        'company_id': requisition.company_id.id,
                        'fiscal_position': supplier.property_account_position and supplier.property_account_position.id or False,
                        'requisition_id':requisition.id,
                        'notes':requisition.description,
                        'warehouse_id':requisition.warehouse_id.id ,
                        'location_id':  location_id ,
                        'department_id':requisition.department_id.id ,
                        'category_id':requisition.category_id.id ,
            })
            res[requisition.id] = purchase_id
            for line in requisition.line_ids:
                
                product = line.product_id
                seller_price, qty, default_uom_po_id, date_planned = self._seller_details(cr, uid, line, supplier, context=context)
                taxes_ids = product.supplier_taxes_id
                taxes = fiscal_position.map_tax(cr, uid, supplier.property_account_position, taxes_ids)
                purchase_order_line.create(cr, uid, {
                    'order_id': purchase_id,
                    'name': line.product_id.name + "\n" + (line.name or " "),
                    'product_qty': qty,
                    'product_id': product.id,
                    'product_uom': default_uom_po_id,
                    'price_unit': 0.0,
                    'date_planned': date_planned,
                    'taxes_id': [(6, 0, taxes)],
                }, context=context)
                
        return res




class _settings(osv.osv_memory):
    _inherit = 'purchase.config.settings'
    

    def get_limit_amount(self, cr, uid, ids, context=None):
        purchase_pool = self.pool.get('purchase.config.settings')
        idss = purchase_pool.search(cr,uid,[],context=context)
        vals = purchase_pool.browse(cr, uid, idss, context)
        if idss:
            id = vals[0].id
            for pur in  purchase_pool.browse(cr, uid, idss, context):
                if pur.id > id:
                    id = pur.id
            config = purchase_pool.browse(cr, uid, id, context)
            return config.limit_amount


class purchase_requisition_line(osv.Model):
    _inherit = "purchase.requisition.line"

    _columns = {
        'name': fields.char('Specification'),
    }


class purchase_order(osv.Model):
    _inherit = 'purchase.order'
    
    STATE_SELECTION = [
        ('draft', 'Draft PO'),
        ('sent', 'RFQ Sent'),
        ('confirmed', 'Waiting Approval'),
        ('create_pickin', 'Waiting Order Picking'),
        ('approved', 'Purchase Order'),
        ('except_picking', 'Shipping Exception'),
        ('except_invoice', 'Invoice Exception'),
        ('waiting_budget', 'Waiting for Budget Approve'),
        ('budget_approved', 'Budget Approved'),
        ('not_approve','Budget Not Approved'),
        ('done', 'Done'),
        ('cancel', 'Cancelled'),]

    _columns = {

        'state': fields.selection(STATE_SELECTION, 'Status', readonly=True),
        'location_id': fields.many2one('stock.location', 'Destination', domain=[('usage','<>','view')], states={'approved':[('readonly',True)],'done':[('readonly',True)]}), 

    }


    def action_invoice_create(self ,cr , uid, ids , context=None):
        res = {}
        for rec in self.browse(cr,uid,ids):
            if not rec.invoice_ids:
               return super(purchase_order,self).action_invoice_create(cr , uid, ids , context=context)
        
        return res
        
        
        
        
    def onchange_warehouse_id(self, cr, uid, ids, warehouse_id):
        if not warehouse_id:
            return {}
        warehouse = self.pool.get('stock.warehouse').browse(cr, uid, warehouse_id)
        #'location_id': warehouse.lot_input_id.id, 
        return {'value':{'dest_address_id': False}}


    def create_budget_confirmation(self, cr, uid, ids, context={}):
        budget_pool=self.pool.get('account.budget.confirmation')
        period_pool=self.pool.get('account.period')
        requisition_obj = self.pool.get('purchase.requisition')
        ctx = context.copy()
        wf_service = netsvc.LocalService('workflow')
        for order in self.browse(cr, uid, ids, context=context):
            val={}
            total_amount=0
            subtotal=0
            pro_list=""
            ctx.update({'account_period_prefer_normal': True, 'company_id': order.company_id.id})
            pids = period_pool.find(cr, uid, order.date_order, context=ctx)
            for order_line in order.order_line:
                total_amount += order_line.price_subtotal
                subtotal += order_line.price_subtotal
                name =u' '.join((order_line.name)).encode('utf-8').strip()
                product_uom =u' '.join((order_line.product_uom.name)).encode('utf-8').strip()
                currency_name =u' '.join((order.company_id.currency_id.name)).encode('utf-8').strip()
                
                pro_list+=('- '+name+' , '+str(order_line.product_qty)+' '+product_uom+' , '+str(order_line.price_subtotal)+' '+currency_name+' . \n')
            
            val={
                'reference': str(order.requisition_id.name)+'/'+str(order.name),
                'partner_id': order.partner_id.id,
                'general_account_id':self._choose_account_from_po_line(cr, uid, order_line, context=context),
                'period_id': pids and pids[0],
                'analytic_account_id': order_line.account_analytic_id.id or order_line.order_id.department_id.analytic_account_id.id,
                'amount':total_amount, #order_line.price_subtotal,
                'residual_amount':subtotal, #order_line.price_subtotal,
                'date': order.date_order,
                'type' : 'purchase',
                'note': pro_list, #order_line.name,
            }
                
            if order.requisition_id.exclusive  == 'exclusive':
                for orders in order.requisition_id.purchase_ids:
                    if orders.id != order.id:
                       self.write(cr,uid,[orders.id],{'state': 'cancel'})
            confirm_id = budget_pool.create(cr, uid, val, context=context)
            requisition_obj.write(cr,uid,[order.requisition_id.id],{'budget_confirm_id':confirm_id})
            for order_line in order.order_line:
                order_line.write({'budget_confirm_id':confirm_id})           
                 
            

    def _prepare_order_picking(self, cr, uid, order, context=None):
        result = super(purchase_order, self)._prepare_order_picking(cr, uid, order, context=context)

        result.update({

            'purchase_id': order.id,
            'location_dest_id' : order.location_id.id,
            'company_id': order.company_id.id,
            'department_id':order.department_id.id,
            'category_id':order.category_id.id,
 

                })

        

        return result


    

       
    def purchase_confirm_order(self, cr, uid, ids, context=None):
        
        """ Function For Change Order State into Budget Approve """

        requisition = self.browse(cr,uid,ids)[0].requisition_id
        
        for user in requisition.user_ids:
            if not user.opinion:
               raise osv.except_osv(_('Warning!'), _('Some of Tender Members didnt sign on this tender like "%s" ') % (user.user_id.name)) 
        if requisition.exclusive == 'exclusive': 
            
           for quote in requisition.purchase_ids:
               if quote.id != ids[0]:
                  self.write(cr,uid,[quote.id],{'state' : 'cancel'}) 
               else :
                   self.write(cr,uid,ids,{'state' : 'budget_approved'})  
        else :
            self.write(cr,uid,ids,{'state' : 'budget_approved'})  
        send_mail(self, cr, uid, ids[0] , 'purchase_ntc.group_internal_auditor' , "New Purchase Requisition", self.message , user=False  , department=False,context=context)      
        return True




    def _check_negative(self, cr, uid, ids, context=None):
        """ 
       
        @return: Boolean of True or False
        """
        for order in self.browse(cr, uid, ids, context=context):
            for order_line in order.order_line:
                if order_line.price_unit <= 0.0 or order_line.price_subtotal <= 0.0:
                    raise osv.except_osv(_('Notification !'), _('Unit price value for %s , must be greater than zero !'%(order_line.name,))) 
        return True


    _constraints = [
        (_check_negative, '', ['price_unit','price_subtotal']),
    ]


class purchase_tender_members_info(osv.Model):
      _name = 'purchase.tender.members.info'
      _columns = {
          
          'name' : fields.char('Name', size=256 , readonly=True,), 
          'requisition_id' : fields.many2one('purchase.requisition' , 'Order' ,),
          'user_id' : fields.many2one('res.users' , 'User' ,),
          'opinion' : fields.selection( [('agree','I agree'),('disagree','I Disagree')] , 'Opinion'),
          'comment' : fields.char('Comment', size=256 ,), 
          
          
          
          
          
          
          
          
          }
    
